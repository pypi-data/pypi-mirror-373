"""
Configuration Models Test Module

This module provides comprehensive unit tests for all configuration
models in the MCP Security Framework. It tests validation, default
values, and edge cases for all configuration classes.

Test Classes:
    TestSSLConfig: Tests for SSL/TLS configuration
    TestAuthConfig: Tests for authentication configuration
    TestCertificateConfig: Tests for certificate configuration
    TestPermissionConfig: Tests for permission configuration
    TestRateLimitConfig: Tests for rate limiting configuration
    TestLoggingConfig: Tests for logging configuration
    TestSecurityConfig: Tests for main security configuration
    TestCAConfig: Tests for CA configuration
    TestClientCertConfig: Tests for client certificate configuration
    TestServerCertConfig: Tests for server certificate configuration

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import pytest
from pydantic import ValidationError

from mcp_security_framework.schemas.config import (
    AuthConfig,
    AuthMethod,
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    IntermediateCAConfig,
    LoggingConfig,
    LogLevel,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    ServerCertConfig,
    SSLConfig,
    TLSVersion,
)


class TestSSLConfig:
    """Test suite for SSLConfig class."""

    def test_ssl_config_defaults(self):
        """Test SSLConfig with default values."""
        config = SSLConfig()

        assert config.enabled is False
        assert config.cert_file is None
        assert config.key_file is None
        assert config.ca_cert_file is None
        assert config.verify_mode == "CERT_REQUIRED"
        assert config.min_tls_version == TLSVersion.TLS_1_2
        assert config.max_tls_version is None
        assert config.cipher_suite is None
        assert config.check_hostname is True
        assert config.check_expiry is True
        assert config.expiry_warning_days == 30

    def test_ssl_config_enabled_without_certificates(self):
        """Test SSLConfig validation when enabled without certificates."""
        with pytest.raises(ValidationError) as exc_info:
            SSLConfig(enabled=True)

        assert "SSL enabled but certificate and key files are required" in str(
            exc_info.value
        )

    def test_ssl_config_invalid_verify_mode(self):
        """Test SSLConfig with invalid verify mode."""
        with pytest.raises(ValidationError) as exc_info:
            SSLConfig(verify_mode="INVALID_MODE")

        assert "Invalid verify_mode" in str(exc_info.value)

    def test_ssl_config_valid_verify_modes(self):
        """Test SSLConfig with valid verify modes."""
        valid_modes = ["CERT_NONE", "CERT_OPTIONAL", "CERT_REQUIRED"]

        for mode in valid_modes:
            config = SSLConfig(verify_mode=mode)
            assert config.verify_mode == mode

    def test_ssl_config_tls_versions(self):
        """Test SSLConfig with different TLS versions."""
        config = SSLConfig(
            min_tls_version=TLSVersion.TLS_1_3, max_tls_version=TLSVersion.TLS_1_3
        )

        assert config.min_tls_version == TLSVersion.TLS_1_3
        assert config.max_tls_version == TLSVersion.TLS_1_3

    def test_ssl_config_expiry_warning_days_validation(self):
        """Test SSLConfig expiry warning days validation."""
        # Valid range
        config = SSLConfig(expiry_warning_days=1)
        assert config.expiry_warning_days == 1

        config = SSLConfig(expiry_warning_days=365)
        assert config.expiry_warning_days == 365

        # Invalid range
        with pytest.raises(ValidationError):
            SSLConfig(expiry_warning_days=0)

        with pytest.raises(ValidationError):
            SSLConfig(expiry_warning_days=366)


class TestAuthConfig:
    """Test suite for AuthConfig class."""

    def test_auth_config_defaults(self):
        """Test AuthConfig with default values."""
        config = AuthConfig()

        assert config.enabled is True
        assert config.methods == [AuthMethod.API_KEY]
        assert config.api_keys == {}
        assert config.jwt_secret is None
        assert config.jwt_algorithm == "HS256"
        assert config.jwt_expiry_hours == 24
        assert config.certificate_auth is False
        assert config.certificate_roles_oid == "1.3.6.1.4.1.99999.1.1"
        assert config.certificate_permissions_oid == "1.3.6.1.4.1.99999.1.2"
        assert config.basic_auth is False
        assert config.oauth2_config is None

    def test_auth_config_enabled_without_methods(self):
        """Test AuthConfig validation when enabled without methods."""
        with pytest.raises(ValidationError) as exc_info:
            AuthConfig(enabled=True, methods=[])

        assert "Authentication enabled but no methods specified" in str(exc_info.value)

    def test_auth_config_jwt_without_secret(self):
        """Test AuthConfig validation when JWT enabled without secret."""
        with pytest.raises(ValidationError) as exc_info:
            AuthConfig(methods=[AuthMethod.JWT])

        assert "JWT authentication enabled but no JWT secret provided" in str(
            exc_info.value
        )

    def test_auth_config_invalid_jwt_algorithm(self):
        """Test AuthConfig with invalid JWT algorithm."""
        with pytest.raises(ValidationError) as exc_info:
            AuthConfig(jwt_algorithm="INVALID_ALG")

        assert "Invalid JWT algorithm" in str(exc_info.value)

    def test_auth_config_valid_jwt_algorithms(self):
        """Test AuthConfig with valid JWT algorithms."""
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]

        for algorithm in valid_algorithms:
            config = AuthConfig(jwt_algorithm=algorithm)
            assert config.jwt_algorithm == algorithm

    def test_auth_config_jwt_expiry_hours_validation(self):
        """Test AuthConfig JWT expiry hours validation."""
        # Valid range
        config = AuthConfig(jwt_expiry_hours=1)
        assert config.jwt_expiry_hours == 1

        config = AuthConfig(jwt_expiry_hours=8760)  # 1 year
        assert config.jwt_expiry_hours == 8760

        # Invalid range
        with pytest.raises(ValidationError):
            AuthConfig(jwt_expiry_hours=0)

        with pytest.raises(ValidationError):
            AuthConfig(jwt_expiry_hours=8761)

    def test_auth_config_api_keys(self):
        """Test AuthConfig with API keys."""
        api_keys = {"key1": "user1", "key2": "user2"}
        config = AuthConfig(api_keys=api_keys)

        assert config.api_keys == api_keys
        assert len(config.api_keys) == 2


class TestCertificateConfig:
    """Test suite for CertificateConfig class."""

    def test_certificate_config_defaults(self):
        """Test CertificateConfig with default values."""
        config = CertificateConfig()

        assert config.enabled is False
        assert config.ca_cert_path is None
        assert config.ca_key_path is None
        assert config.cert_storage_path == "./certs"
        assert config.key_storage_path == "./keys"
        assert config.default_validity_days == 365
        assert config.key_size == 2048
        assert config.hash_algorithm == "sha256"
        assert config.crl_enabled is False
        assert config.crl_path is None
        assert config.crl_validity_days == 30
        assert config.auto_renewal is False
        assert config.renewal_threshold_days == 30

    def test_certificate_config_enabled_without_ca(self):
        """Test CertificateConfig validation when enabled without CA."""
        with pytest.raises(ValidationError) as exc_info:
            CertificateConfig(enabled=True)

        assert (
            "Certificate management enabled but CA certificate and key paths are required"
            in str(exc_info.value)
        )

    def test_certificate_config_crl_enabled_without_path(self):
        """Test CertificateConfig validation when CRL enabled without path."""
        with pytest.raises(ValidationError) as exc_info:
            CertificateConfig(crl_enabled=True)

        assert "CRL enabled but CRL path is required" in str(exc_info.value)

    def test_certificate_config_invalid_hash_algorithm(self):
        """Test CertificateConfig with invalid hash algorithm."""
        with pytest.raises(ValidationError) as exc_info:
            CertificateConfig(hash_algorithm="INVALID_HASH")

        assert "Invalid hash algorithm" in str(exc_info.value)

    def test_certificate_config_valid_hash_algorithms(self):
        """Test CertificateConfig with valid hash algorithms."""
        valid_algorithms = ["sha1", "sha256", "sha384", "sha512"]

        for algorithm in valid_algorithms:
            config = CertificateConfig(hash_algorithm=algorithm)
            assert config.hash_algorithm == algorithm

    def test_certificate_config_key_size_validation(self):
        """Test CertificateConfig key size validation."""
        # Valid range
        config = CertificateConfig(key_size=1024)
        assert config.key_size == 1024

        config = CertificateConfig(key_size=4096)
        assert config.key_size == 4096

        # Invalid range
        with pytest.raises(ValidationError):
            CertificateConfig(key_size=512)

        with pytest.raises(ValidationError):
            CertificateConfig(key_size=8192)

    def test_certificate_config_validity_days_validation(self):
        """Test CertificateConfig validity days validation."""
        # Valid range
        config = CertificateConfig(default_validity_days=1)
        assert config.default_validity_days == 1

        config = CertificateConfig(default_validity_days=3650)  # 10 years
        assert config.default_validity_days == 3650

        # Invalid range
        with pytest.raises(ValidationError):
            CertificateConfig(default_validity_days=0)

        with pytest.raises(ValidationError):
            CertificateConfig(default_validity_days=3651)


class TestPermissionConfig:
    """Test suite for PermissionConfig class."""

    def test_permission_config_defaults(self):
        """Test PermissionConfig with default values."""
        config = PermissionConfig()

        assert config.enabled is True
        assert config.roles_file is None
        assert config.default_role == "guest"
        assert config.admin_role == "admin"
        assert config.role_hierarchy == {}
        assert config.permission_cache_enabled is True
        assert config.permission_cache_ttl == 300
        assert config.wildcard_permissions is False
        assert config.strict_mode is True

    def test_permission_config_cache_ttl_validation(self):
        """Test PermissionConfig cache TTL validation."""
        # Valid range
        config = PermissionConfig(permission_cache_ttl=1)
        assert config.permission_cache_ttl == 1

        config = PermissionConfig(permission_cache_ttl=3600)
        assert config.permission_cache_ttl == 3600

        # Invalid range
        with pytest.raises(ValidationError):
            PermissionConfig(permission_cache_ttl=0)

        with pytest.raises(ValidationError):
            PermissionConfig(permission_cache_ttl=3601)

    def test_permission_config_role_hierarchy(self):
        """Test PermissionConfig with role hierarchy."""
        hierarchy = {"admin": ["user", "moderator"], "moderator": ["user"], "user": []}
        config = PermissionConfig(role_hierarchy=hierarchy)

        assert config.role_hierarchy == hierarchy
        assert len(config.role_hierarchy) == 3


class TestRateLimitConfig:
    """Test suite for RateLimitConfig class."""

    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig with default values."""
        config = RateLimitConfig()

        assert config.enabled is True
        assert config.default_requests_per_minute == 60
        assert config.default_requests_per_hour == 1000
        assert config.burst_limit == 2
        assert config.window_size_seconds == 60
        assert config.storage_backend == "memory"
        assert config.redis_config is None
        assert config.cleanup_interval == 300
        assert config.exempt_paths == []
        assert config.exempt_roles == []

    def test_rate_limit_config_invalid_storage_backend(self):
        """Test RateLimitConfig with invalid storage backend."""
        with pytest.raises(ValidationError) as exc_info:
            RateLimitConfig(storage_backend="INVALID_BACKEND")

        assert "Invalid storage backend" in str(exc_info.value)

    def test_rate_limit_config_valid_storage_backends(self):
        """Test RateLimitConfig with valid storage backends."""
        valid_backends = ["memory", "redis", "database"]

        for backend in valid_backends:
            config = RateLimitConfig(storage_backend=backend)
            assert config.storage_backend == backend

    def test_rate_limit_config_requests_per_minute_validation(self):
        """Test RateLimitConfig requests per minute validation."""
        # Valid range
        config = RateLimitConfig(default_requests_per_minute=1)
        assert config.default_requests_per_minute == 1

        config = RateLimitConfig(default_requests_per_minute=10000)
        assert config.default_requests_per_minute == 10000

        # Invalid range
        with pytest.raises(ValidationError):
            RateLimitConfig(default_requests_per_minute=0)

        with pytest.raises(ValidationError):
            RateLimitConfig(default_requests_per_minute=10001)

    def test_rate_limit_config_burst_limit_validation(self):
        """Test RateLimitConfig burst limit validation."""
        # Valid range
        config = RateLimitConfig(burst_limit=1)
        assert config.burst_limit == 1

        config = RateLimitConfig(burst_limit=10)
        assert config.burst_limit == 10

        # Invalid range
        with pytest.raises(ValidationError):
            RateLimitConfig(burst_limit=0)

        with pytest.raises(ValidationError):
            RateLimitConfig(burst_limit=11)


