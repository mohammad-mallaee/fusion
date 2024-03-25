import stat
from io import BufferedReader, BufferedWriter
from subprocess import PIPE
from time import time
import os
from pathlib import Path

default_file_mode = 0o755 | stat.S_IFREG


# file properties should be extracted from the actual file.
class File:
    def __init__(
        self,
        local_path,
        remote_path,
        name,
        size,
        modified_time=int(time()),
        mode=default_file_mode,
    ):
        self.remote_path: str = remote_path
        self.local_path: str = local_path
        self.modified_time: int = modified_time
        self.mode: int = mode
        self.size: int = size
        self.buffer: BufferedWriter | BufferedReader
        self.name: str = name

    def __enter__(self):
        self.buffer = self.__open()

    def __exit__(self, *args):
        self.buffer.close()

    def __open(self):
        return open(self.local_path, "rb")

    def create(self):
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)
        flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        os.open(self.local_path, flags)

    def open_for_writing(self):
        self.buffer = open(self.local_path, "wb")

    def set_modified_time(self):
        os.utime(self.local_path, times=(self.modified_time, self.modified_time))
