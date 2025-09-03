import os
import sys
import yaml
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from pathlib import Path


def get_base_dir():
    """Détermine dynamiquement le répertoire de base de l'application"""
    # 1. Si exécuté en tant que script (développement)
    if hasattr(sys, '_MEIPASS'):
        # Mode PyInstaller (exécutable)
        base_path = Path.home() / ".watchman-agent"  # Exemple : C:/Users/Bienvenu/.watchman-agent
        base_path.mkdir(parents=True, exist_ok=True)
    elif '__file__' in globals():
        # Mode script Python normal
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Remonter de 2 niveaux pour atteindre la racine du projet
        base_path = os.path.dirname(os.path.dirname(base_path))
    else:
        # Fallback: répertoire courant
        base_path = os.getcwd()
    
    return base_path

class ConfigManager:
    def __init__(self, client=None):
        # Obtenir le répertoire de base
        self.base_dir = get_base_dir()
        # Chemin absolu pour la configuration globale
        config_dir = os.path.join(self.base_dir, "configs")
        os.makedirs(config_dir, exist_ok=True)
        
        self.config_path = os.path.join(config_dir, "global.yaml")
        
        # Chemin pour les overrides client
        if client:
            override_dir = os.path.join(config_dir, "client_overrides")
            os.makedirs(override_dir, exist_ok=True)
            self.override_path = os.path.join(override_dir, f"{client}.yaml")
        else:
            self.override_path = None
            
        self.crypto_key = self._load_crypto_key()
        self.config = self._load_config()

    def _load_crypto_key(self):
        """Charge la clé de chiffrement depuis .env"""
        # Chemin absolu pour .env
        env_path = os.path.join(self.base_dir, ".env")
        load_dotenv(dotenv_path=env_path)
        
        key = os.getenv("CRYPTO_KEY")
        if not key:
            key = self.generate_key()
        return key.encode()

    def _load_yaml(self, path):
        """Charge un fichier YAML en toute sécurité."""
        if os.path.exists(path):
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_config(self):
        """Charge la configuration globale et applique un override si disponible."""
        config = self._load_yaml(self.config_path)
        if self.override_path:
            override_config = self._load_yaml(self.override_path)
            config = self._merge_configs(config, override_config)
        return config

    def _merge_configs(self, base_config, override_config):
        """Fusionne récursivement la config globale avec l'override client."""
        for key, value in override_config.items():
            if isinstance(value, dict) and key in base_config:
                base_config[key] = self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value
        return base_config

    def save_config(self, data, client=None):
        """Sauvegarde la configuration, globale ou spécifique à un client."""
        path = self.override_path if client else self.config_path
        with open(path, "w") as f:
            yaml.dump(data, f)

    def get(self, key, default=None):
        """Accède à une clé spécifique dans la configuration."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def encrypt(self, plain_text):
        """Chiffre une donnée sensible."""
        fernet = Fernet(self.crypto_key)
        encrypted_value = base64.urlsafe_b64encode(fernet.encrypt(plain_text.encode())).decode()
        return encrypted_value

    def decrypt(self, encrypted_value):
        """Déchiffre une donnée sensible."""
        if not encrypted_value:
            return None
        try:
            fernet = Fernet(self.crypto_key)
            return fernet.decrypt(base64.urlsafe_b64decode(encrypted_value)).decode()
        except Exception as error:
            raise Exception("DEcryptage de la clé don't work")
        
        
        
    def generate_key(self):
        """
        Génère une clé de cryptographie AES-256 et l'enregistre dans le fichier .env.
        """
        # Génère 32 octets pour AES-256
        key = os.urandom(32)
        # Encode la clé en base64 pour la rendre lisible et facile à stocker
        encoded_key = base64.urlsafe_b64encode(key).decode('utf-8')
        
        env_file = os.path.join(self.base_dir, ".env")
        new_line = f"\nCRYPTO_KEY={encoded_key}\n"
        
        # Si le fichier .env existe déjà, on le met à jour
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                lines = f.readlines()
            updated = False
            new_lines = []
            for line in lines:
                if line.startswith("CRYPTO_KEY="):
                    new_lines.append(new_line)
                    updated = True
                else:
                    new_lines.append(line)
            if not updated:
                new_lines.append(new_line)
            with open(env_file, "w") as f:
                f.writelines(new_lines)
        else:
            # Sinon, on crée le fichier .env et on y écrit la clé
            with open(env_file, "w") as f:
                f.write(new_line)
                
        return encoded_key
        
