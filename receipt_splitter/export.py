import asyncio
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl


def next_receipt_path(
    directory: str = "receipts",
) -> Path:
    """Finds or makes receipts directory and returns the next
    available receipt file path (e.g. receipts/receipts1.png)."""

    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)

    highest_number = 0

    for path in directory_path.glob("receipt*.png"):
        match = re.fullmatch(r"receipt(\d+)\.png", path.name)

        if match:
            number = int(match.group(1))
            highest_number = max(highest_number, number)

    return directory_path / f"receipt{highest_number + 1}.png"


def receipt_to_png(
    receipt_text: str,
    output_path: str = "receipt.png",
    font_path: str = "fonts/DejaVuSansMono.ttf",
    font_size: int = 20,
    padding: int = 40,
    line_spacing: int = 8,
    text_color: tuple[int, int, int] = (55, 55, 55),
    background_color: tuple[int, int, int] = (255, 255, 255),
) -> tuple[bool, str]:
    """Takes receipt string and creates .png file saved to output path.
    Returns True on success and False on system file error with error message."""

    font = ImageFont.truetype(font_path, font_size)

    if not receipt_text.strip():
        receipt_text = "RECEIPT"

    lines = receipt_text.splitlines()

    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    line_height = font.getbbox("Ag")[3] + line_spacing

    text_width = max(
        dummy.textbbox((0, 0), line, font=font)[2]
        if line else 0
        for line in lines
    )

    image_width = text_width + (padding * 2)
    image_height = line_height * len(lines) + (padding * 2)

    image = Image.new(
        "RGB",
        (image_width, image_height),
        background_color,
    )

    draw = ImageDraw.Draw(image)

    y = padding

    for line in lines:
        draw.text(
            (padding, y),
            line,
            font=font,
            fill=text_color,
        )
        y += line_height

    output = Path(output_path)

    try:
        dir_existed = output.parent.exists()

        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output, format="PNG")

        return True, ""
    
    except OSError as e:
        if output.exists():
            output.unlink()

        if not dir_existed and output.parent.exists() and not any(output.parent.iterdir()):
            try:
                output.parent.rmdir()
            except OSError:
                pass

        err_details = str(e) or type(e).__name__

        return False, err_details


def confirm_save_with_timeout(timeout: float = 30.0) -> bool:
    """Creates an animated timer bar and listens in the background
    for user input to save receipt or times out instead. Returns True if saved."""

    kb = KeyBindings()
    control = FormattedTextControl("[s] Save? [░░░░░░░░░░]", show_cursor=False)
    text_window = Window(content=control)

    @kb.add("s")
    def save(event):
        event.app.exit(result=True)

    bar_length = 32
    interval = 0.05
    steps = int(timeout / interval)

    async def timer(app):
        for i in range(steps):
            await asyncio.sleep(interval)

            blocks = " ▏▎▍▌▋▊▉█"

            progress = (i / steps) * bar_length
            filled = int(progress)
            fraction = int((progress - filled) * 8)

            remaining_spaces = max(0, bar_length - filled - 1)
            bar = "█" * filled + blocks[fraction] + " " * remaining_spaces

            control.text = f"[s] Save? [{bar}]"
            app.invalidate()

        app.exit(result=False)

    app = Application(
        layout=Layout(text_window),
        key_bindings=kb,
        full_screen=False,
        cursor=None,
    )

    async def run():
        asyncio.create_task(timer(app))
        return await app.run_async()

    return asyncio.run(run())
