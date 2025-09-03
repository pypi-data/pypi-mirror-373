"""
Setup configuration for CipherQR package.
"""

from setuptools import setup, find_packages
import os

# Read README
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "End-to-end encrypted QR code generator and scanner with forward secrecy"

# Core requirements (minimal for maximum compatibility)
requirements = [
    "cryptography>=40.0.0",  # Lowered version requirement
    "cbor2>=5.4.0"
]

# Optional requirements for QR rendering
extras_require = {
    "qr": ["qrcode[pil]>=7.4.0", "Pillow>=9.0.0"],
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0"
    ]
}

setup(
    name="CipherQR",
    version="1.0.0",
    author="CipherQR Development Team",
    author_email="dev@cipherqr.com",
    description="End-to-end encrypted QR code generator and scanner with forward secrecy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    include_package_data=True,
    zip_safe=False,
)
