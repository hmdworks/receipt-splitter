import io
from rich.console import Console
from rich.panel import Panel

from .styles import app_theme


def panel_to_ansi(panel: Panel) -> str:
    """Converts a Rich Panel or renderable into an ANSI-formatted string for prompt_toolkit."""
    string_io = io.StringIO()
    temp_console = Console(file=string_io, theme=app_theme, force_terminal=True)
    temp_console.print(panel)
    return string_io.getvalue()
