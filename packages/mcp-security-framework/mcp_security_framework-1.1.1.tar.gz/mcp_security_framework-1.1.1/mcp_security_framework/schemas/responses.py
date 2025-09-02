"""
Response Models Module

This module provides comprehensive response models for all API responses,
error handling, and validation responses used throughout the MCP Security
Framework. It includes standardized response formats with proper HTTP
status codes and error handling.

Key Features:
    - Standardized API response formats
    - Comprehensive error handling models
    - HTTP status code integration
    - Validation response models
    - Success response models
    - Consistent error message formatting

Classes:
    SecurityResponse: Base response model
    ErrorResponse: Error response model
    SuccessResponse: Success response model
    ValidationResponse: Validation response model
    AuthResponse: Authentication response model
    CertificateResponse: Certificate response model
    PermissionResponse: Permission response model
    RateLimitResponse: Rate limiting response model

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

from .models import AuthResult, CertificateInfo, RateLimitStatus, ValidationResult


class ResponseStatus(str, Enum):
    """Response status enumeration."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SecurityStatus(str, Enum):
    """Security status enumeration."""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ErrorCode(str, Enum):
    """Error code enumeration."""

    # Authentication errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Certificate errors
    CERTIFICATE_INVALID = "CERTIFICATE_INVALID"
    CERTIFICATE_EXPIRED = "CERTIFICATE_EXPIRED"
    CERTIFICATE_REVOKED = "CERTIFICATE_REVOKED"
    CERTIFICATE_CHAIN_INVALID = "CERTIFICATE_CHAIN_INVALID"
    CERTIFICATE_NOT_FOUND = "CERTIFICATE_NOT_FOUND"

    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"

    # Configuration errors
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    MISSING_CONFIGURATION = "MISSING_CONFIGURATION"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # System errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"

    # Security errors
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    ACCESS_DENIED = "ACCESS_DENIED"
    FORBIDDEN = "FORBIDDEN"
    UNAUTHORIZED = "UNAUTHORIZED"


# Generic type for response data
T = TypeVar("T")


