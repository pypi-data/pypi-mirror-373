"""
Response Models Test Module

This module provides comprehensive unit tests for all response models
in the MCP Security Framework. It tests validation, factory methods,
and edge cases for all response classes.

Test Classes:
    TestSecurityResponse: Tests for base security response model
    TestErrorResponse: Tests for error response model
    TestSuccessResponse: Tests for success response model
    TestValidationResponse: Tests for validation response model
    TestAuthResponse: Tests for authentication response model
    TestCertificateResponse: Tests for certificate response model
    TestPermissionResponse: Tests for permission response model
    TestRateLimitResponse: Tests for rate limiting response model

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
    CertificateInfo,
    CertificateType,
    RateLimitStatus,
    ValidationResult,
    ValidationStatus,
)
from mcp_security_framework.schemas.responses import (
    AuthResponse,
    CertificateResponse,
    ErrorCode,
    ErrorResponse,
    PermissionResponse,
    RateLimitResponse,
    ResponseStatus,
    SecurityResponse,
    SuccessResponse,
    ValidationResponse,
)


class TestSecurityResponse:
    """Test suite for SecurityResponse class."""

    def test_security_response_basic(self):
        """Test SecurityResponse with basic information."""
        response = SecurityResponse(
            status=ResponseStatus.SUCCESS,
            message="Operation completed successfully",
            data={"key": "value"},
        )

        assert response.status == ResponseStatus.SUCCESS
        assert response.message == "Operation completed successfully"
        assert response.data == {"key": "value"}
        assert response.timestamp is not None
        assert response.request_id is None
        assert response.version == "1.0.0"
        assert response.metadata == {}

    def test_security_response_with_metadata(self):
        """Test SecurityResponse with metadata."""
        response = SecurityResponse(
            status=ResponseStatus.SUCCESS,
            message="Operation completed successfully",
            data={"key": "value"},
            request_id="req-123",
            metadata={"user_id": "12345", "operation": "create"},
        )

        assert response.request_id == "req-123"
        assert response.metadata == {"user_id": "12345", "operation": "create"}

    def test_security_response_message_validation(self):
        """Test SecurityResponse message validation."""
        # Valid message
        response = SecurityResponse(
            status=ResponseStatus.SUCCESS, message="Valid message"
        )
        assert response.message == "Valid message"

        # Message with whitespace
        response = SecurityResponse(
            status=ResponseStatus.SUCCESS, message="  Valid message  "
        )
        assert response.message == "Valid message"

        # Empty message
        with pytest.raises(ValidationError) as exc_info:
            SecurityResponse(status=ResponseStatus.SUCCESS, message="")

        assert "Response message cannot be empty" in str(exc_info.value)

    def test_security_response_properties(self):
        """Test SecurityResponse properties."""
        # Success response
        response = SecurityResponse(status=ResponseStatus.SUCCESS, message="Success")

        assert response.is_success is True
        assert response.is_error is False

        # Error response
        response = SecurityResponse(status=ResponseStatus.ERROR, message="Error")

        assert response.is_success is False
        assert response.is_error is True


class TestErrorResponse:
    """Test suite for ErrorResponse class."""

    def test_error_response_basic(self):
        """Test ErrorResponse with basic information."""
        error_response = ErrorResponse(
            status=ResponseStatus.ERROR,
            message="Authentication failed",
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            http_status_code=401,
            details="Invalid API key provided",
        )

        assert error_response.status == ResponseStatus.ERROR
        assert error_response.message == "Authentication failed"
        assert error_response.error_code == ErrorCode.AUTHENTICATION_FAILED
        assert error_response.http_status_code == 401
        assert error_response.details == "Invalid API key provided"
        assert error_response.error_type == "SecurityError"
        assert error_response.field_errors == {}
        assert error_response.stack_trace is None
        assert error_response.retry_after is None

    def test_error_response_complete(self):
        """Test ErrorResponse with complete information."""
        error_response = ErrorResponse(
            status=ResponseStatus.ERROR,
            message="Validation failed",
            error_code=ErrorCode.VALIDATION_ERROR,
            http_status_code=400,
            details="Multiple validation errors occurred",
            field_errors={"username": ["Required field"], "email": ["Invalid format"]},
            stack_trace="Traceback (most recent call last):...",
            retry_after=60,
            error_type="ValidationError",
        )

        assert error_response.field_errors == {
            "username": ["Required field"],
            "email": ["Invalid format"],
        }
        assert error_response.stack_trace == "Traceback (most recent call last):..."
        assert error_response.retry_after == 60
        assert error_response.error_type == "ValidationError"

    def test_error_response_status_validation(self):
        """Test ErrorResponse status validation."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                status=ResponseStatus.SUCCESS,  # Should be ERROR
                message="Error message",
                error_code=ErrorCode.AUTHENTICATION_FAILED,
                http_status_code=401,
            )

        assert "Error responses must have ERROR status" in str(exc_info.value)

    def test_error_response_http_status_code_validation(self):
        """Test ErrorResponse HTTP status code validation."""
        # Valid range
        error_response = ErrorResponse(
            status=ResponseStatus.ERROR,
            message="Error",
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            http_status_code=401,
        )
        assert error_response.http_status_code == 401

        # Invalid range - too low
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                status=ResponseStatus.ERROR,
                message="Error",
                error_code=ErrorCode.AUTHENTICATION_FAILED,
                http_status_code=200,  # Should be 4xx or 5xx
            )

        assert "Input should be greater than or equal to 400" in str(exc_info.value)

        # Invalid range - too high
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                status=ResponseStatus.ERROR,
                message="Error",
                error_code=ErrorCode.AUTHENTICATION_FAILED,
                http_status_code=600,  # Should be 4xx or 5xx
            )

        assert "Input should be less than or equal to 599" in str(exc_info.value)

    def test_error_response_consistency_validation(self):
        """Test ErrorResponse consistency validation."""
        # Authentication failed should have 401
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                status=ResponseStatus.ERROR,
                message="Authentication failed",
                error_code=ErrorCode.AUTHENTICATION_FAILED,
                http_status_code=403,  # Should be 401
            )

        assert "Authentication failed should have HTTP status 401" in str(
            exc_info.value
        )

        # Insufficient permissions should have 403
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                status=ResponseStatus.ERROR,
                message="Insufficient permissions",
                error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
                http_status_code=401,  # Should be 403
            )

        assert "Insufficient permissions should have HTTP status 403" in str(
            exc_info.value
        )

        # Rate limit exceeded should have 429
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                status=ResponseStatus.ERROR,
                message="Rate limit exceeded",
                error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
                http_status_code=400,  # Should be 429
            )

        assert "Rate limit exceeded should have HTTP status 429" in str(exc_info.value)

    def test_error_response_factory_methods(self):
        """Test ErrorResponse factory methods."""
        # Authentication error
        auth_error = ErrorResponse.create_authentication_error(
            "Invalid credentials", "API key not found"
        )

        assert auth_error.status == ResponseStatus.ERROR
        assert auth_error.message == "Invalid credentials"
        assert auth_error.error_code == ErrorCode.AUTHENTICATION_FAILED
        assert auth_error.http_status_code == 401
        assert auth_error.details == "API key not found"
        assert auth_error.error_type == "AuthenticationError"

        # Permission error
        perm_error = ErrorResponse.create_permission_error(
            "Access denied", "User lacks required permissions"
        )

        assert perm_error.status == ResponseStatus.ERROR
        assert perm_error.message == "Access denied"
        assert perm_error.error_code == ErrorCode.INSUFFICIENT_PERMISSIONS
        assert perm_error.http_status_code == 403
        assert perm_error.details == "User lacks required permissions"
        assert perm_error.error_type == "PermissionError"

        # Rate limit error
        rate_error = ErrorResponse.create_rate_limit_error("Too many requests", 60)

        assert rate_error.status == ResponseStatus.ERROR
        assert rate_error.message == "Too many requests"
        assert rate_error.error_code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert rate_error.http_status_code == 429
        assert rate_error.retry_after == 60
        assert rate_error.error_type == "RateLimitError"

        # Validation error
        field_errors = {"username": ["Required"], "email": ["Invalid format"]}
        val_error = ErrorResponse.create_validation_error(
            "Validation failed", field_errors
        )

        assert val_error.status == ResponseStatus.ERROR
        assert val_error.message == "Validation failed"
        assert val_error.error_code == ErrorCode.VALIDATION_ERROR
        assert val_error.http_status_code == 400
        assert val_error.field_errors == field_errors
        assert val_error.error_type == "ValidationError"


