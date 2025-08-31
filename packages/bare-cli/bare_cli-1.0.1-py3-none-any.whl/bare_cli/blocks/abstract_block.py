from abc import ABC, abstractmethod
from colorama import Fore, Style


class AbstractBlock(ABC):
    """Represents a string, its ANSI color values and its internal alignment (aka: a Block).

    Blocks are the core visual identity of BareCLI and are the only components that contain color.
    Each subclass of AbstractBlock is expected to implement the str Dunder method so
    working with these objects is seamless.
    """

    SIDEBAR_WIDTH = 11
    block_start: str = "["
    block_end: str = "]"

    @property
    @abstractmethod
    def raw(self) -> str:
        pass

    @property
    @abstractmethod
    def colorized(self) -> str:
        pass

    @property
    @abstractmethod
    def aligned(self) -> str:
        pass

    def _get_bare_block(self, content: str, color: str) -> str:
        """Return the signature colorized block style of BareCLI."""

        return (
            Style.DIM
            + self.block_start
            + Style.RESET_ALL
            + Style.BRIGHT
            + color
            + content
            + Fore.RESET
            + Style.RESET_ALL
            + Style.DIM
            + self.block_end
        )

    def _align(self, fill: str, align: str, width: int) -> str:
        """Align a colorized string with provided format.

        ANSI color codes will break padding if formatted directly because Python counts their
        characters as strings even though they are not shown visually. We pad the raw string
        first and then replace it with the colorized string.
        """

        format_spec = f"{fill}{align}{width}"
        padded = f"{self.raw:{format_spec}}{Style.RESET_ALL}"
        return padded.replace(self.raw, self.colorized, 1)
