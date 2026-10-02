"""Dialog components and UI sessions for Receipt Splitter TUI."""

import inspect
import sys

from decimal import Decimal

from prompt_toolkit.application import Application, get_app
from prompt_toolkit.formatted_text import ANSI, HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame, TextArea

from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from receipt_splitter.core.calculator import calculate_subtotal, calculate_receipt_total, calculate_people_total
from receipt_splitter.core.models import ChargeType, Receipt
from .rich_helpers import panel_to_ansi
from .styles import MAX_UI_WIDTH


# # ========================================================================================
# ### START MENU
# # ========================================================================================


def format_start_menu_rich() -> Panel:
    table = Table(box=None, expand=True, padding=(0, 1), show_footer=True)

    table.add_row("[menu.enter][ Enter ][menu.enter]", "Start Normal Split")
    table.add_row("[menu.fast][ f ][menu.fast]", "Fast Split")

    menu_group = Group(
        Text("~~* RECEIPT SPLITTER *~~", style="app.header", justify="center"),
        Text(""),
        Text("When splitting with your friends, " 
            "never be a penny off the total ever again!", style="app.subtitle", justify="center"),
        table,
        Text("Press Esc to quit anytime", style="menu.footer", justify="center")
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


# # ========================================================================================
# ### RECEIPT
# # ========================================================================================


def format_receipt_rich(receipt: Receipt):
    renderables = []

    if receipt.people:
        people_str = "  •  ".join(receipt.people.keys())
        renderables.append(
            Panel(
                Text(people_str, style="COLOR_ITEM", justify="center"),
                border_style="COLOR_BORDER",
                box=box.ROUNDED,
            )
        )

    if receipt.items:
        table = Table(box=None, expand=True, padding=(0, 1))

        table.add_column(width = 2 * MAX_UI_WIDTH // 3, justify="left")
        table.add_column(width = MAX_UI_WIDTH // 3, justify="right")

        for item in receipt.items.values():
            table.add_row(item.name, f"£ {item.price:.2f}\n")

        renderables.append(
            Panel(
                table,
                border_style="COLOR_BORDER",
                box=box.ROUNDED,
            )
        )

        subtotal = calculate_subtotal(receipt)
        total = calculate_receipt_total(receipt)

        summary_table = Table(box=None, expand=True)
        summary_table.add_column(width = 2 * MAX_UI_WIDTH // 3, justify="left")
        summary_table.add_column(width = MAX_UI_WIDTH // 3, justify="right")
        
        summary_table.add_row("Subtotal", f"£ {subtotal:.2f}")

        if receipt.service_rate > Decimal("0"):
            summary_table.add_row(f"Service charge ({receipt.service_rate * 100}%)", f"£ {(subtotal * receipt.service_rate):.2f}")

        for charge in receipt.extra_charges:
            label = charge.label or "Charge"
            if charge.type == ChargeType.PERCENTAGE:
                amount = subtotal * (charge.value / Decimal("100"))
                summary_table.add_row(f"{label} ({charge.value}%)", f"£ {amount:.2f}")
            else:
                summary_table.add_row(label, f"£ {charge.value:.2f}")

        summary_table.add_row("Total", f"£ {total:.2f}")

        renderables.append(
            Panel(summary_table, border_style="COLOR_MUTED", box=box.ROUNDED)
        )

    if not renderables:
        group = Group(
            Text("No receipt details added.", style="COLOR_MUTED", justify="center")
        )
    else:
        group = Group(*renderables)

    return Panel(
        group,
        title="✦ RECEIPT SUMMARY ✦",
        border_style="COLOR_BORDER",
        box=box.ROUNDED,
        width=MAX_UI_WIDTH,
    )

def clear_terminal():
    """Clears the terminal screen and resets cursor to top-left."""
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()


def run_interactive_rich_session(
    title: str,
    render_func,
    receipt_data,
    prompt: str = "> ",
    validator=None,
    on_submit=None,
    is_done_check=None,
    exit_on_submit: bool = False,
):
    """Runs a prompt_toolkit loop with internal input padding."""
    clear_terminal()

    kb = KeyBindings()
    error_control = FormattedTextControl(text="")

    content_control = FormattedTextControl(
        text=ANSI(panel_to_ansi(render_func(receipt_data)))
    )

    input_field = TextArea(
        height=3,
        prompt=prompt,
        multiline=False,
        wrap_lines=False,
    )

    collected_results = []

    @kb.add("escape")
    def _exit(event):
        event.app.exit(exception=KeyboardInterrupt)

    def _accept(buff):
        user_input = buff.text.strip()
        app = get_app()

        if is_done_check and is_done_check(user_input):
            app.exit(result=collected_results)
            return

        if validator:
            try:
                sig = inspect.signature(validator)
                num_params = len(sig.parameters)

                if num_params > 1:
                    validated_val = validator(user_input, receipt_data.items)
                else:
                    validated_val = validator(user_input)

                collected_results.append(validated_val)

                if on_submit:
                    on_submit(receipt_data, validated_val)

                if exit_on_submit:
                    app.exit(result=validated_val)
                    return

                content_control.text = panel_to_ansi(
                    render_func(receipt_data)
                )
                error_control.text = ""
                buff.text = ""

            except ValueError as err:
                error_control.text = HTML(f"<style fg='ansired'>   ✗ {str(err)}</style>")
                buff.text = ""
        else:
            if on_submit:
                on_submit(receipt_data, user_input)
            if exit_on_submit:
                app.exit(result="done")
                return
            content_control.text = ANSI(panel_to_ansi(
                render_func(receipt_data))
            )
            buff.text = ""

    input_field.buffer.accept_handler = _accept

    padded_input = VSplit([
        Window(width=1),
        input_field,
        Window(width=1),
    ])

    main_stack = HSplit([
        Window(content=content_control, dont_extend_height=True, width=MAX_UI_WIDTH),
        Frame(padded_input, title=title, width=MAX_UI_WIDTH),
        Window(
            content=error_control,
            height=1,
            dont_extend_height=True,
            width=MAX_UI_WIDTH,
        ),
    ])

    bounded_layout = Layout(
        VSplit([
            main_stack,
            Window(),
        ]),
        focused_element=input_field,
    )

    app = Application(
        layout=bounded_layout,
        key_bindings=kb,
        full_screen=False,
    )

    return app.run()
