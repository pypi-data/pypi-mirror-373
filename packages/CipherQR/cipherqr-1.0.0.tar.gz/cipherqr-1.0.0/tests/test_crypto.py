"""
Tests for CipherQR crypto backend.
"""

import unittest
import os
from CipherQR.crypto import CryptoBackend
from cryptography.exceptions import InvalidSignature

class TestCryptoBackend(unittest.TestCase):

    def setUp(self):
        self.crypto = CryptoBackend()

    def test_backend_initialization(self):
        """Test crypto backend initializes properly."""
        self.assertIsNotNone(self.crypto)
        self.assertIn(self.crypto.cipher_name, ["ChaCha20Poly1305", "AES-GCM"])
        self.assertGreaterEqual(self.crypto.NONCE_SIZE, 12)
        self.assertEqual(self.crypto.PUBLIC_KEY_SIZE, 32)

    def test_keypair_generation(self):
        """Test X25519 keypair generation."""
        private_key, public_key_bytes = self.crypto.generate_keypair()

        # Check public key size
        self.assertEqual(len(public_key_bytes), 32)

        # Check we can load the keys back
        from cryptography.hazmat.primitives import serialization
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.assertEqual(len(private_key_bytes), 32)

        loaded_private = self.crypto.load_private_key_from_bytes(private_key_bytes)
        loaded_public = self.crypto.load_public_key_from_bytes(public_key_bytes)

        self.assertIsNotNone(loaded_private)
        self.assertIsNotNone(loaded_public)

    def test_ecdh_roundtrip(self):
        """Test ECDH key agreement."""
        # Generate two keypairs
        priv1, pub1 = self.crypto.generate_keypair()
        priv2, pub2 = self.crypto.generate_keypair()

        # Perform ECDH from both sides
        shared1 = self.crypto.perform_ecdh(priv1, pub2)
        shared2 = self.crypto.perform_ecdh(priv2, pub1)

        # Shared secrets should match
        self.assertEqual(shared1, shared2)
        self.assertEqual(len(shared1), 32)

    def test_key_derivation(self):
        """Test HKDF key derivation."""
        shared_secret = os.urandom(32)

        # Derive same key twice
        key1 = self.crypto.derive_symmetric_key(shared_secret)
        key2 = self.crypto.derive_symmetric_key(shared_secret)

        self.assertEqual(key1, key2)
        self.assertEqual(len(key1), 32)

        # Different context should give different key
        key3 = self.crypto.derive_symmetric_key(shared_secret, b"different-context")
        self.assertNotEqual(key1, key3)

    def test_aead_roundtrip(self):
        """Test AEAD encryption/decryption."""
        key = os.urandom(32)
        plaintext = b"Hello, World! This is a test message."
        aad = b"additional authenticated data"

        # Encrypt
        nonce, ciphertext = self.crypto.encrypt_aead(key, plaintext, aad)

        # Verify nonce size
        self.assertEqual(len(nonce), self.crypto.NONCE_SIZE)

        # Verify ciphertext is different from plaintext
        self.assertNotEqual(plaintext, ciphertext)

        # Decrypt
        decrypted = self.crypto.decrypt_aead(key, nonce, ciphertext, aad)

        # Verify roundtrip
        self.assertEqual(plaintext, decrypted)

    def test_aead_authentication(self):
        """Test AEAD authentication failure."""
        key = os.urandom(32)
        plaintext = b"Hello, World!"
        aad = b"additional data"

        nonce, ciphertext = self.crypto.encrypt_aead(key, plaintext, aad)

        # Wrong key should fail
        wrong_key = os.urandom(32)
        with self.assertRaises(InvalidSignature):
            self.crypto.decrypt_aead(wrong_key, nonce, ciphertext, aad)

        # Wrong AAD should fail
        with self.assertRaises(InvalidSignature):
            self.crypto.decrypt_aead(key, nonce, ciphertext, b"wrong aad")

        # Corrupted ciphertext should fail
        if len(ciphertext) > 1:
            corrupted = bytearray(ciphertext)
            corrupted[0] ^= 1
            with self.assertRaises(InvalidSignature):
                self.crypto.decrypt_aead(key, nonce, bytes(corrupted), aad)

    def test_secure_compare(self):
        """Test constant-time comparison."""
        a = b"hello world"
        b = b"hello world"
        c = b"hello worlx"
        d = b"hello"

        self.assertTrue(self.crypto.secure_compare(a, b))
        self.assertFalse(self.crypto.secure_compare(a, c))
        self.assertFalse(self.crypto.secure_compare(a, d))

if __name__ == '__main__':
    unittest.main()