class TestLoggingConfig:
    """Test suite for LoggingConfig class."""

    def test_logging_config_defaults(self):
        """Test LoggingConfig with default values."""
        config = LoggingConfig()

        assert config.enabled is True
        assert config.level == LogLevel.INFO
        assert config.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert config.date_format == "%Y-%m-%d %H:%M:%S"
        assert config.file_path is None
        assert config.max_file_size == 10
        assert config.backup_count == 5
        assert config.console_output is True
        assert config.json_format is False
        assert config.include_timestamp is True
        assert config.include_level is True
        assert config.include_module is True

    def test_logging_config_file_size_validation(self):
        """Test LoggingConfig file size validation."""
        # Valid range
        config = LoggingConfig(max_file_size=1)
        assert config.max_file_size == 1

        config = LoggingConfig(max_file_size=1000)
        assert config.max_file_size == 1000

        # Invalid range
        with pytest.raises(ValidationError):
            LoggingConfig(max_file_size=0)

        with pytest.raises(ValidationError):
            LoggingConfig(max_file_size=1001)

    def test_logging_config_backup_count_validation(self):
        """Test LoggingConfig backup count validation."""
        # Valid range
        config = LoggingConfig(backup_count=0)
        assert config.backup_count == 0

        config = LoggingConfig(backup_count=100)
        assert config.backup_count == 100

        # Invalid range
        with pytest.raises(ValidationError):
            LoggingConfig(backup_count=-1)

        with pytest.raises(ValidationError):
            LoggingConfig(backup_count=101)


