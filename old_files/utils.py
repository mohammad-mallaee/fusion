import os

from pathlib import Path

class PathError(Exception):
    pass

def confirm(title: str):
    confirm_text = input(title)
    lower = confirm_text.lower()
    if lower == "y" or lower == "yes":
        return True
    else:
        return False


def is_dir(path):
        _, extention = os.path.splitext(path)
        return extention == ""


def get_dir_path(path: str):
    if not is_dir(path):
        dir = os.path.dirname(path)
        path = dir
    return path

def get_file_name(path):
    return os.path.basename(path)


def join_file_dir(dir_path, file_path):
    return os.path.join(dir_path, get_file_name(file_path))


def check_paths(client, source, destination):
    command = None
    if client.exists(source):
        command = "pull"
        destination = destination if destination is not None else "./"
        dir = get_dir_path(destination)
        if not os.path.exists(dir) :
            print(f"Destination directory '{dir}' does not exist on your computer.")
            confirmation = confirm("do you want to create it (y/n) ? ")
            if confirmation:
                Path(dir).mkdir(parents=True)
            else:
                raise PathError("Exit.")
    elif os.path.exists(source):
        command = "push"
        destination = destination if destination is not None else "/sdcard"
        dir = get_dir_path(destination)
        if not client.exists(dir):
            print(f"Destination directory '{dir}' does not exist on your phone.")
            confirmation = confirm("do you want to create it (y/n) ? ")
            if confirmation:
               client.mkdir(dir)
            else:
                raise PathError("Exit.")
    else:
        raise PathError(f"Source {source} does not exist")
    return command, source, destination
