from datetime import datetime
import json
import os
from abc import ABC
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from watchman_agent_v2.core.protocols.protocol_factory import BaseProtocol
import httpx

from watchman_agent_v2.core.utils.log_manager import LogManager


class HttpProtocol(BaseProtocol):
    """
    Implémentation avancée du protocole HTTP avec gestion d'erreurs améliorée,
    validation de configuration et support async/await.
    """

    def __init__(self):
        super().__init__()
        self._client: Optional[httpx.Client] = None
        load_dotenv()  # Chargement une seule fois
        self.default_timeout = 100.0
        self.connect()

    def connect(self) -> None:
        """Initialise le client HTTP avec une session persistante"""
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.default_timeout,
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=10)
            )

    def collect_info(self, ip: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collecte les informations via HTTP avec gestion avancée des erreurs
        
        Args:
            ip: Adresse IP cible
            config: Configuration spécifique au protocole
        
        Returns:
            Données formatées ou erreur
            
        Raises:
            ProtocolError: Pour les erreurs spécifiques au protocole
        """
        # Validation de la configuration
        required_keys = {'api_key', 'port'}
        if missing := required_keys - config.keys():
            raise ValueError(f"Configuration manquante: {missing}")

        # Construction de l'URL
        port = config['port']
        endpoint = config.get('endpoint', '/apps')
        url = f"http://{ip}:{port}{endpoint}"

        # Gestion des headers
        headers = {
            "WATCHMAN-API-KEY": config['api_key'],
            "User-Agent": "WatchmanAgent/2.0"
        }
        

        try:
            response = self._client.get(
                url,
                headers=headers,
                params=config.get('query_params'),
                timeout=config.get('timeout', self.default_timeout)
            )
            response.raise_for_status()
            
            return self._format_response(response.json())
            
        except httpx.HTTPStatusError as e:
            LogManager.error(f"Erreur HTTP [{e.response.status_code}] sur {url}")
            raise ProtocolError(f"Erreur serveur: {e.response.status_code}") from e
        except httpx.RequestError as e:
            LogManager.error(f"Erreur de connexion à {url}: {str(e)}")
            raise ProtocolError("Erreur réseau") from e
        except (json.JSONDecodeError, ValueError) as e:
            LogManager.error(f"Erreur de décodage JSON depuis {url}")
            raise ProtocolError("Réponse invalide") from e

    def _format_response(self, raw_data: Dict) -> Dict:
        """Normalise la réponse HTTP"""
        return raw_data

    def disconnect(self) -> None:
        """Ferme proprement la connexion HTTP"""
        if self._client:
            self._client.close()
            self._client = None


class ProtocolError(Exception):
    """Exception personnalisée pour les erreurs de protocole"""
    pass
