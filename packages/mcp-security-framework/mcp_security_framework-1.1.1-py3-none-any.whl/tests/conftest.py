"""
Test Configuration and Fixtures

This module provides test configuration, fixtures, and mock objects
for the MCP Security Framework test suite.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    ValidationResult,
    ValidationStatus,
)


@pytest.fixture
def mock_security_manager():
    """
    Create a mock SecurityManager instance for testing.

    This fixture provides a properly configured mock SecurityManager
    that can be used in tests without conflicts with the real implementation.

    Returns:
        Mock: Mock SecurityManager instance
    """
    mock_manager = Mock(spec=SecurityManager)

    # Mock authentication methods
    def mock_authenticate_api_key(api_key: str) -> AuthResult:
        if api_key == "admin_key_123":
            return AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username="admin",
                roles=["admin"],
                auth_method=AuthMethod.API_KEY,
            )
        elif api_key == "user_key_456":
            return AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username="user",
                roles=["user"],
                auth_method=AuthMethod.API_KEY,
            )
        elif api_key == "readonly_key_789":
            return AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username="readonly",
                roles=["readonly"],
                auth_method=AuthMethod.API_KEY,
            )
        else:
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=-32002,
                error_message="Invalid API key",
            )

    def mock_authenticate_jwt_token(token: str) -> AuthResult:
        if token == "valid_jwt_token":
            return AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username="jwt_user",
                roles=["user"],
                auth_method=AuthMethod.JWT,
            )
        else:
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=-32003,
                error_message="Invalid JWT token",
            )

    def mock_check_permissions(
        user_roles: list, required_permissions: list
    ) -> ValidationResult:
        if "admin" in user_roles:
            return ValidationResult(is_valid=True, status=ValidationStatus.VALID)
        elif "user" in user_roles and "read" in required_permissions:
            return ValidationResult(is_valid=True, status=ValidationStatus.VALID)
        elif "readonly" in user_roles and "read" in required_permissions:
            return ValidationResult(is_valid=True, status=ValidationStatus.VALID)
        else:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                error_code=-32007,
                error_message="Insufficient permissions",
            )

    def mock_check_rate_limit(identifier: str) -> bool:
        # Simple rate limiting logic for testing
        if not hasattr(mock_manager, "_request_counts"):
            mock_manager._request_counts = {}

        if identifier not in mock_manager._request_counts:
            mock_manager._request_counts[identifier] = 0

        mock_manager._request_counts[identifier] += 1

        # Allow up to 100 requests per identifier
        return mock_manager._request_counts[identifier] <= 100

    # Assign mock methods
    mock_manager.authenticate_api_key = mock_authenticate_api_key
    mock_manager.authenticate_jwt_token = mock_authenticate_jwt_token
    mock_manager.check_permissions = mock_check_permissions
    mock_manager.check_rate_limit = mock_check_rate_limit

    # Mock other properties and methods
    mock_manager.is_authenticated = True
    mock_manager.user_roles = ["user"]
    mock_manager.effective_permissions = {"read", "write"}

    return mock_manager


@pytest.fixture
def mock_security_manager_class():
    """
    Create a mock SecurityManager class for testing.

    This fixture provides a mock class that can be used to patch
    SecurityManager imports in tests.

    Returns:
        Mock: Mock SecurityManager class
    """
    mock_class = Mock()
    mock_class.return_value = Mock(spec=SecurityManager)
    return mock_class


@pytest.fixture
def mock_certificate_manager():
    """
    Create a mock CertificateManager instance for testing.

    Returns:
        Mock: Mock CertificateManager instance
    """
    mock_manager = Mock()

    # Mock certificate validation
    mock_manager.validate_certificate_chain.return_value = True
    mock_manager.get_certificate_info.return_value = Mock(
        subject={"CN": "test.example.com"},
        issuer={"CN": "Test CA"},
        serial_number="123456789",
        not_before="2023-01-01",
        not_after="2024-01-01",
        key_size=2048,
        certificate_type="SERVER",
        subject_alt_names=["test.example.com"],
    )
    mock_manager.revoke_certificate.return_value = True

    return mock_manager


@pytest.fixture
def mock_ssl_manager():
    """
    Create a mock SSLManager instance for testing.

    Returns:
        Mock: Mock SSLManager instance
    """
    mock_manager = Mock()
    mock_manager.create_server_context.return_value = Mock()
    mock_manager.create_client_context.return_value = Mock()
    mock_manager.validate_certificate.return_value = True
    return mock_manager


@pytest.fixture
def test_config():
    """
    Create a test configuration for testing.

    Returns:
        Dict[str, Any]: Test configuration
    """
    return {
        "auth": {
            "enabled": True,
            "methods": ["api_key", "jwt"],
            "api_keys": {
                "admin_key_123": {
                    "username": "admin",
                    "roles": ["admin"],
                    "permissions": ["read", "write", "delete", "admin"],
                },
                "user_key_456": {
                    "username": "user",
                    "roles": ["user"],
                    "permissions": ["read", "write"],
                },
                "readonly_key_789": {
                    "username": "readonly",
                    "roles": ["readonly"],
                    "permissions": ["read"],
                },
            },
            "jwt": {
                "secret": "test_secret_key",
                "algorithm": "HS256",
                "expiry_hours": 24,
            },
        },
        "ssl": {
            "enabled": False,
            "cert_file": None,
            "key_file": None,
            "ca_cert_file": None,
            "verify_mode": "CERT_NONE",
            "min_version": "TLSv1.2",
        },
        "rate_limiting": {
            "enabled": True,
            "requests_per_minute": 100,
            "window_seconds": 60,
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }


@pytest.fixture
def temp_config_file(tmp_path, test_config):
    """
    Create a temporary configuration file for testing.

    Args:
        tmp_path: Pytest temporary directory fixture
        test_config: Test configuration fixture

    Returns:
        str: Path to temporary configuration file
    """
    import json
    import os

    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(test_config, f)

    return str(config_file)


# Patch decorators for common mocks
def patch_security_manager():
    """
    Create a patch decorator for SecurityManager.

    Returns:
        function: Patch decorator
    """
    return patch("mcp_security_framework.core.security_manager.SecurityManager")


def patch_certificate_manager():
    """
    Create a patch decorator for CertificateManager.

    Returns:
        function: Patch decorator
    """
    return patch("mcp_security_framework.core.cert_manager.CertificateManager")


def patch_ssl_manager():
    """
    Create a patch decorator for SSLManager.

    Returns:
        function: Patch decorator
    """
    return patch("mcp_security_framework.core.ssl_manager.SSLManager")
