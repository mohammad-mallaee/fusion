import os
from typing import Literal
from shift.helpers.fileListing import FileListing
from shift.helpers.file import File
from shift.helpers.stat import Stat


class Storage:
    def list_files(self, path, file_listing:FileListing) -> None:
        for root, dirs, file_paths in os.walk(path):
            dirs[:] = [d for d in dirs if not file_listing.is_excluded(os.path.join(root, d))]
            for file_path in file_paths:
                file_listing.proccessed += 1
                file_path = os.path.join(root, file_path)
                if file_listing.is_excluded(file_path):
                    continue
                file_stats = os.stat(file_path)
                file = File(
                    file_path,
                    file_listing.get_dest_path(file_path),
                    os.path.basename(file_path),
                    file_stats.st_size,
                    int(file_stats.st_mtime),
                    file_stats.st_mode,
                )
                if file_listing.should_sync(file):
                    file_listing.valid += 1
                    file_listing.total_size += file.size
                    file_listing.files.append(file)
            file_listing.show_progress()

    def should_sync(self, file: File):
        try:
            file_stats = os.stat(file.local_path)
            return file.modified_time > int(file_stats.st_mtime) or file.size != file_stats.st_size
        except FileNotFoundError:
            return True

    def create(self, file: File):
        file.create()
        file.open_for_writing()

    def write(self, file: File, data):
        file.buffer.write(data)

    def save(self, file: File):
        if not file.buffer.closed:
            file.buffer.close()
        file.set_modified_time()


    def exists(self, path):
        return os.path.exists(path)

    def stat(self, path, follow_symlinks = True):
        stats = os.stat(path, follow_symlinks=follow_symlinks)
        return Stat(
            name=os.path.basename(path),
            path=path,
            mode=stats.st_mode,
            modified_time=int(stats.st_mtime),
            size=stats.st_size
        )


    def is_file(self, path) -> Literal[False] | File:
        file_stats = os.stat(path)
        if oct(file_stats.st_mode).startswith("0o10"):
            return File(
                path,
                None,
                os.path.basename(path),
                file_stats.st_size,
                int(file_stats.st_mtime),
                file_stats.st_mode,
            )
        else:
            return False