class SecurityResponse(BaseModel, Generic[T]):
    """
    Base Security Response Model

    This is the base response model that provides a standardized
    format for all API responses in the MCP Security Framework.

    Attributes:
        status: Response status (success, error, warning, info)
        message: Human-readable response message
        data: Response data payload
        timestamp: Response timestamp
        request_id: Unique request identifier
        version: API version
        metadata: Additional response metadata
    """

    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Human-readable response message")
    data: Optional[T] = Field(default=None, description="Response data payload")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    request_id: Optional[str] = Field(
        default=None, description="Unique request identifier"
    )
    version: str = Field(default="1.0.0", description="API version")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional response metadata"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        """Validate response message."""
        if len(v.strip()) == 0:
            raise ValueError("Response message cannot be empty")
        return v.strip()

    @property
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.status == ResponseStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        """Check if response indicates error."""
        return self.status == ResponseStatus.ERROR


class ErrorResponse(SecurityResponse[None]):
    """
    Error Response Model

    This model represents error responses with detailed error
    information including error codes, HTTP status codes, and
    additional error context.

    Attributes:
        error_code: Specific error code
        http_status_code: HTTP status code
        details: Detailed error information
        field_errors: Field-specific validation errors
        stack_trace: Stack trace for debugging (optional)
        retry_after: Retry after time in seconds
        error_type: Type of error
    """

    error_code: ErrorCode = Field(..., description="Specific error code")
    http_status_code: int = Field(..., ge=400, le=599, description="HTTP status code")
    details: Optional[str] = Field(
        default=None, description="Detailed error information"
    )
    field_errors: Dict[str, List[str]] = Field(
        default_factory=dict, description="Field-specific validation errors"
    )
    stack_trace: Optional[str] = Field(
        default=None, description="Stack trace for debugging"
    )
    retry_after: Optional[int] = Field(
        default=None, ge=0, description="Retry after time in seconds"
    )
    error_type: str = Field(default="SecurityError", description="Type of error")

    @field_validator("status")
    @classmethod
    def validate_error_status(cls, v):
        """Validate that error responses have error status."""
        if v != ResponseStatus.ERROR:
            raise ValueError("Error responses must have ERROR status")
        return v

    @field_validator("http_status_code")
    @classmethod
    def validate_http_status_code(cls, v):
        """Validate HTTP status code for errors."""
        if v < 400 or v > 599:
            raise ValueError(
                "Error responses must have HTTP status code between 400 and 599"
            )
        return v

    @model_validator(mode="after")
    def validate_error_response(self):
        """Validate error response consistency."""
        if self.status != ResponseStatus.ERROR:
            raise ValueError("Error responses must have ERROR status")

        # Validate error code and HTTP status code consistency
        if (
            self.error_code == ErrorCode.AUTHENTICATION_FAILED
            and self.http_status_code != 401
        ):
            raise ValueError("Authentication failed should have HTTP status 401")

        if (
            self.error_code == ErrorCode.INSUFFICIENT_PERMISSIONS
            and self.http_status_code != 403
        ):
            raise ValueError("Insufficient permissions should have HTTP status 403")

        if (
            self.error_code == ErrorCode.RATE_LIMIT_EXCEEDED
            and self.http_status_code != 429
        ):
            raise ValueError("Rate limit exceeded should have HTTP status 429")

        return self

    @classmethod
    def create_authentication_error(
        cls, message: str, details: Optional[str] = None
    ) -> "ErrorResponse":
        """Create authentication error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            http_status_code=401,
            details=details,
            error_type="AuthenticationError",
        )

    @classmethod
    def create_permission_error(
        cls, message: str, details: Optional[str] = None
    ) -> "ErrorResponse":
        """Create permission error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            http_status_code=403,
            details=details,
            error_type="PermissionError",
        )

    @classmethod
    def create_rate_limit_error(
        cls, message: str, retry_after: Optional[int] = None
    ) -> "ErrorResponse":
        """Create rate limit error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            http_status_code=429,
            retry_after=retry_after,
            error_type="RateLimitError",
        )

    @classmethod
    def create_validation_error(
        cls, message: str, field_errors: Dict[str, List[str]]
    ) -> "ErrorResponse":
        """Create validation error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            http_status_code=400,
            field_errors=field_errors,
            error_type="ValidationError",
        )


class SuccessResponse(SecurityResponse[T]):
    """
    Success Response Model

    This model represents successful responses with data payload
    and optional success metadata.

    Attributes:
        data: Response data payload
        total_count: Total count for paginated responses
        page: Current page number
        page_size: Page size
        has_more: Whether there are more pages
    """

    data: T = Field(..., description="Response data payload")
    total_count: Optional[int] = Field(
        default=None, ge=0, description="Total count for paginated responses"
    )
    page: Optional[int] = Field(default=None, ge=1, description="Current page number")
    page_size: Optional[int] = Field(default=None, ge=1, description="Page size")
    has_more: Optional[bool] = Field(
        default=None, description="Whether there are more pages"
    )

    @field_validator("status")
    @classmethod
    def validate_success_status(cls, v):
        """Validate that success responses have success status."""
        if v != ResponseStatus.SUCCESS:
            raise ValueError("Success responses must have SUCCESS status")
        return v

    @model_validator(mode="after")
    def validate_success_response(self):
        """Validate success response consistency."""
        if self.status != ResponseStatus.SUCCESS:
            raise ValueError("Success responses must have SUCCESS status")

        if self.data is None:
            raise ValueError("Success responses must have data")

        return self

    @classmethod
    def create_success(
        cls, data: T, message: str = "Operation completed successfully"
    ) -> "SuccessResponse[T]":
        """Create success response."""
        return cls(status=ResponseStatus.SUCCESS, message=message, data=data)


class ValidationResponse(SecurityResponse[ValidationResult]):
    """
    Validation Response Model

    This model represents validation responses with detailed
    validation results and field-specific error information.

    Attributes:
        validation_result: Validation result object
        field_errors: Field-specific validation errors
        warnings: List of validation warnings
        suggestions: List of improvement suggestions
    """

    validation_result: ValidationResult = Field(
        ..., description="Validation result object"
    )
    field_errors: Dict[str, List[str]] = Field(
        default_factory=dict, description="Field-specific validation errors"
    )
    warnings: List[str] = Field(
        default_factory=list, description="List of validation warnings"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="List of improvement suggestions"
    )

    @field_validator("status")
    @classmethod
    def validate_validation_status(cls, v):
        """Validate validation response status."""
        # This validation will be handled by model_validator
        return v

    @model_validator(mode="after")
    def validate_validation_response(self):
        """Validate validation response consistency."""
        if self.validation_result.is_valid and self.status != ResponseStatus.SUCCESS:
            raise ValueError("Valid validation must have SUCCESS status")

        if not self.validation_result.is_valid and self.status != ResponseStatus.ERROR:
            raise ValueError("Invalid validation must have ERROR status")

        return self

    @classmethod
    def create_validation_success(
        cls, validation_result: ValidationResult
    ) -> "ValidationResponse":
        """Create successful validation response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            message="Validation completed successfully",
            validation_result=validation_result,
        )

    @classmethod
    def create_validation_error(
        cls, validation_result: ValidationResult, field_errors: Dict[str, List[str]]
    ) -> "ValidationResponse":
        """Create validation error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message="Validation failed",
            validation_result=validation_result,
            field_errors=field_errors,
        )


class AuthResponse(SecurityResponse[AuthResult]):
    """
    Authentication Response Model

    This model represents authentication responses with detailed
    authentication results and user information.

    Attributes:
        auth_result: Authentication result object
        user_info: Additional user information
        session_info: Session information
        token_info: Token information
    """

    auth_result: AuthResult = Field(..., description="Authentication result object")
    user_info: Dict[str, Any] = Field(
        default_factory=dict, description="Additional user information"
    )
    session_info: Dict[str, Any] = Field(
        default_factory=dict, description="Session information"
    )
    token_info: Dict[str, Any] = Field(
        default_factory=dict, description="Token information"
    )

    @field_validator("status")
    @classmethod
    def validate_auth_status(cls, v):
        """Validate authentication response status."""
        # This validation will be handled by model_validator
        return v

    @model_validator(mode="after")
    def validate_auth_response(self):
        """Validate authentication response consistency."""
        if self.auth_result.is_valid and self.status != ResponseStatus.SUCCESS:
            raise ValueError("Successful authentication must have SUCCESS status")

        if not self.auth_result.is_valid and self.status != ResponseStatus.ERROR:
            raise ValueError("Failed authentication must have ERROR status")

        return self

    @classmethod
    def create_auth_success(
        cls, auth_result: AuthResult, user_info: Optional[Dict[str, Any]] = None
    ) -> "AuthResponse":
        """Create successful authentication response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            message="Authentication successful",
            auth_result=auth_result,
            user_info=user_info or {},
        )

    @classmethod
    def create_auth_error(cls, auth_result: AuthResult) -> "AuthResponse":
        """Create authentication error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message=auth_result.error_message or "Authentication failed",
            auth_result=auth_result,
        )


class CertificateResponse(SecurityResponse[CertificateInfo]):
    """
    Certificate Response Model

    This model represents certificate-related responses with
    detailed certificate information and validation results.

    Attributes:
        certificate_info: Certificate information object
        validation_result: Certificate validation result
        chain_info: Certificate chain information
        expiry_info: Certificate expiry information
    """

    certificate_info: CertificateInfo = Field(
        ..., description="Certificate information object"
    )
    validation_result: Optional[ValidationResult] = Field(
        default=None, description="Certificate validation result"
    )
    chain_info: Dict[str, Any] = Field(
        default_factory=dict, description="Certificate chain information"
    )
    expiry_info: Dict[str, Any] = Field(
        default_factory=dict, description="Certificate expiry information"
    )

    @model_validator(mode="after")
    def validate_certificate_response(self):
        """Validate certificate response consistency."""
        if (
            self.validation_result
            and not self.validation_result.is_valid
            and self.status == ResponseStatus.SUCCESS
        ):
            raise ValueError(
                "Invalid certificate validation cannot have SUCCESS status"
            )

        return self

    @classmethod
    def create_certificate_success(
        cls,
        certificate_info: CertificateInfo,
        validation_result: Optional[ValidationResult] = None,
    ) -> "CertificateResponse":
        """Create successful certificate response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            message="Certificate information retrieved successfully",
            certificate_info=certificate_info,
            validation_result=validation_result,
        )


