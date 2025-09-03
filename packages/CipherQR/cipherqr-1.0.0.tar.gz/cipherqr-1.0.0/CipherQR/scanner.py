"""
CipherQR Scanner - Decrypts and validates CipherQR payloads.
"""

import time
import zlib
import base64
import logging
from typing import Dict, Any, Optional
import cbor2

from .crypto import CryptoBackend
from .exceptions import ScanError, DecryptionError, ExpiredError, InvalidFormatError
from .utils import validate_route, decompress_if_compressed

logger = logging.getLogger(__name__)

MAGIC_VERSION = 0x01

class SecurePayload:
    """Represents a successfully decrypted CipherQR payload."""

    def __init__(self, data: Dict[str, Any]):
        self.version = data.get("v", 1)
        self.issued_at = data.get("iat")
        self.ttl = data.get("ttl")
        self.payload_type = data.get("t", "data")
        self.payload = data.get("p")
        self.metadata = data.get("meta", {})
        self.raw_data = data

    @property
    def is_expired(self) -> bool:
        """Check if payload has expired based on iat + ttl."""
        if not self.issued_at or not self.ttl:
            return True
        return time.time() > (self.issued_at + self.ttl)

    @property
    def expires_at(self) -> Optional[int]:
        """Get expiration timestamp."""
        if self.issued_at and self.ttl:
            return self.issued_at + self.ttl
        return None

    def __repr__(self):
        return f"SecurePayload(type={self.payload_type}, expired={self.is_expired})"

class CipherQRScanner:
    """
    Production CipherQR scanner with strict validation and error handling.

    Features:
    - Strict format validation
    - Anti-replay protection via TTL checking
    - Route validation for security
    - Graceful error handling without information leakage
    - Compatible with multiple AEAD ciphers
    """

    def __init__(self, 
                 long_term_private_key: bytes,
                 crypto_backend: Optional[CryptoBackend] = None,
                 strict_mode: bool = True,
                 allowed_routes: Optional[set] = None):
        """
        Initialize scanner with long-term private key.

        Args:
            long_term_private_key: 32-byte X25519 private key for this device
            crypto_backend: Crypto implementation (default: CryptoBackend())
            strict_mode: Reject invalid payloads silently vs raise exceptions
            allowed_routes: Set of allowed route patterns for route-type payloads
        """
        self.crypto = crypto_backend or CryptoBackend()
        self.long_term_private_key = self.crypto.load_private_key_from_bytes(long_term_private_key)
        self.strict_mode = strict_mode
        self.allowed_routes = allowed_routes or set()
        logger.info(f"CipherQR scanner initialized with {self.crypto.cipher_name}")

    def scan(self, encoded_payload: str) -> SecurePayload:
        """
        Scan and decrypt CipherQR payload.

        Args:
            encoded_payload: Base64URL-encoded CipherQR string

        Returns:
            SecurePayload object with decrypted data

        Raises:
            InvalidFormatError: If payload format is invalid
            DecryptionError: If decryption fails
            ExpiredError: If payload has expired
            ScanError: For other scanning errors
        """
        try:
            # Decode base64url
            try:
                packet = self._base64url_decode(encoded_payload)
            except Exception as e:
                raise InvalidFormatError("Invalid base64url encoding") from e

            # Validate minimum size and magic byte
            min_size = 1 + 32 + self.crypto.NONCE_SIZE + 16  # version + pubkey + nonce + min_ciphertext
            if len(packet) < min_size:
                raise InvalidFormatError(f"Packet too short: {len(packet)} < {min_size}")

            if packet[0] != MAGIC_VERSION:
                raise InvalidFormatError(f"Invalid magic/version byte: {packet[0]} != {MAGIC_VERSION}")

            # Parse packet structure (variable nonce size)
            ephemeral_pub_bytes = packet[1:33]
            nonce_end = 33 + self.crypto.NONCE_SIZE
            nonce = packet[33:nonce_end]
            ciphertext = packet[nonce_end:]

            # Perform ECDH with ephemeral public key
            try:
                shared_secret = self.crypto.perform_ecdh(self.long_term_private_key, ephemeral_pub_bytes)
            except Exception as e:
                raise DecryptionError("ECDH failed") from e

            # Derive symmetric key
            symmetric_key = self.crypto.derive_symmetric_key(shared_secret)

            # Decrypt with AEAD
            aad = bytes([MAGIC_VERSION])
            try:
                plaintext_bytes = self.crypto.decrypt_aead(symmetric_key, nonce, ciphertext, aad)
            except Exception as e:
                raise DecryptionError("AEAD decryption failed") from e

            # Decompress if needed
            plaintext_bytes = decompress_if_compressed(plaintext_bytes)

            # Decode CBOR
            try:
                data = cbor2.loads(plaintext_bytes)
            except Exception as e:
                raise InvalidFormatError("Invalid CBOR data") from e

            # Create payload object
            payload = SecurePayload(data)

            # Validate timing
            if payload.is_expired:
                raise ExpiredError(f"Payload expired at {payload.expires_at}")

            # Validate routes if applicable
            if payload.payload_type == "route":
                if not self._validate_route(payload.payload):
                    raise ScanError(f"Route not allowed: {payload.payload}")

            logger.info(f"Successfully scanned CipherQR: type={payload.payload_type}")
            return payload

        except (InvalidFormatError, DecryptionError, ExpiredError, ScanError):
            # Re-raise known errors
            raise
        except Exception as e:
            logger.error(f"Unexpected scan error: {e}")
            if self.strict_mode:
                raise ScanError("Scanning failed") from e
            else:
                raise

    def _base64url_decode(self, data: str) -> bytes:
        """Decode base64url with proper padding."""
        padding = '=' * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)

    def _validate_route(self, route: str) -> bool:
        """Validate route against allowed patterns."""
        if not self.allowed_routes:
            return True  # No restrictions

        return validate_route(route, self.allowed_routes)

    def add_allowed_route(self, route_pattern: str):
        """Add allowed route pattern."""
        self.allowed_routes.add(route_pattern)

    def remove_allowed_route(self, route_pattern: str):
        """Remove allowed route pattern."""
        self.allowed_routes.discard(route_pattern)
