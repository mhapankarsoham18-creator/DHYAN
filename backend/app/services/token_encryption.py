import os
import base64
import logging
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)

_raw_key = os.getenv("AES_ENCRYPTION_KEY")
if not _raw_key:
    print("FATAL: AES_ENCRYPTION_KEY environment variable is missing", file=sys.stderr)
    sys.exit(1)

MASTER_KEY = base64.b64decode(_raw_key)


class TokenEncryption:
    @staticmethod
    def derive_key(user_id: str) -> bytes:
        """HKDF key derivation — unique encryption key per user."""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=f"dhyan_broker_token_{user_id}".encode(),
        )
        return hkdf.derive(MASTER_KEY)

    @staticmethod
    def encrypt_token(token: str, user_id: str) -> str | None:
        """AES-256-GCM encryption with a 96-bit random nonce."""
        if not token:
            return None

        key = TokenEncryption.derive_key(user_id)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)

        try:
            ciphertext = aesgcm.encrypt(nonce, token.encode(), None)
            return base64.b64encode(nonce + ciphertext).decode()
        except Exception as e:
            logger.error("Encryption failed for user %s: %s", user_id, e)
            return None

    @staticmethod
    def decrypt_token(encrypted_data: str, user_id: str) -> str | None:
        """AES-256-GCM decryption."""
        if not encrypted_data:
            return None

        key = TokenEncryption.derive_key(user_id)
        aesgcm = AESGCM(key)

        try:
            data = base64.b64decode(encrypted_data)
            nonce, ciphertext = data[:12], data[12:]
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode()
        except Exception as e:
            logger.error("Decryption failed for user %s: %s", user_id, e)
            return None
