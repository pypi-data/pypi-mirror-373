"""
Datetime Compatibility Module

This module provides compatibility functions for working with certificate
datetime fields across different versions of the cryptography library.

The module handles the transition from naive datetime fields to UTC-aware
fields introduced in cryptography>=42, ensuring backward compatibility with
older versions.

Key Features:
- Compatible datetime field access for certificates
- Automatic timezone normalization
- Backward compatibility with cryptography<42
- Forward compatibility with cryptography>=42

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from datetime import datetime, timezone
from typing import Optional

from cryptography.x509 import Certificate


def get_not_valid_before_utc(cert: Certificate) -> datetime:
    """
    Get certificate not_valid_before field in UTC timezone.

    This function provides compatibility across different cryptography
    versions:
    - For cryptography>=42: Returns cert.not_valid_before_utc directly
    - For cryptography<42: Returns cert.not_valid_before normalized to UTC

    Args:
        cert (Certificate): Certificate object from cryptography library

    Returns:
        datetime: UTC timezone-aware datetime representing certificate
        start date

    Example:
        >>> from cryptography import x509
        >>> cert = x509.load_pem_x509_certificate(cert_data)
        >>> start_date = get_not_valid_before_utc(cert)
        >>> print(f"Certificate valid from: {start_date}")
    """
    # Try to access the new UTC field first (cryptography>=42)
    if hasattr(cert, "not_valid_before_utc"):
        val = getattr(cert, "not_valid_before_utc")
        if val is not None:
            return val

    # Fall back to the old field and normalize to UTC (cryptography<42)
    v = cert.not_valid_before
    return v if v.tzinfo else v.replace(tzinfo=timezone.utc)


def get_not_valid_after_utc(cert: Certificate) -> datetime:
    """
    Get certificate not_valid_after field in UTC timezone.

    This function provides compatibility across different cryptography
    versions:
    - For cryptography>=42: Returns cert.not_valid_after_utc directly
    - For cryptography<42: Returns cert.not_valid_after normalized to UTC

    Args:
        cert (Certificate): Certificate object from cryptography library

    Returns:
        datetime: UTC timezone-aware datetime representing certificate
        expiry date

    Example:
        >>> from cryptography import x509
        >>> cert = x509.load_pem_x509_certificate(cert_data)
        >>> expiry_date = get_not_valid_after_utc(cert)
        >>> print(f"Certificate expires: {expiry_date}")
    """
    # Try to access the new UTC field first (cryptography>=42)
    if hasattr(cert, "not_valid_after_utc"):
        val = getattr(cert, "not_valid_after_utc")
        if val is not None:
            return val

    # Fall back to the old field and normalize to UTC (cryptography<42)
    v = cert.not_valid_after
    return v if v.tzinfo else v.replace(tzinfo=timezone.utc)


def is_cryptography_42_plus() -> bool:
    """
    Check if cryptography version is 42 or higher.

    This function checks if the current cryptography version supports
    the new UTC datetime fields (not_valid_before_utc, not_valid_after_utc).

    Returns:
        bool: True if cryptography>=42, False otherwise

    Example:
        >>> if is_cryptography_42_plus():
        ...     print("Using new UTC datetime fields")
        ... else:
        ...     print("Using legacy datetime fields with normalization")
    """
    try:
        import cryptography
        from packaging import version

        return version.parse(cryptography.__version__) >= version.parse("42.0.0")
    except (ImportError, AttributeError):
        # If we can't determine version, assume older version for safety
        return False
