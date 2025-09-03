import ipaddress

class NetworkUtils:
    
    @staticmethod
    def generate_from_range(start_ip: str, end_ip: str) -> list:
        """
        Génère toutes les adresses IPv4 dans une plage donnée.
        
        Args:
            start_ip (str): Adresse de début (ex. '192.168.1.1')
            end_ip (str): Adresse de fin (ex. '192.168.1.5')
        
        Returns:
            list: Liste des adresses IPv4 entre start_ip et end_ip inclus.
        """
        start = NetworkUtils.ip_to_int(start_ip)
        end = NetworkUtils.ip_to_int(end_ip)
        if start > end:
            start, end = end, start
        return [NetworkUtils.int_to_ip(ip) for ip in range(start, end + 1)]
    
    @staticmethod
    def generate_from_network_mask(network_address: str, subnet_mask: str | int) -> list:
        """
        Génère toutes les adresses IPv4 d'un sous-réseau.
        
        Args:
            network_address (str): Adresse réseau (ex. '192.168.1.0')
            subnet_mask (str | int): Masque de sous-réseau (ex. '255.255.255.0' ou 24)
        
        Returns:
            list: Liste des adresses IPv4 du sous-réseau.
        """
        prefix = NetworkUtils.mask_to_prefix(subnet_mask)
        network = ipaddress.IPv4Network(f"{network_address}/{prefix}", strict=False)
        return [str(ip) for ip in network]
    
    @staticmethod
    def mask_to_prefix(subnet_mask: str | int) -> int:
        """
        Convertit un masque de sous-réseau en notation CIDR (ex. '255.255.255.0' → 24).
        
        Args:
            subnet_mask (str | int): Masque sous forme de chaîne ou de préfixe entier.
        
        Returns:
            int: Préfixe CIDR (entre 0 et 32).
        
        Raises:
            ValueError: Si le masque est invalide.
        """
        if isinstance(subnet_mask, int):
            if 0 <= subnet_mask <= 32:
                return subnet_mask
            raise ValueError("Le préfixe doit être entre 0 et 32.")
        
        if isinstance(subnet_mask, str):
            if subnet_mask.startswith('/'):
                subnet_mask = subnet_mask[1:]
            
            try:
                # Traitement des masques en notation CIDR ou décimale
                network = ipaddress.IPv4Network(f"0.0.0.0/{subnet_mask}", strict=False)
                return network.prefixlen
            except ValueError:
                raise ValueError("Masque de sous-réseau invalide.")
        
        raise TypeError("Le masque doit être une chaîne ou un entier.")
    
    @staticmethod
    def ip_to_int(ip_str: str) -> int:
        """
        Convertit une adresse IPv4 en entier.
        
        Args:
            ip_str (str): Adresse IPv4 (ex. '192.168.1.1')
        
        Returns:
            int: Représentation entière de l'adresse.
        """
        octets = list(map(int, ip_str.split('.')))
        if len(octets) != 4 or any(octet < 0 or octet > 255 for octet in octets):
            raise ValueError("Adresse IPv4 invalide.")
        return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]
    
    @staticmethod
    def int_to_ip(ip_int: int) -> str:
        """
        Convertit un entier en adresse IPv4.
        
        Args:
            ip_int (int): Entier représentant l'adresse IPv4.
        
        Returns:
            str: Adresse IPv4 formatée.
        """
        if ip_int < 0 or ip_int > 0xFFFFFFFF:
            raise ValueError("Entier hors plage IPv4.")
        return '.'.join(map(str, [
            (ip_int >> 24) & 0xFF,
            (ip_int >> 16) & 0xFF,
            (ip_int >> 8) & 0xFF,
            ip_int & 0xFF
        ]))
    
    @staticmethod
    def is_valid_ip(ip_str: str) -> bool:
        """
        Vérifie si une chaîne est une adresse IPv4 valide.
        
        Args:
            ip_str (str): Chaîne à vérifier.
        
        Returns:
            bool: True si valide, False sinon.
        """
        try:
            ipaddress.IPv4Address(ip_str)
            return True
        except ipaddress.AddressValueError:
            return False
    
    @staticmethod
    def get_network_address(ip_str: str, subnet_mask: str | int) -> str:
        """
        Calcule l'adresse réseau à partir d'une adresse IPv4 et d'un masque.
        
        Args:
            ip_str (str): Adresse IPv4 (ex. '192.168.1.5')
            subnet_mask (str | int): Masque de sous-réseau.
        
        Returns:
            str: Adresse réseau.
        """
        prefix = NetworkUtils.mask_to_prefix(subnet_mask)
        interface = ipaddress.IPv4Interface(f"{ip_str}/{prefix}")
        return str(interface.network.network_address)
    
    @staticmethod
    def get_broadcast_address(network_address: str, subnet_mask: str | int) -> str:
        """
        Calcule l'adresse de broadcast d'un sous-réseau.
        
        Args:
            network_address (str): Adresse réseau.
            subnet_mask (str | int): Masque de sous-réseau.
        
        Returns:
            str: Adresse de broadcast.
        """
        prefix = NetworkUtils.mask_to_prefix(subnet_mask)
        network = ipaddress.IPv4Network(f"{network_address}/{prefix}", strict=False)
        return str(network.broadcast_address)
    
    @staticmethod
    def get_wildcard_mask(subnet_mask: str | int) -> str:
        """
        Calcule le masque inversé (wildcard) d'un sous-réseau.
        
        Args:
            subnet_mask (str | int): Masque de sous-réseau.
        
        Returns:
            str: Masque inversé (ex. '0.0.0.255' pour 24).
        """
        prefix = NetworkUtils.mask_to_prefix(subnet_mask)
        mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        wildcard_int = 0xFFFFFFFF ^ mask_int
        return NetworkUtils.int_to_ip(wildcard_int)
    
    @staticmethod
    def get_num_hosts(subnet_mask: str | int) -> int:
        """
        Calcule le nombre d'hôtes possibles dans un sous-réseau.
        
        Args:
            subnet_mask (str | int): Masque de sous-réseau.
        
        Returns:
            int: Nombre d'hôtes utilisables.
        """
        prefix = NetworkUtils.mask_to_prefix(subnet_mask)
        if prefix >= 31:
            return 2 ** (32 - prefix)
        return 2 ** (32 - prefix) - 2