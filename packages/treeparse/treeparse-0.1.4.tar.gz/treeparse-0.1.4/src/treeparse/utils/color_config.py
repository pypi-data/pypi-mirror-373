"""Color configuration for help output."""

from enum import Enum
from pydantic import BaseModel


class ColorTheme(Enum):
    DEFAULT = "default"
    MONOCHROME = "monochrome"
    MONONEON = "mononeon"


class color_config(BaseModel):
    """Color configuration for help output."""

    app: str = "bold bright_cyan"
    group: str = "bold green"
    command: str = "cyan"
    argument: str = "orange1"
    option: str = "yellow"
    option_help: str = "italic yellow"
    requested_help: str = "bold white"
    normal_help: str = "bold rgb(180,180,180)"
    type_color: str = "dim white"
    connector: str = "rgb(45,45,45)"
    guide: str = "rgb(45,45,45)"

    @classmethod
    def from_theme(cls, theme: ColorTheme):
        if theme == ColorTheme.DEFAULT:
            return cls()
        elif theme == ColorTheme.MONOCHROME:
            return cls(
                app="bold italic rgb(200,200,200)",
                group="bold rgb(180,180,180)",
                command="rgb(160,160,160)",
                argument="rgb(140,140,140)",
                option="rgb(120,120,120)",
                option_help="italic rgb(100,100,100)",
                requested_help="rgb(255,255,255)",
                normal_help="bold rgb(200,200,200)",
                type_color="rgb(160,160,160)",
                connector="rgb(80,80,80)",
                guide="rgb(80,80,80)",
            )
        elif theme == ColorTheme.MONONEON:
            # Neon green base: rgb(57,255,20)
            # Varying intensities by scaling brightness
            return cls(
                app="bold italic rgb(57,255,20)",  # full bright
                group="bold rgb(51,229,18)",  # 90%
                command="rgb(46,204,16)",  # 80%
                argument="rgb(40,179,14)",  # 70%
                option="rgb(34,153,12)",  # 60%
                option_help="italic rgb(29,128,10)",  # 50%
                requested_help="rgb(57,255,20)",  # full
                normal_help="rgb(46,204,16)",  # 80%
                type_color="rgb(40,179,14)",  # 70%
                connector="rgb(29,128,10)",  # 50%
                guide="rgb(29,128,10)",  # 50%
            )
