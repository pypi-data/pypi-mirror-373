from __future__ import annotations
from typing import Iterable, Literal

__all__ = ["__version__", "print_five_lines", "five_default_colors"]
__version__ = "0.1.0"

ColorName = Literal["red", "green", "yellow", "blue", "magenta", "cyan", "white", "black", "reset"]

# ANSI sequences (Colorama will enable these on Windows)
ANSI = {
    "reset": "\033[0m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "black": "\033[30m",
}

def five_default_colors() -> list[ColorName]:
    return ["red", "green", "yellow", "blue", "magenta"]

def print_five_lines(text: str = "khx", colors: Iterable[ColorName] | None = None) -> None:
    """
    Print five colored lines to stdout.
    Args:
        text: content to print on each line.
        colors: optional iterable of 5 color names; defaults to red, green, yellow, blue, magenta.
    """
    cols = list(colors) if colors is not None else five_default_colors()
    if len(cols) != 5:
        raise ValueError("colors must contain exactly 5 entries")
    for c in cols:
        code = ANSI.get(c, ANSI["reset"])
        print(f"{code}{text}{ANSI['reset']}")

