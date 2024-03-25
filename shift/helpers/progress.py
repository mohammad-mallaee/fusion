import time
from shift.helpers.file import File
from shift.helpers.utils import truncate_middle

class Progress:
    def __init__(self, total_size, total_files) -> None:
        self.total_size = total_size
        self.total_transfer = 0
        self.file_transfer = 0
        self.total_files = total_files
        self.files = 0

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()
        self.show_result()

    def start_file(self, file: File):
        self.file_start_time = time.time()
        self.file_transfer = 0
        self.file = file

    def end_file(self, size):
        self.file_end_time = time.time()
        self.files += 1
        self.total_transfer += size
        self.show_file_result()

    def update_file(self, size):
        self.file_transfer += size
        self.total_transfer += size
        self.show_file_progress()

    def show_progress(self):
        pass

    def show_result(self):
        self.end_time = time.time()
        speed = self.total_transfer / 1024 / 1024 / (self.end_time - self.start_time)
        print("-" * 56)
        print(
            f"Done transferring files. Execution time: {round(self.end_time - self.start_time, 2)} second(s)",
            f"\navg. speed: {round(speed, 2)} MB/s\n",
        )

    def show_file_progress(self):
        end = time.time()
        speed = round(self.file_transfer / (end - self.file_start_time) / 1024 / 1024, 1)
        transferred = round(self.file_transfer / 1024 / 1024, 1)
        file_size = round(self.file.size / 1024 / 1024, 1)
        print(
            f'transferring "{truncate_middle(self.file.name, 50)}" -- {transferred}/{file_size}MB -- {speed} MB/s        ',
            end="\r",
        )

    def show_file_result(self):
        end = time.time()
        speed = self.file.size / (end - self.file_start_time) / 1024 / 1024
        print(
            f'\rtransferred "{truncate_middle(self.file.name, 50)}" in {round(end - self.file_start_time, 2)} second(s)                 ',
            f"\navg. speed : {round(speed, 2)} MB/s\n",
        )
