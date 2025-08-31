import os
import sys

if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix-like systems
    import termios
    import tty

def get_key():
    """Capture single key press."""
    if os.name == 'nt':  # Windows
        key = msvcrt.getch()

        # Check if it's an extended key (arrow keys)
        if key == b'\xe0':
            key = msvcrt.getch()

            match key:
                case b'H': return 'UP'
                case b'P': return 'DOWN'
                case b'K': return 'LEFT'
                case b'M': return 'RIGHT'
                case _: return key.decode('utf-8', errors='ignore')


        elif key == b'\r':
            return 'ENTER'

        return key.decode('utf-8', errors='ignore')

    else:  # Unix-like systems
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            # Check if it's an escape sequence
            if key == '\x1b':
                # Read the next two characters
                seq = sys.stdin.read(2)
                if seq[0] == '[':

                    match seq[1]:
                        case 'A': return 'UP'
                        case 'B': return 'DOWN'
                        case 'C': return 'RIGHT'
                        case 'D': return 'LEFT'
                        case _: return key + seq


            elif key in ('\r', '\n'):
                return 'ENTER'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key