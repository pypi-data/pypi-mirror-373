"""
Tests for CipherQR generator and scanner.
"""

import unittest
import time
from CipherQR import CipherQRGenerator, CipherQRScanner
from CipherQR.keystore import KeyStore
from CipherQR.exceptions import ExpiredError, DecryptionError, InvalidPayloadError

class TestGeneratorScanner(unittest.TestCase):

    def setUp(self):
        # Create test keypairs
        self.keystore = KeyStore()
        self.private_key, self.public_key = self.keystore.generate_keypair()

        self.generator = CipherQRGenerator()
        self.scanner = CipherQRScanner(self.private_key)

    def test_basic_roundtrip(self):
        """Test basic generation and scanning."""
        payload = {
            "message": "Hello, World!", 
            "timestamp": int(time.time()),
            "data": [1, 2, 3, 4, 5]
        }

        # Generate
        qr_data = self.generator.generate(
            payload=payload,
            recipient_public_key=self.public_key
        )

        # Verify QR data format
        self.assertIsInstance(qr_data, str)
        self.assertGreater(len(qr_data), 50)

        # Scan
        result = self.scanner.scan(qr_data)

        # Verify result
        self.assertEqual(result.payload, payload)
        self.assertEqual(result.payload_type, "data")
        self.assertFalse(result.is_expired)
        self.assertEqual(result.version, 1)

    def test_route_payload(self):
        """Test route-type payload."""
        route_data = {"route": "/user/profile/123", "action": "view"}

        qr_data = self.generator.generate(
            payload=route_data,
            recipient_public_key=self.public_key,
            payload_type="route"
        )

        result = self.scanner.scan(qr_data)
        self.assertEqual(result.payload_type, "route")
        self.assertEqual(result.payload, route_data)

    def test_metadata(self):
        """Test metadata handling."""
        payload = {"message": "Test with metadata"}
        metadata = {"sender": "alice", "priority": "high", "tags": ["urgent", "test"]}

        qr_data = self.generator.generate(
            payload=payload,
            recipient_public_key=self.public_key,
            metadata=metadata
        )

        result = self.scanner.scan(qr_data)
        self.assertEqual(result.metadata, metadata)
        self.assertEqual(result.payload, payload)

    def test_expiry(self):
        """Test TTL expiry."""
        payload = {"message": "This will expire quickly"}

        # Generate with 1 second TTL
        qr_data = self.generator.generate(
            payload=payload,
            recipient_public_key=self.public_key,
            ttl_seconds=1
        )

        # Should work immediately
        result = self.scanner.scan(qr_data)
        self.assertFalse(result.is_expired)
        self.assertEqual(result.ttl, 1)

        # Wait for expiry
        time.sleep(1.5)

        # Should now fail
        with self.assertRaises(ExpiredError):
            self.scanner.scan(qr_data)

    def test_wrong_key(self):
        """Test decryption with wrong key."""
        payload = {"message": "Secret message"}

        # Generate for our key
        qr_data = self.generator.generate(
            payload=payload,
            recipient_public_key=self.public_key
        )

        # Try to scan with different key
        other_keystore = KeyStore()
        other_private, _ = other_keystore.generate_keypair()
        other_scanner = CipherQRScanner(other_private)

        with self.assertRaises(DecryptionError):
            other_scanner.scan(qr_data)

    def test_invalid_payload(self):
        """Test invalid payload handling."""
        # Invalid TTL
        with self.assertRaises(InvalidPayloadError):
            self.generator.generate(
                payload={"test": "data"},
                recipient_public_key=self.public_key,
                ttl_seconds=0
            )

        # Invalid public key
        with self.assertRaises(InvalidPayloadError):
            self.generator.generate(
                payload={"test": "data"},
                recipient_public_key=b"too_short"
            )

    def test_compression(self):
        """Test compression for large payloads."""
        # Create large, compressible payload
        large_payload = {
            "data": "A" * 1000,  # Highly compressible
            "metadata": {"type": "test", "size": "large"}
        }

        # Generate with and without compression
        qr_compressed = self.generator.generate(
            payload=large_payload,
            recipient_public_key=self.public_key,
            compress=True
        )

        qr_uncompressed = self.generator.generate(
            payload=large_payload,
            recipient_public_key=self.public_key,
            compress=False
        )

        # Compressed should be smaller (or same size if compression not beneficial)
        self.assertLessEqual(len(qr_compressed), len(qr_uncompressed))

        # Both should decrypt to same result
        result1 = self.scanner.scan(qr_compressed)
        result2 = self.scanner.scan(qr_uncompressed)

        self.assertEqual(result1.payload, result2.payload)
        self.assertEqual(result1.payload, large_payload)

    def test_size_estimation(self):
        """Test QR size estimation."""
        payload = {"message": "Test message for size estimation"}
        import cbor2
        payload_size = len(cbor2.dumps(payload))

        estimation = self.generator.estimate_qr_size(payload_size)

        self.assertIsInstance(estimation, dict)
        self.assertIn("plaintext_bytes", estimation)
        self.assertIn("encrypted_bytes", estimation)
        self.assertIn("base64_chars", estimation)
        self.assertIn("recommended_single_qr", estimation)
        self.assertIn("cipher", estimation)

        self.assertEqual(estimation["plaintext_bytes"], payload_size)
        self.assertGreater(estimation["encrypted_bytes"], payload_size)
        self.assertTrue(isinstance(estimation["recommended_single_qr"], bool))

    def test_binary_payload(self):
        """Test with binary payload data."""
        binary_payload = os.urandom(200)

        qr_data = self.generator.generate(
            payload=binary_payload,
            recipient_public_key=self.public_key
        )

        result = self.scanner.scan(qr_data)
        self.assertEqual(result.payload, binary_payload)

if __name__ == '__main__':
    import os
    unittest.main()
