# vmaudit
# Author: Arcitec
# Project Site: https://github.com/Arcitec/vmaudit
# SPDX-License-Identifier: GPL-2.0-only


import sys
from enum import Enum
from typing import Union

# Global flag to control coloring.
ENABLE_COLOR = sys.stdout.isatty()


class Align(Enum):
    LEFT = "<"
    RIGHT = ">"
    CENTER = "^"


class Color(Enum):
    RESET = "\033[0m"
    BOLD = "\033[1m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    LIGHT_BLUE = "\033[94m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    BOLD_YELLOW = "\033[1;33m"

    @classmethod
    def enable_color(cls, enabled: bool) -> None:
        """Globally enable or disable the ANSI colors."""
        global ENABLE_COLOR
        ENABLE_COLOR = enabled

    def __call__(self, text: Union[str, int]) -> str:
        """Return text wrapped in this ANSI terminal color (if TTY output)."""
        return f"{self.value}{text}{Color.RESET.value}" if ENABLE_COLOR else str(text)

    def pad(self, text: Union[str, int], padding: int = 0, align: Align = Align.RIGHT) -> str:
        """Return text wrapped in this ANSI terminal color (if TTY output), and padded to the chosen width."""
        if padding > 0:
            text = f"{text:{align.value}{padding}}"
        return self(text) if ENABLE_COLOR else str(text)
