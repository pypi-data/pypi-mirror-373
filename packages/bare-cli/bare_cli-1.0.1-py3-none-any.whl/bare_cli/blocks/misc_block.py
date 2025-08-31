from .abstract_block import AbstractBlock


class MiscBlock(AbstractBlock):
    """Return a colorized value bookended in block characters.

    MiscBlocks can be peppered around since they have no internal alignment. are always displayed in the left sidebar and right padded. They give a
    Use the add_spacing kwarg to add spacing around a given value.

    Examples: [ The Title ], [yes]
    """

    def __init__(self, content: str, color: str, *, add_spacing: bool = False):
        self.content = content
        self.color = color

        if add_spacing:
            self.block_start = self.block_start + " "
            self.block_end = " " + self.block_end + " "

    def __str__(self) -> str:
        return self.colorized

    @property
    def raw(self) -> str:
        return self.block_start + self.content + self.block_end

    @property
    def colorized(self) -> str:
        return self._get_bare_block(self.content, self.color)

    @property
    def aligned(self) -> str:
        # No alignment needed
        return self.colorized
