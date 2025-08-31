"""
CLI per pickpy: fornisce una demo di TerminalMenu.

Viene installato come comando `pickpy-demo` tramite entry point console.
"""
from __future__ import annotations

from .menu import TerminalMenu
from .terminal import BColors


def main() -> None:
    menu = TerminalMenu()
    title = "Pickpy Demo"

    def pause():
        try:
            input("Press Enter to continue...")
        except EOFError:
            # Ambienti non interattivi
            pass
        finally:
            menu.terminal.clear_terminal()

    while True:
        choice = menu.select_option(
            ["Start Game", "Options", "Exit"],
            header=f"{title}: Use arrow keys to navigate and press Enter",
            header_color=BColors.OKBLUE,
            selected_color=BColors.WARNING,
            unselected_color=BColors.OKGREEN,
        )

        if choice == "Start Game":
            menu.terminal.safe_print("Starting game... (demo)")
            pause()
        elif choice == "Options":
            opt = menu.get_choice(["Low", "Medium", "High"], header="Select difficulty:")
            menu.terminal.safe_print(f"Difficulty set to: {opt}")
            pause()
        elif choice == "Exit":
            menu.terminal.safe_print("Goodbye!")
            break


if __name__ == "__main__":
    main()

