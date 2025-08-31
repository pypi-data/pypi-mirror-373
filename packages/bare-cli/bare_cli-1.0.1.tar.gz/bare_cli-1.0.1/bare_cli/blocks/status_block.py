from .abstract_block import AbstractBlock
from ..enums import Status


class StatusBlock(AbstractBlock):
    """Return a colorized status bookended in block characters with ample spacing.

    StatusBlocks are always displayed in the left sidebar and right padded. They give a
    quick visual indication of the type of content that is immediately to the right.

    Example: [ ERROR ] .. Main content here
    """

    def __init__(self, status: Status, color: str):
        self.content = status.value
        self.color = color
        self.block_start = self.block_start + " "
        self.block_end = " " + self.block_end + " "

    def __str__(self) -> str:
        return self.aligned

    @property
    def raw(self) -> str:
        return self.block_start + self.content + self.block_end

    @property
    def colorized(self) -> str:
        return self._get_bare_block(self.content, self.color)

    @property
    def aligned(self) -> str:
        return self._align(".", "<", self.SIDEBAR_WIDTH)
