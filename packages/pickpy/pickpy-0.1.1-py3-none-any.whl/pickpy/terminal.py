import os
import sys
import re
from typing import Optional
from enum import Enum
from typing import Union

class BColors(str, Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CYAN = '\033[36m'
    LIGHTCYAN = '\033[96m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    WHITE = '\033[37m'
    BLACK = '\033[30m'

    # Backgrounds
    BLACK_BG = '\033[40m'
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'
    YELLOW_BG = '\033[43m'
    BLUE_BG = '\033[44m'
    MAGENTA_BG = '\033[45m'
    CYAN_BG = '\033[46m'
    WHITE_BG = '\033[47m'


class Terminal:
    def __init__(self):
        self.name = "Terminal"
        # Best-effort: abilita i colori su Windows
        self._colorama = None
        if os.name == 'nt':
            try:
                import colorama  # type: ignore
                # Attiva modalità VT se possibile e abilita traduzione ANSI su Win32
                if hasattr(colorama, "just_fix_windows_console"):
                    colorama.just_fix_windows_console()
                else:
                    colorama.init(autoreset=False)
                self._colorama = colorama
            except Exception:
                # Se colorama non è presente o fallisce, prosegui senza
                self._colorama = None

    def is_interactive(self) -> bool:
        """Return True if stdin is a TTY (interactive terminal)."""
        try:
            return sys.stdin.isatty()
        except Exception:
            return False

    def supports_color(self) -> bool:
        """Heuristic to check if ANSI colors are supported, overridable via PICKPY_COLOR."""
        # Override esplicito da env: PICKPY_COLOR=1 forza ON, =0 forza OFF
        force = os.environ.get("PICKPY_COLOR")
        if force == '1':
            return True
        if force == '0':
            return False
        if not self.is_interactive():
            # PyCharm Run/Debug console può supportare ANSI; prova a usarlo se hosted
            if os.environ.get("PYCHARM_HOSTED") == "1":
                return True
            return False
        if os.name != 'nt':
            return True
        # Su Windows: se colorama è attivo o terminale moderno
        if self._colorama is not None:
            return True
        env = os.environ
        return any(k in env for k in ("ANSICON", "WT_SESSION")) or env.get("TERM", "").startswith("xterm")

    def colorize(self, text: str, color: Union[str, BColors]) -> str:
        """Wrap text with ANSI color if supported, else return plain text.
        Accetta sia stringhe ANSI sia BColors.
        """
        if not self.supports_color():
            return text
        col = color.value if isinstance(color, BColors) else color
        end = BColors.ENDC.value
        return f"{col}{text}{end}"

    def sanitize(self, text: str) -> str:
        """Remove ANSI escape sequences and control chars to prevent terminal injection."""
        if not isinstance(text, str):
            text = str(text)
        # Remove ANSI escape sequences
        text = re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', text)
        # Remove other control chars except newline and carriage return
        text = ''.join(ch for ch in text if ch in ('\n', '\r') or ord(ch) >= 32)
        return text

    def safe_print(self, text: str, color: Optional[Union[str, BColors]] = None, trusted: bool = False, end: str = "\n") -> None:
        """Print sanitized text; optionally apply color if supported.
        - If trusted is False, sanitize the text.
        - If color is provided, colorize when supported.
        """
        out = text if trusted else self.sanitize(text)
        if color is not None:
            out = self.colorize(out, color)
        print(out, end=end)

    def clear_terminal(self):
        """Clear the terminal screen in a cross-platform way."""
        # Prefer native clear for real TTYs
        if self.is_interactive():
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        # PyCharm hosted: try ANSI clear+home (often supported in Run/Debug console)
        if os.environ.get("PYCHARM_HOSTED") == "1":
            # ESC[2J = clear screen, ESC[H = cursor home
            print("\033[2J\033[H", end="")
            return
        # Fallback: simulate "clear" by pushing content down
        print("\n" * 50)

    # --- Cursor/control helpers to enable low-flicker incremental updates ---
    def _write(self, s: str) -> None:
        """Low-level write to stdout without sanitization or newline."""
        sys.stdout.write(s)
        sys.stdout.flush()

    def hide_cursor(self) -> None:
        """Hide cursor (if terminal likely supports ANSI)."""
        # Evita in ambienti non interattivi sconosciuti
        if self.is_interactive() or os.environ.get("PYCHARM_HOSTED") == "1":
            self._write("\033[?25l")

    def show_cursor(self) -> None:
        """Show cursor back."""
        if self.is_interactive() or os.environ.get("PYCHARM_HOSTED") == "1":
            self._write("\033[?25h")

    def move_cursor_up(self, n: int = 1) -> None:
        if n > 0:
            self._write(f"\033[{n}A")

    def move_cursor_down(self, n: int = 1) -> None:
        if n > 0:
            self._write(f"\033[{n}B")

    def carriage_return(self) -> None:
        self._write("\r")

    def clear_line(self) -> None:
        """Clear current line and move cursor to column 0."""
        self._write("\033[2K\r")
