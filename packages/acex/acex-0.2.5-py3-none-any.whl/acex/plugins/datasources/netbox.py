from .datasource_plugin_base import DatasourcePluginBase
from .datasource_plugin_factory_base import PluginFactoryBase

from acex.utils import RestClient
from acex.models import Asset, LogicalNode, Node, NodeResponse, LogicalNodeResponse

from typing import Type
from pydantic import BaseModel

import json


class Netbox(): 

    def __init__(self, url: str, token: str, verify_ssl: bool = True):
        """
        Used to define the connection to netbox. This is a factory class
        that will create a NetboxPluginInstance for each model used.
        """
        self.base_url = f"{url}api/"
        self.token = token
        self.rest = RestClient(self.base_url, verify_ssl=verify_ssl)
        self.rest.add_header("Authorization", f"Token {self.token}")
        self.rest.add_header("Content-Type", "application/json")


    def create_plugin(self, model: Type[BaseModel]) -> 'NetboxPlugin':
        """
        Create a plugin instance for a specific model.
        :param model: The Pydantic model class to use for the plugin.
        :return: An instance of NetboxPlugin.
        """
        return NetboxPlugin(model=model, restclient=self.rest)


class NetboxPlugin:
    """
    The actual plugin instance that will be used by the adapter in the
    inventory. Will be instanciated for each model used. Using the Netbox class
    to define the connection details.
    """

    ENTITY_ENDPOINTS = {
        Asset: "dcim/devices/",
        LogicalNode: "dcim/devices/",
    }

    def __init__(self, model: Type[BaseModel], restclient: RestClient):
        """
        Initialize the Netbox datasource plugin with a Netbox API client.
        :param url: The base URL of the Netbox instance.
        :param token: The API token for authentication.
        :param verify_ssl: Whether to verify SSL certificates (default is True).
        """
        self.rest = restclient
        self.model = model

    def _get_ep(self, id: str = None, filters: dict | None = None) -> str:
        """
        Return endpoint for the model.
        """
        url =  self.__class__.ENTITY_ENDPOINTS.get(self.model, "")
        if id is not None:
            url += f"{id}/"
        elif filters:
            url += "?" + "&".join(f"{k}={v}" for k, v in filters.items())
        return url


    def _build_asset_model(self, data: dict) -> Asset:
        """
        Build an Asset model instance from raw data.
        :param data: Raw data from Netbox API.
        :return: An Asset model instance.
        """
        return Asset(
            id=data.get("id"),
            vendor=data.get("device_type", {}).get("manufacturer", {}).get("name"),
            os=data.get("platform", {}).get("name"),
            serial_number=data.get("serial"),
            ned_id=data.get("custom_fields", {}).get("ned_id"),
        )

    def _build_logical_node_model(self, data: dict) -> LogicalNode:
        """
        Build a LogicalNode model instance from raw data.
        :param data: Raw data from Netbox API.
        :return: A LogicalNode model instance.
        """
        return LogicalNodeResponse(
            id=data.get("id"),
            hostname=data.get("name"),
            role=data.get("role", {}).get("name"),
            site=data.get("site", {}).get("name"),
            interfaces={"najs": "rajs"}
        )

    # TODO: Fixa så vi kan ta interfaces från netbox :)





    def _build_model(self, data: dict, model: Type[BaseModel] = None) -> BaseModel:
        """
        Build a correct model instance with data from netbox api.
        Input data is a raw dict from netbox, and the model is the pydantic model
        used in the rest of ACE.
        """
        if self.model is Asset:
            return self._build_asset_model(data)
        elif self.model is LogicalNode:
            return self._build_logical_node_model(data)
        return {}


    def get(self, id: str):
        response = self.rest.get(self._get_ep(id=id))
        return self._build_model(response.json())

    # def create(self, data: BaseModel):
    #     return {}


    def query(self, filters: dict | None = None) -> list:
        response = self.rest.get(self._get_ep(filters=filters))
        for d in response.json().get("results", []):
            yield self._build_model(d)


    # def update(self, id: str, data: BaseModel):
    #     return {}

    # def delete(self, id: str):
    #     return {}

