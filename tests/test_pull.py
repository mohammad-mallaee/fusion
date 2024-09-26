from fusion.helpers.fileListing import SyncList
from fusion.helpers.progress import Progress
import os
import shutil


def test_pull_file(storage, device):
    device.send_shell_command("mkdir sdcard/fusion_test", True)
    device.send_shell_command(
        f"echo {' test content ' * 4000} > sdcard/fusion_test/test.txt", True
    )
    device.reset_connection(True)
    file = device.get_file("sdcard/fusion_test/test.txt")
    file.local_path = "./fusion_test/test.txt"
    file_listing = SyncList(lambda path: path, local=False)
    file_listing.append_process(file)
    file_listing.append(file)
    progress = Progress(file_listing)
    progress.start()
    device.pull_files(storage, progress, file)
    assert os.path.exists("./fusion_test/test.txt")
    f = open("./fusion_test/test.txt", "r")
    device.send_shell_command("cat sdcard/fusion_test/test.txt")
    assert f.read() == device.client.read_string_until_close()
    shutil.rmtree("./fusion_test")
    device.send_shell_command("rm -rf sdcard/fusion_test", True)


def test_dir_pull(device, storage):
    device.send_shell_command("mkdir sdcard/fusion_test", True)
    file_paths = [
        "test.txt",
        "test2.txt",
        "1/test3.txt",
        "1/test4.txt",
        "1/2/test5.txt",
        "2/test6.txt",
    ]
    file_listing = SyncList(lambda path: path, local=False)
    for file_path in file_paths:
        path = f"/sdcard/fusion_test/{file_path}"
        device.send_shell_command(f"mkdir -p {os.path.dirname(path)}", True)
        device.send_shell_command(f"echo {' test content ' * 4000} > {path}", True)
        device.reset_connection(True)
        file = device.get_file(path)
        file.local_path = f"fusion_test/{file_path}"
        file_listing.append_process(file)
        file_listing.append(file)

    progress = Progress(file_listing)
    progress.start()
    device.pull_files(storage, progress, *file_listing.files)
    device.send_shell_command("rm -rf sdcard/fusion_test", True)
    shutil.rmtree("fusion_test")
