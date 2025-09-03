import platform
import logging
import csv
import json
import sys
from typing import List, Dict, Any
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM
import socket
from watchman_agent_v2.core.protocols.http import HttpProtocol
from watchman_agent_v2.core.protocols.snmp import SNMPHandler
from watchman_agent_v2.core.protocols.ssh import SSHProtocol
from watchman_agent_v2.core.protocols.wmi_protocol import WMIProtocol
from watchman_agent_v2.core.utils.host.manage_host import ManageHost
from watchman_agent_v2.core.utils.log_manager import LogManager
from watchman_agent_v2.core.utils.protocol_selector import ProtocolSelector

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ManageAd(ManageHost):
    def __init__(self,
                 ldap_server: str,
                 ldap_user: str,
                 ldap_password: str,
                 search_base: str,
                 domain: str,
                 remote_user: str,
                 remote_password: str):
        """
        Initialise la connexion LDAP et stocke les informations d'authentification pour l'accès distant.
        :param ldap_server: URL ou IP du contrôleur de domaine (ex: 'ldap://dc.domaine.local')
        :param ldap_user: Utilisateur LDAP (ex: 'DOMAIN\\username')
        :param ldap_password: Mot de passe LDAP
        :param search_base: Base de recherche LDAP (ex: 'DC=domaine,DC=local')
        :param domain: Nom de domaine (pour WMI ou WinRM)
        :param remote_user: Identifiant pour se connecter aux machines distantes (généralement identique à ldap_user)
        :param remote_password: Mot de passe associé
        """
        super().__init__()
        self.ldap_server = ldap_server
        self.ldap_user = ldap_user
        self.ldap_password = ldap_password
        self.search_base = search_base
        self.domain = domain
        self.remote_user = remote_user
        self.remote_password = remote_password

        self.conn = None  # Connexion LDAP
        self.logger = LogManager
        self.results: Dict[str, Any] = {'devices': {}}
        self.addresses: List[str] = []
        # networks data 
        self.exclusions = self.config.config['network'].get('exclusions',[])
        self.protocols = self.config.config['network'].get('protocols')
        self.protocol_handlers={
                    'http': HttpProtocol,
                    'snmp': SNMPHandler,
                    'ssh':SSHProtocol,
                    'wmi': WMIProtocol
                        }
        
        self.protocol_selector = ProtocolSelector(self.protocol_handlers,self.protocols)
   
    def connect_ldap(self) -> bool:
        """
        Établit la connexion au serveur LDAP.
        """
        try:
            server = Server(self.ldap_server, get_info=ALL)
            self.conn = Connection(server,
                                   user=self.ldap_user,
                                   password=self.ldap_password,
                                   authentication='SIMPLE',
                                   auto_bind=True)
            self.logger.info("Connexion LDAP établie avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur de connexion LDAP : {e}")
            return False

    def fetch_computers(self, group_dn: str = None) -> None:
        """
        Récupère les machines du domaine ou d'un groupe spécifique.
        :param group_dn: DN du groupe LDAP (optionnel). Si None, tous les objets de type computer sont recherchés.
        """
        if not self.conn:
            self.logger.error("La connexion LDAP n'est pas établie")
            return

        try:
            if group_dn:
                # Recherche des ordinateurs membres d'un groupe spécifique
                search_filter = f'(&(objectCategory=computer)(memberOf={group_dn}))'
            else:
                # Recherche de tous les objets de type computer
                search_filter = '(objectCategory=computer)'

            self.conn.search(search_base=self.search_base,
                             search_filter=search_filter,
                             search_scope=SUBTREE,
                             attributes=['cn', 'dNSHostName'])
            self.logger.info(f"{len(self.conn.entries)} ordinateur(s) trouvé(s)")
            for entry in self.conn.entries:
                # On privilégie le dNSHostName sinon le cn
                hostname = str(entry.dNSHostName) if entry.dNSHostName.value else str(entry.cn)
                
                if hostname:
                    try:
                        ip = socket.gethostbyname(hostname)
                    except socket.gaierror:
                        self.logger.warning(f"Impossible de résoudre {hostname}")
                        ip=hostname
                    self.addresses.append(ip)
                    print(hostname)
                    self.results['devices'][ip] = {
                        'system_info': {'hostname': hostname,"ip":ip},
                        'applications': []
                    }
            if not self.addresses:
                self.logger.warning("Aucun ordinateur trouvé.")
            self.addresses = [
                ip for ip in self.addresses 
                if ip not in self.exclusions
            ]
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des machines : {e}")

    def fetch_installed_applications(self) -> None:
        """
        Pour chaque machine récupérée, se connecte en remote et extrait la liste des applications installées.
        Utilise WMI sous Windows ou WinRM sous Linux.
        """
        current_os = platform.system().lower()
        self.logger.info(f"Système d'exécution détecté : {current_os}")
        for hostname in self.addresses:
            self.logger.info(f"Récupération des applications sur : {hostname}")
            apps = []
            system_info = {}
            # device_results, selected_protocol, handler = self.protocol_selector.select_and_run(hostname)
            if current_os == 'windows':
                # Utilisation de WMI pour Windows
                try:
                    import wmi
                    c = wmi.WMI(computer=hostname,
                                user=self.remote_user,
                                password=self.remote_password)
                    for product in c.Win32_Product():
                        app = {
                            'name': product.Name,
                            'version': product.Version,
                            'vendor': product.Vendor,
                            'type': 'application'  # À adapter si besoin
                        }
                        apps.append(app)
                    for os in c.Win32_OperatingSystem():
                        system_info['os'] = os.Caption
                        system_info['os_version'] = os.Version
                        system_info['architecture'] = os.OSArchitecture

                    for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                        if nic.MACAddress:
                            system_info['mac'] = nic.MACAddress
                            break
                    # add os as apps 
                    apps.append({
                            'name':system_info['os'],
                            'version':system_info['os_version'],
                            "vendor":"*",
                            "type":"os"})
                    self.logger.info(f"{len(apps)} application(s) trouvée(s) sur {hostname} via WMI")
                except Exception as e:
                    self.logger.error(f"Erreur lors de la connexion WMI sur {hostname}: {e}")
            else:
                # Utilisation de WinRM pour Linux (ou autres OS non Windows)
                try:
                    import winrm
                    # Construit l'URL WinRM pour la machine distante
                    # Le port 5985 est utilisé par défaut pour WinRM en HTTP
                   
                    # Construit l'URL WinRM pour la machine distante
                    winrm_url = f'http://{hostname}:5985/wsman'
                    session = winrm.Session(winrm_url, auth=(self.remote_user, self.remote_password), transport='ntlm')
                    self.logger.info('connexion success')
                    # La commande PowerShell pour récupérer les applications installées et infos système
                    ps_script = r"""
$ProgressPreference = 'SilentlyContinue'
$ErrorActionPreference = 'Continue'

# Infos système
$sysinfo = @{    os           = (Get-CimInstance Win32_OperatingSystem).Caption
    os_version   = (Get-CimInstance Win32_OperatingSystem).Version
    architecture = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
    mac          = (Get-CimInstance Win32_NetworkAdapterConfiguration |
                    Where-Object { $_.MACAddress -and $_.IPEnabled } |
                    Select-Object -First 1).MACAddress
}

# Liste des applications installées
$appList = Get-CimInstance Win32_Product |
           Select-Object Name, Version, Vendor

# Conversion en JSON, suppression du flux d'erreur et sortie complète
@{
    system_info  = $sysinfo
    applications = $appList
} |
ConvertTo-Json -Depth 3 2>$null |
Out-String -Width 4096
"""
                    result = session.run_ps(ps_script)
                    if result.status_code == 0:
                        # La sortie est en JSON
                        data = json.loads(result.std_out.decode('utf-8'))
                        
                        # Extraire les infos
                        system_info = data.get('system_info', {})
                        apps_data = data.get('applications', [])

                        # Si un seul objet est retourné, le mettre dans une liste
                        if isinstance(apps_data, dict):
                            apps_data = [apps_data]

                        apps = [{
                            'name': app.get('Name', ''),
                            'version': app.get('Version', ''),
                            'vendor': app.get('Vendor', ''),
                            'type': 'application'
                        } for app in apps_data if app.get('Name')]
                        # add os as apps 
                        apps.append({
                            'name':system_info['os'],
                            'version':system_info['os_version'],
                            "vendor":"*",
                            "type":"os"})
                        self.logger.info(f"{len(apps)} application(s) trouvée(s) sur {hostname} via WinRM")
                    else:
                        err = result.std_err.decode('utf-8')
                        self.logger.error(f"Erreur WinRM sur {hostname}: {err}")
                except Exception as e:
                    self.logger.error(f"Erreur lors de la connexion WinRM sur {hostname}: {e}")

            # Ajouter les informations récupérées (applications + system_info)
            self.results['devices'][hostname]['applications'] = apps
            self.results['devices'][hostname]['system_info'].update(system_info)



    def export_to_csv(self, filename: str = 'applications.csv') -> None:
        """
        Exporte les informations collectées au format CSV.
        """
        if not self.results['devices']:
            self.logger.error("Veuillez récupérer d'abord les informations")
            return
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                # En-têtes du CSV
                headers = [
                    'hostname', 'ip', 'mac', 'os', 'architecture',
                    'application_name', 'application_version', 'vendor', 'type'
                ]
                writer.writerow(headers)
                for hostname, data in self.results['devices'].items():
                    sys_info = data.get('system_info', {})
                    applications = data.get('applications', [])
                    ip = sys_info.get('ip', '')
                    mac = sys_info.get('mac', '')
                    os_name = sys_info.get('os', '')
                    arch = sys_info.get('architecture', '')
                    for app in applications:
                        row = [
                            hostname,
                            ip,
                            mac,
                            os_name,
                            arch,
                            app.get('name', ''),
                            app.get('version', ''),
                            app.get('vendor', ''),
                            app.get('type', '')
                        ]
                        writer.writerow(row)
            self.logger.info(f"CSV généré avec succès : {filename}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export CSV: {e}")

    def export_to_json(self, filename: str = 'system_info.json') -> None:
        """
        Exporte les informations collectées au format JSON.
        """
        if not self.results['devices']:
            self.logger.error("Veuillez récupérer d'abord les informations")
            return
        try:
            data_array = {'assets': []}
            for hostname, data in self.results['devices'].items():
                sys_info = data.get('system_info', {})
                asset = {
                    'hostname': sys_info.get('hostname', ''),
                    'ip': sys_info.get('ip', ''),
                    'mac': sys_info.get('mac', ''),
                    'os': sys_info.get('os', ''),
                    'architecture': sys_info.get('architecture', ''),
                    'applications': data.get('applications', [])
                }
                data_array['assets'].append(asset)
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data_array, jsonfile, indent=4, ensure_ascii=False)
            self.logger.info(f"JSON généré avec succès : {filename}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export JSON: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Paramètres LDAP et domaine
    LDAP_SERVER = "ldap://10.10.15.100"  # ou "ldaps://domaine.local" si vous utilisez LDAPS
    LDAP_PORT = 389                       # 389 pour LDAP ou 636 pour LDAPS
    USER_DN = "GITS\\Bienvenu"            # Format (ex: "DOMAINE\\utilisateur")
    PASSWORD = "Welcom@94513830&"
    # GROUP_NAME peut être None pour récupérer tous les utilisateurs
    LDAP_USER = USER_DN
    LDAP_PASSWORD = PASSWORD
    SEARCH_BASE = "DC=GITS,DC=BJ"
    # Optionnel : DN du groupe pour filtrer les machines
    GROUP_DN = None  # ex: "CN=NomDuGroupe,OU=Groupes,DC=domaine,DC=local"

    # Paramètres pour la connexion distante (WMI ou WinRM)
    REMOTE_USER = LDAP_USER
    REMOTE_PASSWORD = LDAP_PASSWORD

    manager = ManageAd(ldap_server=LDAP_SERVER,
                       ldap_user=LDAP_USER,
                       ldap_password=LDAP_PASSWORD,
                       search_base=SEARCH_BASE,
                       domain="GITS.BJ",
                       remote_user=REMOTE_USER,
                       remote_password=REMOTE_PASSWORD)

    if manager.connect_ldap():
        manager.fetch_computers(group_dn=GROUP_DN)
        manager.fetch_installed_applications()
        
        # Export des résultats
        manager.export_to_json('system_info.json')
