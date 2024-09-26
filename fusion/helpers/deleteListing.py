from pytermgui import boxes, Window, Button

from fusion.helpers.file import File
from fusion.helpers.utils import truncate_first, get_size
from fusion.ui.container import AlignedContainer
from fusion.config import config


class DeleteList(AlignedContainer):
    def __init__(
        self, convert_path, validate=None, check_exclution=None, local=False
    ) -> None:
        super().__init__(box=boxes.Box(["", " x ", ""]))
        self.processed: int = 0
        self.valid: int = 0
        self.delete_size: int = 0
        self.total_size: int = 0
        self.deleted = 0
        self.files: list[File] = []
        self.validate = self.validate if validate is None else validate
        self.convert_path = convert_path
        self.is_excluded = (
            self.is_excluded if check_exclution is None else check_exclution
        )
        self.local = local
        self.set_widgets(["", "", "", ""])
        self.window = (
            Window(self, box="ROUNDED", width=80).center().set_title("Processing Files")
        )

    def append_process(self, file: File):
        self.processed += 1
        self.total_size += file.size

    def get_last_files(self, max_length=60, count=2):
        last_files = self.files[-count:]
        last_file_names = [
            f.local_path if self.local else f.remote_path for f in last_files
        ]
        last_files_str = [
            "[gray]" + truncate_first(name, max_length) for name in last_file_names
        ]
        return [""] * (count - len(last_files_str)) + last_files_str

    def append(self, file: File):
        self.files.append(file)
        self.delete_size += file.size
        self.valid += 1

    def show_result(self, callback=None):
        self.window.set_title("Deleting Result")

        def handle_click(_):
            if callback:
                callback()

        self.set_widgets(
            [
                f"Processed {self.processed} files and deleted {self.deleted} of them",
                f'Total delete size: {get_size(self.delete_size, " ")}',
                "",
                Button(
                    "OK",
                    onclick=handle_click,
                    self_align=1,
                ),
            ]
        )

    def is_excluded(self, path):
        return path in config.excluded_paths

    def validate(self, path):
        return False

    def update_progress(self):
        self.set_widgets(
            [
                f"{self.valid} / {self.processed} -- {get_size(self.delete_size)}",
            ]
            + self.get_last_files(self.width - 2, 3)
        )
