from shift.device import Device
from shift.storage import Storage
from shift.ui import UserInterface

from shift.helpers.fileListing import SyncList
from shift.helpers.deleteListing import DeleteList
from shift.helpers.progress import Progress

from shift.helpers.constants import PULL, PUSH


def shift(device: Device, ui: UserInterface, args):
    source = args.source
    command = args.command
    destination = args.destination

    def get_dest_path(path):
        return path.replace(source, destination)

    def get_source_path(path):
        return path.replace(destination, source)

    storage = Storage()
    if command == PULL:
        if args.is_file:
            progress = Progress(source.size, 1)
            file = device.get_file(source)
            device.pull_files(storage, progress, file)
        else:
            file_listing = SyncList(
                get_dest_path,
                None if args.force else storage.should_sync,
            )
            ui.show(file_listing.window)
            device.list_files(source, file_listing)
            if args.dryrun:
                return file_listing.show_result(ui)
            progress = Progress(file_listing.transfer_size, file_listing.valid)
            ui.replace_current(progress.window)
            progress.start()
            device.pull_files(storage, progress, *file_listing.files)
            if args.delete:
                delete_listing = DeleteList(get_source_path, device.should_delete)
                ui.replace_current(delete_listing.window)
                storage.list_files(destination, delete_listing)
                storage.delete_files(delete_listing)
                delete_listing.show_result(ui)
            # ui.replace_current(progress.window)
            # progress.end(ui)

    elif command == PUSH:
        if args.is_file:
            progress = Progress(source.size, 1)
            file = storage.get_file(source)
            device.push_files(progress, file)
        else:
            file_listing = SyncList(
                get_dest_path,
                None if args.force else storage.should_sync,
            )
            ui.show(file_listing.window)
            storage.list_files(source, file_listing)
            if args.dryrun:
                return file_listing.show_result(ui)
            progress = Progress(file_listing.transfer_size, file_listing.valid)
            ui.replace_current(progress.window)
            progress.start()
            device.push_files(progress, *file_listing.files)
            if args.delete:
                delete_listing = DeleteList(get_source_path, storage.should_delete)
                ui.replace_current(delete_listing.window)
                device.list_files(destination, delete_listing)
                device.delete_files(delete_listing)
                delete_listing.show_result(ui)
            # ui.replace_current(progress.window)
            # progress.end(ui)
    else:
        raise Exception("Unknown Command !!")
