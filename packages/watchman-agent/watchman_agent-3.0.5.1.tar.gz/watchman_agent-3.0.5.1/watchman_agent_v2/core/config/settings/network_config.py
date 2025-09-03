import ipaddress
import re

from watchman_agent_v2.core.config.config_manager import ConfigManager
import csv


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except ValueError:
        return False


def extract_ips_from_file(filepath, ip_column_name=None):
    ips = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            f.seek(0)

            if ',' in first_line:
                # Fichier CSV
                reader = csv.DictReader(f)
                if ip_column_name and ip_column_name not in reader.fieldnames:
                    raise ValueError(f"❌ Colonne '{ip_column_name}' introuvable dans le fichier CSV")
                for row in reader:
                    if ip_column_name:
                        ip = row.get(ip_column_name)
                        if ip and is_valid_ip(ip):
                            ips.append(ip.strip())
                    else:
                        # Si pas de colonne spécifiée, on cherche la première IP valide dans la ligne
                        for val in row.values():
                            if is_valid_ip(val):
                                ips.append(val.strip())
                                break
            else:
                # Fichier texte simple (ligne par ligne)
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if ',' in line:
                        parts = line.split(',')
                        for part in parts:
                            part = part.strip()
                            if is_valid_ip(part):
                                ips.append(part)
                    else:
                        if is_valid_ip(line):
                            ips.append(line)
    except Exception as e:
        raise RuntimeError(f"Erreur de lecture du fichier {filepath}: {e}")

    return ips


class NetworkConfig:
    def __init__(self):
        self.config_manager = ConfigManager()
        self._init_section()

    def _init_section(self) -> None:
        if 'network' not in self.config_manager.config:
            config = self.config_manager.config
            config['network'] = {}
            self.config_manager.save_config(config)

    def set_network(self, mode=None, cidr=None, start_ip=None, end_ip=None, network_address=None, inclusions=None,
                    exclusions=None, protocols=None):
        config = self.config_manager.config
        if mode:
            config["network"]["mode"] = mode
        if cidr:
            config["network"]["cidr"] = cidr
        if start_ip:
            config["network"]["start_address"] = start_ip
        if end_ip:
            config["network"]["end_address"] = end_ip
        if network_address:
            config["network"]["network_address"] = network_address
        if inclusions and len(inclusions) > 0:
            config["network"]["inclusions"] = inclusions
        if exclusions:
            config["network"]["exclusions"] = exclusions.split(",")
        if protocols:
            config["network"]["protocols"] = protocols.split(",")

        self.config_manager.save_config(config)

    def get_network(self):
        return self.config_manager.get("network", {})

# class NetworkConfig:
#     def __init__(self):
#         self.config_manager = ConfigManager()
#         self._init_section()
#
#     def _init_section(self) -> None:
#         """Initialise la section API si elle n'existe pas"""
#         if 'network' not in self.config_manager.config:
#             config = self.config_manager.config
#             config['network'] = {}
#             self.config_manager.save_config(config)
#
#     def set_network(self, mode=None, cidr=None, start_ip=None, end_ip=None, network_adress=None, inclusions=None,
#                     exclusions=None, protocols=None):
#         """Modifie la configuration réseau"""
#         config = self.config_manager.config
#         if mode:
#             config["network"]["mode"] = mode
#         if cidr:
#             config["network"]["cidr"] = cidr
#         if start_ip:
#             config["network"]["start_address"] = start_ip
#         if end_ip:
#             config["network"]["end_address"] = end_ip
#         if network_adress:
#             config["network"]["network_address"] = network_adress
#         if inclusions:
#             config["network"]["inclusions"] = inclusions.split(",")
#         if exclusions:
#             config["network"]["exclusions"] = exclusions.split(",")
#         if protocols:
#             config["network"]["protocols"] = protocols.split(",")
#
#         self.config_manager.save_config(config)
#
#     def get_network(self):
#         """Récupère la configuration réseau"""
#         return self.config_manager.get("network", {})
