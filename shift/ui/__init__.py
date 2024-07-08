import traceback

from typing import Any
from pytermgui import WindowManager
from shift.helpers.worker import Worker
from shift.helpers.utils import write_log


class UserInterface(WindowManager):
    def __init__(self) -> None:
        super().__init__()
        self.worker = Worker(self.run)

    def __enter__(self):
        self.worker.start()
        return self

    def __exit__(self, _: Any, exception: Exception, __: Any) -> bool:
        super().__exit__(_, exception, __)
        if exception:
            write_log("ERROR", traceback.format_exception(exception))
