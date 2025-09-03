"""
Tests for CipherQR keystore.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from CipherQR.keystore import KeyStore

class TestKeyStore(unittest.TestCase):

    def setUp(self):
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.keystore = KeyStore(storage_path=self.temp_dir)

    def tearDown(self):
        # Clean up temporary directory
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def test_keystore_initialization(self):
        """Test keystore initializes properly."""
        self.assertTrue(self.temp_dir.exists())
        self.assertEqual(self.keystore.storage_path, self.temp_dir)

    def test_keypair_generation(self):
        """Test keypair generation and storage."""
        private_key, public_key = self.keystore.generate_keypair()

        self.assertEqual(len(private_key), 32)
        self.assertEqual(len(public_key), 32)

        # Keys should be stored
        self.assertTrue((self.temp_dir / 'private_key.bin').exists())
        self.assertTrue((self.temp_dir / 'public_key.bin').exists())
        self.assertTrue((self.temp_dir / 'metadata.json').exists())

    def test_key_loading(self):
        """Test loading stored keys."""
        # Generate and store keys
        orig_private, orig_public = self.keystore.generate_keypair()

        # Load keys
        loaded_private = self.keystore.load_private_key()
        loaded_public = self.keystore.load_public_key()

        self.assertEqual(orig_private, loaded_private)
        self.assertEqual(orig_public, loaded_public)

    def test_get_or_generate(self):
        """Test get_or_generate_keypair method."""
        # First call should generate
        private1, public1 = self.keystore.get_or_generate_keypair()

        # Second call should return existing keys
        private2, public2 = self.keystore.get_or_generate_keypair()

        self.assertEqual(private1, private2)
        self.assertEqual(public1, public2)

    def test_missing_keys(self):
        """Test behavior when keys don't exist."""
        # Initially no keys exist
        private_key = self.keystore.load_private_key()
        public_key = self.keystore.load_public_key()

        self.assertIsNone(private_key)
        self.assertIsNone(public_key)

    def test_corrupted_keys(self):
        """Test handling of corrupted key files."""
        # Create corrupted private key file
        with open(self.temp_dir / 'private_key.bin', 'wb') as f:
            f.write(b"corrupted_data_wrong_size")

        # Should return None for corrupted key
        private_key = self.keystore.load_private_key()
        self.assertIsNone(private_key)

    def test_clear_keys(self):
        """Test clearing all keys."""
        # Generate keys
        self.keystore.generate_keypair()

        # Verify they exist
        self.assertTrue((self.temp_dir / 'private_key.bin').exists())
        self.assertTrue((self.temp_dir / 'public_key.bin').exists())

        # Clear keys
        self.keystore.clear_all_keys()

        # Verify they're gone
        self.assertFalse((self.temp_dir / 'private_key.bin').exists())
        self.assertFalse((self.temp_dir / 'public_key.bin').exists())

    def test_default_storage_path(self):
        """Test default storage path selection."""
        keystore = KeyStore()  # No explicit path

        # Should create a reasonable default path
        self.assertTrue(keystore.storage_path.exists())
        self.assertTrue(str(keystore.storage_path).endswith('cipherqr'))

if __name__ == '__main__':
    unittest.main()
