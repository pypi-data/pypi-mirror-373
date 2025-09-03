from watchman_agent_v2.core.utils.log_manager import LogManager


class ProtocolSelector:
    def __init__(self, protocol_handlers: dict, protocols_config: dict):
        self.protocol_handlers = protocol_handlers
        self.protocols = protocols_config
        self.logger = LogManager

    def deep_merge(self, base: dict, update: dict) -> dict:
        """
        Fusion récursive de dictionnaires.
        Combine les configurations globales et les surcharges intelligemment.
        """
        merged = base.copy()
        for key, val in update.items():
            if isinstance(val, dict) and key in merged:
                merged[key] = self.deep_merge(merged.get(key, {}), val)
            else:
                merged[key] = val
        return merged

    def get_protocols(self, address: str) -> dict:
        """
        Retourne la configuration complète des protocoles pour une adresse,
        en conservant TOUS les protocoles globaux et leurs paramètres,
        même si non mentionnés dans les surcharges.
        """
        global_config = self.protocols.get('global', {})
        address_overrides = self.protocols.get('overrides', {}).get(address, {})
        return self.deep_merge(global_config, address_overrides)

    def select_and_run(self, address: str) -> tuple:
        """
        Sélectionne et exécute le premier protocole activé.
        Retourne (résultat, nom du protocole, instance handler)
        """
        protocols_config = self.get_protocols(address)
        self.logger.info(f"Protocoles configurés pour {address}")

        for protocol_name, protocol_config in protocols_config.items():
            if not protocol_config.get('enabled', False):
                continue

            try:
                handler = self._get_handler(protocol_name)
                result = handler.collect_info(address, protocol_config)
                return result, protocol_name, handler
            except Exception as e:
                self.logger.error(f"Erreur avec {protocol_name} sur {address}: {str(e)}")
                continue

        raise Exception(f"Aucun protocole n'a réussi pour {address}")

    def _get_handler(self, protocol_name: str):
        handler_class = self.protocol_handlers.get(protocol_name)
        if not handler_class:
            raise ValueError(f"Handler non trouvé pour le protocole: {protocol_name}")
        return handler_class()
