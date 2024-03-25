from pathlib import Path
import os
from shift.adb import adb
import re

def pull_file(client, source: str, dest: str):
    client.device.sync.pull(source, dest)


def pull_files(client, files, source, dest):
    source = source.strip("/")
    source_regex = fr"(\/)?{source}(\/)?"
    for file in files:
        file_dest = os.path.join(dest, re.sub(source_regex, "", file))
        parent_dir = os.path.dirname(file_dest)
        Path(parent_dir).mkdir(parents=True, exist_ok=True)
        pull_file(client, file, file_dest)


def pull_dir(client: adb, source: str, dest: str):
    files = client.ls_all_files(path=source)
    pull_files(client, files, source, dest)

