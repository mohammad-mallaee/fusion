from shift.adb import adb
import os
import re
import glob

def push_file(client, source, dest):
    client.device.sync.push(source, dest)

def push_files(client, files, source, dest):
    source = source.strip("/")
    source_regex = fr"(\/)?{source}(\/)?"
    for file in files:
        file_dest = os.path.join(dest, re.sub(source_regex, "", file))
        push_file(client, file, file_dest)


def get_all_files(path):
    files_iterator = glob.iglob(path + "/**/*.*", recursive=True)
    return files_iterator

def push_dir(client: adb, source: str, dest: str):
    files = get_all_files(source) 
    push_files(client, files, source, dest)
 

