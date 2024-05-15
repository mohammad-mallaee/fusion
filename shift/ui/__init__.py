import traceback

from typing import Any
from pytermgui import WindowManager, Window
from shift.helpers.worker import Worker
from shift.helpers.utils import write_log


class UserInterface(WindowManager):
    def __init__(self) -> None:
        super().__init__()
        self.current_window: Window = None
        self.last_window: Window = None
        self.worker = Worker(self.run)

    def __enter__(self):
        self.worker.start()
        return self

    def __exit__(self, _: Any, exception: Exception, __: Any) -> bool:
        if not exception:
            return
        from shift.ui.message import show_message

        write_log("ERROR", traceback.format_exception(exception))
        show_message("Enexpected Error", exception)

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
