"""Dialog components and UI sessions for Receipt Splitter TUI."""

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Box
from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .rich_helpers import panel_to_ansi
from .styles import MAX_UI_WIDTH


# # ========================================================================================
# ### START MENU
# # ========================================================================================


def format_start_menu_rich() -> Panel:
    table = Table(box=None, expand=True, padding=(0, 1), show_footer=True)

    table.add_row("[menu.enter][ Enter ][menu.enter]", "Start Normal Split")
    table.add_row("[menu.fast][ f ][menu.fast]", "Fast Split")
    table.add_row("[menu.esc][ Esc ][menu.esc]", "Quit")

    menu_group = Group(
        Text("~~* RECEIPT SPLITTER *~~", style="app.header", justify="center"),
        table,
        Text("When splitting with your friends, " 
            "never be a penny off the total ever again!\n", style="app.subtitle", justify="center"),
    )

    return Panel(
        menu_group,
        border_style="menu.border",
        box=box.ROUNDED,
        width=MAX_UI_WIDTH,
    )


def run_start_menu_dialog() -> str:
    kb = KeyBindings()

    @kb.add("enter")
    def _(event):
        event.app.exit(result="normal")

    @kb.add("f")
    def _(event):
        event.app.exit(result="fast")

    @kb.add("escape")
    def _(event):
        event.app.exit(result="quit")

    ansi_content = panel_to_ansi(format_start_menu_rich())

    content_control = FormattedTextControl(
        text=ANSI(ansi_content),
        show_cursor=False,
    )

    layout = Layout(Window(content=content_control))

    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=False,
    )

    return app.run()