class Old:

    def _get_devices(self, filter: dict = {}):
        """
        Get devices from Netbox. Note: this does not return ACE models, but raw data from Netbox.
        :param filter: Optional filter dictionary to apply to the query.
        :return: List of devices matching the filter.
        """
        endpoint = "dcim/devices/"
        if filter:
            endpoint += f"?{filter}"
        response = self.rest.get(endpoint)
        
        if response.status_code == 200:
            return response.json()

    def _get_device(self, id: str = None):
        """
        Get a specific device from Netbox. Note: this does not return ACE models, but raw data from Netbox.
        :param id: The ID of the device to retrieve.
        :return: The device data or None if not found.
        """
        endpoint = f"dcim/devices/{id}/"
        response = self.rest.get(endpoint)

        if response.status_code == 200:
            return response.json()
        return None
        endpoint = "dcim/devices/"
        if filter:
            endpoint += f"?{filter}"
        response = self.rest.get(endpoint)
        
        if response.status_code == 200:
            return response.json()

    def get_node_instance(self, id: str):
        """
        Get a specific node instance by ID from Netbox.
        :param id: The ID of the node instance to retrieve.
        :return: The node instance data or None if not found.
        """
        asset = self.get_asset(id)
        ln = self.get_logical_node(id)
        if asset and ln:
            return Node(
                id=ln.id,
                asset_id=asset.id,
                logical_node_id=ln.id,
            )

    def get_assets(self, filter: dict = {}):
        """
        Get assets from Netbox. Note: this does not return ACE models, but raw data from Netbox.
        :param filter: Optional filter dictionary to apply to the query.
        :return: List of assets matching the filter.
        """
        if filter:
            print("filters are not supported yet.")

        nb_devices = self._get_devices(filter)
        assets = []
        for device in nb_devices.get("results", []):
            asset = Asset(
                id=device.get("id"),
                vendor=device.get("device_type", {}).get("manufacturer", {}).get("name"),
                os=device.get("platform", {}).get("name"),
                serial_number=device.get("serial"),
            )
            assets.append(asset)
        return assets

    def get_asset(self, id: str):
        """
        Get a specific asset by ID from Netbox.
        :param id: The ID of the asset to retrieve.
        :return: The asset data or None if not found.
        """
        response = self._get_device(id)

        if response is not None:
            return Asset(
                id=response.get("id"),
                vendor=response.get("device_type", {}).get("manufacturer", {}).get("name"),
                os=response.get("platform", {}).get("name"),
                serial_number=response.get("serial"),
            )
        return None

    def get_logical_nodes(self, filter: dict = {}):
        """
        Get logical nodes from Netbox. Note: this does not return ACE models, but raw data from Netbox.
        :param filter: Optional filter dictionary to apply to the query.
        :return: List of logical nodes matching the filter.
        """
        if filter:
            print("filters are not supported yet.")

        nb_devices = self._get_devices()
        logical_nodes = []
        for device in nb_devices.get("results", []):
            # print(device)
            logical_node = LogicalNode(
                id=device.get("id"),
                hostname=device.get("name"),
                role=device.get("role", {}).get("name"),
                site=device.get("site", {}).get("name")
            )
            logical_nodes.append(logical_node)
        return logical_nodes

    def get_logical_node(self, id: str):
        """
        Get a specific logical node by ID from Netbox.
        :param id: The ID of the logical node to retrieve.
        :return: The logical node data or None if not found.
        """
        response = self._get_device(id)

        if response is not None:
            return LogicalNode(
                id=response.get("id"),
                hostname=response.get("name"),
                role=response.get("role", {}).get("name"),
                site=response.get("site", {}).get("name")
            )
        return None

