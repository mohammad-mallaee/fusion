from pytermgui import Container, boxes, Window, Button

from shift.helpers.file import File
from config import config


class DeleteList(Container):
    def __init__(self, convert_path, validate=None, check_exclution=None) -> None:
        super().__init__(box=boxes.Box(["     ", "  x  ", "     "]))
        self.processed: int = 0
        self.valid: int = 0
        self.delete_size: int = 0
        self.total_size: int = 0
        self.files: list[File] = []
        self.validate = self.validate if validate is None else validate
        self.convert_path = convert_path
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
        self.delete_size += file.size
        self.valid += 1

    def show_result(self, ui):
        self.window.set_title("Delete Listing Result")
        self.set_widgets(
            [
                f"processed {self.processed} files and deleting {self.valid} of them",
                f"total delete size: {round(self.delete_size / 1024 / 1024, 2)} MB",
                Button("OK", onclick=lambda: ui.remove(self.window) if ui else None),
            ]
        )

    def is_excluded(self, path):
        return path in config["excluded_paths"]

    def validate(self, path):
        return False

    def update_progress(self):
        self.set_widgets(
            [
                f"processed {self.processed} files and deleting {self.valid} of them",
                f"total delete size: {round(self.delete_size / 1024 / 1024, 2)} MB",
            ]
        )
