
# Exceptions personnalisées
class APIError(Exception):
    """Base exception pour les erreurs API"""

class APIAuthError(APIError):
    """Erreur d'authentification API"""

class APIConnectionError(APIError):
    """Erreur de connexion réseau"""

class APIValidationError(APIError):
    """Erreur de validation des données"""

class InventoryValidationError(APIValidationError):
    """Erreur de validation des données d'inventaire"""

class AuthenticationError(Exception):
    """Exception personnalisée pour les erreurs d'authentification"""
