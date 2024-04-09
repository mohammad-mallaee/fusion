from pytermgui import Window, Container
from typing import Any


class KeyboardWindow(Window):
    def __init__(self, *widgets: Any, handle_key: Container, **attrs) -> None:
        super().__init__(*widgets, **attrs)
        self.handle_key = handle_key
