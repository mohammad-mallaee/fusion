from shift.device import Device
from shift.storage import Storage
from shift.ui import UserInterface
from time import sleep
import traceback

from shift.helpers.fileListing import SyncList
from shift.helpers.deleteListing import DeleteList
from shift.helpers.progress import Progress
from shift.helpers.utils import write_log
from shift.ui.message import show_message

from shift.helpers.constants import PULL, PUSH, SYNC, DELETE
from config import config


def handle_exception(e, ui):
    sleep(0.2)
    write_log(f"ERROR {ui.exit_event.is_set()}", "".join(traceback.format_exception(e)))
    if not ui.exit_event.is_set():
        show_message("Unexpected Error", str(e), ui=ui, stop=True, wait=0.5)


def shift(device: Device, storage: Storage, ui: UserInterface, args):
    command = args.command
    source = args.source
    dest = args.destination

    try:
        if args.is_file:
            if command == PULL:
                file = device.get_file(source)
                file.local_path = dest
                progress = Progress(file.size, 1)
                progress.start()
                ui.show(progress.window)
                device.pull_files(storage, progress, file)
                progress.end(ui.animate_stop)
            elif command == PUSH:
                file = storage.get_file(source)
                file.remote_path = dest
                progress = Progress(file.size, 1)
                progress.start()
                ui.show(progress.window)
                device.push_files(progress, file)
                progress.end(ui.animate_stop)
        else:
            if command == PULL or command == PUSH:
                return transfer(device, storage, args, ui)
            elif command == SYNC:
                return sync(device, storage, args, ui)
            elif command == DELETE:
                return delete(device, storage, args, ui)

    except Exception as e:
        handle_exception(e, ui)


def transfer(device: Device, storage: Storage, args, ui: UserInterface):
    command = args.command
    local = command == PUSH
    source_interface = device if command == PULL else storage
    dest_interface = storage if command == PULL else device

    def default_validate(path: str):
        if config.conflict_resolution == "sync":
            return dest_interface.should_sync(path)
        if config.conflict_resolution == "force":
            return True
        if config.conflict_resolution == "skip":
            return False

    def get_dest_path(path):
        return path.replace(args.source, args.destination)

    def validate(path):
        if args.force:
            return True
        if args.skip:
            return False
        if args.sync:
            return dest_interface.should_sync(path)
        return default_validate(path)

    file_listing = SyncList(get_dest_path, validate, local=local)
    ui.show(file_listing.window)
    source_interface.list_files(args.source, file_listing)
    if args.dryrun:
        return file_listing.show_result(ui.animate_stop)

    progress = Progress(file_listing.transfer_size, file_listing.valid, local)
    ui.show(progress.window)
    progress.start()
    if command == PULL:
        device.pull_files(storage, progress, *file_listing.files)
    elif command == PUSH:
        device.push_files(progress, *file_listing.files)
    progress.end(ui.animate_stop)


def sync(device: Device, storage: Storage, ui: UserInterface, args):
    source_interface = storage if args.reverse else device
    dest_interface = device if args.reverse else storage
    local = args.reverse

    def get_dest_path(path):
        return path.replace(args.source, args.destination)

    file_listing = SyncList(get_dest_path, dest_interface.should_sync, local=local)
    ui.show(file_listing.window)
    source_interface.list_files(args.source, file_listing)

    def get_source_path(path):
        return path.replace(args.destination, args.source)

    def sync_callback():
        if args.delete:
            try:
                device.reset_connection(True)
                delete_listing = DeleteList(
                    get_source_path, source_interface.should_delete, local=local
                )
                ui.show(delete_listing.window)
                dest_interface.list_files(args.destination, delete_listing)
                if not args.dryrun:
                    dest_interface.delete_files(delete_listing)
                delete_listing.show_result(ui.animate_stop)
            except Exception as e:
                handle_exception(e, ui)
        else:
            ui.animate_stop()

    if args.dryrun:
        file_listing.show_result(sync_callback)
    else:
        progress = Progress(file_listing.transfer_size, file_listing.valid, local)
        ui.show(progress.window)
        progress.start()
        if args.reverse:
            device.pull_files(storage, progress, *file_listing.files)
        else:
            device.push_files(progress, *file_listing.files)
        progress.end(sync_callback)


def delete(device: Device, storage: Storage, ui: UserInterface, args):
    source_interface = storage if args.reverse else device
    dest_interface = device if args.reverse else storage
    local = args.reverse

    def get_source_path(path):
        return path.replace(args.destination, args.source)

    delete_listing = DeleteList(
        get_source_path, source_interface.should_delete, local=local
    )
    ui.show(delete_listing.window)
    dest_interface.list_files(args.destination, delete_listing)
    if not args.dryrun:
        dest_interface.delete_files(delete_listing)
    delete_listing.show_result(ui.animate_stop)
