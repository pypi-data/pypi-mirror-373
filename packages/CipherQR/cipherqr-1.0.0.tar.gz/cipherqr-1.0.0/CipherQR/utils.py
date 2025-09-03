"""
Utility functions for CipherQR package.
"""

import zlib
import re
import logging
from typing import Set

logger = logging.getLogger(__name__)

def validate_ttl(ttl_seconds: int) -> bool:
    """Validate TTL is within reasonable bounds."""
    return isinstance(ttl_seconds, int) and 1 <= ttl_seconds <= 86400 * 7  # 1 second to 1 week

def compress_if_beneficial(data: bytes, min_compression_ratio: float = 0.9) -> bytes:
    """
    Compress data if it reduces size significantly.

    Args:
        data: Input data
        min_compression_ratio: Only compress if result is < ratio * original_size

    Returns:
        Compressed data if beneficial, otherwise original data
    """
    if len(data) < 100:  # Don't compress very small data
        return data

    try:
        compressed = zlib.compress(data, level=6)

        if len(compressed) < len(data) * min_compression_ratio:
            logger.debug(f"Compression: {len(data)} -> {len(compressed)} bytes ({len(compressed)/len(data)*100:.1f}%)")
            return compressed
        else:
            logger.debug("Compression not beneficial")
            return data
    except Exception as e:
        logger.warning(f"Compression failed: {e}")
        return data

def decompress_if_compressed(data: bytes) -> bytes:
    """
    Attempt to decompress data, return original if not compressed.

    Args:
        data: Potentially compressed data

    Returns:
        Decompressed data or original data if not compressed
    """
    try:
        # Try to decompress
        decompressed = zlib.decompress(data)
        logger.debug(f"Decompression: {len(data)} -> {len(decompressed)} bytes")
        return decompressed
    except zlib.error:
        # Not compressed or corrupted
        return data
    except Exception as e:
        logger.warning(f"Decompression failed: {e}")
        return data

def validate_route(route: str, allowed_patterns: Set[str]) -> bool:
    """
    Validate route against allowed patterns.

    Args:
        route: Route string to validate
        allowed_patterns: Set of allowed route patterns (support regex)

    Returns:
        True if route is allowed
    """
    if not isinstance(route, str) or not allowed_patterns:
        return False

    for pattern in allowed_patterns:
        try:
            if re.match(pattern, route):
                return True
        except re.error:
            # Treat as literal string if regex fails
            if pattern == route:
                return True

    return False

def safe_encode_base64url(data: bytes) -> str:
    """Safely encode bytes to base64url string."""
    import base64
    try:
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')
    except Exception as e:
        raise ValueError(f"Failed to encode base64url: {e}") from e

def safe_decode_base64url(data: str) -> bytes:
    """Safely decode base64url string to bytes."""
    import base64
    try:
        padding = '=' * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)
    except Exception as e:
        raise ValueError(f"Failed to decode base64url: {e}") from e
