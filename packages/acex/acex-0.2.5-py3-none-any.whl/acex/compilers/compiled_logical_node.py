from typing import Callable, Union, Awaitable
from acex.config_map import ConfigMap
import inspect
from acex.models import LogicalNodeResponse
from acex.configuration import Configuration

class CompiledLogicalNode: 

    def __init__(self, logical_node: dict):
        self.logical_node = logical_node
        self.configuration = Configuration()
        self.meta_data = {} # Får inte heta "metadata" pga SQLModel
        self.processors = []
        # self._init_configuration()

    @property
    def response(self):
        response = self.logical_node.model_dump()
        response["meta_data"] = {"compiled": True}
        response["meta_data"]["processors"] = [str(x.__self__.__class__) for x in self.processors]
        response["configuration"] = self.configuration.to_json()
        return LogicalNodeResponse(**response)

    # def _init_configuration(self):
    #     """
    #     Initializes the configuration for the logical node.
    #     This method can be overridden to set specific configurations.
    #     """
    #     self.configuration = {
    #         "interfaces": [],
    #         "hostname": self.logical_node.hostname
    #     }

    def check_config_map_filter(self, config_map: ConfigMap):
        """
        Returns True if the config_map matches the logical node's filter.
        This method should be implemented to check against the logical node's filters.
        """
        if config_map.filters is not None:
            for exp in config_map.filters.as_alternatives():
                match = exp.match(self.logical_node)
                if match is True:
                    return True

        return False


    async def compile(self):
        # run all registered processors
        for processor in self.processors:
            if inspect.iscoroutinefunction(processor):
                await processor(self)
            else:
                processor(self)


    def register(self, fn: Callable[[dict], Union[dict, Awaitable[dict]]]):
        """Register a new compile processor."""
        self.processors.append(fn)
