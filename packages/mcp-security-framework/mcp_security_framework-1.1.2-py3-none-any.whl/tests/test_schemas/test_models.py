"""
Data Models Test Module

This module provides comprehensive unit tests for all data models
in the MCP Security Framework. It tests validation, properties,
and edge cases for all model classes.

Test Classes:
    TestAuthResult: Tests for authentication result model
    TestValidationResult: Tests for validation result model
    TestCertificateInfo: Tests for certificate information model
    TestCertificatePair: Tests for certificate pair model
    TestRateLimitStatus: Tests for rate limiting status model
    TestUserCredentials: Tests for user credentials model
    TestRolePermissions: Tests for role permissions model
    TestCertificateChain: Tests for certificate chain model

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from mcp_security_framework.schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    CertificateChain,
    CertificateInfo,
    CertificatePair,
    CertificateType,
    RateLimitStatus,
    RolePermissions,
    UserCredentials,
    ValidationResult,
    ValidationStatus,
)


class TestAuthResult:
    """Test suite for AuthResult class."""

    def test_auth_result_success(self):
        """Test AuthResult with successful authentication."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="testuser",
            user_id="12345",
            roles=["user", "admin"],
            permissions={"read", "write", "delete"},
            auth_method=AuthMethod.API_KEY,
            token_expiry=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        assert auth_result.is_valid is True
        assert auth_result.status == AuthStatus.SUCCESS
        assert auth_result.username == "testuser"
        assert auth_result.user_id == "12345"
        assert auth_result.roles == ["user", "admin"]
        assert auth_result.permissions == {"read", "write", "delete"}
        assert auth_result.auth_method == AuthMethod.API_KEY
        assert auth_result.error_code is None
        assert auth_result.error_message is None

    def test_auth_result_failure(self):
        """Test AuthResult with failed authentication."""
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            error_code=401,
            error_message="Invalid credentials",
        )

        assert auth_result.is_valid is False
        assert auth_result.status == AuthStatus.FAILED
        assert auth_result.error_code == 401
        assert auth_result.error_message == "Invalid credentials"
        assert auth_result.username is None
        assert auth_result.user_id is None

    def test_auth_result_invalid_username(self):
        """Test AuthResult with invalid username."""
        with pytest.raises(ValidationError) as exc_info:
            AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username="   ",  # Empty after strip
            )

        assert "Username cannot be empty" in str(exc_info.value)

    def test_auth_result_validation_consistency_success_with_error(self):
        """Test AuthResult validation when success has error code."""
        with pytest.raises(ValidationError) as exc_info:
            AuthResult(is_valid=True, status=AuthStatus.SUCCESS, error_code=401)

        assert "Valid authentication cannot have error code" in str(exc_info.value)

    def test_auth_result_validation_consistency_failure_without_error(self):
        """Test AuthResult validation when failure has no error."""
        with pytest.raises(ValidationError) as exc_info:
            AuthResult(is_valid=False, status=AuthStatus.SUCCESS)

        assert "Invalid authentication cannot have SUCCESS status" in str(
            exc_info.value
        )

    def test_auth_result_properties(self):
        """Test AuthResult properties."""
        # Not expired
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            token_expiry=datetime.now(timezone.utc) + timedelta(hours=2),
        )

        assert auth_result.is_expired is False
        assert auth_result.expires_soon is False

        # Expires soon
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            token_expiry=datetime.now(timezone.utc) + timedelta(minutes=30),
        )

        assert auth_result.is_expired is False
        assert auth_result.expires_soon is True

        # Expired
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            token_expiry=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        assert auth_result.is_expired is True
        assert auth_result.expires_soon is True

        # No expiry
        auth_result = AuthResult(
            is_valid=True, status=AuthStatus.SUCCESS, token_expiry=None
        )

        assert auth_result.is_expired is False
        assert auth_result.expires_soon is False


