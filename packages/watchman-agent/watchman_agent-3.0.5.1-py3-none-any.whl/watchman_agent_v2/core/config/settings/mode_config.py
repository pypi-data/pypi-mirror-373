from watchman_agent_v2.core.config.config_manager import ConfigManager

class ModeConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
        self._init_section()
        
        
    def _init_section(self) -> None:
        """Initialise la section API si elle n'existe pas"""
        if 'mode' not in self.config_manager.config:
            config=self.config_manager.config
            config['mode'] = {}
            self.config_manager.save_config(config)

    def set_mode(self, mode=None):
        """Modifie la configuration réseau"""
        config = self.config_manager.config
        if mode:
            config["mode"] = mode
        self.config_manager.save_config(config)

    def get_mode(self):
        """Récupère la configuration réseau"""
        return self.config_manager.get("mode", {})
