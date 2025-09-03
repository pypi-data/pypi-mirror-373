"""Positional argument model."""

from typing import Any, List, Optional, Union
from pydantic import BaseModel


class argument(BaseModel):
    """Positional argument model."""

    name: str
    dest: Optional[str] = None
    arg_type: Any = str
    help: str = ""
    nargs: Union[int, str, None] = None
    default: Any = None
    choices: Optional[List[Any]] = None
    sort_key: int = 0
