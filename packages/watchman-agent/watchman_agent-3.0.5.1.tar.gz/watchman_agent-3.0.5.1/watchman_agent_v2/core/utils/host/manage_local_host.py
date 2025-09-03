import platform
import csv
import json
import subprocess
import socket
import uuid
import sys
from typing import List, Dict, Optional, Tuple
import psutil

from watchman_agent_v2.core.utils.log_manager import LogManager

class ManageLocalhost:
    def __init__(self):
        self.os_name, self.os_version = self._get_os_info()
        self.architecture = platform.machine()
        self.hostname = socket.gethostname()
        self.ip_address = self._get_ip_address()
        self.mac_address = self._get_mac_address()
        self.applications = self.get_installed_apps()
        self.virtualization_info = self._detect_virtualization()
        
    def _get_os_info(self) -> Tuple[str, str]:
        """Récupère les informations détaillées du système d'exploitation"""
        system = platform.system()
        if system == 'Darwin':
            version = subprocess.getoutput('sw_vers -productVersion')
            return 'macOS', version
        elif system == 'Linux':
            try:
                with open('/etc/os-release') as f:
                    content = f.read().splitlines()
                    os_info = {k:v.strip('"') for k,v in (line.split('=',1) for line in content if '=' in line)}
                    return os_info.get('PRETTY_NAME', 'Linux'), os_info.get('VERSION_ID', platform.release())
            except:
                return 'Linux', platform.release()
        elif system == 'Windows':
            return 'Windows', platform.win32_ver()[0]
        return 'Unknown', ''

    def _get_ip_address(self) -> str:
        """Récupère l'adresse IP principale"""
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return '127.0.0.1'

    def _get_mac_address(self) -> str:
        """Récupère l'adresse MAC principale"""
        try:
            mac_num = hex(uuid.getnode()).replace('0x', '').upper()
            mac = '-'.join(mac_num[i:i+2] for i in range(0,11,2))
            return mac
        except:
            return '00:00:00:00:00:00'

    def _detect_virtualization(self) -> Dict:
        """Détecte l'environnement de virtualisation"""
        virt_info = {
            'is_virtual': False,
            'host_machine': {}
        }

        try:
            if platform.system() == 'Linux':
                virt = subprocess.check_output(['systemd-detect-virt'], text=True).strip()
                if virt != 'none':
                    virt_info['is_virtual'] = True
                    virt_info['host_machine']['type'] = virt
            elif platform.system() == 'Windows':
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\\') as key:
                    try:
                        virt_type = winreg.QueryValueEx(key, 'SystemManufacturer')[0]
                        if any(x in virt_type for x in ['VMware', 'VirtualBox', 'QEMU']):
                            virt_info['is_virtual'] = True
                            virt_info['host_machine']['type'] = virt_type
                    except:
                        pass
            elif platform.system() == 'Darwin':
                output = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], text=True).strip()
                if 'Virtual' in output:
                    virt_info['is_virtual'] = True
                    virt_info['host_machine']['type'] = output
        except:
            pass

        return virt_info

    def _get_windows_apps(self) -> List[Dict]:
        """Récupère les applications Windows avec les nouvelles métadonnées"""
        import winreg

        apps = []
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'),
            (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Uninstall')
        ]

        for root, key_path in registry_keys:
            try:
                with winreg.OpenKey(root, key_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                app_data = {
                                    'name': winreg.QueryValueEx(subkey, 'DisplayName')[0],
                                    'version': winreg.QueryValueEx(subkey, 'DisplayVersion')[0],
                                    'vendor': winreg.QueryValueEx(subkey, 'Publisher')[0],
                                    'type': 'application'
                                }
                                if app_data['name']:
                                    apps.append(app_data)
                            except OSError:
                                continue
            except OSError:
                continue

        return apps

    def _get_linux_apps(self) -> List[Dict]:
        """Récupère les applications Linux avec les nouvelles métadonnées"""
        apps = []

        # Détection des paquets Debian/Ubuntu
        try:
            output = subprocess.check_output(
                ['dpkg-query', '-W', '-f=${Package};${Version};${Maintainer}\n'],
                text=True
            )
            for line in output.split('\n'):
                if line.strip():
                    name, version, vendor = line.strip().split(';', 2)
                    apps.append({
                        'name': name,
                        'version': version,
                        'vendor': vendor,
                        'type': 'application'
                    })
            return apps
        except:
            pass

        # Détection des paquets RPM
        try:
            output = subprocess.check_output(
                ['rpm', '-qa', '--queryformat', '%{NAME};%{VERSION};%{VENDOR}\n'],
                text=True
            )
            for line in output.split('\n'):
                if line.strip():
                    name, version, vendor = line.strip().split(';', 2)
                    apps.append({
                        'name': name,
                        'version': version,
                        'vendor': vendor,
                        'type': 'application'
                    })
            return apps
        except:
            pass

        return apps

    def _get_macos_apps(self) -> List[Dict]:
        """Récupère les applications macOS avec les nouvelles métadonnées"""
        apps = []
        try:
            output = subprocess.check_output(['system_profiler', 'SPApplicationsDataType', '-xml'], text=True)
            import plistlib
            plist = plistlib.loads(output.encode('utf-8'))
            for app in plist[0]['_items']:
                apps.append({
                    'name': app.get('_name', ''),
                    'version': app.get('version', ''),
                    'vendor': app.get('obtained_from', ''),
                    'type': 'application'
                })
        except Exception as e:
            LogManager.error(f"Erreur applications macOS: {e}", file=sys.stderr)
        
        return apps

    def get_installed_apps(self) -> List[Dict]:
        """Récupère les applications avec métadonnées étendues"""
        apps = []

        # Ajout de l'OS comme première application
        apps.append({
            'name': self.os_name,
            'version': self.os_version,
            'vendor': self.os_name,
            'type': 'os'
        })

        # Récupération des autres applications
        if platform.system() == 'Windows':
            apps += self._get_windows_apps()
        elif platform.system() == 'Darwin':
            apps += self._get_macos_apps()
        else:
            apps += self._get_linux_apps()

        return apps

    def export_to_csv(self, filename: str = 'applications.csv'):
        """Exporte les données au format CSV professionnel"""
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

                for app in self.applications:
                    row = [
                        self.ip_address,
                        self.mac_address,
                        self.architecture,
                        self.hostname,
                        f"{self.os_name} {self.os_version}",
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
            
            LogManager.success(f"CSV généré avec succès : {filename}")
        except Exception as e:
            LogManager.error(f"Erreur CSV: {str(e)}", file=sys.stderr)

    def export_to_json(self, filename: str = 'system_info.json'):
        """Exporte les données au format JSON professionnel"""
        data = {'ip': self.ip_address,
            'mac': self.mac_address,
            'architecture': self.architecture,
            'os': f"{self.os_name} {self.os_version}",
            'hostname': self.hostname,
            'host_machine': "",
            'host_machine_hostname': "",
            'host_machine_os': "",
            'host_machine_architecture': "",
            'host_machine_mac': "",
            'applications': [
                {
                    'name': app['name'],
                    'version': app['version'],
                    'vendor': app['vendor'],
                    'type': app['type']
                }
                for app in self.applications
            ]}
        
        

        # Ajout des informations de virtualisation si nécessaire
        if self.virtualization_info['is_virtual']:
            data.update({
                'host_machine': self.virtualization_info['host_machine'].get('type', ''),
                'host_machine_hostname': '',
                'host_machine_os': '',
                'host_machine_architecture': '',
                'host_machine_mac': ''
            })
            
        data_array={
            'assets':[
                data
            ]
        }

        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data_array, jsonfile, indent=4, ensure_ascii=False)
            LogManager.success(f"JSON généré avec succès : {filename}")
        except Exception as e:
            LogManager.error(f"Erreur JSON: {str(e)}", file=sys.stderr)

# how to use it 
if __name__ == '__main__':
    manager = ManageLocalhost()
    manager.export_to_csv()
    manager.export_to_json()