class PermissionResponse(SecurityResponse[Dict[str, Any]]):
    """
    Permission Response Model

    This model represents permission-related responses with
    user roles, permissions, and access control information.

    Attributes:
        user_roles: List of user roles
        user_permissions: Set of user permissions
        effective_permissions: Effective permissions after inheritance
        access_granted: Whether access is granted
        required_permissions: Required permissions for the operation
        missing_permissions: Missing permissions
    """

    user_roles: List[str] = Field(
        default_factory=list, description="List of user roles"
    )
    user_permissions: set = Field(
        default_factory=set, description="Set of user permissions"
    )
    effective_permissions: set = Field(
        default_factory=set, description="Effective permissions after inheritance"
    )
    access_granted: bool = Field(..., description="Whether access is granted")
    required_permissions: List[str] = Field(
        default_factory=list, description="Required permissions for the operation"
    )
    missing_permissions: List[str] = Field(
        default_factory=list, description="Missing permissions"
    )

    @model_validator(mode="after")
    def validate_permission_response(self):
        """Validate permission response consistency."""
        if self.access_granted and self.status != ResponseStatus.SUCCESS:
            raise ValueError("Granted access must have SUCCESS status")

        if not self.access_granted and self.status != ResponseStatus.ERROR:
            raise ValueError("Denied access must have ERROR status")

        return self

    @classmethod
    def create_permission_granted(
        cls,
        user_roles: List[str],
        user_permissions: set,
        required_permissions: List[str],
    ) -> "PermissionResponse":
        """Create permission granted response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            message="Access granted",
            user_roles=user_roles,
            user_permissions=user_permissions,
            effective_permissions=user_permissions,
            access_granted=True,
            required_permissions=required_permissions,
            missing_permissions=[],
        )

    @classmethod
    def create_permission_denied(
        cls,
        user_roles: List[str],
        user_permissions: set,
        required_permissions: List[str],
    ) -> "PermissionResponse":
        """Create permission denied response."""
        missing_permissions = [
            perm for perm in required_permissions if perm not in user_permissions
        ]
        return cls(
            status=ResponseStatus.ERROR,
            message="Access denied - insufficient permissions",
            user_roles=user_roles,
            user_permissions=user_permissions,
            effective_permissions=user_permissions,
            access_granted=False,
            required_permissions=required_permissions,
            missing_permissions=missing_permissions,
        )


class RateLimitResponse(SecurityResponse[RateLimitStatus]):
    """
    Rate Limit Response Model

    This model represents rate limiting responses with current
    rate limit status and usage information.

    Attributes:
        rate_limit_status: Rate limit status object
        usage_percentage: Current usage percentage
        reset_time: Time when rate limit resets
        retry_after: Retry after time in seconds
    """

    rate_limit_status: RateLimitStatus = Field(
        ..., description="Rate limit status object"
    )
    usage_percentage: float = Field(..., ge=0.0, description="Current usage percentage")
    reset_time: datetime = Field(..., description="Time when rate limit resets")
    retry_after: Optional[int] = Field(
        default=None, ge=0, description="Retry after time in seconds"
    )

    @model_validator(mode="after")
    def validate_rate_limit_response(self):
        """Validate rate limit response consistency."""
        is_exceeded = self.rate_limit_status.is_exceeded

        if is_exceeded and self.status != ResponseStatus.ERROR:
            raise ValueError("Exceeded rate limit must have ERROR status")

        if not is_exceeded and self.status != ResponseStatus.SUCCESS:
            raise ValueError("Within rate limit must have SUCCESS status")

        return self

    @classmethod
    def create_rate_limit_status(
        cls, rate_limit_status: RateLimitStatus
    ) -> "RateLimitResponse":
        """Create rate limit status response."""
        is_exceeded = rate_limit_status.is_exceeded
        return cls(
            status=ResponseStatus.ERROR if is_exceeded else ResponseStatus.SUCCESS,
            message="Rate limit exceeded" if is_exceeded else "Rate limit status",
            rate_limit_status=rate_limit_status,
            usage_percentage=rate_limit_status.utilization_percentage,
            reset_time=rate_limit_status.reset_time,
            retry_after=rate_limit_status.seconds_until_reset if is_exceeded else None,
        )


__all__ = [
    "ResponseStatus",
    "SecurityStatus",
    "ErrorCode",
    "SecurityResponse",
    "ErrorResponse",
    "SuccessResponse",
    "ValidationResponse",
    "AuthResponse",
    "CertificateResponse",
    "PermissionResponse",
    "RateLimitResponse",
]
