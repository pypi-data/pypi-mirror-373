from watchman_agent_v2.core.config.config_manager import ConfigManager

class APIConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
        self._init_section()
        
        
    def _init_section(self) -> None:
        """Initialise la section API si elle n'existe pas"""
        if 'api' not in self.config_manager.config:
            config=self.config_manager.config
            config['api'] = {}
            self.config_manager.save_config(config)

    def set_api_keys(self, client_id, client_secret):
        """Stocke et chiffre les clés API"""
        config = self.config_manager.config
        if client_id:
            config["api"]["client_id"] = client_id
        if client_secret:
            config["api"]["client_secret"] = self.config_manager.encrypt(client_secret)

        self.config_manager.save_config(config)

    def get_api_keys(self):
        """Récupère les clés API (client_id en clair, client_secret déchiffré)"""
        api_config = self.config_manager.get("api", {})
        api_config["client_secret"] = self.config_manager.decrypt(api_config.get("client_secret", ""))
        return api_config
