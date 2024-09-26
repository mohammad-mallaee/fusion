from fusion.helpers.progress import Progress
import os
from fusion.helpers.fileListing import SyncList
import shutil


def test_file_push(device, storage):
    device.send_shell_command("mkdir sdcard/fusion_test", True)
    content = "test content of teset.txt file\n" * 100000
    f = open("test.txt", "w")
    f.write(content)
    f.close()
    file = storage.get_file("test.txt")
    file.remote_path = "sdcard/fusion_test/test.txt"
    file_listing = SyncList(lambda path: path, local=True)
    file_listing.append_process(file)
    file_listing.append(file)
    progress = Progress(file_listing)
    progress.start()
    device.reset_connection(True)
    device.push_files(progress, file)
    device.send_shell_command("ls sdcard/fusion_test/test.txt")
    assert "test.txt" in device.client.read_string_until_close()
    device.send_shell_command("cat sdcard/fusion_test/test.txt")
    assert device.client.read_string_until_close() == content
    assert progress.files == 1
    assert progress.total_transfer == progress.total_size
    device.send_shell_command("rm -rf sdcard/fusion_test", True)
    os.remove("test.txt")


def test_dir_push(device, storage):
    device.send_shell_command("mkdir sdcard/fusion_test", True)
    file_paths = [
        "test.txt",
        "test2.txt",
        "1/test3.txt",
        "1/test4.txt",
        "1/2/test5.txt",
        "2/test6.txt",
    ]

    os.mkdir("fusion_test")
    file_listing = SyncList(lambda path: path, local=True)
    for file_path in file_paths:
        path = f"fusion_test/{file_path}"
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        f = open(path, "w")
        f.write("test content of teset.txt file\n" * 40000)
        f.close()
        file = storage.get_file(path)
        file.remote_path = f"sdcard/fusion_test/{file_path}"
        file_listing.append_process(file)
        file_listing.append(file)

    progress = Progress(file_listing)
    progress.start()
    device.reset_connection(True)
    device.push_files(progress, *file_listing.files)
    device.send_shell_command("rm -rf sdcard/fusion_test", True)
    shutil.rmtree("fusion_test")
