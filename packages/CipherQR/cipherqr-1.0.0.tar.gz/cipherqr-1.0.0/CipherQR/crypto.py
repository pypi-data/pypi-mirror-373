"""
Cryptographic backend for CipherQR using widely supported primitives.
Uses X25519 ECDH + HKDF-SHA256 + ChaCha20-Poly1305 AEAD for forward-secret encryption.
"""

import os
import logging
from typing import Tuple, Optional
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

# Try to import AEAD ciphers in order of preference
AEAD_CIPHER = None
NONCE_SIZE = 12  # Default for most AEAD ciphers

try:
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    AEAD_CIPHER = ChaCha20Poly1305
    NONCE_SIZE = 12
    CIPHER_NAME = "ChaCha20Poly1305"
except ImportError:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        AEAD_CIPHER = AESGCM
        NONCE_SIZE = 12
        CIPHER_NAME = "AES-GCM"
    except ImportError:
        raise ImportError("No supported AEAD cipher found. Please upgrade cryptography: pip install --upgrade cryptography")

logger = logging.getLogger(__name__)

class CryptoBackend:
    """
    Production cryptographic backend implementing the CipherQR protocol.

    Protocol:
    - Ephemeral X25519 keys per QR for forward secrecy
    - HKDF-SHA256 for key derivation with context
    - ChaCha20-Poly1305 or AES-GCM AEAD for authenticated encryption
    - Variable nonce size based on cipher (12 bytes for ChaCha20/AES-GCM)
    """

    CONTEXT_INFO = b"cipherqr-v1-2025"
    NONCE_SIZE = NONCE_SIZE
    PUBLIC_KEY_SIZE = 32

    def __init__(self):
        self.cipher_name = CIPHER_NAME
        self._validate_crypto_availability()
        logger.info(f"CryptoBackend initialized with {self.cipher_name}")

    def _validate_crypto_availability(self):
        """Ensure cryptographic primitives are available"""
        try:
            # Test key generation
            key = X25519PrivateKey.generate()
            # Test AEAD
            if self.cipher_name == "AES-GCM":
                aead = AEAD_CIPHER(os.urandom(32))  # AES-256
            else:
                aead = AEAD_CIPHER(os.urandom(32))  # ChaCha20
            logger.info(f"Cryptographic backend validated with {self.cipher_name}")
        except Exception as e:
            logger.error(f"Crypto backend validation failed: {e}")
            raise RuntimeError(f"Cryptographic primitives unavailable: {e}") from e

    def generate_keypair(self) -> Tuple[X25519PrivateKey, bytes]:
        """
        Generate X25519 keypair for long-term or ephemeral use.

        Returns:
            Tuple of (private_key_object, public_key_bytes)
        """
        private_key = X25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return private_key, public_key_bytes

    def load_private_key_from_bytes(self, key_bytes: bytes) -> X25519PrivateKey:
        """Load X25519 private key from raw bytes"""
        return X25519PrivateKey.from_private_bytes(key_bytes)

    def load_public_key_from_bytes(self, key_bytes: bytes) -> X25519PublicKey:
        """Load X25519 public key from raw bytes"""
        if len(key_bytes) != self.PUBLIC_KEY_SIZE:
            raise ValueError(f"Invalid public key size: {len(key_bytes)} != {self.PUBLIC_KEY_SIZE}")
        return X25519PublicKey.from_public_bytes(key_bytes)

    def perform_ecdh(self, private_key: X25519PrivateKey, peer_public_bytes: bytes) -> bytes:
        """
        Perform ECDH key agreement.

        Args:
            private_key: Local X25519 private key
            peer_public_bytes: Peer's X25519 public key (32 bytes)

        Returns:
            32-byte shared secret
        """
        peer_public_key = self.load_public_key_from_bytes(peer_public_bytes)
        shared_secret = private_key.exchange(peer_public_key)
        logger.debug(f"ECDH performed, shared secret length: {len(shared_secret)}")
        return shared_secret

    def derive_symmetric_key(self, shared_secret: bytes, context: Optional[bytes] = None) -> bytes:
        """
        Derive symmetric key using HKDF-SHA256.

        Args:
            shared_secret: Output from ECDH
            context: Additional context info (default: CONTEXT_INFO)

        Returns:
            32-byte symmetric key for AEAD cipher
        """
        if context is None:
            context = self.CONTEXT_INFO

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes for ChaCha20 or AES-256
            salt=None,
            info=context,
        )
        derived_key = hkdf.derive(shared_secret)
        logger.debug("Symmetric key derived via HKDF")
        return derived_key

    def encrypt_aead(self, key: bytes, plaintext: bytes, aad: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt using AEAD cipher (ChaCha20-Poly1305 or AES-GCM).

        Args:
            key: 32-byte symmetric key
            plaintext: Data to encrypt
            aad: Additional authenticated data

        Returns:
            Tuple of (nonce, ciphertext_with_tag)
        """
        if len(key) != 32:
            raise ValueError(f"Invalid key size: {len(key)} != 32")

        nonce = os.urandom(self.NONCE_SIZE)
        aead = AEAD_CIPHER(key)
        ciphertext = aead.encrypt(nonce, plaintext, aad)

        logger.debug(f"AEAD encryption ({self.cipher_name}): plaintext={len(plaintext)}B -> ciphertext={len(ciphertext)}B")
        return nonce, ciphertext

    def decrypt_aead(self, key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
        """
        Decrypt using AEAD cipher.

        Args:
            key: 32-byte symmetric key
            nonce: Nonce used for encryption (size varies by cipher)
            ciphertext: Ciphertext with authentication tag
            aad: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext

        Raises:
            cryptography.exceptions.InvalidSignature: If authentication fails
        """
        if len(key) != 32:
            raise ValueError(f"Invalid key size: {len(key)} != 32")
        if len(nonce) != self.NONCE_SIZE:
            raise ValueError(f"Invalid nonce size: {len(nonce)} != {self.NONCE_SIZE}")

        aead = AEAD_CIPHER(key)

        try:
            plaintext = aead.decrypt(nonce, ciphertext, aad)
            logger.debug(f"AEAD decryption ({self.cipher_name}): ciphertext={len(ciphertext)}B -> plaintext={len(plaintext)}B")
            return plaintext
        except InvalidSignature as e:
            logger.warning("AEAD authentication failed")
            raise
        except Exception as e:
            logger.error(f"AEAD decryption failed: {e}")
            raise InvalidSignature("Decryption failed") from e

    def secure_compare(self, a: bytes, b: bytes) -> bool:
        """Constant-time comparison to prevent timing attacks"""
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        return result == 0
