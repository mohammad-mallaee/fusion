import adbutils
import os

class NoDeviceFound(Exception):
    pass


class adb(adbutils.AdbClient):
    def __init__(self, host="127.0.0.1", port=5037):
        super().__init__(host=host, port=port)
        try:
            self.device: adbutils.AdbDevice = self.device_list()[0]
        except Exception:
            raise NoDeviceFound

    def exists(self, path):
        output = self.device.shell2(f"ls {path}")
        return output.returncode == 0

    def ls(self, path):
        files_output = self.device.shell2(f"find {path} -type f -maxdepth 1").output
        files = files_output.split("\n")[0:-1]
        dirs_output = self.device.shell2(f"find {path} -type d -maxdepth 1").output
        directories = dirs_output.split("\n")[1:-1]
        return files, directories

    def ls_all_files(self, path):
        output = self.device.shell2(f"find {path} -type f").output.split("\n")
        return output[:-1]

    def ls_all_dirs(self, path):
        output = self.device.shell2(f"find {path} -type d").output.split("\n")
        return output[:-1]

    def is_dir(self, path):
        _, extention = os.path.splitext(path)
        return extention == ""

    def mkdir(self, path, parents=True):
        output = self.device.shell2(f"mkdir{' -p' if parents else ''} {path}")
        return output.returncode == 0
