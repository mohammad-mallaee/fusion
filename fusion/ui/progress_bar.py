from typing import Any
from pytermgui import Widget, tim
from math import floor


class ProgresBar(Widget):
    def __init__(self, fill_char="█", **attrs: Any) -> None:
        super().__init__(**attrs)
        self.progress = 0
        self.fill_char = fill_char

    def update(self, value):
        self.progress = max(min(value, 100), 0)

    def get_lines(self) -> list[str]:
        bar_width = self.width - 6 - 1 - 2 - 2
        fill_chars = self.fill_char * floor(bar_width / 100 * self.progress)
        empty_chars = self.fill_char * (bar_width - len(fill_chars))
        progress = tim.parse(f"[#05eb59]{fill_chars}[#383838]{empty_chars}")
        progress = f"[{self.progress:>3}%] ｜{progress}｜"
        return [progress]
