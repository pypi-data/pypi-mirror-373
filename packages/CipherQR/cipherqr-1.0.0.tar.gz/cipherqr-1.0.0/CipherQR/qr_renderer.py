"""
QR Code renderer with customization support for CipherQR.
"""

import logging
from typing import Optional
from io import BytesIO

logger = logging.getLogger(__name__)

# Try to import QR rendering dependencies
QR_AVAILABLE = False
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
    logger.debug("QR rendering dependencies available")
except ImportError as e:
    logger.debug(f"QR rendering not available: {e}")
    qrcode = None
    Image = None

class QRStyle:
    """QR code styling configuration."""

    def __init__(self,
                 module_color: str = "#000000",
                 background_color: str = "#FFFFFF",
                 border: int = 4):
        """
        Initialize QR styling options.

        Args:
            module_color: Hex color for QR modules
            background_color: Hex color for background
            border: Border size in modules
        """
        self.module_color = module_color
        self.background_color = background_color
        self.border = border

class QRRenderer:
    """
    QR code renderer with basic styling support.

    Note: Requires optional dependencies: pip install qrcode[pil] Pillow
    """

    def __init__(self):
        if not QR_AVAILABLE:
            raise ImportError("QR rendering requires: pip install qrcode[pil] Pillow")
        logger.info("QR renderer initialized")

    def render(self,
               data: str,
               style: Optional[QRStyle] = None,
               size: int = 300,
               error_correction: str = "M"):
        """
        Render QR code with styling.

        Args:
            data: Data to encode in QR
            style: QRStyle configuration (default: basic black/white)
            size: Output size in pixels
            error_correction: "L", "M", "Q", or "H"

        Returns:
            PIL Image object
        """
        if not QR_AVAILABLE:
            raise ImportError("QR rendering not available")

        if style is None:
            style = QRStyle()

        try:
            # Map error correction levels
            ec_map = {
                "L": qrcode.constants.ERROR_CORRECT_L,
                "M": qrcode.constants.ERROR_CORRECT_M,
                "Q": qrcode.constants.ERROR_CORRECT_Q,
                "H": qrcode.constants.ERROR_CORRECT_H
            }

            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,  # Auto-size
                error_correction=ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
                box_size=10,
                border=style.border,
            )

            qr.add_data(data)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(
                fill_color=style.module_color,
                back_color=style.background_color
            )

            # Resize to requested size
            if hasattr(img, 'resize') and hasattr(Image, 'Resampling'):
                img = img.resize((size, size), Image.Resampling.LANCZOS)
            elif hasattr(img, 'resize'):
                # Fallback for older PIL versions
                img = img.resize((size, size))

            logger.debug(f"QR rendered: {size}x{size}, EC={error_correction}")
            return img

        except Exception as e:
            logger.error(f"QR rendering failed: {e}")
            raise

    def save(self, img, path: str, format: str = "PNG"):
        """Save QR image to file."""
        try:
            if hasattr(img, 'save'):
                img.save(path, format=format)
                logger.info(f"QR saved to {path}")
            else:
                raise ValueError("Invalid image object")
        except Exception as e:
            logger.error(f"Failed to save QR: {e}")
            raise

    def to_bytes(self, img, format: str = "PNG") -> bytes:
        """Convert QR image to bytes."""
        try:
            if not hasattr(img, 'save'):
                raise ValueError("Invalid image object")
            buffer = BytesIO()
            img.save(buffer, format=format)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Failed to convert QR to bytes: {e}")
            raise

    def estimate_scannability(self, data_length: int, error_correction: str = "M") -> dict:
        """
        Estimate QR scannability for given data length.
        """
        # Rough capacity estimates by error correction level
        capacity_map = {
            "L": 2953,  # Low - 7% recovery
            "M": 2331,  # Medium - 15% recovery  
            "Q": 1663,  # Quartile - 25% recovery
            "H": 1273   # High - 30% recovery
        }

        max_capacity = capacity_map.get(error_correction, capacity_map["M"])
        utilization = data_length / max_capacity if max_capacity > 0 else 1.0

        if utilization <= 0.6:
            assessment = "excellent"
        elif utilization <= 0.8:
            assessment = "good"
        elif utilization <= 0.95:
            assessment = "marginal"
        else:
            assessment = "poor"

        return {
            "data_length": data_length,
            "max_capacity": max_capacity,
            "utilization": utilization,
            "assessment": assessment,
            "recommended_ec": error_correction if utilization <= 0.8 else "H"
        }

# Convenience function to check if QR rendering is available
def is_qr_rendering_available() -> bool:
    """Check if QR rendering dependencies are available."""
    return QR_AVAILABLE
