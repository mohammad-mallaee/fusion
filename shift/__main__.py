import argparse
from threading import Thread
import subprocess
import os

from shift.ui import UserInterface
from shift.client import AdbClient
from shift.device import Device
from shift.storage import Storage
from shift.index import shift

from shift.path import process_paths
from shift.helpers.constants import PULL, PUSH
from shift.ui.prompt_list import PromptList
from shift.ui.message import show_message
from shift.ui.confirm import confirm
from config import config


def configuration(args):
    def _run_config_command(func, *args):
        try:
            func(*args)
            print(config)
        except Exception as e:
            print(e)

    if args.command == "edit":
        app_path = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(app_path, "config.json")
        if config.editor_name is None:
            print("Could not identify your operating system!")
            print("The configuration file is located at:")
            print(config_path)
            print("You can set your editor by running:")
            print("shift config set editor <editor_name>")
        else:
            subprocess.run([config.editor_name, config_path])

    elif args.command == "show":
        print(config)
    elif args.command == "set":
        _run_config_command(config.set, args.key, args.value)
    elif args.command == "add":
        _run_config_command(config.add, args.key, args.value)
    elif args.command == "remove":
        _run_config_command(config.remove, args.key, args.value)
    elif args.command == "reset":
        _run_config_command(config.reset, args.key)


def transfer(args):
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

                def _start_thread():
                    Thread(target=shift, args=(device, storage, ui, args)).start()

                if command == "pull":
                    process_paths(device, storage, args)
                elif command == "push":
                    process_paths(storage, device, args)
                if args.confirmation and not args.dryrun:
                    confirm(
                        "Confirmation",
                        args.error,
                        ui=ui,
                        callback=_start_thread,
                        stop=True,
                    )
                elif args.error and not args.confirmation:
                    show_message("Path Error", args.error, ui=ui, stop=True)
                else:
                    _start_thread()

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
                )
        ui.exit_event.set()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="shift",
        description="keep your phone and computer in sync",
        epilog="I'll be happy to take your comments and feedbacks",
    )
    parser.add_argument("-d", "--delete", action="store_true")
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument("-r", "--dryrun", action="store_true")
    parser.add_argument("-c", "--content", action="store_true")

    sub_parsers = parser.add_subparsers()

    config_parser = sub_parsers.add_parser("config")
    config_parser.add_argument(
        "command", choices=["edit", "show", "reset", "set", "add", "remove"]
    )
    config_parser.add_argument("key", nargs="?")
    config_parser.add_argument("value", nargs="?")
    config_parser.set_defaults(func=configuration)

    pull_parser = sub_parsers.add_parser(PULL)
    pull_parser.add_argument("source")
    pull_parser.add_argument("destination", nargs="?", default="./")
    pull_parser.set_defaults(func=transfer)

    pull_parser = sub_parsers.add_parser(PUSH)
    pull_parser.add_argument("source")
    pull_parser.add_argument("destination", nargs="?", default="sdcard/")
    pull_parser.set_defaults(func=transfer)

    args = parser.parse_args()
    args.func(args)
