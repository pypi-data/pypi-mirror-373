
from abc import ABC, abstractmethod



class PluginFactoryBase:
    """
    Base class for plugin factories.
    """

    @abstractmethod
    def create_plugin(self, *args, **kwargs):
        """
        Create a plugin instance.
        """
        pass