
from .adapter_base import AdapterBase
from acex.models import Asset


class DatasourcePluginAdapter(AdapterBase):

    def create(self, asset: Asset): 
        if hasattr(self.plugin, "create"):
            return getattr(self.plugin, "create")(asset)

    def get(self, id: str): 
        if hasattr(self.plugin, "get"):
            return getattr(self.plugin, "get")(id)

    def query(self): 
        if hasattr(self.plugin, "query"):
            return getattr(self.plugin, "query")()

    def update(self, asset: Asset): 
        if hasattr(self.plugin, "update"):
            return getattr(self.plugin, "update")(asset)

    def delete(self, id: str): 
        if hasattr(self.plugin, "delete"):
            return getattr(self.plugin, "delete")(id)
