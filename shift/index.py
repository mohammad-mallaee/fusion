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
    storage = Storage()

    if args.is_file:
        if command == PULL:
            progress = Progress(source.size, 1)
            file = device.get_file(source)
            device.pull_files(storage, progress, file)
        elif command == PUSH:
            progress = Progress(source.size, 1)
            file = storage.get_file(source)
            device.push_files(progress, file)
    else:
        return _shift_directory(device, storage, args, ui)


def _shift_directory(device, storage, args, ui):
    source = args.source
    command = args.command
    destination = args.destination

    source_interface = device if command == PULL else storage
    dest_interface = storage if command == PULL else device

    def get_dest_path(path):
        return path.replace(source, destination)

    def get_source_path(path):
        return path.replace(destination, source)

    file_listing = SyncList(
        get_dest_path,
        None if args.force else dest_interface.should_sync,
    )
    ui.show(file_listing.window)
    source_interface.list_files(source, file_listing)
    if args.dryrun:
        return file_listing.show_result(ui)

    delete_listing = None

    def progress_callback(x):
        ui.remove(x)
        if delete_listing:
            ui.show(delete_listing.window)

    progress = Progress(file_listing.transfer_size, file_listing.valid)
    ui.replace_current(progress.window)
    progress.start()
    if command == PULL:
        device.pull_files(storage, progress, *file_listing.files)
    elif command == PUSH:
        device.push_files(progress, *file_listing.files)
    progress.end(callback=progress_callback)
    if args.delete:
        delete_listing = DeleteList(get_source_path, device.should_delete)
        dest_interface.list_files(destination, delete_listing)
        dest_interface.delete_files(delete_listing)
        delete_listing.show_result(ui)
