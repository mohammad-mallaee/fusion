from pytermgui import boxes, Window, Button
import os

from shift.helpers.file import File
from shift.ui.container import AlignedContainer
from shift.helpers.utils import truncate_first, get_size
from config import config


class SyncList(AlignedContainer):
    def __init__(
        self, convert_path, validate=None, check_exclution=None, local=False
    ) -> None:
        super().__init__(box=boxes.Box(["", " x ", ""]))
        self.processed: int = 0
        self.valid: int = 0
        self.transfer_size: int = 0
        self.total_size: int = 0
        self.files: list[File] = []
        self._current_dir = ""
        self.local = local
        self.processed_dirs = 0
        self.validate = self.validate if validate is None else validate
        self.convert_path = convert_path
        self.is_excluded = (
            self.is_excluded if check_exclution is None else check_exclution
        )
        self.set_widgets(["", "", "", "", ""])
        self.window = Window(self, box=boxes.Box(["─", "x", "─"]), width=80).set_title(
            "Processing Files"
        )

    @property
    def current_dir(self):
        return self._current_dir

    @current_dir.setter
    def current_dir(self, value):
        self._current_dir = value
        self.processed_dirs += 1

    def append_process(self, file: File):
        self.processed += 1
        self.total_size += file.size

    def append(self, file: File):
        self.files.append(file)
        self.transfer_size += file.size
        self.valid += 1

    def get_last_files(self, max_length=60, count=2):
        last_files = self.files[-count:]
        last_file_names = [
            f.local_path if self.local else f.remote_path for f in last_files
        ]
        last_files_str = [
            "[gray]" + truncate_first(name, max_length) for name in last_file_names
        ]
        return [""] * (count - len(last_files_str)) + last_files_str

    def show_result(self, ui):
        self.window.set_title("File Listing Result")
        progress_str = f"{self.valid}/{self.processed} -- {get_size(self.transfer_size)} / {get_size(self.total_size)}"
        progress_width = len(progress_str)
        dir_width = self.width - progress_width - 3
        dir_str = f"Proccessed {self.processed_dirs} directories"
        self.set_widgets(
            [
                f"{dir_str:<{dir_width}} {progress_str:>{progress_width}}",
            ]
            + self.get_last_files(self.width - 2, 2)
            + [
                "",
                Button(
                    "OK",
                    onclick=lambda _: ui.remove(self.window),
                    self_align=1,
                ),
            ]
        )

    def is_excluded(self, path: str):
        exc_path = path in config["excluded_paths"]
        hidden = not config["hidden_files"] and os.path.basename(path).startswith(".")
        return exc_path or hidden

    def validate(self, path):
        return True

    def update_progress(self):
        progress_str = (
            f"{self.valid}/{self.processed} -- {get_size(self.transfer_size)}"
        )
        progress_width = max(20, len(progress_str))
        dir_width = self.width - progress_width - 3
        dir_str = truncate_first(self.current_dir, dir_width)
        self.set_widgets(
            [
                f"{dir_str:<{dir_width}} {progress_str:>{progress_width}}",
                "",
            ]
            + self.get_last_files(self.width - 2, 3)
        )
