from rich.theme import Theme

MAX_UI_WIDTH = 55

app_theme = Theme(
    {
        "app.header": "bold cyan",
        "app.title": "bold #56B6C2",
        "app.subtitle": "italic #8395a7",
        "app.footer": "italic #A1A1A1",
        "menu.enter": "bold green",
        "menu.fast": "bold magenta",
        "menu.footer": "#841515",
        "menu.border": "#576574",
        "menu.action": "white",
        "prompt": "bold #56B6C2",
        "error": "bold red",
        "success": "bold green",
        # receipt themes
        "COLOR_TITLE": "bold #f1c40f",
        "COLOR_BORDER": "#576574",
        "COLOR_HEADER": "bold #2ecc71",
        "COLOR_ITEM": "#f5f6fa",
        "COLOR_PRICE": "#00b894",
        "COLOR_TOTAL":"bold #ff7675",
        "COLOR_MUTED": "#8395a7",
    }
)
