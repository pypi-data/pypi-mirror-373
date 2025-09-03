import os
import yaml
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv

class CryptManager:
    def __init__(self):
        self.crypto_key = self._load_crypto_key()

    def _load_crypto_key(self):
        """Charge la clé de chiffrement depuis .env"""
        load_dotenv()
        key = os.getenv("CRYPTO_KEY")
        if not key:
            raise ValueError("CRYPTO_KEY est manquant dans .env !")
        return key.encode()

    def encrypt(self, plain_text):
        """Chiffre une donnée sensible."""
        fernet = Fernet(self.crypto_key)
        encrypted_value = base64.urlsafe_b64encode(fernet.encrypt(plain_text.encode())).decode()
        return encrypted_value

    def decrypt(self, encrypted_value):
        """Déchiffre une donnée sensible."""
        if not encrypted_value:
            return None
        fernet = Fernet(self.crypto_key)
        return fernet.decrypt(base64.urlsafe_b64decode(encrypted_value)).decode()
