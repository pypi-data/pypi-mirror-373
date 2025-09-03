import logging
import ssl
from typing import Dict, List
import pythoncom
import watchman_agent_v2.core.protocols.wmi_protocol as wmi_protocol
from ldap3 import Server, Connection, Tls, ALL, SUBTREE

logger = logging.getLogger(__name__)

class SecureSystemInspector:
    """
    Classe combinant WMI (Windows Management Instrumentation) et LDAPS
    pour une collecte sécurisée d'informations système et AD.
    """
    
    def __init__(self, ldap_config: Dict, wmi_credentials: Dict = None):
        self.ldap_config = ldap_config
        self.wmi_credentials = wmi_credentials or {}
        self.ldap_conn = None
        self.wmi_conn = None

    def connect_ldaps(self):
        """Établit une connexion sécurisée LDAPS"""
        try:
            tls_config = Tls(
                validate=ssl.CERT_REQUIRED,
                version=ssl.PROTOCOL_TLSv1_2
            )
            server = Server(
                self.ldap_config['server'],
                use_ssl=True,
                tls=tls_config,
                get_info=ALL
            )
            self.ldap_conn = Connection(
                server,
                user=self.ldap_config['user'],
                password=self.ldap_config['password'],
                auto_bind=True
            )
            logger.info("Connexion LDAPS établie avec succès")
        except Exception as e:
            logger.error(f"Erreur LDAPS: {str(e)}")
            raise

    def connect_wmi(self):
        """Établit une connexion WMI sécurisée"""
        try:
            pythoncom.CoInitialize()
            self.wmi_conn = wmi_protocol.WMI(
                computer=self.wmi_credentials.get('host', 'localhost'),
                user=self.wmi_credentials.get('user'),
                password=self.wmi_credentials.get('password'),
                namespace='root\\Microsoft\\Windows\\Storage'
            )
            logger.info("Connexion WMI sécurisée établie")
        except Exception as e:
            logger.error(f"Erreur WMI: {str(e)}")
            raise

    def get_combined_system_info(self) -> Dict:
        """Combine les données WMI et AD"""
        return {
            'local_system': self.get_wmi_system_info(),
            'ad_data': self.get_ad_computer_info(),
            'software': self.get_installed_software(),
            'storage': self.get_secure_storage_info()
        }

    def get_wmi_system_info(self) -> Dict:
        """Récupère les informations système via WMI"""
        info = {}
        try:
            cs = self.wmi_conn.Win32_ComputerSystem()[0]
            os = self.wmi_conn.Win32_OperatingSystem()[0]
            info = {
                'manufacturer': cs.Manufacturer,
                'model': cs.Model,
                'domain': cs.Domain,
                'os_version': os.Caption,
                'last_boot': os.LastBootUpTime
            }
        except Exception as e:
            logger.error(f"Erreur WMI système: {str(e)}")
        return info

    def get_ad_computer_info(self) -> Dict:
        """Récupère les informations AD via LDAPS"""
        search_base = f"OU=Computers,{self.ldap_config['base_dn']}"
        search_filter = f"(cn={self.wmi_credentials.get('host', '*')})"
        
        try:
            self.ldap_conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['*']
            )
            return self.ldap_conn.entries[0].entry_attributes_as_dict
        except Exception as e:
            logger.error(f"Erreur AD: {str(e)}")
            return {}

    def get_installed_software(self) -> List[Dict]:
        """Liste les logiciels installés de manière sécurisée"""
        software = []
        try:
            for pkg in self.wmi_conn.Win32_Product():
                software.append({
                    'name': pkg.Name,
                    'version': pkg.Version,
                    'vendor': pkg.Vendor,
                    'install_date': pkg.InstallDate
                })
        except Exception as e:
            logger.error(f"Erreur logiciels: {str(e)}")
        return software

    def get_secure_storage_info(self) -> Dict:
        """Récupère les informations de stockage chiffrées"""
        try:
            disks = {}
            for disk in self.wmi_conn.MSFT_PhysicalDisk():
                disks[disk.DeviceId] = {
                    'model': disk.Model,
                    'size_GB': int(disk.Size) // (1024**3) if disk.Size else 0,
                    'encrypted': disk.IsEncrypted,
                    'health_status': disk.HealthStatus
                }
            return disks
        except Exception as e:
            logger.error(f"Erreur stockage: {str(e)}")
            return {}

    def __del__(self):
        """Nettoyage sécurisé des connexions"""
        if self.ldap_conn:
            self.ldap_conn.unbind()
        if self.wmi_conn:
            pythoncom.CoUninitialize()

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration
    LDAP_CONFIG = {
        'server': '10.10.15.100',
        'base_dn': 'dc=GITS,dc=BJ',
        'user': 'GITS\\Bienvenu',
        'password': 'Welcom@94513830&'
    }

    WMI_CREDS = {
        'host': '10.10.15.100',
        'user': 'GITS\\Bienvenu',
        'password': 'Welcom@94513830&'
    }

    # Initialisation
    inspector = SecureSystemInspector(LDAP_CONFIG, WMI_CREDS)
    
    try:
        inspector.connect_ldaps()
        inspector.connect_wmi()
        
        system_data = inspector.get_combined_system_info()
        
        # Affichage des résultats
        print("=== Informations Système ===")
        print(f"Modèle: {system_data['local_system']['model']}")
        print(f"Domaine AD: {system_data['ad_data']['distinguishedName']}")
        
        print("\n=== Logiciels Installés ===")
        for soft in system_data['software'][:5]:
            print(f"- {soft['name']} ({soft['version']})")

    except Exception as e:
        print(f"Erreur critique: {str(e)}")