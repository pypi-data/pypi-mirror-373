#!/usr/bin/env python3
from datetime import datetime, timedelta
import logging
import ssl
from ldap3 import Server, Connection, ALL, SUBTREE, Tls

# Configuration du logging pour suivre l'exécution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LDAPClient:
    """
    Client LDAP pour se connecter à un Active Directory et récupérer des informations.
    """

    def __init__(self, ldap_server, ldap_port, user_dn, password, search_base):
        """
        Initialise le client LDAP.

        :param ldap_server: Adresse du serveur LDAP (ex: 'ldap://domaine.local' ou 'ldaps://domaine.local')
        :param ldap_port: Port du serveur LDAP (389 pour LDAP ou 636 pour LDAPS)
        :param user_dn: DN de l'utilisateur pour se connecter (ex: 'DOMAIN\\utilisateur')
        :param password: Mot de passe de l'utilisateur
        :param search_base: Base de recherche dans l'annuaire (ex: 'DC=domaine,DC=local')
        """
        self.ldap_server = ldap_server
        self.ldap_port = ldap_port
        self.user_dn = user_dn
        self.password = password
        self.search_base = search_base
        self.conn = None
        self.connect()

    def connect(self):
        """
        Établit la connexion au serveur LDAP en utilisant une authentification SIMPLE.
        """
        try:
            tls_configuration = Tls(validate=ssl.CERT_NONE)
            use_ssl = self.ldap_port == 636
            server = Server(
                self.ldap_server,
                port=self.ldap_port,
                use_ssl=use_ssl,
                get_info=ALL,
                tls=tls_configuration
            )
            self.conn = Connection(
                server,
                user=self.user_dn,
                password=self.password,
                authentication='SIMPLE',
                auto_bind=True
            )
            logger.info("Connexion réussie au serveur LDAP.")
        except Exception as e:
            logger.exception("Erreur lors de la connexion au serveur LDAP: %s", e)
            raise

    def get_users(self, group_name=None):
        """
        Récupère les utilisateurs formatés avec email, prénom et nom.
        Format de retour :
        [
            {"email": "alice@example.com", "first_name": "Alice", "last_name": "Johnson"},
            {"email": "bob@example.com", "first_name": "Bob", "last_name": "Smith"}
        ]
        """
        try:
            users = []
            # [Début] Partie existante inchangée pour la récupération des membres_dn
            if group_name:
                group_filter = f"(&(objectClass=group)(cn={group_name}))"
                self.conn.search(
                    self.search_base,
                    group_filter,
                    search_scope=SUBTREE,
                    attributes=['member']
                )
                if len(self.conn.entries) == 0:
                    logger.error("Groupe '%s' non trouvé.", group_name)
                    return []
                group_entry = self.conn.entries[0]
                membres_dn = group_entry.member.values if 'member' in group_entry else []
            else:
                membres_dn = []
                user_filter = "(&(objectClass=user)(!(objectClass=computer)))"
                self.conn.search(
                    self.search_base,
                    user_filter,
                    search_scope=SUBTREE,
                    attributes=['distinguishedName']
                )
                for entry in self.conn.entries:
                    membres_dn.append(entry.entry_dn)
            # [Fin] Partie existante inchangée

            for dn in membres_dn:
                self.conn.search(
                    dn,
                    '(objectClass=user)',
                    search_scope='BASE',
                    attributes=['mail', 'displayName']
                )
                
                if self.conn.entries:
                    user_entry = self.conn.entries[0]
                    
                    # Extraction du nom complet
                    display_name = user_entry.displayName.value if 'displayName' in user_entry else ''
                    name_parts = display_name.split(' ', 1)  # Sépare prénom/nom
                    
                    # Formatage selon les besoins
                    users.append({
                        "email": user_entry.mail.value if 'mail' in user_entry else None,
                        "first_name": name_parts[0] if len(name_parts) > 0 else '',
                        "last_name": name_parts[1] if len(name_parts) > 1 else ''
                    })

            return users

        except Exception as e:
            logger.exception("Erreur lors de la récupération des utilisateurs: %s", e)
            return []
        
    def get_users(self, group_name=None):
        """
        Récupère les utilisateurs formatés avec email, prénom et nom.
        Format de retour :
        [
            {
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Johnson",
                "login": "ajohnson"  # sAMAccountName
            },
            {
                "email": "bob@example.com",
                "first_name": "Bob",
                "last_name": "Smith",
                "login": "bsmith"
            }
        ]
        """
        try:
            users = []
            
            # 1. Récupération des DN des membres (groupe ou tous les utilisateurs)
            if group_name:
                # Recherche du groupe par son nom
                group_filter = f"(&(objectClass=group)(cn={group_name}))"
                self.conn.search(
                    self.search_base,
                    group_filter,
                    search_scope=SUBTREE,
                    attributes=['member']
                )
                
                if not self.conn.entries:
                    logger.error(f"Groupe '{group_name}' non trouvé.")
                    return []
                    
                membres_dn = self.conn.entries[0].member.values if 'member' in self.conn.entries[0] else []
            else:
                # Recherche de tous les utilisateurs (exclut les comptes machines)
                user_filter = "(&(objectClass=user)(!(objectClass=computer)))"
                self.conn.search(
                    self.search_base,
                    user_filter,
                    search_scope=SUBTREE,
                    attributes=['distinguishedName']
                )
                membres_dn = [entry.entry_dn for entry in self.conn.entries]

            # 2. Récupération des détails pour chaque utilisateur
            for dn in membres_dn:
                self.conn.search(
                    dn,
                    '(objectClass=user)',
                    search_scope='BASE',
                    attributes=['mail', 'givenName', 'sn', 'sAMAccountName', 'displayName']
                )
                
                if not self.conn.entries:
                    continue
                    
                user_entry = self.conn.entries[0]
                
                # Fallback: Si givenName/sn manquants, on découpe displayName
                display_name = user_entry.displayName.value if 'displayName' in user_entry else ""
                first_name = user_entry.givenName.value if 'givenName' in user_entry else display_name.split(' ')[0]
                last_name = user_entry.sn.value if 'sn' in user_entry else ' '.join(display_name.split(' ')[1:])
                
                if ('mail' in user_entry) and (user_entry.mail.value is not None):
                    users.append({
                        "email": user_entry.mail.value if 'mail' in user_entry else None,
                        "first_name": first_name,
                        "last_name": last_name,
                        "login": user_entry.sAMAccountName.value if 'sAMAccountName' in user_entry else None
                    })

            return users

        except Exception as e:
            logger.exception(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
            return []

    @staticmethod
    def convert_ad_timestamp(ad_timestamp):
        """
        Convertit le timestamp Active Directory (nombre de 100-nanosecondes depuis 1601-01-01)
        en datetime Python.
        """
        if not ad_timestamp:
            return None
            
        try:
            # Conversion du timestamp Windows en datetime
            epoch_start = datetime(1601, 1, 1)
            microseconds = int(ad_timestamp) / 10
            return epoch_start + timedelta(microseconds=microseconds)
        except Exception as e:
            logger.warning("Erreur de conversion du timestamp: %s", e)
            return None

    def disconnect(self):
        """
        Ferme la connexion LDAP.
        """
        if self.conn:
            self.conn.unbind()
            logger.info("Connexion LDAP fermée.")


if __name__ == "__main__":
    # Paramètres de connexion à adapter selon votre environnement
    LDAP_SERVER = "ldap://10.10.15.100"  # ou "ldaps://domaine.local" si vous utilisez LDAPS
    LDAP_PORT = 389                       # 389 pour LDAP ou 636 pour LDAPS
    USER_DN = "GITS\\Bienvenu"            # Format (ex: "DOMAINE\\utilisateur")
    PASSWORD = "PASSWORD"
    SEARCH_BASE = "DC=GITS,DC=BJ"
    # GROUP_NAME peut être None pour récupérer tous les utilisateurs
    GROUP_NAME = None

    try:
        client = LDAPClient(LDAP_SERVER, LDAP_PORT, USER_DN, PASSWORD, SEARCH_BASE)
        utilisateurs = client.get_users(GROUP_NAME)
        if utilisateurs:
            for user in utilisateurs:
                print(user)
        else:
            print("Aucun utilisateur trouvé ou une erreur s'est produite lors de la récupération.")
            
#         full_machines_data = client.get_machines(include_attributes=True)

# # Affichage des résultats
#         for machine in full_machines_data:
#             print(machine)
#             print(f"Machine: {machine['sAMAccountName']}")
#             print(f"Dernière connexion: {machine['last_logon']}")
#             print(f"Système d'exploitation: {machine['os']} {machine['os_version']}\n")
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
