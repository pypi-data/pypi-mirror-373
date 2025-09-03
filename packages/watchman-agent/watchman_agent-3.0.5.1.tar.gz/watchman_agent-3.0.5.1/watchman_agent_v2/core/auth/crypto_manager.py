from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class CryptoManager:
    """
    Gestion du chiffrement AES-256 et de la rotation des clés.
    """
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        """Chiffre les données avec AES-256 (exemple simplifié)."""
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Déchiffre les données avec AES-256."""
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()

    def rotate_key(self, new_key: bytes):
        """Effectue la rotation de la clé."""
        self.key = new_key
