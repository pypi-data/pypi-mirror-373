class CredentialVault:
    """
    Gestion centralisée des secrets et credentials.
    """
    def __init__(self):
        self._secrets = {}

    def store_credentials(self, protocol: str, target: str, credentials: dict):
        """Stocke les credentials pour un protocole et une cible donnés."""
        self._secrets[(protocol, target)] = credentials

    def get_credentials(self, protocol: str, target: str):
        """Récupère les credentials pour un protocole et une cible donnés."""
        return self._secrets.get((protocol, target), {})
