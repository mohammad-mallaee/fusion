import argparse
from threading import Thread

from shift.ui import UserInterface
from shift.client import AdbClient
from shift.device import Device
from shift.storage import Storage
from shift.index import shift

from shift.path import process_paths
from shift.helpers.constants import PULL, PUSH, SYNC, DELETE
from shift.ui.prompt_list import PromptList
from shift.ui.message import show_message
from config import configure


def transfer(args):
    try:
        c = AdbClient().__enter__()
        c.__exit__()
    except FileNotFoundError:
        show_message("Connection Error", "Couldn't find adb", stop=True, wait=0.5)
    else:
        with AdbClient() as client, UserInterface() as ui:
            storage = Storage()
            online_devices = client.list_devices()

            def start_transfer(device_serial):
                device = Device(device_serial, client)
                command = args.command
                args.is_file = False

                def _start_thread():
                    Thread(target=shift, args=(device, storage, ui, args)).start()

                if command in [PULL, SYNC, DELETE]:
                    process_paths(device, storage, args)
                elif command == PUSH:
                    process_paths(storage, device, args)

                if args.error:
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

    sub_parsers = parser.add_subparsers()

    config_parser = sub_parsers.add_parser("config")
    config_parser.add_argument(
        "command", choices=["edit", "show", "reset", "set", "add", "remove"]
    )
    config_parser.add_argument("key", nargs="?")
    config_parser.add_argument("value", nargs="?")
    config_parser.set_defaults(func=configure)

    pull_parser = sub_parsers.add_parser(PULL)
    pull_parser.add_argument("source")
    pull_parser.add_argument("destination", nargs="?", default="./")
    pull_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    pull_parser.add_argument("-c", "--content", action="store_true")
    pull_resolve_methods = pull_parser.add_mutually_exclusive_group()
    pull_resolve_methods.add_argument("-p", "--skip", action="store_true")
    pull_resolve_methods.add_argument("-s", "--sync", action="store_true")
    pull_resolve_methods.add_argument("-f", "--force", action="store_true")
    pull_parser.set_defaults(func=transfer, command=PULL)

    push_parser = sub_parsers.add_parser(PUSH)
    push_parser.add_argument("source")
    push_parser.add_argument("destination", nargs="?", default="sdcard/")
    push_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    push_parser.add_argument("-c", "--content", action="store_true")
    push_resolve_methods = push_parser.add_mutually_exclusive_group()
    push_resolve_methods.add_argument("-p", "--skip", action="store_true")
    push_resolve_methods.add_argument("-s", "--sync", action="store_true")
    push_resolve_methods.add_argument("-f", "--force", action="store_true")
    push_parser.set_defaults(func=transfer, command=PUSH)

    sync_parser = sub_parsers.add_parser(SYNC)
    sync_parser.add_argument("source")
    sync_parser.add_argument("destination")
    sync_parser.add_argument("-r", "--reverse", action="store_true")
    sync_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    sync_parser.add_argument("-d", "--delete", action="store_true")
    sync_parser.set_defaults(func=transfer, command=SYNC)

    # push_parser = sub_parsers.add_parser(DELETE)
    # push_parser.add_argument("source")
    # push_parser.add_argument("destination")
    # push_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    # push_parser.add_argument("-r", "--reverse", action="store_true")
    # push_parser.set_defaults(func=transfer, command=DELETE)

    args = parser.parse_args()
    if args.command == SYNC or args.command == DELETE:
        args.destination = (
            "./" if args.reverse and args.destination is None else args.destination
        )
    args.func(args)