class TestSuccessResponse:
    """Test suite for SuccessResponse class."""

    def test_success_response_basic(self):
        """Test SuccessResponse with basic information."""
        success_response = SuccessResponse(
            status=ResponseStatus.SUCCESS,
            message="Operation completed successfully",
            data={"user_id": "12345", "status": "active"},
        )

        assert success_response.status == ResponseStatus.SUCCESS
        assert success_response.message == "Operation completed successfully"
        assert success_response.data == {"user_id": "12345", "status": "active"}
        assert success_response.total_count is None
        assert success_response.page is None
        assert success_response.page_size is None
        assert success_response.has_more is None

    def test_success_response_with_pagination(self):
        """Test SuccessResponse with pagination information."""
        success_response = SuccessResponse(
            status=ResponseStatus.SUCCESS,
            message="Users retrieved successfully",
            data=[{"id": "1"}, {"id": "2"}],
            total_count=100,
            page=1,
            page_size=10,
            has_more=True,
        )

        assert success_response.total_count == 100
        assert success_response.page == 1
        assert success_response.page_size == 10
        assert success_response.has_more is True

    def test_success_response_status_validation(self):
        """Test SuccessResponse status validation."""
        with pytest.raises(ValidationError) as exc_info:
            SuccessResponse(
                status=ResponseStatus.ERROR,  # Should be SUCCESS
                message="Success",
                data={"key": "value"},
            )

        assert "Success responses must have SUCCESS status" in str(exc_info.value)

    def test_success_response_data_validation(self):
        """Test SuccessResponse data validation."""
        with pytest.raises(ValidationError) as exc_info:
            SuccessResponse(
                status=ResponseStatus.SUCCESS,
                message="Success",
                data=None,  # Should not be None
            )

        assert "Success responses must have data" in str(exc_info.value)

    def test_success_response_pagination_validation(self):
        """Test SuccessResponse pagination validation."""
        # Valid pagination
        success_response = SuccessResponse(
            status=ResponseStatus.SUCCESS,
            message="Success",
            data=[],
            total_count=0,
            page=1,
            page_size=10,
        )
        assert success_response.total_count == 0
        assert success_response.page == 1
        assert success_response.page_size == 10

        # Invalid total_count
        with pytest.raises(ValidationError):
            SuccessResponse(
                message="Success", data=[], total_count=-1
            )  # Should be >= 0

        # Invalid page
        with pytest.raises(ValidationError):
            SuccessResponse(message="Success", data=[], page=0)  # Should be >= 1

        # Invalid page_size
        with pytest.raises(ValidationError):
            SuccessResponse(message="Success", data=[], page_size=0)  # Should be >= 1

    def test_success_response_factory_method(self):
        """Test SuccessResponse factory method."""
        data = {"user_id": "12345", "name": "John Doe"}
        success_response = SuccessResponse.create_success(
            data=data, message="User created successfully"
        )

        assert success_response.status == ResponseStatus.SUCCESS
        assert success_response.message == "User created successfully"
        assert success_response.data == data

        # Default message
        success_response = SuccessResponse.create_success(data=data)
        assert success_response.message == "Operation completed successfully"


