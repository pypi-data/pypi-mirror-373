"""CLI model with methods."""

from typing import List, Union
import argparse
import sys
import json
import inspect
from pathlib import Path
from pydantic import model_validator
from rich.console import Console
from rich.tree import Tree
from rich.text import Text
from rich.syntax import Syntax
from .group import group
from .command import command
from .chain import chain
from .option import option
from ..utils.color_config import color_config, ColorTheme
from ..utils.helpers import load_yaml_config
from .argument import argument


def str2bool(v):
    """Convert string to boolean for argparse."""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def chain_runner(chain_obj: chain, **kwargs):
    """Runner function for chain commands."""
    for sub_cmd in chain_obj.chained_commands:
        sig = inspect.signature(sub_cmd.callback)
        sub_kwargs = {k: kwargs.get(k) for k in sig.parameters if k in kwargs}
        sub_cmd.callback(**sub_kwargs)


class RichArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser with rich-formatted errors."""

    def error(self, message):
        console = Console()
        if "invalid choice" in message:
            parts = message.split("invalid choice: ")
            if len(parts) > 1:
                invalid = parts[1].split(" (choose from")[0].strip("'")
                console.print(
                    f"[bold red]Error:[/bold red] {parts[0]}invalid choice: [yellow]'{invalid}'[/yellow] (choose from{parts[1].split('(choose from')[1]}"
                )
            else:
                console.print(f"[bold red]Error:[/bold red] {message}")
        else:
            console.print(f"[bold red]Error:[/bold red] {message}")
        self.exit(2)


class cli(group):
    """CLI model inheriting from group for sub-CLI composition."""

    max_width: int = 120
    theme: ColorTheme = ColorTheme.DEFAULT
    colors: color_config = color_config()
    show_types: bool = False
    show_defaults: bool = False
    line_connect: bool = False
    yml_config: Path = None

    @model_validator(mode="after")
    def set_colors_from_theme(self):
        self.colors = color_config.from_theme(self.theme)
        return self

    def get_max_depth(self) -> int:
        """Compute max depth of CLI tree."""

        def recurse(node: Union["cli", group, command, chain]) -> int:
            if isinstance(node, (command, chain)):
                return 0
            children = (
                node.subgroups + node.commands if hasattr(node, "subgroups") else []
            )
            if not children:
                return 0
            return 1 + max(recurse(c) for c in children)

        return recurse(self)

    def _get_node_from_path(
        self, path: List[str]
    ) -> Union[group, command, chain, "cli"]:
        """Get node from path."""
        current: Union["cli", group, command, chain] = self
        for p in path:
            if not hasattr(current, "subgroups"):
                raise ValueError(f"Path not found: {path}")
            children = current.subgroups + current.commands
            ch = next((c for c in children if c.display_name == p), None)
            if ch is None:
                raise ValueError(f"Path not found: {path}")
            current = ch
        return current

    def structure_dict(self):
        """Return a dictionary representation of the CLI structure."""

        def recurse(node: Union["cli", group, command, chain], is_root: bool = True):
            d = {"name": node.name, "help": node.help}
            if hasattr(node, "sort_key"):
                d["sort_key"] = node.sort_key
            d["options"] = [
                {
                    **opt.model_dump(exclude={"arg_type"}),
                    "arg_type": opt.arg_type.__name__,
                    "choices": opt.choices,
                }
                for opt in sorted(node.options, key=lambda x: (x.sort_key, x.flags[0]))
            ]
            d["arguments"] = [
                {
                    **arg.model_dump(exclude={"arg_type"}),
                    "arg_type": arg.arg_type.__name__,
                    "choices": arg.choices,
                }
                for arg in sorted(node.arguments, key=lambda x: (x.sort_key, x.name))
            ]
            if isinstance(node, command):
                d["type"] = "command"
                d["callback"] = node.callback.__name__
            elif isinstance(node, chain):
                d["type"] = "chain"
                d["chained"] = [recurse(c, False) for c in node.chained_commands]
            else:
                if is_root:
                    d["type"] = "cli"
                else:
                    d["type"] = "group"
            if hasattr(node, "subgroups"):
                d["subgroups"] = [
                    recurse(g, is_root=False)
                    for g in sorted(node.subgroups, key=lambda x: (x.sort_key, x.name))
                ]
            if hasattr(node, "commands"):
                d["commands"] = [
                    recurse(c, is_root=False)
                    for c in sorted(node.commands, key=lambda x: (x.sort_key, x.name))
                ]
            return d

        return recurse(self, is_root=True)

    def build_parser(self) -> argparse.ArgumentParser:
        """Build argparse parser from CLI structure."""
        self._validate()
        max_depth = self.get_max_depth()
        parser = RichArgumentParser(
            prog=self.display_name, description=self.help, add_help=False
        )
        self._add_args_and_opts_to_parser(parser, self.arguments, self.options)
        self._build_subparser(parser, self, 1, max_depth, self.arguments, self.options)
        return parser

    def _add_args_and_opts_to_parser(
        self, parser: argparse.ArgumentParser, args: List[argument], opts: List[option]
    ):
        for opt in opts:
            dest = opt.get_dest()
            kwargs = {"dest": dest, "help": opt.help}
            if opt.default is not None:
                kwargs["default"] = opt.default
            kwargs["type"] = opt.arg_type if opt.arg_type is not bool else str2bool
            if opt.nargs is not None:
                kwargs["nargs"] = opt.nargs
            if opt.choices is not None:
                kwargs["choices"] = opt.choices
            if opt.required:
                kwargs["required"] = True
            parser.add_argument(*opt.flags, **kwargs)
        for arg in args:
            kwargs = {
                "help": arg.help,
                "type": arg.arg_type if arg.arg_type is not bool else str2bool,
            }
            if arg.dest is not None:
                kwargs["dest"] = arg.dest
            if arg.nargs is not None:
                kwargs["nargs"] = arg.nargs
            if arg.default is not None:
                kwargs["default"] = arg.default
            elif arg.nargs == "?":
                kwargs["default"] = None
            if arg.choices is not None:
                kwargs["choices"] = arg.choices
            parser.add_argument(arg.name, **kwargs)

    def _build_subparser(
        self,
        parent_parser: argparse.ArgumentParser,
        node: Union["cli", group],
        depth: int,
        max_depth: int,
        inherited_args: List[argument],
        inherited_opts: List[option],
    ):
        if depth > max_depth:
            return
        # Filter inherited options to only those that should be inherited
        inheritable_inherited_opts = [opt for opt in inherited_opts if opt.inherit]
        children = sorted(
            (node.subgroups + node.commands) if hasattr(node, "subgroups") else [],
            key=lambda x: (x.sort_key, x.name),
        )
        if children:
            subparsers = parent_parser.add_subparsers(dest=f"command_{depth}")
            for child in children:
                child_parser = subparsers.add_parser(
                    child.display_name, help=child.help, add_help=False
                )
                if isinstance(child, group):
                    self._add_args_and_opts_to_parser(
                        child_parser,
                        inherited_args + child.arguments,
                        inheritable_inherited_opts + child.options,
                    )
                    self._build_subparser(
                        child_parser,
                        child,
                        depth + 1,
                        max_depth,
                        inherited_args + child.arguments,
                        inheritable_inherited_opts + child.options,
                    )
                else:  # command or chain
                    self._add_args_and_opts_to_parser(
                        child_parser,
                        child.effective_arguments,
                        child.effective_options,  # Removed inheritable_inherited_opts to prevent default override
                    )
                    if isinstance(child, command):
                        child_parser.set_defaults(func=child.callback)
                    else:
                        child_parser.set_defaults(func=chain_runner, chain_obj=child)

    def _validate(self):
        """Validate all commands in the CLI structure, considering inherited options and arguments."""

        def recurse(
            node: Union["cli", group, command, chain],
            inherited_args: List[argument] = [],
            inherited_opts: List[option] = [],
        ):
            if isinstance(node, command):
                # Filter inherited options to only those that should be inherited
                inheritable_opts = [opt for opt in inherited_opts if opt.inherit]
                effective_args = inherited_args + node.arguments
                effective_opts = inheritable_opts + node.options
                provided = {}
                for arg in effective_args:
                    dest = arg.dest or arg.name
                    arg_type = arg.arg_type
                    if arg.nargs in ["*", "+"]:
                        arg_type = List[arg_type]
                    provided[dest] = arg_type
                for opt in effective_opts:
                    dest = opt.get_dest()
                    opt_type = opt.arg_type
                    if opt.nargs in ["*", "+"]:
                        opt_type = List[opt_type]
                    provided[dest] = opt_type
                sig = inspect.signature(node.callback)
                param_names = set(sig.parameters.keys())
                param_types = {
                    k: v.annotation
                    for k, v in sig.parameters.items()
                    if v.annotation != inspect.Parameter.empty
                }
                provided_names = set(provided.keys())
                if param_names != provided_names:
                    missing = param_names - provided_names
                    extra = provided_names - param_names
                    error_msg = f"Parameter name mismatch for command '[bold red]{node.name}[/bold red]': "
                    if missing:
                        error_msg += f"Missing parameters in CLI definition: [yellow]{missing}[/yellow]. "
                    if extra:
                        error_msg += f"Extra parameters in CLI definition: [yellow]{extra}[/yellow]. "
                    error_msg += f"Callback expects: [cyan]{param_names}[/cyan], CLI provides: [cyan]{provided_names}[/cyan]"
                    raise ValueError(error_msg)
                type_mismatches = []
                for param, p_type in param_types.items():
                    cli_type = provided.get(param)
                    # Handle list vs List equivalence
                    if p_type is list and str(cli_type).startswith("typing.List"):
                        continue  # Consider them equivalent
                    if str(p_type).startswith("typing.List") and cli_type is list:
                        continue
                    if cli_type != p_type:
                        type_mismatches.append(
                            f"{param}: callback [green]{p_type.__name__ if hasattr(p_type, '__name__') else str(p_type)}[/green] vs CLI [green]{cli_type.__name__ if hasattr(cli_type, '__name__') else str(cli_type)}[/green]"
                        )
                if type_mismatches:
                    error_msg = (
                        f"Parameter type mismatch for command '[bold red]{node.name}[/bold red]': "
                        + "; ".join(type_mismatches)
                    )
                    raise ValueError(error_msg)
                # Check defaults against choices (only local)
                for arg in node.arguments:
                    if arg.choices is not None and arg.default is not None:
                        if arg.nargs in ["*", "+"] and isinstance(arg.default, list):
                            for d in arg.default:
                                if d not in arg.choices:
                                    raise ValueError(
                                        f"Default value {d} not in choices {arg.choices} for argument '{arg.name}' in command '{node.name}'"
                                    )
                        else:
                            if arg.default not in arg.choices:
                                raise ValueError(
                                    f"Default value {arg.default} not in choices {arg.choices} for argument '{arg.name}' in command '{node.name}'"
                                )
                for opt in node.options:  # only local options for this check
                    if opt.choices is not None and opt.default is not None:
                        if opt.nargs in ["*", "+"] and isinstance(opt.default, list):
                            for d in opt.default:
                                if d not in opt.choices:
                                    raise ValueError(
                                        f"Default value {d} not in choices {opt.choices} for option '{opt.flags[0]}' in command '{node.name}'"
                                    )
                        else:
                            if opt.default not in opt.choices:
                                raise ValueError(
                                    f"Default value {opt.default} not in choices {opt.choices} for option '{opt.flags[0]}' in command '{node.name}'"
                                )
            elif isinstance(node, chain):
                node.validate()
            else:
                for cmd in node.commands:
                    recurse(
                        cmd,
                        inherited_args + node.arguments,
                        inherited_opts + node.options,
                    )
                for grp in node.subgroups:
                    recurse(
                        grp,
                        inherited_args + node.arguments,
                        inherited_opts + node.options,
                    )

        recurse(self, [], [])

    def run(self):
        """Run the CLI."""
        console = Console()
        try:
            parser = self.build_parser()
        except ValueError as e:
            console.print(str(e), markup=True)
            sys.exit(1)
        # Handle special flags
        argv = sys.argv[1:]
        help_flags = ["--help", "-h"]
        json_flags = ["--json", "-j"]
        has_help = any(a in help_flags for a in argv)
        has_json = any(a in json_flags for a in argv)
        if has_help or has_json:
            if has_json:
                structure = self.structure_dict()
                json_str = json.dumps(structure, indent=2)
                syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
                console.print(syntax)
            else:
                path = []
                for a in argv:
                    if a in help_flags:
                        break
                    if not a.startswith("-"):
                        path.append(a)
                self.print_help(path)
            sys.exit(0)
        # Load YAML config if provided
        if self.yml_config:
            config = load_yaml_config(str(self.yml_config))
            # Simple override: set defaults from config (extend as needed)
            for opt in self.options:
                if opt.get_dest() in config:
                    opt.default = config[opt.get_dest()]
        # Normal parsing
        try:
            args = parser.parse_args()
        except SystemExit:
            sys.exit(1)
        path = []
        for i in range(1, self.get_max_depth() + 2):
            cmd = getattr(args, f"command_{i}", None)
            if cmd is None:
                break
            path.append(cmd)
        if not hasattr(args, "func"):
            self.print_help(path)
            sys.exit(0)
        current = self._get_node_from_path(path)
        missing = []
        for arg in current.effective_arguments:
            dest = arg.dest or arg.name
            if (
                arg.nargs is None
                and arg.default is None
                and getattr(args, dest, None) is None
            ):
                missing.append(arg.name)
        if missing:
            parser.error("the following arguments are required: " + ", ".join(missing))
        # Collect effective args and opts from the path
        effective_args = []
        effective_opts = []
        path_nodes = [self]
        current_node = self
        for p in path:
            children = current_node.subgroups + current_node.commands
            child = next((c for c in children if c.display_name == p), None)
            if child:
                path_nodes.append(child)
                current_node = child
        for node in path_nodes:
            if hasattr(node, "arguments"):
                effective_args.extend(node.arguments)
            else:
                effective_args.extend(node.effective_arguments)
            if hasattr(node, "options"):
                effective_opts.extend(node.options)
            else:
                effective_opts.extend(node.effective_options)
        # For the current node, add inherited options from ancestors
        if isinstance(current, (command, chain)):
            for node in path_nodes[:-1]:
                effective_opts.extend([opt for opt in node.options if opt.inherit])
        # Collect all options from the CLI
        all_options = []

        def collect_opts(node):
            if hasattr(node, "options"):
                all_options.extend(node.options)
            if hasattr(node, "subgroups"):
                for g in node.subgroups:
                    collect_opts(g)
            if hasattr(node, "commands"):
                for c in node.commands:
                    collect_opts(c)

        collect_opts(self)
        provided_names = set()
        for opt in all_options:
            provided_names.add(opt.get_dest())
        for arg in effective_args:
            provided_names.add(arg.dest or arg.name)
        arg_dict = {
            k: v
            for k, v in vars(args).items()
            if not k.startswith("command_")
            and k not in ("func", "chain_obj")
            and k in provided_names
        }
        if hasattr(args, "chain_obj"):
            args.func(args.chain_obj, **arg_dict)
        else:
            args.func(**arg_dict)

    def print_help(self, path: List[str]):
        """Print custom tree help."""
        # Find the deepest valid command path
        current = self
        consumed = 0
        for i, p in enumerate(path):
            if not hasattr(current, "subgroups"):
                if isinstance(current, command) and consumed < len(path):
                    break
                raise ValueError(f"Path not found: {path}")
            children = current.subgroups + current.commands
            ch = next((c for c in children if c.display_name == p), None)
            if ch is None:
                raise ValueError(f"Path not found: {path}")
            current = ch
            consumed = i + 1
        effective_path = path[:consumed]
        # Build usage string
        path_str = " ".join(effective_path)
        if path_str:
            path_str += " "
        if consumed < len(path):
            path_str += "[ARGS...] "
        usage = f"[bold]Usage: {self.display_name} {path_str}... [rgb(45,45,45)] (--json, -j, --help, -h)"
        console = Console(width=self.max_width)
        console.print(usage)
        console.print(
            f"[{self.colors.requested_help}]Description: {current.help}[/{self.colors.requested_help}]"
        )
        max_start = 0

        def collect_recurse(
            node: Union["cli", group, command, chain],
            on_path: bool,
            remaining_path: List[str],
            depth: int,
        ):
            nonlocal max_start
            name_len = len(self._get_name_part(node))
            prefix_len = depth * 4
            max_start = max(max_start, prefix_len + name_len)
            opts = node.options if hasattr(node, "options") else node.effective_options
            opts_sorted = sorted(opts, key=lambda x: (x.sort_key, x.flags[0]))
            for opt in opts_sorted:
                flags = sorted(opt.flags, key=lambda f: (-len(f), f))
                opt_name = ", ".join(flags)
                opt_len = len(opt_name)
                if self.show_types:
                    type_name = opt.arg_type.__name__
                    opt_len += len(f": {type_name}")
                if opt.choices is not None:
                    choices_str = f" ({'|'.join(map(str, opt.choices))})"
                    opt_len += len(choices_str)
                opt_prefix = (depth + 1) * 4
                max_start = max(max_start, opt_prefix + opt_len)
            if isinstance(node, (command, chain)):
                return
            children = sorted(
                (node.subgroups + node.commands) if hasattr(node, "subgroups") else [],
                key=lambda x: (x.sort_key, x.name),
            )
            if on_path and remaining_path:
                next_name = remaining_path[0]
                for child in children:
                    if child.display_name == next_name:
                        collect_recurse(child, True, remaining_path[1:], depth + 1)
                        break
            else:
                for child in children:
                    collect_recurse(child, False, [], depth + 1)

        collect_recurse(self, True, effective_path, 0)
        selected_depth = len(effective_path)
        root_label = self._get_root_label(max_start, 0, True)
        tree = Tree(root_label, guide_style=self.colors.guide)
        self._add_children(
            tree, self, True, effective_path, max_start, 0, selected_depth
        )
        console.print(tree)

    def _get_name_part(self, node: Union[group, command, chain]) -> str:
        args_parts = []
        args_list = (
            node.arguments if hasattr(node, "arguments") else node.effective_arguments
        )
        for arg in sorted(args_list, key=lambda x: (x.sort_key, x.name)):
            part = f"[{arg.name.upper()}"
            extra = []
            if self.show_types:
                extra.append(arg.arg_type.__name__)
            if arg.choices is not None:
                extra.append(f"({'|'.join(map(str, arg.choices))})")
            if extra:
                part += f", {' '.join(extra)}"
            part += "]"
            args_parts.append(part)
        args_str = " ".join(args_parts)
        return f"{node.display_name} {args_str}".rstrip()

    def _wrap_help(self, help: str, width: int) -> List[str]:
        if width <= 0:
            width = 20
        lines = []
        current = []
        current_len = 0
        words = help.split()
        for word in words:
            word_len = len(word)
            if current and current_len + 1 + word_len > width:
                lines.append(" ".join(current))
                current = [word]
                current_len = word_len
            else:
                if current:
                    current_len += 1
                current.append(word)
                current_len += word_len
        if current:
            lines.append(" ".join(current))
        return lines

    def _get_root_label(self, max_start: int, depth: int, is_ancestor: bool) -> Text:
        style = "dim " + self.colors.app if is_ancestor else self.colors.app
        help_style = (
            "dim " + self.colors.normal_help if is_ancestor else self.colors.normal_help
        )
        label = Text()
        label.append(self.display_name, style=style)
        args_parts = []
        for arg in sorted(self.arguments, key=lambda x: (x.sort_key, x.name)):
            part = f"[{arg.name.upper()}"
            extra = []
            if self.show_types:
                extra.append(arg.arg_type.__name__)
            if arg.choices is not None:
                extra.append(f"({'|'.join(map(str, arg.choices))})")
            if extra:
                part += f", {' '.join(extra)}"
            part += "]"
            args_parts.append(part)
        args_str = " ".join(args_parts)
        if args_str:
            label.append(" ")
            label.append(
                args_str,
                style="dim " + self.colors.argument
                if is_ancestor
                else self.colors.argument,
            )
        name_len = label.cell_len
        prefix_len = depth * 4
        padding = max_start - prefix_len - name_len
        if self.help:
            help_lines = self._wrap_help(self.help, self.max_width - (max_start + 1))
            if self.line_connect:
                label.append(Text("─" * (padding + 1), style=self.colors.connector))
                label.append(help_lines[0], style=help_style)
                for hl in help_lines[1:]:
                    label.append("\n")
                    label.append(" " * (name_len + padding + 1))
                    label.append(hl, style=help_style)
            else:
                label.append(" " * padding)
                label.append(" ")
                label.append(help_lines[0], style=help_style)
                for hl in help_lines[1:]:
                    label.append("\n")
                    label.append(" " * (name_len + padding + 1))
                    label.append(hl, style=help_style)
        else:
            label.append(" " * padding)
        return label

    def _get_label(
        self,
        node: Union[group, command, chain],
        max_start: int,
        on_path: bool,
        depth: int,
        is_ancestor: bool,
    ) -> Text:
        base_help_style = (
            self.colors.requested_help if on_path else self.colors.normal_help
        )
        help_style = "dim " + base_help_style if is_ancestor else base_help_style
        name_style = (
            "dim " + self.colors.group
            if is_ancestor and isinstance(node, group)
            else self.colors.group
            if isinstance(node, group)
            else "dim " + self.colors.command
            if is_ancestor
            else self.colors.command
        )
        arg_style = (
            "dim " + self.colors.argument if is_ancestor else self.colors.argument
        )
        label = Text()
        label.append(node.display_name, style=name_style)
        args_list = (
            node.arguments if isinstance(node, group) else node.effective_arguments
        )
        args_parts = []
        for arg in sorted(args_list, key=lambda x: (x.sort_key, x.name)):
            part = f"[{arg.name.upper()}"
            extra = []
            if self.show_types:
                extra.append(arg.arg_type.__name__)
            if arg.choices is not None:
                extra.append(f"({'|'.join(map(str, arg.choices))})")
            if extra:
                part += f", {' '.join(extra)}"
            part += "]"
            args_parts.append(part)
        args_str = " ".join(args_parts)
        if args_str:
            label.append(" ")
            label.append(args_str, style=arg_style)
        name_len = label.cell_len
        prefix_len = depth * 4
        padding = max_start - prefix_len - name_len
        if node.help:
            help_lines = self._wrap_help(node.help, self.max_width - (max_start + 1))
            if self.line_connect:
                label.append(Text("─" * (padding + 1), style=self.colors.connector))
                label.append(help_lines[0], style=help_style)
                for hl in help_lines[1:]:
                    label.append("\n")
                    label.append(" " * (name_len + padding + 1))
                    label.append(hl, style=help_style)
            else:
                label.append(" " * padding)
                label.append(" ")
                label.append(help_lines[0], style=help_style)
                for hl in help_lines[1:]:
                    label.append("\n")
                    label.append(" " * (name_len + padding + 1))
                    label.append(hl, style=help_style)
        else:
            label.append(" " * padding)
        return label

    def _get_option_label(
        self, opt: option, max_start: int, depth: int, is_ancestor: bool
    ) -> Text:
        option_style = (
            "dim " + self.colors.option if is_ancestor else self.colors.option
        )
        option_help_style = (
            "dim " + self.colors.option_help if is_ancestor else self.colors.option_help
        )
        default_style = "bold dim white"
        label = Text()
        flags = sorted(opt.flags, key=lambda f: (-len(f), f))
        flags_str = ", ".join(flags)
        label.append(flags_str, style=option_style)
        type_part = ""
        if self.show_types:
            type_name = opt.arg_type.__name__
            type_part = f": {type_name}"
        choices_part = ""
        if opt.choices is not None:
            choices_part = f" ({'|'.join(map(str, opt.choices))})"
        label.append(type_part + choices_part, style=self.colors.type_color)
        name_len = label.cell_len
        prefix_len = depth * 4
        padding = max_start - prefix_len - name_len
        if opt.help:
            help_lines = self._wrap_help(opt.help, self.max_width - (max_start + 1))
            if self.line_connect:
                label.append(Text("─" * (padding + 1), style=self.colors.connector))
                label.append(help_lines[0], style=option_help_style)
                for hl in help_lines[1:]:
                    label.append("\n")
                    label.append(" " * (name_len + padding + 1))
                    label.append(hl, style=option_help_style)
            else:
                label.append(" " * padding)
                label.append(" ")
                label.append(help_lines[0], style=option_help_style)
                for hl in help_lines[1:]:
                    label.append("\n")
                    label.append(" " * (name_len + padding + 1))
                    label.append(hl, style=option_help_style)
        else:
            label.append(" " * padding)
        if self.show_defaults and opt.default is not None:
            default_str = f" (default: {opt.default})"
            if opt.help:
                label.append(
                    Text.from_markup(
                        f"[{default_style}]{default_str}[/{default_style}]"
                    )
                )
            else:
                label.append(" ")
                label.append(
                    Text.from_markup(
                        f"[{default_style}]{default_str}[/{default_style}]"
                    )
                )
        return label

    def _add_children(
        self,
        current_tree: Tree,
        node: Union["cli", group, command, chain],
        on_path: bool,
        remaining_path: List[str],
        max_start: int,
        depth: int,
        selected_depth: int,
    ):
        is_ancestor = depth < selected_depth
        opts = node.options if hasattr(node, "options") else node.effective_options
        opts_sorted = sorted(opts, key=lambda x: (x.sort_key, x.flags[0]))
        for opt in opts_sorted:
            opt_label = self._get_option_label(opt, max_start, depth + 1, is_ancestor)
            current_tree.add(opt_label)
        if isinstance(node, (command, chain)):
            return
        children = sorted(
            (node.subgroups + node.commands) if hasattr(node, "subgroups") else [],
            key=lambda x: (x.sort_key, x.name),
        )
        if on_path and remaining_path:
            next_name = remaining_path[0]
            for child in children:
                if child.display_name == next_name:
                    child_is_ancestor = (depth + 1) < selected_depth
                    child_label = self._get_label(
                        child, max_start, True, depth + 1, child_is_ancestor
                    )
                    child_tree = current_tree.add(child_label)
                    self._add_children(
                        child_tree,
                        child,
                        True,
                        remaining_path[1:],
                        max_start,
                        depth + 1,
                        selected_depth,
                    )
                    break
        else:
            for child in children:
                child_label = self._get_label(child, max_start, False, depth + 1, False)
                child_tree = current_tree.add(child_label)
                self._add_children(
                    child_tree, child, False, [], max_start, depth + 1, selected_depth
                )
