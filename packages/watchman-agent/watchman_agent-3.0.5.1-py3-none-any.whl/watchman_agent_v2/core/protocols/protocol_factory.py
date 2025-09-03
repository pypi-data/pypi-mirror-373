from abc import ABC, abstractmethod

from watchman_agent_v2.core.config.config_manager import ConfigManager


class BaseProtocol(ABC):
    """
    Implémentation spécifique du protocole SNMP.
    """

    def __init__(self):
        self.config = ConfigManager()

    
