from .abstract_block import AbstractBlock


class ChoiceBlock(AbstractBlock):
    """Return a colorized int bookended in block characters.

    ChoiceBlocks are used to house the int choices a user can select
    when using the choice method. These are similar to all other blocks
    but are left padded.

    Example: [3] An option here
    """

    WIDTH = 4

    def __init__(self, choice: int, color: str):
        self.content = str(choice)
        self.color = color

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
        return self._align("", ">", self.WIDTH)
