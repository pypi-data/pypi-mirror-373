import json
import os
import paramiko
from typing import Dict, Any, Optional

from watchman_agent_v2.core.protocols.protocol_factory import BaseProtocol
from watchman_agent_v2.core.utils.functions import parse_version
from watchman_agent_v2.core.utils.log_manager import LogManager

class SSHProtocol(BaseProtocol):
    def __init__(self):
        super().__init__()
        self._client = None
        self.default_timeout = 10.0
        
    def load_private_key_by_filename(self,key_path: str, passphrase: Optional[str] = None):
        """
        Charge une clé privée SSH en se basant sur le nom du fichier.
        
        :param key_path: Chemin vers la clé privée
        :param passphrase: Mot de passe de la clé si nécessaire
        :return: Objet paramiko.PKey
        :raises: ValueError si le type est inconnu ou en cas d'échec
        """
        filename = os.path.basename(key_path).lower()

        try:
            if "rsa" in filename:
                return paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
            elif "ed25519" in filename:
                return paramiko.Ed25519Key.from_private_key_file(key_path, password=passphrase)
            elif "ecdsa" in filename:
                return paramiko.ECDSAKey.from_private_key_file(key_path, password=passphrase)
            elif "dsa" in filename or "dss" in filename:
                return paramiko.DSSKey.from_private_key_file(key_path, password=passphrase)
            else:
                raise ValueError(f"Impossible de déduire le type de clé à partir du nom de fichier : {filename}")
        except paramiko.PasswordRequiredException:
            raise ValueError("La clé est protégée par une passphrase, mais aucune n'a été fournie.")
        except paramiko.SSHException as e:
            raise ValueError(f"Erreur lors du chargement de la clé SSH : {str(e)}")
        
    def connect(self, ip: str, username: str, password: str = None, port: int = 22, key_path: str = None, passphrase: str = None) -> None:
        """Initialise la connexion SSH avec mot de passe ou clé privée"""
        if self._client is None:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if key_path:
                # Authentification par clé
                pkey = self.load_private_key_by_filename(key_path, passphrase=passphrase)
                self._client.connect(
                    ip,
                    username=username,
                    port=port if port else 22,
                    pkey=pkey,
                    # key_filename=key_path,
                    # passphrase=passphrase,
                    timeout=self.default_timeout,
                    look_for_keys=False,
                    allow_agent=False
                )
            else:
                # Authentification par mot de passe
                self._client.connect(
                    ip,
                    username=username,
                    password=password,
                    port=port if port else 22,
                    timeout=self.default_timeout,
                    look_for_keys=False,
                    allow_agent=False
                )

        except paramiko.AuthenticationException:
            raise ValueError("Échec de l'authentification SSH.")
        except paramiko.SSHException as e:
            raise RuntimeError(f"Erreur SSH : {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Connexion SSH échouée : {str(e)}")
    def detect_remote_os(self) -> str:
        """
        Détecte le système d'exploitation de la machine distante via SSH.
        Tente d'abord d'exécuter "uname -s". Si aucun résultat n'est obtenu,
        essaie d'exécuter "ver" afin de détecter Windows.
        """
        try:
            stdin, stdout, stderr = self._client.exec_command("uname -s")
            os_type = stdout.read().decode().strip()
            if os_type:
                return os_type  # Par exemple "Linux" ou "Darwin" pour macOS
        except Exception:
            pass

        try:
            # Pour Windows, la commande "ver" retourne une ligne contenant "Windows"
            stdin, stdout, stderr = self._client.exec_command("ver")
            output = stdout.read().decode().strip()
            if "Windows" in output:
                return "Windows"
        except Exception:
            pass

        return "Unknown"

    def get_system_info(self) -> Dict[str, str]:
        """
        Récupère les informations système de la machine distante via SSH.
        Retourne un dictionnaire contenant :
        - hostname, ip, mac, architecture
        - os : Nom du système d'exploitation (ex. Ubuntu, macOS, Windows 10)
        - os_version : Version du système
        - os_vendor : Éditeur du système (ex. Canonical, Apple, Microsoft)
        """
        try:
            os_type = self.detect_remote_os()
            results = {}

            if os_type == "Linux":
                # Pour Linux, on tente d'utiliser lsb_release (disponible sur les distributions basées sur Debian/Ubuntu)
                commandes = {
                    "hostname": "hostname",
                    "ip": "hostname -I | awk '{print $1}'",
                    "mac": "cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address",
                    "architecture": "uname -m",
                    # lsb_release fournit le nom et la version ; pour le vendor, on récupère l'ID du distributeur
                    "os": "lsb_release -si",
                    "os_version": "lsb_release -sr",
                    "os_vendor": "lsb_release -i | cut -f2"
                }
                for key, cmd in commandes.items():
                    stdin, stdout, stderr = self._client.exec_command(cmd)
                    results[key] = stdout.read().decode(errors='ignore').strip()

            elif os_type == "Darwin":  # macOS
                commandes = {
                    "hostname": "hostname",
                    # Pour l'adresse IP, ici on suppose que l'interface principale est 'en0'
                    "ip": "ipconfig getifaddr en0",
                    "mac": "ifconfig en0 | awk '/ether/{print $2}'",
                    "architecture": "uname -m",
                    # Pour macOS, sw_vers retourne le nom du produit et la version
                    "os": "sw_vers -productName",
                    "os_version": "sw_vers -productVersion",
                    # Le vendor est Apple
                    "os_vendor": "echo Apple"
                }
                for key, cmd in commandes.items():
                    stdin, stdout, stderr = self._client.exec_command(cmd)
                    results[key] = stdout.read().decode(errors='ignore').strip()

            elif os_type == "Windows":
                commandes = {
                    "hostname": "hostname",
                    "ip": "powershell -Command \"(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' }).IPAddress | Select-Object -First 1\"",
                    "mac": "powershell -Command \"(Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1).MacAddress\"",
                    "architecture": "powershell -Command \"(Get-CimInstance Win32_OperatingSystem).OSArchitecture\"",
                    "os": "powershell -Command \"(Get-CimInstance Win32_OperatingSystem).Caption\"",
                    "os_version": "powershell -Command \"(Get-CimInstance Win32_OperatingSystem).Version\"",
                    "os_vendor": "powershell -Command \"(Get-CimInstance Win32_OperatingSystem).Manufacturer\""
                }
                for key, cmd in commandes.items():
                    stdin, stdout, stderr = self._client.exec_command(cmd)
                    results[key] = stdout.read().decode(errors='ignore').strip()
            else:
                return {"error": f"OS non supporté : {os_type}"}

            return results

        except Exception as e:
            LogManager.error(f"Erreur lors de la récupération des infos système via SSH : {e}")
            return {"error": str(e)}

    def get_installed_apps(self) -> Any:
        """
        Récupère la liste des applications installées sur la machine distante via SSH.
        La méthode est adaptée aux trois systèmes courants :
          - Linux : essaie d'abord dpkg-query (Debian/Ubuntu), puis rpm (RedHat/CentOS)
          - Darwin (macOS) : utilise system_profiler et parse le JSON
          - Windows : utilise wmic pour récupérer la liste des applications
        """
        apps = []
        os_type = self.detect_remote_os()

        if os_type == "Linux":
            # D'abord, tenter dpkg-query (pour Debian/Ubuntu)
            try:
                cmd = "dpkg-query -W -f='${Package} ${Version} ${Maintainer}\\n'"
                stdin, stdout, stderr = self._client.exec_command(cmd)
                output = stdout.read().decode()
                if output:
                    for line in output.strip().split("\n"):
                        parts = line.strip().split(" ")
                        if len(parts) >= 3:
                            name = parts[0]
                            version = parse_version(parts[1])
                            vendor = " ".join(parts[2:])
                            apps.append({
                                "name": name,
                                "version": version,
                                "vendor": vendor,
                                "type": "application"
                            })
                    return apps
            except Exception:
                pass
            # En cas d'échec, essayer avec rpm (pour RedHat/CentOS)
            try:
                cmd = "rpm -qa --queryformat '%{NAME} %{VERSION}-%{RELEASE} %{PACKAGER}\\n'"
                stdin, stdout, stderr = self._client.exec_command(cmd)
                output = stdout.read().decode()
                for line in output.strip().split("\n"):
                    parts = line.split(" ")
                    if len(parts) >= 3:
                        name = parts[0]
                        version =  parse_version(parts[1])
                        vendor = " ".join(parts[2:])
                        apps.append({
                            "name": name,
                            "version": version,
                            "vendor": vendor,
                            "type": "application"
                        })
                if apps:
                    return apps
                else:
                    return {"error": "Aucun package détecté via dpkg ou rpm."}
            except Exception as e:
                LogManager.error(f"Erreur lors de la récupération des applications sur Linux : {e}")
                return {"error": str(e)}

        elif os_type == "Darwin":
            try:
                cmd = "system_profiler SPApplicationsDataType -json"
                stdin, stdout, stderr = self._client.exec_command(cmd)
                output = stdout.read().decode()
                data = json.loads(output)
                if "SPApplicationsDataType" in data:
                    for app in data["SPApplicationsDataType"]:
                        name = app.get("_name", "Unknown")
                        version = app.get("version", "Unknown")
                        vendor = app.get("obtained_from", "Unknown")
                        apps.append({
                            "name": name,
                            "version":  parse_version(version),
                            "vendor": vendor,
                            "type": "application"
                        })
                return apps
            except Exception as e:
                LogManager.error(f"Erreur lors de la récupération des applications sur macOS : {e}")
                return {"error": str(e)}

        elif os_type == "Windows":
            try:
                # La commande wmic retourne la liste en format "clé=valeur"
                cmd = "wmic product get Name,Version,Vendor /FORMAT:LIST"
                stdin, stdout, stderr = self._client.exec_command(cmd)
                output = stdout.read().decode("utf-8", errors="ignore")
                current_app = {}
                for line in output.strip().splitlines():
                    if line.strip() == "":
                        # Séparation entre les enregistrements
                        if current_app.get("Name"):
                            apps.append({
                                "name": current_app.get("Name", "Unknown"),
                                "version":  parse_version(current_app.get("Version", "Unknown")),
                                "vendor": current_app.get("Vendor", "Unknown"),
                                "type": "application"
                            })
                        current_app = {}
                    else:
                        if "=" in line:
                            key, value = line.split("=", 1)
                            current_app[key.strip()] = value.strip()
                # Ajout du dernier enregistrement si présent
                if current_app.get("Name"):
                    apps.append({
                        "name": current_app.get("Name", "Unknown"),
                        "version": current_app.get("Version", "Unknown"),
                        "vendor": current_app.get("Vendor", "Unknown"),
                        "type": "application"
                    })
                return apps
            except Exception as e:
                LogManager.error(f"Erreur lors de la récupération des applications sur Windows : {e}")
                return {"error": str(e)}
        else:
            return {"error": f"Système d'exploitation non supporté : {os_type}"}

    def collect_info(self, ip: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Se connecte via SSH à la machine distante, récupère les informations système et
        la liste des applications installées.
        La configuration doit contenir les clés 'username', 'password' et 'port'.
        """
        required_keys = {'username', 'password', 'port'}
        if missing := required_keys - config.keys():
            raise ValueError(f"Configuration manquante: {missing}")

        username = self.config.decrypt(config['username']) if ('username' in config.keys()) else None
        password = self.config.decrypt(config['password']) if ('password' in config.keys()) else None
        key_path = self.config.decrypt(config['key_path']) if ('key_path' in config.keys()) else None
        passphrase = self.config.decrypt(config['passphrase']) if ('passphrase' in config.keys()) else None
        port = config['port']

        try:
            # Se connecter à la machine distante via SSH
            self.connect(ip=ip, username=username, password=password,key_path=key_path,passphrase=passphrase,port=port)
            # Récupération des informations système et de la liste des applications
            system_info = self.get_system_info()
            applications = self.get_installed_apps()

            # On ajoute aussi une "application" spéciale pour l'OS
            system_info_app = {
                "name": system_info.get("os", "Unknown"),
                "version": system_info.get("os_version", "Unknown"),
                "vendor": system_info.get("os_vendor", "Unknown"),
                "type": "os"
            }

            response = {
                "system_info": system_info,
                "applications": [system_info_app] + (applications if isinstance(applications, list) else [])
            }

            return response

        except Exception as e:
            return {"error": str(e)}
        finally:
            if self._client:
                self._client.close()


if __name__ == "__main__":
    ssh = SSHProtocol()
    
    ip = ""  # Remplace par l'IP réelle
    config = {
        "username": ssh.config.encrypt(""),
        "port": 22,
        # Auth par mot de passe :
        "password": "",

        # OU Auth par clé :
        "key_path": ssh.config.encrypt(""),
        "passphrase": ssh.config.encrypt("")  # ou None si pas de mot de passe
    }

    result = ssh.collect_info(ip, config)
    print(json.dumps(result, indent=2, ensure_ascii=False))