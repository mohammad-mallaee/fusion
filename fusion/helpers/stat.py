import stat


class Stat:
    def __init__(
        self, path: str, name: str, mode: int, size: int, modified_time: int
    ) -> None:
        self.path = path
        self.name = name
        self.size = size
        self.mode = mode
        self.modified_time = modified_time
        self.is_file = stat.S_ISREG(mode)
