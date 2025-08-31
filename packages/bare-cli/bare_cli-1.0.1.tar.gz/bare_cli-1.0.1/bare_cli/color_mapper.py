from colorama import Fore
from .enums import Color


class ColorMapper:
    """Maps a Color enum to a corresponding Colorama Fore color.

    Used so consumers of BareCLI do not have to import Colorama to set
    an accent color.
    """

    def from_color(self, accent: Color) -> str:
        match accent:
            case Color.CYAN:
                return Fore.CYAN
            case Color.MAGENTA:
                return Fore.MAGENTA
            case Color.BLUE:
                return Fore.BLUE
            case Color.YELLOW:
                return Fore.YELLOW
            case _:
                # Default to yellow if no match
                return Fore.YELLOW
