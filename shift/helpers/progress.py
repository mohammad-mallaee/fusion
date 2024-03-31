from pytermgui import Container, Label
import time
from shift.helpers.file import File
from shift.helpers.utils import truncate_middle


class Progress(Container):
    def __init__(self, total_size, total_files, **attrs) -> None:
        super().__init__(**attrs)
        self.total_size = total_size
        self.total_transfer = 0
        self.file_transfer = 0
        self.total_files = total_files
        self.files = 0
        self.set_widgets(["", "", ""])
        self.file = File("", "", "", 0, 0, 0)

    def start(self):
        self.start_time = time.time()
        self.update_progress()

    def end(self):
        self.end_time = time.time()
        self.update_progress()

    def start_file(self, file: File):
        self.file_start_time = time.time()
        self.file_transfer = 0
        self.file = file
        self.update_progress()

    def end_file(self):
        self.file_end_time = time.time()
        self.files += 1
        self.update_progress()

    def update_file(self, size):
        self.file_transfer += size
        self.total_transfer += size
        self.update_progress()

    def update_progress(self):
        speed = round(
            self.total_transfer / 1024 / 1024 / (time.time() - self.start_time), 1
        )
        self.set_widgets(
            [
                Label(
                    (
                        f"transffered {self.files} / {self.total_files} files and "
                        f"{round(self.total_transfer / 1024 / 1024, 1)}MB / {round(self.total_size / 1024 / 1024, 1)}MB"
                    ),
                    parent_align=0,
                ),
                Label(
                    f"transferring {truncate_middle(self.file.name, 40)}",
                    parent_align=0,
                ),
                Label(
                    (
                        f"{round(self.file_transfer / 1024 / 1024, 1)}MB / {round(self.file.size / 1024 / 1024, 1)}MB"
                        f" avg. speed : {speed} MB/s"
                    ),
                    parent_align=0,
                ),
            ]
        )
