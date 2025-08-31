# Copyright 2025 Jamison Griffith
# Licensed under the Apache License, Version 2.0 (see LICENSE file for details)
import sys
from colorama import Fore
from .enums import Color, Status
from .blocks.status_block import StatusBlock
from .blocks.nested_status_block import NestedStatusBlock
from .blocks.choice_block import ChoiceBlock
from .blocks.misc_block import MiscBlock
from .invalid_choice_error import InvalidChoiceError
from .color_mapper import ColorMapper


class BareCLI:
    """May your CLI code be semantic and your text output beautifully bare.

    Pass a Color to the constructor to color your title and input status blocks.
    """

    def __init__(self, accent_color: Color = Color.YELLOW):
        self.accent_color = ColorMapper().from_color(accent_color)

    def title(self, title: str):
        """Display a title in accent color sandwiched by newlines."""

        print(f"\n{MiscBlock(title, self.accent_color, add_spacing=True)}\n")

    def info(self, message: str):
        """Display a blue info status sidebar and a main content message."""

        print(self._get_bareline(Status.INFO, Fore.BLUE, message))

    def success(self, message: str):
        """Display a green success status sidebar and a main content message."""

        print(self._get_bareline(Status.SUCCESS, Fore.GREEN, message))

    def error(self, message: str):
        """Display a red error status sidebar and a main content message."""

        print(self._get_bareline(Status.ERROR, Fore.RED, message))

    def ask(self, prompt: str) -> str:
        """Prompt the user for input."""

        print(self._get_bareline(Status.INPUT, self.accent_color, prompt))
        input_prompt = self._get_bareline(Status.INPUT, self.accent_color, "")
        return input(input_prompt).strip()

    def confirm(self, prompt: str, *, permissive_by_default: bool = True) -> bool:
        """Prompt the user to answer a boolean question.

        Use the permissive_by_default kwarg to set the default bool to allow
        the user to just hit the Enter key instead of typing in an answer.
        """

        if permissive_by_default:
            default = "yes"
        else:
            default = "no"

        displayed_default = MiscBlock(default, self.accent_color)
        message = f"{prompt} (yes/no) {displayed_default}:"
        print(self._get_bareline(Status.INPUT, self.accent_color, message))
        input_prompt = self._get_bareline(Status.INPUT, self.accent_color, "")
        response = input(input_prompt)

        if response == "":
            return default == "yes"
        elif "y" in response.lower():
            return True
        else:
            return False

    def choice(
        self,
        prompt: str,
        choices: list[str],
        *,
        allow_chances: bool = True,
        exit_early: bool = True,
    ) -> tuple[int, str]:
        """Prompt the user to choose a value from a list of choices and return tuple with index and value.

        Setting the allow_chances kwarg to True gives the user multiple chances to select
        a valid option.
        Setting the exit_early kwarg to True will exit the program with an error message
        when the user fails to make a valid selection. Setting this to False will instead
        raise an InvalidChoiceError for your own code to handle how you want.

        Raises:
            InvalidChoiceError: When exit_early set to False and user fails to make a valid choice
        """

        status_block = StatusBlock(Status.INPUT, self.accent_color)
        print(f"{status_block} {prompt}")

        valid_inputs = [i for i in range(0, len(choices))]
        for i, choice in enumerate(choices):
            print(self._get_choice_line(i, choice, status_block))

        prompt = f"Enter a number from {valid_inputs[0]} to {valid_inputs[-1]}:"
        print(self._get_bareline(Status.INPUT, self.accent_color, prompt))
        input_prompt = self._get_bareline(Status.INPUT, self.accent_color, "")
        id_input = input(input_prompt).strip()
        int_input = self._try_parse_int(id_input)

        # Boot out immediately if chances not allowed
        if not allow_chances and int_input not in valid_inputs:
            if not exit_early:
                raise InvalidChoiceError()
            else:
                self.error("Please try again later.")
                sys.exit(1)

        # If chances allowed, give user multiple chances to make a selection
        if allow_chances and int_input not in valid_inputs:
            chances = 1
            chance_limit = 3
            while int_input not in valid_inputs:
                if chances >= chance_limit:
                    if not exit_early:
                        raise InvalidChoiceError()
                    else:
                        self.error("Please try again later.")
                        sys.exit(1)

                print(self._get_bareline(Status.INPUT, self.accent_color, prompt))
                id_input = input(input_prompt).strip()
                int_input = self._try_parse_int(id_input)
                chances += 1

        # int_input will not be None here since it would not exit the loop
        return (int_input, choices[int_input])  # type: ignore[index, return-value]

    def _get_choice_line(self, index: int, choice: str, parent_block: StatusBlock):
        """Get formatted string for a choice line when using the choice method."""

        option_colors = [
            Fore.RESET,
            Fore.YELLOW,
            Fore.RED,
            Fore.GREEN,
            Fore.BLUE,
            Fore.MAGENTA,
            Fore.CYAN,
        ]

        choice_block = ChoiceBlock(index, option_colors[index % len(option_colors)])
        nested_block = NestedStatusBlock(parent_block)
        return f"{nested_block} {choice_block} {choice}"

    def _get_bareline(
        self, status: Status, colorama_fore_color: str, message: str
    ) -> str:
        """Get the signature line of BareCLI: a StatusBlock in left sidebar and main content to the right."""

        status_block = StatusBlock(status, colorama_fore_color)
        return f"{status_block} {message}"

    def _try_parse_int(self, string_input: str) -> int | None:
        """Attempt to parse user input ints for choice method."""

        try:
            return int(string_input)
        except ValueError:
            return None
