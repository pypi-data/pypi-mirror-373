
from acex.exceptions import MethodNotImplemented

class DatasourcePluginBase:

    @property
    def capabilities(self):
        caps = {}
        for attr_name in dir(self):
            if attr_name == "capabilities":
                continue
            attr = getattr(self, attr_name)
            if callable(attr) and not attr_name.startswith("__"):
                func = getattr(attr, "__func__", attr)
                caps[attr_name] = func
        return caps
