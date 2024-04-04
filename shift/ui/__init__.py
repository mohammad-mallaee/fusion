from pytermgui import WindowManager, Window
from threading import Thread


class UserInterface(WindowManager):
    def __init__(self) -> None:
        self.current_window: Window = None
        self.last_window: Window = None
        self.thread = Thread(target=self.run)
        super().__init__()

    def __enter__(self):
        self.start()
        return self

    def start(self):
        self.thread.start()

    def show(self, window: Window):
        self.add(window)
        self.last_window = self.current_window
        self.current_window = window

    def replace(self, window: Window, new_window: Window):
        self.remove(window)
        self.add(new_window)

    def replace_current(self, window: Window):
        self.remove(self.current_window)
        self.add(window)
        self.last_window = self.current_window
        self.current_window = window
