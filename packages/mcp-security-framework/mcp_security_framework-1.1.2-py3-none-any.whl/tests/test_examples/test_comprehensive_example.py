"""
Tests for Comprehensive Security Example

This module tests the comprehensive security example that demonstrates
all capabilities of the MCP Security Framework.
"""

import os
import shutil
import tempfile
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from mcp_security_framework.examples.comprehensive_example import (
    ComprehensiveSecurityExample,
)
from mcp_security_framework.schemas.config import SecurityConfig
from mcp_security_framework.schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    ValidationResult,
    ValidationStatus,
)


class TestComprehensiveSecurityExample:
    """Test suite for ComprehensiveSecurityExample class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp(prefix="test_comprehensive_")
        self.example = ComprehensiveSecurityExample(work_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_comprehensive_security_example_initialization(self):
        """Test ComprehensiveSecurityExample initialization."""
        assert self.example.work_dir == self.temp_dir
        assert os.path.exists(self.example.certs_dir)
        assert os.path.exists(self.example.keys_dir)
        assert os.path.exists(self.example.config_dir)
        assert isinstance(self.example.config, SecurityConfig)
        assert self.example.logger is not None
        assert self.example.test_api_key == "admin_key_123"
        assert self.example.test_jwt_token is not None

    def test_create_comprehensive_config(self):
        """Test comprehensive configuration creation."""
        config = self.example._create_comprehensive_config()
        assert isinstance(config, SecurityConfig)
        assert config.auth.enabled is True
        assert config.permissions.enabled is True
        assert config.ssl.enabled is False  # Initially disabled
        assert config.certificates.enabled is False  # Initially disabled
        assert config.rate_limit.enabled is True
        assert config.logging.enabled is True

    def test_create_test_jwt_token(self):
        """Test JWT token creation."""
        token = self.example._create_test_jwt_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_roles_config(self):
        """Test roles configuration creation."""
        roles_file = os.path.join(self.example.config_dir, "roles.json")
        assert os.path.exists(roles_file)

        # Verify roles file content
        import json

        with open(roles_file, "r") as f:
            roles_config = json.load(f)

        assert "roles" in roles_config
        assert "admin" in roles_config["roles"]
        assert "user" in roles_config["roles"]
        assert "readonly" in roles_config["roles"]

    @patch("mcp_security_framework.examples.comprehensive_example.CertificateManager")
    def test_demonstrate_certificate_management_success(self, mock_cert_manager):
        """Test successful certificate management demonstration."""
        # Mock certificate manager methods
        mock_manager = Mock()
        mock_cert_manager.return_value = mock_manager

        # Mock certificate creation results
        mock_ca_pair = Mock()
        mock_ca_pair.certificate_path = "/path/to/ca.crt"
        mock_ca_pair.private_key_path = "/path/to/ca.key"
        mock_ca_pair.serial_number = "123456789"

        mock_intermediate_pair = Mock()
        mock_intermediate_pair.certificate_path = "/path/to/intermediate.crt"
        mock_intermediate_pair.private_key_path = "/path/to/intermediate.key"
        mock_intermediate_pair.serial_number = "987654321"

        mock_server_pair = Mock()
        mock_server_pair.certificate_path = "/path/to/server.crt"
        mock_server_pair.private_key_path = "/path/to/server.key"
        mock_server_pair.serial_number = "111222333"

        mock_client_pair = Mock()
        mock_client_pair.certificate_path = "/path/to/client.crt"
        mock_client_pair.private_key_path = "/path/to/client.key"
        mock_client_pair.serial_number = "444555666"

        mock_manager.create_root_ca.return_value = mock_ca_pair
        mock_manager.create_intermediate_ca.return_value = mock_intermediate_pair
        mock_manager.create_server_certificate.return_value = mock_server_pair
        mock_manager.create_client_certificate.return_value = mock_client_pair
        mock_manager.create_certificate_signing_request.return_value = (
            "/path/to/csr.pem",
            "/path/to/csr.key",
        )
        mock_manager.create_crl.return_value = "/path/to/crl.pem"

        mock_cert_info = Mock()
        mock_cert_info.subject = "CN=test.example.com"
        mock_cert_info.issuer = "CN=Test CA"
        mock_cert_info.serial_number = "123456789"
        mock_cert_info.not_before = datetime.now(timezone.utc)
        mock_cert_info.not_after = datetime.now(timezone.utc)
        mock_cert_info.is_expired = False
        mock_manager.get_certificate_info.return_value = mock_cert_info

        # Run demonstration
        results = self.example.demonstrate_certificate_management()

        # Verify results
        assert "root_ca_creation" in results
        assert results["root_ca_creation"]["success"] is True
        assert "intermediate_ca_creation" in results
        assert results["intermediate_ca_creation"]["success"] is True
        assert "server_cert_creation" in results
        assert results["server_cert_creation"]["success"] is True
        assert "client_cert_creation" in results
        assert results["client_cert_creation"]["success"] is True
        assert "csr_creation" in results
        assert results["csr_creation"]["success"] is True
        assert "crl_creation" in results
        assert results["crl_creation"]["success"] is True
        assert "certificate_validation" in results
        assert results["certificate_validation"]["success"] is True

    def test_demonstrate_certificate_management_exception(self):
        """Test certificate management demonstration with exception."""
        # Mock certificate manager to raise exception
        with patch.object(self.example, "cert_manager") as mock_cert_manager:
            mock_cert_manager.create_root_ca.side_effect = Exception(
                "Certificate creation failed"
            )

            results = self.example.demonstrate_certificate_management()

            assert "error" in results
            assert "Certificate creation failed" in results["error"]

    def test_demonstrate_ssl_tls_management_success(self):
        """Test successful SSL/TLS management demonstration."""
        # Set certificate paths
        self.example.server_cert_path = "/path/to/server.crt"
        self.example.server_key_path = "/path/to/server.key"
        self.example.ca_cert_path = "/path/to/ca.crt"
        self.example.client_cert_path = "/path/to/client.crt"
        self.example.client_key_path = "/path/to/client.key"

        # Mock SSL manager methods
        with patch.object(self.example, "ssl_manager") as mock_ssl_manager:
            # Mock SSL contexts
            mock_server_context = Mock()
            mock_server_context.verify_mode = "CERT_REQUIRED"
            mock_server_context.minimum_version = "TLSv1.2"
            mock_server_context.maximum_version = "TLSv1.3"

            mock_client_context = Mock()
            mock_client_context.verify_mode = "CERT_REQUIRED"
            mock_client_context.minimum_version = "TLSv1.2"
            mock_client_context.maximum_version = "TLSv1.3"

            mock_ssl_manager.create_server_context.return_value = mock_server_context
            mock_ssl_manager.create_client_context.return_value = mock_client_context

            # Mock file existence
            with patch("os.path.exists", return_value=True):
                results = self.example.demonstrate_ssl_tls_management()

            # Verify results
            assert "server_context_creation" in results
            assert results["server_context_creation"]["success"] is True
            assert "client_context_creation" in results
            assert results["client_context_creation"]["success"] is True
            assert "mtls_context_creation" in results
            assert results["mtls_context_creation"]["success"] is True
            assert "ssl_validation" in results
            assert results["ssl_validation"]["success"] is True

    def test_demonstrate_ssl_tls_management_exception(self):
        """Test SSL/TLS management demonstration with exception."""
        # Mock SSL manager to raise exception
        with patch.object(self.example, "ssl_manager") as mock_ssl_manager:
            mock_ssl_manager.create_server_context.side_effect = Exception(
                "SSL context creation failed"
            )

            results = self.example.demonstrate_ssl_tls_management()

            assert "error" in results
            assert "SSL context creation failed" in results["error"]

    def test_demonstrate_authentication_success(self):
        """Test successful authentication demonstration."""
        # Set client certificate path
        self.example.client_cert_path = "/path/to/client.crt"

        # Mock security manager methods
        with patch.object(self.example, "security_manager") as mock_security_manager:
            # Mock authentication results
            success_auth_result = AuthResult(
                is_valid=True,
                username="test_user",
                roles=["user"],
                auth_method=AuthMethod.API_KEY,
                status=AuthStatus.SUCCESS,
            )

            failed_auth_result = AuthResult(
                is_valid=False,
                username=None,
                roles=[],
                auth_method=AuthMethod.API_KEY,
                status=AuthStatus.INVALID,
                error_code=-32001,
                error_message="Invalid API key",
            )

            mock_security_manager.authenticate_user.side_effect = [
                success_auth_result,  # API key auth
                success_auth_result,  # JWT auth
                success_auth_result,  # Certificate auth
                failed_auth_result,  # Failed auth
            ]

            # Mock file reading
            with patch("builtins.open", mock_open(read_data="test certificate")):
                results = self.example.demonstrate_authentication()

            # Verify results
            assert "api_key_auth" in results
            assert results["api_key_auth"]["success"] is True
            assert "jwt_auth" in results
            assert results["jwt_auth"]["success"] is True
            assert "certificate_auth" in results
            assert results["certificate_auth"]["success"] is True
            assert "failed_auth" in results
            assert results["failed_auth"]["success"] is False

    def test_demonstrate_authentication_exception(self):
        """Test authentication demonstration with exception."""
        # Mock security manager to raise exception
        with patch.object(self.example, "security_manager") as mock_security_manager:
            mock_security_manager.authenticate_user.side_effect = Exception(
                "Authentication failed"
            )

            results = self.example.demonstrate_authentication()

            assert "error" in results
            assert "Authentication failed" in results["error"]

    def test_demonstrate_authorization_success(self):
        """Test successful authorization demonstration."""
        # Mock security manager methods
        with patch.object(self.example, "security_manager") as mock_security_manager:
            # Mock authorization results
            success_result = ValidationResult(
                is_valid=True, status=ValidationStatus.VALID
            )

            failed_result = ValidationResult(
                is_valid=False, status=ValidationStatus.INVALID
            )

            mock_security_manager.check_permissions.side_effect = [
                success_result,  # Admin permissions
                success_result,  # User permissions
                success_result,  # Readonly permissions
                failed_result,  # Denied permissions
            ]

            results = self.example.demonstrate_authorization()

            # Verify results
            assert "admin_permissions" in results
            assert results["admin_permissions"]["success"] is True
            assert "user_permissions" in results
            assert results["user_permissions"]["success"] is True
            assert "readonly_permissions" in results
            assert results["readonly_permissions"]["success"] is True
            assert "denied_permissions" in results
            assert results["denied_permissions"]["success"] is False

    def test_demonstrate_authorization_exception(self):
        """Test authorization demonstration with exception."""
        # Mock security manager to raise exception
        with patch.object(self.example, "security_manager") as mock_security_manager:
            mock_security_manager.check_permissions.side_effect = Exception(
                "Authorization failed"
            )

            results = self.example.demonstrate_authorization()

            assert "error" in results
            assert "Authorization failed" in results["error"]

    def test_demonstrate_rate_limiting_success(self):
        """Test successful rate limiting demonstration."""
        # Mock security manager methods
        with patch.object(self.example, "security_manager") as mock_security_manager:
            # Mock rate limiting results (first 4 allowed, 5th denied)
            mock_security_manager.check_rate_limit.side_effect = [
                True,
                True,
                True,
                True,
                False,
            ]

            results = self.example.demonstrate_rate_limiting()

            # Verify results
            assert "rate_limit_checks" in results
            assert len(results["rate_limit_checks"]) == 5
            assert results["rate_limit_exceeded"] is True

    def test_demonstrate_rate_limiting_exception(self):
        """Test rate limiting demonstration with exception."""
        # Mock security manager to raise exception
        with patch.object(self.example, "security_manager") as mock_security_manager:
            mock_security_manager.check_rate_limit.side_effect = Exception(
                "Rate limiting failed"
            )

            results = self.example.demonstrate_rate_limiting()

            assert "error" in results
            assert "Rate limiting failed" in results["error"]

    def test_demonstrate_security_validation_success(self):
        """Test successful security validation demonstration."""
        # Mock security manager methods
        with patch.object(self.example, "security_manager") as mock_security_manager:
            # Mock validation results
            success_result = ValidationResult(
                is_valid=True, status=ValidationStatus.VALID
            )

            mock_security_manager.validate_request.return_value = success_result
            mock_security_manager.validate_configuration.return_value = success_result

            results = self.example.demonstrate_security_validation()

            # Verify results
            assert "request_validation" in results
            assert results["request_validation"]["success"] is True
            assert "configuration_validation" in results
            assert results["configuration_validation"]["success"] is True

    def test_demonstrate_security_validation_exception(self):
        """Test security validation demonstration with exception."""
        # Mock security manager to raise exception
        with patch.object(self.example, "security_manager") as mock_security_manager:
            mock_security_manager.validate_request.side_effect = Exception(
                "Validation failed"
            )

            results = self.example.demonstrate_security_validation()

            assert "error" in results
            assert "Validation failed" in results["error"]

    def test_demonstrate_security_monitoring_success(self):
        """Test successful security monitoring demonstration."""
        # Mock security manager methods
        with patch.object(self.example, "security_manager") as mock_security_manager:
            # Mock monitoring results
            mock_security_manager.get_security_status.return_value = {
                "status": "healthy"
            }
            mock_security_manager.get_security_metrics.return_value = {"requests": 100}

            results = self.example.demonstrate_security_monitoring()

            # Verify results
            assert "security_status" in results
            assert results["security_status"]["status"] == "healthy"
            assert "security_metrics" in results
            assert results["security_metrics"]["requests"] == 100
            assert "security_audit" in results

    def test_demonstrate_security_monitoring_exception(self):
        """Test security monitoring demonstration with exception."""
        # Mock security manager to raise exception
        with patch.object(self.example, "security_manager") as mock_security_manager:
            mock_security_manager.get_security_status.side_effect = Exception(
                "Monitoring failed"
            )

            results = self.example.demonstrate_security_monitoring()

            assert "error" in results
            assert "Monitoring failed" in results["error"]

    def test_update_config_after_certificates(self):
        """Test configuration update after certificate creation."""
        # Set certificate paths
        self.example.ca_cert_path = "/path/to/ca.crt"
        self.example.ca_key_path = "/path/to/ca.key"
        self.example.server_cert_path = "/path/to/server.crt"
        self.example.server_key_path = "/path/to/server.key"

        # Mock file existence and SSL manager creation
        with patch("os.path.exists", return_value=True), patch(
            "mcp_security_framework.examples.comprehensive_example.SSLManager"
        ) as mock_ssl_manager_class, patch(
            "mcp_security_framework.examples.comprehensive_example.CertificateManager"
        ) as mock_cert_manager_class:

            mock_ssl_manager = Mock()
            mock_cert_manager = Mock()
            mock_ssl_manager_class.return_value = mock_ssl_manager
            mock_cert_manager_class.return_value = mock_cert_manager

            self.example._update_config_after_certificates()

            # Verify configuration was updated
            assert self.example.config.certificates.enabled is True
            assert self.example.config.certificates.ca_cert_path == "/path/to/ca.crt"
            assert self.example.config.certificates.ca_key_path == "/path/to/ca.key"
            assert self.example.config.ssl.enabled is True
            assert self.example.config.ssl.cert_file == "/path/to/server.crt"
            assert self.example.config.ssl.key_file == "/path/to/server.key"
            assert self.example.config.ssl.ca_cert_file == "/path/to/ca.crt"

    @patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample.demonstrate_certificate_management"
    )
    @patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample.demonstrate_ssl_tls_management"
    )
    @patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample.demonstrate_authentication"
    )
    @patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample.demonstrate_authorization"
    )
    @patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample.demonstrate_rate_limiting"
    )
    @patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample.demonstrate_security_validation"
    )
    @patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample.demonstrate_security_monitoring"
    )
    def test_run_comprehensive_demo_success(
        self,
        mock_monitoring,
        mock_validation,
        mock_rate_limit,
        mock_authz,
        mock_auth,
        mock_ssl,
        mock_cert,
    ):
        """Test successful comprehensive demonstration."""
        # Mock all demonstration methods
        mock_cert.return_value = {"root_ca_creation": {"success": True}}
        mock_ssl.return_value = {"server_context_creation": {"success": True}}
        mock_auth.return_value = {"api_key_auth": {"success": True}}
        mock_authz.return_value = {"admin_permissions": {"success": True}}
        mock_rate_limit.return_value = {"rate_limit_checks": []}
        mock_validation.return_value = {"request_validation": {"success": True}}
        mock_monitoring.return_value = {"security_status": {"status": "healthy"}}

        results = self.example.run_comprehensive_demo()

        # Verify results structure
        assert "framework" in results
        assert "version" in results
        assert "timestamp" in results
        assert "certificate_management" in results
        assert "ssl_tls_management" in results
        assert "authentication" in results
        assert "authorization" in results
        assert "rate_limiting" in results
        assert "security_validation" in results
        assert "security_monitoring" in results

    def test_comprehensive_example_cleanup(self):
        """Test that working directory is properly cleaned up."""
        # Create a temporary example
        temp_example = ComprehensiveSecurityExample()
        work_dir = temp_example.work_dir

        # Verify directory exists
        assert os.path.exists(work_dir)

        # Clean up
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

        # Verify directory is removed
        assert not os.path.exists(work_dir)


def test_main_function():
    """Test the main function."""
    with patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample"
    ) as mock_example_class:
        mock_example = Mock()
        mock_example_class.return_value = mock_example

        # Mock the run_comprehensive_demo method
        mock_example.run_comprehensive_demo.return_value = {
            "framework": "MCP Security Framework",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "certificate_management": {
                "root_ca_creation": {"success": True},
                "intermediate_ca_creation": {"success": True},
                "server_cert_creation": {"success": True},
                "client_cert_creation": {"success": True},
                "csr_creation": {"success": True},
                "crl_creation": {"success": True},
                "certificate_validation": {"success": True},
            },
            "ssl_tls_management": {
                "server_context_creation": {"success": True},
                "client_context_creation": {"success": True},
                "mtls_context_creation": {"success": True},
                "ssl_validation": {"success": True},
            },
            "authentication": {
                "api_key_auth": {"success": True},
                "jwt_auth": {"success": True},
                "certificate_auth": {"success": True},
                "failed_auth": {"success": False},
            },
            "authorization": {
                "admin_permissions": {"success": True},
                "user_permissions": {"success": True},
                "readonly_permissions": {"success": True},
                "denied_permissions": {"success": False},
            },
            "rate_limiting": {
                "rate_limit_checks": [{"request": 1, "allowed": True}],
                "rate_limit_exceeded": False,
            },
            "security_validation": {
                "request_validation": {"success": True},
                "configuration_validation": {"success": True},
            },
            "security_monitoring": {
                "security_status": {"status": "healthy"},
                "security_metrics": {"requests": 100},
                "security_audit": {"authentication": []},
            },
        }

        # Mock cleanup
        mock_example.work_dir = "/tmp/test"

        # Import and run main function
        from mcp_security_framework.examples.comprehensive_example import main

        # Mock print to avoid output during tests
        with patch("builtins.print"):
            main()

        # Verify example was created and demo was run
        mock_example_class.assert_called_once()
        mock_example.run_comprehensive_demo.assert_called_once()


def test_main_function_exception():
    """Test main function with exception."""
    with patch(
        "mcp_security_framework.examples.comprehensive_example.ComprehensiveSecurityExample"
    ) as mock_example_class:
        mock_example = Mock()
        mock_example_class.return_value = mock_example

        # Mock the run_comprehensive_demo method to raise exception
        mock_example.run_comprehensive_demo.side_effect = Exception("Test exception")

        # Import and run main function
        from mcp_security_framework.examples.comprehensive_example import main

        # Mock print to avoid output during tests
        with patch("builtins.print"):
            main()

        # Verify example was created and demo was attempted
        mock_example_class.assert_called_once()
        mock_example.run_comprehensive_demo.assert_called_once()
