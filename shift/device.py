import struct
import time
import os
import stat as st
from shift import client

from shift.client import AdbClient
from shift.exceptions import AdbError
from shift.storage import Storage
from shift.helpers.constants import DATA, DENT, STAT, DONE, OKAY, FAIL
from shift.helpers.utils import truncate_middle
from shift.helpers.fileListing import FileListing
from shift.helpers.file import File
from shift.helpers.stat import Stat
from shift.helpers.progress import Progress


class Device:
    def __init__(
        self,
        serial,
        client: AdbClient,
        show_progress=None,
        show_result=None,
    ):
        self.client: AdbClient = client
        self.serial = serial
        self.connection = client.connection
        self.prepare_sync()

    def open_transport(self):
        self.client.send_command(f"host:transport:{self.serial}")

    def prepare_sync(self):
        self.open_transport()
        self.client.send_command("sync:")

    def send_sync_command(self, client, command, path):
        path_len = len(path.encode())
        client.connection.send(
            command.encode() + struct.pack("<I", path_len) + path.encode()
        )

    def get_chunk(self, client, size) -> bytes:
        chunk_size = 0
        chunk = b""
        while chunk_size < size:
            chunk += client.recv(size - chunk_size)
            chunk_size = len(chunk)
        return chunk

    def should_sync(self, file: File):
        self.send_sync_command(self.client, "STAT", file.remote_path)
        self.client.read_string(4)
        mode, size, mtime = struct.unpack("<III", self.client.recv(12))
        return file.modified_time > mtime and file.size != size

    def stat(self, path, follow_symlinks = False):
        self.send_sync_command(self.client, "STAT", path)
        id = self.client.read_string(4)
        mode, size, mtime = struct.unpack("<III", self.client.recv(12))
        if st.S_ISLNK(mode) and follow_symlinks:
            self.client.reset_connection()
            self.open_transport()
            self.client.send_shell_command(f"readlink -f {path}")
            real_path = self.client.recv(2048).decode().split("\n")[0]
            self.client.reset_connection()
            self.open_transport()
            self.client.send_command("sync:")
            return self.stat(real_path)
        return Stat(
            mode=mode,
            size=size,
            modified_time=mtime,
            path=path,
            name=os.path.basename(path)
        )

    def exists(self, path):
        self.send_sync_command(self.client, "STAT", path)
        id = self.client.read_string(4)
        mode, size, mtime = struct.unpack("<III", self.client.recv(12))
        return mode != 0

    # This should be removed as it doesn't make sense and its name is misleading
    def is_file(self, path):
        self.send_sync_command(self.client, "STAT", path)
        id = self.client.read_string(4)
        if id == STAT:
            mode, size, mtime = struct.unpack("<III", self.client.recv(12))
            if oct(mode).startswith("0o10"):
                return File(None, path, os.path.basename(path), size, mtime, mode)
            else:
                return False

    def list_files(self, path, file_listing:FileListing) -> None:
        def _ls(client, path):
            self.send_sync_command(client, "LIST", path)
            dirs = []
            while True:
                id = client.read_string(4)
                if id == DONE:
                    self.client.recv(1024)
                    break
                if id == DENT:
                    bytes = client.recv(16)
                    mode, size, modified_time, name_length = struct.unpack(
                        "<IIII", bytes
                    )
                    name = client.read_string(name_length)
                    entity_path = os.path.join(path, name)
                    if file_listing.is_excluded(entity_path):
                        continue
                    if st.S_ISREG(mode):
                        file = File(
                            file_listing.get_dest_path(entity_path),
                            entity_path,
                            name,
                            size,
                            modified_time,
                            mode,
                        )
                        file_listing.proccessed += 1
                        file_listing.total_size += file.size
                        if file_listing.should_sync(file):
                            file_listing.transfer_size += file.size
                            file_listing.valid += 1
                            file_listing.files.append(file)
                    elif name != "." and name != "..":
                            dirs.append(entity_path)
                elif id == FAIL:
                    print(path)
                    raise AdbError(
                        "Failure response from device", client.read_string(1024)
                    )
                else:
                    raise AdbError("Unknown response from device", id)
            file_listing.show_progress()
            for dir in dirs:
                _ls(client, dir)

        _ls(self.client, path)

    def _push_file(self, progress: Progress, file: File):
        progress.start_file(file)
        with file:
            start = time.time()
            adb_path = f"{file.remote_path},{file.mode}"
            self.send_sync_command(self.client, "SEND", adb_path)
            transferred_size = 0
            while True:
                chunk = file.buffer.read(64 * 1024)
                if not chunk:
                    self.client.send(b"DONE" + struct.pack("<I", file.modified_time))
                    break
                chunk_size = len(chunk)
                self.client.send(b"DATA" + struct.pack("<I", chunk_size))
                self.client.send(chunk)
                transferred_size += chunk_size
                progress.update_file(chunk_size)
            status_msg = self.client.read_string(4)
            if status_msg != OKAY:
                raise AdbError(status_msg)
            else:
                self.client.recv(4)
                progress.show_file_result()

    def push_files(self, progress: Progress, *files: File):
        for file in files:
            try:
                self._push_file(progress, file)
            except Exception as e:
                print("there was an error:", e)

    def _pull_file(self, storage: Storage, progress: Progress, file: File):
        progress.start_file(file)
        self.send_sync_command(self.client, "RECV", file.remote_path)
        start = time.time()
        transferred_size = 0
        storage.create(file)
        while True:
            status = self.get_chunk(self.client, 4).decode()
            if status == DATA:
                chunk_size = struct.unpack("<I", self.client.recv(4))[0]
                received_chunk = self.get_chunk(self.client, chunk_size)
                received_chunk_size = len(received_chunk)
                if received_chunk_size != chunk_size:
                    raise RuntimeError("Missing Data")
                transferred_size += received_chunk_size
                storage.write(file, received_chunk)
                progress.update_file(chunk_size)
            elif status == FAIL:
                str_size = struct.unpack("<I", self.client.recv(4))[0]
                error_message = self.client.read_string(str_size)
                raise AdbError(error_message, file.remote_path, status)
            elif status == DONE:
                # 4 bytes after DONE is a hexadecimal number representing 0 which will be ignored.
                self.client.recv(4)
                storage.save(file)
                progress.show_file_result()
                break
            else:
                raise AdbError("Invalid Sync Status", status)

    def pull_files(self, storage: Storage, progress: Progress, *files):
        for file in files:
            try:
                self._pull_file(storage, progress, file)
            except Exception as e:
                print("there was an error:", e)
