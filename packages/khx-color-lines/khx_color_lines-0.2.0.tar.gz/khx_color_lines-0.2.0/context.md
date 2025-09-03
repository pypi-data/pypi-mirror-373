# Goal

Create and publish a **pip-installable** Python package named **`khx_color_lines`** that prints **five colored lines** in the terminal. It must install cleanly on Windows/macOS/Linux and expose both a **Python API** and a **CLI command**.

# Context

* You currently have an empty folder named `khx_color_lines` on Windows 11.
* We want a minimal, reliable package with **zero headaches** for users.
* Windows needs proper ANSI handling → use **`colorama`**.

# Constraints

* Keep it **tiny** and beginner-friendly (no heavy deps).
* Use **modern packaging** (**PEP 621**, `pyproject.toml`, **hatchling**).
* Provide a **CLI** entry point (`khx-lines`).
* Python ≥ **3.9**.
* Clear license and README.
* Version must increment for each publish.

# Tasks

1. **Create structure & files** (from inside the `khx_color_lines` folder):

```
khx_color_lines/
│  pyproject.toml
│  README.md
│  LICENSE
│  .gitignore
└─ src/
   └─ khx_color_lines/
      │  __init__.py
      └─ cli.py
```

2. **Add packaging metadata** → `pyproject.toml`

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "khx_color_lines"
version = "0.1.0"
description = "Print five colored lines in the terminal (Windows/macOS/Linux)."
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
authors = [{ name = "Khader Abueltayef" }]
keywords = ["colors", "terminal", "ansi", "lines"]
classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent"
]
dependencies = ["colorama>=0.4.6"]

[project.scripts]
khx-lines = "khx_color_lines.cli:main"

[tool.hatch.build]
packages = ["src/khx_color_lines"]
```

3. **Implement the package API** → `src/khx_color_lines/__init__.py`

```python
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
```

4. **CLI entry point** → `src/khx_color_lines/cli.py`

```python
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
```

5. **README** → `README.md`

````markdown
# khx_color_lines

Print five colored lines in the terminal (cross-platform).

## Install
```bash
pip install khx_color_lines
````

## CLI

```bash
khx-lines
khx-lines --text "Hello"
khx-lines --colors red green yellow blue magenta
```

## Python API

```python
from khx_color_lines import print_five_lines
print_five_lines("Hello")  # prints 5 lines with default colors
```

```

6) **LICENSE** → `LICENSE` (MIT template is fine).

7) **.gitignore**
```

.venv/
**pycache**/
dist/
build/
\*.egg-info/

````

8) **Build & test locally (PowerShell)**
```powershell
# in khx_color_lines/
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip build
py -m build
# Test the wheel
py -m pip install --force-reinstall dist\khx_color_lines-0.1.0-py3-none-any.whl
khx-lines
python -c "import khx_color_lines as k; k.print_five_lines('Hello')"
````

9. **Publish to TestPyPI (safe rehearsal)**

```powershell
py -m pip install --upgrade twine
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-AgENdGVzdC5weXBpLm9yZwIkOWU4NTlmMmEtMzI0Mi00MmUxLWFhMWMtMmU1ZDFlYzQ0MWE5AAIqWzMsImI2MDI4MmViLTgyZjEtNGVhYS05YzRhLTNjNGNiY2Y0N2U2ZCJdAAAGIJX_9QkbgMNH6QbHBPyui0y3a0se0TuGwr3v9LL7GZTG"
py -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# fresh venv to test:
py -m venv .testenv
.\.testenv\Scripts\Activate.ps1
py -m pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple khx_color_lines
khx-lines --text "TestPyPI OK"
```

10. **Publish to real PyPI**

```powershell
deactivate
.\.venv\Scripts\Activate.ps1
# (bump version in both __init__.py and pyproject.toml if you rebuilt)
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmcCJDIwN2RkZDAwLTMxMjEtNDRhYy05ZmU5LTU0NmI5NDBmYjQ3ZgACKlszLCI4YWQ4YWUzZi0zY2NiLTRiZjQtOTA0Yy02ZThlYTVmYjczOTQiXQAABiAVlVBvdlf2El3v6HcnZeugYqElYDVqR06MNLTpuD8aEQ"
py -m twine upload dist/*
```

# Non-goals

* No theming system, gradients, or advanced styling.
* No dependency on heavy UI libraries.
* No packaging via legacy `setup.py`; stick to `pyproject.toml` + hatchling.

---