from acex.plugins.adaptors import AssetAdapter
from acex.plugins.adaptors import LogicalNodeAdapter
from acex.plugins.adaptors import NodeAdapter
from acex.plugins.datasources import DatasourcePluginBase, DatabasePlugin

from acex.models import Asset
from acex.models import LogicalNode
from acex.models import Node

from .logical_node_service import LogicalNodeService
from .node_service import NodeService

class Datasources(): ...


class Inventory: 

    def __init__(
            self, 
            db_connection = None,
            assets_plugin = None,
            logical_nodes_plugin = None,
            config_compiler = None,
        ):

        # För presistent storage monteras en postgresql anslutning:
        # monterar datasources som datastores med specifika adaptrar
        # Om ingen plugin eller db injiceras i används sqlite
        if assets_plugin:
            self.assets = AssetAdapter(assets_plugin, self)
        else:
            default_assets_plugin = DatabasePlugin(db_connection, Asset)
            self.assets = AssetAdapter(default_assets_plugin, self)

        # Logical Nodes - skapa adapter och wrappa i service layer
        if logical_nodes_plugin:
            logical_nodes_adapter = LogicalNodeAdapter(logical_nodes_plugin, self)
        else:
            default_logical_nodes_plugin = DatabasePlugin(db_connection, LogicalNode)
            logical_nodes_adapter = LogicalNodeAdapter(default_logical_nodes_plugin, self)
        
        self.logical_nodes = LogicalNodeService(logical_nodes_adapter, config_compiler)

        # Node instances
        node_instance_plugin = DatabasePlugin(db_connection, Node)
        node_instances_adapter = NodeAdapter(node_instance_plugin, self)
        self.node_instances = NodeService(node_instances_adapter, self)


    def add_datasource(self, name: str, plugin: DatasourcePluginBase):
        """
        Additional datasources can be mounted using a datasourceplugin.
        """
        setattr(self.datasources, name, plugin)

