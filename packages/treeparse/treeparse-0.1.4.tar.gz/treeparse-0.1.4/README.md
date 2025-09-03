# Treeparse

CLI framework to make tools maximally transparent to LLMs. 

## Overview

Treeparse is an intuitive CLI framework leveraging `argparse`, `rich`, and `pydantic` to create structured, testable command-line interfaces. It mirrors the tree-like help output of `treeclick` but uses `argparse` for parsing and `pydantic` for model-based definitions.

Key goals include speed, LLM transparency (JSON and rich tree help formats), ease of authoring (especially for AI-generated code).

![Demo scripts](docs/assets/demos.gif)


## Key Features

- **Object-Oriented Structure**: Define CLI using Pydantic models: `cli`, `group`, `command`, `argument`, `option`.
- **Rich Tree Help**: Tree-structured help with branch pruning for subcommands, including higher levels.
- **JSON Output**: `--json` / `-j` provides syntax-highlighted JSON of the CLI structure for LLM parsing.
- **Parameter Validation**: Automatic matching of callback params to CLI definitions (names, types).
- **Sorting**: `sort_key` for ordering elements in help outputs.
- **Type and Default Display**: Optional `show_types` and `show_defaults` flags to include types and defaults in help.
- **Nargs Support**: Handles variable arguments/options (e.g., `*`, `+` for lists).
- **Boolean Handling**: Supports bool types with string-to-bool conversion.
- **Argparse Abstraction**: Users work with models; parsing logic is hidden.
- **Dynamic Alignment**: Help text aligns vertically, adjusting for type/default info.

## Structure

- **cli**: Root with subgroups, commands, options, configs (e.g., `show_types`, `show_defaults`).
- **group**: Nested groups with subgroups, commands, options.
- **command**: Commands with callbacks, arguments, options.
- **argument**: Positional args (type, nargs, default, etc.).
- **option**: Flags/options (type, nargs, default, etc.).

Models are modularized into files: `argument.py`, `option.py`, `command.py`, `group.py`, `color_config.py`, `cli.py`.

Initialization in `__init__.py` rebuilds models to handle forward references.

## Usage Example

From `examples/basic.py`:

```python
from treeparse import cli, command

def hello():
    print("Hello, world!")

app = cli(
    name="basic.py",
    help="A basic CLI example.",
    commands=[
        command(
            name="hello",
            help="Print hello world.",
            callback=hello,
        )
    ],
)

def main():
    app.run()

if __name__ == "__main__":
    main()
```

Run: `python examples/basic.py hello`

## Help Output

Tree-structured help prunes irrelevant branches for subcommands while retaining context. Supports long help text wrapping.

## LLM Transparency

- **Rich Tree Format**: Visual, human/LLM-readable tree.
- **JSON Format**: Structured, parseable output for LLMs.

## Current Status

- Implemented: Model definitions, tree/JSON help, validation, nargs, bool support, type/default display.
- Examples: `basic.py`, `demo.py` (complex), `list_demo.py` (nargs).
- Tests: Extensive pytest coverage (validation, execution, outputs) with cov reporting.
- Tools: Ruff for lint/format, pytest-cov for coverage.

## Plan

- [active], make cli (inherit from) a group, so that a higher level cli can be constructed that can add an existing CLI as a sub-cli without any additional code
    - when this happens, use the layout options (colors, show_types etc) from the new top level

Planned: Config overriding.

## License

MIT License.
