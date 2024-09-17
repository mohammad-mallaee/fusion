from pytest import fixture
from shift.client import AdbClient
from shift.device import Device
from shift.storage import Storage


@fixture
def client():
    client = AdbClient().__enter__()
    yield client
    client.__exit__()


@fixture
def device(client):
    online_devices = client.list_devices()
    device_serial = online_devices[0][0]
    device = Device(device_serial, client)
    return device


@fixture
def storage():
    storage = Storage()
    return storage
