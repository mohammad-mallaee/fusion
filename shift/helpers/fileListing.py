from shift.helpers.file import File
from config import config

class FileListing:
    def __init__(self, get_dest_path, should_sync=None, check_exclution=None, show_progress=None) -> None:
        self.proccessed: int = 0
        self.valid: int = 0
        self.transfer_size: int = 0
        self.total_size: int = 0
        self.files: list[File] = []
        self.should_sync = self.should_sync if should_sync is None else should_sync
        self.get_dest_path = get_dest_path
        self.is_excluded = self.is_excluded if check_exclution is None else check_exclution
        self.show_progress = self.show_progress if show_progress is None else show_progress

    def is_excluded(self, path):
        return path in config["excluded_paths"]

    def should_sync(self, path):
        return True

    def show_progress(self):
        print(f"Processed {self.proccessed} files, transferring {self.valid} of them.", end="\r")
