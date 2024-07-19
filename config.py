import json
import platform


class Config:
    def __init__(self, data):
        self.excluded_paths = data["excluded_paths"]
        self.hidden_files = data["hidden_files"]
        self.editor = data["editor"]

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
                else False if data.lower() == "false" else None
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
        with open("default.json", "r") as default_file:
            default_data = json.load(default_file)
        if key is None:
            with open("config.json", "w") as config_file:
                json.dump(default_data, config_file, indent=4)
            self.__init__(default_data)
        else:
            if key in self.__dict__:
                self.__dict__[key] = default_data[key]
                with open("config.json", "w") as f:
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
        with open("config.json", "w") as f:
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
        with open("config.json", "w") as f:
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
        with open("config.json", "w") as f:
            json.dump(self.__dict__, f, indent=4)


with open("config.json") as f:
    config_data = json.load(f)


config = Config(config_data)
