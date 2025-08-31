class InvalidChoiceError(Exception):
    """Raised when user does not enter valid input in the choice method."""

    def __init__(self, message: str = "User provided invalid choice input."):
        self.message = message
        super().__init__(f"{message}")
