from rich.console import Console
from rich.style import Style
from rich.theme import Theme

# default green color makes it hard for color-blind people to read highlights in error messages
custom_theme = Theme({"repr.str": Style(color="cyan")})

_console_instance = None


def get_custom_console() -> Console:
    global _console_instance
    if _console_instance is None:
        _console_instance = Console(theme=custom_theme)
    return _console_instance
