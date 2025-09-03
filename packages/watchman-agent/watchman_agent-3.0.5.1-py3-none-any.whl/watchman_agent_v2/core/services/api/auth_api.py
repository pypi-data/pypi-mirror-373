import os
import time
import logging
from typing import Dict, Optional
from threading import Lock
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from watchman_agent_v2.core.services.api.exceptions import AuthenticationError

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthClient:
    """
    Client d'authentification sécurisé avec gestion de token JWT/OAuth2
    
    Features :
    - Gestion du cycle de vie du token
    - Rafraîchissement automatique
    - Stockage sécurisé en mémoire
    - Thread-safe
    - Gestion des erreurs
    """
    AUTH_ENDPOINT = "https://api.watchman.bj/api/v2/agent/connect/"
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_ttl: int = 3600,
        scope: str = "read write"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_endpoint = self.AUTH_ENDPOINT
        self.scope = scope
        self.token_ttl = token_ttl
        self._token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = Lock()
        self.session = self._configure_session()

    def _configure_session(self) -> requests.Session:
        """Configure une session HTTP sécurisée"""
        session = requests.Session()
        
        # Configuration TLS
        # session.verify = True
        # session.cert = os.getenv('SSL_CERT_PATH', None)
        
        # Politique de retry
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=['POST']
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        
        return session

    def _request_token(self) -> Dict:
        """Demande un nouveau token d'accès"""
        try:
            
            data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials',
                    'scope': self.scope
                }
            response = self.session.get(
                self.auth_endpoint,
                headers={
                    'Content-Type': 'application/json',
                    "AGENT-ID": self.client_id,
                    "AGENT-SECRET": self.client_secret
                },
                timeout=10
            )
            response.raise_for_status()
            
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur d'authentification: {str(e)}")
            raise AuthenticationError("Échec de l'authentification") from e

    def _is_token_valid(self) -> bool:
        """Vérifie si le token est toujours valide"""
        return time.time() < self._expires_at - 60  # 60s de marge

    def get_token(self) -> str:
        """Récupère le token valide (thread-safe)"""
        with self._lock:
            if not self._is_token_valid():
                self._refresh_token()
            return self._token

    def _refresh_token(self):
        """Rafraîchit le token d'accès"""
        try:
            token_data = self._request_token()
            self._token = token_data['token']
            # self._expires_at = time.time() + token_data.get('expires_in', self.token_ttl)
            
            # Sécurité : effacer les données sensibles
            del token_data
            
        except KeyError as e:
            logger.error("Réponse d'authentification invalide")
            raise AuthenticationError("Réponse API incorrecte") from e

    def revoke_token(self):
        """Révoque le token actuel (implémentation de base)"""
        with self._lock:
            self._token = None
            self._expires_at = 0.0
            # Implémenter l'appel à l'endpoint de révocation ici

    def test_connection(self) -> bool:
        """Teste la connectivité au service d'authentification"""
        try:
            response = self.session.head(
                self.auth_endpoint,
                timeout=5
            )
            print(self.auth_endpoint)
            return response.status_code in [200, 405,412]
        except requests.exceptions.RequestException as error:
            return False

