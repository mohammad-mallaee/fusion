import argparse
import time

from shift.client import AdbClient
from shift.device import Device
# from pytermgui import tim
from shift.index import shift
from shift.helpers.constants import PULL, PUSH
import os
import stat

from shift.storage import Storage

parser = argparse.ArgumentParser(prog="shift",
    description="keep your phone in sync with your desktop",
    epilog="I'll be happy to take your comments and feedbacks")

parser.add_argument("command", choices=["pull", "push"])
parser.add_argument("source")
parser.add_argument("destination", nargs="?", default="./")
parser.add_argument("-d", "--delete", action="store_true")
parser.add_argument("-f", "--force", action="store_true")
parser.add_argument("-r", "--dryrun", action="store_true")


args = parser.parse_args()

def proccess_paths(interface, source, destination):
    pass



if __name__ == "__main__":
    client = AdbClient()
    storage = Storage()
    online_devices, offline_devices = client.list_devices()
    if len(online_devices) > 1:
        print("select one device")
    elif len(online_devices) == 1:
        device_serial = online_devices[0]
        device = Device(device_serial, client)

        command = args.command
        source_path = args.source
        dest_path = args.destination

        if command == "pull" and device.exists(source_path):
            source_path = os.path.normpath(source_path)
            args.source = source_path
            source_stats = device.stat(source_path, True)
            if stat.S_ISREG(source_stats.mode):
                if os.path.exists(dest_path):
                    dest_stats = storage.stat(dest_path)
                    if stat.S_ISREG(dest_stats.mode):
                        print("pulling a file from", source_path, "to", dest_path)
                        shift(device, args)
                    elif stat.S_ISDIR(dest_stats.mode):
                        dest_file_path = os.path.join(dest_path, source_stats.name)
                        args.destination = dest_file_path
                        shift(device, args)
                        print("pulling a file from", source_path, "to", dest_file_path)
                    else:
                        print("This is not a file or a directory")
                else:
                   print("destination path doesn't exist.")
            elif stat.S_ISDIR(source_stats.mode):
                if os.path.exists(dest_path):
                    dest_stats = storage.stat(dest_path)
                    if stat.S_ISREG(dest_stats.mode):
                        print("You cannot transfer a directory to a file!")
                    elif stat.S_ISDIR(dest_stats.mode):
                        dest_path = os.path.normpath(dest_path)
                        args.destination = dest_path
                        print("pulling a directory from", source_path, "to", dest_path)
                        shift(device, args)
                    else:
                        print("This is not a file or a directory")
                else:
                    print("destination path doesn't exist")
            else:
                print("This is not a file or directory")
        elif command == "push" and os.path.exists(source_path):
            source_path = os.path.normpath(source_path)
            source_stats = storage.stat(source_path)
            args.source = source_path

            if stat.S_ISREG(source_stats.mode):
                if device.exists(dest_path):
                    dest_stats = device.stat(dest_path, True)
                    if stat.S_ISREG(dest_stats.mode):
                        print("pushing a file from", source_path, "to", dest_path)
                    elif stat.S_ISDIR(dest_stats.mode):
                        dest_file_path = os.path.join(dest_path, source_stats.name)
                        print("pushing a file from", source_path, "to", dest_file_path)
                    else:
                        print("This is not a file or a directory")
                else:
                    print("destination path doesn't exist.")
            elif stat.S_ISDIR(source_stats.mode):
                if device.exists(dest_path):
                    dest_stats = device.stat(dest_path, True)
                    if stat.S_ISREG(dest_stats.mode):
                        print("You cannot transfer a directory to a file!")
                    elif stat.S_ISDIR(dest_stats.mode):
                        dest_path = os.path.normpath(dest_path)
                        args.destination = dest_path
                        shift(device, args)
                        print("pulling a directory from", source_path, "to", dest_path)
                    else:
                        print("This is not a file or a directory")
                else:
                    print("destination path doesn't exist")
            else:
                print("This is not a file or directory")



        # source_exists = device.exists(source_path) if command == PULL else os.path.exists(source_path)
        # if not source_exists:
        #     print("Source Does not exist. Check the paths.")
        # elif command == "pull":
            # source_path = os.path.normpath(source_path)
            # source = device.stat(source_path)
            # dest_path = get_destpath()

        # shift(device_serial, "pull","/sdcard", "/Users/mohammad/PhoneBackup")
        # shift(device_serial, "push", "/Users/mohammad/PhoneBackup", "/sdcard")
    else:
        print("There is no device connected")
