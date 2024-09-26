from pytermgui import boxes, Window, Button
import time
from fusion.helpers.file import File
from fusion.helpers.utils import truncate_middle, get_size, get_percent
from fusion.ui.container import AlignedContainer
from fusion.ui.progress_bar import ProgresBar
from fusion.helpers.fileListing import SyncList


class Progress(AlignedContainer):
    def __init__(self, file_listing: SyncList) -> None:
        super().__init__(box=boxes.Box(["", " x ", ""]))
        self.total_size = file_listing.total_size
        self.total_transfer = 0
        self.file_transfer = 0
        self.total_files = len(file_listing.files)
        self.files = 0
        self.file = File("", "", "", 0, 0, 0)
        self.local = file_listing.local
        self.dirs = file_listing.dirs.copy()

        self.progress_bar = ProgresBar()
        self.set_widgets(["", "", "", "", "", ""])
        self.window = (
            Window(self, box="ROUNDED", width=80)
            .center()
            .set_title("Transferring Files")
        )

    def start(self):
        self.start_time = time.time()
        self.update_progress()

    def end(self, callback=None):
        self.end_time = time.time()
        self.window.set_title("Transfer Result")

        def handle_click(_):
            if callback:
                callback()

        elapsed_time = time.time() - self.start_time
        err_msg = (
            "There was no error during transfer"
            if self.total_transfer == self.total_size
            else f"[lightred]There was error during transfer. {self.files} / {self.total_files} of files were transferred"
        )
        self.set_widgets(
            [
                f"Transferred {self.files} file(s) with size of {get_size(self.total_transfer)}",
                (
                    f"Elapsed time was {round(elapsed_time, 1)} seconds and "
                    f'average speed was {get_size(self.total_transfer / elapsed_time, " ")}/s'
                ),
                err_msg,
                "",
                Button("OK", onclick=handle_click, self_align=1),
            ]
        )

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
        self.progress_bar.update(get_percent(self.total_transfer, self.total_size))

        speed = get_size(self.total_transfer / (time.time() - self.start_time), " ")
        files_progress = f"{self.files} / {self.total_files}"
        size_progress = f'{get_size(self.total_transfer, " "):>8} / {get_size(self.total_size, " "):<8}'
        speed_prgress = f"{speed}/s"
        size_width = self.width - len(files_progress) - len(speed_prgress) - 6
        file_progress = f"\\[{get_percent(self.file_transfer, self.file.size):>3}%]"
        file_size_progress = f'{get_size(self.file_transfer, " "):>8} / {get_size(self.file.size, " "):<8}'
        file_path = self.file.local_path if self.local else self.file.remote_path

        self.set_widgets(
            [
                f"{files_progress} {size_progress:^{size_width}} {speed_prgress}",
                "",
                f"{file_progress} {file_size_progress}",
                f"{truncate_middle(file_path, self.width - 2)}",
                "",
                self.progress_bar,
            ]
        )
