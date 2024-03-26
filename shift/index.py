from shift.device import Device
from shift.storage import Storage

from shift.helpers.fileListing import FileListing
from shift.helpers.progress import Progress

from shift.helpers.constants import PULL, PUSH

def shift(device: Device, args):
    source = args.source
    command = args.command
    destination = args.destination

    def get_dest_path(path):
        return path.replace(source, destination)

    storage = Storage()
    print()

    if command == PULL:
        file = device.is_file(source)
        if file:
            file.local_path = get_dest_path(file.remote_path)
            progress = Progress(file.size, 1)
            device.pull_files(storage, progress, file)
        else:
            file_listing = FileListing(get_dest_path, storage.should_sync)
            device.list_files(source, file_listing)
            progress = Progress(file_listing.total_size, file_listing.valid)
            progress.start()
            print(f"Total files to transfer: {len(file_listing.files)}                      ")
            print(f"Total size to transfer: {round(file_listing.transfer_size / 1024 / 1024, 2)} MB /",
                round(file_listing.transfer_size / 1024 / 1024 / 30 / 60, 2),
                "minutes")
            print("-" * 56)
            device.pull_files(storage, progress, *file_listing.files)
            progress.end()
    elif command == PUSH:
        file = storage.is_file(source)

        if file:
            file.remote_path = get_dest_path(file.local_path)
            progress = Progress(file.size, 1)
            device.push_files(progress, file)
        else:
            file_listing = FileListing(get_dest_path, device.should_sync)
            storage.list_files(source, file_listing)
            progress = Progress(file_listing.total_size, file_listing.valid)
            progress.start()
            print(f"Total files to transfer: {len(file_listing.files)}")
            print(f"Total size to transfer: {round(file_listing.total_size / 1024 / 1024, 2)} MB")
            print("-" * 56)
            print(len(file_listing.files))
            device.push_files(progress, *file_listing.files)
            progress.end()
    else:
        raise Exception("Unknown Command !!")
