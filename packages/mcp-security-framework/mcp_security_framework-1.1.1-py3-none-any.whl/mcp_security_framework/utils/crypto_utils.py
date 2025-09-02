"""
Cryptographic Utilities Module

This module provides comprehensive cryptographic utilities for the
MCP Security Framework. It includes functions for hashing, key generation,
signing, verification, and JWT operations.

Key Features:
    - Secure hash functions (SHA-256, SHA-512)
    - Key generation utilities
    - Digital signature creation and verification
    - JWT token creation and validation
    - Password hashing and verification
    - Random data generation

Functions:
    hash_password: Hash password with salt
    verify_password: Verify password against hash
    generate_random_bytes: Generate random bytes
    generate_api_key: Generate secure API key
    create_jwt_token: Create JWT token
    verify_jwt_token: Verify JWT token
    hash_data: Hash data with specified algorithm
    sign_data: Sign data with private key
    verify_signature: Verify signature with public key

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Union

import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoError(Exception):
    """Raised when cryptographic operations fail."""

    def __init__(self, message: str, error_code: int = -32001):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    """
    Hash password with salt using PBKDF2.

    Args:
        password: Plain text password to hash
        salt: Optional salt. If None, generates random salt

    Returns:
        Dictionary containing hash and salt

    Raises:
        CryptoError: If password is empty or hashing fails
    """
    if not password or not password.strip():
        raise CryptoError("Password cannot be empty")

    try:
        # Generate salt if not provided
        if salt is None:
            salt = secrets.token_hex(16)

        # Convert password and salt to bytes
        password_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")

        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
        )

        # Generate hash
        key = kdf.derive(password_bytes)
        hash_hex = key.hex()

        return {"hash": hash_hex, "salt": salt}
    except Exception as e:
        raise CryptoError(f"Password hashing failed: {str(e)}")


def verify_password(password: str, hash_value: str, salt: str) -> bool:
    """
    Verify password against stored hash and salt.

    Args:
        password: Plain text password to verify
        hash_value: Stored hash value
        salt: Stored salt value

    Returns:
        True if password matches, False otherwise

    Raises:
        CryptoError: If verification fails
    """
    try:
        # Hash the provided password with the stored salt
        result = hash_password(password, salt)
        return result["hash"] == hash_value
    except Exception as e:
        raise CryptoError(f"Password verification failed: {str(e)}")


def generate_random_bytes(length: int = 32) -> bytes:
    """
    Generate cryptographically secure random bytes.

    Args:
        length: Number of bytes to generate

    Returns:
        Random bytes

    Raises:
        CryptoError: If length is invalid or generation fails
    """
    if length <= 0:
        raise CryptoError("Length must be positive")

    try:
        return secrets.token_bytes(length)
    except Exception as e:
        raise CryptoError(f"Random bytes generation failed: {str(e)}")


def generate_api_key(length: int = 32) -> str:
    """
    Generate secure API key.

    Args:
        length: Length of API key in bytes

    Returns:
        Base64 encoded API key

    Raises:
        CryptoError: If generation fails
    """
    try:
        random_bytes = generate_random_bytes(length)
        return base64.urlsafe_b64encode(random_bytes).decode("utf-8").rstrip("=")
    except Exception as e:
        raise CryptoError(f"API key generation failed: {str(e)}")


def hash_data(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """
    Hash data with specified algorithm.

    Args:
        data: Data to hash
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        Hexadecimal hash string

    Raises:
        CryptoError: If algorithm is unsupported or hashing fails
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    try:
        if algorithm.lower() == "sha256":
            hash_obj = hashlib.sha256(data)
        elif algorithm.lower() == "sha512":
            hash_obj = hashlib.sha512(data)
        elif algorithm.lower() == "md5":
            hash_obj = hashlib.md5(data)
        else:
            raise CryptoError(f"Unsupported hash algorithm: {algorithm}")

        return hash_obj.hexdigest()
    except Exception as e:
        raise CryptoError(f"Data hashing failed: {str(e)}")


def create_jwt_token(
    payload: Dict,
    secret: str,
    algorithm: str = "HS256",
    expires_in: Optional[int] = None,
) -> str:
    """
    Create JWT token.

    Args:
        payload: Token payload data
        secret: Secret key for signing
        algorithm: JWT algorithm (HS256, HS512, RS256)
        expires_in: Token expiration time in seconds

    Returns:
        JWT token string

    Raises:
        CryptoError: If token creation fails
    """
    try:
        # Add expiration if specified
        if expires_in:
            payload["exp"] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Add issued at time
        payload["iat"] = datetime.now(timezone.utc)

        return jwt.encode(payload, secret, algorithm=algorithm)
    except Exception as e:
        raise CryptoError(f"JWT token creation failed: {str(e)}")


