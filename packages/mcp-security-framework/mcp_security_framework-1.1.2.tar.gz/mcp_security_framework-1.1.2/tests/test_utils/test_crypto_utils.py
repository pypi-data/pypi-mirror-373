"""
Cryptographic Utilities Test Module

This module provides comprehensive unit tests for all cryptographic
utilities in the MCP Security Framework.

Test Classes:
    TestPasswordHashing: Tests for password hashing and verification
    TestRandomGeneration: Tests for random data generation
    TestJWTOperations: Tests for JWT token creation and verification
    TestDataHashing: Tests for data hashing functions
    TestDigitalSignatures: Tests for digital signature operations
    TestHMAC: Tests for HMAC generation and verification

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from unittest.mock import patch

import pytest

from mcp_security_framework.utils.crypto_utils import (
    CryptoError,
    create_jwt_token,
    generate_api_key,
    generate_hmac,
    generate_random_bytes,
    generate_rsa_key_pair,
    hash_data,
    hash_password,
    sign_data,
    verify_hmac,
    verify_jwt_token,
    verify_password,
    verify_signature,
)


class TestPasswordHashing:
    """Test suite for password hashing functions."""

    def test_hash_password_success(self):
        """Test successful password hashing."""
        password = "test_password_123"
        result = hash_password(password)

        assert "hash" in result
        assert "salt" in result
        assert isinstance(result["hash"], str)
        assert isinstance(result["salt"], str)
        assert len(result["hash"]) > 0
        assert len(result["salt"]) > 0

    def test_hash_password_with_salt(self):
        """Test password hashing with provided salt."""
        password = "test_password_123"
        salt = "test_salt_123"
        result = hash_password(password, salt)

        assert result["salt"] == salt
        assert result["hash"] != password

    def test_hash_password_empty_password(self):
        """Test password hashing with empty password."""
        with pytest.raises(CryptoError) as exc_info:
            hash_password("")

        assert "Password cannot be empty" in str(exc_info.value)

    def test_hash_password_none_password(self):
        """Test password hashing with None password."""
        with pytest.raises(CryptoError) as exc_info:
            hash_password(None)

        assert "Password cannot be empty" in str(exc_info.value)

    def test_hash_password_whitespace_only(self):
        """Test password hashing with whitespace-only password."""
        with pytest.raises(CryptoError) as exc_info:
            hash_password("   ")

        assert "Password cannot be empty" in str(exc_info.value)

    def test_hash_password_exception(self):
        """Test password hashing with exception."""
        # Test with invalid salt that will cause an exception
        with patch(
            "cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC.derive",
            side_effect=Exception("Test exception"),
        ):
            with pytest.raises(CryptoError) as exc_info:
                hash_password("password", "salt")

            assert "Password hashing failed" in str(exc_info.value)

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "test_password_123"
        hashed = hash_password(password)

        result = verify_password(password, hashed["hash"], hashed["salt"])
        assert result is True

    def test_verify_password_wrong_password(self):
        """Test password verification with wrong password."""
        password = "test_password_123"
        hashed = hash_password(password)

        result = verify_password("wrong_password", hashed["hash"], hashed["salt"])
        assert result is False

    def test_verify_password_wrong_salt(self):
        """Test password verification with wrong salt."""
        password = "test_password_123"
        hashed = hash_password(password)

        result = verify_password(password, hashed["hash"], "wrong_salt")
        assert result is False

    def test_verify_password_exception(self):
        """Test password verification with exception."""
        # Test with invalid hash that will cause an exception
        with patch(
            "mcp_security_framework.utils.crypto_utils.hash_password",
            side_effect=Exception("Test exception"),
        ):
            with pytest.raises(CryptoError) as exc_info:
                verify_password("password", "invalid_hash", "invalid_salt")

            assert "Password verification failed" in str(exc_info.value)


class TestRandomGeneration:
    """Test suite for random data generation."""

    def test_generate_random_bytes_success(self):
        """Test successful random bytes generation."""
        length = 32
        result = generate_random_bytes(length)

        assert isinstance(result, bytes)
        assert len(result) == length

    def test_generate_random_bytes_different_lengths(self):
        """Test random bytes generation with different lengths."""
        lengths = [16, 32, 64, 128]

        for length in lengths:
            result = generate_random_bytes(length)
            assert len(result) == length

    def test_generate_random_bytes_unique(self):
        """Test that generated random bytes are unique."""
        results = []
        for _ in range(10):
            result = generate_random_bytes(32)
            assert result not in results
            results.append(result)

    def test_generate_random_bytes_invalid_length(self):
        """Test random bytes generation with invalid length."""
        with pytest.raises(CryptoError) as exc_info:
            generate_random_bytes(0)

        assert "Length must be positive" in str(exc_info.value)

    def test_generate_random_bytes_negative_length(self):
        """Test random bytes generation with negative length."""
        with pytest.raises(CryptoError) as exc_info:
            generate_random_bytes(-1)

        assert "Length must be positive" in str(exc_info.value)

    def test_generate_api_key_success(self):
        """Test successful API key generation."""
        length = 32
        result = generate_api_key(length)

        assert isinstance(result, str)
        assert len(result) > 0
        # API key should be URL-safe base64
        assert "=" not in result
        assert "/" not in result
        assert "+" not in result

    def test_generate_api_key_different_lengths(self):
        """Test API key generation with different lengths."""
        lengths = [16, 32, 64]

        for length in lengths:
            result = generate_api_key(length)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_generate_api_key_invalid_length(self):
        """Test API key generation with invalid length."""
        with pytest.raises(CryptoError) as exc_info:
            generate_api_key(0)

        assert "Length must be positive" in str(exc_info.value)

    def test_generate_random_bytes_exception(self):
        """Test random bytes generation with exception."""
        # This is hard to trigger in practice, but we can test the exception path
        # by mocking secrets.token_bytes to raise an exception
        with patch("secrets.token_bytes", side_effect=Exception("Test exception")):
            with pytest.raises(CryptoError) as exc_info:
                generate_random_bytes(32)

            assert "Random bytes generation failed" in str(exc_info.value)


class TestJWTOperations:
    """Test suite for JWT operations."""

    def test_create_jwt_token_success(self):
        """Test successful JWT token creation."""
        payload = {"user_id": "123", "username": "testuser"}
        secret = "test_secret_key"

        token = create_jwt_token(payload, secret)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_with_expiry(self):
        """Test JWT token creation with expiry."""
        payload = {"user_id": "123"}
        secret = "test_secret_key"
        expires_in = 3600  # 1 hour

        token = create_jwt_token(payload, secret, expires_in=expires_in)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_with_algorithm(self):
        """Test JWT token creation with specific algorithm."""
        payload = {"user_id": "123"}
        secret = "test_secret_key"

        token = create_jwt_token(payload, secret, algorithm="HS512")

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_exception(self):
        """Test JWT token creation with exception."""
        # Test with invalid payload that will cause an exception
        with pytest.raises(CryptoError) as exc_info:
            create_jwt_token({"invalid": object()}, "secret")

        assert "JWT token creation failed" in str(exc_info.value)

    def test_verify_jwt_token_success(self):
        """Test successful JWT token verification."""
        payload = {"user_id": "123", "username": "testuser"}
        secret = "test_secret_key"

        token = create_jwt_token(payload, secret)
        decoded = verify_jwt_token(token, secret)

        assert decoded["user_id"] == "123"
        assert decoded["username"] == "testuser"
        assert "iat" in decoded

    def test_verify_jwt_token_invalid_token(self):
        """Test JWT token verification with invalid token."""
        secret = "test_secret_key"

        with pytest.raises(CryptoError) as exc_info:
            verify_jwt_token("invalid_token", secret)

        assert "Invalid JWT token" in str(exc_info.value)

    def test_verify_jwt_token_wrong_secret(self):
        """Test JWT token verification with wrong secret."""
        payload = {"user_id": "123"}
        secret = "test_secret_key"
        wrong_secret = "wrong_secret"

        token = create_jwt_token(payload, secret)

        with pytest.raises(CryptoError) as exc_info:
            verify_jwt_token(token, wrong_secret)

        assert "Invalid JWT token" in str(exc_info.value)

    def test_verify_jwt_token_expired(self):
        """Test JWT token verification with expired token."""
        payload = {"user_id": "123"}
        secret = "test_secret_key"
        expires_in = -1  # Expired immediately

        token = create_jwt_token(payload, secret, expires_in=expires_in)

        with pytest.raises(CryptoError) as exc_info:
            verify_jwt_token(token, secret)

        assert "JWT token has expired" in str(exc_info.value)

    def test_verify_jwt_token_with_custom_algorithms(self):
        """Test JWT token verification with custom algorithms."""
        payload = {"user_id": "123"}
        secret = "test_secret_key"

        token = create_jwt_token(payload, secret)
        decoded = verify_jwt_token(token, secret, algorithms=["HS256", "HS512"])

        assert decoded["user_id"] == "123"

    def test_verify_jwt_token_exception(self):
        """Test JWT token verification with exception."""
        # Test with invalid token that will cause an exception
        with pytest.raises(CryptoError) as exc_info:
            verify_jwt_token("invalid_token", "secret")

        assert "Invalid JWT token" in str(exc_info.value)


class TestDataHashing:
    """Test suite for data hashing functions."""

    def test_hash_data_sha256(self):
        """Test data hashing with SHA-256."""
        data = "test_data"
        result = hash_data(data, "sha256")

        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 produces 64 hex characters

    def test_hash_data_sha512(self):
        """Test data hashing with SHA-512."""
        data = "test_data"
        result = hash_data(data, "sha512")

        assert isinstance(result, str)
        assert len(result) == 128  # SHA-512 produces 128 hex characters

    def test_hash_data_md5(self):
        """Test data hashing with MD5."""
        data = "test_data"
        result = hash_data(data, "md5")

        assert isinstance(result, str)
        assert len(result) == 32  # MD5 produces 32 hex characters

    def test_hash_data_bytes_input(self):
        """Test data hashing with bytes input."""
        data = b"test_data"
        result = hash_data(data, "sha256")

        assert isinstance(result, str)
        assert len(result) == 64

    def test_hash_data_unsupported_algorithm(self):
        """Test data hashing with unsupported algorithm."""
        data = "test_data"

        with pytest.raises(CryptoError) as exc_info:
            hash_data(data, "unsupported")

        assert "Unsupported hash algorithm" in str(exc_info.value)

    def test_hash_data_consistent(self):
        """Test that hashing the same data produces consistent results."""
        data = "test_data"
        result1 = hash_data(data, "sha256")
        result2 = hash_data(data, "sha256")

        assert result1 == result2

    def test_hash_data_case_insensitive_algorithm(self):
        """Test data hashing with case insensitive algorithm names."""
        data = "test_data"
        result1 = hash_data(data, "SHA256")
        result2 = hash_data(data, "sha256")

        assert result1 == result2


class TestDigitalSignatures:
    """Test suite for digital signature operations."""

    def test_generate_rsa_key_pair_success(self):
        """Test successful RSA key pair generation."""
        result = generate_rsa_key_pair(2048)

        assert "private_key" in result
        assert "public_key" in result
        assert isinstance(result["private_key"], str)
        assert isinstance(result["public_key"], str)
        assert "-----BEGIN PRIVATE KEY-----" in result["private_key"]
        assert "-----BEGIN PUBLIC KEY-----" in result["public_key"]

    def test_generate_rsa_key_pair_4096(self):
        """Test RSA key pair generation with 4096 bits."""
        result = generate_rsa_key_pair(4096)

        assert "private_key" in result
        assert "public_key" in result

    def test_generate_rsa_key_pair_invalid_size(self):
        """Test RSA key pair generation with invalid key size."""
        with pytest.raises(CryptoError) as exc_info:
            generate_rsa_key_pair(1024)

        assert "Key size must be 2048 or 4096 bits" in str(exc_info.value)

    def test_generate_rsa_key_pair_another_invalid_size(self):
        """Test RSA key pair generation with another invalid key size."""
        with pytest.raises(CryptoError) as exc_info:
            generate_rsa_key_pair(3072)

        assert "Key size must be 2048 or 4096 bits" in str(exc_info.value)

    def test_generate_rsa_key_pair_exception(self):
        """Test RSA key pair generation with exception."""
        # This is hard to trigger in practice, but we can test the exception path
        # by mocking rsa.generate_private_key to raise an exception
        with patch(
            "cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key",
            side_effect=Exception("Test exception"),
        ):
            with pytest.raises(CryptoError) as exc_info:
                generate_rsa_key_pair(2048)

            assert "RSA key pair generation failed" in str(exc_info.value)

    def test_sign_data_success(self):
        """Test successful data signing."""
        key_pair = generate_rsa_key_pair(2048)
        data = "test_data_to_sign"

        signature = sign_data(data, key_pair["private_key"])

        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_sign_data_bytes_input(self):
        """Test data signing with bytes input."""
        key_pair = generate_rsa_key_pair(2048)
        data = b"test_data_to_sign"

        signature = sign_data(data, key_pair["private_key"])

        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_sign_data_exception(self):
        """Test data signing with exception."""
        # Test with invalid private key that will cause an exception
        with pytest.raises(CryptoError) as exc_info:
            sign_data("test_data", "invalid_private_key")

        assert "Data signing failed" in str(exc_info.value)

    def test_verify_signature_success(self):
        """Test successful signature verification."""
        key_pair = generate_rsa_key_pair(2048)
        data = "test_data_to_sign"

        signature = sign_data(data, key_pair["private_key"])
        result = verify_signature(data, signature, key_pair["public_key"])

        assert result is True

    def test_verify_signature_wrong_data(self):
        """Test signature verification with wrong data."""
        key_pair = generate_rsa_key_pair(2048)
        data = "test_data_to_sign"
        wrong_data = "wrong_data"

        signature = sign_data(data, key_pair["private_key"])
        result = verify_signature(wrong_data, signature, key_pair["public_key"])

        assert result is False

    def test_verify_signature_wrong_signature(self):
        """Test signature verification with wrong signature."""
        key_pair = generate_rsa_key_pair(2048)
        data = "test_data_to_sign"

        result = verify_signature(data, "wrong_signature", key_pair["public_key"])

        assert result is False

    def test_verify_signature_bytes_input(self):
        """Test signature verification with bytes input."""
        key_pair = generate_rsa_key_pair(2048)
        data = b"test_data_to_sign"

        signature = sign_data(data, key_pair["private_key"])
        result = verify_signature(data, signature, key_pair["public_key"])

        assert result is True


class TestHMAC:
    """Test suite for HMAC operations."""

    def test_generate_hmac_success(self):
        """Test successful HMAC generation."""
        data = "test_data"
        key = "test_key"

        hmac_value = generate_hmac(data, key)

        assert isinstance(hmac_value, str)
        assert len(hmac_value) == 64  # SHA-256 HMAC produces 64 hex characters

    def test_generate_hmac_bytes_input(self):
        """Test HMAC generation with bytes input."""
        data = b"test_data"
        key = b"test_key"

        hmac_value = generate_hmac(data, key)

        assert isinstance(hmac_value, str)
        assert len(hmac_value) == 64

    def test_generate_hmac_mixed_input(self):
        """Test HMAC generation with mixed string/bytes input."""
        data = "test_data"
        key = b"test_key"

        hmac_value = generate_hmac(data, key)

        assert isinstance(hmac_value, str)
        assert len(hmac_value) == 64

    def test_verify_hmac_success(self):
        """Test successful HMAC verification."""
        data = "test_data"
        key = "test_key"

        hmac_value = generate_hmac(data, key)
        result = verify_hmac(data, key, hmac_value)

        assert result is True

    def test_verify_hmac_wrong_data(self):
        """Test HMAC verification with wrong data."""
        data = "test_data"
        wrong_data = "wrong_data"
        key = "test_key"

        hmac_value = generate_hmac(data, key)
        result = verify_hmac(wrong_data, key, hmac_value)

        assert result is False

    def test_verify_hmac_wrong_key(self):
        """Test HMAC verification with wrong key."""
        data = "test_data"
        key = "test_key"
        wrong_key = "wrong_key"

        hmac_value = generate_hmac(data, key)
        result = verify_hmac(data, wrong_key, hmac_value)

        assert result is False

    def test_verify_hmac_wrong_hmac(self):
        """Test HMAC verification with wrong HMAC value."""
        data = "test_data"
        key = "test_key"

        result = verify_hmac(data, key, "wrong_hmac")

        assert result is False

    def test_verify_hmac_bytes_input(self):
        """Test HMAC verification with bytes input."""
        data = b"test_data"
        key = b"test_key"

        hmac_value = generate_hmac(data, key)
        result = verify_hmac(data, key, hmac_value)

        assert result is True

    def test_generate_hmac_exception(self):
        """Test HMAC generation with exception."""
        # This is hard to trigger in practice, but we can test the exception path
        # by mocking hmac.new to raise an exception
        with patch("hmac.new", side_effect=Exception("Test exception")):
            with pytest.raises(CryptoError) as exc_info:
                generate_hmac("test_data", "test_key")

            assert "HMAC generation failed" in str(exc_info.value)

    def test_verify_hmac_exception(self):
        """Test HMAC verification with exception."""
        # Test with invalid data that will cause an exception in generate_hmac
        with patch(
            "mcp_security_framework.utils.crypto_utils.generate_hmac",
            side_effect=Exception("Test exception"),
        ):
            result = verify_hmac("test_data", "test_key", "expected_hmac")
            assert result is False