class TestValidationResult:
    """Test suite for ValidationResult class."""

    def test_validation_result_success(self):
        """Test ValidationResult with successful validation."""
        validation_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            field_name="username",
            value="testuser",
        )

        assert validation_result.is_valid is True
        assert validation_result.status == ValidationStatus.VALID
        assert validation_result.field_name == "username"
        assert validation_result.value == "testuser"
        assert validation_result.error_code is None
        assert validation_result.error_message is None
        assert validation_result.warnings == []

    def test_validation_result_failure(self):
        """Test ValidationResult with failed validation."""
        validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            field_name="password",
            value="",
            error_code=400,
            error_message="Password cannot be empty",
            warnings=["Password is too weak"],
        )

        assert validation_result.is_valid is False
        assert validation_result.status == ValidationStatus.INVALID
        assert validation_result.field_name == "password"
        assert validation_result.value == ""
        assert validation_result.error_code == 400
        assert validation_result.error_message == "Password cannot be empty"
        assert validation_result.warnings == ["Password is too weak"]

    def test_validation_result_validation_consistency_success_with_error(self):
        """Test ValidationResult validation when success has error code."""
        with pytest.raises(ValidationError) as exc_info:
            ValidationResult(
                is_valid=True, status=ValidationStatus.VALID, error_code=400
            )

        assert "Valid validation cannot have error code" in str(exc_info.value)

    def test_validation_result_validation_consistency_failure_without_error(self):
        """Test ValidationResult validation when failure has no error."""
        with pytest.raises(ValidationError) as exc_info:
            ValidationResult(is_valid=False, status=ValidationStatus.VALID)

        assert "Invalid validation cannot have VALID status" in str(exc_info.value)


class TestCertificateInfo:
    """Test suite for CertificateInfo class."""

    def test_certificate_info_basic(self):
        """Test CertificateInfo with basic information."""
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com", "O": "Test Org"},
            issuer={"CN": "Test CA", "O": "Test CA Org"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        assert cert_info.subject == {"CN": "test.example.com", "O": "Test Org"}
        assert cert_info.issuer == {"CN": "Test CA", "O": "Test CA Org"}
        assert cert_info.serial_number == "123456789"
        assert cert_info.certificate_type == CertificateType.SERVER
        assert cert_info.key_size == 2048
        assert cert_info.signature_algorithm == "sha256WithRSAEncryption"
        assert cert_info.subject_alt_names == []
        assert cert_info.key_usage == []
        assert cert_info.extended_key_usage == []
        assert cert_info.is_ca is False
        assert cert_info.roles == []
        assert cert_info.permissions == []

    def test_certificate_info_complete(self):
        """Test CertificateInfo with complete information."""
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com", "O": "Test Org", "OU": "IT"},
            issuer={"CN": "Test CA", "O": "Test CA Org"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.CLIENT,
            key_size=4096,
            signature_algorithm="sha384WithRSAEncryption",
            subject_alt_names=["*.example.com", "example.com"],
            key_usage=["digitalSignature", "keyEncipherment"],
            extended_key_usage=["clientAuth"],
            is_ca=False,
            path_length=None,
            roles=["developer", "admin"],
            permissions=["read", "write"],
            certificate_path="/path/to/cert.pem",
            fingerprint_sha1="abcd1234",
            fingerprint_sha256="abcd12345678",
        )

        assert cert_info.subject_alt_names == ["*.example.com", "example.com"]
        assert cert_info.key_usage == ["digitalSignature", "keyEncipherment"]
        assert cert_info.extended_key_usage == ["clientAuth"]
        assert cert_info.is_ca is False
        assert cert_info.roles == ["developer", "admin"]
        assert cert_info.permissions == ["read", "write"]
        assert cert_info.certificate_path == "/path/to/cert.pem"
        assert cert_info.fingerprint_sha1 == "abcd1234"
        assert cert_info.fingerprint_sha256 == "abcd12345678"

    def test_certificate_info_invalid_key_size(self):
        """Test CertificateInfo with invalid key size."""
        with pytest.raises(ValidationError) as exc_info:
            CertificateInfo(
                subject={"CN": "test.example.com"},
                issuer={"CN": "Test CA"},
                serial_number="123456789",
                not_before=datetime.now(timezone.utc),
                not_after=datetime.now(timezone.utc) + timedelta(days=365),
                certificate_type=CertificateType.SERVER,
                key_size=256,  # Too small
                signature_algorithm="sha256WithRSAEncryption",
            )

        assert "Key size must be between 512 and 8192 bits" in str(exc_info.value)

    def test_certificate_info_properties(self):
        """Test CertificateInfo properties."""
        # Not expired
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc) - timedelta(days=30),
            not_after=datetime.now(timezone.utc) + timedelta(days=60),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        assert cert_info.is_expired is False
        assert cert_info.expires_soon is False
        assert cert_info.days_until_expiry > 0
        assert cert_info.common_name == "test.example.com"
        assert cert_info.organization is None

        # Expires soon
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com", "O": "Test Org"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc) - timedelta(days=340),
            not_after=datetime.now(timezone.utc) + timedelta(days=20),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        assert cert_info.is_expired is False
        assert cert_info.expires_soon is True
        assert cert_info.organization == "Test Org"

        # Expired
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc) - timedelta(days=400),
            not_after=datetime.now(timezone.utc) - timedelta(days=10),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        assert cert_info.is_expired is True
        assert cert_info.days_until_expiry == 0


