import os
from acex.constants import DEFAULT_ROOT_DIR, BASE_URL

from fastapi import FastAPI, APIRouter
from acex.api import Api
from acex.inventory import Inventory
from acex.plugins.datasources import DatasourcePluginBase
from acex.compilers import ConfigCompiler
from acex.database import Connection, DatabaseManager

from acex.models import Asset, LogicalNode


class AutomationEngine: 

    def __init__(
            self,
            db_connection:Connection|None = None,
            assets_plugin:DatasourcePluginBase|None = None,
            logical_nodes_plugin:DatasourcePluginBase|None = None
        ):
        self.api = Api()
        self.config_compiler = ConfigCompiler()
        self.db = DatabaseManager(db_connection)
        self.cors_settings_default = True
        self.cors_allowed_origins = []

        # create plugin instances.
        if assets_plugin is not None:
            assets_plugin = assets_plugin.create_plugin(Asset)

        if logical_nodes_plugin is not None:
            logical_nodes_plugin = logical_nodes_plugin.create_plugin(LogicalNode)

        self.inventory = Inventory(
            db_connection = self.db,
            assets_plugin=assets_plugin,
            logical_nodes_plugin=logical_nodes_plugin,
            config_compiler=self.config_compiler,
        )
        self._create_db_tables()
        
    def _create_db_tables(self):
        """
        Create tables if not exist, use on startup.
        """
        self.db.create_tables()


    def create_app(self) -> FastAPI:
        """
        This is the method that creates the full API.
        """
        return self.api.create_app(self)

    def add_datasource(self, name: str, plugin):
        self.inventory.add_datasource(name, plugin)

    def add_configmap_dir(self, dir_path: str):
        self.config_compiler.add_config_map_path(dir_path)

    def add_cors_allowed_origin(self, origin: str):
        self.cors_settings_default = False
        self.cors_allowed_origins.append(origin)