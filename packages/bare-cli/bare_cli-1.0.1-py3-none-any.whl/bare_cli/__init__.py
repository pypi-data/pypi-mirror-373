"""May your CLI code be semantic and your text output beautifully bare.

To start: Construct a BareCLI instance with an optional accent Color.
Handling the InvalidChoiceError is an opt-in behavior of the choice method.
"""

from .bare_cli import BareCLI
from .enums import Color
from .invalid_choice_error import InvalidChoiceError

__all__ = ["BareCLI", "Color", "InvalidChoiceError"]
