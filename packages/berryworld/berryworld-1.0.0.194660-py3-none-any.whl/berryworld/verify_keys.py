import os
import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

backend = default_backend()
load_dotenv(os.path.join(os.getcwd(), '.env'))


class Verify:
    """ Encrypt and Verify keys """

    def __init__(self, key_name: str = 'SECRET-KEY', key_override: str = None):
        """ Initialize the class """
        self.key = os.environ.get(key_name)
        if key_override is not None:
            self.key = key_override
        self.iterations = 100_000

    def decrypt(self, token: str) -> str:
        """ Get token and decrypt it
        :param token: Encrypted key
        :return: Decrypted token
        """
        decoded = b64d(token.encode('utf-8'))
        salt, itera, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
        iterations = int.from_bytes(itera, 'big')
        key = self._derive_key(self.key, salt, iterations)
        return Fernet(key).decrypt(token).decode('utf-8')

    def encrypt(self, message: str) -> str:
        """ Encrypt message
        :param message: Plain text message
        :return: Encrypted message
        """
        salt = secrets.token_bytes(16)
        key = self._derive_key(self.key, salt, self.iterations)
        return b64e(
            b'%b%b%b' % (
                salt,
                self.iterations.to_bytes(4, 'big'),
                b64d(Fernet(key).encrypt(message.encode())),
            )
        ).decode('utf-8')

    def verify(self, key: str, encrypted: str) -> bool:
        """ Verify encrypted passwords
        :param key: Encrypted key
        :param encrypted: Second encrypted key
        :return: Whether the two encrypted values are equal or not
        """
        return self.decrypt(key) == self.decrypt(encrypted)

    def double_encrypt(self, message: str) -> str:
        """ Encrypt message
        :param message: Plain text message
        :return: Encrypted message
        """
        salt = secrets.token_bytes(16)
        key = self._derive_key(self.key, salt, self.iterations)
        first_encryption = b64e(
            b'%b%b%b' % (
                salt,
                self.iterations.to_bytes(4, 'big'),
                b64d(Fernet(key).encrypt(message.encode())),
            )
        ).decode('utf-8')
        key2 = self._derive_key(self.key[::-1], salt, self.iterations)
        second_encryption = b64e(
            b'%b%b%b' % (
                salt,
                self.iterations.to_bytes(4, 'big'),
                b64d(Fernet(key2).encrypt(first_encryption.encode())),
            )
        ).decode('utf-8')
        return second_encryption

    def double_decrypt(self, token: str) -> str:
        """ Get token and decrypt it
        :param token: Encrypted key
        :return: Decrypted token
        """
        decoded = b64d(token.encode('utf-8'))
        salt, itera, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
        iterations = int.from_bytes(itera, 'big')
        key = self._derive_key(self.key[::-1], salt, iterations)
        first_token = Fernet(key).decrypt(token).decode('utf-8')

        decoded = b64d(first_token.encode('utf-8'))
        salt, itera, first_token = decoded[:16], decoded[16:20], b64e(decoded[20:])
        iterations = int.from_bytes(itera, 'big')
        key2 = self._derive_key(self.key, salt, iterations)
        second_decryption = Fernet(key2).decrypt(first_token).decode('utf-8')
        return second_decryption

    def double_verify(self, key: str, encrypted: str) -> bool:
        """ Verify encrypted passwords
        :param key: Encrypted key
        :param encrypted: Second encrypted key
        :return: Whether the two encrypted values are equal or not
        """
        return self.double_decrypt(key) == self.double_decrypt(encrypted)

    @staticmethod
    def _derive_key(key: str, salt: bytes, iterations: int) -> bytes:
        """Derive a secret key from a given passphrase and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt,
            iterations=iterations, backend=backend)
        return b64e(kdf.derive(key.encode()))