class TestCertificatePair:
    """Test suite for CertificatePair class."""

    def test_certificate_pair_basic(self):
        """Test CertificatePair with basic information."""
        cert_pair = CertificatePair(
            certificate_path="/path/to/cert.pem",
            private_key_path="/path/to/key.pem",
            certificate_pem="-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----",
            private_key_pem="-----BEGIN PRIVATE KEY-----\nMII...\n-----END PRIVATE KEY-----",
            serial_number="123456789",
            common_name="test.example.com",
            organization="Test Org",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
        )

        assert cert_pair.certificate_path == "/path/to/cert.pem"
        assert cert_pair.private_key_path == "/path/to/key.pem"
        assert cert_pair.serial_number == "123456789"
        assert cert_pair.common_name == "test.example.com"
        assert cert_pair.organization == "Test Org"
        assert cert_pair.certificate_type == CertificateType.SERVER
        assert cert_pair.key_size == 2048
        assert cert_pair.roles == []
        assert cert_pair.permissions == []

    def test_certificate_pair_invalid_certificate_pem(self):
        """Test CertificatePair with invalid certificate PEM."""
        with pytest.raises(ValidationError) as exc_info:
            CertificatePair(
                certificate_path="/path/to/cert.pem",
                private_key_path="/path/to/key.pem",
                certificate_pem="INVALID_CERT",
                private_key_pem="-----BEGIN PRIVATE KEY-----\nMII...\n-----END PRIVATE KEY-----",
                serial_number="123456789",
                common_name="test.example.com",
                organization="Test Org",
                not_before=datetime.now(timezone.utc),
                not_after=datetime.now(timezone.utc) + timedelta(days=365),
                certificate_type=CertificateType.SERVER,
                key_size=2048,
            )

        assert "Invalid certificate PEM format" in str(exc_info.value)

    def test_certificate_pair_invalid_private_key_pem(self):
        """Test CertificatePair with invalid private key PEM."""
        with pytest.raises(ValidationError) as exc_info:
            CertificatePair(
                certificate_path="/path/to/cert.pem",
                private_key_path="/path/to/key.pem",
                certificate_pem="-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----",
                private_key_pem="INVALID_KEY",
                serial_number="123456789",
                common_name="test.example.com",
                organization="Test Org",
                not_before=datetime.now(timezone.utc),
                not_after=datetime.now(timezone.utc) + timedelta(days=365),
                certificate_type=CertificateType.SERVER,
                key_size=2048,
            )

        assert "Invalid private key PEM format" in str(exc_info.value)

    def test_certificate_pair_rsa_private_key_pem(self):
        """Test CertificatePair with RSA private key PEM format."""
        cert_pair = CertificatePair(
            certificate_path="/path/to/cert.pem",
            private_key_path="/path/to/key.pem",
            certificate_pem="-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----",
            private_key_pem=(
                "-----BEGIN RSA PRIVATE KEY-----\nMII...\n-----END RSA PRIVATE KEY-----"
            ),
            serial_number="123456789",
            common_name="test.example.com",
            organization="Test Org",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
        )

        expected_key = (
            "-----BEGIN RSA PRIVATE KEY-----\nMII...\n-----END RSA PRIVATE KEY-----"
        )
        assert cert_pair.private_key_pem == expected_key

    def test_certificate_pair_properties(self):
        """Test CertificatePair properties."""
        # Not expired
        cert_pair = CertificatePair(
            certificate_path="/path/to/cert.pem",
            private_key_path="/path/to/key.pem",
            certificate_pem="-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----",
            private_key_pem="-----BEGIN PRIVATE KEY-----\nMII...\n-----END PRIVATE KEY-----",
            serial_number="123456789",
            common_name="test.example.com",
            organization="Test Org",
            not_before=datetime.now(timezone.utc) - timedelta(days=30),
            not_after=datetime.now(timezone.utc) + timedelta(days=60),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
        )

        assert cert_pair.is_expired is False
        assert cert_pair.expires_soon is False

        # Expires soon
        cert_pair = CertificatePair(
            certificate_path="/path/to/cert.pem",
            private_key_path="/path/to/key.pem",
            certificate_pem="-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----",
            private_key_pem="-----BEGIN PRIVATE KEY-----\nMII...\n-----END PRIVATE KEY-----",
            serial_number="123456789",
            common_name="test.example.com",
            organization="Test Org",
            not_before=datetime.now(timezone.utc) - timedelta(days=340),
            not_after=datetime.now(timezone.utc) + timedelta(days=20),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
        )

        assert cert_pair.is_expired is False
        assert cert_pair.expires_soon is True


