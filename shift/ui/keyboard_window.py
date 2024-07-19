from pytermgui import Window, Widget


class KeyboardWindow(Window):
    def __init__(self, *widgets: list[Widget], handle_key, **attrs) -> None:
        super().__init__(*widgets, **attrs)
        self._handle_key = handle_key

    def handle_key(self, key: str) -> bool:
        if super().handle_key(key):
            return True
        return self._handle_key(key)
