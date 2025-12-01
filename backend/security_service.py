import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import logging

# Logger Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SafeChildSecurity")

class SecurityService:
    """
    Handles encryption/decryption of forensic evidence files (AES-256-GCM).
    Implements Envelope Encryption pattern.
    """

    def __init__(self, master_key_str: str = None):
        # In production, this MUST come from a secure Vault or Environment Variable
        env_key = os.getenv("SAFECHILD_MASTER_KEY")
        
        if not env_key:
            # CRITICAL: Fail fast if no key is provided to prevent permanent data loss
            error_msg = "CRITICAL: SAFECHILD_MASTER_KEY is not set. Application cannot start to prevent data loss."
            logger.critical(error_msg)
            raise RuntimeError(error_msg)
        
        # Ensure key is 32 bytes (using KDF if it's a string passphrase)
        # TODO: In future, migrate to a random salt stored per-installation or per-key
        salt = b'safechild_static_salt' 
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        self.master_key = kdf.derive(env_key.encode())

    def encrypt_file(self, file_content: bytes) -> dict:
        """
        Encrypts file content using a unique random key (DEK).
        Returns the encrypted content and the encrypted DEK.
        """
        try:
            # 1. Generate a random Data Encryption Key (DEK) for this file
            dek = os.urandom(32)
            iv = os.urandom(12)  # 96-bit nonce for GCM

            # 2. Encrypt the content with DEK
            encryptor = Cipher(
                algorithms.AES(dek),
                modes.GCM(iv),
                backend=default_backend()
            ).encryptor()

            ciphertext = encryptor.update(file_content) + encryptor.finalize()
            tag = encryptor.tag

            # 3. Encrypt the DEK with Master Key (Key Wrapping)
            # We use simple AES-ECB for key wrapping since key is random block, or GCM again.
            # Let's use GCM for wrapping too for integrity.
            wrapper_iv = os.urandom(12)
            wrapper = Cipher(
                algorithms.AES(self.master_key),
                modes.GCM(wrapper_iv),
                backend=default_backend()
            ).encryptor()
            
            encrypted_dek = wrapper.update(dek) + wrapper.finalize()
            wrapper_tag = wrapper.tag

            return {
                "encrypted_data": ciphertext,
                "file_iv": base64.b64encode(iv).decode('utf-8'),
                "file_tag": base64.b64encode(tag).decode('utf-8'),
                "encrypted_dek": base64.b64encode(encrypted_dek).decode('utf-8'),
                "dek_iv": base64.b64encode(wrapper_iv).decode('utf-8'),
                "dek_tag": base64.b64encode(wrapper_tag).decode('utf-8')
            }

        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt_file(self, encrypted_data: bytes, metadata: dict) -> bytes:
        """
        Decrypts file content by first unwrapping the DEK.
        """
        try:
            # 1. Unwrap (Decrypt) the DEK using Master Key
            wrapper_iv = base64.b64decode(metadata['dek_iv'])
            wrapper_tag = base64.b64decode(metadata['dek_tag'])
            encrypted_dek = base64.b64decode(metadata['encrypted_dek'])

            unwrapper = Cipher(
                algorithms.AES(self.master_key),
                modes.GCM(wrapper_iv, wrapper_tag),
                backend=default_backend()
            ).decryptor()

            dek = unwrapper.update(encrypted_dek) + unwrapper.finalize()

            # 2. Decrypt the file content using DEK
            file_iv = base64.b64decode(metadata['file_iv'])
            file_tag = base64.b64decode(metadata['file_tag'])

            decryptor = Cipher(
                algorithms.AES(dek),
                modes.GCM(file_iv, file_tag),
                backend=default_backend()
            ).decryptor()

            plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
            return plaintext

        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

# Singleton instance
security_service = SecurityService()
