"""
Serialization Tests Module

This module provides comprehensive tests for serialization and deserialization
of all data models in the MCP Security Framework. It tests JSON serialization,
model validation, and data consistency.

Test Classes:
    TestConfigSerialization: Tests for configuration model serialization
    TestModelSerialization: Tests for data model serialization
    TestResponseSerialization: Tests for response model serialization

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime, timezone
from typing import Any, Dict

from mcp_security_framework.schemas.config import (
    AuthConfig,
    AuthMethod,
    CertificateConfig,
    LoggingConfig,
    LogLevel,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
    TLSVersion,
)
from mcp_security_framework.schemas.models import (
    AuthResult,
    AuthStatus,
    CertificateInfo,
    CertificateType,
    RateLimitStatus,
    ValidationResult,
    ValidationStatus,
)
from mcp_security_framework.schemas.responses import (
    ErrorCode,
    ErrorResponse,
    ResponseStatus,
    SecurityResponse,
    SuccessResponse,
)


class TestConfigSerialization:
    """Test suite for configuration model serialization."""

    def test_ssl_config_serialization(self):
        """Test SSLConfig serialization and deserialization."""
        config = SSLConfig(
            enabled=False,  # Disabled to avoid file validation
            cert_file=None,
            key_file=None,
            ca_cert_file=None,
            verify_mode="CERT_REQUIRED",
            min_tls_version=TLSVersion.TLS_1_2,
            max_tls_version=TLSVersion.TLS_1_3,
            cipher_suite="ECDHE-RSA-AES256-GCM-SHA384",
            check_hostname=True,
            check_expiry=True,
            expiry_warning_days=30,
        )

        # Test model_dump
        data = config.model_dump()
        assert data["enabled"] is False
        assert data["cert_file"] is None
        assert data["key_file"] is None
        assert data["verify_mode"] == "CERT_REQUIRED"
        assert data["min_tls_version"] == "TLSv1.2"
        assert data["max_tls_version"] == "TLSv1.3"

        # Test model_dump_json
        json_str = config.model_dump_json()
        assert isinstance(json_str, str)
        assert "TLSv1.2" in json_str
        assert "CERT_REQUIRED" in json_str

        # Test deserialization
        parsed_config = SSLConfig.model_validate_json(json_str)
        assert parsed_config.enabled == config.enabled
        assert parsed_config.cert_file == config.cert_file
        assert parsed_config.min_tls_version == config.min_tls_version

    def test_auth_config_serialization(self):
        """Test AuthConfig serialization and deserialization."""
        config = AuthConfig(
            enabled=True,
            methods=[AuthMethod.API_KEY, AuthMethod.JWT],
            api_keys={"admin": "admin_key_123", "user": "user_key_456"},
            jwt_secret="secret_key",
            jwt_expiry_hours=24,
            jwt_algorithm="HS256",
            public_paths=["/docs", "/health"],
            require_auth_for_all=True,
            default_role="guest",
        )

        # Test model_dump
        data = config.model_dump()
        assert data["enabled"] is True
        assert data["methods"] == ["api_key", "jwt"]
        assert data["api_keys"]["admin"] == "admin_key_123"
        assert data["jwt_algorithm"] == "HS256"

        # Test model_dump_json
        json_str = config.model_dump_json()
        assert isinstance(json_str, str)
        assert "admin_key_123" in json_str
        assert "api_key" in json_str

        # Test deserialization
        parsed_config = AuthConfig.model_validate_json(json_str)
        assert parsed_config.enabled == config.enabled
        assert parsed_config.methods == config.methods
        assert parsed_config.api_keys == config.api_keys

    def test_security_config_serialization(self):
        """Test SecurityConfig serialization and deserialization."""
        config = SecurityConfig(
            ssl=SSLConfig(enabled=False),  # Disabled to avoid file validation
            auth=AuthConfig(enabled=True, methods=[AuthMethod.API_KEY]),
            certificates=CertificateConfig(cert_storage_path="./certs"),
            permissions=PermissionConfig(
                roles_file=None
            ),  # Set to None to avoid file validation
            rate_limit=RateLimitConfig(enabled=True, default_requests_per_minute=100),
            logging=LoggingConfig(level=LogLevel.INFO),
        )

        # Test model_dump
        data = config.model_dump()
        assert data["ssl"]["enabled"] is False
        assert data["auth"]["enabled"] is True
        assert data["certificates"]["cert_storage_path"] == "./certs"
        assert data["permissions"]["roles_file"] is None
        assert data["rate_limit"]["default_requests_per_minute"] == 100

        # Test model_dump_json
        json_str = config.model_dump_json()
        assert isinstance(json_str, str)

        # Test deserialization
        parsed_config = SecurityConfig.model_validate_json(json_str)
        assert parsed_config.ssl.enabled == config.ssl.enabled
        assert parsed_config.auth.enabled == config.auth.enabled
        assert (
            parsed_config.certificates.cert_storage_path
            == config.certificates.cert_storage_path
        )


class TestModelSerialization:
    """Test suite for data model serialization."""

    def test_auth_result_serialization(self):
        """Test AuthResult serialization and deserialization."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            user_id="user_123",
            roles=["admin", "user"],
            permissions={"read", "write", "delete"},
            auth_method=AuthMethod.API_KEY,
            auth_timestamp=datetime.now(timezone.utc),
            error_code=None,
            error_message=None,
            metadata={"ip": "192.168.1.1", "user_agent": "test-agent"},
        )

        # Test model_dump
        data = auth_result.model_dump()
        assert data["is_valid"] is True
        assert data["status"] == "success"
        assert data["username"] == "test_user"
        assert data["roles"] == ["admin", "user"]
        assert data["auth_method"] == "api_key"
        assert "ip" in data["metadata"]

        # Test model_dump_json
        json_str = auth_result.model_dump_json()
        assert isinstance(json_str, str)
        assert "test_user" in json_str
        assert "admin" in json_str

        # Test deserialization
        parsed_result = AuthResult.model_validate_json(json_str)
        assert parsed_result.is_valid == auth_result.is_valid
        assert parsed_result.status == auth_result.status
        assert parsed_result.username == auth_result.username
        assert parsed_result.roles == auth_result.roles

    def test_validation_result_serialization(self):
        """Test ValidationResult serialization and deserialization."""
        validation_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            field_name="permissions",
            value=["read", "write"],
            error_code=None,
            error_message=None,
            warnings=[],
            metadata={"resource": "/api/data", "action": "GET"},
        )

        # Test model_dump
        data = validation_result.model_dump()
        assert data["is_valid"] is True
        assert data["status"] == "valid"
        assert data["field_name"] == "permissions"
        assert data["value"] == ["read", "write"]
        assert data["metadata"]["resource"] == "/api/data"

        # Test model_dump_json
        json_str = validation_result.model_dump_json()
        assert isinstance(json_str, str)
        assert "read" in json_str
        assert "write" in json_str

        # Test deserialization
        parsed_result = ValidationResult.model_validate_json(json_str)
        assert parsed_result.is_valid == validation_result.is_valid
        assert parsed_result.status == validation_result.status
        assert parsed_result.field_name == validation_result.field_name

    def test_certificate_info_serialization(self):
        """Test CertificateInfo serialization and deserialization."""
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com", "O": "Test Org"},
            issuer={"CN": "Test CA", "O": "Test CA Org"},
            serial_number="1234567890",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc),
            certificate_type=CertificateType.SERVER,
            is_expired=False,
            is_revoked=False,
            revocation_reason=None,
            roles=["server"],
            permissions={"ssl"},
            key_usage=["digitalSignature", "keyEncipherment"],
            extended_key_usage=["serverAuth"],
            signature_algorithm="sha256WithRSAEncryption",
            public_key_algorithm="rsaEncryption",
            key_size=2048,
        )

        # Test model_dump
        data = cert_info.model_dump()
        assert data["subject"]["CN"] == "test.example.com"
        assert data["issuer"]["CN"] == "Test CA"
        assert data["serial_number"] == "1234567890"
        assert data["roles"] == ["server"]
        assert data["key_size"] == 2048

        # Test model_dump_json
        json_str = cert_info.model_dump_json()
        assert isinstance(json_str, str)
        assert "test.example.com" in json_str
        assert "Test CA" in json_str

        # Test deserialization
        parsed_info = CertificateInfo.model_validate_json(json_str)
        assert parsed_info.subject["CN"] == cert_info.subject["CN"]
        assert parsed_info.issuer["CN"] == cert_info.issuer["CN"]
        assert parsed_info.key_size == cert_info.key_size

    def test_rate_limit_status_serialization(self):
        """Test RateLimitStatus serialization and deserialization."""
        now = datetime.now(timezone.utc)
        rate_limit_status = RateLimitStatus(
            identifier="user:test_user",
            current_count=50,
            limit=100,
            window_start=now,
            window_end=now,
            window_size_seconds=60,
            is_exceeded=False,
            remaining_requests=50,
            reset_time=now,
        )

        # Test model_dump
        data = rate_limit_status.model_dump()
        assert data["identifier"] == "user:test_user"
        assert data["current_count"] == 50
        assert data["limit"] == 100
        assert data["is_exceeded"] is False
        assert data["remaining_requests"] == 50

        # Test model_dump_json
        json_str = rate_limit_status.model_dump_json()
        assert isinstance(json_str, str)
        assert "test_user" in json_str
        assert "50" in json_str

        # Test deserialization
        parsed_status = RateLimitStatus.model_validate_json(json_str)
        assert parsed_status.identifier == rate_limit_status.identifier
        assert parsed_status.current_count == rate_limit_status.current_count
        assert parsed_status.remaining_requests == rate_limit_status.remaining_requests


