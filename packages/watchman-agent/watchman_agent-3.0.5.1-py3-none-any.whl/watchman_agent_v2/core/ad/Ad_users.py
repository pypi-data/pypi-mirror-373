import click

from watchman_agent_v2.core.ad.ldap_client import LDAPClient
from watchman_agent_v2.core.config.config_manager import ConfigManager
from watchman_agent_v2.core.services.api.users_api import UserAPIClient
from watchman_agent_v2.core.utils.host.manage_local_host import ManageLocalhost
from watchman_agent_v2.core.services.api.assets_api import AssetAPIClient
from watchman_agent_v2.core.services.api.auth_api import AuthClient
from watchman_agent_v2.core.services.api.exceptions import AuthenticationError
from watchman_agent_v2.core.utils.log_manager import LogManager

class AdUsers:
    
    
    def __init__(self):
        self.config=ConfigManager()
        
    def run(self):
        self.setup_ad()
        # Implémenter la logique de collecte locale
        pass

    def configure(self):
        """Configure le LocalAgent."""
        pass
    
    def setup_ad(self):
        
        try:
            LogManager.info('Connexion à AD ....')
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

            try:
                client = LDAPClient(LDAP_SERVER, LDAP_PORT, USER_DN, PASSWORD, SEARCH_BASE)
                users = client.get_users(GROUP_NAME)
                LogManager.info(f'Nous avons recuperé {len(users)} utilisateurs')
                
            except:
                
                LogManager.error('Error lors de la connexion et la recuperations des utilisateurs par LDAP')
                return
        
            if len(users) == 0 :
                 LogManager.info(f'Aucun utilisateurs dans le domaine ....')
                 return
            LogManager.info(f'Trouve {len(users)} utilisateurs  ....')
            LogManager.info(f'Envoie de ces utilisateurs vers Watchman  ....')
            asset_api=UserAPIClient(credentials={
                    "AGENT-ID": client_id,
                    "AGENT-SECRET": client_secret})
            # send to server
            LogManager.info(f'Envoie des informations vers Watchman ....')
            data={"collaborators":users}
            print(data)
            is_send,error_message=asset_api.create_users(data)
            if is_send :
                LogManager.success(f'Les données sont envoyés avec succès')
            else :
                LogManager.error(f'Une erreur s\'est produite lors de l\'envoie des données ')
                LogManager.error(f'Error : {error_message} ')
                      
        except Exception as error:
            click.echo(f'Erreur {error}')
        
        
        
