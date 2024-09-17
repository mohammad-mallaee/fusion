import os


def truncate_middle(text, max_length):
    if len(text) > max_length:
        return text[: (max_length - 3) // 2] + "..." + text[-(max_length - 3) // 2 :]
    return text


def truncate_first(text, max_length):
    return (
        text if len(text) <= max_length else f"...{text[len(text) - max_length + 3:]}"
    )


def can_creat_directory(path: str):
    parts = path.split(os.path.sep)
    for i in range(1, len(parts) + 1):
        p = os.path.join(*parts[:i])
        if os.path.exists(p):
            if os.path.isfile(p):
                return False
        else:
            break
    return True


def get_size(size_in_bytes: int, divider="", precision=2):
    units = ["B", "KB", "MB", "GB", "PB"]
    size: int = size_in_bytes
    i = 0
    while size > 1024:
        size = size / 1024
        i += 1
    sizr_str = f"{size:.{precision}f}{divider}{units[i]}"
    return sizr_str


def get_percent(a, b):
    if b < 0:
        raise ValueError
    if b == 0:
        return 0
    return int(a / b * 100)
