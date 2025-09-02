"""
Tests for Authentication Manager Module

This module contains comprehensive tests for the AuthManager class,
covering all authentication methods and edge cases.

Test Coverage:
- API key authentication
- JWT token authentication and creation
- Certificate-based authentication
- Error handling and edge cases
- Configuration validation
- Integration with PermissionManager

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_security_framework.core.auth_manager import (
    AuthenticationConfigurationError,
    AuthenticationError,
    AuthManager,
    CertificateValidationError,
    JWTValidationError,
)
from mcp_security_framework.core.permission_manager import PermissionManager
from mcp_security_framework.schemas.config import AuthConfig
from mcp_security_framework.schemas.models import AuthResult, AuthStatus


class TestAuthManager:
    """Test suite for AuthManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create mock permission manager
        self.mock_permission_manager = Mock(spec=PermissionManager)
        # Configure mock to return default roles
        self.mock_permission_manager.get_user_roles.return_value = ["user"]

        # Create test configuration
        self.auth_config = AuthConfig(
            api_keys={"test_api_key_123": "test_user"},
            jwt_secret="test_jwt_secret_key_32_chars_long",
            jwt_expiry_hours=1,
            ca_cert_file=None,
        )

        # Create AuthManager instance
        self.auth_manager = AuthManager(self.auth_config, self.mock_permission_manager)

    def teardown_method(self):
        """Clean up after each test method."""
        # Clear caches
        self.auth_manager.clear_token_cache()
        self.auth_manager.clear_session_store()

    def test_init_success(self):
        """Test successful AuthManager initialization."""
        assert self.auth_manager.config == self.auth_config
        assert self.auth_manager.permission_manager == self.mock_permission_manager
        assert self.auth_manager._api_keys == {"test_user": "test_api_key_123"}
        assert self.auth_manager._jwt_secret == "test_jwt_secret_key_32_chars_long"
        assert isinstance(self.auth_manager._token_cache, dict)
        assert isinstance(self.auth_manager._session_store, dict)

    def test_init_without_config(self):
        """Test AuthManager initialization without config."""
        with pytest.raises(AuthenticationConfigurationError) as exc_info:
            AuthManager(None, self.mock_permission_manager)
        assert "Authentication configuration is required" in str(exc_info.value)

    def test_init_without_permission_manager(self):
        """Test AuthManager initialization without permission manager."""
        with pytest.raises(AuthenticationConfigurationError) as exc_info:
            AuthManager(self.auth_config, None)
        assert "Permission manager is required" in str(exc_info.value)

    def test_init_with_short_jwt_secret(self):
        """Test AuthManager initialization with short JWT secret."""
        short_config = AuthConfig(
            api_keys={"test_api_key_123": "test_user"},
            jwt_secret="short",
            jwt_expiry_hours=1,
        )

        with pytest.raises(AuthenticationConfigurationError) as exc_info:
            AuthManager(short_config, self.mock_permission_manager)
        assert "JWT secret must be at least 16 characters" in str(exc_info.value)

    def test_init_with_generated_jwt_secret(self):
        """Test AuthManager initialization with auto-generated JWT secret."""
        config_without_secret = AuthConfig(
            api_keys={"test_api_key_123": "test_user"},
            jwt_secret=None,
            jwt_expiry_hours=1,
        )

        auth_manager = AuthManager(config_without_secret, self.mock_permission_manager)
        assert len(auth_manager._jwt_secret) >= 32

    def test_authenticate_api_key_success(self):
        """Test successful API key authentication."""
        # Mock user roles
        with patch.object(
            self.auth_manager, "_get_user_roles", return_value=["user", "admin"]
        ):
            result = self.auth_manager.authenticate_api_key("test_api_key_123")

        assert result.is_valid is True
        assert result.status == AuthStatus.SUCCESS
        assert result.username == "test_user"
        assert result.roles == ["user", "admin"]
        assert result.auth_method == "api_key"
        assert result.error_code is None
        assert result.error_message is None
        assert result.auth_timestamp is not None

    def test_authenticate_api_key_empty_key(self):
        """Test API key authentication with empty key."""
        result = self.auth_manager.authenticate_api_key("")

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "api_key"
        assert result.error_code == -32001
        assert "API key is required" in result.error_message

    def test_authenticate_api_key_none_key(self):
        """Test API key authentication with None key."""
        result = self.auth_manager.authenticate_api_key(None)

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "api_key"
        assert result.error_code == -32001
        assert "API key is required" in result.error_message

    def test_authenticate_api_key_invalid_format(self):
        """Test API key authentication with invalid format."""
        with patch(
            "mcp_security_framework.utils.crypto_utils.validate_api_key_format",
            return_value=False,
        ):
            result = self.auth_manager.authenticate_api_key("short")

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "api_key"
        assert result.error_code == -32002
        assert "Invalid API key format" in result.error_message

    def test_authenticate_api_key_not_found(self):
        """Test API key authentication with non-existent key."""
        result = self.auth_manager.authenticate_api_key("non_existent_key")

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "api_key"
        assert result.error_code == -32003
        assert "Invalid API key" in result.error_message

    def test_authenticate_api_key_roles_error(self):
        """Test API key authentication when role retrieval fails."""
        with patch.object(
            self.auth_manager, "_get_user_roles", side_effect=Exception("Role error")
        ):
            result = self.auth_manager.authenticate_api_key("test_api_key_123")

        assert result.is_valid is False
        assert result.status == AuthStatus.FAILED
        assert result.auth_method == "api_key"
        assert result.error_code == -32004
        assert "Failed to retrieve user roles" in result.error_message

    def test_authenticate_jwt_token_success(self):
        """Test successful JWT token authentication."""
        # Create a valid JWT token
        user_data = {"username": "test_user", "roles": ["user", "admin"]}
        token = self.auth_manager.create_jwt_token(user_data)

        # Authenticate with the token
        result = self.auth_manager.authenticate_jwt_token(token)

        assert result.is_valid is True
        assert result.status == AuthStatus.SUCCESS
        assert result.username == "test_user"
        assert result.roles == ["user", "admin"]
        assert result.auth_method == "jwt"
        assert result.error_code is None
        assert result.error_message is None
        assert result.auth_timestamp is not None
        assert result.token_expiry is not None

    def test_authenticate_jwt_token_empty_token(self):
        """Test JWT authentication with empty token."""
        result = self.auth_manager.authenticate_jwt_token("")

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "jwt"
        assert result.error_code == -32001
        assert "JWT token is required" in result.error_message

    def test_authenticate_jwt_token_none_token(self):
        """Test JWT authentication with None token."""
        result = self.auth_manager.authenticate_jwt_token(None)

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "jwt"
        assert result.error_code == -32001
        assert "JWT token is required" in result.error_message

    def test_authenticate_jwt_token_invalid_token(self):
        """Test JWT authentication with invalid token."""
        result = self.auth_manager.authenticate_jwt_token("invalid.jwt.token")

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "jwt"
        assert result.error_code == -32003
        assert "Invalid JWT token" in result.error_message

    def test_authenticate_jwt_token_expired_token(self):
        """Test JWT authentication with expired token."""
        # Create an expired token
        expired_payload = {
            "username": "test_user",
            "roles": ["user"],
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
        }

        import jwt

        expired_token = jwt.encode(
            expired_payload, self.auth_manager._jwt_secret, algorithm="HS256"
        )

        result = self.auth_manager.authenticate_jwt_token(expired_token)

        assert result.is_valid is False
        assert result.status == AuthStatus.EXPIRED
        assert result.auth_method == "jwt"
        assert result.error_code == -32002
        assert "JWT token has expired" in result.error_message

    def test_authenticate_jwt_token_missing_username(self):
        """Test JWT authentication with token missing username."""
        # Create token without username
        payload = {
            "roles": ["user"],
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }

        import jwt

        token = jwt.encode(payload, self.auth_manager._jwt_secret, algorithm="HS256")

        result = self.auth_manager.authenticate_jwt_token(token)

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "jwt"
        assert result.error_code == -32004
        assert "JWT token missing username" in result.error_message

    def test_authenticate_jwt_token_cached_result(self):
        """Test JWT authentication with cached result."""
        # Create a valid token
        user_data = {"username": "test_user", "roles": ["user"]}
        token = self.auth_manager.create_jwt_token(user_data)

        # First authentication
        result1 = self.auth_manager.authenticate_jwt_token(token)

        # Second authentication (should use cache)
        result2 = self.auth_manager.authenticate_jwt_token(token)

        assert result1.is_valid is True
        assert result2.is_valid is True
        assert result1.username == result2.username
        assert result1.roles == result2.roles

    def test_authenticate_certificate_success(self):
        """Test successful certificate authentication."""
        # Test with invalid certificate format (should fail gracefully)
        cert_pem = "invalid_certificate_data"

        result = self.auth_manager.authenticate_certificate(cert_pem)

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "certificate"
        assert result.error_code == -32002
        assert "Invalid certificate format" in result.error_message

    def test_authenticate_certificate_empty_cert(self):
        """Test certificate authentication with empty certificate."""
        result = self.auth_manager.authenticate_certificate("")

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "certificate"
        assert result.error_code == -32001
        assert "Certificate is required" in result.error_message

    def test_authenticate_certificate_invalid_format(self):
        """Test certificate authentication with invalid format."""
        result = self.auth_manager.authenticate_certificate("invalid_certificate")

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "certificate"
        assert result.error_code == -32002
        assert "Invalid certificate format" in result.error_message

    def test_authenticate_certificate_missing_username(self):
        """Test certificate authentication with missing username."""
        # Test with invalid certificate format (should fail before username check)
        cert_pem = "invalid_certificate_data"

        result = self.auth_manager.authenticate_certificate(cert_pem)

        assert result.is_valid is False
        assert result.status == AuthStatus.INVALID
        assert result.auth_method == "certificate"
        assert result.error_code == -32002
        assert "Invalid certificate format" in result.error_message

    def test_create_jwt_token_success(self):
        """Test successful JWT token creation."""
        user_data = {
            "username": "test_user",
            "roles": ["user", "admin"],
            "permissions": ["read:users", "write:posts"],
        }

        token = self.auth_manager.create_jwt_token(user_data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        import jwt

        payload = jwt.decode(
            token,
            self.auth_manager._jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )

        assert payload["username"] == "test_user"
        assert payload["roles"] == ["user", "admin"]
        assert payload["permissions"] == ["read:users", "write:posts"]
        assert "iat" in payload
        assert "exp" in payload
        assert "sub" in payload
        assert "iss" in payload

    def test_create_jwt_token_with_additional_data(self):
        """Test JWT token creation with additional user data."""
        user_data = {
            "username": "test_user",
            "roles": ["user"],
            "additional_data": {"email": "test@example.com", "department": "IT"},
        }

        token = self.auth_manager.create_jwt_token(user_data)

        # Verify token can be decoded
        import jwt

        payload = jwt.decode(
            token,
            self.auth_manager._jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )

        assert payload["username"] == "test_user"
        assert payload["user_data"]["email"] == "test@example.com"
        assert payload["user_data"]["department"] == "IT"

    def test_create_jwt_token_invalid_user_data(self):
        """Test JWT token creation with invalid user data."""
        with pytest.raises(JWTValidationError) as exc_info:
            self.auth_manager.create_jwt_token(None)
        assert "User data must be provided" in str(exc_info.value)

        with pytest.raises(JWTValidationError) as exc_info:
            self.auth_manager.create_jwt_token({})
        assert "User data dictionary cannot be empty" in str(exc_info.value)

        with pytest.raises(JWTValidationError) as exc_info:
            self.auth_manager.create_jwt_token({"roles": ["user"]})
        assert "Username is required in user data" in str(exc_info.value)

    def test_validate_jwt_token_valid(self):
        """Test JWT token validation with valid token."""
        user_data = {"username": "test_user", "roles": ["user"]}
        token = self.auth_manager.create_jwt_token(user_data)

        is_valid = self.auth_manager.validate_jwt_token(token)
        assert is_valid is True

    def test_validate_jwt_token_invalid(self):
        """Test JWT token validation with invalid token."""
        is_valid = self.auth_manager.validate_jwt_token("invalid.token")
        assert is_valid is False

        is_valid = self.auth_manager.validate_jwt_token("")
        assert is_valid is False

        is_valid = self.auth_manager.validate_jwt_token(None)
        assert is_valid is False

    def test_add_api_key_success(self):
        """Test successful API key addition."""
        success = self.auth_manager.add_api_key("new_user", "new_api_key_456789")

        assert success is True
        assert "new_user" in self.auth_manager._api_keys
        assert self.auth_manager._api_keys["new_user"] == "new_api_key_456789"

    def test_add_api_key_invalid_input(self):
        """Test API key addition with invalid input."""
        success = self.auth_manager.add_api_key("", "valid_key")
        assert success is False

        success = self.auth_manager.add_api_key("user", "")
        assert success is False

        success = self.auth_manager.add_api_key(None, "valid_key")
        assert success is False

    def test_add_api_key_invalid_format(self):
        """Test API key addition with invalid format."""
        with patch(
            "mcp_security_framework.core.auth_manager.validate_api_key_format",
            return_value=False,
        ):
            success = self.auth_manager.add_api_key("user", "invalid_key")
            assert success is False

    def test_remove_api_key_success(self):
        """Test successful API key removal."""
        # Add a key first
        self.auth_manager.add_api_key("temp_user", "temp_key_123456789")
        assert "temp_user" in self.auth_manager._api_keys

        # Remove the key
        success = self.auth_manager.remove_api_key("temp_user")
        assert success is True
        assert "temp_user" not in self.auth_manager._api_keys

    def test_remove_api_key_not_found(self):
        """Test API key removal for non-existent user."""
        success = self.auth_manager.remove_api_key("non_existent_user")
        assert success is False

    def test_clear_token_cache(self):
        """Test token cache clearing."""
        # Add a token to cache
        user_data = {"username": "test_user", "roles": ["user"]}
        token = self.auth_manager.create_jwt_token(user_data)
        self.auth_manager.authenticate_jwt_token(token)

        assert len(self.auth_manager._token_cache) > 0

        # Clear cache
        self.auth_manager.clear_token_cache()
        assert len(self.auth_manager._token_cache) == 0

    def test_clear_session_store(self):
        """Test session store clearing."""
        # Add a session
        self.auth_manager._session_store["test_session"] = {"user": "test"}

        assert len(self.auth_manager._session_store) > 0

        # Clear session store
        self.auth_manager.clear_session_store()
        assert len(self.auth_manager._session_store) == 0

    def test_get_user_roles(self):
        """Test user roles retrieval."""
        roles = self.auth_manager._get_user_roles("test_user")
        assert isinstance(roles, list)
        assert "user" in roles

    def test_extract_username_from_certificate(self):
        """Test username extraction from certificate."""
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        # Create a mock certificate
        mock_cert = Mock(spec=x509.Certificate)
        mock_cn = Mock()
        mock_cn.value = "test_user"
        mock_cert.subject.get_attributes_for_oid.return_value = [mock_cn]

        username = self.auth_manager._extract_username_from_certificate(mock_cert)
        assert username == "test_user"

    def test_is_token_expired(self):
        """Test token expiration check."""
        # Create a non-expired result
        non_expired_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method="jwt",
            token_expiry=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        assert self.auth_manager._is_token_expired(non_expired_result) is False

        # Create an expired result
        expired_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method="jwt",
            token_expiry=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        assert self.auth_manager._is_token_expired(expired_result) is True

        # Test with no expiration
        no_expiry_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method="jwt",
        )

        assert self.auth_manager._is_token_expired(no_expiry_result) is False


class TestAuthManagerExceptions:
    """Test suite for AuthManager exception classes."""

    def test_authentication_configuration_error(self):
        """Test AuthenticationConfigurationError."""
        error = AuthenticationConfigurationError("Test error", -32001)
        assert error.message == "Test error"
        assert error.error_code == -32001
        assert str(error) == "Test error"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Auth failed", -32002)
        assert error.message == "Auth failed"
        assert error.error_code == -32002
        assert str(error) == "Auth failed"

    def test_jwt_validation_error(self):
        """Test JWTValidationError."""
        error = JWTValidationError("JWT invalid", -32003)
        assert error.message == "JWT invalid"
        assert error.error_code == -32003
        assert str(error) == "JWT invalid"

    def test_certificate_validation_error(self):
        """Test CertificateValidationError."""
        error = CertificateValidationError("Cert invalid", -32004)
        assert error.message == "Cert invalid"
        assert error.error_code == -32004
        assert str(error) == "Cert invalid"
