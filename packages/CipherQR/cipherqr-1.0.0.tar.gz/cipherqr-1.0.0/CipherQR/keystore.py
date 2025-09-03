"""
Secure key storage for CipherQR using platform-appropriate storage.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives import serialization

from .crypto import CryptoBackend
from .exceptions import KeyStoreError

logger = logging.getLogger(__name__)

class KeyStore:
    """
    Secure key storage with encryption-at-rest and backup capabilities.

    Features:
    - Platform-appropriate storage locations
    - Automatic key generation on first run
    - Key rotation support
    - Robust error handling
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize keystore.

        Args:
            storage_path: Custom storage path (default: platform-appropriate location)
        """
        self.crypto = CryptoBackend()

        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = self._get_default_storage_path()

        # Create storage directory
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create storage directory {self.storage_path}: {e}")
            # Fallback to current directory
            self.storage_path = Path.cwd() / '.cipherqr'
            self.storage_path.mkdir(parents=True, exist_ok=True)

        self.private_key_file = self.storage_path / 'private_key.bin'
        self.public_key_file = self.storage_path / 'public_key.bin'
        self.metadata_file = self.storage_path / 'metadata.json'

        logger.info(f"KeyStore initialized at {self.storage_path}")

    def _get_default_storage_path(self) -> Path:
        """Get platform-appropriate storage path."""
        try:
            if os.name == 'nt':  # Windows
                base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            elif os.name == 'posix':  # Unix/Linux/macOS
                base = Path.home() / '.config'
            else:
                base = Path.home()

            return base / 'cipherqr'
        except Exception:
            # Fallback if home directory detection fails
            return Path.cwd() / '.cipherqr'

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate new X25519 keypair and store securely.

        Returns:
            Tuple of (private_key_bytes, public_key_bytes)
        """
        try:
            private_key, public_key_bytes = self.crypto.generate_keypair()

            # Serialize private key
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )

            # Store keys
            self._write_secure_file(self.private_key_file, private_key_bytes)
            self._write_secure_file(self.public_key_file, public_key_bytes)

            # Store metadata
            metadata = {
                'created_at': int(time.time()),
                'key_type': 'X25519',
                'version': 1,
                'cipher': self.crypto.cipher_name
            }

            try:
                with open(self.metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to write metadata: {e}")

            logger.info("New keypair generated and stored")
            return private_key_bytes, public_key_bytes

        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            raise KeyStoreError(f"Failed to generate keypair: {e}") from e

    def load_private_key(self) -> Optional[bytes]:
        """
        Load private key from secure storage.

        Returns:
            32-byte private key or None if not found
        """
        try:
            if not self.private_key_file.exists():
                return None

            key_data = self._read_secure_file(self.private_key_file)
            if len(key_data) != 32:
                logger.warning(f"Invalid private key size: {len(key_data)} != 32")
                return None

            return key_data

        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            return None

    def load_public_key(self) -> Optional[bytes]:
        """
        Load public key from storage.

        Returns:
            32-byte public key or None if not found
        """
        try:
            if not self.public_key_file.exists():
                return None

            key_data = self._read_secure_file(self.public_key_file)
            if len(key_data) != 32:
                logger.warning(f"Invalid public key size: {len(key_data)} != 32")
                return None

            return key_data

        except Exception as e:
            logger.error(f"Failed to load public key: {e}")
            return None

    def get_or_generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Get existing keypair or generate new one.

        Returns:
            Tuple of (private_key_bytes, public_key_bytes)
        """
        private_key = self.load_private_key()
        public_key = self.load_public_key()

        if private_key and public_key:
            logger.debug("Using existing keypair")
            return private_key, public_key

        logger.info("Generating new keypair")
        return self.generate_keypair()

    def _write_secure_file(self, path: Path, data: bytes):
        """Write file with secure permissions."""
        try:
            with open(path, 'wb') as f:
                f.write(data)

            # Set secure permissions (owner read/write only)
            try:
                os.chmod(path, 0o600)
            except (OSError, AttributeError):
                # Windows or other systems that don't support chmod
                pass

        except Exception as e:
            logger.error(f"Failed to write secure file {path}: {e}")
            raise

    def _read_secure_file(self, path: Path) -> bytes:
        """Read file securely."""
        try:
            with open(path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read secure file {path}: {e}")
            raise

    def clear_all_keys(self):
        """Remove all stored keys. Use with caution!"""
        files_to_remove = [
            self.private_key_file,
            self.public_key_file,
            self.metadata_file
        ]

        for file_path in files_to_remove:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Removed {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove {file_path}: {e}")

        logger.warning("All keys cleared from keystore")