class TestSecurityConfig:
    """Test suite for SecurityConfig class."""

    def test_security_config_defaults(self):
        """Test SecurityConfig with default values."""
        config = SecurityConfig()

        assert config.debug is False
        assert config.environment == "dev"
        assert config.version == "1.0.0"
        assert isinstance(config.ssl, SSLConfig)
        assert isinstance(config.auth, AuthConfig)
        assert isinstance(config.certificates, CertificateConfig)
        assert isinstance(config.permissions, PermissionConfig)
        assert isinstance(config.rate_limit, RateLimitConfig)
        assert isinstance(config.logging, LoggingConfig)

    def test_security_config_invalid_environment(self):
        """Test SecurityConfig with invalid environment."""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(environment="INVALID_ENV")

        assert "Invalid environment" in str(exc_info.value)

    def test_security_config_valid_environments(self):
        """Test SecurityConfig with valid environments."""
        valid_environments = [
            "dev",
            "development",
            "staging",
            "prod",
            "production",
            "test",
        ]

        for env in valid_environments:
            config = SecurityConfig(environment=env)
            assert config.environment == env

    def test_security_config_custom_components(self):
        """Test SecurityConfig with custom component configurations."""
        # Create temporary files for testing
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".crt", delete=False
        ) as cert_file:
            cert_file.write("test certificate content")
            cert_path = cert_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".key", delete=False
        ) as key_file:
            key_file.write("test key content")
            key_path = key_file.name

        try:
            ssl_config = SSLConfig(enabled=True, cert_file=cert_path, key_file=key_path)
        finally:
            # Clean up temporary files
            os.unlink(cert_path)
            os.unlink(key_path)
        auth_config = AuthConfig(enabled=True, methods=[AuthMethod.API_KEY])

        config = SecurityConfig(
            ssl=ssl_config, auth=auth_config, debug=True, environment="prod"
        )

        assert config.ssl == ssl_config
        assert config.auth == auth_config
        assert config.debug is True
        assert config.environment == "prod"


