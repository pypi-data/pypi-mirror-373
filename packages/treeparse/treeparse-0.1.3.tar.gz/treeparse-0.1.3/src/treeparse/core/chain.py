from typing import List
from pydantic import BaseModel, model_validator, computed_field
from .command import command
from .argument import argument
from .option import option


class chain(BaseModel):
    """Chain model that aggregates commands."""

    name: str
    help: str = ""
    chained_commands: List[command]
    sort_key: int = 0

    @model_validator(mode="after")
    def set_default_help(self):
        if not self.help:
            self.help = " ➜ ".join(c.name for c in self.chained_commands)
        return self

    @computed_field
    @property
    def display_name(self) -> str:
        return self.name

    @computed_field
    @property
    def effective_arguments(self) -> List[argument]:
        all_args = []
        seen = set()
        for cmd in self.chained_commands:
            for arg in cmd.arguments:
                dest = arg.dest or arg.name
                if dest in seen:
                    raise ValueError(
                        f"Conflicting argument dest '{dest}' in chain '{self.name}'"
                    )
                seen.add(dest)
                all_args.append(arg)
        return all_args

    @computed_field
    @property
    def effective_options(self) -> List[option]:
        all_opts = []
        seen = set()
        for cmd in self.chained_commands:
            for opt in cmd.options:
                dest = opt.get_dest()
                if dest in seen:
                    raise ValueError(
                        f"Conflicting option dest '{dest}' in chain '{self.name}'"
                    )
                seen.add(dest)
                all_opts.append(opt)
        return all_opts

    def validate(self):
        """Validate chained commands."""
        for cmd in self.chained_commands:
            cmd.validate()
        # Access effective to trigger any conflicts
        _ = self.effective_arguments
        _ = self.effective_options
