"""group model."""

from typing import List, Union
from pydantic import BaseModel
from .command import command
from .chain import chain
from .option import option
from .argument import argument


class group(BaseModel):
    """group model."""

    name: str
    help: str = ""
    subgroups: List["group"] = []
    commands: List[Union[command, chain]] = []
    options: List[option] = []
    arguments: List[argument] = []
    sort_key: int = 0

    @property
    def display_name(self) -> str:
        """Get display name."""
        return self.name
