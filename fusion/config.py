import json
import platform
import subprocess
import importlib
from os.path import join

configs_dir = importlib.import_module("fusion.configs").__path__[0]
config_path = join(configs_dir, "config.json")


class Config:
    def __init__(self, data):
        self.excluded_paths = data["excluded_paths"]
        self.hidden_files = data["hidden_files"]
        self.editor = data["editor"]
        self.conflict_resolution = data["conflict_resolution"]
        if self.conflict_resolution not in ["sync", "force", "skip"]:
            raise ValueError(
                "Invalid conflict resolution. Must be one of: sync, force, skip"
            )

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)

    @property
    def editor_name(self):
        if self.editor == "default":
            system = platform.system()
            if system == "Linux" or system == "Darwin":
                return "vi"
            elif system == "Windows":
                return "notepad"
            else:
                None
        else:
            return self.editor

    def convert(self, type, data: str):
        if type is bool:
            return (
                True
                if data.lower() == "true"
                else False
                if data.lower() == "false"
                else None
            )
        elif type is int:
            try:
                return int(data)
            except ValueError:
                return None
        elif type is str:
            return data
        return None

    def reset(self, key=None):
        with open(join(configs_dir, "default.json"), "r") as default_file:
            default_data = json.load(default_file)
        if key is None:
            with open(config_path, "w") as config_file:
                json.dump(default_data, config_file, indent=4)
            self.__init__(default_data)
        else:
            if key in self.__dict__:
                self.__dict__[key] = default_data[key]
                with open(config_path, "w") as f:
                    json.dump(self.__dict__, f, indent=4)
            else:
                raise Exception(f"{key} is not a valid setting")

    def set(self, key, value):
        item = self.__dict__.get(key, None)
        if item is None:
            raise Exception(f"{key} is not a valid setting")
        converted_value = self.convert(type(item), value)
        if converted_value is None:
            raise Exception("Invalid value for setting")
        self.__dict__[key] = converted_value
        with open(config_path, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    def add(self, key, value):
        item = self.__dict__.get(key, None)
        if item is None:
            raise Exception(f"{key} is not a valid setting")
        if type(item) is not list:
            raise Exception("setting must be a list")
        if value in item:
            raise Exception("Value already exists in the list")
        self.__dict__[key].append(value)
        with open(config_path, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    def remove(self, key, value):
        item = self.__dict__.get(key, None)
        if not item:
            raise Exception(f"{key} is not a valid setting")
        if type(item) is not list:
            raise Exception("setting must be a list")
        if value not in item:
            raise Exception("Value does not exist in the list")
        self.__dict__[key].remove(value)
        with open(config_path, "w") as f:
            json.dump(self.__dict__, f, indent=4)


def configure(args):
    def _run_config_command(func, *args):
        try:
            func(*args)
            print(config)
        except Exception as e:
            print(e)

    if args.command == "edit":
        if config.editor_name is None:
            print("Could not identify your operating system!")
            print("The configuration file is located at:")
            print(config_path)
            print("You can set your editor by running:")
            print("fusion config set editor <editor_name>")
        else:
            subprocess.run([config.editor_name, config_path])
    else:
        commands = {
            "show": (print, config),
            "set": (_run_config_command, config.set, args.key, args.value),
            "add": (_run_config_command, config.add, args.key, args.value),
            "remove": (_run_config_command, config.remove, args.key, args.value),
            "reset": (_run_config_command, config.remove, args.key),
        }
        commands[args.command][0](*commands[args.command][1:])


with open(config_path, "r") as f:
    config_data = json.load(f)

config = Config(config_data)
