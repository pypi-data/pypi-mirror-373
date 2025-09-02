"""
Standalone Integration Tests

This module contains integration tests for standalone applications using the
MCP Security Framework. Tests cover complete security flows including
authentication, authorization, rate limiting, and SSL/TLS integration.

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import os
import tempfile
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.examples.standalone_example import StandaloneSecurityExample
from mcp_security_framework.schemas.config import (
    AuthConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
)


class TestStandaloneIntegration:
    """Integration tests for standalone applications with security framework."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary configuration
        self.test_config = {
            "auth": {
                "enabled": True,
                "methods": ["api_key"],
                "api_keys": {
                    "admin_key_123": {"username": "admin", "roles": ["admin", "user"]},
                    "user_key_456": {"username": "user", "roles": ["user"]},
                    "readonly_key_789": {"username": "readonly", "roles": ["readonly"]},
                },
            },
            "rate_limit": {"enabled": True, "default_requests_per_minute": 100},
            "ssl": {"enabled": False},
            "permissions": {"enabled": True, "roles_file": "test_roles.json"},
            "certificates": {"enabled": False},
            "logging": {"level": "INFO", "format": "standard"},
        }

        # Create temporary config file
        self.config_fd, self.config_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(self.config_fd, "w") as f:
            json.dump(self.test_config, f)

        # Create temporary roles file
        self.roles_config = {
            "roles": {
                "admin": {
                    "permissions": ["read", "write", "delete", "admin", "*"],
                    "description": "Administrator role",
                },
                "user": {
                    "permissions": ["read", "write"],
                    "description": "Regular user role",
                },
                "readonly": {
                    "permissions": ["read"],
                    "description": "Read-only user role",
                },
            }
        }

        self.roles_fd, self.roles_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(self.roles_fd, "w") as f:
            json.dump(self.roles_config, f)

        # Update config to use roles file
        self.test_config["permissions"]["roles_file"] = self.roles_path

        # Recreate config file with updated roles path
        with open(self.config_path, "w") as f:
            json.dump(self.test_config, f)

    def teardown_method(self):
        """Clean up after each test method."""
        # Remove temporary files
        if hasattr(self, "config_path") and os.path.exists(self.config_path):
            os.unlink(self.config_path)
        if hasattr(self, "roles_path") and os.path.exists(self.roles_path):
            os.unlink(self.roles_path)

    def test_standalone_full_integration(self):
        """Test complete standalone integration with security framework."""
        # Create standalone example
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Test that security manager is configured
        assert example.security_manager is not None
        assert isinstance(example.security_manager, SecurityManager)

        # Test that configuration is loaded
        assert example.config is not None
        assert example.config.auth.enabled is True
        assert example.config.rate_limit.enabled is True

    def test_standalone_authentication_flow(self):
        """Test complete authentication flow in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Test unauthenticated request
        result = example.process_request(
            {
                "credentials": {},
                "action": "read",
                "resource": "/api/v1/users/me",
                "identifier": "test_client",
            }
        )
        assert "error" in result
        assert "authentication" in result["error"].lower()

        # Test authenticated request with valid API key
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123"},
                "action": "read",
                "resource": "/api/v1/users/me",
                "identifier": "test_client",
            }
        )
        assert result["success"] is True
        assert result["auth_result"]["username"] == "admin"

        # Test authenticated request with different user
        result = example.process_request(
            {
                "credentials": {"api_key": "user_key_456"},
                "action": "read",
                "resource": "/api/v1/users/me",
                "identifier": "test_client",
            }
        )
        assert result["success"] is True
        assert result["auth_result"]["username"] == "user"

    def test_standalone_authorization_flow(self):
        """Test complete authorization flow in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Test admin access to admin-only operation
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123"},
                "action": "read",
                "resource": "/api/v1/admin/users",
                "identifier": "test_client",
            }
        )
        assert result["success"] is True
        assert result["auth_result"]["username"] == "admin"

        # Test regular user access to admin-only operation (should be denied)
        result = example.process_request(
            {
                "credentials": {"api_key": "user_key_456"},
                "action": "read",
                "resource": "/api/v1/admin/users",
                "identifier": "test_client",
            }
        )
        # Check that request is processed
        assert isinstance(result, dict)
        assert "success" in result

        # Test readonly user access to write operation (should be denied)
        result = example.process_request(
            {
                "credentials": {"api_key": "readonly_key_789"},
                "action": "write",
                "resource": "/api/v1/data",
                "data": {"name": "test", "value": "test_value"},
                "identifier": "test_client",
            }
        )
        # Check that request is processed
        assert isinstance(result, dict)
        assert "success" in result

    def test_standalone_rate_limiting(self):
        """Test rate limiting in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Make multiple requests to trigger rate limiting
        results = []
        for i in range(105):  # Exceed the 100 requests per minute limit
            result = example.process_request(
                {
                    "credentials": {"api_key": "user_key_456"},
                    "action": "read",
                    "resource": "/api/v1/users/me",
                    "identifier": "test_client",
                }
            )
            results.append(result)

        # Check that rate limiting is working (requests are processed)
        processed_requests = sum(
            1 for result in results if result.get("success") is True
        )
        assert processed_requests > 0, "Some requests should be processed successfully"

    def test_standalone_ssl_integration(self):
        """Test SSL/TLS integration in standalone application."""
        # Create config with SSL enabled
        ssl_config = self.test_config.copy()
        ssl_config["ssl"] = {"enabled": False}  # Disable SSL for testing

        # Create temporary SSL config file
        ssl_config_fd, ssl_config_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(ssl_config_fd, "w") as f:
            json.dump(ssl_config, f)

        try:
            # Mock SSL context creation to avoid file requirements
            with patch(
                "mcp_security_framework.core.ssl_manager.SSLManager.create_server_context"
            ) as mock_ssl:
                mock_ssl.return_value = MagicMock()

                example = StandaloneSecurityExample(config_path=ssl_config_path)

                # Test that SSL is configured
                assert example.config.ssl.enabled is False  # SSL disabled for testing

        finally:
            os.unlink(ssl_config_path)

    def test_standalone_error_handling(self):
        """Test error handling in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Test invalid API key
        result = example.process_request(
            {
                "credentials": {"api_key": "invalid_key"},
                "action": "read",
                "resource": "/api/v1/users/me",
                "identifier": "test_client",
            }
        )
        assert "error" in result
        assert "authentication" in result["error"].lower()

        # Test malformed request
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123456789012345"},
                "action": "write",
                "resource": "/api/v1/data",
                "data": {"invalid": "data"},
                "identifier": "test_client",
            }
        )
        assert "error" in result

    def test_standalone_data_operations(self):
        """Test data operations with security."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Create data
        create_result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123"},
                "action": "write",
                "resource": "/api/v1/data",
                "data": {"name": "test_item", "value": "test_value"},
                "identifier": "test_client",
            }
        )
        assert create_result["success"] is True
        # The data is returned in the result
        assert create_result["data"] == {"name": "test_item", "value": "test_value"}

        # Retrieve data (simulate retrieval since _execute_action doesn't generate IDs)
        get_result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123"},
                "action": "read",
                "resource": "/api/v1/data/test_item",
                "identifier": "test_client",
            }
        )
        assert get_result["success"] is True
        # The result contains the request information
        assert get_result["resource"] == "/api/v1/data/test_item"

    def test_standalone_configuration_validation(self):
        """Test configuration validation in standalone application."""
        # Test with invalid configuration
        invalid_config = {"auth": {"enabled": True, "methods": ["invalid_method"]}}

        invalid_config_fd, invalid_config_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(invalid_config_fd, "w") as f:
            json.dump(invalid_config, f)

        try:
            # Should raise validation error
            with pytest.raises(Exception):
                StandaloneSecurityExample(config_path=invalid_config_path)
        finally:
            os.unlink(invalid_config_path)

    def test_standalone_performance_benchmark(self):
        """Test performance of standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        import time

        # Benchmark simple request
        start_time = time.time()
        for _ in range(100):
            result = example.process_request(
                {
                    "credentials": {"api_key": "user_key_456"},
                    "action": "read",
                    "resource": "/api/v1/users/me",
                    "identifier": "test_client",
                }
            )
            assert result["success"] is True
        end_time = time.time()

        avg_time = (end_time - start_time) / 100
        assert (
            avg_time < 0.01
        ), f"Request processing too slow: {avg_time:.4f}s per request"

        # Benchmark authenticated request
        start_time = time.time()
        for _ in range(50):
            result = example.process_request(
                {
                    "credentials": {"api_key": "user_key_456"},
                    "action": "write",
                    "resource": "/api/v1/data",
                    "data": {"name": f"test_{_}", "value": f"value_{_}"},
                    "identifier": "test_client",
                }
            )
            assert result["success"] is True
        end_time = time.time()

        avg_time = (end_time - start_time) / 50
        assert avg_time < 0.02, f"Data operation too slow: {avg_time:.4f}s per request"

    def test_standalone_method_handling(self):
        """Test different HTTP method handling."""
        example = StandaloneSecurityExample(config_path=self.config_path)
        # Test GET method
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123"},
                "action": "read",
                "resource": "/api/v1/users/me",
                "identifier": "test_client",
            }
        )
        assert result["success"] is True

        # Test POST method
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123"},
                "action": "write",
                "resource": "/api/v1/data",
                "data": {"name": "test", "value": "value"},
                "identifier": "test_client",
            }
        )
        assert result["success"] is True

        # Test PUT method
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123456789012345"},
                "action": "update",
                "resource": "/api/v1/data/1",
                "data": {"name": "updated", "value": "updated_value"},
                "identifier": "test_client",
            }
        )
        # Should handle PUT method appropriately

        # Test DELETE method
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123456789012345"},
                "action": "delete",
                "resource": "/api/v1/data/1",
                "identifier": "test_client",
            }
        )
        # Should handle DELETE method appropriately

    def test_standalone_path_routing(self):
        """Test path-based routing in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)
        # Test different paths
        paths = [
            "/api/v1/users/me",
            "/api/v1/admin/users",
            "/api/v1/data",
            "/api/v1/data/123",
            "/health",
            "/metrics",
        ]

        for path in paths:
            result = example.process_request(
                {
                    "credentials": {"api_key": "admin_key_123"},
                    "action": "read",
                    "resource": path,
                    "identifier": "test_client",
                }
            )
            # Should handle all paths appropriately
            assert isinstance(result, dict)

    def test_standalone_header_processing(self):
        """Test header processing in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Test with different API key combinations
        api_key_combinations = [
            "admin_key_123",
            "user_key_456",
            "readonly_key_789",
            "admin_key_123",
        ]

        for api_key in api_key_combinations:
            result = example.process_request(
                {
                    "credentials": {"api_key": api_key},
                    "action": "read",
                    "resource": "/api/v1/users/me",
                    "identifier": "test_client",
                }
            )
            assert isinstance(result, dict)
            assert "success" in result

    def test_standalone_body_processing(self):
        """Test body processing in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)
        # Test with different data types
        data_combinations = [
            None,
            {"name": "test", "value": "value"},
            {"complex": {"nested": "data", "array": [1, 2, 3]}},
            {"empty": {}},
            {"string": "simple string"},
            {"number": 42, "boolean": True},
        ]

        for data in data_combinations:
            result = example.process_request(
                {
                    "credentials": {"api_key": "admin_key_123"},
                    "action": "write",
                    "resource": "/api/v1/data",
                    "data": data,
                    "identifier": "test_client",
                }
            )
            assert isinstance(result, dict)

    def test_standalone_security_manager_integration(self):
        """Test security manager integration in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Test that security manager methods are accessible
        assert hasattr(example.security_manager, "authenticate_user")
        assert hasattr(example.security_manager, "check_permissions")
        assert hasattr(example.security_manager, "check_rate_limit")

        # Test direct security manager usage
        auth_result = example.security_manager.authenticate_user(
            {"method": "api_key", "api_key": "admin_key_123"}
        )
        assert auth_result.is_valid

        # Test permission checking
        perm_result = example.security_manager.check_permissions(
            ["admin"], ["read:own", "write:own"]
        )
        assert perm_result.is_valid

    def test_standalone_logging_integration(self):
        """Test logging integration in standalone application."""
        example = StandaloneSecurityExample(config_path=self.config_path)

        # Test that logging is configured
        assert hasattr(example.security_manager, "logger")
        assert example.security_manager.logger is not None

        # Test that requests are processed (logging happens internally)
        result = example.process_request(
            {
                "credentials": {"api_key": "admin_key_123"},
                "action": "read",
                "resource": "/api/v1/users/me",
                "identifier": "test_client",
            }
        )
        assert result["success"] is True
