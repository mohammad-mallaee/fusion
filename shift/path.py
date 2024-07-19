from os.path import basename, join, normpath, dirname
import stat
from shift.helpers.utils import can_creat_directory
from shift.helpers.interface import PathInterface

from shift.helpers.constants import PULL, PUSH


def process_paths(source_interface: PathInterface, dest_interface: PathInterface, args):
    source_path = normpath(args.source)
    dest_path = normpath(args.destination)

    if args.command == PULL:
        source_path = source_path.lstrip("/")
    elif args.command == PUSH:
        dest_path = "sdcard" if dest_path == "." else dest_path.lstrip("/")

    args.error = None
    args.confirmation = False
    args.source = source_path

    if not source_interface.exists(source_path):
        args.error = "source path does not exist:" + "\n[yellow]" + source_path
        return

    source_stats = source_interface.stat(source_path, True)

    def is_file(source: str, dest: str):
        source = basename(source)
        dest = basename(dest)
        if dest.endswith("/"):
            return False
        if source.find(".") != -1 and dest.find(".") != -1:
            return True
        if source.find(".") != -1 and dest.find(".") == -1:
            return False
        return True

    def process_file_path(file_name):
        file_path = join(dest_path, file_name)
        args.destination = file_path
        if dest_interface.exists(file_path):
            dest_stats = dest_interface.stat(dest_path)
            if stat.S_ISDIR(dest_stats.mode):
                args.error = (
                    "a directory with the same name already exists:"
                    + "\n[yellow]"
                    + file_path
                )
            elif stat.S_ISREG(dest_stats.mode):
                args.confirmation = True
                args.error = (
                    "this file already exists!" + "\ndo you want to replace it ?"
                )
            else:
                args.error = (
                    "destination path is not a file nor a directory:"
                    + "\n[yellow]"
                    + dest_path
                )

    if stat.S_ISREG(source_stats.mode):
        dest_directory = dirname(dest_path) if dirname(dest_path) else "."
        args.is_file = True
        if dest_interface.exists(dest_path):
            dest_stats = dest_interface.stat(dest_path)
            if stat.S_ISDIR(dest_stats.mode):
                process_file_path(source_stats.name)
            elif stat.S_ISREG(dest_stats.mode):
                args.destination = dest_path
                args.confirmation = True
                args.error = (
                    "this file already exists!" + "\ndo you want to replace it ?"
                )
            else:
                args.error = (
                    "destination path is not a file nor a directory:"
                    + "\n[yellow]"
                    + dest_path
                )
        elif dest_interface.exists(dest_directory):
            parent_stats = dest_interface.stat(dest_directory)
            if stat.S_ISDIR(parent_stats.mode):
                ii = is_file(source_path, args.destination)
                file_name = basename(dest_path) if ii else source_stats.name
                dest_path = dest_directory if ii else dest_path
                process_file_path(file_name)
            else:
                args.error = (
                    "destination's parent is not a directory" + "\n[yellow]" + dest_path
                )

        else:
            dest_path = join(dest_path, source_stats.name)
            args.destination = dest_path
            if not can_creat_directory(dest_directory):
                args.error = (
                    "destination directory does not exist! and"
                    + "\ncreating a new directory is not possible:"
                    + "\n[yellow]"
                    + dest_path
                )

    elif stat.S_ISDIR(source_stats.mode):
        if dest_interface.exists(dest_path):
            dest_stats = dest_interface.stat(dest_path)
            if stat.S_ISDIR(dest_stats.mode):
                dest_path = join(dest_path, basename(source_path))
                if dest_interface.exists(dest_path):
                    args.confirmation = True
                    args.error = (
                        "destination already exists!                       "
                        + "\ndirectories will be merged by the predefined rules."
                        + "\ndo you want to continue ?                          "
                    )
                args.destination = dest_path
            elif stat.S_ISREG(dest_stats.mode):
                args.error = "you cannot transfer a directory to a file!"
            else:
                args.error = (
                    "destination path is not a file nor a directory:"
                    + "\n[yellow]"
                    + dest_path
                )
        else:
            args.destination = join(dest_path, basename(source_path))
            if not can_creat_directory(dest_path):
                args.error = (
                    "destination directory does not exist! and"
                    + "\ncreating a new directory is not possible:"
                    + "\n[yellow]"
                    + dest_path
                )
    else:
        args.error = (
            "source path is not a file nor a directory:" + "\n[yellow]" + source_path
        )