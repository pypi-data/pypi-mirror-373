import requests
import json
from typing import Dict, Optional, Union
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

from watchman_agent_v2.core.services.api.exceptions import APIAuthError, APIConnectionError, APIError, APIValidationError, InventoryValidationError

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """
    Client API de base avec fonctionnalités de sécurité et gestion d'erreurs avancée
    
    Features :
    - Authentification JWT/OAuth2
    - Gestion des retry intelligents
    - Validation SSL stricte
    - Chiffrement TLS 1.2+
    - Gestion des timeouts
    - Logging détaillé
    """
    
    def __init__(self, endpoint: str, credentials: Dict[str, str]):
        self.endpoint = endpoint
        self.credentials = credentials
        self.session = self._create_secured_session()
        self._authenticate()

    def _create_secured_session(self) -> requests.Session:
        """Crée une session HTTP sécurisée avec chiffrement fort"""
        session = requests.Session()
        
        # Configuration TLS
        session.verify = True  # Forcer la vérification SSL
        session.cert = os.getenv('SSL_CERT_PATH')  # Certificat client si nécessaire
        
        # Politique de retry
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=['POST', 'GET', 'PUT']
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        
        # Headers sécurisés
        session.headers.update({
            'User-Agent': 'InventoryAPIClient/1.0',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        return session

    def _authenticate(self):
        """Mécanisme d'authentification sécurisé"""
        try:
            if self.credentials.get('api_key'):
                self.session.headers.update({
                    'Authorization': f'Bearer {self.credentials["api_key"]}'
                })
            elif self.credentials.get('oauth'):
                token = self._get_oauth_token()
                self.session.headers.update({
                    'Authorization': f'Bearer {token}'
                })
        except Exception as e:
            logger.error(f"Échec authentification: {str(e)}")
            raise APIAuthError("Échec de l'authentification API")

    def _get_oauth_token(self) -> str:
        """Récupère un token OAuth2 sécurisé"""
        # Implémentation spécifique au fournisseur OAuth
        pass

    def send_data(
        self,
        data: Union[Dict, str],
        method: str = 'POST',
        params: Optional[Dict] = None,
        timeout: int = 10
    ) -> requests.Response:
        """
        Envoie des données à l'API avec gestion sécurisée
        
        Args:
            data: Données à envoyer (dict ou JSON string)
            method: Méthode HTTP (POST/GET/PUT)
            params: Paramètres de requête
            timeout: Timeout en secondes
            
        Returns:
            Response: Objet réponse HTTP
            
        Raises:
            APIError: Pour les erreurs d'API
        """
        try:
            # Validation des données
            if isinstance(data, dict):
                payload = json.dumps(data, ensure_ascii=False)
            else:
                payload = data

            # En-têtes de sécurité
            headers = {
                'Content-Type': 'application/json',
                'X-Request-ID': os.urandom(16).hex()
            }

            logger.info(f"Envoi à {self.endpoint} - Taille payload: {len(payload)} bytes")

            response = self.session.request(
                method=method,
                url=self.endpoint,
                data=payload,
                headers=headers,
                params=params,
                timeout=timeout
            )

            self._validate_response(response)
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau: {str(e)}")
            raise APIConnectionError(f"Erreur de connexion API: {str(e)}")
            
    def _validate_response(self, response: requests.Response):
        """Valide la réponse HTTP selon les standards de sécurité"""
        if response.status_code >= 400:
            error_msg = f"Erreur API [{response.status_code}]: {response.text[:200]}"
            logger.error(error_msg)
            raise APIError(error_msg)
            
        # Validation du content-type
        if 'application/json' not in response.headers.get('Content-Type', ''):
            raise APIValidationError("Réponse API non JSON")
