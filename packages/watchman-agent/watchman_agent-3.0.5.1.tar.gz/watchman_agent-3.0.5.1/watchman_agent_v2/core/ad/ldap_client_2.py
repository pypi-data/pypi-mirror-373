from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException
from typing import List, Dict, Optional
import ssl

class ADUserManager:
    """Classe pour gérer les interactions LDAP avec Active Directory"""
    
    def __init__(self, server: str, domain: str, username: str, password: str):
        self.server = server
        self.domain = domain
        self.username = username
        self.password = password
        self.conn = None
        self.domain_dn = self._domain_to_dn(domain)
        
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        
    @staticmethod
    def _domain_to_dn(domain: str) -> str:
        """Convertit un nom de domaine en Distinguished Name (DN)"""
        return ','.join([f'DC={part}' for part in domain.split('.')])
    
    def connect(self, verify_ssl: bool = False) -> bool:
        """Établit une connexion sécurisée avec le serveur LDAP"""
        try:
            tls_config = ssl.create_default_context()
            tls_config.check_hostname = verify_ssl
            tls_config.verify_mode = ssl.CERT_REQUIRED if verify_ssl else ssl.CERT_NONE

            ldap_server = Server(
                self.server, 
                use_ssl=True, 
                tls=tls_config
            )
            
            self.conn = Connection(
                ldap_server,
                user=f'{self.username}@{self.domain}',
                password=self.password,
                authentication='NTLM',
                auto_bind=True
            )
            return True
        except LDAPException as e:
            raise ADConnectionError(f"Échec de la connexion LDAP: {e}")
    
    def disconnect(self):
        """Ferme proprement la connexion LDAP"""
        if self.conn:
            self.conn.unbind()
            self.conn = None
            
    def get_all_users(self, attributes: List[str] = None) -> List[Dict]:
        """Récupère tous les utilisateurs du domaine"""
        default_attrs = ['sAMAccountName', 'givenName', 'sn', 'mail', 'userPrincipalName']
        search_filter = "(&(objectClass=user)(objectCategory=person))"
        return self._search_directory(search_filter, attributes or default_attrs)
    
    def get_group_members(self, group_name: str, ou: str = "Groups", recursive: bool = True) -> List[Dict]:
        """Récupère les membres d'un groupe avec gestion de l'imbrication"""
        group_dn = f"CN={group_name},OU={ou},{self.domain_dn}"
        matching_rule = '1.2.840.113556.1.4.1941' if recursive else None
        search_filter = f"(memberOf:{matching_rule if recursive else ''}={group_dn})"
        return self._search_directory(search_filter, ['sAMAccountName', 'memberOf'])
    
    def _search_directory(self, search_filter: str, attributes: List[str]) -> List[Dict]:
        """Exécute une recherche générique dans l'annuaire"""
        if not self.conn or not self.conn.bound:
            raise ADConnectionError("Non connecté au serveur LDAP")
            
        try:
            entries = []
            self.conn.search(
                search_base=self.domain_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes,
                paged_size=1000,
                generator=False
            )
            
            for entry in self.conn.entries:
                entries.append({attr: entry[attr].value for attr in attributes})
                
            return entries
        except LDAPException as e:
            raise ADOperationError(f"Erreur de recherche LDAP: {e}")

class ADConnectionError(Exception):
    """Erreur personnalisée pour les problèmes de connexion"""
    pass

class ADOperationError(Exception):
    """Erreur personnalisée pour les opérations LDAP"""
    pass

# Exemple d'utilisation
if __name__ == "__main__":
    try:
        with ADUserManager(
            server="dc.example.com",
            domain="example.com",
            username="admin_user",
            password="secure_password"
        ) as ad_manager:
            
            # Récupération de tous les utilisateurs
            all_users = ad_manager.get_all_users()
            print(f"Total utilisateurs: {len(all_users)}")
            
            # Récupération des membres d'un groupe
            dev_group = ad_manager.get_group_members("Developers", ou="IT_Groups")
            print(f"Membres du groupe Developers: {len(dev_group)}")
            
    except ADConnectionError as e:
        print(f"Erreur de connexion: {e}")
    except ADOperationError as e:
        print(f"Erreur d'opération: {e}")