class TestRateLimitStatus:
    """Test suite for RateLimitStatus class."""

    def test_rate_limit_status_basic(self):
        """Test RateLimitStatus with basic information."""
        now = datetime.now(timezone.utc)
        rate_limit_status = RateLimitStatus(
            identifier="192.168.1.1",
            current_count=5,
            limit=10,
            window_start=now,
            window_end=now + timedelta(minutes=1),
            is_exceeded=False,
            remaining_requests=5,
            reset_time=now + timedelta(minutes=1),
            window_size_seconds=60,
        )

        assert rate_limit_status.identifier == "192.168.1.1"
        assert rate_limit_status.current_count == 5
        assert rate_limit_status.limit == 10
        assert rate_limit_status.is_exceeded is False
        assert rate_limit_status.remaining_requests == 5
        assert rate_limit_status.window_size_seconds == 60

    def test_rate_limit_status_exceeded(self):
        """Test RateLimitStatus when limit is exceeded."""
        now = datetime.now(timezone.utc)
        rate_limit_status = RateLimitStatus(
            identifier="192.168.1.1",
            current_count=15,
            limit=10,
            window_start=now,
            window_end=now + timedelta(minutes=1),
            is_exceeded=True,
            remaining_requests=0,
            reset_time=now + timedelta(minutes=1),
            window_size_seconds=60,
        )

        assert rate_limit_status.is_exceeded is True
        assert rate_limit_status.remaining_requests == 0

    def test_rate_limit_status_validation_consistency(self):
        """Test RateLimitStatus validation consistency."""
        now = datetime.now(timezone.utc)

        # Exceeded but is_exceeded is False
        with pytest.raises(ValidationError) as exc_info:
            RateLimitStatus(
                identifier="192.168.1.1",
                current_count=15,
                limit=10,
                window_start=now,
                window_end=now + timedelta(minutes=1),
                is_exceeded=False,  # Should be True
                remaining_requests=0,
                reset_time=now + timedelta(minutes=1),
                window_size_seconds=60,
            )

        assert "Rate limit exceeded but is_exceeded is False" in str(exc_info.value)

        # Not exceeded but is_exceeded is True
        with pytest.raises(ValidationError) as exc_info:
            RateLimitStatus(
                identifier="192.168.1.1",
                current_count=5,
                limit=10,
                window_start=now,
                window_end=now + timedelta(minutes=1),
                is_exceeded=True,  # Should be False
                remaining_requests=5,
                reset_time=now + timedelta(minutes=1),
                window_size_seconds=60,
            )

        assert "Rate limit not exceeded but is_exceeded is True" in str(exc_info.value)

    def test_rate_limit_status_properties(self):
        """Test RateLimitStatus properties."""
        now = datetime.now(timezone.utc)
        rate_limit_status = RateLimitStatus(
            identifier="192.168.1.1",
            current_count=5,
            limit=10,
            window_start=now,
            window_end=now + timedelta(minutes=1),
            is_exceeded=False,
            remaining_requests=5,
            reset_time=now + timedelta(minutes=1),
            window_size_seconds=60,
        )

        assert rate_limit_status.utilization_percentage == 50.0
        assert rate_limit_status.seconds_until_reset > 0

        # 100% utilization
        rate_limit_status = RateLimitStatus(
            identifier="192.168.1.1",
            current_count=10,
            limit=10,
            window_start=now,
            window_end=now + timedelta(minutes=1),
            is_exceeded=False,
            remaining_requests=0,
            reset_time=now + timedelta(minutes=1),
            window_size_seconds=60,
        )

        assert rate_limit_status.utilization_percentage == 100.0

        # 0% utilization
        rate_limit_status = RateLimitStatus(
            identifier="192.168.1.1",
            current_count=0,
            limit=10,
            window_start=now,
            window_end=now + timedelta(minutes=1),
            is_exceeded=False,
            remaining_requests=10,
            reset_time=now + timedelta(minutes=1),
            window_size_seconds=60,
        )

        assert rate_limit_status.utilization_percentage == 0.0