class TestValidationResponse:
    """Test suite for ValidationResponse class."""

    def test_validation_response_success(self):
        """Test ValidationResponse with successful validation."""
        validation_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            field_name="username",
            value="testuser",
        )

        validation_response = ValidationResponse(
            status=ResponseStatus.SUCCESS,
            message="Validation completed successfully",
            validation_result=validation_result,
        )

        assert validation_response.status == ResponseStatus.SUCCESS
        assert validation_response.message == "Validation completed successfully"
        assert validation_response.validation_result == validation_result
        assert validation_response.field_errors == {}
        assert validation_response.warnings == []
        assert validation_response.suggestions == []

    def test_validation_response_error(self):
        """Test ValidationResponse with validation error."""
        validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            field_name="password",
            value="",
            error_code=400,
            error_message="Password cannot be empty",
        )

        field_errors = {"password": ["Required field"], "email": ["Invalid format"]}
        validation_response = ValidationResponse(
            status=ResponseStatus.ERROR,
            message="Validation failed",
            validation_result=validation_result,
            field_errors=field_errors,
            warnings=["Password is too weak"],
            suggestions=["Use at least 8 characters"],
        )

        assert validation_response.status == ResponseStatus.ERROR
        assert validation_response.message == "Validation failed"
        assert validation_response.validation_result == validation_result
        assert validation_response.field_errors == field_errors
        assert validation_response.warnings == ["Password is too weak"]
        assert validation_response.suggestions == ["Use at least 8 characters"]

    def test_validation_response_status_validation(self):
        """Test ValidationResponse status validation."""
        # Valid validation should have SUCCESS status
        validation_result = ValidationResult(
            is_valid=True, status=ValidationStatus.VALID
        )

        with pytest.raises(ValidationError) as exc_info:
            ValidationResponse(
                status=ResponseStatus.ERROR,  # Should be SUCCESS
                message="Validation failed",
                validation_result=validation_result,
            )

        assert "Valid validation must have SUCCESS status" in str(exc_info.value)

        # Invalid validation should have ERROR status
        validation_result = ValidationResult(
            is_valid=False, status=ValidationStatus.INVALID
        )

        with pytest.raises(ValidationError) as exc_info:
            ValidationResponse(
                status=ResponseStatus.SUCCESS,  # Should be ERROR
                message="Validation succeeded",
                validation_result=validation_result,
            )

        assert "Invalid validation must have ERROR status" in str(exc_info.value)

    def test_validation_response_factory_methods(self):
        """Test ValidationResponse factory methods."""
        # Success validation
        validation_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            field_name="username",
            value="testuser",
        )

        success_response = ValidationResponse.create_validation_success(
            validation_result
        )

        assert success_response.status == ResponseStatus.SUCCESS
        assert success_response.message == "Validation completed successfully"
        assert success_response.validation_result == validation_result

        # Error validation
        validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            field_name="password",
            value="",
            error_code=400,
            error_message="Password cannot be empty",
        )

        field_errors = {"password": ["Required field"]}
        error_response = ValidationResponse.create_validation_error(
            validation_result, field_errors
        )

        assert error_response.status == ResponseStatus.ERROR
        assert error_response.message == "Validation failed"
        assert error_response.validation_result == validation_result
        assert error_response.field_errors == field_errors


