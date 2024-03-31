import argparse
import os
import stat
from threading import Thread
from pytermgui import WindowManager

from shift.client import AdbClient
from shift.device import Device

# from shift.index import shift

from shift.helpers.constants import PULL, PUSH
from shift.helpers.interface import PathInterface

from shift.storage import Storage

parser = argparse.ArgumentParser(
    prog="shift",
    description="keep your phone in sync with your desktop",
    epilog="I'll be happy to take your comments and feedbacks",
)

parser.add_argument("command", choices=[PULL, PUSH])
parser.add_argument("source")
parser.add_argument("destination", nargs="?", default="./")
parser.add_argument("-d", "--delete", action="store_true")
parser.add_argument("-f", "--force", action="store_true")
parser.add_argument("-r", "--dryrun", action="store_true")


args = parser.parse_args()


def process_paths(source_interface: PathInterface, dest_interface: PathInterface, args):
    source_path = os.path.normpath(args.source)
    dest_path = os.path.normpath(args.destination)
    args.source = source_path
    args.destination = dest_path

    if not source_interface.exists(source_path):
        print("Source Does not exist. Check the paths.")
        return

    source_stats = source_interface.stat(source_path, True)
    if stat.S_ISREG(source_stats.mode):
        args.is_file = True
        args.source = source_interface.get_file(source_stats)
        if dest_interface.exists(dest_path):
            dest_stats = dest_interface.stat(dest_path)
            if stat.S_ISDIR(dest_stats.mode):
                args.destination = os.path.join(dest_path, source_stats.name)
            elif not stat.S_ISREG(dest_stats.mode):
                print("This is not a file or a directory")
        else:
            print("destination path doesn't exist.")
    elif stat.S_ISDIR(source_stats.mode):
        if dest_interface.exists(dest_path):
            dest_stats = dest_interface.stat(dest_path)
            if stat.S_ISREG(dest_stats.mode):
                print("You cannot transfer a directory to a file!")
            elif not stat.S_ISDIR(dest_stats.mode):
                print("This is not a file or a directory")
        else:
            print("destination path doesn't exist")
    else:
        print("This is not a file or directory")


if __name__ == "__main__":
    with AdbClient() as client, WindowManager() as manager:
        Thread(target=manager.run).start()
        storage = Storage()
        online_devices, offline_devices = client.list_devices()
        if len(online_devices) > 1:
            print("select one device")
        elif len(online_devices) == 1:
            device_serial = online_devices[0]
            device = Device(device_serial, client)

            command = args.command

            if command == "pull":
                process_paths(device, storage, args)
            elif command == "push":
                process_paths(storage, device, args)

            print(args)

            # shift(device_serial, "pull","/sdcard", "/Users/mohammad/PhoneBackup")
            # shift(device_serial, "push", "/Users/mohammad/PhoneBackup", "/sdcard")
        else:
            print("There is no device connected")
        # manager.stop()