class TestUserCredentials:
    """Test suite for UserCredentials class."""

    def test_user_credentials_basic(self):
        """Test UserCredentials with basic information."""
        user_creds = UserCredentials(
            username="testuser",
            password="hashed_password",
            api_key="api_key_123",
            certificate_path="/path/to/cert.pem",
            roles=["user", "admin"],
            permissions={"read", "write"},
        )

        assert user_creds.username == "testuser"
        assert user_creds.password == "hashed_password"
        assert user_creds.api_key == "api_key_123"
        assert user_creds.certificate_path == "/path/to/cert.pem"
        assert user_creds.roles == ["user", "admin"]
        assert user_creds.permissions == {"read", "write"}
        assert user_creds.is_active is True
        assert user_creds.last_login is None

    def test_user_credentials_username_validation(self):
        """Test UserCredentials username validation."""
        # Valid username
        user_creds = UserCredentials(username="testuser")
        assert user_creds.username == "testuser"

        # Username with whitespace
        user_creds = UserCredentials(username="  testuser  ")
        assert user_creds.username == "testuser"

        # Empty username
        with pytest.raises(ValidationError) as exc_info:
            UserCredentials(username="")

        assert "Username cannot be empty" in str(exc_info.value)

        # Username too long
        long_username = "a" * 101
        with pytest.raises(ValidationError) as exc_info:
            UserCredentials(username=long_username)

        assert "Username too long" in str(exc_info.value)

    def test_user_credentials_properties(self):
        """Test UserCredentials properties."""
        # User with password
        user_creds = UserCredentials(username="testuser", password="hashed_password")

        assert user_creds.has_password is True
        assert user_creds.has_api_key is False
        assert user_creds.has_certificate is False

        # User with API key
        user_creds = UserCredentials(username="testuser", api_key="api_key_123")

        assert user_creds.has_password is False
        assert user_creds.has_api_key is True
        assert user_creds.has_certificate is False

        # User with certificate
        user_creds = UserCredentials(
            username="testuser", certificate_path="/path/to/cert.pem"
        )

        assert user_creds.has_password is False
        assert user_creds.has_api_key is False
        assert user_creds.has_certificate is True

        # User with empty password
        user_creds = UserCredentials(username="testuser", password="")

        assert user_creds.has_password is False


class TestRolePermissions:
    """Test suite for RolePermissions class."""

    def test_role_permissions_basic(self):
        """Test RolePermissions with basic information."""
        role_perms = RolePermissions(
            role_name="admin",
            permissions={"read", "write", "delete"},
            parent_roles=["user"],
            child_roles=["moderator"],
            description="Administrator role with full access",
        )

        assert role_perms.role_name == "admin"
        assert role_perms.permissions == {"read", "write", "delete"}
        assert role_perms.parent_roles == ["user"]
        assert role_perms.child_roles == ["moderator"]
        assert role_perms.description == "Administrator role with full access"
        assert role_perms.is_active is True

    def test_role_permissions_username_validation(self):
        """Test RolePermissions role name validation."""
        # Valid role name
        role_perms = RolePermissions(role_name="admin")
        assert role_perms.role_name == "admin"

        # Role name with whitespace
        role_perms = RolePermissions(role_name="  admin  ")
        assert role_perms.role_name == "admin"

        # Empty role name
        with pytest.raises(ValidationError) as exc_info:
            RolePermissions(role_name="")

        assert "Role name cannot be empty" in str(exc_info.value)

        # Role name too long
        long_role_name = "a" * 101
        with pytest.raises(ValidationError) as exc_info:
            RolePermissions(role_name=long_role_name)

        assert "Role name too long" in str(exc_info.value)

    def test_role_permissions_properties(self):
        """Test RolePermissions properties."""
        role_perms = RolePermissions(
            role_name="admin", permissions={"read", "write", "delete"}
        )

        # Test effective permissions (currently returns direct permissions)
        effective_perms = role_perms.effective_permissions
        assert effective_perms == {"read", "write", "delete"}
        assert effective_perms is not role_perms.permissions  # Should be a copy

        # Test has_permission
        assert role_perms.has_permission("read") is True
        assert role_perms.has_permission("write") is True
        assert role_perms.has_permission("delete") is True
        assert role_perms.has_permission("execute") is False


