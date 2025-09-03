from watchman_agent_v2.core.config.config_manager import ConfigManager

class LogConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
        self._init_section()
        
        
    def _init_section(self) -> None:
        """Initialise la section API si elle n'existe pas"""
        if 'log' not in self.config_manager.config:
            config=self.config_manager.config
            config['log'] = {}
            self.config_manager.save_config(config)

    def set_log(self, log_mode):
        """Met à jour le path du fichier d'exportation"""
        config = self.config_manager.config
        config["log"]["mode"] = log_mode
        
        self.config_manager.save_config(config)

    def get_log(self):
        """Récupère la configuration de export"""
        return self.config_manager.get("log", {})
