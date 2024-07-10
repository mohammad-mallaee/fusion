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

from shift.helpers.constants import PULL, PUSH


def shift(device: Device, storage: Storage, ui: UserInterface, args):
    command = args.command

    if command not in [PULL, PUSH]:
        raise Exception("Unknown Command !!")

    source = args.source
    dest = args.destination

    if args.is_file:
        if command == PULL:
            file = device.get_file(source)
            file.local_path = dest
            progress = Progress(file.size, 1)
            progress.start()
            ui.show(progress.window)
            device.pull_files(storage, progress, file)
            progress.end()
        elif command == PUSH:
            file = storage.get_file(source)
            file.remote_path = dest
            progress = Progress(file.size, 1)
            progress.start()
            ui.show(progress.window)
            device.push_files(progress, file)
            progress.end()
    else:
        try:
            return _shift_directory(device, storage, args, ui)
        except Exception as e:
            sleep(0.2)
            if not ui.exit_event.is_set():
                write_log("ERROR", "".join(traceback.format_exception(e)))
                show_message("Error in Shift", str(e), ui=ui, stop=True, wait=0.5)


def _shift_directory(device: Device, storage: Storage, args, ui: UserInterface):
    source = args.source
    command = args.command
    destination = args.destination

    local = command == PUSH
    source_interface = device if command == PULL else storage
    dest_interface = storage if command == PULL else device

    def get_dest_path(path):
        return path.replace(source, destination)

    def get_source_path(path):
        return path.replace(destination, source)

    def end(wait=0):
        sleep(wait)
        device.client.__exit__()
        ui.stop()

    file_listing = SyncList(
        get_dest_path, None if args.force else dest_interface.should_sync, local=local
    )
    ui.show(file_listing.window)
    source_interface.list_files(source, file_listing)
    if args.dryrun:
        return file_listing.show_result(lambda: end(0.4))

    def progress_callback():
        if args.delete:
            device.reset_connection(True)
            delete_listing = DeleteList(
                get_source_path, source_interface.should_delete, local=local
            )
            ui.show(delete_listing.window)
            dest_interface.list_files(destination, delete_listing)
            dest_interface.delete_files(delete_listing)
            delete_listing.show_result(end)
        else:
            end()

    progress = Progress(file_listing.transfer_size, file_listing.valid, local)
    ui.show(progress.window)
    progress.start()
    if command == PULL:
        device.pull_files(storage, progress, *file_listing.files)
    elif command == PUSH:
        device.push_files(progress, *file_listing.files)
    progress.end(progress_callback)
