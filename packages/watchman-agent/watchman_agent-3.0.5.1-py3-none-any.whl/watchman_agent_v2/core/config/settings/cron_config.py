from watchman_agent_v2.core.config.config_manager import ConfigManager

class CronConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
        self._init_section()
        
        
    def _init_section(self) -> None:
        """Initialise la section API si elle n'existe pas"""
        if 'cron' not in self.config_manager.config:
            config=self.config_manager.config
            config['cron'] = {}
            self.config_manager.save_config(config)
        

    def set_cron(self, schedule):
        """Met à jour la planification du cron"""
        config = self.config_manager.config
        config["cron"]["schedule"] = schedule
        self.config_manager.save_config(config)

    def get_cron(self):
        """Récupère la configuration de cron"""
        return self.config_manager.get("cron", {})