class TestResponseSerialization:
    """Test suite for response model serialization."""

    def test_security_response_serialization(self):
        """Test SecurityResponse serialization and deserialization."""
        response = SecurityResponse[Dict[str, Any]](
            status=ResponseStatus.SUCCESS,
            message="Operation completed successfully",
            data={"result": "success", "count": 5},
            timestamp=datetime.now(timezone.utc),
            request_id="req_123",
            metadata={"version": "1.0.0", "environment": "production"},
        )

        # Test model_dump
        data = response.model_dump()
        assert data["status"] == "success"
        assert data["message"] == "Operation completed successfully"
        assert data["data"]["result"] == "success"
        assert data["data"]["count"] == 5
        assert data["metadata"]["version"] == "1.0.0"

        # Test model_dump_json
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert "success" in json_str
        assert "Operation completed successfully" in json_str

        # Test deserialization
        parsed_response = SecurityResponse.model_validate_json(json_str)
        assert parsed_response.status == response.status
        assert parsed_response.message == response.message
        assert parsed_response.data["result"] == response.data["result"]

    def test_error_response_serialization(self):
        """Test ErrorResponse serialization and deserialization."""
        error_response = ErrorResponse(
            status=ResponseStatus.ERROR,
            message="Authentication failed",
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            error_type="AuthenticationError",
            http_status_code=401,
            details="Invalid credentials for user test_user",
            timestamp=datetime.now(timezone.utc),
            request_id="req_456",
        )

        # Test model_dump
        data = error_response.model_dump()
        assert data["status"] == "error"
        assert data["message"] == "Authentication failed"
        assert data["error_code"] == "AUTHENTICATION_FAILED"
        assert data["http_status_code"] == 401
        assert "test_user" in data["details"]

        # Test model_dump_json
        json_str = error_response.model_dump_json()
        assert isinstance(json_str, str)
        assert "Authentication failed" in json_str
        assert "AUTHENTICATION_FAILED" in json_str

        # Test deserialization
        parsed_response = ErrorResponse.model_validate_json(json_str)
        assert parsed_response.status == error_response.status
        assert parsed_response.error_code == error_response.error_code
        assert parsed_response.http_status_code == error_response.http_status_code

    def test_success_response_serialization(self):
        """Test SuccessResponse serialization and deserialization."""
        success_response = SuccessResponse[Dict[str, Any]](
            status=ResponseStatus.SUCCESS,
            message="Data retrieved successfully",
            data={"items": [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]},
            timestamp=datetime.now(timezone.utc),
            request_id="req_789",
        )

        # Test model_dump
        data = success_response.model_dump()
        assert data["status"] == "success"
        assert data["message"] == "Data retrieved successfully"
        assert len(data["data"]["items"]) == 2

        # Test model_dump_json
        json_str = success_response.model_dump_json()
        assert isinstance(json_str, str)
        assert "Data retrieved successfully" in json_str
        assert "item1" in json_str
        assert "item2" in json_str

        # Test deserialization
        parsed_response = SuccessResponse.model_validate_json(json_str)
        assert parsed_response.status == success_response.status
        assert parsed_response.message == success_response.message
        assert len(parsed_response.data["items"]) == 2


