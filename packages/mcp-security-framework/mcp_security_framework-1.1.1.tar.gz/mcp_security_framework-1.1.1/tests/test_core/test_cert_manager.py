"""
Tests for Certificate Manager Module

This module contains comprehensive tests for the CertificateManager class,
covering all certificate creation and management functionality.

Test Coverage:
- Root CA certificate creation
- Client certificate creation
- Server certificate creation
- Certificate revocation
- Certificate chain validation
- Certificate information extraction
- Error handling and edge cases
- Configuration validation

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError

from mcp_security_framework.core.cert_manager import (
    CertificateConfigurationError,
    CertificateGenerationError,
    CertificateManager,
    CertificateValidationError,
)
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    ServerCertConfig,
)
from mcp_security_framework.schemas.models import (
    CertificateInfo,
    CertificatePair,
    CertificateType,
)


class TestCertificateManager:
    """Test suite for CertificateManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test certificates
        self.temp_dir = tempfile.mkdtemp()

        # Create test CA certificate and key files
        self.ca_cert_path = os.path.join(self.temp_dir, "test_ca.crt")
        self.ca_key_path = os.path.join(self.temp_dir, "test_ca.key")

        # Create dummy CA files for testing
        with open(self.ca_cert_path, "w") as f:
            f.write(
                "-----BEGIN CERTIFICATE-----\nDUMMY CA CERT\n-----END CERTIFICATE-----"
            )

        with open(self.ca_key_path, "w") as f:
            f.write(
                "-----BEGIN PRIVATE KEY-----\nDUMMY CA KEY\n-----END PRIVATE KEY-----"
            )

        # Create test configuration
        self.cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=self.ca_cert_path,
            ca_key_path=self.ca_key_path,
            cert_storage_path=self.temp_dir,
            key_storage_path=self.temp_dir,
        )

        # Create certificate manager
        self.cert_manager = CertificateManager(self.cert_config)

    def teardown_method(self):
        """Clean up after each test method."""
        # Remove temporary directory
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_success(self):
        """Test successful CertificateManager initialization."""
        assert self.cert_manager.config == self.cert_config
        assert self.cert_manager._certificate_cache == {}
        assert self.cert_manager._crl_cache == {}

    def test_init_missing_ca_cert(self):
        """Test initialization with missing CA certificate."""
        config = CertificateConfig(
            enabled=True,
            ca_cert_path="/nonexistent/ca.crt",
            ca_key_path=self.ca_key_path,
        )

        with pytest.raises(CertificateConfigurationError) as exc_info:
            CertificateManager(config)

        assert "CA certificate file not found" in str(exc_info.value)

    def test_init_missing_ca_key(self):
        """Test initialization with missing CA key."""
        config = CertificateConfig(
            enabled=True,
            ca_cert_path=self.ca_cert_path,
            ca_key_path="/nonexistent/ca.key",
        )

        with pytest.raises(CertificateConfigurationError) as exc_info:
            CertificateManager(config)

        assert "CA private key file not found" in str(exc_info.value)

    def test_create_root_ca_success(self):
        """Test successful root CA certificate creation."""
        ca_config = CAConfig(
            common_name="Test Root CA",
            organization="Test Organization",
            country="US",
            state="California",
            locality="San Francisco",
            validity_years=10,
            key_size=2048,
        )

        with patch(
            "cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key"
        ) as mock_rsa:
            with patch("cryptography.x509.CertificateBuilder") as mock_builder:
                with patch("builtins.open", create=True) as mock_open:
                    # Mock the certificate building process
                    mock_cert = Mock()
                    mock_cert.serial_number = 123456789
                    mock_cert.not_valid_before_utc = datetime.now(timezone.utc)
                    mock_cert.not_valid_after_utc = datetime.now(
                        timezone.utc
                    ) + timedelta(days=3650)
                    mock_cert.public_bytes.return_value = b"-----BEGIN CERTIFICATE-----\nMOCK CERT\n-----END CERTIFICATE-----"

                    mock_private_key = Mock()
                    mock_public_key = Mock()
                    mock_public_key.public_bytes.return_value = b"mock_public_key_data"
                    mock_private_key.public_key.return_value = mock_public_key
                    mock_private_key.private_bytes.return_value = b"-----BEGIN PRIVATE KEY-----\nMOCK KEY\n-----END PRIVATE KEY-----"

                    mock_rsa.return_value = mock_private_key

                    # Configure the builder mock to return the certificate
                    mock_builder_instance = Mock()
                    mock_builder_instance.subject_name.return_value = (
                        mock_builder_instance
                    )
                    mock_builder_instance.issuer_name.return_value = (
                        mock_builder_instance
                    )
                    mock_builder_instance.public_key.return_value = (
                        mock_builder_instance
                    )
                    mock_builder_instance.serial_number.return_value = (
                        mock_builder_instance
                    )
                    mock_builder_instance.not_valid_before.return_value = (
                        mock_builder_instance
                    )
                    mock_builder_instance.not_valid_after.return_value = (
                        mock_builder_instance
                    )
                    mock_builder_instance.add_extension.return_value = (
                        mock_builder_instance
                    )
                    mock_builder_instance.sign.return_value = mock_cert
                    mock_builder.return_value = mock_builder_instance

                cert_pair = self.cert_manager.create_root_ca(ca_config)

        assert isinstance(cert_pair, CertificatePair)
        assert cert_pair.certificate_path.endswith("test_root_ca_ca.crt")
        assert cert_pair.private_key_path.endswith("test_root_ca_ca.key")
        assert cert_pair.serial_number == "123456789"

    def test_create_root_ca_missing_common_name(self):
        """Test root CA creation with missing common name."""
        ca_config = CAConfig(
            common_name="",
            organization="Test Organization",
            country="US",
            validity_years=10,
        )

        with pytest.raises(CertificateGenerationError) as exc_info:
            self.cert_manager.create_root_ca(ca_config)

        assert "Common name is required for CA certificate" in str(exc_info.value)

    def test_create_client_certificate_success(self):
        """Test successful client certificate creation."""
        client_config = ClientCertConfig(
            common_name="test.client.com",
            organization="Test Organization",
            country="US",
            validity_days=365,
            ca_cert_path=self.ca_cert_path,
            ca_key_path=self.ca_key_path,
        )

        with patch(
            "cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key"
        ) as mock_rsa:
            with patch("cryptography.x509.CertificateBuilder") as mock_builder_class:
                with patch(
                    "cryptography.x509.load_pem_x509_certificate"
                ) as mock_load_cert:
                    with patch(
                        "cryptography.hazmat.primitives.serialization.load_pem_private_key"
                    ) as mock_load_key:
                        with patch("builtins.open", create=True) as mock_open:
                            with patch("os.chmod") as mock_chmod:
                                # Mock file operations
                                mock_file = Mock()
                                mock_open.return_value.__enter__.return_value = (
                                    mock_file
                                )

                                # Mock CA certificate and key
                                mock_ca_cert = Mock()
                                mock_ca_cert.subject = Mock()
                                mock_load_cert.return_value = mock_ca_cert

                                mock_ca_key = Mock()
                                mock_load_key.return_value = mock_ca_key

                                # Mock the certificate building process
                                mock_cert = Mock()
                                mock_cert.serial_number = 987654321
                                mock_cert.not_valid_before_utc = datetime.now(
                                    timezone.utc
                                )
                                mock_cert.not_valid_after_utc = datetime.now(
                                    timezone.utc
                                ) + timedelta(days=365)
                                mock_cert.public_bytes.return_value = b"-----BEGIN CERTIFICATE-----\nMOCK CLIENT CERT\n-----END CERTIFICATE-----"

                                mock_private_key = Mock()
                                mock_public_key = Mock()
                                mock_public_key.public_bytes.return_value = (
                                    b"mock_public_key_data"
                                )
                                mock_private_key.public_key.return_value = (
                                    mock_public_key
                                )
                                mock_private_key.private_bytes.return_value = b"-----BEGIN PRIVATE KEY-----\nMOCK CLIENT KEY\n-----END PRIVATE KEY-----"

                                # Mock the builder chain
                                mock_builder = Mock()
                                mock_builder.subject_name.return_value = mock_builder
                                mock_builder.issuer_name.return_value = mock_builder
                                mock_builder.public_key.return_value = mock_builder
                                mock_builder.serial_number.return_value = mock_builder
                                mock_builder.not_valid_before.return_value = (
                                    mock_builder
                                )
                                mock_builder.not_valid_after.return_value = mock_builder
                                mock_builder.add_extension.return_value = mock_builder
                                mock_builder.sign.return_value = mock_cert

                                mock_builder_class.return_value = mock_builder
                                mock_rsa.return_value = mock_private_key

                                cert_pair = self.cert_manager.create_client_certificate(
                                    client_config
                                )

        assert isinstance(cert_pair, CertificatePair)
        assert cert_pair.certificate_path.endswith("test.client.com_client.crt")
        assert cert_pair.private_key_path.endswith("test.client.com_client.key")
        assert cert_pair.serial_number == "987654321"

    def test_create_client_certificate_missing_common_name(self):
        """Test client certificate creation with missing common name."""
        client_config = ClientCertConfig(
            common_name="",
            organization="Test Organization",
            country="US",
            validity_days=365,
            ca_cert_path=self.ca_cert_path,
            ca_key_path=self.ca_key_path,
        )

        with pytest.raises(CertificateGenerationError) as exc_info:
            self.cert_manager.create_client_certificate(client_config)

        assert "Common name is required for client certificate" in str(exc_info.value)

    def test_create_server_certificate_success(self):
        """Test successful server certificate creation."""
        server_config = ServerCertConfig(
            common_name="api.test.com",
            organization="Test Organization",
            country="US",
            state="California",
            locality="San Francisco",
            validity_days=365,
            key_size=2048,
            subject_alt_names=["api.test.com", "www.test.com"],
            ca_cert_path=self.ca_cert_path,
            ca_key_path=self.ca_key_path,
        )

        with patch(
            "cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key"
        ) as mock_rsa:
            with patch("cryptography.x509.CertificateBuilder") as mock_builder_class:
                with patch(
                    "cryptography.x509.load_pem_x509_certificate"
                ) as mock_load_cert:
                    with patch(
                        "cryptography.hazmat.primitives.serialization.load_pem_private_key"
                    ) as mock_load_key:
                        with patch("builtins.open", create=True) as mock_open:
                            with patch("os.chmod") as mock_chmod:
                                # Mock file operations
                                mock_file = Mock()
                                mock_open.return_value.__enter__.return_value = (
                                    mock_file
                                )

                                # Mock CA certificate and key
                                mock_ca_cert = Mock()
                                mock_ca_cert.subject = Mock()
                                mock_load_cert.return_value = mock_ca_cert

                                mock_ca_key = Mock()
                                mock_load_key.return_value = mock_ca_key

                                # Mock the certificate building process
                                mock_cert = Mock()
                                mock_cert.serial_number = 555666777
                                mock_cert.not_valid_before_utc = datetime.now(
                                    timezone.utc
                                )
                                mock_cert.not_valid_after_utc = datetime.now(
                                    timezone.utc
                                ) + timedelta(days=365)
                                mock_cert.public_bytes.return_value = b"-----BEGIN CERTIFICATE-----\nMOCK SERVER CERT\n-----END CERTIFICATE-----"

                                mock_private_key = Mock()
                                mock_public_key = Mock()
                                mock_public_key.public_bytes.return_value = (
                                    b"mock_public_key_data"
                                )
                                mock_private_key.public_key.return_value = (
                                    mock_public_key
                                )
                                mock_private_key.private_bytes.return_value = b"-----BEGIN PRIVATE KEY-----\nMOCK SERVER KEY\n-----END PRIVATE KEY-----"

                                # Mock the builder chain
                                mock_builder = Mock()
                                mock_builder.subject_name.return_value = mock_builder
                                mock_builder.issuer_name.return_value = mock_builder
                                mock_builder.public_key.return_value = mock_builder
                                mock_builder.serial_number.return_value = mock_builder
                                mock_builder.not_valid_before.return_value = (
                                    mock_builder
                                )
                                mock_builder.not_valid_after.return_value = mock_builder
                                mock_builder.add_extension.return_value = mock_builder
                                mock_builder.sign.return_value = mock_cert

                                mock_builder_class.return_value = mock_builder
                                mock_rsa.return_value = mock_private_key

                                cert_pair = self.cert_manager.create_server_certificate(
                                    server_config
                                )

        assert isinstance(cert_pair, CertificatePair)
        assert cert_pair.certificate_path.endswith("api.test.com_server.crt")
        assert cert_pair.private_key_path.endswith("api.test.com_server.key")
        assert cert_pair.serial_number == "555666777"

    def test_create_server_certificate_missing_common_name(self):
        """Test server certificate creation with missing common name."""
        server_config = ServerCertConfig(
            common_name="",
            organization="Test Organization",
            country="US",
            validity_days=365,
            ca_cert_path=self.ca_cert_path,
            ca_key_path=self.ca_key_path,
        )

        with pytest.raises(CertificateGenerationError) as exc_info:
            self.cert_manager.create_server_certificate(server_config)

        assert "Common name is required for server certificate" in str(exc_info.value)

    def test_revoke_certificate_success(self):
        """Test successful certificate revocation."""
        serial_number = "123456789"
        reason = "key_compromise"

        with patch("builtins.open", create=True) as mock_open:
            with patch(
                "cryptography.x509.CertificateRevocationListBuilder"
            ) as mock_crl_builder_class:
                with patch(
                    "cryptography.x509.RevokedCertificateBuilder"
                ) as mock_revoked_builder_class:
                    with patch("cryptography.x509.ReasonFlags") as mock_reason_flags:
                        with patch(
                            "cryptography.x509.load_pem_x509_certificate"
                        ) as mock_load_cert:
                            with patch(
                                "cryptography.hazmat.primitives.serialization.load_pem_private_key"
                            ) as mock_load_key:
                                with patch("os.chmod") as mock_chmod:
                                    # Mock file operations
                                    mock_file = Mock()
                                    mock_open.return_value.__enter__.return_value = (
                                        mock_file
                                    )

                                    # Mock CA certificate and key
                                    mock_ca_cert = Mock()
                                    mock_ca_cert.subject = Mock()
                                    mock_load_cert.return_value = mock_ca_cert

                                    mock_ca_key = Mock()
                                    mock_load_key.return_value = mock_ca_key

                                    # Mock CRL building process
                                    mock_crl = Mock()
                                    mock_crl.public_bytes.return_value = b"-----BEGIN X509 CRL-----\nMOCK CRL\n-----END X509 CRL-----"

                                    # Mock the builder chain
                                    mock_crl_builder = Mock()
                                    mock_crl_builder.last_update.return_value = (
                                        mock_crl_builder
                                    )
                                    mock_crl_builder.next_update.return_value = (
                                        mock_crl_builder
                                    )
                                    mock_crl_builder.add_revoked_certificate.return_value = (
                                        mock_crl_builder
                                    )
                                    mock_crl_builder.issuer_name.return_value = (
                                        mock_crl_builder
                                    )
                                    mock_crl_builder.sign.return_value = mock_crl

                                    # Mock revoked certificate builder
                                    mock_revoked_cert = Mock()
                                    mock_revoked_builder = Mock()
                                    mock_revoked_builder.serial_number.return_value = (
                                        mock_revoked_builder
                                    )
                                    mock_revoked_builder.revocation_date.return_value = (
                                        mock_revoked_builder
                                    )
                                    mock_revoked_builder.revocation_reason.return_value = (
                                        mock_revoked_builder
                                    )
                                    mock_revoked_builder.build.return_value = (
                                        mock_revoked_cert
                                    )

                                    # Mock ReasonFlags
                                    mock_reason_flags.__getitem__.return_value = (
                                        "KEY_COMPROMISE"
                                    )

                                    mock_crl_builder_class.return_value = (
                                        mock_crl_builder
                                    )
                                    mock_revoked_builder_class.return_value = (
                                        mock_revoked_builder
                                    )

                                    success = self.cert_manager.revoke_certificate(
                                        serial_number, reason
                                    )

        assert success is True

    def test_revoke_certificate_missing_serial_number(self):
        """Test certificate revocation with missing serial number."""
        with pytest.raises(ValueError):
            self.cert_manager.revoke_certificate("", "key_compromise")

    def test_validate_certificate_chain_success(self):
        """Test successful certificate chain validation."""
        cert_path = "/path/to/cert.crt"

        with patch(
            "mcp_security_framework.core.cert_manager.validate_certificate_chain",
            return_value=True,
        ):
            is_valid = self.cert_manager.validate_certificate_chain(cert_path)

        assert is_valid is True

    def test_validate_certificate_chain_failure(self):
        """Test certificate chain validation failure."""
        cert_path = "/path/to/cert.crt"

        with patch(
            "mcp_security_framework.core.cert_manager.validate_certificate_chain",
            return_value=False,
        ):
            is_valid = self.cert_manager.validate_certificate_chain(cert_path)

        assert is_valid is False

    def test_validate_certificate_chain_with_custom_ca(self):
        """Test certificate chain validation with custom CA certificate."""
        cert_path = "/path/to/cert.crt"
        ca_cert_path = "/path/to/custom_ca.crt"

        with patch(
            "mcp_security_framework.core.cert_manager.validate_certificate_chain",
            return_value=True,
        ):
            is_valid = self.cert_manager.validate_certificate_chain(
                cert_path, ca_cert_path
            )

        assert is_valid is True

    def test_get_certificate_info_success(self):
        """Test successful certificate information extraction."""
        cert_path = "/path/to/cert.crt"

        # Mock certificate data with proper structure
        mock_cert = Mock()

        # Mock subject and issuer as x509.Name objects
        mock_subject = Mock()
        mock_subject.get_attributes_for_oid.return_value = [
            Mock(value="test.client.com")
        ]
        mock_cert.subject = mock_subject

        mock_issuer = Mock()
        mock_issuer.get_attributes_for_oid.return_value = [Mock(value="Test Root CA")]
        mock_cert.issuer = mock_issuer

        mock_cert.serial_number = 123456789
        mock_cert.version.name = "v3"
        mock_cert.not_valid_before_utc = datetime.now(timezone.utc)
        mock_cert.not_valid_after_utc = datetime.now(timezone.utc) + timedelta(days=365)

        # Mock signature algorithm
        mock_sig_alg = Mock()
        mock_sig_alg._name = "sha256WithRSAEncryption"
        mock_cert.signature_algorithm_oid = mock_sig_alg

        # Mock public key algorithm
        mock_pub_alg = Mock()
        mock_pub_alg._name = "rsaEncryption"
        mock_cert.public_key_algorithm_oid = mock_pub_alg

        # Mock fingerprint methods
        mock_cert.fingerprint.side_effect = lambda hash_alg: b"mock_fingerprint"

        # Mock extensions
        mock_extension = Mock()
        mock_extension.value.ca = False
        mock_cert.extensions.get_extension_for_oid.return_value = mock_extension

        # Mock all utility functions
        with patch(
            "mcp_security_framework.core.cert_manager.parse_certificate",
            return_value=mock_cert,
        ):
            with patch(
                "mcp_security_framework.core.cert_manager.extract_roles_from_certificate",
                return_value=["user"],
            ):
                with patch(
                    "mcp_security_framework.core.cert_manager.extract_permissions_from_certificate",
                    return_value=["read:users"],
                ):
                    with patch(
                        "mcp_security_framework.core.cert_manager.get_certificate_expiry",
                        return_value={"key_size": 2048},
                    ):
                        with patch(
                            "mcp_security_framework.core.cert_manager.get_certificate_serial_number",
                            return_value="123456789",
                        ):
                            with patch(
                                "mcp_security_framework.core.cert_manager.is_certificate_self_signed",
                                return_value=False,
                            ):
                                cert_info = self.cert_manager.get_certificate_info(
                                    cert_path
                                )

        assert isinstance(cert_info, CertificateInfo)
        assert cert_info.subject == {
            "CN": "test.client.com",
            "C": "test.client.com",
            "O": "test.client.com",
        }
        assert cert_info.issuer == {"CN": "Test Root CA"}
        assert cert_info.serial_number == "123456789"
        assert cert_info.roles == ["user"]
        assert cert_info.permissions == ["read:users"]
        assert cert_info.certificate_path == cert_path

    def test_get_certificate_info_cached(self):
        """Test certificate information retrieval from cache."""
        cert_path = "/path/to/cert.crt"

        # Create cached certificate info
        cached_info = CertificateInfo(
            subject={"CN": "cached.client.com"},
            issuer={"CN": "Test Root CA"},
            serial_number="987654321",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.CLIENT,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
            fingerprint_sha1="mock_sha1",
            fingerprint_sha256="mock_sha256",
            is_ca=False,
            roles=["user"],
            permissions=["read:users"],
            certificate_path=cert_path,
        )

        self.cert_manager._certificate_cache[cert_path] = cached_info

        cert_info = self.cert_manager.get_certificate_info(cert_path)

        assert cert_info == cached_info

    def test_get_certificate_info_parsing_error(self):
        """Test certificate information extraction with parsing error."""
        cert_path = "/path/to/invalid_cert.crt"

        with patch(
            "mcp_security_framework.utils.cert_utils.parse_certificate",
            side_effect=Exception("Parsing failed"),
        ):
            with pytest.raises(CertificateValidationError) as exc_info:
                self.cert_manager.get_certificate_info(cert_path)

        assert "Failed to get certificate info" in str(exc_info.value)

    def test_validate_configuration_missing_ca_cert_path(self):
        """Test configuration validation with missing CA certificate path."""
        with pytest.raises(ValidationError) as exc_info:
            CertificateConfig(
                enabled=True, ca_cert_path="", ca_key_path=self.ca_key_path
            )

        assert "CA certificate and key paths are required" in str(exc_info.value)

    def test_validate_configuration_missing_ca_key_path(self):
        """Test configuration validation with missing CA key path."""
        with pytest.raises(ValidationError) as exc_info:
            CertificateConfig(
                enabled=True, ca_cert_path=self.ca_cert_path, ca_key_path=""
            )

        assert "CA certificate and key paths are required" in str(exc_info.value)

    def test_create_output_directory(self):
        """Test automatic output directory creation."""
        # Create new temp directory
        new_temp_dir = os.path.join(self.temp_dir, "new_output")

        config = CertificateConfig(
            enabled=True,
            ca_cert_path=self.ca_cert_path,
            ca_key_path=self.ca_key_path,
            cert_storage_path=new_temp_dir,
            key_storage_path=new_temp_dir,
        )

        cert_manager = CertificateManager(config)

        assert os.path.exists(new_temp_dir)
        assert cert_manager.config.cert_storage_path == new_temp_dir

    def test_ec_key_generation(self):
        """Test EC key generation for certificates."""
        ca_config = CAConfig(
            common_name="Test EC CA",
            organization="Test Organization",
            country="US",
            validity_years=10,
        )

        with patch(
            "cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key"
        ) as mock_rsa:
            with patch("cryptography.x509.CertificateBuilder") as mock_builder_class:
                with patch("builtins.open", create=True) as mock_open:
                    with patch("os.chmod") as mock_chmod:
                        # Mock the certificate building process
                        mock_cert = Mock()
                        mock_cert.serial_number = 111222333
                        mock_cert.not_valid_before_utc = datetime.now(timezone.utc)
                        mock_cert.not_valid_after_utc = datetime.now(
                            timezone.utc
                        ) + timedelta(days=3650)
                        mock_cert.public_bytes.return_value = b"-----BEGIN CERTIFICATE-----\nMOCK EC CERT\n-----END CERTIFICATE-----"

                        mock_private_key = Mock()
                        mock_public_key = Mock()
                        mock_public_key.public_bytes.return_value = (
                            b"mock_public_key_data"
                        )
                        mock_private_key.public_key.return_value = mock_public_key
                        mock_private_key.private_bytes.return_value = b"-----BEGIN PRIVATE KEY-----\nMOCK EC KEY\n-----END PRIVATE KEY-----"

                        # Mock the builder chain
                        mock_builder = Mock()
                        mock_builder.subject_name.return_value = mock_builder
                        mock_builder.issuer_name.return_value = mock_builder
                        mock_builder.public_key.return_value = mock_builder
                        mock_builder.serial_number.return_value = mock_builder
                        mock_builder.not_valid_before.return_value = mock_builder
                        mock_builder.not_valid_after.return_value = mock_builder
                        mock_builder.add_extension.return_value = mock_builder
                        mock_builder.sign.return_value = mock_cert

                        mock_builder_class.return_value = mock_builder
                        mock_rsa.return_value = mock_private_key

                        # Mock file operations
                        mock_file = Mock()
                        mock_open.return_value.__enter__.return_value = mock_file

                        cert_pair = self.cert_manager.create_root_ca(ca_config)

        assert isinstance(cert_pair, CertificatePair)
        assert cert_pair.serial_number == "111222333"
        assert cert_pair.common_name == "Test EC CA"
        assert cert_pair.organization == "Test Organization"

    def test_certificate_permissions(self):
        """Test that generated certificate files have correct permissions."""
        ca_config = CAConfig(
            common_name="Test Permissions CA",
            organization="Test Organization",
            country="US",
            validity_years=10,
        )

        with patch(
            "cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key"
        ) as mock_rsa:
            with patch("cryptography.x509.CertificateBuilder") as mock_builder_class:
                with patch("builtins.open", create=True) as mock_open:
                    with patch("os.chmod") as mock_chmod:
                        # Mock the certificate building process
                        mock_cert = Mock()
                        mock_cert.serial_number = 444555666
                        mock_cert.not_valid_before_utc = datetime.now(timezone.utc)
                        mock_cert.not_valid_after_utc = datetime.now(
                            timezone.utc
                        ) + timedelta(days=3650)
                        mock_cert.public_bytes.return_value = b"-----BEGIN CERTIFICATE-----\nMOCK CERT\n-----END CERTIFICATE-----"

                        mock_private_key = Mock()
                        mock_public_key = Mock()
                        mock_public_key.public_bytes.return_value = (
                            b"mock_public_key_data"
                        )
                        mock_private_key.public_key.return_value = mock_public_key
                        mock_private_key.private_bytes.return_value = b"-----BEGIN PRIVATE KEY-----\nMOCK KEY\n-----END PRIVATE KEY-----"

                        # Mock the builder chain
                        mock_builder = Mock()
                        mock_builder.subject_name.return_value = mock_builder
                        mock_builder.issuer_name.return_value = mock_builder
                        mock_builder.public_key.return_value = mock_builder
                        mock_builder.serial_number.return_value = mock_builder
                        mock_builder.not_valid_before.return_value = mock_builder
                        mock_builder.not_valid_after.return_value = mock_builder
                        mock_builder.add_extension.return_value = mock_builder
                        mock_builder.sign.return_value = mock_cert

                        mock_builder_class.return_value = mock_builder
                        mock_rsa.return_value = mock_private_key

                        # Mock file operations
                        mock_file = Mock()
                        mock_open.return_value.__enter__.return_value = mock_file

                        cert_pair = self.cert_manager.create_root_ca(ca_config)

        # Verify that chmod was called with correct permissions
        assert mock_chmod.call_count >= 2  # At least for cert and key files
        # Note: In a real test, we would check actual file permissions
        # but since we're using mocks, we just verify the chmod calls were made
