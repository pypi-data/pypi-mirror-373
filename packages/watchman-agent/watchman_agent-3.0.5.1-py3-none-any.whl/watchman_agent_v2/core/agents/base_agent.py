from abc import ABC, abstractmethod
from watchman_agent_v2.core.config.config_manager import ConfigManager

class BaseAgent(ABC):
    """
    Classe abstraite pour les agents.
    """
    def __init__(self):
        self.config=ConfigManager()
        
        
    @abstractmethod
    def run(self):
        """Exécute la collecte d'informations."""
        pass

    @abstractmethod
    def configure(self):
        """Configure l'agent."""
        pass
