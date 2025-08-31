# pickpy: Lightweight Terminal Menus for Python

![License Badge](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-%3E=3.10-green.svg)

## 📝 Usage example
Here's a quick example to spark your imagination:
```python
from pickpy.menu import TerminalMenu

options = ["Start Game", "Options", "Exit"]
menu = TerminalMenu()

choice = menu.select_option(
    options, 
    header="Pickpy Demo: Use arrow keys to navigate and press Enter"
)

match choice:
    case "Start Game":
        print("Starting game... (demo)")
    case "Options":
        print("Opening options...")
    case "Exit":
        print("Exiting...")
```

<img src="images/pickpy.gif" loop=infinite />


---

Are you tired of clunky, hard-to-use terminal menus? Want to build sleek, interactive command-line interfaces with minimal effort? Look no further — **pickpy** is here to revolutionize how you create terminal menus in Python!

## 🎨 Custom colors
You can customize colors easily using ANSI strings or the built-in BColors enum:
```python
from pickpy.menu import TerminalMenu
from pickpy.terminal import BColors

menu = TerminalMenu()

# Interactive menu with custom colors
choice = menu.select_option(
    ["Start", "Options", "Exit"],
    header="Custom Colors Demo",
    header_color=BColors.OKBLUE,
    selected_color=BColors.WARNING,
    unselected_color=BColors.OKGREEN,
)

# Fallback (non-TTY) also supports custom colors via get_choice
choice = menu.get_choice(
    ["Red", "Green", "Blue"],
    header="Pick a color:",
    header_color=BColors.WARNING,
    option_color=BColors.OKGREEN,
)

# Customize input prompt color
match choice:
    case "Red":
        menu.terminal.safe_print("You picked Red!", color=BColors.FAIL)
    case "Green":
        menu.terminal.safe_print("You picked Green!", color=BColors.OKGREEN)
    case "Blue":
        menu.terminal.safe_print("You picked Blue!", color=BColors.OKBLUE)
```
![pickpy_colors.gif](images/pickpy_colors.gif)


## 🚀 Why choose pickpy?

- **Lightweight & Easy to Use:** Designed for simplicity, perfect for quick prototyping or production use.
- **Flexible & Customizable:** Supports color, navigation via arrow keys, and safe terminal handling – all out of the box.
- **Cross-Platform Compatibility:** Works smoothly on Windows, macOS, and Linux.
- **Extensible & Modular:** Built with best practices to allow easy future enhancements.

## 🎯 What can you do with pickpy?

- Build interactive menus with arrow key navigation
- Present choices with color themes and style
- Support non-interactive environments gracefully
- Easily extend or embed into your scripts or tools

## 📦 Installation

Getting started is a snap:

```bash
pip install pickpy
```
