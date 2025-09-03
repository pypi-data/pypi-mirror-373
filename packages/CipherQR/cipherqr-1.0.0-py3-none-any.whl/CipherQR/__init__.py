"""
CipherQR - End-to-end encrypted QR code generator and scanner
============================================================

A production-grade Python package for generating and scanning encrypted QR codes
with forward secrecy, using X25519 ECDH + ChaCha20-Poly1305 AEAD.

Example usage:
    >>> from CipherQR import CipherQRGenerator, CipherQRScanner
    >>> generator = CipherQRGenerator()
    >>> scanner = CipherQRScanner()
"""

__version__ = "1.0.0"
__author__ = "CipherQR Team"

from .generator import CipherQRGenerator
from .scanner import CipherQRScanner
from .crypto import CryptoBackend
from .keystore import KeyStore
from .exceptions import *
from .utils import *

try:
    from .qr_renderer import QRRenderer
    QR_RENDERING_AVAILABLE = True
except ImportError:
    QR_RENDERING_AVAILABLE = False

__all__ = [
    'CipherQRGenerator', 
    'CipherQRScanner', 
    'CryptoBackend', 
    'KeyStore'
]

if QR_RENDERING_AVAILABLE:
    __all__.append('QRRenderer')
