# khx_color_lines

Print five colored lines in the terminal (cross-platform).

## Install
```bash
pip install khx_color_lines
```

## CLI

```bash
khx-lines
khx-lines --text "Hello"
khx-lines --colors red green yellow blue magenta
```

## Python API

```python
from khx_color_lines import print_five_lines, colorize_text
print_five_lines("Hello")  # prints 5 lines with default colors

# New in 0.2.0: colorize a single string
print(colorize_text("Hello", "cyan"))
```
