"""
Certificate Utilities Test Module

This module provides comprehensive unit tests for all certificate
utilities in the MCP Security Framework.

Test Classes:
    TestCertificateParsing: Tests for certificate parsing
    TestCertificateInfo: Tests for certificate information extraction
    TestCertificateValidation: Tests for certificate validation
    TestCertificateExtensions: Tests for certificate extensions

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime, timedelta, timezone

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mcp_security_framework.utils.cert_utils import (
    CertificateError,
    convert_certificate_format,
    extract_certificate_info,
    extract_permissions_from_certificate,
    extract_public_key,
    extract_roles_from_certificate,
    get_certificate_expiry,
    get_certificate_serial_number,
    is_certificate_self_signed,
    parse_certificate,
    validate_certificate_chain,
    validate_certificate_format,
    validate_certificate_purpose,
)


class TestCertificateCreation:
    """Test suite for creating test certificates."""

    @staticmethod
    def create_test_certificate():
        """Create a test certificate for testing."""
        # Generate private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Create certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Organization"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("test.example.com"),
                        x509.DNSName("role=admin,permission=read"),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        return cert, private_key

    @staticmethod
    def create_test_ca_certificate():
        """Create a test CA certificate for testing."""
        # Generate private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Create CA certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "Test CA"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test CA Organization"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .sign(private_key, hashes.SHA256())
        )

        return cert, private_key


class TestCertificateParsing:
    """Test suite for certificate parsing functions."""

    def test_parse_certificate_invalid_data(self):
        """Test certificate parsing with invalid data."""
        with pytest.raises(CertificateError) as exc_info:
            parse_certificate("invalid_certificate_data")

        assert "Certificate parsing failed" in str(exc_info.value)

    def test_parse_certificate_valid_pem(self):
        """Test certificate parsing with valid PEM data."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        parsed_cert = parse_certificate(cert_pem)
        assert isinstance(parsed_cert, x509.Certificate)
        assert parsed_cert.subject == cert.subject

    def test_parse_certificate_valid_der(self):
        """Test certificate parsing with valid DER data."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_der = cert.public_bytes(serialization.Encoding.DER)

        parsed_cert = parse_certificate(cert_der)
        assert isinstance(parsed_cert, x509.Certificate)
        assert parsed_cert.subject == cert.subject

    def test_parse_certificate_with_headers(self):
        """Test certificate parsing with PEM headers."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        parsed_cert = parse_certificate(cert_pem)
        assert isinstance(parsed_cert, x509.Certificate)

    def test_validate_certificate_format_invalid(self):
        """Test certificate format validation with invalid format."""
        result = validate_certificate_format("invalid_format")
        assert result is False

    def test_validate_certificate_format_valid(self):
        """Test certificate format validation with valid format."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        result = validate_certificate_format(cert_pem)
        assert result is True

    def test_parse_certificate_file_not_found(self):
        """Test certificate parsing with non-existent file path."""
        with pytest.raises(CertificateError) as exc_info:
            parse_certificate("nonexistent_file.crt")

        assert "Certificate parsing failed" in str(exc_info.value)

    def test_parse_certificate_path_object_not_found(self):
        """Test certificate parsing with Path object pointing to non-existent file."""
        from pathlib import Path

        with pytest.raises(CertificateError) as exc_info:
            parse_certificate(Path("nonexistent_file.crt"))

        assert "Certificate file not found" in str(exc_info.value)

    def test_parse_certificate_string_not_pem_not_file(self):
        """Test certificate parsing with string that's neither PEM nor file path."""
        with pytest.raises(CertificateError) as exc_info:
            parse_certificate("not_a_pem_string_and_not_a_file")

        assert "Certificate parsing failed" in str(exc_info.value)


