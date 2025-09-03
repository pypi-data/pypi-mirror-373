import os
from watchman_agent_v2.core.services.api.assets_api import AssetAPIClient
from watchman_agent_v2.core.services.api.auth_api import AuthClient
from watchman_agent_v2.core.services.api.exceptions import AuthenticationError
from watchman_agent_v2.core.utils.log_manager import LogManager
from watchman_agent_v2.core.utils.host.manage_network_host import ManageNetworkHost
from .base_agent import BaseAgent

class NetworkAgent(BaseAgent):
    """
    Agent en mode réseau (CIDR/IP range).
    """
    def run(self):
        """Exécute la collecte d'informations en mode réseau."""
        # Implémenter la logique de collecte réseau
        self.setup_agent()

    def configure(self):
        """Configure le NetworkAgent."""
        pass
    
    def setup_agent(self):
        
        try:
            LogManager.info('Connexion à Watchman ....')
            try:
                client_id=self.config.config['api']['client_id']
                client_secret=self.config.decrypt(self.config.config['api']['client_secret'])
            except Exception as e:
                LogManager.error(f"Erreur lors de la récupération des informations d'authentification")
                return
            auth_client=AuthClient(
            client_id=client_id,
            client_secret=client_secret
             )
            
            token=''
            
            if auth_client.test_connection():
                token = auth_client.get_token()
                LogManager.success(f'Authentification réussie')
            else:
                LogManager.error(f"Impossible de se connecter au service d'authentification ")
                raise AuthenticationError()
            
            LogManager.info('Recuperations des adresses ....')
            manager=ManageNetworkHost()
            manager.collect_all_info()
            file_path = 'watchman_agent_v2/data/json/watchman_system_info.json'
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            manager.export_to_json(file_path)
            asset_api=AssetAPIClient(credentials={
                    "AGENT-ID": client_id,
                    "AGENT-SECRET": client_secret})
            # manage_host.export_to_csv('watchman_agent_v2/data/csv/watchman_system_info.csv')
            # to json
            LogManager.info(f'Envoie des informations vers Watchman ....')
            
            is_send, report, error_message = asset_api.send_assets(file_path)

            if is_send:
                success_msg = (
                    f"Envoi réussi de {report.get('total', 0)} actifs | "
                    f"Succès: {report.get('success', 0)}/{report.get('total', 0)} | "
                    f"Taux: {report.get('success', 0)/max(report.get('total', 1), 1)*100:.1f}%"
                )
                LogManager.success(success_msg)
                
                # Log détaillé des erreurs si besoin
                if report.get('failures', 0) > 0:
                    error_details = "\n".join(
                        [f"[{err['asset']}] {err['error']}" 
                        for err in report.get('errors', [])]
                    )
                    LogManager.error(f"Erreurs mineures détectées (non bloquantes):\n{error_details}")

            else:
                error_msg = (
                    f"Échec de l'envoi - {error_message} | "
                    f"Rapport partiel: {report.get('success', 0)}/{report.get('total', 0)} réussis" 
                    if report 
                    else f"Échec complet - Aucun rapport disponible"
                )
                LogManager.error(error_msg)
                
                # Log supplémentaire si on a des détails d'erreur
                if report and report.get('errors'):
                    errors_str = "\n".join(
                        [f"- {err['asset']}: {err['error'][:100]}..." 
                        for err in report.get('errors', [])]
                    )
                    LogManager.error(f"Détails des erreurs:\n{errors_str}")
            
        except Exception as error:
            LogManager.error(f'Erreur {error}')
        
        
        
