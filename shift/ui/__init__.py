from pytermgui import WindowManager, Window
from threading import Event
from time import sleep


class UserInterface(WindowManager):
    def __init__(self) -> None:
        super().__init__()
        self.exit_event = Event()
        self.current_window: Window = None

    def show(self, window: Window):
        if self.current_window:
            self.current_window.close()
        self.add(window)
        self.current_window = window

    def animate_stop(self, wait=0.5):
        if self.current_window:
            self.current_window.close()
        sleep(wait)
        self.stop()