class TestCertificateChain:
    """Test suite for CertificateChain class."""

    def test_certificate_chain_basic(self):
        """Test CertificateChain with basic information."""
        # Create mock certificates
        end_entity = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Intermediate CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        intermediate = CertificateInfo(
            subject={"CN": "Intermediate CA"},
            issuer={"CN": "Root CA"},
            serial_number="987654321",
            not_before=datetime.now(timezone.utc) - timedelta(days=365),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.INTERMEDIATE_CA,
            key_size=4096,
            signature_algorithm="sha256WithRSAEncryption",
            is_ca=True,
        )

        root = CertificateInfo(
            subject={"CN": "Root CA"},
            issuer={"CN": "Root CA"},
            serial_number="111111111",
            not_before=datetime.now(timezone.utc) - timedelta(days=730),
            not_after=datetime.now(timezone.utc) + timedelta(days=3650),
            certificate_type=CertificateType.ROOT_CA,
            key_size=4096,
            signature_algorithm="sha256WithRSAEncryption",
            is_ca=True,
        )

        cert_chain = CertificateChain(
            certificates=[end_entity, intermediate, root],
            chain_length=3,
            is_valid=True,
            root_ca=root,
            intermediate_cas=[intermediate],
            end_entity=end_entity,
        )

        assert cert_chain.chain_length == 3
        assert cert_chain.is_valid is True
        assert len(cert_chain.certificates) == 3
        assert cert_chain.root_ca == root
        assert cert_chain.intermediate_cas == [intermediate]
        assert cert_chain.end_entity == end_entity
        assert cert_chain.validation_errors == []

    def test_certificate_chain_validation_consistency(self):
        """Test CertificateChain validation consistency."""
        # Create mock certificate
        cert = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        # Chain length mismatch
        with pytest.raises(ValidationError) as exc_info:
            CertificateChain(
                certificates=[cert], chain_length=2, is_valid=True
            )  # Should be 1

        assert "Chain length must match number of certificates" in str(exc_info.value)

    def test_certificate_chain_properties(self):
        """Test CertificateChain properties."""
        # Create mock certificates
        end_entity = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Intermediate CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        intermediate = CertificateInfo(
            subject={"CN": "Intermediate CA"},
            issuer={"CN": "Root CA"},
            serial_number="987654321",
            not_before=datetime.now(timezone.utc) - timedelta(days=365),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.INTERMEDIATE_CA,
            key_size=4096,
            signature_algorithm="sha256WithRSAEncryption",
            is_ca=True,
        )

        root = CertificateInfo(
            subject={"CN": "Root CA"},
            issuer={"CN": "Root CA"},
            serial_number="111111111",
            not_before=datetime.now(timezone.utc) - timedelta(days=730),
            not_after=datetime.now(timezone.utc) + timedelta(days=3650),
            certificate_type=CertificateType.ROOT_CA,
            key_size=4096,
            signature_algorithm="sha256WithRSAEncryption",
            is_ca=True,
        )

        # Chain with intermediate CAs
        cert_chain = CertificateChain(
            certificates=[end_entity, intermediate, root], chain_length=3, is_valid=True
        )

        assert cert_chain.has_intermediate_cas is True
        assert cert_chain.is_self_signed is False

        # Self-signed certificate
        self_signed = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "test.example.com"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        cert_chain = CertificateChain(
            certificates=[self_signed], chain_length=1, is_valid=True
        )

        assert cert_chain.has_intermediate_cas is False
        assert cert_chain.is_self_signed is True
