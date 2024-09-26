import subprocess
import socket
import re

from fusion.helpers.constants import OKAY, FAIL
from fusion.helpers.logger import log


class AdbClient:
    def __init__(self, address=("127.0.0.1", 5037)):
        self.address = address

    def __enter__(self):
        self.connection = self.create_connection()
        return self

    def __exit__(self, *args):
        self.connection.close()

    def reset_connection(self):
        self.connection.close()
        adb_socket = socket.socket()
        adb_socket.connect(self.address)
        self.connection = adb_socket

    def send_shell_command(self, shell_cmd: str):
        shell_command = f"shell:{shell_cmd}"
        self.send_command(shell_command)

    @staticmethod
    def start_server():
        result = subprocess.run(
            ["adb", "start-server"],
            stderr=subprocess.PIPE,
        )
        if result.stderr:
            log.error("AdbError", result.stderr.decode())
            raise FileNotFoundError()

    def connect_to_server(self, socket: socket.socket):
        socket.connect(self.address)

    def create_connection(self):
        self.start_server()
        adb_socket = socket.socket()
        self.connect_to_server(adb_socket)
        return adb_socket

    def send(self, content):
        self.connection.send(content)

    def recv(self, size: int):
        return self.connection.recv(size)

    def send_command(self, cmd: str):
        encoded_command = cmd.encode()
        encoded_command_length = "{:04x}".format(len(encoded_command)).encode()
        self.send(encoded_command_length + encoded_command)
        self.check_response()

    def check_response(self):
        status = self.read_string(4)
        if status == OKAY:
            return
        elif status == FAIL:
            raise Exception(self.read_string_block())
        raise Exception("Invalid response from device !!")

    def get_msg_length(self):
        return int(self.recv(4), 16)

    def read_string(self, size: int):
        return self.recv(size).decode()

    def read_string_block(self):
        msg_length = self.get_msg_length()
        return self.read_string(msg_length)

    def list_devices(self) -> tuple[list[str], list[str]]:
        self.send_command("host:devices-l")
        output = self.read_string_block()
        pattern = r"^(\S+)\s+(\S+).*\bmodel:(\S+)"
        devices = [
            re.search(pattern, device).groups() for device in output.split("\n")[:-1]
        ]
        online_devices = list(
            filter(lambda d: d[1] == "device" or d[1] == "recovery", devices)
        )
        self.reset_connection()
        return online_devices

    def read_string_until_close(self, encoding: str = "utf-8") -> str:
        content = b""
        while True:
            chunk = self.connection.recv(4096)
            if not chunk:
                break
            content += chunk
        return content.decode(encoding)
