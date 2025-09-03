
import binascii
import re


class ExtractSnmpInfo:

    @staticmethod 
    def extract_info_linux(package_string):
        # Original regular expression pattern
        original_pattern = r'^(.*?)_([^_]+)_([^\s]+)$'

        # Additional pattern to handle strings like "whiptail-0.52.20-1ubuntu1"
        additional_pattern = r'^([^-\s]+)-([\d.]+)-(\S+)$'

        # Pattern for strings like "ncurses-6.1-10.20180224.el8"
        new_pattern = r'^([^-\s]+)-([\d.]+)-([\d.]+)\.([^\s]+)$'

        # Pattern for strings like "ncurses-6.1-10.20180224.el8"
        second_pattern = r'(.*)-(.*)-(.*).(.*)'
        third_pattern = r'\d+(\.\d+)*'

        # Try the original pattern first
        match = re.match(original_pattern, package_string)

        if match:
            name = match.group(1)
            version = match.group(2)
            architecture = match.group(3)
            return {"name": name, "version": version, "arch": architecture}
        else:
            # If the original pattern didn't match, try the additional pattern
            match = re.match(additional_pattern, package_string)

            if match:
                name = match.group(1)
                version = match.group(2)
                architecture = match.group(3)
                return {"name": name, "version": version, "arch": architecture}
            else:
                # If the additional pattern didn't match, try the new pattern
                match = re.match(new_pattern, package_string)

                if match:
                    name = match.group(1)
                    version = match.group(2)
                    release = match.group(3)
                    architecture = match.group(4)
                    return {"name": name, "version": version, "arch": architecture}
                else:
                    # If the new pattern didn't match, try the second pattern
                    match = re.match(second_pattern, package_string)

                    if match:
                        name = match.group(1)
                        version = match.group(2)
                        release = match.group(3)
                        architecture = match.group(4)
                        return {"name": name, "version": version, "arch": architecture}
                    else:
                        return None
    def extract_info_windows(package_string):
        try:
            # Essayer de décoder la chaîne hexadécimale
            decoded_string = binascii.unhexlify(package_string[2:]).decode('latin-1')
        except (binascii.Error, ValueError):
            # Si ce n'est pas une chaîne hexadécimale, utiliser directement la valeur
            decoded_string = package_string

        # Regex améliorée pour capturer des formats plus variés
        pattern = r'^(.*?)\s*-\s*([\d\w\.\-]+)\s*(?:\((.*?)\))?$'
        match = re.match(pattern, decoded_string)

        if match:
            name = match.group(1).strip()
            version = match.group(2).strip()
            architecture = match.group(3).strip() if match.group(3) else None
            return {"name": name, "version": version, "architecture": architecture}

        # Vérifier si la chaîne se termine par un numéro (potentielle version)
        version_match = re.search(r'([\d]+(\.\d+)+)$', decoded_string)
        if version_match:
            name = decoded_string[:version_match.start()].strip()
            version = version_match.group(1)
            return {"name": name, "version": version, "architecture": None}

        # Retourner au cas où aucun pattern ne correspond
        return {"name": decoded_string.strip(), "version": None, "architecture": None}
    @staticmethod
    def extract_windows_host_info(input_str):
        # Expression régulière pour extraire l'architecture matérielle (premier mot après "Hardware:")
        hardware_architecture_pattern = r'Hardware:\s(\S+)'

        # Expression régulière pour extraire les informations logicielles
        software_pattern = r'Software:\s(.*?)\sVersion\s(\d+\.\d+).*\(Build\s(\d+)\s.*\)$'

        # Rechercher les correspondances dans la chaîne d'entrée
        hardware_architecture_match = re.search(hardware_architecture_pattern, input_str, re.IGNORECASE)
        software_match = re.search(software_pattern, input_str)

        # Extraire l'architecture matérielle
        hardware_architecture = hardware_architecture_match.group(1).strip() if hardware_architecture_match else None

        # Extraire les informations logicielles
        software_name = software_match.group(1).strip() if software_match else None
        software_version = software_match.group(2).strip() if software_match else None
        software_build = software_match.group(3).strip() if software_match else None

        return {
            "arch": hardware_architecture,
            "os_name": software_name,
            "kernel_version": software_version,
            "build": software_build
        }

    @staticmethod
    def extract_info_macos(package_string):
        # Utilisation d'une expression régulière pour extraire le nom et la version sous macOS
        pattern = r'^(.*?)\s+(\S+)\s*$'
        match = re.match(pattern, package_string)

        if match:
            name = match.group(1)
            version = match.group(2)
            if '(null)' in version:
                version = None
            if '(null)' in name:
                name = None
            return {"name": name, "version": version, "arch": None}
        else:
            return None
