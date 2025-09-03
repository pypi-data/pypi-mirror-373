import json
import os
import re
import magic
from typing import Dict, Optional
import click
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from watchman_agent_v2.core.services.api.api_client import APIClient
from watchman_agent_v2.core.services.api.exceptions import InventoryValidationError

class UserAPIClient(APIClient):
    """
    Client spécialisé pour l'envoi de données (inventaire ou utilisateurs)
    avec validation avancée.
    """
    API_BASE_URL = 'https://api.watchman.bj/api/v2/'
    API_ENDPOINT = 'agent/users/'
    
    def __init__(self, credentials: Dict[str, str]):
        full_endpoint = f"{self.API_BASE_URL.rstrip('/')}/{self.API_ENDPOINT.lstrip('/')}"
        super().__init__(full_endpoint, credentials)

    def create_users(self, data) -> bool:
        """
        Envoie des données (JSON) pour créer des utilisateurs avec validation complète.
        
        Args:
            data: Les données à envoyer (ex. un JSON contenant la liste des utilisateurs).
            
        Returns:
            tuple: (True, None) si l'envoi réussit, sinon (False, message d'erreur).
            
        Raises:
            InventoryValidationError: Si la validation côté serveur échoue.
        """
        headers = {
            'Content-Type': "application/json",
            **self.credentials
        }
        
        response = self.send_data(data=data, headers=headers)
        
        # Affichage de la réponse pour debug
        print(f"Réponse du serveur : {response.json()}")
        
        error_message = None
        code = response.status_code
        
        if code != 200:
            try:
                response_data = response.json()
                # Extraction d'un message d'erreur détaillé si disponible
                match = re.search(r"'message': ErrorDetail\(string='([^']*)'", response_data.get('detail', ''))
                if match:
                    error_message = match.group(1)
                else:
                    error_message = response_data.get('detail', 'Erreur inconnue.')
            except Exception:
                error_message = "Erreur serveur ! Veuillez contacter le développeur Watchman."
            
            # Optionnellement, vous pouvez lever une exception
            raise InventoryValidationError(error_message)
        
        return True,error_message

    def send_data(self, data, headers: Optional[Dict] = None):
        """
        Envoie les données au serveur via une requête POST.
        
        Args:
            data: Données à envoyer.
            headers: En-têtes HTTP à utiliser pour la requête.
            
        Returns:
            Response: L'objet réponse de la requête.
        """
        try:
            return self.session.post(
                self.endpoint,
                data=json.dumps(data),
                headers=headers or {},
                timeout=30
            )
        except requests.exceptions.RequestException as e:
            click.echo(f"Erreur réseau : {str(e)}", err=True)
            raise