class TestCertificateInfo:
    """Test suite for certificate information extraction."""

    def test_extract_certificate_info_invalid_cert(self):
        """Test certificate info extraction with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            extract_certificate_info("invalid_cert")

        assert "Certificate information extraction failed" in str(exc_info.value)

    def test_extract_certificate_info_valid_cert(self):
        """Test certificate info extraction with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        info = extract_certificate_info(cert_pem)

        assert "subject" in info
        assert "issuer" in info
        assert "serial_number" in info
        assert "version" in info
        assert "not_before" in info
        assert "not_after" in info
        assert "signature_algorithm" in info
        assert "public_key_algorithm" in info
        assert "key_size" in info
        assert "extensions" in info
        assert "fingerprint_sha1" in info
        assert "fingerprint_sha256" in info
        assert "common_name" in info
        assert "organization" in info
        assert "country" in info

    def test_get_certificate_expiry_invalid_cert(self):
        """Test certificate expiry extraction with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            get_certificate_expiry("invalid_cert")

        assert "Certificate expiry information extraction failed" in str(exc_info.value)

    def test_get_certificate_expiry_exception(self):
        """Test certificate expiry extraction with exception."""
        with pytest.raises(CertificateError) as exc_info:
            get_certificate_expiry("invalid_cert_data")

        assert "Certificate expiry information extraction failed" in str(exc_info.value)

    def test_get_certificate_expiry_valid_cert(self):
        """Test certificate expiry extraction with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        expiry_info = get_certificate_expiry(cert_pem)

        assert "not_after" in expiry_info
        assert "not_before" in expiry_info
        assert "days_until_expiry" in expiry_info
        assert "is_expired" in expiry_info
        assert "expires_soon" in expiry_info
        assert "status" in expiry_info
        assert "total_seconds_until_expiry" in expiry_info

    def test_get_certificate_serial_number_invalid_cert(self):
        """Test serial number extraction with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            get_certificate_serial_number("invalid_cert")

        assert "Serial number extraction failed" in str(exc_info.value)

    def test_get_certificate_serial_number_valid_cert(self):
        """Test serial number extraction with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        serial_number = get_certificate_serial_number(cert_pem)
        assert isinstance(serial_number, str)
        assert len(serial_number) > 0

    def test_extract_public_key_invalid_cert(self):
        """Test public key extraction with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            extract_public_key("invalid_cert")

        assert "Public key extraction failed" in str(exc_info.value)

    def test_extract_public_key_valid_cert(self):
        """Test public key extraction with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        public_key = extract_public_key(cert_pem)
        assert isinstance(public_key, str)
        assert "-----BEGIN PUBLIC KEY-----" in public_key