class TestAuthResponse:
    """Test suite for AuthResponse class."""

    def test_auth_response_success(self):
        """Test AuthResponse with successful authentication."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="testuser",
            roles=["user", "admin"],
            permissions={"read", "write"},
            auth_method=AuthMethod.API_KEY,
        )

        auth_response = AuthResponse(
            status=ResponseStatus.SUCCESS,
            message="Authentication successful",
            auth_result=auth_result,
            user_info={"email": "test@example.com"},
            session_info={"session_id": "sess-123"},
            token_info={"expires_in": 3600},
        )

        assert auth_response.status == ResponseStatus.SUCCESS
        assert auth_response.message == "Authentication successful"
        assert auth_response.auth_result == auth_result
        assert auth_response.user_info == {"email": "test@example.com"}
        assert auth_response.session_info == {"session_id": "sess-123"}
        assert auth_response.token_info == {"expires_in": 3600}

    def test_auth_response_error(self):
        """Test AuthResponse with authentication error."""
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            error_code=401,
            error_message="Invalid credentials",
        )

        auth_response = AuthResponse(
            status=ResponseStatus.ERROR,
            message="Authentication failed",
            auth_result=auth_result,
        )

        assert auth_response.status == ResponseStatus.ERROR
        assert auth_response.message == "Authentication failed"
        assert auth_response.auth_result == auth_result
        assert auth_response.user_info == {}
        assert auth_response.session_info == {}
        assert auth_response.token_info == {}

    def test_auth_response_status_validation(self):
        """Test AuthResponse status validation."""
        # Successful auth should have SUCCESS status
        auth_result = AuthResult(is_valid=True, status=AuthStatus.SUCCESS)

        with pytest.raises(ValidationError) as exc_info:
            AuthResponse(
                status=ResponseStatus.ERROR,  # Should be SUCCESS
                message="Authentication failed",
                auth_result=auth_result,
            )

        assert "Successful authentication must have SUCCESS status" in str(
            exc_info.value
        )

        # Failed auth should have ERROR status
        auth_result = AuthResult(is_valid=False, status=AuthStatus.FAILED)

        with pytest.raises(ValidationError) as exc_info:
            AuthResponse(
                status=ResponseStatus.SUCCESS,  # Should be ERROR
                message="Authentication succeeded",
                auth_result=auth_result,
            )

        assert "Failed authentication must have ERROR status" in str(exc_info.value)

    def test_auth_response_factory_methods(self):
        """Test AuthResponse factory methods."""
        # Success authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="testuser",
            roles=["user"],
            permissions={"read"},
        )

        user_info = {"email": "test@example.com"}
        success_response = AuthResponse.create_auth_success(auth_result, user_info)

        assert success_response.status == ResponseStatus.SUCCESS
        assert success_response.message == "Authentication successful"
        assert success_response.auth_result == auth_result
        assert success_response.user_info == user_info

        # Error authentication
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            error_code=401,
            error_message="Invalid credentials",
        )

        error_response = AuthResponse.create_auth_error(auth_result)

        assert error_response.status == ResponseStatus.ERROR
        assert error_response.message == "Invalid credentials"
        assert error_response.auth_result == auth_result


class TestCertificateResponse:
    """Test suite for CertificateResponse class."""

    def test_certificate_response_success(self):
        """Test CertificateResponse with successful certificate info."""
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        cert_response = CertificateResponse(
            status=ResponseStatus.SUCCESS,
            message="Certificate information retrieved successfully",
            certificate_info=cert_info,
            chain_info={"length": 2},
            expiry_info={"days_remaining": 300},
        )

        assert cert_response.status == ResponseStatus.SUCCESS
        assert cert_response.message == "Certificate information retrieved successfully"
        assert cert_response.certificate_info == cert_info
        assert cert_response.validation_result is None
        assert cert_response.chain_info == {"length": 2}
        assert cert_response.expiry_info == {"days_remaining": 300}

    def test_certificate_response_with_validation(self):
        """Test CertificateResponse with validation result."""
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        validation_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            field_name="certificate",
            value=cert_info,
        )

        cert_response = CertificateResponse(
            status=ResponseStatus.SUCCESS,
            message="Certificate validated successfully",
            certificate_info=cert_info,
            validation_result=validation_result,
        )

        assert cert_response.validation_result == validation_result

    def test_certificate_response_validation_consistency(self):
        """Test CertificateResponse validation consistency."""
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            field_name="certificate",
            value=cert_info,
        )

        # Invalid validation cannot have SUCCESS status
        with pytest.raises(ValidationError) as exc_info:
            CertificateResponse(
                status=ResponseStatus.SUCCESS,  # Should be ERROR
                message="Certificate validated successfully",
                certificate_info=cert_info,
                validation_result=validation_result,
            )

        assert "Invalid certificate validation cannot have SUCCESS status" in str(
            exc_info.value
        )

    def test_certificate_response_factory_method(self):
        """Test CertificateResponse factory method."""
        cert_info = CertificateInfo(
            subject={"CN": "test.example.com"},
            issuer={"CN": "Test CA"},
            serial_number="123456789",
            not_before=datetime.now(timezone.utc),
            not_after=datetime.now(timezone.utc) + timedelta(days=365),
            certificate_type=CertificateType.SERVER,
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption",
        )

        validation_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            field_name="certificate",
            value=cert_info,
        )

        success_response = CertificateResponse.create_certificate_success(
            cert_info, validation_result
        )

        assert success_response.status == ResponseStatus.SUCCESS
        assert (
            success_response.message == "Certificate information retrieved successfully"
        )
        assert success_response.certificate_info == cert_info
        assert success_response.validation_result == validation_result


class TestPermissionResponse:
    """Test suite for PermissionResponse class."""

    def test_permission_response_granted(self):
        """Test PermissionResponse with granted access."""
        user_roles = ["user", "admin"]
        user_permissions = {"read", "write", "delete"}
        required_permissions = ["read", "write"]

        perm_response = PermissionResponse(
            status=ResponseStatus.SUCCESS,
            message="Access granted",
            user_roles=user_roles,
            user_permissions=user_permissions,
            effective_permissions=user_permissions,
            access_granted=True,
            required_permissions=required_permissions,
            missing_permissions=[],
        )

        assert perm_response.status == ResponseStatus.SUCCESS
        assert perm_response.message == "Access granted"
        assert perm_response.user_roles == user_roles
        assert perm_response.user_permissions == user_permissions
        assert perm_response.effective_permissions == user_permissions
        assert perm_response.access_granted is True
        assert perm_response.required_permissions == required_permissions
        assert perm_response.missing_permissions == []

    def test_permission_response_denied(self):
        """Test PermissionResponse with denied access."""
        user_roles = ["user"]
        user_permissions = {"read"}
        required_permissions = ["read", "write", "delete"]
        missing_permissions = ["write", "delete"]

        perm_response = PermissionResponse(
            status=ResponseStatus.ERROR,
            message="Access denied - insufficient permissions",
            user_roles=user_roles,
            user_permissions=user_permissions,
            effective_permissions=user_permissions,
            access_granted=False,
            required_permissions=required_permissions,
            missing_permissions=missing_permissions,
        )

        assert perm_response.status == ResponseStatus.ERROR
        assert perm_response.message == "Access denied - insufficient permissions"
        assert perm_response.user_roles == user_roles
        assert perm_response.user_permissions == user_permissions
        assert perm_response.effective_permissions == user_permissions
        assert perm_response.access_granted is False
        assert perm_response.required_permissions == required_permissions
        assert perm_response.missing_permissions == missing_permissions

    def test_permission_response_validation_consistency(self):
        """Test PermissionResponse validation consistency."""
        user_roles = ["user"]
        user_permissions = {"read"}
        required_permissions = ["read", "write"]

        # Granted access should have SUCCESS status
        with pytest.raises(ValidationError) as exc_info:
            PermissionResponse(
                status=ResponseStatus.ERROR,  # Should be SUCCESS
                message="Access granted",
                user_roles=user_roles,
                user_permissions=user_permissions,
                effective_permissions=user_permissions,
                access_granted=True,
                required_permissions=required_permissions,
                missing_permissions=[],
            )

        assert "Granted access must have SUCCESS status" in str(exc_info.value)

        # Denied access should have ERROR status
        with pytest.raises(ValidationError) as exc_info:
            PermissionResponse(
                status=ResponseStatus.SUCCESS,  # Should be ERROR
                message="Access denied",
                user_roles=user_roles,
                user_permissions=user_permissions,
                effective_permissions=user_permissions,
                access_granted=False,
                required_permissions=required_permissions,
                missing_permissions=["write"],
            )

        assert "Denied access must have ERROR status" in str(exc_info.value)

    def test_permission_response_factory_methods(self):
        """Test PermissionResponse factory methods."""
        user_roles = ["user", "admin"]
        user_permissions = {"read", "write", "delete"}
        required_permissions = ["read", "write"]

        # Granted access
        granted_response = PermissionResponse.create_permission_granted(
            user_roles, user_permissions, required_permissions
        )

        assert granted_response.status == ResponseStatus.SUCCESS
        assert granted_response.message == "Access granted"
        assert granted_response.user_roles == user_roles
        assert granted_response.user_permissions == user_permissions
        assert granted_response.effective_permissions == user_permissions
        assert granted_response.access_granted is True
        assert granted_response.required_permissions == required_permissions
        assert granted_response.missing_permissions == []

        # Denied access
        denied_response = PermissionResponse.create_permission_denied(
            user_roles, user_permissions, required_permissions
        )

        assert denied_response.status == ResponseStatus.ERROR
        assert denied_response.message == "Access denied - insufficient permissions"
        assert denied_response.user_roles == user_roles
        assert denied_response.user_permissions == user_permissions
        assert denied_response.effective_permissions == user_permissions
        assert denied_response.access_granted is False
        assert denied_response.required_permissions == required_permissions
        assert (
            denied_response.missing_permissions == []
        )  # User has all required permissions


class TestRateLimitResponse:
    """Test suite for RateLimitResponse class."""

    def test_rate_limit_response_within_limit(self):
        """Test RateLimitResponse when within rate limit."""
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

        rate_response = RateLimitResponse(
            status=ResponseStatus.SUCCESS,
            message="Rate limit status",
            rate_limit_status=rate_limit_status,
            usage_percentage=50.0,
            reset_time=now + timedelta(minutes=1),
        )

        assert rate_response.status == ResponseStatus.SUCCESS
        assert rate_response.message == "Rate limit status"
        assert rate_response.rate_limit_status == rate_limit_status
        assert rate_response.usage_percentage == 50.0
        assert rate_response.reset_time == now + timedelta(minutes=1)
        assert rate_response.retry_after is None

    def test_rate_limit_response_exceeded(self):
        """Test RateLimitResponse when rate limit is exceeded."""
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

        rate_response = RateLimitResponse(
            status=ResponseStatus.ERROR,
            message="Rate limit exceeded",
            rate_limit_status=rate_limit_status,
            usage_percentage=150.0,
            reset_time=now + timedelta(minutes=1),
            retry_after=60,
        )

        assert rate_response.status == ResponseStatus.ERROR
        assert rate_response.message == "Rate limit exceeded"
        assert rate_response.rate_limit_status == rate_limit_status
        assert rate_response.usage_percentage == 150.0
        assert rate_response.reset_time == now + timedelta(minutes=1)
        assert rate_response.retry_after == 60

    def test_rate_limit_response_validation_consistency(self):
        """Test RateLimitResponse validation consistency."""
        now = datetime.now(timezone.utc)

        # Exceeded rate limit should have ERROR status
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

        with pytest.raises(ValidationError) as exc_info:
            RateLimitResponse(
                status=ResponseStatus.SUCCESS,  # Should be ERROR
                message="Rate limit status",
                rate_limit_status=rate_limit_status,
                usage_percentage=150.0,
                reset_time=now + timedelta(minutes=1),
            )

        assert "Exceeded rate limit must have ERROR status" in str(exc_info.value)

        # Within rate limit should have SUCCESS status
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

        with pytest.raises(ValidationError) as exc_info:
            RateLimitResponse(
                status=ResponseStatus.ERROR,  # Should be SUCCESS
                message="Rate limit exceeded",
                rate_limit_status=rate_limit_status,
                usage_percentage=50.0,
                reset_time=now + timedelta(minutes=1),
            )

        assert "Within rate limit must have SUCCESS status" in str(exc_info.value)

    def test_rate_limit_response_factory_method(self):
        """Test RateLimitResponse factory method."""
        now = datetime.now(timezone.utc)

        # Within limit
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

        response = RateLimitResponse.create_rate_limit_status(rate_limit_status)

        assert response.status == ResponseStatus.SUCCESS
        assert response.message == "Rate limit status"
        assert response.rate_limit_status == rate_limit_status
        assert response.usage_percentage == 50.0
        assert response.reset_time == now + timedelta(minutes=1)
        assert response.retry_after is None

        # Exceeded limit
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

        response = RateLimitResponse.create_rate_limit_status(rate_limit_status)

        assert response.status == ResponseStatus.ERROR
        assert response.message == "Rate limit exceeded"
        assert response.rate_limit_status == rate_limit_status
        assert response.usage_percentage == 150.0
        assert response.reset_time == now + timedelta(minutes=1)
        assert response.retry_after is not None
        assert response.retry_after >= 59  # Allow for small time differences
