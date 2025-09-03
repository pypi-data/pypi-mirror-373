"""
En datastore är en composition av en eller flera datasources.
Vid användning av flera sources behöver attribute maps användas

Instansieras en Datastore utan datasources kommer den defaulta
till att köra en instans av in_memory och mappa alla attribut till
den datasourcen.
"""

from ace.plugins.adaptors import DatasourcePluginAdapterBase
from ace.plugins.datasources import DatasourcePluginBase
from ace.plugins.adaptors import DatasourcePluginAdapter


class Datastore: 

    def __init__(
            self,
            name: str
        ):
        self.name = name

    def add_datasource(self, key: str, plugin: DatasourcePluginBase|None = None):
        if plugin is None:
            # Montera en in_memory med standardadapter.
            ...