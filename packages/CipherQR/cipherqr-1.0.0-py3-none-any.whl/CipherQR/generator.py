"""
CipherQR Generator - Creates encrypted QR payloads with forward secrecy.
"""

import time
import zlib
import base64
import logging
from typing import Dict, Any, Optional, Union, List
import cbor2

from .crypto import CryptoBackend
from .exceptions import GenerationError, InvalidPayloadError
from .utils import validate_ttl, compress_if_beneficial

logger = logging.getLogger(__name__)

# Protocol constants
MAGIC_VERSION = 0x01
MAX_SINGLE_QR_SIZE = 800  # Base64 bytes for reliable scanning
DEFAULT_TTL = 300  # 5 minutes

class CipherQRGenerator:
    """
    Production CipherQR generator with compression and robust error handling.

    Features:
    - Forward-secret ephemeral keys per QR
    - CBOR encoding for compact payloads
    - Optional zlib compression
    - TTL validation and anti-replay protection
    - Compatible with multiple AEAD ciphers
    """

    def __init__(self, crypto_backend: Optional[CryptoBackend] = None):
        self.crypto = crypto_backend or CryptoBackend()
        logger.info(f"CipherQR generator initialized with {self.crypto.cipher_name}")

    def generate(self, 
                payload: Union[Dict[str, Any], bytes], 
                recipient_public_key: bytes,
                ttl_seconds: int = DEFAULT_TTL,
                compress: bool = True,
                payload_type: str = "data",
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate encrypted CipherQR payload string.

        Args:
            payload: Data to encrypt (dict or raw bytes)
            recipient_public_key: 32-byte X25519 public key
            ttl_seconds: Time-to-live in seconds (default: 5min)
            compress: Apply zlib compression if beneficial
            payload_type: "data" or "route" for payload classification
            metadata: Optional additional metadata

        Returns:
            Base64URL-encoded CipherQR string ready for QR encoding

        Raises:
            InvalidPayloadError: If payload is invalid
            GenerationError: If encryption fails
        """
        try:
            # Validate inputs
            if not validate_ttl(ttl_seconds):
                raise InvalidPayloadError(f"Invalid TTL: {ttl_seconds}")

            if len(recipient_public_key) != 32:
                raise InvalidPayloadError("Recipient public key must be 32 bytes")

            # Build plaintext structure
            issued_at = int(time.time())
            plaintext_obj = {
                "v": 1,  # Protocol version
                "iat": issued_at,
                "ttl": ttl_seconds,
                "t": payload_type,
                "p": payload,
            }

            if metadata:
                plaintext_obj["meta"] = metadata

            # Encode to CBOR
            try:
                plaintext_bytes = cbor2.dumps(plaintext_obj)
                logger.debug(f"CBOR encoded: {len(plaintext_bytes)} bytes")
            except Exception as e:
                raise InvalidPayloadError(f"Failed to encode payload to CBOR: {e}") from e

            # Compress if beneficial
            if compress:
                plaintext_bytes = compress_if_beneficial(plaintext_bytes)

            # Generate ephemeral keypair for forward secrecy
            ephemeral_private, ephemeral_public_bytes = self.crypto.generate_keypair()

            # Perform ECDH
            shared_secret = self.crypto.perform_ecdh(ephemeral_private, recipient_public_key)

            # Derive symmetric key
            symmetric_key = self.crypto.derive_symmetric_key(shared_secret)

            # Encrypt with AEAD
            aad = bytes([MAGIC_VERSION])  # Authenticated additional data
            nonce, ciphertext = self.crypto.encrypt_aead(symmetric_key, plaintext_bytes, aad)

            # Build binary packet: version || ephemeral_pub || nonce || ciphertext
            packet = bytes([MAGIC_VERSION]) + ephemeral_public_bytes + nonce + ciphertext

            # Encode to base64url (QR-friendly)
            encoded = base64.urlsafe_b64encode(packet).rstrip(b'=').decode('ascii')

            logger.info(f"Generated CipherQR: {len(packet)} bytes -> {len(encoded)} chars")

            if len(encoded) > MAX_SINGLE_QR_SIZE:
                logger.warning(f"Large payload ({len(encoded)} chars) may need multi-part QR")

            return encoded

        except (InvalidPayloadError, GenerationError):
            # Re-raise known errors
            raise
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise GenerationError(f"Failed to generate CipherQR: {e}") from e

    def estimate_qr_size(self, payload_size: int) -> Dict[str, int]:
        """
        Estimate final QR size for capacity planning.

        Args:
            payload_size: Size of plaintext payload in bytes

        Returns:
            Dict with estimated sizes at different stages
        """
        # Overhead: version(1) + ephemeral_pub(32) + nonce(12) + auth_tag(16)
        crypto_overhead = 1 + 32 + self.crypto.NONCE_SIZE + 16

        # CBOR overhead (estimated)
        cbor_overhead = payload_size * 0.1  # ~10% overhead

        # Base64 expansion (4/3 ratio)
        total_binary = payload_size + cbor_overhead + crypto_overhead
        base64_size = int(total_binary * 4 / 3)

        return {
            "plaintext_bytes": payload_size,
            "cbor_bytes": int(payload_size + cbor_overhead),
            "encrypted_bytes": int(total_binary),
            "base64_chars": base64_size,
            "recommended_single_qr": base64_size <= MAX_SINGLE_QR_SIZE,
            "cipher": self.crypto.cipher_name
        }