class TestCAConfig:
    """Test suite for CAConfig class."""

    def test_ca_config_required_fields(self):
        """Test CAConfig with required fields."""
        config = CAConfig(common_name="Test CA", organization="Test Organization")

        assert config.common_name == "Test CA"
        assert config.organization == "Test Organization"
        assert config.country == "US"
        assert config.validity_years == 10
        assert config.key_size == 4096
        assert config.hash_algorithm == "sha256"

    def test_ca_config_all_fields(self):
        """Test CAConfig with all fields."""
        config = CAConfig(
            common_name="Test CA",
            organization="Test Organization",
            organizational_unit="IT Department",
            country="CA",
            state="Ontario",
            locality="Toronto",
            email="ca@test.com",
            validity_years=5,
            key_size=2048,
            hash_algorithm="sha384",
        )

        assert config.common_name == "Test CA"
        assert config.organization == "Test Organization"
        assert config.organizational_unit == "IT Department"
        assert config.country == "CA"
        assert config.state == "Ontario"
        assert config.locality == "Toronto"
        assert config.email == "ca@test.com"
        assert config.validity_years == 5
        assert config.key_size == 2048
        assert config.hash_algorithm == "sha384"

    def test_ca_config_validity_years_validation(self):
        """Test CAConfig validity years validation."""
        # Valid range
        config = CAConfig(
            common_name="Test CA", organization="Test Organization", validity_years=1
        )
        assert config.validity_years == 1

        config = CAConfig(
            common_name="Test CA", organization="Test Organization", validity_years=50
        )
        assert config.validity_years == 50

        # Invalid range
        with pytest.raises(ValidationError):
            CAConfig(
                common_name="Test CA",
                organization="Test Organization",
                validity_years=0,
            )

        with pytest.raises(ValidationError):
            CAConfig(
                common_name="Test CA",
                organization="Test Organization",
                validity_years=51,
            )

    def test_ca_config_key_size_validation(self):
        """Test CAConfig key size validation."""
        # Valid range
        config = CAConfig(
            common_name="Test CA", organization="Test Organization", key_size=2048
        )
        assert config.key_size == 2048

        config = CAConfig(
            common_name="Test CA", organization="Test Organization", key_size=8192
        )
        assert config.key_size == 8192

        # Invalid range
        with pytest.raises(ValidationError):
            CAConfig(
                common_name="Test CA", organization="Test Organization", key_size=1024
            )

        with pytest.raises(ValidationError):
            CAConfig(
                common_name="Test CA", organization="Test Organization", key_size=16384
            )


