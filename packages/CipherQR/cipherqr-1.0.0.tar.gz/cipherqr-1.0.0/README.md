# CipherQR

> End-to-end encrypted QR codes with forward secrecy

CipherQR is a production-grade Python package for generating and scanning encrypted QR codes that only authorized recipients can decrypt. Each QR code uses ephemeral keys for forward secrecy and authenticated encryption to prevent tampering.

## 🔐 Key Features

- **Forward Secrecy**: Ephemeral X25519 keys per QR code
- **Strong Encryption**: ChaCha20-Poly1305 or AES-GCM AEAD cipher (auto-detected)
- **Anti-Replay Protection**: Time-based expiry (TTL)
- **Wide Compatibility**: Works with older cryptography library versions
- **Optional QR Rendering**: Styled QR codes with graceful fallback
- **Secure Key Storage**: Platform-appropriate key management
- **Production Ready**: Comprehensive testing and error handling

## 🚀 Quick Start

### Installation

```bash
# Extract package
unzip CipherQR_FINAL.zip
cd CipherQR_FINAL

# Install core dependencies
pip install -r requirements.txt

# Install CipherQR
python setup.py install

# Optional: Install QR rendering support
pip install qrcode[pil] Pillow
```

### Quick Test

```bash
# Verify installation
python examples/simple_test.py
```

### Basic Usage

```python
from CipherQR import CipherQRGenerator, CipherQRScanner
from CipherQR.keystore import KeyStore

# Setup
keystore = KeyStore()
private_key, public_key = keystore.get_or_generate_keypair()

# Generate encrypted QR
generator = CipherQRGenerator()
scanner = CipherQRScanner(private_key)

payload = {"message": "Hello, World!", "timestamp": "2025-09-02"}
qr_data = generator.generate(payload, public_key)

# Scan and decrypt
result = scanner.scan(qr_data)
print(f"Decrypted: {result.payload}")
```

## 🛡️ Security Model

### Encryption Protocol
- **Key Agreement**: X25519 Elliptic Curve Diffie-Hellman
- **Key Derivation**: HKDF-SHA256 with context separation
- **Encryption**: ChaCha20-Poly1305 (preferred) or AES-GCM AEAD cipher
- **Forward Secrecy**: New ephemeral keys for each QR code

### Compatibility
CipherQR automatically detects available AEAD ciphers:
- **ChaCha20-Poly1305** (preferred, modern cryptography versions)
- **AES-GCM** (fallback, widely supported)

### Wire Format
```
┌─────────┬──────────────────┬─────────┬─────────────┐
│ Version │ Ephemeral PubKey │  Nonce  │ Ciphertext  │
│ (1 byte)│    (32 bytes)    │(12 bytes)│   (variable) │
└─────────┴──────────────────┴─────────┴─────────────┘
```

## 📖 Testing

```bash
# Quick compatibility test
python examples/simple_test.py

# Run full test suite
python -m pytest tests/ -v

# Individual test files
python tests/test_crypto.py
python tests/test_generator_scanner.py  
python tests/test_keystore.py
```

## 🔧 Advanced Usage

### Route-based Payloads
```python
route_payload = {
    "route": "/user/profile/123", 
    "action": "view"
}

qr_data = generator.generate(
    payload=route_payload,
    recipient_public_key=public_key,
    payload_type="route"
)
```

### Size Estimation
```python
estimation = generator.estimate_qr_size(payload_size)
print(f"Base64 size: {estimation['base64_chars']} chars")
print(f"Single QR recommended: {estimation['recommended_single_qr']}")
```

### QR Rendering (Optional)
```python
try:
    from CipherQR.qr_renderer import QRRenderer, QRStyle

    renderer = QRRenderer()
    style = QRStyle(module_color="#2563eb")

    qr_image = renderer.render(qr_data, style=style)
    renderer.save(qr_image, "encrypted_qr.png")
except ImportError:
    print("QR rendering not available - install qrcode[pil] Pillow")
```

## ⚙️ Requirements

### Core (Required)
- Python 3.8+
- cryptography >= 40.0.0
- cbor2 >= 5.4.0

### Optional (QR Rendering)
- qrcode[pil] >= 7.4.0
- Pillow >= 9.0.0

## 🔍 Troubleshooting

**Q: Getting "cannot import XChaCha20Poly1305" error?**  
A: This version uses ChaCha20-Poly1305 or AES-GCM with automatic fallback for compatibility.

**Q: QR rendering not working?**  
A: QR rendering is optional: `pip install qrcode[pil] Pillow`

**Q: Tests failing?**  
A: Run `python examples/simple_test.py` to isolate the issue.

## 📄 License

MIT License - see LICENSE for details.

---

**✅ This version is compatible with older cryptography libraries and includes graceful fallbacks for all optional features.**
