from watchman_agent_v2.core.config.config_manager import ConfigManager

class AdConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
        self._init_section()
        
        
    def _init_section(self) -> None:
        """Initialise la section API si elle n'existe pas"""
        if 'ad' not in self.config_manager.config:
            config=self.config_manager.config
            config['ad'] = {}
            self.config_manager.save_config(config)

    def set_ad_keys(self, ldap_server=None, ldap_port=None,search_base=None,group=None,domain=None):
        """Stocke et chiffre les clés API"""
        config = self.config_manager.config
        if ldap_server:
            config["ad"]["ldap_server"] = ldap_server
        if ldap_port:
            config["ad"]["ldap_port"] = ldap_port
        if search_base:
            config["ad"]["search_base"] = search_base
        if group:
            config["ad"]["group"] = group
        if domain:
            config["ad"]["domain"] = domain

        self.config_manager.save_config(config)
    def set_ad_user_key(self, user=None, password=None):
        """Stocke et chiffre les clés API"""
        config = self.config_manager.config
        if user:
            config["ad"]["user"] = self.config_manager.encrypt(user)
        if password:
            config["ad"]["password"] = self.config_manager.encrypt(password)

        self.config_manager.save_config(config)

    def get_api_keys(self):
        """Récupère les clés API (client_id en clair, client_secret déchiffré)"""
        api_config = self.config_manager.get("api", {})
        api_config["client_secret"] = self.config_manager.decrypt(api_config.get("client_secret", ""))
        return api_config
