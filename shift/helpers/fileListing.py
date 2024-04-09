from pytermgui import Container, boxes, Window

from shift.helpers.file import File
from config import config


class FileListing(Container):
    def __init__(self, get_dest_path, should_sync=None, check_exclution=None) -> None:
        super().__init__(box=boxes.Box(["     ", "  x  ", "     "]))
        self.processed: int = 0
        self.valid: int = 0
        self.transfer_size: int = 0
        self.total_size: int = 0
        self.files: list[File] = []
        self.should_sync = self.should_sync if should_sync is None else should_sync
        self.get_dest_path = get_dest_path
        self.is_excluded = (
            self.is_excluded if check_exclution is None else check_exclution
        )
        self.set_widgets(["", ""])
        self.window = Window(self, box="EMPTY_VERTICAL", width=80).set_title(
            "Processing Files"
        )

    def append_process(self, file: File):
        self.processed += 1
        self.total_size += file.size

    def append(self, file: File):
        self.files.append(file)
        self.transfer_size += file.size
        self.valid += 1

    def is_excluded(self, path):
        return path in config["excluded_paths"]

    def should_sync(self, path):
        return True

    def update_progress(self):
        self.set_widgets(
            [
                f"processed {self.processed} files and transferring {self.valid} of them",
                f"total transfer size: {round(self.transfer_size / 1024 / 1024, 2)} MB",
            ]
        )