class TestClientCertConfig:
    """Test suite for ClientCertConfig class."""

    def test_client_cert_config_required_fields(self):
        """Test ClientCertConfig with required fields."""
        config = ClientCertConfig(
            common_name="test.client.com",
            organization="Test Organization",
            ca_cert_path="/path/to/ca.crt",
            ca_key_path="/path/to/ca.key",
        )

        assert config.common_name == "test.client.com"
        assert config.organization == "Test Organization"
        assert config.ca_cert_path == "/path/to/ca.crt"
        assert config.ca_key_path == "/path/to/ca.key"
        assert config.country == "US"
        assert config.validity_days == 365
        assert config.key_size == 2048
        assert config.roles == []
        assert config.permissions == []

    def test_client_cert_config_all_fields(self):
        """Test ClientCertConfig with all fields."""
        config = ClientCertConfig(
            common_name="test.client.com",
            organization="Test Organization",
            organizational_unit="Development",
            country="CA",
            state="Ontario",
            locality="Toronto",
            email="client@test.com",
            validity_days=730,
            key_size=4096,
            roles=["developer", "tester"],
            permissions=["read", "write"],
            ca_cert_path="/path/to/ca.crt",
            ca_key_path="/path/to/ca.key",
        )

        assert config.common_name == "test.client.com"
        assert config.organization == "Test Organization"
        assert config.organizational_unit == "Development"
        assert config.country == "CA"
        assert config.state == "Ontario"
        assert config.locality == "Toronto"
        assert config.email == "client@test.com"
        assert config.validity_days == 730
        assert config.key_size == 4096
        assert config.roles == ["developer", "tester"]
        assert config.permissions == ["read", "write"]
        assert config.ca_cert_path == "/path/to/ca.crt"
        assert config.ca_key_path == "/path/to/ca.key"

    def test_client_cert_config_validity_days_validation(self):
        """Test ClientCertConfig validity days validation."""
        # Valid range
        config = ClientCertConfig(
            common_name="test.client.com",
            organization="Test Organization",
            ca_cert_path="/path/to/ca.crt",
            ca_key_path="/path/to/ca.key",
            validity_days=1,
        )
        assert config.validity_days == 1

        config = ClientCertConfig(
            common_name="test.client.com",
            organization="Test Organization",
            ca_cert_path="/path/to/ca.crt",
            ca_key_path="/path/to/ca.key",
            validity_days=3650,
        )
        assert config.validity_days == 3650

        # Invalid range
        with pytest.raises(ValidationError):
            ClientCertConfig(
                common_name="test.client.com",
                organization="Test Organization",
                ca_cert_path="/path/to/ca.crt",
                ca_key_path="/path/to/ca.key",
                validity_days=0,
            )

        with pytest.raises(ValidationError):
            ClientCertConfig(
                common_name="test.client.com",
                organization="Test Organization",
                ca_cert_path="/path/to/ca.crt",
                ca_key_path="/path/to/ca.key",
                validity_days=3651,
            )


