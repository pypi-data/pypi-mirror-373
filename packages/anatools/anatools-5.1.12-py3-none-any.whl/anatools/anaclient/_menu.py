"""
Menu Navigation Functions
"""

def _arrow_select(options, title="Select an option:"):
    """Display a list of options and allow the user to navigate with ↑/↓ and confirm with Enter.
    Returns the selected element from *options*.
    """
    from anatools.lib.print import print_color
    # Lazy import to avoid circular issues

    current = 0
    last_lines = 0

    def _clear(lines: int):
        if lines > 0:
            _clear_lines(lines)

    def _render():
        nonlocal last_lines
        _clear(last_lines)
        print(f"\n📝 Use arrow keys (↑/↓) to select an option, Enter to confirm.\n\n")
        print_color(f"{title}\n", 'brand')
        for i, opt in enumerate(options):
            prefix = "▶" if i == current else " "
            line = f"  {prefix} {opt}"
            if i == current:
                # Blue background for selected line
                print(f"\033[44m{line}\033[0m")
            else:
                print(line)
        last_lines = len(options) + 6  # title line + options + trailing blank

    _render()
    while True:
        key = _get_key(None)
        if key == "up":
            current = (current - 1) % len(options)
            _render()
        elif key == "down":
            current = (current + 1) % len(options)
            _render()
        elif key == "enter":
            _clear(last_lines)
            return options[current]
        elif key in ("q", "Q"):
            raise KeyboardInterrupt


def _get_key(self, timeout = None):
    """Return a single key press from the user or ``None`` if ``timeout`` expires.

    Parameters
    ----------
    timeout : float | None, optional
        Maximum time in *seconds* to wait for a key press. ``None`` means wait
        indefinitely (the historical behaviour).
    """
    import os
    import sys
    import time
    if os.name == 'nt':  # Windows
        import msvcrt
    else:  # Unix-like systems
        import tty
        import termios
    # ------------------------------------------------------------
    # Windows implementation
    # ------------------------------------------------------------
    if os.name == 'nt':  # Windows
        start = time.time()
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # Handle special keys (arrow keys come in as two-byte sequences)
                if key == b'\xe0':  # Special prefix
                    key = msvcrt.getch()
                    if key == b'H':
                        return 'up'
                    elif key == b'P':
                        return 'down'
                elif key == b'\r':
                    return 'enter'
                elif key == b'q':
                    return 'q'
                elif key == b'r':
                    return 'r'
                elif key == b'\x03':  # Ctrl-C
                    raise KeyboardInterrupt
                return key.decode('utf-8', errors='ignore')

            # No key yet ––– check timeout
            if timeout is not None and (time.time() - start) >= timeout:
                return None
            # Prevent busy-waiting
            time.sleep(0.01)

    # ------------------------------------------------------------
    # POSIX implementation (Linux/macOS, incl. WSL)
    # ------------------------------------------------------------
    else:  # Unix-like systems
        import select  # Local import to avoid Windows issues

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)

            # Use select() so we can honour the timeout without blocking
            if timeout is not None:
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if not rlist:
                    return None  # Timed out – no key press

            ch = sys.stdin.read(1)
            if ch == '\x1b':  # Potential escape sequence (arrow keys)
                # Read next two characters that make up the arrow key code
                ch = sys.stdin.read(1)
                if ch == '[':
                    ch = sys.stdin.read(1)
                    if ch == 'A':
                        return 'up'
                    elif ch == 'B':
                        return 'down'
            elif ch == '\r':
                return 'enter'
            elif ch == 'q':
                return 'q'
            elif ch == '\x03':  # Ctrl-C
                raise KeyboardInterrupt
            return ch.decode() if isinstance(ch, bytes) else ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _clear_lines(n):
    """Clear n lines from the terminal."""
    import sys
    for _ in range(n):
        sys.stdout.write('\033[F')  # Move cursor up
        sys.stdout.write('\033[K')  # Clear line


def paginate_select(options, title="Select an option:", page_size: int = 10):
    """Select from *options* showing *page_size* items per page.

    Uses the existing `_arrow_select` for each page and injects virtual
    "Next…"/"Previous…" entries to navigate alphabetically through the
    collection.
    """
    if not options: raise ValueError("No options provided")
    options = sorted(list(options), key=str.lower)
    start = 0
    while True:
        page = options[start:start + page_size]
        page_entries = page.copy()
        if start > 0: page_entries.insert(0, "Previous…")
        if start + page_size < len(options): page_entries.append("Next…")
        choice = _arrow_select(page_entries, title=f"{title} (showing {start + 1}-{min(start + page_size, len(options))} of {len(options)})")
        if choice == "Next…": start += page_size; continue
        elif choice == "Previous…": start = max(0, start - page_size); continue
        return choice


def print_link(text, url):
    ESC = "\033"
    OSC = f"{ESC}]8;;{url}{ESC}\\"
    ST = f"{ESC}]8;;{ESC}\\"
    print(f"{OSC}{text}{ST}")