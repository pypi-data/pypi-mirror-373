from enum import Enum


class Color(Enum):
    """Colors that can be set as an accent color in BareCLI."""

    CYAN = "CYAN"
    MAGENTA = "MAGENTA"
    BLUE = "BLUE"
    YELLOW = "YELLOW"


class Status(Enum):
    """The vast majority of BareCLI's line output is prefixed with a status in the left sidebar."""

    INFO = "INFO"
    SUCCESS = "OK"
    ERROR = "ERROR"
    INPUT = "INPUT"