class TestServerCertConfig:
    """Test suite for ServerCertConfig class."""

    def test_server_cert_config_inheritance(self):
        """Test ServerCertConfig inheritance from ClientCertConfig."""
        config = ServerCertConfig(
            common_name="test.server.com",
            organization="Test Organization",
            ca_cert_path="/path/to/ca.crt",
            ca_key_path="/path/to/ca.key",
        )

        # Inherited fields
        assert config.common_name == "test.server.com"
        assert config.organization == "Test Organization"
        assert config.ca_cert_path == "/path/to/ca.crt"
        assert config.ca_key_path == "/path/to/ca.key"

        # Server-specific fields
        assert config.subject_alt_names == []
        assert config.key_usage == ["digitalSignature", "keyEncipherment"]
        assert config.extended_key_usage == ["serverAuth"]

    def test_server_cert_config_with_san(self):
        """Test ServerCertConfig with subject alternative names."""
        config = ServerCertConfig(
            common_name="test.server.com",
            organization="Test Organization",
            ca_cert_path="/path/to/ca.crt",
            ca_key_path="/path/to/ca.key",
            subject_alt_names=["*.test.com", "test.com", "api.test.com"],
        )

        assert config.subject_alt_names == ["*.test.com", "test.com", "api.test.com"]

    def test_server_cert_config_custom_key_usage(self):
        """Test ServerCertConfig with custom key usage."""
        config = ServerCertConfig(
            common_name="test.server.com",
            organization="Test Organization",
            ca_cert_path="/path/to/ca.crt",
            ca_key_path="/path/to/ca.key",
            key_usage=["digitalSignature"],
            extended_key_usage=["serverAuth", "clientAuth"],
        )

        assert config.key_usage == ["digitalSignature"]
        assert config.extended_key_usage == ["serverAuth", "clientAuth"]


class TestIntermediateCAConfig:
    """Test suite for IntermediateCAConfig class."""

    def test_intermediate_ca_config_inheritance(self):
        """Test IntermediateCAConfig inheritance from CAConfig."""
        config = IntermediateCAConfig(
            common_name="Intermediate CA",
            organization="Test Organization",
            parent_ca_cert="/path/to/parent.crt",
            parent_ca_key="/path/to/parent.key",
        )

        # Inherited fields
        assert config.common_name == "Intermediate CA"
        assert config.organization == "Test Organization"
        assert config.validity_years == 10
        assert config.key_size == 4096

        # Intermediate-specific fields
        assert config.parent_ca_cert == "/path/to/parent.crt"
        assert config.parent_ca_key == "/path/to/parent.key"
        assert config.path_length == 0

    def test_intermediate_ca_config_path_length_validation(self):
        """Test IntermediateCAConfig path length validation."""
        # Valid range
        config = IntermediateCAConfig(
            common_name="Intermediate CA",
            organization="Test Organization",
            parent_ca_cert="/path/to/parent.crt",
            parent_ca_key="/path/to/parent.key",
            path_length=0,
        )
        assert config.path_length == 0

        config = IntermediateCAConfig(
            common_name="Intermediate CA",
            organization="Test Organization",
            parent_ca_cert="/path/to/parent.crt",
            parent_ca_key="/path/to/parent.key",
            path_length=10,
        )
        assert config.path_length == 10

        # Invalid range
        with pytest.raises(ValidationError):
            IntermediateCAConfig(
                common_name="Intermediate CA",
                organization="Test Organization",
                parent_ca_cert="/path/to/parent.crt",
                parent_ca_key="/path/to/parent.key",
                path_length=-1,
            )

        with pytest.raises(ValidationError):
            IntermediateCAConfig(
                common_name="Intermediate CA",
                organization="Test Organization",
                parent_ca_cert="/path/to/parent.crt",
                parent_ca_key="/path/to/parent.key",
                path_length=11,
            )
