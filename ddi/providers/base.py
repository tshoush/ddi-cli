from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """
    Abstract base class for all cloud providers.
    It defines a common interface for all provider-specific operations.
    """

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def sync(self, infoblox_manager):
        """
        Synchronizes network data from the cloud provider to Infoblox.
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, search_term):
        """
        Searches for network resources within the cloud provider.
        """
        raise NotImplementedError

    @abstractmethod
    def audit(self):
        """
        Performs an audit of network resources in the cloud provider.
        """
        raise NotImplementedError
