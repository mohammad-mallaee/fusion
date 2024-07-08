from pytermgui import Window, Widget


class KeyboardWindow(Window):
    def __init__(self, *widgets: list[Widget], handle_key, **attrs) -> None:
        super().__init__(*widgets, **attrs)
        self.handle_key = handle_key
