
from .base_component import ConfigComponent

from ipaddress import ip_interface

class IPInterface(ConfigComponent):
    def __init__(self, address: str):
        self.address = ip_interface(address)


    def to_json(self):
        json_data = super().to_json()
        json_data.update({
            "version": str(self.address.version),
            "address": str(self.address.ip),
            "subnetmask": str(self.address.netmask),
            "prefix_length": str(self.address.network.prefixlen)
        })
        return json_data