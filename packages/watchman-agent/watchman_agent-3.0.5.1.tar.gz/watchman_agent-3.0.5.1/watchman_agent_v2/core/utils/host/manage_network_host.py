from datetime import datetime
import platform
import csv
import json
import subprocess
import socket
import uuid
import sys
from typing import List, Dict, Optional, Tuple
import psutil

from watchman_agent_v2.core.protocols.http import HttpProtocol
from watchman_agent_v2.core.protocols.snmp import SNMPHandler
from watchman_agent_v2.core.protocols.ssh import SSHProtocol
from watchman_agent_v2.core.protocols.wmi_protocol import WMIProtocol
from watchman_agent_v2.core.utils.host.manage_host import ManageHost
from watchman_agent_v2.core.utils.network.network_utils import NetworkUtils
from watchman_agent_v2.core.utils.log_manager import LogManager

class ManageNetworkHost(ManageHost):
    def __init__(self):
        super().__init__()
        network_config = self.config.config.get('network', {})
        self.mode = network_config.get('mode', 'cidr')  # valeur par défaut : 'cidr'
        self.cidr = network_config.get('cidr', '')
        self.start_address = network_config.get('start_address', '')
        self.end_address = network_config.get('end_address', '')
        self.network_address = network_config.get('network_address', '')
        self.inclusions = network_config.get('inclusions', [])
        self.exclusions = network_config.get('exclusions', [])
        self.protocols = network_config.get('protocols', {})

        self.protocol_handlers={
                    'http': HttpProtocol,
                    'snmp': SNMPHandler,
                    'ssh':SSHProtocol,
                    'wmi': WMIProtocol
                        }
        self.logger=LogManager        
        self.network_manager=NetworkUtils()
        
        self.addresses=self.get_address()
        
    def get_address(self):
        """
        Génère les adresses IP selon le mode configuré (cidr, iplist ou plage),
        en appliquant les inclusions/exclusions et les validations.
        """
        addresses = []

        # Génération de base selon le mode
        if self.mode == "cidr":
            # Mode CIDR (sous-réseau)
            prefix = NetworkUtils.mask_to_prefix(self.cidr)
            print(f'prefix {prefix} ' )
            addresses = NetworkUtils.generate_from_network_mask(
                self.network_address, 
                prefix
            )
        elif self.mode == "plage":
            # Mode plage IP
            addresses = NetworkUtils.generate_from_range(
                self.start_address, 
                self.end_address
            )
        elif self.mode == "ip_list":
            # Mode liste manuelle
            addresses = self.inclusions
        else:
            raise ValueError(f"Mode réseau inconnu: {self.mode}")

        # Filtrage des adresses invalides
        valid_addresses = [ip for ip in addresses if NetworkUtils.is_valid_ip(ip)]

        # Application des exclusions
        filtered_addresses = [
            ip for ip in valid_addresses 
            if ip not in self.exclusions
        ]

        # Dédoublonnage (optionnel)
        seen = set()
        return [ip for ip in filtered_addresses if not (ip in seen or seen.add(ip))]
    
    def deep_merge(self, base: dict, update: dict) -> dict:
        """
        Fusion récursive de dictionnaires.
        Combine les configurations globales et les surcharges intelligemment.
        """
        merged = base
        for key, val in update.items():
            if isinstance(val, dict) and key in merged:
                merged[key] = self.deep_merge(merged.get(key, {}), val)
            else:
                merged[key] = val
        return merged

    def get_protocols(self, address: str) -> dict:
        """
        Retourne la configuration complète des protocoles pour une adresse,
        en conservant TOUS les protocoles globaux et leurs paramètres,
        même si non mentionnés dans les surcharges.
        """
        # Configuration globale de base
        global_config = self.protocols.get('global', {})
        
        # Surcharges spécifiques à l'adresse (si existantes)
        address_overrides = self.protocols.get('overrides', {}).get(address, {})
        
        # Fusion récursive
        return self.deep_merge(global_config, address_overrides)

    def collect_all_info(self) -> dict:
        """
        Collecte les informations de toutes les adresses via les protocoles configurés
        Retourne un dictionnaire structuré avec les résultats
        """
        results = {
            'metadata': {
                'start_time': datetime.utcnow().isoformat(),
                'total_addresses': 0,
                'success_count': 0,
                'error_count': 0
            },
            'devices': {}
        }
        
        self.logger.info(f"Commence la recuperation des données .....")
        

        addresses = self.get_address()
        results['metadata']['total_addresses'] = len(addresses)

        for address in addresses:
            self.logger.info(f"Commence la recuperation des données de {address} ....")
            device_results = {}
            protocols_config = self.get_protocols(address)
            self.logger.info(f"Les protocoles de  {address} sont: {protocols_config.keys()} ")
            
            for protocol_name, protocol_config in protocols_config.items():
                if not protocol_config.get('enabled', False):
                    continue

                try:
                    handler = self._get_protocol_handler(protocol_name, protocol_config)
                    device_results = handler.collect_info(address, protocol_config)
                    results['metadata']['success_count'] += 1
                    self.logger.success(f"Informations de {address} recuperées avec succès par le protocol {protocol_name}")
                    temp_system_info=device_results.get('system_info',None)
                    temp_applications=device_results.get('applications',None)
                    if not temp_system_info or not temp_applications:
                        self.logger.error(f"Les informations de {address} sont incomplètes pour le protocol {protocol_name}")
                        continue
                    break
                except Exception as e:
                    self.logger.error(f"Error with {protocol_name} on {address}: {str(e)}")
                    results['metadata']['error_count'] += 1
                    
            results['devices'][address] = device_results

        results['metadata']['end_time'] = datetime.utcnow().isoformat()
        self.results=results
        return results

    def _get_protocol_handler(self, protocol_name: str, config: dict):
        """
        Factory pour obtenir une instance du handler de protocole
        """
        handler_class = self.protocol_handlers.get(protocol_name,{})
        if not handler_class:
            raise ValueError(f"Protocol handler not found for {protocol_name}")
        
        return handler_class()
    
    
    def export_to_csv(self, filename: str = 'applications.csv'):
        """Exporte les données au format CSV professionnel"""
        if not self.results:
            self.logger.error('Veuiller recuperer d \'abord les informations ' )
            return 
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                
                # Entête selon les spécifications
                headers = [
                    'ip', 'mac', 'architecture', 'hostname', 'os',
                    'stack_name', 'stack_version', 'stack_type', 'stack_vendor',
                    'host_machine', 'host_machine_architecture',
                    'host_machine_os', 'host_machine_hostname', 'host_machine_mac'
                ]
                writer.writerow(headers)
                
                for address in self.addresses:
                    system_info=self.results['devices'][address]['system_info']
                    applications=self.results['devices'][address]['applications']

                    for app in applications:
                        row = [
                            system_info['ip'],
                            system_info['mac'],
                            system_info['architecture'],
                            system_info['hostname'],
                            system_info['os'],
                            app['name'],
                            app['version'],
                            app['type'],
                            app['vendor'],
                            self.virtualization_info['host_machine'].get('type', '') if self.virtualization_info['is_virtual'] else '',
                            '',  # host_machine_architecture
                            '',  # host_machine_os
                            '',  # host_machine_hostname
                            ''   # host_machine_mac
                        ]
                        writer.writerow(row)
            
            print(f"CSV généré avec succès : {filename}")
        except Exception as e:
            print(f"Erreur CSV: {str(e)}", file=sys.stderr)

    def export_to_json(self, filename: str = 'system_info.json'):
        if not self.results['devices']:
            self.logger.error('Veuiller recuperer d \'abord les informations ' )
            return 
        """Exporte les données au format JSON professionnel"""
        data_array={
                    'assets':[
                        
                    ]
                }
        for address in self.addresses:
            system_info=self.results['devices'][address].get('system_info',None)
            applications=self.results['devices'][address].get('applications',None)
            if not system_info or not applications:
                self.logger.error(f"Les informations de {address} sont incomplètes.")
                continue
            data = {'ip': address,
                'mac': system_info['mac'],
                'architecture': system_info['architecture'],
                'os': system_info['os'],
                'hostname': system_info['hostname'],
                'host_machine':system_info.get('host_machine','')  ,
                'host_machine_hostname': system_info.get('host_machine_hostname',''),
                'host_machine_os': system_info.get('host_machine_os',''),
                'host_machine_architecture': system_info.get('host_machine_architecture',''),
                'host_machine_mac': system_info.get('host_machine_mac',''),
                'applications': [
                    {
                        'name': app['name'],
                        'version': app['version'],
                        'vendor': app['vendor'],
                        'type': app['type']
                    }
                    for app in applications
                ]}
            
            data_array['assets'].append(data)
            
        if data_array['assets'] == []:
            self.logger.error('Aucune donnée à exporter.')
            raise ValueError('Aucune donnée à exporter.')

        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data_array, jsonfile, indent=4, ensure_ascii=False)
            print(f"JSON généré avec succès : {filename}")
        except Exception as e:
            print(f"Erreur JSON: {str(e)}", file=sys.stderr)
        
     
        
        
        