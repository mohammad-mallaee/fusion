import os
from fusion.helpers.fileListing import SyncList
from fusion.helpers.deleteListing import DeleteList
from fusion.helpers.file import File
from fusion.helpers.stat import Stat
from fusion.helpers.interface import PathInterface


class Storage(PathInterface):
    def list_files(self, path, file_listing: SyncList) -> None:
        for root, dirs, file_paths in os.walk(path):
            file_listing.current_dir = root
            dirs[:] = [
                d for d in dirs if not file_listing.is_excluded(os.path.join(root, d))
            ]
            for file_path in file_paths:
                file_path = os.path.join(root, file_path)
                if file_listing.is_excluded(file_path):
                    continue
                file_stats = os.stat(file_path)
                file = File(
                    file_path,
                    file_listing.convert_path(file_path),
                    os.path.basename(file_path),
                    file_stats.st_size,
                    int(file_stats.st_mtime),
                    file_stats.st_mode,
                )
                if file_listing.validate(file):
                    file_listing.append(file)
                file_listing.append_process(file)
            file_listing.update_progress()

    def should_sync(self, file: File):
        try:
            file_stats = os.stat(file.local_path)
            return (
                file.modified_time > int(file_stats.st_mtime)
                or file.size != file_stats.st_size
            )
        except FileNotFoundError:
            return True

    def should_delete(self, file: File):
        return not self.exists(file.local_path)

    def create(self, file: File):
        file.create()
        file.open_for_writing()

    def write(self, file: File, data):
        file.buffer.write(data)

    def save(self, file: File):
        if not file.buffer.closed:
            file.buffer.close()
        file.set_modified_time()

    def delete_files(self, delete_listing: DeleteList):
        for file in delete_listing.files:
            try:
                os.remove(file.local_path)
                delete_listing.deleted += 1
                delete_listing.delete_size += file.size
            except Exception:
                pass

    def exists(self, path):
        return os.path.exists(path)

    def stat(self, path, follow_symlinks=True):
        stats = os.stat(path, follow_symlinks=follow_symlinks)
        return Stat(
            name=os.path.basename(path),
            path=path,
            mode=stats.st_mode,
            modified_time=int(stats.st_mtime),
            size=stats.st_size,
        )

    def get_file(self, data: str | Stat):
        stat = data
        if isinstance(data, str):
            stat = self.stat(data)
        return File(stat.path, None, stat.name, stat.size, stat.modified_time)
