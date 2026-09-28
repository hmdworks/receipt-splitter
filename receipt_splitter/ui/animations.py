from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout.containers import Container, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl

_H_PATTERN = ["-", "┈"]
_V_PATTERN = ["|", "┊"]
_WIDTH = 37


class BoxAnimator:
    def __init__(self, content: list[str]):
        self.content = content
        self.width = _WIDTH
        self._frame = 0

    def render_frame(self) -> HTML:
        """Calculates alternating border characters and constructs each frame of the box."""
        self._frame = (self._frame + 1) % 2

        c1, c2 = _H_PATTERN[self._frame], _H_PATTERN[(self._frame + 1) % 2]
        top_bot = (c1 + c2) * (self.width // 2) + (c1 if self.width % 2 != 0 else "")

        output = [f"<border>┌{top_bot}┐</border>"]

        for i, line in enumerate(self.content):
            l_char = _V_PATTERN[(self._frame + i) % 2]
            r_char = _V_PATTERN[(self._frame + i + 1) % 2]
            output.append(f"<border>{l_char}</border>{line}<border>{r_char}</border>")

        output.append(f"<border>└{top_bot}┘</border>")

        return HTML("\n".join(output))

    def create_padded_container(
        self, padding_left: int = 4, padding_top: int = 1
    ) -> Container:
        menu_window = Window(
            content=FormattedTextControl(
                text=self.render_frame,
                focusable=True,
                show_cursor=False,
            ),
            dont_extend_width=True,
            dont_extend_height=True,
        )

        horizontal_layout = (
            VSplit(
                [
                    Window(width=padding_left),
                    menu_window,
                ]
            )
            if padding_left > 0
            else menu_window
        )

        if padding_top > 0:
            return HSplit(
                [
                    Window(height=padding_top),
                    horizontal_layout,
                ]
            )

        return horizontal_layout
