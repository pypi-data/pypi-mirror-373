"""
Security CLI Tests

This module contains tests for the security management CLI commands.
"""

import os
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from mcp_security_framework.cli.security_cli import security_cli
from mcp_security_framework.schemas.config import (
    AuthConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
)
from mcp_security_framework.schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    ValidationResult,
)


class TestSecurityCLI:
    """Test suite for security CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_add_api_key_success(self, mock_security_manager_class):
        """Test successful API key addition."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.auth_manager.add_api_key.return_value = True

        # Run command
        result = self.runner.invoke(
            security_cli,
            [
                "auth",
                "add-api-key",
                "--username",
                "testuser",
                "--api-key",
                "test_key_123",
            ],
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ API key added successfully" in result.output
        assert "testuser" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_add_api_key_failure(self, mock_security_manager_class):
        """Test API key addition failure."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.auth_manager.add_api_key.return_value = False

        # Run command
        result = self.runner.invoke(
            security_cli,
            [
                "auth",
                "add-api-key",
                "--username",
                "testuser",
                "--api-key",
                "test_key_123",
            ],
        )

        # Assertions
        assert result.exit_code != 0
        assert "❌ Failed to add API key" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_remove_api_key_success(self, mock_security_manager_class):
        """Test successful API key removal."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.auth_manager.remove_api_key.return_value = True

        # Run command
        result = self.runner.invoke(
            security_cli, ["auth", "remove-api-key", "--username", "testuser"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ API key removed successfully" in result.output
        assert "testuser" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_test_api_key_success(self, mock_security_manager_class):
        """Test successful API key authentication."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock auth result
        mock_auth_result = Mock(spec=AuthResult)
        mock_auth_result.is_valid = True
        mock_auth_result.username = "testuser"
        mock_auth_result.roles = ["user", "admin"]
        mock_auth_result.auth_method = AuthMethod.API_KEY
        mock_security_manager.auth_manager.authenticate_api_key.return_value = (
            mock_auth_result
        )

        # Run command
        result = self.runner.invoke(
            security_cli, ["auth", "test-api-key", "--api-key", "test_key_123"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ API key authentication successful!" in result.output
        assert "testuser" in result.output
        assert "user, admin" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_test_api_key_failure(self, mock_security_manager_class):
        """Test API key authentication failure."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock auth result
        mock_auth_result = Mock(spec=AuthResult)
        mock_auth_result.is_valid = False
        mock_auth_result.error_message = "Invalid API key"
        mock_security_manager.auth_manager.authenticate_api_key.return_value = (
            mock_auth_result
        )

        # Run command
        result = self.runner.invoke(
            security_cli, ["auth", "test-api-key", "--api-key", "invalid_key"]
        )

        # Assertions
        assert result.exit_code != 0
        assert "❌ API key authentication failed!" in result.output
        assert "Invalid API key" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_test_jwt_success(self, mock_security_manager_class):
        """Test successful JWT authentication."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock auth result
        mock_auth_result = Mock(spec=AuthResult)
        mock_auth_result.is_valid = True
        mock_auth_result.username = "testuser"
        mock_auth_result.roles = ["user"]
        mock_auth_result.auth_method = AuthMethod.JWT
        mock_security_manager.auth_manager.authenticate_jwt_token.return_value = (
            mock_auth_result
        )

        # Run command
        result = self.runner.invoke(
            security_cli, ["auth", "test-jwt", "--token", "test_jwt_token"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ JWT token authentication successful!" in result.output
        assert "testuser" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_check_permissions_success(self, mock_security_manager_class):
        """Test successful permission check."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock user roles
        mock_security_manager.auth_manager._get_user_roles.return_value = [
            "user",
            "admin",
        ]

        # Mock validation result
        mock_validation_result = Mock(spec=ValidationResult)
        mock_validation_result.is_valid = True
        mock_validation_result.missing_permissions = []
        mock_security_manager.permission_manager.validate_access.return_value = (
            mock_validation_result
        )

        # Run command
        result = self.runner.invoke(
            security_cli,
            [
                "permissions",
                "check",
                "--username",
                "testuser",
                "--permissions",
                "read",
                "--permissions",
                "write",
            ],
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ User has all required permissions!" in result.output
        assert "testuser" in result.output
        assert "user, admin" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_check_permissions_failure(self, mock_security_manager_class):
        """Test permission check failure."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock user roles
        mock_security_manager.auth_manager._get_user_roles.return_value = ["user"]

        # Mock validation result
        mock_validation_result = Mock(spec=ValidationResult)
        mock_validation_result.is_valid = False
        mock_validation_result.missing_permissions = ["admin"]
        mock_security_manager.permission_manager.validate_access.return_value = (
            mock_validation_result
        )

        # Run command
        result = self.runner.invoke(
            security_cli,
            [
                "permissions",
                "check",
                "--username",
                "testuser",
                "--permissions",
                "admin",
            ],
        )

        # Assertions
        assert result.exit_code != 0
        assert "❌ User does not have required permissions!" in result.output
        assert "admin" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_list_role_permissions_success(self, mock_security_manager_class):
        """Test successful role permissions listing."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.permission_manager.get_role_permissions.return_value = [
            "read",
            "write",
            "delete",
        ]

        # Run command
        result = self.runner.invoke(
            security_cli, ["permissions", "list-role-permissions", "--role", "admin"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "Permissions for role 'admin':" in result.output
        assert "read" in result.output
        assert "write" in result.output
        assert "delete" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_rate_limit_check_success(self, mock_security_manager_class):
        """Test successful rate limit check."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        # Run command
        result = self.runner.invoke(
            security_cli, ["rate-limit", "check", "--identifier", "192.168.1.1"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ Rate limit check passed" in result.output
        assert "192.168.1.1" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_rate_limit_check_failure(self, mock_security_manager_class):
        """Test rate limit check failure."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.rate_limiter.check_rate_limit.return_value = False

        # Run command
        result = self.runner.invoke(
            security_cli, ["rate-limit", "check", "--identifier", "192.168.1.1"]
        )

        # Assertions
        assert result.exit_code != 0
        assert "❌ Rate limit exceeded" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_rate_limit_reset_success(self, mock_security_manager_class):
        """Test successful rate limit reset."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Run command
        result = self.runner.invoke(
            security_cli, ["rate-limit", "reset", "--identifier", "192.168.1.1"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ Rate limit reset successfully" in result.output
        assert "192.168.1.1" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_rate_limit_status_success(self, mock_security_manager_class):
        """Test successful rate limit status."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock rate limit status
        mock_status = Mock()
        mock_status.current_count = 5
        mock_status.limit = 100
        mock_status.window_start = "2024-01-01 10:00:00"
        mock_status.window_end = "2024-01-01 10:01:00"
        mock_status.is_allowed = True
        mock_security_manager.rate_limiter.get_rate_limit_status.return_value = (
            mock_status
        )

        # Run command
        result = self.runner.invoke(
            security_cli, ["rate-limit", "status", "--identifier", "192.168.1.1"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "Rate Limit Status for '192.168.1.1':" in result.output
        assert "Current Count: 5" in result.output
        assert "Limit: 100" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_config_validate_success(self, mock_security_manager_class):
        """Test successful configuration validation."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Run command
        result = self.runner.invoke(security_cli, ["config", "validate"])

        # Assertions
        assert result.exit_code == 0
        assert "✅ Configuration validation passed!" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_config_export_success(self, mock_security_manager_class):
        """Test successful configuration export."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Create temporary output file
        output_file = os.path.join(self.temp_dir, "config.json")

        # Run command
        result = self.runner.invoke(
            security_cli, ["config", "export", "--output", output_file]
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ Configuration exported to:" in result.output
        assert os.path.exists(output_file)

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_status_success(self, mock_security_manager_class):
        """Test successful security status display."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.auth_manager = Mock()
        mock_security_manager.permission_manager = Mock()
        mock_security_manager.rate_limiter = Mock()
        mock_security_manager.ssl_manager = Mock()
        mock_security_manager.cert_manager = Mock()

        # Run command
        result = self.runner.invoke(security_cli, ["status"])

        # Assertions
        assert result.exit_code == 0
        assert "Security Status:" in result.output
        assert "Component Status:" in result.output

    def test_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(security_cli, ["--help"])
        assert result.exit_code == 0
        assert "Security Management CLI" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_auth_help(self, mock_security_manager_class):
        """Test auth help output."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        result = self.runner.invoke(security_cli, ["auth", "--help"])
        assert result.exit_code == 0
        assert "Authentication operations" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_permissions_help(self, mock_security_manager_class):
        """Test permissions help output."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        result = self.runner.invoke(security_cli, ["permissions", "--help"])
        assert result.exit_code == 0
        assert "Permission management operations" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_rate_limit_help(self, mock_security_manager_class):
        """Test rate-limit help output."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        result = self.runner.invoke(security_cli, ["rate-limit", "--help"])
        assert result.exit_code == 0
        assert "Rate limiting operations" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_config_help(self, mock_security_manager_class):
        """Test config help output."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        result = self.runner.invoke(security_cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "Configuration management operations" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_missing_required_options(self, mock_security_manager_class):
        """Test missing required options."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        result = self.runner.invoke(security_cli, ["auth", "add-api-key"])
        assert result.exit_code != 0
        assert "Missing option" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_generate_roles_template(self, mock_security_manager_class):
        """Test generating template roles configuration."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Run command
        result = self.runner.invoke(security_cli, ["generate-roles", "--template"])

        # Assertions
        assert result.exit_code == 0
        assert "admin" in result.output
        assert "user" in result.output
        assert "guest" in result.output
        assert "permissions" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_generate_roles_current(self, mock_security_manager_class):
        """Test generating current roles configuration."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock permission manager
        mock_permission_manager = Mock()
        mock_security_manager.permission_manager = mock_permission_manager

        # Mock export method
        mock_roles_config = {
            "roles": {
                "admin": {
                    "description": "Administrator role",
                    "permissions": ["*"],
                    "parent_roles": [],
                }
            },
            "permissions": {"*": "All permissions"},
        }
        mock_permission_manager.export_roles_config.return_value = mock_roles_config

        # Run command
        result = self.runner.invoke(security_cli, ["generate-roles"])

        # Assertions
        assert result.exit_code == 0
        assert "admin" in result.output
        assert "Administrator role" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_generate_roles_with_output(self, mock_security_manager_class):
        """Test generating roles configuration with output file."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock permission manager
        mock_permission_manager = Mock()
        mock_security_manager.permission_manager = mock_permission_manager

        # Mock export method
        mock_roles_config = {
            "roles": {
                "user": {
                    "description": "User role",
                    "permissions": ["read:own"],
                    "parent_roles": [],
                }
            },
            "permissions": {"read:own": "Read own resources"},
        }
        mock_permission_manager.export_roles_config.return_value = mock_roles_config

        # Create temporary output file
        output_file = os.path.join(self.temp_dir, "roles.json")

        # Run command
        result = self.runner.invoke(
            security_cli, ["generate-roles", "--output", output_file]
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ Current roles configuration exported" in result.output
        assert os.path.exists(output_file)

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_security_audit_text_format(self, mock_security_manager_class):
        """Test security audit in text format."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock components
        mock_auth_manager = Mock()
        mock_auth_manager.api_keys = {"key1": "user1", "key2": "user2"}
        mock_security_manager.auth_manager = mock_auth_manager

        mock_permission_manager = Mock()
        mock_permission_manager.roles = {"admin": {}, "user": {}}
        mock_security_manager.permission_manager = mock_permission_manager

        mock_security_manager.rate_limiter = Mock()
        mock_security_manager.ssl_manager = Mock()
        mock_security_manager.cert_manager = Mock()

        # Run command
        result = self.runner.invoke(security_cli, ["security-audit"])

        # Assertions
        assert result.exit_code == 0
        assert "Security Audit Report" in result.output
        assert "Configuration:" in result.output
        assert "Components:" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_security_audit_json_format(self, mock_security_manager_class):
        """Test security audit in JSON format."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock components
        mock_auth_manager = Mock()
        mock_auth_manager.api_keys = {"key1": "user1"}
        mock_security_manager.auth_manager = mock_auth_manager

        mock_permission_manager = Mock()
        mock_permission_manager.roles = {"admin": {}}
        mock_security_manager.permission_manager = mock_permission_manager

        mock_security_manager.rate_limiter = Mock()
        mock_security_manager.ssl_manager = Mock()
        mock_security_manager.cert_manager = Mock()

        # Run command
        result = self.runner.invoke(
            security_cli, ["security-audit", "--format", "json"]
        )

        # Assertions
        assert result.exit_code == 0
        assert "timestamp" in result.output
        assert "configuration" in result.output
        assert "components" in result.output

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_security_audit_with_output(self, mock_security_manager_class):
        """Test security audit with output file."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager

        # Mock components
        mock_auth_manager = Mock()
        mock_auth_manager.api_keys = {"key1": "user1"}
        mock_security_manager.auth_manager = mock_auth_manager

        mock_permission_manager = Mock()
        mock_permission_manager.roles = {"admin": {}}
        mock_security_manager.permission_manager = mock_permission_manager

        mock_security_manager.rate_limiter = Mock()
        mock_security_manager.ssl_manager = Mock()
        mock_security_manager.cert_manager = Mock()

        # Create temporary output file
        output_file = os.path.join(self.temp_dir, "audit.json")

        # Run command
        result = self.runner.invoke(
            security_cli,
            ["security-audit", "--output", output_file, "--format", "json"],
        )

        # Assertions
        assert result.exit_code == 0
        assert "✅ Security audit report saved" in result.output
        assert os.path.exists(output_file)

    @patch("mcp_security_framework.cli.security_cli.SecurityManager")
    def test_security_audit_failure(self, mock_security_manager_class):
        """Test security audit failure."""
        # Mock security manager
        mock_security_manager = Mock()
        mock_security_manager_class.return_value = mock_security_manager
        mock_security_manager.auth_manager = None  # This will cause an error

        # Run command
        result = self.runner.invoke(security_cli, ["security-audit"])

        # Assertions
        assert result.exit_code != 0
        assert "❌ Failed to perform security audit" in result.output
