from watchman_agent_v2.core.config.config_manager import ConfigManager

class ExportConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
        self._init_section()
        
        
    def _init_section(self) -> None:
        """Initialise la section API si elle n'existe pas"""
        if 'export' not in self.config_manager.config:
            config=self.config_manager.config
            config['export'] = {}
            self.config_manager.save_config(config)

    def set_export(self, activate,path,file_name):
        """Met à jour le path du fichier d'exportation"""
        config = self.config_manager.config
        config["export"]["activate"] = activate
        config["export"]["path"] = path
        config["export"]["file-name"] = file_name
        
        self.config_manager.save_config(config)

    def get_export(self):
        """Récupère la configuration de export"""
        return self.config_manager.get("export", {})
