import argparse
import argcomplete
from threading import Thread

from fusion.helpers.completion import device_completer, sync_completer
from fusion.ui import UserInterface
from fusion.client import AdbClient
from fusion.device import Device
from fusion.storage import Storage
from fusion.index import fusion

from fusion.path import process_paths
from fusion.helpers.constants import PULL, PUSH, SYNC, CLEANUP
from fusion.ui.prompt_list import PromptList
from fusion.ui.message import show_message
from fusion.config import configure
from fusion.helpers.logger import handle_log_command, log
from fusion import __version__

import traceback


def transfer(args):
    if args.command == SYNC or args.command == CLEANUP:
        log.info(
            f"""{args.command}{" dryrun" if args.dryrun else ""}
>> source: {args.source}
>> destination: {args.destination}"""
        )
    else:
        log.info(
            f"""{args.command}{" dryrun" if args.dryrun else ""}{" content" if args.content else ""}{" force" if args.force else ""}{" skip" if args.skip else ""}{" sync" if args.sync else ""}
>> source: {args.source}
>> destination: {args.destination}"""
        )
    try:
        c = AdbClient().__enter__()
        c.__exit__()
    except Exception as e:
        show_message("Connection Error", "Error while starting ADB", stop=True)
        log.error("".join(traceback.format_exception(e)))
    else:
        with AdbClient() as client, UserInterface() as ui:
            storage = Storage()
            online_devices, offline_unauth_devices = client.list_devices()

            def start_transfer(device_serial):
                device = Device(device_serial, client)
                command = args.command
                args.is_file = False

                def _start_thread():
                    Thread(target=fusion, args=(device, storage, ui, args)).start()

                if command in [PULL, SYNC, CLEANUP]:
                    process_paths(device, storage, args)
                elif command == PUSH:
                    process_paths(storage, device, args)

                if args.error:
                    show_message("Path Error", args.error, ui=ui, stop=True)
                    log.error(f"Path_Error\n>> {args.error}")
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
                unavailable_devices_message = (
                    [
                        f"However, {len(offline_unauth_devices)} device(s) are offline or unathorized and cannot be used."
                    ]
                    if len(offline_unauth_devices) > 0
                    else []
                )
                show_message(
                    "Connection Error",
                    "\n".join(
                        [
                            "There is no device connected",
                            "You can check the connected devices using `adb devices` command",
                        ]
                        + unavailable_devices_message
                    ),
                    ui=ui,
                    stop=True,
                )
        ui.exit_event.set()


def main():
    parser = argparse.ArgumentParser(
        prog="fusion",
        description="keep your phone and computer in sync",
        epilog="I'll be happy to take your comments and feedbacks",
    )

    parser.add_argument("-v", "--version", action="store_true")

    sub_parsers = parser.add_subparsers()

    config_parser = sub_parsers.add_parser("config")
    config_parser.add_argument(
        "command", choices=["edit", "show", "reset", "set", "add", "remove"]
    )
    config_parser.add_argument("key", nargs="?")
    config_parser.add_argument("value", nargs="?")
    config_parser.set_defaults(func=configure)

    pull_parser = sub_parsers.add_parser(PULL)
    pull_parser.add_argument("source").completer = device_completer
    pull_parser.add_argument(
        "destination", nargs="?", default="./"
    ).completer = argcomplete.completers.FilesCompleter()
    pull_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    pull_parser.add_argument("-c", "--content", action="store_true")
    pull_resolve_methods = pull_parser.add_mutually_exclusive_group()
    pull_resolve_methods.add_argument("-p", "--skip", action="store_true")
    pull_resolve_methods.add_argument("-s", "--sync", action="store_true")
    pull_resolve_methods.add_argument("-f", "--force", action="store_true")
    pull_parser.set_defaults(func=transfer, command=PULL)

    push_parser = sub_parsers.add_parser(PUSH)
    push_parser.add_argument(
        "source"
    ).completer = argcomplete.completers.FilesCompleter()
    push_parser.add_argument(
        "destination", nargs="?", default="sdcard/"
    ).completer = device_completer
    push_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    push_parser.add_argument("-c", "--content", action="store_true")
    push_resolve_methods = push_parser.add_mutually_exclusive_group()
    push_resolve_methods.add_argument("-p", "--skip", action="store_true")
    push_resolve_methods.add_argument("-s", "--sync", action="store_true")
    push_resolve_methods.add_argument("-f", "--force", action="store_true")
    push_parser.set_defaults(func=transfer, command=PUSH)

    sync_parser = sub_parsers.add_parser(SYNC)
    sync_parser.add_argument("source").completer = sync_completer("source")
    sync_parser.add_argument("destination").completer = sync_completer("destination")
    sync_parser.add_argument("-r", "--reverse", action="store_true")
    sync_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    sync_parser.add_argument("-d", "--delete", action="store_true")
    sync_parser.set_defaults(func=transfer, command=SYNC)

    push_parser = sub_parsers.add_parser(CLEANUP)
    push_parser.add_argument("source")
    push_parser.add_argument("destination")
    push_parser.add_argument("--dry", "--dryrun", dest="dryrun", action="store_true")
    push_parser.add_argument("-r", "--reverse", action="store_true")
    push_parser.set_defaults(func=transfer, command=CLEANUP)

    log_parser = sub_parsers.add_parser("log")
    log_parser.add_argument("command", choices=["open", "copy"])
    log_parser.add_argument("path", nargs="?", default=".")
    log_parser.set_defaults(func=handle_log_command)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.version:
        print(f"v{__version__}")
    elif "command" not in args:
        parser.print_help()
    else:
        if args.command == SYNC or args.command == CLEANUP:
            args.destination = (
                "./" if args.reverse and args.destination is None else args.destination
            )
        args.func(args)


if __name__ == "__main__":
    main()
