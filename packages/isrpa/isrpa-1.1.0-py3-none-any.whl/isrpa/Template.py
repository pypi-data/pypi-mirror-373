import json


class Template:
    version = "1.0.0"
    author = "isearch"
    date = "2024-12-20"
    desc = "自动化魔术师模板"


class Parameters:
    def __init__(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        self._data = data
        self._convert_to_object(self._data)

    def _convert_to_object(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                setattr(self, key, self._wrap(value))
        elif isinstance(data, list):
            for index, value in enumerate(data):
                data[index] = self._wrap(value)

    def _wrap(self, value):
        if isinstance(value, dict):
            return Parameters(value)
        elif isinstance(value, list):
            return [self._wrap(item) for item in value]
        else:
            return value

    def __repr__(self):
        return json.dumps(self._data, ensure_ascii=False, indent=4)

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class Node:
    def __init__(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        self.main_function = data.get("main_function")
        self.title = data.get("title")
        self.description = data.get("description")
        self.icon = data.get("icon")
        self.node_type = data.get("node_type")
        self.parameters = Parameters(data.get("parameters"))
        self.returns = Parameters(data.get("returns"))
        self.template = Template
        self._data = Parameters(data)

    def __getattr__(self, name):
        if name in self._data._data:
            return getattr(self._data, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
