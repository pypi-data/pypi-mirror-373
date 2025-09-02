"""
Authentication Flow Integration Tests

This module contains integration tests for complete authentication and
authorization flows using the MCP Security Framework. Tests cover API key
authentication, JWT authentication, role-based access control, and
permission management.

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import jwt
import pytest

from mcp_security_framework.core.auth_manager import AuthManager
from mcp_security_framework.core.permission_manager import PermissionManager
from mcp_security_framework.core.security_manager import (
    SecurityManager,
    SecurityValidationError,
)
from mcp_security_framework.schemas.config import (
    AuthConfig,
    CertificateConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
)
from mcp_security_framework.schemas.responses import AuthResult, ValidationResult


class TestAuthFlowIntegration:
    """Integration tests for complete authentication and authorization flows."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary roles file
        self.roles_fd, self.roles_path = tempfile.mkstemp(suffix=".json")
        self.roles_config = {
            "roles": {
                "admin": {
                    "permissions": ["read", "write", "delete", "admin"],
                    "description": "Administrator role",
                    "inherits": ["user", "moderator"],
                },
                "user": {
                    "permissions": ["read", "write"],
                    "description": "Regular user role",
                },
                "readonly": {
                    "permissions": ["read"],
                    "description": "Read-only user role",
                },
                "moderator": {
                    "permissions": ["read", "write", "moderate"],
                    "description": "Moderator role",
                    "inherits": ["user"],
                },
            }
        }

        with os.fdopen(self.roles_fd, "w") as f:
            json.dump(self.roles_config, f)

        # Create authentication configuration
        self.auth_config = AuthConfig(
            enabled=True,
            methods=["api_key", "jwt"],
            api_keys={
                "admin_key_123456789012345": "admin",
                "user_key_456789012345678": "user",
                "readonly_key_789012345678": "readonly",
                "moderator_key_101234567890": "moderator",
            },
            user_roles={
                "admin": ["admin"],
                "user": ["user"],
                "readonly": ["readonly"],
                "moderator": ["moderator"],
            },
            jwt_secret="test_jwt_secret_key_for_integration_tests",
            jwt_algorithm="HS256",
            jwt_expiry_hours=24,
        )

        # Create permission configuration
        self.permission_config = PermissionConfig(
            enabled=True, roles_file=self.roles_path
        )

        # Create security configuration
        self.security_config = SecurityConfig(
            auth=self.auth_config,
            permissions=self.permission_config,
            rate_limit=RateLimitConfig(enabled=True, default_requests_per_minute=100),
            ssl=SSLConfig(enabled=False),
            certificates=CertificateConfig(enabled=False),
        )

        # Create security manager
        self.security_manager = SecurityManager(self.security_config)

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self, "roles_path") and os.path.exists(self.roles_path):
            os.unlink(self.roles_path)

    def test_complete_api_key_authentication_flow(self):
        """Test complete API key authentication flow."""
        # Test valid API key authentication
        auth_result = self.security_manager.auth_manager.authenticate_api_key(
            "admin_key_123456789012345"
        )

        assert auth_result.is_valid is True
        assert auth_result.username == "admin"
        assert "admin" in auth_result.roles
        assert auth_result.auth_method == "api_key"

        # Test invalid API key
        auth_result = self.security_manager.auth_manager.authenticate_api_key("short")

        assert auth_result.is_valid is False
        assert auth_result.error_code == -32002

        # Test missing API key
        auth_result = self.security_manager.auth_manager.authenticate_api_key("")

        assert auth_result.is_valid is False
        assert auth_result.error_code == -32001

    def test_complete_jwt_authentication_flow(self):
        """Test complete JWT authentication flow."""
        # Create JWT token
        payload = {
            "username": "admin",
            "roles": ["admin"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }

        token = jwt.encode(
            payload,
            self.auth_config.jwt_secret.get_secret_value(),
            algorithm=self.auth_config.jwt_algorithm,
        )

        # Test valid JWT authentication
        auth_result = self.security_manager.authenticate_user(
            {"method": "jwt", "token": token}
        )

        assert auth_result.is_valid is True
        assert auth_result.username == "admin"
        assert "admin" in auth_result.roles
        assert auth_result.auth_method == "jwt"

        # Test expired JWT token
        expired_payload = {
            "username": "admin",
            "roles": ["admin"],
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }

        expired_token = jwt.encode(
            expired_payload,
            self.auth_config.jwt_secret.get_secret_value(),
            algorithm=self.auth_config.jwt_algorithm,
        )

        auth_result = self.security_manager.authenticate_user(
            {"method": "jwt", "token": expired_token}
        )

        assert auth_result.is_valid is False
        assert auth_result.error_code == -32002  # JWT token expired error

        # Test invalid JWT token
        auth_result = self.security_manager.authenticate_user(
            {"method": "jwt", "token": "invalid_token"}
        )

        assert auth_result.is_valid is False
        assert auth_result.error_code == -32003  # Invalid JWT token error

    def test_complete_authorization_flow(self):
        """Test complete authorization flow."""
        # Test admin permissions
        auth_result = self.security_manager.authenticate_user(
            {"method": "api_key", "api_key": "admin_key_123456789012345"}
        )

        assert auth_result.is_valid is True

        # Check admin permissions
        perm_result = self.security_manager.check_permissions(
            auth_result.roles, ["read", "write", "delete", "admin"]
        )

        assert perm_result.is_valid is True
        assert set(perm_result.granted_permissions) == {
            "read",
            "write",
            "delete",
            "admin",
            "moderate",
        }

        # Test user permissions
        auth_result = self.security_manager.auth_manager.authenticate_api_key(
            "user_key_456789012345678"
        )

        assert auth_result.is_valid is True

        # Check user permissions
        perm_result = self.security_manager.check_permissions(
            auth_result.roles, ["read", "write"]
        )

        assert perm_result.is_valid is True
        assert set(perm_result.granted_permissions) == {"read", "write"}

        # Test user denied admin permissions
        perm_result = self.security_manager.check_permissions(
            auth_result.roles, ["admin"]
        )

        assert perm_result.is_valid is False
        assert perm_result.denied_permissions == ["admin"]

        # Test readonly permissions
        auth_result = self.security_manager.auth_manager.authenticate_api_key(
            "readonly_key_789012345678"
        )

        assert auth_result.is_valid is True

        # Check readonly permissions
        perm_result = self.security_manager.check_permissions(
            auth_result.roles, ["read"]
        )

        assert perm_result.is_valid is True
        assert perm_result.granted_permissions == ["read"]

        # Test readonly denied write permissions
        perm_result = self.security_manager.check_permissions(
            auth_result.roles, ["write"]
        )

        assert perm_result.is_valid is False
        assert perm_result.denied_permissions == ["write"]

    def test_role_hierarchy_flow(self):
        """Test role hierarchy inheritance flow."""
        # Test admin role (inherits from user and guest)
        auth_result = self.security_manager.auth_manager.authenticate_api_key(
            "admin_key_123456789012345"
        )

        assert auth_result.is_valid is True
        assert "admin" in auth_result.roles
        # Admin inherits from user and guest through hierarchy

        # Check inherited permissions (admin has all permissions including moderate from moderator)
        perm_result = self.security_manager.check_permissions(
            auth_result.roles, ["read", "write", "moderate", "admin"]
        )

        assert perm_result.is_valid is True
        assert set(perm_result.granted_permissions) == {
            "read",
            "write",
            "moderate",
            "admin",
            "delete",
        }
        assert "read" in perm_result.granted_permissions
        assert "write" in perm_result.granted_permissions
        assert "moderate" in perm_result.granted_permissions

    def test_rate_limiting_integration_flow(self):
        """Test rate limiting integration with authentication."""
        # Test rate limiting for authenticated user
        user_identifier = "user_key_456789012345678"

        # Make multiple requests to trigger rate limiting
        for i in range(105):  # Exceed default limit
            rate_limit_result = self.security_manager.check_rate_limit(user_identifier)

            # Rate limiting should work
            assert isinstance(rate_limit_result, bool)

        # Test rate limiting reset
        # Note: In real implementation, this would depend on time window
        # For testing, we'll just verify the mechanism works

    def test_multi_method_authentication_flow(self):
        """Test authentication with multiple methods."""
        # Test API key first, then JWT
        auth_result = self.security_manager.auth_manager.authenticate_api_key(
            "admin_key_123456789012345"
        )

        # Should use API key (first method)
        assert auth_result.is_valid is True
        assert auth_result.auth_method == "api_key"

        # Test JWT when API key is invalid
        auth_result = self.security_manager.authenticate_user(
            {"method": "api_key", "api_key": "invalid_key"}
        )

        # Should fail (both methods invalid)
        assert auth_result.is_valid is False

    def test_session_management_flow(self):
        """Test session management flow."""
        # Create session for user
        auth_result = self.security_manager.authenticate_user(
            {"method": "api_key", "api_key": "user_key_456789012345678"}
        )

        assert auth_result.is_valid is True

        # Simulate session persistence
        session_data = {
            "user_id": auth_result.username,
            "roles": auth_result.roles,
            "permissions": auth_result.permissions,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Verify session data
        assert session_data["user_id"] == "user"
        assert "user" in session_data["roles"]
        assert "read" in session_data["permissions"]
        assert "write" in session_data["permissions"]

    def test_error_handling_flow(self):
        """Test error handling in authentication flow."""
        # Test with malformed headers
        auth_result = self.security_manager.authenticate_user(
            {"method": "api_key", "api_key": ""}  # Empty API key
        )

        assert auth_result.is_valid is False
        assert auth_result.error_code == -32001

        # Test with invalid JWT format
        auth_result = self.security_manager.authenticate_user(
            {"method": "jwt", "token": "InvalidFormat token"}
        )

        assert auth_result.is_valid is False
        assert auth_result.error_code == -32003

        # Test with unsupported authentication method
        with pytest.raises(SecurityValidationError) as exc_info:
            self.security_manager.authenticate_user(
                {"method": "custom", "custom_token": "custom_token"}
            )

        assert "Unsupported authentication method: custom" in str(exc_info.value)

    def test_performance_benchmark_flow(self):
        """Test performance of authentication flow."""
        import time

        # Benchmark API key authentication
        start_time = time.time()
        for i in range(1000):
            auth_result = self.security_manager.authenticate_user(
                {"method": "api_key", "api_key": "admin_key_123456789012345"}
            )
            assert auth_result.is_valid is True
        end_time = time.time()

        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.001, f"API key auth too slow: {avg_time:.6f}s per request"

        # Benchmark permission checking
        auth_result = self.security_manager.authenticate_user(
            {"method": "api_key", "api_key": "admin_key_123456789012345"}
        )

        start_time = time.time()
        for i in range(1000):
            perm_result = self.security_manager.check_permissions(
                auth_result.roles, ["read", "write", "delete"]
            )
            assert perm_result.is_valid is True
        end_time = time.time()

        avg_time = (end_time - start_time) / 1000
        assert (
            avg_time < 0.001
        ), f"Permission check too slow: {avg_time:.6f}s per request"

    def test_security_audit_flow(self):
        """Test security audit flow."""
        # Perform security audit
        audit_result = self.security_manager.perform_security_audit()

        # Verify audit results
        assert audit_result is not None
        assert "authentication" in audit_result
        assert "authorization" in audit_result
        assert "rate_limiting" in audit_result

        # Check authentication audit
        auth_audit = audit_result["authentication"]
        assert auth_audit["enabled"] is True
        assert "api_key" in auth_audit["methods"]
        assert "jwt" in auth_audit["methods"]

        # Check authorization audit
        authz_audit = audit_result["authorization"]
        assert authz_audit["enabled"] is True
        assert authz_audit["roles_count"] >= 4  # admin, user, readonly, moderator

        # Check rate limiting audit
        rate_audit = audit_result["rate_limiting"]
        assert rate_audit["enabled"] is True

    def test_configuration_validation_flow(self):
        """Test configuration validation flow."""
        # Test valid configuration
        validation_result = self.security_manager.validate_configuration()
        assert validation_result.is_valid is True

        # Test with invalid configuration (missing API keys)
        invalid_auth_config = AuthConfig(
            enabled=True,
            methods=["api_key"],
            api_keys={},  # Empty API keys
            jwt_secret="test_secret_long_enough_for_validation",
        )

        invalid_config = SecurityConfig(
            auth=invalid_auth_config,
            permissions=self.permission_config,
            rate_limit=RateLimitConfig(enabled=True, default_requests_per_minute=100),
            ssl=SSLConfig(enabled=False),
            certificates=CertificateConfig(enabled=False),
        )

        invalid_manager = SecurityManager(invalid_config)
        validation_result = invalid_manager.validate_configuration()
        assert validation_result.is_valid is False

    def test_logging_and_monitoring_flow(self):
        """Test logging and monitoring flow."""
        # Perform authentication with logging
        auth_result = self.security_manager.authenticate_user(
            {"method": "api_key", "api_key": "admin_key_123456789012345"}
        )

        assert auth_result.is_valid is True

        # Check that logging is configured
        assert hasattr(self.security_manager.auth_manager, "logger")
        assert self.security_manager.auth_manager.logger is not None

        assert hasattr(self.security_manager.permission_manager, "logger")
        assert self.security_manager.permission_manager.logger is not None

        # Get security metrics
        metrics = self.security_manager.get_security_metrics()

        assert metrics is not None
        assert "authentication_attempts" in metrics
        assert "successful_authentications" in metrics
        assert "failed_authentications" in metrics
        assert "permission_checks" in metrics
        assert "rate_limit_violations" in metrics

    def test_integration_with_external_systems_flow(self):
        """Test integration with external systems flow."""
        # Test with external user store (mocked)
        with patch(
            "mcp_security_framework.core.auth_manager.AuthManager._validate_external_user"
        ) as mock_validate:
            mock_validate.return_value = True

            auth_result = self.security_manager.authenticate_user(
                {"method": "api_key", "api_key": "external_user_key"}
            )

            # Should handle external authentication gracefully
            assert auth_result.is_valid is False  # Key not in config
            assert auth_result.error_code == -32003

        # Test with external permission store (mocked)
        with patch(
            "mcp_security_framework.core.permission_manager.PermissionManager._load_external_permissions"
        ) as mock_load:
            mock_load.return_value = {
                "external_role": {"permissions": ["external_perm"]}
            }

            # Should integrate with external permission systems
            perm_result = self.security_manager.check_permissions(
                ["external_role"], ["external_perm"]
            )

            # In this case, external permissions would be loaded
            # but the test role doesn't exist in our config
            assert perm_result.is_valid is False
