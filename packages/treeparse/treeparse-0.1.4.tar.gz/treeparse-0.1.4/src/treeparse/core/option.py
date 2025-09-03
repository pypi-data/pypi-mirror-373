"""option model."""

from typing import Any, List, Optional, Union
from pydantic import BaseModel


class option(BaseModel):
    """option model."""

    flags: List[str]
    dest: Optional[str] = None
    arg_type: Any = str
    help: str = ""
    default: Any = None
    nargs: Union[int, str, None] = None
    choices: Optional[List[Any]] = None
    sort_key: int = 0
    required: bool = False
    inherit: bool = True

    def get_dest(self) -> str:
        """Compute the destination name for this option."""
        if self.dest:
            return self.dest
        long_flags = [f for f in self.flags if f.startswith("--")]
        if long_flags:
            return long_flags[0].lstrip("--").replace("-", "_")
        if self.flags:
            return self.flags[0].lstrip("-").replace("-", "_")
        raise ValueError("No flags defined for option")
