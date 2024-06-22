import stat
from io import BufferedReader, BufferedWriter
from time import time
import os

default_file_mode = 0o755 | stat.S_IFREG


# file properties should be extracted from the actual file.
class File:
    def __init__(
        self,
        local_path: str,
        remote_path: str,
        name: str,
        size: int,
        modified_time=int(time()),
        mode: int = default_file_mode,
    ):
        self.remote_path = remote_path
        self.local_path = local_path
        self.modified_time = modified_time
        self.mode = mode
        self.size = size
        self.name = name
        self.buffer: BufferedWriter | BufferedReader = None

    def __enter__(self):
        self.buffer = self.__open()

    def __exit__(self, *args):
        self.buffer.close()

    def __open(self):
        return open(self.local_path, "rb")

    def create(self):
        os.makedirs(os.path.dirname(self.local_path) or ".", exist_ok=True)
        flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        os.open(self.local_path, flags)

    def open_for_writing(self):
        self.buffer = open(self.local_path, "wb")

    def set_modified_time(self):
        os.utime(self.local_path, times=(self.modified_time, self.modified_time))
