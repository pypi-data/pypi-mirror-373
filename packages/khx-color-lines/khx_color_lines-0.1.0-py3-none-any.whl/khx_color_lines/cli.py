from __future__ import annotations
import argparse
from colorama import init as colorama_init
from . import print_five_lines, five_default_colors

def main() -> None:
    colorama_init(autoreset=True)  # enable ANSI on Windows
    parser = argparse.ArgumentParser(
        prog="khx-lines",
        description="Print five colored lines in the terminal."
    )
    parser.add_argument("-t", "--text", default="khx", help="Text to print on each line.")
    parser.add_argument("--colors", nargs=5, metavar=("C1","C2","C3","C4","C5"),
                        help="Five color names (red, green, yellow, blue, magenta, cyan, white, black).")
    args = parser.parse_args()
    cols = args.colors if args.colors else five_default_colors()
    print_five_lines(text=args.text, colors=cols)

