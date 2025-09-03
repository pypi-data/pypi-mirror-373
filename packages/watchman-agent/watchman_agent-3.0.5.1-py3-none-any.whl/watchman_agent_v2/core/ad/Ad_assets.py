from watchman_agent_v2.core.config.config_manager import ConfigManager
from watchman_agent_v2.core.services.api.assets_api import AssetAPIClient
from watchman_agent_v2.core.services.api.auth_api import AuthClient
from watchman_agent_v2.core.services.api.exceptions import AuthenticationError
from watchman_agent_v2.core.utils.host.manage_ad import ManageAd
from watchman_agent_v2.core.utils.log_manager import LogManager
from watchman_agent_v2.core.utils.host.manage_network_host import ManageNetworkHost

class AdAssets:
    
    def __init__(self):
        self.config=ConfigManager()
        
        
    def run(self):
        """Exécute la collecte d'informations en mode réseau."""
        # Implémenter la logique de collecte réseau
        self.setup_agent()

    def configure(self):
        """Configure le NetworkAgent."""
        pass
    
    def setup_agent(self):
        
        try:
            LogManager.info('Connexion à AD ....')
            try:
                client_id=self.config.config['api']['client_id']
                print(f'client_id {client_id} ')
                client_secret=self.config.decrypt(self.config.config['api']['client_secret'])
            except Exception as e:
                LogManager.error(f"Erreur lors de la récupération des informations d'authentification: {e}")
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
            
            LogManager.info(f'Recuperations des utilisateurs ....')
            # recuperations des configurations
            ad_config= self.config.config['ad']
            if all(ad_config.get(attr) for attr in ['ldap_server', 'ldap_port', 'search_base','user','password']):
                LogManager.info(f'Recuperations des valeurs des configs ....')
            else:
                LogManager.error(f'Configuration LDAP invalide ....')
                return
            LDAP_SERVER = ad_config['ldap_server']  # ou "ldaps://domaine.local" si vous utilisez LDAPS
            LDAP_PORT = int(ad_config['ldap_port'])                      # 389 pour LDAP ou 636 pour LDAPS
            USER_DN =  self.config.decrypt(ad_config['user'])            # Format (ex: "DOMAINE\\utilisateur")
            PASSWORD = self.config.decrypt(ad_config['password'])
            SEARCH_BASE = ad_config['search_base']
            # GROUP_NAME peut être None pour récupérer tous les utilisateurs
            GROUP_NAME = ad_config.get('group',None)
            DOMAIN = ad_config.get('domain',"")
            
            LDAP_USER = USER_DN
            LDAP_PASSWORD = PASSWORD
            # Optionnel : DN du groupe pour filtrer les machines
            GROUP_DN = GROUP_NAME  # ex: "CN=NomDuGroupe,OU=Groupes,DC=domaine,DC=local"

            # Paramètres pour la connexion distante (WMI ou WinRM)
            REMOTE_USER = LDAP_USER
            REMOTE_PASSWORD = LDAP_PASSWORD

            manager = ManageAd(ldap_server=LDAP_SERVER,
                            ldap_user=LDAP_USER,
                            ldap_password=LDAP_PASSWORD,
                            search_base=SEARCH_BASE,
                            domain=DOMAIN,
                            remote_user=REMOTE_USER,
                            remote_password=REMOTE_PASSWORD)

            if manager.connect_ldap():
                manager.fetch_computers(group_dn=GROUP_DN)
                manager.fetch_installed_applications()
                # Export des résultats
                path='watchman_agent_v2/data/json/watchman_system_info.json'
                manager.export_to_json(path)
                asset_api=AssetAPIClient(credentials={
                    "AGENT-ID": client_id,
                    "AGENT-SECRET": client_secret})
            # manage_host.export_to_csv('watchman_agent_v2/data/csv/watchman_system_info.csv')
            # to json
                LogManager.info(f'Envoie des informations vers Watchman ....')
            
                file_path='watchman_agent_v2/data/json/watchman_system_info.json'
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
            else :
                LogManager.error(f'Nous n\'avons pas pu trouver')
                
        except Exception as error:
            LogManager.error(f'Erreur {error}')
        
        
        