def verify_jwt_token(
    token: str, secret: str, algorithms: Optional[list] = None
) -> Dict:
    """
    Verify JWT token.

    Args:
        token: JWT token to verify
        secret: Secret key for verification
        algorithms: List of allowed algorithms

    Returns:
        Decoded token payload

    Raises:
        CryptoError: If token verification fails
    """
    if algorithms is None:
        algorithms = ["HS256", "HS512"]

    try:
        payload = jwt.decode(token, secret, algorithms=algorithms)
        return payload
    except jwt.ExpiredSignatureError:
        raise CryptoError("JWT token has expired")
    except jwt.InvalidTokenError as e:
        raise CryptoError(f"Invalid JWT token: {str(e)}")
    except Exception as e:
        raise CryptoError(f"JWT token verification failed: {str(e)}")


def generate_rsa_key_pair(key_size: int = 2048) -> Dict[str, str]:
    """
    Generate RSA key pair.

    Args:
        key_size: Key size in bits (2048, 4096)

    Returns:
        Dictionary containing private and public keys in PEM format

    Raises:
        CryptoError: If key generation fails
    """
    if key_size not in [2048, 4096]:
        raise CryptoError("Key size must be 2048 or 4096 bits")

    try:
        # Generate private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

        # Get public key
        public_key = private_key.public_key()

        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return {
            "private_key": private_pem.decode("utf-8"),
            "public_key": public_pem.decode("utf-8"),
        }
    except Exception as e:
        raise CryptoError(f"RSA key pair generation failed: {str(e)}")


def sign_data(data: Union[str, bytes], private_key_pem: str) -> str:
    """
    Sign data with private key.

    Args:
        data: Data to sign
        private_key_pem: Private key in PEM format

    Returns:
        Base64 encoded signature

    Raises:
        CryptoError: If signing fails
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    try:
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"), password=None
        )

        # Sign data
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        return base64.b64encode(signature).decode("utf-8")
    except Exception as e:
        raise CryptoError(f"Data signing failed: {str(e)}")


def verify_signature(
    data: Union[str, bytes], signature: str, public_key_pem: str
) -> bool:
    """
    Verify signature with public key.

    Args:
        data: Original data
        signature: Base64 encoded signature
        public_key_pem: Public key in PEM format

    Returns:
        True if signature is valid, False otherwise

    Raises:
        CryptoError: If verification fails
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    try:
        # Load public key
        public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))

        # Decode signature
        signature_bytes = base64.b64decode(signature)

        # Verify signature
        public_key.verify(
            signature_bytes,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        return True
    except Exception:
        return False


def generate_hmac(data: Union[str, bytes], key: Union[str, bytes]) -> str:
    """
    Generate HMAC for data.

    Args:
        data: Data to hash
        key: HMAC key

    Returns:
        Hexadecimal HMAC string

    Raises:
        CryptoError: If HMAC generation fails
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if isinstance(key, str):
        key = key.encode("utf-8")

    try:
        hmac_obj = hmac.new(key, data, hashlib.sha256)
        return hmac_obj.hexdigest()
    except Exception as e:
        raise CryptoError(f"HMAC generation failed: {str(e)}")


def verify_hmac(
    data: Union[str, bytes], key: Union[str, bytes], expected_hmac: str
) -> bool:
    """
    Verify HMAC for data.

    Args:
        data: Original data
        key: HMAC key
        expected_hmac: Expected HMAC value

    Returns:
        True if HMAC matches, False otherwise
    """
    try:
        actual_hmac = generate_hmac(data, key)
        return hmac.compare_digest(actual_hmac, expected_hmac)
    except Exception:
        return False


def generate_secure_token(length: int = 32) -> str:
    """
    Generate secure random token.

    Args:
        length: Length of token in bytes

    Returns:
        Hexadecimal token string

    Raises:
        CryptoError: If generation fails
    """
    try:
        random_bytes = generate_random_bytes(length)
        return random_bytes.hex()
    except Exception as e:
        raise CryptoError(f"Secure token generation failed: {str(e)}")


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if format is valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False

    # Check minimum length (at least 8 characters for flexibility)
    if len(api_key) < 8:
        return False

    # Check maximum length (reasonable limit)
    if len(api_key) > 256:
        return False

    # Check for valid characters (alphanumeric, hyphens, underscores)
    import re

    if not re.match(r"^[a-zA-Z0-9_-]+$", api_key):
        return False

    return True
