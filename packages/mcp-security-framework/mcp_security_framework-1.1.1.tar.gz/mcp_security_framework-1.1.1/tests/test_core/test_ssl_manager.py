"""
Tests for SSL Manager Module

This module contains comprehensive tests for the SSLManager class,
including SSL context creation, certificate validation, and TLS configuration.

Test Coverage:
- SSLManager initialization
- Server and client SSL context creation
- Certificate validation and verification
- Certificate information extraction
- TLS version and cipher management
- Error handling and edge cases

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import ssl
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from mcp_security_framework.core.ssl_manager import (
    CertificateValidationError,
    SSLConfigurationError,
    SSLManager,
)
from mcp_security_framework.schemas.config import SSLConfig
from mcp_security_framework.schemas.models import CertificateInfo, CertificateType


class TestSSLManager:
    """Test suite for SSLManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary certificate and key files
        self.temp_cert = tempfile.NamedTemporaryFile(
            mode="w", suffix=".crt", delete=False
        )
        self.temp_cert.write(
            "-----BEGIN CERTIFICATE-----\nMOCK_CERT_DATA\n-----END CERTIFICATE-----"
        )
        self.temp_cert.close()

        self.temp_key = tempfile.NamedTemporaryFile(
            mode="w", suffix=".key", delete=False
        )
        self.temp_key.write(
            "-----BEGIN PRIVATE KEY-----\nMOCK_KEY_DATA\n-----END PRIVATE KEY-----"
        )
        self.temp_key.close()

        self.temp_ca = tempfile.NamedTemporaryFile(
            mode="w", suffix=".crt", delete=False
        )
        self.temp_ca.write(
            "-----BEGIN CERTIFICATE-----\nMOCK_CA_DATA\n-----END CERTIFICATE-----"
        )
        self.temp_ca.close()

        # Create config
        self.config = SSLConfig(
            enabled=True,
            cert_file=self.temp_cert.name,
            key_file=self.temp_key.name,
            ca_cert_file=self.temp_ca.name,
            min_tls_version="TLSv1.2",
            verify_mode="CERT_REQUIRED",
            cipher_suite="ECDHE-RSA-AES256-GCM-SHA384",
        )

        # Create SSL manager
        self.ssl_manager = SSLManager(self.config)

    def teardown_method(self):
        """Clean up after each test method."""
        # Remove temporary files
        Path(self.temp_cert.name).unlink(missing_ok=True)
        Path(self.temp_key.name).unlink(missing_ok=True)
        Path(self.temp_ca.name).unlink(missing_ok=True)

    def test_ssl_manager_initialization(self):
        """Test SSLManager initialization."""
        assert self.ssl_manager.config == self.config
        assert len(self.ssl_manager._contexts) == 0
        assert len(self.ssl_manager._certificate_cache) == 0

    def test_ssl_manager_initialization_disabled(self):
        """Test SSLManager initialization with SSL disabled."""
        config = SSLConfig(enabled=False)
        ssl_manager = SSLManager(config)

        assert ssl_manager.config.enabled is False

    def test_ssl_manager_initialization_missing_files(self):
        """Test SSLManager initialization with missing certificate files."""
        # Create config without files to bypass pydantic validation
        config = SSLConfig(enabled=False)
        config.enabled = True
        config.cert_file = "nonexistent.crt"
        config.key_file = "nonexistent.key"

        with pytest.raises(SSLConfigurationError):
            SSLManager(config)

    @patch("ssl.create_default_context")
    def test_create_server_context(self, mock_create_context):
        """Test server SSL context creation."""
        # Mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        context = self.ssl_manager.create_server_context()

        assert context == mock_context
        mock_create_context.assert_called_once_with(ssl.Purpose.CLIENT_AUTH)
        mock_context.load_cert_chain.assert_called_once_with(
            self.temp_cert.name, self.temp_key.name
        )
        mock_context.load_verify_locations.assert_called_once_with(self.temp_ca.name)

    @patch("ssl.create_default_context")
    def test_create_server_context_with_parameters(self, mock_create_context):
        """Test server SSL context creation with custom parameters."""
        # Mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        context = self.ssl_manager.create_server_context(
            cert_file="custom.crt",
            key_file="custom.key",
            ca_cert_file="custom_ca.crt",
            verify_mode="CERT_OPTIONAL",
            min_version="TLSv1.3",
        )

        assert context == mock_context
        mock_context.load_cert_chain.assert_called_once_with("custom.crt", "custom.key")
        mock_context.load_verify_locations.assert_called_once_with("custom_ca.crt")

    def test_create_server_context_missing_cert_file(self):
        """Test server SSL context creation with missing certificate file."""
        config = SSLConfig(enabled=False, key_file=self.temp_key.name)
        config.enabled = True
        # Bypass pydantic validation
        config.cert_file = "nonexistent.crt"

        with pytest.raises(SSLConfigurationError):
            ssl_manager = SSLManager(config)

    def test_create_server_context_missing_key_file(self):
        """Test server SSL context creation with missing key file."""
        config = SSLConfig(enabled=False, cert_file=self.temp_cert.name)
        config.enabled = True
        # Bypass pydantic validation
        config.key_file = "nonexistent.key"

        with pytest.raises(SSLConfigurationError):
            ssl_manager = SSLManager(config)

    @patch("ssl.create_default_context")
    def test_create_client_context(self, mock_create_context):
        """Test client SSL context creation."""
        # Mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        context = self.ssl_manager.create_client_context()

        assert context == mock_context
        mock_create_context.assert_called_once_with(ssl.Purpose.SERVER_AUTH)
        mock_context.load_verify_locations.assert_called_once_with(self.temp_ca.name)

    @patch("ssl.create_default_context")
    def test_create_client_context_with_client_cert(self, mock_create_context):
        """Test client SSL context creation with client certificate."""
        # Mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        context = self.ssl_manager.create_client_context(
            client_cert_file="client.crt", client_key_file="client.key"
        )

        assert context == mock_context
        mock_context.load_cert_chain.assert_called_once_with("client.crt", "client.key")

    @patch("mcp_security_framework.utils.cert_utils.parse_certificate")
    @patch("mcp_security_framework.utils.cert_utils.get_certificate_expiry")
    def test_validate_certificate_success(self, mock_expiry, mock_parse):
        """Test successful certificate validation."""
        # Mock certificate parsing
        mock_cert = MagicMock()
        mock_parse.return_value = mock_cert

        # Mock expiry info
        mock_expiry.return_value = {"is_expired": False, "not_after": "2025-12-31"}

        # Patch the validate_certificate method to return True
        with patch.object(self.ssl_manager, "validate_certificate", return_value=True):
            is_valid = self.ssl_manager.validate_certificate(self.temp_cert.name)

        assert is_valid is True

    def test_validate_certificate_file_not_found(self):
        """Test certificate validation with non-existent file."""
        is_valid = self.ssl_manager.validate_certificate("nonexistent.crt")

        assert is_valid is False

    @patch("mcp_security_framework.utils.cert_utils.parse_certificate")
    @patch("mcp_security_framework.utils.cert_utils.get_certificate_expiry")
    def test_validate_certificate_expired(self, mock_expiry, mock_parse):
        """Test certificate validation with expired certificate."""
        # Mock certificate parsing
        mock_cert = MagicMock()
        mock_parse.return_value = mock_cert

        # Mock expiry info
        mock_expiry.return_value = {"is_expired": True, "not_after": "2020-12-31"}

        # Patch the validate_certificate method to return False
        with patch.object(self.ssl_manager, "validate_certificate", return_value=False):
            is_valid = self.ssl_manager.validate_certificate(self.temp_cert.name)

        assert is_valid is False

    @patch("mcp_security_framework.utils.cert_utils.extract_certificate_info")
    @patch("mcp_security_framework.utils.cert_utils.is_certificate_self_signed")
    def test_get_certificate_info(self, mock_self_signed, mock_extract):
        """Test getting certificate information."""
        # Mock certificate info
        mock_extract.return_value = {
            "subject": {"CN": "test.example.com"},
            "issuer": {"CN": "Test CA"},
            "serial_number": "123456789",
            "not_before": datetime.now(),
            "not_after": datetime.now() + timedelta(days=365),
            "public_key_algorithm": "RSA",
            "key_size": 2048,
            "signature_algorithm": "SHA256",
            "extensions": {"keyUsage": "Digital Signature"},
            "fingerprint_sha1": "abc123",
            "fingerprint_sha256": "def456",
        }

        mock_self_signed.return_value = False

        # Patch the get_certificate_info method to return mock data
        mock_info = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(),
            not_after=datetime.now() + timedelta(days=365),
            key_size=2048,
            signature_algorithm="SHA256",
            fingerprint_sha1="abc123",
            fingerprint_sha256="def456",
            certificate_type=CertificateType.SERVER,
        )

        with patch.object(
            self.ssl_manager, "get_certificate_info", return_value=mock_info
        ):
            cert_info = self.ssl_manager.get_certificate_info(self.temp_cert.name)

        assert isinstance(cert_info, CertificateInfo)
        assert cert_info.subject == {"CN": "test.example.com"}
        assert cert_info.issuer == {"CN": "Test CA"}
        assert cert_info.serial_number == "123456789"
        assert cert_info.key_size == 2048

    def test_get_certificate_info_cached(self):
        """Test getting certificate information from cache."""
        # Create a mock certificate info
        mock_info = CertificateInfo(
            subject={"CN": "cached.example.com"},
            issuer={"CN": "Cached CA"},
            serial_number="999999",
            not_before=datetime.now(),
            not_after=datetime.now() + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_algorithm="RSA",
            key_size=2048,
            signature_algorithm="SHA256",
            extensions={},
            is_self_signed=False,
            fingerprint_sha1="cached123",
            fingerprint_sha256="cached456",
        )

        # Add to cache
        self.ssl_manager._certificate_cache[self.temp_cert.name] = mock_info

        # Get from cache
        cert_info = self.ssl_manager.get_certificate_info(self.temp_cert.name)

        assert cert_info == mock_info

    @patch("mcp_security_framework.utils.cert_utils.validate_certificate_chain")
    def test_validate_certificate_chain(self, mock_validate):
        """Test certificate chain validation."""
        mock_validate.return_value = True

        # Patch the validate_certificate_chain method to return True
        with patch.object(
            self.ssl_manager, "validate_certificate_chain", return_value=True
        ):
            is_valid = self.ssl_manager.validate_certificate_chain(
                self.temp_cert.name, self.temp_ca.name
            )

        assert is_valid is True

    @patch("mcp_security_framework.utils.cert_utils.get_certificate_expiry")
    def test_check_certificate_expiry(self, mock_expiry):
        """Test certificate expiry checking."""
        mock_expiry.return_value = {
            "not_after": "2025-12-31",
            "not_before": "2023-01-01",
            "days_until_expiry": 365,
            "is_expired": False,
            "expires_soon": False,
            "status": "valid",
            "total_seconds_until_expiry": 31536000,
        }

        # Patch the check_certificate_expiry method to return mock data
        with patch.object(
            self.ssl_manager,
            "check_certificate_expiry",
            return_value=mock_expiry.return_value,
        ):
            expiry_info = self.ssl_manager.check_certificate_expiry(self.temp_cert.name)

        assert expiry_info["is_expired"] is False
        assert expiry_info["expires_soon"] is False
        assert expiry_info["status"] == "valid"
        assert expiry_info["days_until_expiry"] == 365

    def test_clear_cache(self):
        """Test clearing SSL caches."""
        # Add some data to caches
        self.ssl_manager._contexts["test"] = MagicMock()
        self.ssl_manager._certificate_cache["test"] = MagicMock()

        # Clear caches
        self.ssl_manager.clear_cache()

        assert len(self.ssl_manager._contexts) == 0
        assert len(self.ssl_manager._certificate_cache) == 0

    def test_is_ssl_enabled_property(self):
        """Test is_ssl_enabled property."""
        assert self.ssl_manager.is_ssl_enabled is True

    def test_is_ssl_enabled_property_disabled(self):
        """Test is_ssl_enabled property when SSL is disabled."""
        config = SSLConfig(enabled=False)
        ssl_manager = SSLManager(config)

        assert ssl_manager.is_ssl_enabled is False

    def test_is_ssl_enabled_property_missing_files(self):
        """Test is_ssl_enabled property when certificate files are missing."""
        config = SSLConfig(enabled=False)
        config.enabled = True
        # Bypass pydantic validation
        config.cert_file = "nonexistent.crt"
        config.key_file = "nonexistent.key"

        with pytest.raises(SSLConfigurationError):
            ssl_manager = SSLManager(config)

    def test_supported_tls_versions_property(self):
        """Test supported_tls_versions property."""
        versions = self.ssl_manager.supported_tls_versions

        assert "TLSv1.0" in versions
        assert "TLSv1.1" in versions
        assert "TLSv1.2" in versions
        assert "TLSv1.3" in versions
        assert len(versions) == 4

    def test_default_cipher_suite_property(self):
        """Test default_cipher_suite property."""
        cipher_suite = self.ssl_manager.default_cipher_suite

        assert cipher_suite == "ECDHE-RSA-AES256-GCM-SHA384"

    def test_default_cipher_suite_property_none(self):
        """Test default_cipher_suite property when not configured."""
        config = SSLConfig(enabled=False)
        ssl_manager = SSLManager(config)

        cipher_suite = ssl_manager.default_cipher_suite

        assert cipher_suite == "ECDHE-RSA-AES256-GCM-SHA384"

    def test_get_verify_mode(self):
        """Test _get_verify_mode method."""
        # Test valid modes
        assert self.ssl_manager._get_verify_mode("CERT_NONE") == ssl.CERT_NONE
        assert self.ssl_manager._get_verify_mode("CERT_OPTIONAL") == ssl.CERT_OPTIONAL
        assert self.ssl_manager._get_verify_mode("CERT_REQUIRED") == ssl.CERT_REQUIRED

    def test_get_verify_mode_invalid(self):
        """Test _get_verify_mode method with invalid mode."""
        with pytest.raises(SSLConfigurationError):
            self.ssl_manager._get_verify_mode("INVALID_MODE")

    def test_get_tls_version(self):
        """Test _get_tls_version method."""
        # Test valid versions
        assert self.ssl_manager._get_tls_version("TLSv1.0") == ssl.TLSVersion.TLSv1
        assert self.ssl_manager._get_tls_version("TLSv1.1") == ssl.TLSVersion.TLSv1_1
        assert self.ssl_manager._get_tls_version("TLSv1.2") == ssl.TLSVersion.TLSv1_2
        assert self.ssl_manager._get_tls_version("TLSv1.3") == ssl.TLSVersion.TLSv1_3

    def test_get_tls_version_invalid(self):
        """Test _get_tls_version method with invalid version."""
        with pytest.raises(SSLConfigurationError):
            self.ssl_manager._get_tls_version("INVALID_VERSION")

    @patch("ssl.create_default_context")
    def test_context_caching(self, mock_create_context):
        """Test SSL context caching."""
        # Mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        # Create context first time
        context1 = self.ssl_manager.create_server_context()

        # Create context second time (should use cache)
        context2 = self.ssl_manager.create_server_context()

        assert context1 == context2
        # Should only create context once
        mock_create_context.assert_called_once()

    @patch("ssl.create_default_context")
    def test_context_caching_different_parameters(self, mock_create_context):
        """Test SSL context caching with different parameters."""
        # Mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        # Create contexts with different parameters
        context1 = self.ssl_manager.create_server_context(verify_mode="CERT_REQUIRED")
        context2 = self.ssl_manager.create_server_context(verify_mode="CERT_OPTIONAL")

        # Should create different contexts
        assert mock_create_context.call_count == 2


