from .terminal import Terminal, BColors
from .keyboard import get_key
from typing import Optional, Union

class TerminalMenu:
    def __init__(self):
        self.terminal = Terminal()

    def get_input(self, prompt: str='Please add your input: ', *, prompt_color: Optional[Union[str, BColors]] = BColors.HEADER) -> str:
        """Get user input with a prompt.
        - prompt_color: color of the prompt
        """
        self.terminal.clear_terminal()
        self.terminal.safe_print(prompt, color=prompt_color)
        return input("> ")

    def get_choice(self, options, header="Menu Options:", *, header_color: Optional[Union[str, BColors]] = BColors.HEADER, option_color: Optional[Union[str, BColors]] = None, error_color: Optional[Union[str, BColors]] = None):
        """Display a list of options and get user choice.
        - header_color: color of the header
        - option_color: color for the options
        - error_color: color for error messages
        """
        self.terminal.clear_terminal()
        self.terminal.safe_print(header, color=header_color)
        for idx, option in enumerate(options, start=1):
            self.terminal.safe_print(f"{idx}. {option}", color=option_color, trusted=False)

        while True:
            try:
                choice = int(input("Select an option by number: "))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                else:
                    self.terminal.safe_print(f"Please enter a number between 1 and {len(options)}.", color=error_color)
            except ValueError:
                self.terminal.safe_print("Invalid input. Please enter a number.", color=error_color)

    def select_option(self, options, header="Use arrow keys to navigate and press Enter to select:", *, header_color: Optional[Union[str, BColors]] = BColors.HEADER, selected_color: Optional[Union[str, BColors]] = BColors.OKCYAN, unselected_color: Optional[Union[str, BColors]] = None):
        """Interactive menu for selecting an option. Falls back to numeric selection if no TTY.
        - header_color: color of the header
        - selected_color: color for the selected option
        - unselected_color: color for unselected options (None for default terminal color)
        """
        # Fallback per console non interattive (es. PyCharm Python Console)
        is_tty = getattr(self.terminal, "is_interactive", lambda: False)()
        if not is_tty:
            return self.get_choice(
                options,
                header="(No TTY) " + (header or "Menu Options:"),
                header_color=header_color,
                option_color=unselected_color,
            )

        term = self.terminal
        idx = 0

        def render_line(i: int, selected: bool):
            prefix = "> " if selected else "  "
            color = selected_color if selected else unselected_color
            text = f"{prefix}{options[i]}"
            # Sanitize to avoid injection; colorize if requested
            plain = term.sanitize(text)
            out = term.colorize(plain, color) if color is not None else plain
            term.clear_line()
            term._write(out)

        try:
            term.hide_cursor()
            term.clear_terminal()
            term.safe_print(header, color=header_color)
            for i in range(len(options)):
                render_line(i, i == idx)
                term._write("\n")

            while True:
                key = get_key()
                if key == 'UP':
                    new_idx = (idx - 1) % len(options)
                elif key == 'DOWN':
                    new_idx = (idx + 1) % len(options)
                elif key == 'ENTER':
                    return options[idx]
                else:
                    continue

                if new_idx == idx:
                    continue

                # move to the row previously selected
                lines_up = (len(options) - idx)
                term.move_cursor_up(lines_up)
                render_line(idx, selected=False)

                # Spostati alla riga della nuova selezione
                delta = new_idx - idx
                if delta > 0:
                    term.move_cursor_down(delta)
                elif delta < 0:
                    term.move_cursor_up(-delta)
                render_line(new_idx, selected=True)

                tail = (len(options) - new_idx)
                if tail > 0:
                    term.move_cursor_down(tail)
                idx = new_idx
        finally:
            term.show_cursor()
