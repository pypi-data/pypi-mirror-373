import platform
import json

from watchman_agent_v2.core.utils.log_manager import LogManager
from watchman_agent_v2.core.protocols.protocol_factory import BaseProtocol


class WMIProtocol(BaseProtocol):
    """
    Classe permettant de récupérer des informations système et les applications installées sur une machine Windows.
    Elle gère les connexions locales (via WMI, uniquement sous Windows) et distantes (via WMI sur Windows ou WinRM depuis Linux).
    """
    def __init__(self):
        super().__init__()
        self.conn = None
        self.logger=LogManager
        self.remote_mode = False  # Flag indiquant une connexion distante
        self.results={'system_info':{},'applications':[]}
    

    def fetch_installed_applications(self, ip: str, username: str = None, password: str = None, port: int = 135) -> None:
        """
        Pour chaque machine récupérée, se connecte en remote et extrait la liste des applications installées.
        Utilise WMI sous Windows ou WinRM sous Linux.
        """
        current_os = platform.system().lower()
        self.logger.info(f"Système d'exécution détecté : {current_os}")
        hostname=ip
        self.remote_user=username
        self.remote_password=password
        self.logger.info(f"Récupération des applications sur : {hostname}")
        apps = []
        system_info = {}
        if current_os == 'windows':
            # Utilisation de WMI pour Windows
            try:
                import wmi
                if ip in ["localhost", "127.0.0.1"]:
                    # Connexion locale (uniquement possible sous Windows)
                    if platform.system() != "Windows":
                        raise Exception("La connexion locale WMI est uniquement supportée sous Windows.")
                    try:
                        c = wmi.WMI(computer=ip)
                        print(f"Connexion locale réussie à {ip}")
                    except Exception as e:
                        print(f"Erreur lors de la connexion locale WMI: {str(e)}")
                        raise
                else:
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
                    system_info['hostname'] = os.CSName
                    system_info['ip'] = ip
                    system_info['os'] = os.Caption
                    system_info['version'] = os.Version
                    system_info['architecture'] = os.OSArchitecture

                for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                    if nic.MACAddress:
                        system_info['mac'] = nic.MACAddress
                        break
                # add os as apps 
                apps.append({
                        'name':system_info['os'],
                        'version':system_info['version'],
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
                session = winrm.Session(winrm_url, auth=(self.config.decrypt(self.remote_user), self.config.decrypt(self.remote_password)), transport='ntlm')
                self.logger.info(f"Connexion avec succès ")
                # La commande PowerShell pour récupérer les applications installées et infos système
                ps_script = """
                $sysinfo = @{
                    hostname = (Get-WmiObject -Class Win32_ComputerSystem).Name
                    os = (Get-WmiObject -Class Win32_OperatingSystem).Caption
                    version = (Get-WmiObject -Class Win32_OperatingSystem).Version
                    architecture = (Get-WmiObject -Class Win32_OperatingSystem).OSArchitecture
                    mac = (Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Where-Object { $_.MACAddress -and $_.IPEnabled -eq $true } | Select-Object -First 1).MACAddress
                }

                $apps = Get-WmiObject -Class Win32_Product |
                    Select-Object Name, Version, Vendor

                @{
                    system_info = $sysinfo
                    applications = $apps
                } | ConvertTo-Json -Depth 3
                """
                result = session.run_ps(ps_script)
                if result.status_code == 0:
                    # La sortie est en JSON
                    data = json.loads(result.std_out.decode('utf-8'))
                    
                    # Extraire les infos
                    system_info = data.get('system_info', {})
                    system_info.update({'ip':ip})
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
                        'version':system_info['version'],
                        "vendor":"*",
                        "type":"os"})
                    self.logger.info(f"{len(apps)} application(s) trouvée(s) sur {hostname} via WinRM")
                else:
                    err = result.std_err.decode('utf-8')
                    self.logger.error(f"Erreur WinRM sur {hostname}: {err}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la connexion WinRM sur {hostname}: {e}")

            # Ajouter les informations récupérées (applications + system_info)
            self.results['applications'] = apps
            self.results['system_info'].update(system_info)


    def collect_info(self, ip: str, config: dict):
        """
        Récupère les informations système et la liste des applications installées.
        
        Pour une connexion locale, aucune authentification n'est nécessaire.
        Pour une connexion distante, le dictionnaire 'config' doit contenir au minimum 'username' et 'password'.
        """
        if ip in ["localhost", "127.0.0.1"]:
            username = None
            password = None
            port = config.get('port', 135)
        else:
            required_keys = {'username', 'password'}
            missing = required_keys - config.keys()
            if missing:
                return {"error": f"Configuration manquante: {missing}"}
            username = config.get('username')
            password = config.get('password')
            port = config.get('port', 5985)  # port pour WMI ou WinRM (par défaut, WinRM utilise 5985)
        
        self.fetch_installed_applications(ip,username,password,port)
        return {
            "system_info": self.results['system_info'],
            "applications": self.results['applications']
        }


if __name__ == "__main__":
    import getpass

    # ip = input("Adresse IP (entrez 'localhost' pour une connexion locale) : ").strip()
    ip='10.10.15.100'
    if ip in ["localhost", "127.0.0.1"]:
        config = {}
    else:
        # username = input("Nom d'utilisateur : ")
        # password = getpass.getpass("Mot de passe : ")
        USER_DN = ""            # Format (ex: "DOMAINE\\utilisateur")
        PASSWORD = ""
        # Pour WinRM, le port par défaut est généralement 5985 (non sécurisé)
        port_input = 135
        port = int(port_input) if port_input else 135
        config = {"username": USER_DN, "password": PASSWORD, "port": port}

    client = WMIProtocol()
    info = client.collect_info(ip, config)
    print(json.dumps(info, indent=4, ensure_ascii=False))
