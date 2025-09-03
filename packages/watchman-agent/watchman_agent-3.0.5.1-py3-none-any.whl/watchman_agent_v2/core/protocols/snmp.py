import re
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime

import getmac
from puresnmp import Client, V2C, PyWrapper

from watchman_agent_v2.core.utils.extract_snmp_info import ExtractSnmpInfo
from watchman_agent_v2.core.utils.functions import parse_version


logger = logging.getLogger(__name__)

class SNMPHandler():
    """
    Handler SNMP pour la collecte d'informations système et logicielles.
    Utilise puresnmp pour interroger un hôte via SNMP.
    """
    
    # Définition des OIDs standard et étendu
    OIDS = {
        "sys_descr": "1.3.6.1.2.1.1.1.0",                   # Description système
        "sys_name": "1.3.6.1.2.1.1.5.0",                    # Nom d'hôte
        "if_phys_address": "1.3.6.1.2.1.2.2.1.6",           # Adresse MAC
        "hr_sw_installed": "1.3.6.1.2.1.25.6.3.1.2",        # Logiciels installés (standard)
        "hr_sw_installed_ext": "1.3.6.1.4.1.8072.1.3.2"     # Logiciels installés étendu (Linux)
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le gestionnaire SNMP avec la configuration donnée.
        """
        super().__init__()
        self.config = config or {}
        self.community = self.config.get("community", "public")
        self.port = self.config.get("port", 161)
        self.timeout = self.config.get("timeout", 3)
        self.version = self.config.get("version", "2c")
    
    def collect_info(self, ip: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
         return asyncio.run(self.get_info(ip,config))
    
    async def get_info(self, ip: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collecte et retourne les informations SNMP complètes depuis l'hôte cible.
        Ajoute également le timestamp d'accès.
        """
        if config:
            self.config = config
            self.community = config.get("community", "public")
            self.port = config.get("port", 161)
            self.timeout = config.get("timeout", 3)
            self.version = config.get("version", "2c")
            self.ip=ip
        
        # Initialisation du client SNMP pour l'IP cible
        self.client = PyWrapper(
            Client(ip=ip, credentials=V2C(self.community), port=self.port)
        )

        result: Dict[str, Any] = {
            'system_info': {
                "ip": ip,
                "mac": "",
                "architecture": "",
                "os": "",
                "hostname": "",
            },
            "applications": [],
            "accessed_at": ""  # Timestamp d'accès
        }
        
        try:
            # Récupération des informations de base
            basic_info = await self._get_basic_info()
            self.basic_info=basic_info
            result['system_info'].update(basic_info)
            
            # Récupération des applications installées
            result["applications"] = await self._get_installed_software()
            
            # Récupération de l'adresse MAC et mise à jour dans system_info
            mac = await self._get_mac_address()
            result['system_info']["mac"] = mac
            
            # Ajout du timestamp d'accès
            result["accessed_at"] = datetime.now().isoformat()
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout SNMP sur {ip}")
        except Exception as e:
            logger.error(f"Erreur SNMP sur {ip}: {str(e)}")
            
        return result
    
    async def _get_basic_info(self) -> Dict[str, str]:
        """
        Récupère les informations système de base.
        Retourne un dictionnaire contenant l'OS, l'architecture et le hostname.
        """
        info: Dict[str, str] = {}
        try:
            # Récupération de la description système
            sys_descr = await self.client.get(self.OIDS["sys_descr"])
            # Décodage si nécessaire
            if isinstance(sys_descr, bytes):
                sys_descr = sys_descr.decode('utf-8', errors='replace')
            print(f'sys_info {sys_descr} ')
            lower_value=sys_descr.lower()
            if "windows" in lower_value:
                info = ExtractSnmpInfo.extract_windows_host_info(sys_descr)
                info["os"] = info.get("os_name")
                info["kernel_version"] = info.get("kernel_version")
                info["architecture"] = info.get("arch")
                info["build"] = info.get("build")
            elif "darwin" in lower_value:
                partitioned = sys_descr.split()
                if partitioned:
                    info["os"] = partitioned[0]
                    info["kernel_version"] = partitioned[2]
                    info["architecture"] = partitioned[-1]
            elif "linux" in lower_value:
                partitioned = sys_descr.split()
                if partitioned:
                    info["os"] = partitioned[0]
                    info["kernel_version"] = partitioned[2]
                    info["architecture"] = partitioned[-1]
            else :
                info["os"] = self._parse_os(sys_descr)
                info["architecture"] = self._parse_architecture(sys_descr)
        
            # Récupération du nom d'hôte
            hostname = await self.client.get(self.OIDS["sys_name"])
            if isinstance(hostname, bytes):
                hostname = hostname.decode('utf-8', errors='replace')
            info["hostname"] = hostname
            info["mac"] = getmac.get_mac_address(ip=self.ip)
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des informations de base: {str(e)}")
        return info
    
    async def _get_installed_software(self) -> List[Dict[str, str]]:
        """
        Récupère la liste des logiciels installés.
        Tente d'abord avec l'OID étendu pour obtenir nom et version directement,
        sinon retombe sur l'OID standard et tente de parser la version depuis le nom.
        Chaque entrée est un dictionnaire avec le nom, la version et le fournisseur.
        """
        applications: List[Dict[str, str]] = []
        # Première tentative avec l'OID étendu
        try:
            ext_entries = []
            async for entry in self.client.walk(self.OIDS["hr_sw_installed_ext"]):
                ext_entries.append(entry)
            if ext_entries:
                # Exemple de chaîne : b'xkb-data\t2.33-1'
                for entry in ext_entries:
                    if isinstance(entry.value, bytes):
                        decoded = entry.value.decode('utf-8', errors='replace')
                        parts = decoded.split('\t')
                        if len(parts) >= 2:
                            app_info = {
                                "name": parts[0].strip(),
                                "version": parts[1].strip(),
                                "vendor": "*",  # Vendor non fourni par cet OID
                                "type": "application"
                            }
                            applications.append(app_info)
                if applications:
                    return applications
        except Exception as e:
            logger.error(f"Erreur lors de la collecte avec OID étendu: {str(e)}")
        
        # Fallback sur l'OID standard
        try:
            async for entry in self.client.walk(self.OIDS["hr_sw_installed"]):
                # Selon la version de puresnmp, la structure peut varier.
                raw_value = getattr(entry, "raw_value", {}) or getattr(entry, "value", {})
                if type(raw_value) == int:
                    continue
                name = raw_value
                if isinstance(name, bytes):
                    name = name.decode('utf-8', errors='replace')
                
                extract_fnc =  ExtractSnmpInfo.extract_info_windows
                if self.basic_info['os'].lower() == "linux":
                    extract_fnc = ExtractSnmpInfo.extract_info_linux
                elif self.basic_info['os'].lower() == "mac" or self.basic_info['os'].lower() == "darwin":
                    extract_fnc = ExtractSnmpInfo.extract_info_macos
                    
                host_info=extract_fnc(name)
                version=host_info['version']
                name=host_info['name']
                vendor="*"
                
                app_info = {
                    "name": name,
                    "version": parse_version(version),
                    "vendor": vendor,
                    "type": "application"
                }
                if app_info["name"]:
                    applications.append(app_info)
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des logiciels installés avec l'OID standard: {str(e)}")
        return applications
    
    async def _get_mac_address(self) -> str:
        """
        Parcourt les interfaces et retourne la première adresse MAC non-nulle.
        """
        mac_address: str = ""
        try:
            async for entry in self.client.walk(self.OIDS["if_phys_address"]):
                mac_bytes = entry.value
                if mac_bytes and isinstance(mac_bytes, bytes):
                    mac = ":".join(f"{b:02x}" for b in mac_bytes)
                    if mac != "00:00:00:00:00:00":
                        return mac
                elif mac_bytes and isinstance(mac_bytes, str) and mac_bytes.strip():
                    return mac_bytes.strip()
        except Exception as e:
            logger.error(f"Erreur lors de la collecte de l'adresse MAC: {str(e)}")
        return mac_address
    
    @staticmethod
    def _parse_os(sys_descr: str) -> str:
        """
        Extrait le nom de l'OS depuis la description système.
        """
        patterns = [
            r"Linux\s+([^\s]+)",
            r"Windows\s+([^\s]+)",
            r"Darwin/([^\s]+)",  # macOS
            r"([A-Za-z]+)\s+UNIX"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sys_descr)
            if match:
                return match.group(1)
        return sys_descr.split()[0] if sys_descr else ""
    
    @staticmethod
    def _parse_architecture(sys_descr: str) -> str:
        """
        Extrait l'architecture depuis la description système.
        """
        patterns = {
            r"x86_64": "x86_64",
            r"amd64": "x86_64",
            r"i[3456]86": "x86",
            r"armv[^\s]+": "ARM",
            r"aarch64": "ARM64"
        }
        
        for pattern, arch in patterns.items():
            if re.search(pattern, sys_descr, re.IGNORECASE):
                return arch
        return "unknown"



# Exemple d'utilisation asynchrone
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = {
        "community": "public",
        "version": "2c",
        "timeout": 5
    }
    
    var_binds = {
        'sys_hostname_bind': '1.3.6.1.2.1.1.5.0',
        'sys_descr_bind': '1.3.6.1.2.1.1.1.0',
    }
    
    def main():
        handler = SNMPHandler()
        info =  handler.collect_info("10.10.15.100",config)
        return info
    
    print(main())
    
    # async def example():
    #     client = PyWrapper(Client("localhost", V2C("public")))
    #     output = []
        
        
    #     async for item in client.walk("1.3.6.1.2.1.25.6.3.1.2"):
    #         output.append(item.value)
    #     return output

    # print(asyncio.run(example()))
