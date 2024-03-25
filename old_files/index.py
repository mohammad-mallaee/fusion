from adbutils import AdbClient

from shift.adb import NoDeviceFound, adb
from shift.pull import pull_file, pull_dir
from shift.push import push_file, push_dir
from shift.utils import check_paths, is_dir, join_file_dir, PathError

def shift(source, destination=None):
    try:
        client: AdbClient = adb()
        command, source, destination = check_paths(client, source, destination)
        if command == "pull":
            if not is_dir(source):
                destination = destination if not is_dir(destination) else join_file_dir(destination, source)
                pull_file(client, source, destination)
            else:
                pull_dir(client, source, destination)
        elif command == "push":
            if not is_dir(source):
                destination = destination if not is_dir(destination) else join_file_dir(destination, source)
                push_file(client, source, destination)
            else:
                push_dir(client, source, destination)
    except PathError as e:
        print(e)
    except NoDeviceFound:
        print("There is no device to connect to!")
