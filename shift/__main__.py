import argparse
import os
import stat
from threading import Thread

from shift.ui import UserInterface
from shift.client import AdbClient
from shift.device import Device
from shift.storage import Storage


from shift.index import shift

from shift.helpers.constants import PULL, PUSH
from shift.helpers.interface import PathInterface
from shift.ui.prompt_list import PromptList
from shift.ui.message import show_message

parser = argparse.ArgumentParser(
    prog="shift",
    description="keep your phone and computer in sync",
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

    if args.command == PULL:
        source_path = source_path.lstrip("/")
    elif args.command == PUSH:
        dest_path = "sdcard" if dest_path == "." else dest_path.lstrip("/")

    args.source = source_path
    args.destination = dest_path
    args.error = None

    if not source_interface.exists(source_path):
        args.error = "source path does not exist:" + "\n[yellow]" + source_path
        return

    source_stats = source_interface.stat(source_path, True)
    if stat.S_ISREG(source_stats.mode):
        args.is_file = True
        if dest_interface.exists(dest_path):
            dest_stats = dest_interface.stat(dest_path)
            if stat.S_ISDIR(dest_stats.mode):
                args.destination = os.path.join(dest_path, source_stats.name)
            elif not stat.S_ISREG(dest_stats.mode):
                args.error = (
                    "destination path is not a file nor a directory:"
                    + "\n[yellow]"
                    + dest_path
                )
        else:
            args.error = "destination path does not exist:" + "\n[yellow]" + dest_path
    elif stat.S_ISDIR(source_stats.mode):
        if dest_interface.exists(dest_path):
            dest_stats = dest_interface.stat(dest_path)
            if stat.S_ISREG(dest_stats.mode):
                args.error = "You cannot transfer a directory to a file!"
            elif not stat.S_ISDIR(dest_stats.mode):
                args.error = (
                    "destination path is not a file nor a directory:"
                    + "\n[yellow]"
                    + dest_path
                )
        else:
            args.error = "destination path does not exist:" + "\n[yellow]" + dest_path
    else:
        args.error = (
            "source path is not a file nor a directory:" + "\n[yellow]" + source_path
        )


if __name__ == "__main__":
    try:
        c = AdbClient().__enter__()
        c.__exit__()
    except FileNotFoundError:
        show_message("Connection Error", "Couldn't find adb", stop=True, wait=0.5)
    else:
        with AdbClient() as client, UserInterface() as ui:
            storage = Storage()
            online_devices, offline_devices = client.list_devices()

            def start_transfer(device_serial):
                device = Device(device_serial, client)
                command = args.command
                args.is_file = False

                if command == "pull":
                    process_paths(device, storage, args)
                elif command == "push":
                    process_paths(storage, device, args)
                if args.error:
                    show_message("Path Error", args.error, wait=0.5, manager=ui)

                Thread(target=shift, args=(device, storage, ui, args)).start()

            if len(online_devices) > 1:
                PromptList(
                    ui,
                    [f"{d[2]} ({d[0]})" for d in online_devices],
                    "Select a device",
                    lambda index: start_transfer(online_devices[index][0]),
                )
            elif len(online_devices) == 1:
                start_transfer(online_devices[0][0])
            else:
                show_message(
                    "Connection Error",
                    "\n".join(
                        [
                            "There is no device connected",
                            "You can check the connected devices using `adb devices` command",
                        ]
                    ),
                    ui=ui,
                    stop=True,
                    wait=0.5,
                )
        ui.exit_event.set()