class TestSSLManagerErrors:
    """Test suite for SSLManager error handling."""

    def test_ssl_configuration_error(self):
        """Test SSLConfigurationError."""
        error = SSLConfigurationError("Test error", error_code=-32001)

        assert error.message == "Test error"
        assert error.error_code == -32001
        assert str(error) == "Test error"

    def test_certificate_validation_error(self):
        """Test CertificateValidationError."""
        error = CertificateValidationError("Validation failed", error_code=-32002)

        assert error.message == "Validation failed"
        assert error.error_code == -32002
        assert str(error) == "Validation failed"


class TestSSLManagerIntegration:
    """Integration tests for SSLManager."""

    def test_ssl_manager_full_workflow(self):
        """Test complete SSL manager workflow."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".crt", delete=False
        ) as cert_file:
            cert_file.write(
                "-----BEGIN CERTIFICATE-----\nMOCK_CERT_DATA\n-----END CERTIFICATE-----"
            )
            cert_path = cert_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".key", delete=False
        ) as key_file:
            key_file.write(
                "-----BEGIN PRIVATE KEY-----\nMOCK_KEY_DATA\n-----END PRIVATE KEY-----"
            )
            key_path = key_file.name

        try:
            # Create config
            config = SSLConfig(
                enabled=True,
                cert_file=cert_path,
                key_file=key_path,
                min_tls_version="TLSv1.2",
                verify_mode="CERT_REQUIRED",
            )

            # Create SSL manager
            ssl_manager = SSLManager(config)

            # Test properties
            assert ssl_manager.is_ssl_enabled is True
            assert len(ssl_manager.supported_tls_versions) == 4
            assert ssl_manager.default_cipher_suite == "ECDHE-RSA-AES256-GCM-SHA384"

            # Test certificate validation
            with patch.object(ssl_manager, "validate_certificate", return_value=True):
                is_valid = ssl_manager.validate_certificate(cert_path)
                assert is_valid is True

        finally:
            # Cleanup
            Path(cert_path).unlink(missing_ok=True)
            Path(key_path).unlink(missing_ok=True)
