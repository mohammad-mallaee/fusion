from fusion.device import Device
from fusion.client import AdbClient
from argcomplete.completers import FilesCompleter


def device_completer(**kwargs):
    prefix: str = kwargs["prefix"]
    with AdbClient() as client:
        online_devices = client.list_devices()
        if len(online_devices) == 0:
            return ()
        device = Device(online_devices[0][0], client)
        dir = prefix[: prefix.rfind("/") + 1]
        return (dir + name for name in device.ls(dir))


def sync_completer(arg):
    def _sync_completer(**kwargs):
        args = kwargs["parsed_args"]
        if args.reverse and arg == "destination":
            return device_completer(**kwargs)
        if not args.reverse and arg == "source":
            return device_completer(**kwargs)
        return FilesCompleter().__call__(**kwargs)

    return _sync_completer
