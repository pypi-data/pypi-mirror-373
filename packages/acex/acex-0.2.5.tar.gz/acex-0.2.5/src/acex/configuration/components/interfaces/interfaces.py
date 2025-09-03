
from acex.configuration.components.base_component import ConfigComponent


class InterfaceBase(ConfigComponent): 
    def __init__(self, *, name: str):
        self.name = name


class Loopback(InterfaceBase): ...


class Vlan(InterfaceBase): ...


class Physical(InterfaceBase): ...


