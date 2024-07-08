from shift.device import Device
from shift.storage import Storage
from shift.ui import UserInterface

from shift.helpers.fileListing import SyncList
from shift.helpers.deleteListing import DeleteList
from shift.helpers.progress import Progress

from shift.helpers.constants import PULL, PUSH


def shift(device: Device, ui: UserInterface, args):
    command = args.command

    if command not in [PULL, PUSH]:
        raise Exception("Unknown Command !!")

    source = args.source
    dest = args.destination
    storage = Storage()

    if args.is_file:
        if command == PULL:
            file = device.get_file(source)
            file.local_path = dest
            progress = Progress(file.size, 1)
            progress.start()
            ui.add(progress.window)
            device.pull_files(storage, progress, file)
            progress.end()
        elif command == PUSH:
            file = storage.get_file(source)
            file.remote_path = dest
            progress = Progress(file.size, 1)
            progress.start()
            ui.add(progress.window)
            device.push_files(progress, file)
            progress.end()
    else:
        return _shift_directory(device, storage, args, ui)


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

    def end():
        device.client.__exit__()
        ui.stop()

    file_listing = SyncList(
        get_dest_path, None if args.force else dest_interface.should_sync, local=local
    )
    ui.add(file_listing.window)
    source_interface.list_files(source, file_listing)
    file_listing.window.close()
    if args.dryrun:
        file_listing.show_result(end)

    def progress_callback():
        if args.delete:
            device.reset_connection(True)
            delete_listing = DeleteList(
                get_source_path, source_interface.should_delete, local=local
            )
            ui.add(delete_listing.window)
            dest_interface.list_files(destination, delete_listing)
            dest_interface.delete_files(delete_listing)
            delete_listing.show_result(end)
        else:
            end()

    progress = Progress(file_listing.transfer_size, file_listing.valid, local)
    ui.add(progress.window)
    progress.start()
    if command == PULL:
        device.pull_files(storage, progress, *file_listing.files)
    elif command == PUSH:
        device.push_files(progress, *file_listing.files)
    progress.end(progress_callback)