class TestEdgeCases:
    """Test suite for edge cases in serialization."""

    def test_empty_data_serialization(self):
        """Test serialization with empty data."""
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            user_id=None,
            roles=[],
            permissions=set(),
            auth_method=None,
            auth_timestamp=datetime.now(timezone.utc),
            error_code=-32001,
            error_message="Authentication failed",
            metadata={},
        )

        json_str = auth_result.model_dump_json()
        parsed_result = AuthResult.model_validate_json(json_str)

        assert parsed_result.is_valid is False
        assert parsed_result.status == AuthStatus.FAILED
        assert parsed_result.username is None
        assert parsed_result.roles == []
        assert parsed_result.error_code == -32001

    def test_nested_object_serialization(self):
        """Test serialization of nested objects."""
        config = SecurityConfig(
            ssl=SSLConfig(enabled=False),  # Disabled to avoid file validation
            auth=AuthConfig(
                enabled=True,
                methods=[AuthMethod.API_KEY],
                api_keys={"admin": "admin_key"},
            ),
            certificates=CertificateConfig(cert_storage_path="./certs"),
            permissions=PermissionConfig(
                roles_file=None
            ),  # Set to None to avoid file validation
            rate_limit=RateLimitConfig(enabled=True, default_requests_per_minute=100),
            logging=LoggingConfig(level=LogLevel.INFO),
        )

        json_str = config.model_dump_json()
        parsed_config = SecurityConfig.model_validate_json(json_str)

        assert parsed_config.ssl.enabled is False
        assert parsed_config.auth.enabled is True
        assert parsed_config.auth.api_keys["admin"] == "admin_key"
        assert parsed_config.rate_limit.default_requests_per_minute == 100

    def test_datetime_serialization(self):
        """Test datetime serialization and deserialization."""
        timestamp = datetime.now(timezone.utc)

        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            auth_timestamp=timestamp,
            roles=["user"],
        )

        json_str = auth_result.model_dump_json()
        parsed_result = AuthResult.model_validate_json(json_str)

        # Check that datetime is properly serialized and deserialized
        assert parsed_result.auth_timestamp is not None
        assert isinstance(parsed_result.auth_timestamp, datetime)

    def test_enum_serialization(self):
        """Test enum serialization and deserialization."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            auth_method=AuthMethod.JWT,
            roles=["user"],
        )

        json_str = auth_result.model_dump_json()
        parsed_result = AuthResult.model_validate_json(json_str)

        assert parsed_result.auth_method == AuthMethod.JWT
        assert parsed_result.auth_method == "jwt"
