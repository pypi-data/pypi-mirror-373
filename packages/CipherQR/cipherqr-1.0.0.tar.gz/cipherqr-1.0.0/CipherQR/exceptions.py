"""
Custom exceptions for CipherQR package.
"""

class CipherQRError(Exception):
    """Base exception for CipherQR package."""
    pass

class GenerationError(CipherQRError):
    """Error during QR generation."""
    pass

class ScanError(CipherQRError):
    """Error during QR scanning."""
    pass

class InvalidPayloadError(CipherQRError):
    """Invalid payload data."""
    pass

class InvalidFormatError(CipherQRError):
    """Invalid QR format."""
    pass

class DecryptionError(CipherQRError):
    """Decryption failed."""
    pass

class ExpiredError(CipherQRError):
    """QR payload has expired."""
    pass

class KeyStoreError(CipherQRError):
    """Key storage error."""
    pass
