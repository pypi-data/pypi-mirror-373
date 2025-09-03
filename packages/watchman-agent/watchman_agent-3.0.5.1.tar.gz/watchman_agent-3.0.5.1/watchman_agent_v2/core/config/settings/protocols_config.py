from watchman_agent_v2.core.config.config_manager import ConfigManager
from typing import Optional, Dict, Any

class ProtocolsConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def set_protocols(
    self,
    protocol: str,
    proto_config: Dict[str, Any],
    client_ip: Optional[str] = None
) -> None:
        """Met à jour la configuration d'un protocole de manière sécurisée"""
        config = self.config_manager.config
        
        # Filtrer les valeurs None et les entrées vides
        filtered_config = {
            k: v 
            for k, v in proto_config.items() 
            if v is not None and v not in ({}, [], '')
        }
        
        # Ne rien faire si la configuration filtrée est vide
        if not filtered_config:
            return
        
        # Initialisation de la structure si nécessaire
        network_config = config.setdefault("network", {})
        protocols_config = network_config.setdefault("protocols", {
            "global": {},
            "overrides": {}
        })
        
        if client_ip:
            # Fusion sécurisée pour les overrides IP
            ip_overrides = protocols_config["overrides"].setdefault(client_ip, {})
            existing_config = ip_overrides.get(protocol, {})
            
            # Mise à jour seulement des clés non-None
            ip_overrides[protocol] = {
                **existing_config,
                **filtered_config
            }
        else:
            # Fusion sécurisée pour la config globale
            existing_config = protocols_config["global"].get(protocol, {})
            protocols_config["global"][protocol] = {
                **existing_config,
                **filtered_config
            }
        
        self.config_manager.save_config(config)

    def get_protocols(
        self, 
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Récupère la configuration avec fusion hiérarchique"""
        base_config = self.config_manager.get("network.protocols.global", {})
        
        if client_ip:
            overrides = self.config_manager.get(
                f"network.protocols.overrides.{client_ip}", 
                {}
            )
            return {**base_config, **overrides}
        
        return {
            "global": base_config,
            "overrides": self.config_manager.get("network.protocols.overrides", {})
        }