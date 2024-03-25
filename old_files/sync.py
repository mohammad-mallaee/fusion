from pathlib import Path
from shift.adb import NoDeviceFound, adb
from shift.utils import join_file_dir
from shift.pull import pull_file
import os
import re

def sync(_, source, destination = './'):
    try:
        client = adb()
        files = client.ls_all_files(source)
        source = source.strip("/")
        source_regex = fr"(\/)?{source}(\/)?"
        for file in files:
            file_dest = os.path.join(destination, re.sub(source_regex, "", file))
            parent_dir = os.path.dirname(file_dest)
            if not Path(file_dest).is_file():
                Path(parent_dir).mkdir(parents=True, exist_ok=True)
                print(client.device.sync.stat(file))
                pull_file(client, file, file_dest)

    except NoDeviceFound:
        print("There is no device to connect to")
