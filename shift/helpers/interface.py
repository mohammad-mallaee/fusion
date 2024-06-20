from shift.helpers.stat import Stat
from shift.helpers.file import File


class PathInterface:
    def exists(self, path: str) -> bool:
        pass

    def stat(self, path: str, follow_symlinks=True) -> Stat:
        pass

    def get_file(self, data: str | Stat) -> File:
        pass
