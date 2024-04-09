from pytermgui import WindowManager, Window
from shift.helpers.worker import Worker


class UserInterface(WindowManager):
    def __init__(self) -> None:
        super().__init__()
        self.current_window: Window = None
        self.last_window: Window = None
        self.thread = Worker(self.run)

    def __enter__(self):
        self.thread.start()
        return self

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