class TestCertificateValidation:
    """Test suite for certificate validation functions."""

    def test_validate_certificate_chain_invalid_certs(self):
        """Test certificate chain validation with invalid certificates."""
        result = validate_certificate_chain("invalid_cert", "invalid_ca_cert")
        assert result is False

    def test_validate_certificate_chain_valid_certs(self):
        """Test certificate chain validation with valid certificates."""
        ca_cert, ca_key = TestCertificateCreation.create_test_ca_certificate()

        # Create a certificate signed by the CA
        cert, cert_key = TestCertificateCreation.create_test_certificate()

        ca_pem = ca_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        # This should fail because the cert is not signed by the CA
        result = validate_certificate_chain(cert_pem, ca_pem)
        assert result is False

    def test_validate_certificate_chain_exception(self):
        """Test certificate chain validation with exception."""
        # Test with invalid certificate data that will cause an exception
        result = validate_certificate_chain("invalid_cert", "invalid_ca_cert")
        assert result is False

    def test_validate_certificate_purpose_invalid_cert(self):
        """Test certificate purpose validation with invalid certificate."""
        with pytest.raises(CertificateError):
            validate_certificate_purpose("invalid_cert", "server")

    def test_validate_certificate_purpose_valid_cert(self):
        """Test certificate purpose validation with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        # Test with server purpose (should return False for this test cert)
        result = validate_certificate_purpose(cert_pem, "server")
        assert isinstance(result, bool)

    def test_is_certificate_self_signed_invalid_cert(self):
        """Test self-signed check with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            is_certificate_self_signed("invalid_cert")

        assert "Self-signed check failed" in str(exc_info.value)

    def test_is_certificate_self_signed_valid_cert(self):
        """Test self-signed check with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        result = is_certificate_self_signed(cert_pem)
        assert isinstance(result, bool)

    def test_get_certificate_serial_number_exception(self):
        """Test serial number extraction with exception."""
        with pytest.raises(CertificateError) as exc_info:
            get_certificate_serial_number("invalid_cert_data")

        assert "Serial number extraction failed" in str(exc_info.value)

    def test_is_certificate_self_signed_exception(self):
        """Test self-signed check with exception."""
        with pytest.raises(CertificateError) as exc_info:
            is_certificate_self_signed("invalid_cert_data")

        assert "Self-signed check failed" in str(exc_info.value)


class TestCertificateExtensions:
    """Test suite for certificate extension functions."""

    def test_extract_roles_from_certificate_invalid_cert(self):
        """Test role extraction with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            extract_roles_from_certificate("invalid_cert")

        assert "Role extraction failed" in str(exc_info.value)

    def test_extract_roles_from_certificate_valid_cert(self):
        """Test role extraction with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        roles = extract_roles_from_certificate(cert_pem)
        assert isinstance(roles, list)
        # Should extract role from SAN extension
        assert "admin" in roles

    def test_extract_permissions_from_certificate_invalid_cert(self):
        """Test permission extraction with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            extract_permissions_from_certificate("invalid_cert")

        assert "Permission extraction failed" in str(exc_info.value)

    def test_extract_permissions_from_certificate_valid_cert(self):
        """Test permission extraction with valid certificate."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        permissions = extract_permissions_from_certificate(cert_pem)
        assert isinstance(permissions, list)
        # Should return empty list since no custom permissions extension exists
        assert permissions == []

    def test_extract_roles_from_certificate_no_extensions(self):
        """Test role extraction with certificate that has no relevant extensions."""
        # Create certificate without SAN or custom extensions
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Organization"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
            .sign(private_key, hashes.SHA256())
        )

        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
        roles = extract_roles_from_certificate(cert_pem)

        assert isinstance(roles, list)
        assert roles == []

    def test_extract_permissions_from_certificate_no_extensions(self):
        """Test permission extraction with certificate that has no permissions extension."""
        # Create certificate without custom permissions extension
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Organization"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
            .sign(private_key, hashes.SHA256())
        )

        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
        permissions = extract_permissions_from_certificate(cert_pem)

        assert isinstance(permissions, list)
        assert permissions == []

    def test_extract_permissions_from_certificate_non_bytes_data(self):
        """Test permission extraction with non-bytes extension data."""
        # This test would require creating a certificate with a custom extension
        # that has non-bytes data, which is complex. Instead, we'll test the
        # exception handling path by passing invalid data.
        with pytest.raises(CertificateError):
            extract_permissions_from_certificate("invalid_cert_data")


class TestCertificateFormatConversion:
    """Test suite for certificate format conversion."""

    def test_convert_certificate_format_invalid_cert(self):
        """Test certificate format conversion with invalid certificate."""
        with pytest.raises(CertificateError) as exc_info:
            convert_certificate_format("invalid_cert", "PEM")

        assert "Certificate format conversion failed" in str(exc_info.value)

    def test_convert_certificate_format_unsupported_format(self):
        """Test certificate format conversion with unsupported format."""
        with pytest.raises(CertificateError) as exc_info:
            convert_certificate_format("invalid_cert", "UNSUPPORTED")

        assert "Certificate format conversion failed" in str(exc_info.value)

    def test_convert_certificate_format_pem_to_pem(self):
        """Test certificate format conversion from PEM to PEM."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        result = convert_certificate_format(cert_pem, "PEM")
        assert isinstance(result, str)
        assert "-----BEGIN CERTIFICATE-----" in result

    def test_convert_certificate_format_pem_to_der(self):
        """Test certificate format conversion from PEM to DER."""
        cert, _ = TestCertificateCreation.create_test_certificate()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

        result = convert_certificate_format(cert_pem, "DER")
        assert isinstance(result, str)
        # Should be base64 encoded DER
        assert len(result) > 0

    def test_convert_certificate_format_exception(self):
        """Test certificate format conversion with exception."""
        with pytest.raises(CertificateError) as exc_info:
            convert_certificate_format("invalid_cert_data")

        assert "Certificate format conversion failed" in str(exc_info.value)

    def test_extract_public_key_exception(self):
        """Test public key extraction with exception."""
        with pytest.raises(CertificateError) as exc_info:
            extract_public_key("invalid_cert_data")

        assert "Public key extraction failed" in str(exc_info.value)
