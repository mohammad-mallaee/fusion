import subprocess
import socket

from shift.helpers.constants import OKAY, FAIL


class AdbClient:
    def __init__(self, address=("127.0.0.1", 5037)):
        self.address = address
        self.connection = self.create_connection()

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
        subprocess.run(["adb", "start-server"], timeout=20)

    def connect_to_server(self, socket: socket.socket):
        socket.connect(self.address)

    def create_connection(self):
        adb_socket = socket.socket()
        self.start_server()
        self.connect_to_server(adb_socket)
        return adb_socket

    def send(self, content):
        self.connection.send(content)

    def recv(self, size: int):
        return self.connection.recv(size)

    def send_command(self, cmd: str, reset_connection = False):
        encoded_command = cmd.encode()
        encoded_command_length = "{:04x}".format(len(encoded_command)).encode()
        self.send(encoded_command_length + encoded_command)
        try:
            self.check_response()
        except Exception:
            raise

    def check_response(self):
        status = self.read_string(4)
        if status == OKAY:
            return
        elif status == FAIL:
            raise Exception(self.read_string_block())
        raise Exception("Unexpected Error Happened !!", status)

    def get_msg_length(self):
        return int(self.recv(4), 16)

    def read_string(self, size: int):
        return self.recv(size).decode()

    def read_string_block(self):
        msg_length = self.get_msg_length()
        return self.read_string(msg_length)

    def list_devices(self) -> tuple[list[str], list[str]]:
        self.send_command("host:devices")
        output = self.read_string_block()
        devices_output = output.split("\n")[:-1]
        devices = [device.split("\t") for device in output.split("\n")[:-1]]
        online_devices = [device[0] for device in devices if device[1] == "device" or device[1] == "recovery"]
        offiline_devices = [device[0] for device in devices if device[1] == "offline"]
        self.reset_connection()
        return online_devices, offiline_devices

    # These are to be gone if no proper usecase is found
    # -----------------------------------------------------------------------------------
    # def read_until_close(self, encoding: str | None = "utf-8") -> Union[str, bytes]:
    #     content = b""
    #     while True:
    #         chunk = self.connection.recv(4096)
    #         if not chunk:
    #             break
    #         content += chunk
    #     return content.decode(encoding, errors="replace") if encoding else content

    # def read_string_until_close(self, encoding: str = "utf-8") -> str:
    #     content = b""
    #     while True:
    #         chunk = self.connection.recv(4096)
    #         if not chunk:
    #             break
    #         content += chunk
    #     return content.decode(encoding)
    # ------------------------------------------------------------------------------------
