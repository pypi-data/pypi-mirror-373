"""
Data Models Module

This module provides comprehensive data models for all core data structures
used throughout the MCP Security Framework. It includes models for
authentication results, validation results, certificate information,
and other essential data types.

Key Features:
    - Type-safe data models with validation
    - Comprehensive field documentation
    - Default values for common use cases
    - Serialization and deserialization support
    - Type aliases for better code readability

Classes:
    AuthResult: Authentication result model
    ValidationResult: Validation result model
    CertificateInfo: Certificate information model
    CertificatePair: Certificate and key pair model
    RateLimitStatus: Rate limiting status model
    UserCredentials: User credentials model
    RolePermissions: Role permissions mapping model
    CertificateChain: Certificate chain model

Type Aliases:
    ApiKey: Type alias for API key strings
    Username: Type alias for username strings
    RoleName: Type alias for role name strings
    PermissionName: Type alias for permission name strings
    CertificatePath: Type alias for certificate file paths

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, TypeAlias

from pydantic import BaseModel, Field, field_validator, model_validator

# Type aliases for better code readability
ApiKey: TypeAlias = str
Username: TypeAlias = str
RoleName: TypeAlias = str
PermissionName: TypeAlias = str
CertificatePath: TypeAlias = str


class AuthStatus(str, Enum):
    """Authentication status enumeration."""

    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"
    UNAUTHORIZED = "unauthorized"


class ValidationStatus(str, Enum):
    """Validation status enumeration."""

    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNTRUSTED = "untrusted"


class CertificateType(str, Enum):
    """Certificate type enumeration."""

    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"
    SERVER = "server"
    CLIENT = "client"
    CODE_SIGNING = "code_signing"
    EMAIL = "email"


class AuthMethod(str, Enum):
    """Authentication method enumeration."""

    API_KEY = "api_key"
    JWT = "jwt"
    CERTIFICATE = "certificate"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    UNKNOWN = "unknown"


class AuthResult(BaseModel):
    """
    Authentication Result Model

    This model represents the result of an authentication attempt,
    including success status, user information, and authentication
    metadata.

    Attributes:
        is_valid: Whether authentication was successful
        status: Authentication status (success, failed, expired, etc.)
        username: Authenticated username if successful
        user_id: Unique user identifier
        roles: List of user roles
        permissions: Set of user permissions
        auth_method: Method used for authentication
        auth_timestamp: When authentication occurred
        token_expiry: When authentication token expires
        error_code: Error code if authentication failed
        error_message: Human-readable error message
        metadata: Additional authentication metadata
    """

    is_valid: bool = Field(..., description="Whether authentication was successful")
    status: AuthStatus = Field(..., description="Authentication status")
    username: Optional[str] = Field(default=None, description="Authenticated username")
    user_id: Optional[str] = Field(default=None, description="Unique user identifier")
    roles: List[str] = Field(default_factory=list, description="List of user roles")
    permissions: Set[str] = Field(
        default_factory=set, description="Set of user permissions"
    )
    auth_method: Optional[AuthMethod] = Field(
        default=None, description="Method used for authentication"
    )
    auth_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When authentication occurred"
    )
    token_expiry: Optional[datetime] = Field(
        default=None, description="When authentication token expires"
    )
    error_code: Optional[int] = Field(
        default=None, description="Error code if authentication failed"
    )
    error_message: Optional[str] = Field(
        default=None, description="Human-readable error message"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional authentication metadata"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Username cannot be empty")
        return v

    @model_validator(mode="after")
    def validate_auth_result(self):
        """Validate authentication result consistency."""
        if self.is_valid and self.status != AuthStatus.SUCCESS:
            raise ValueError("Valid authentication must have SUCCESS status")

        if not self.is_valid and self.status == AuthStatus.SUCCESS:
            raise ValueError("Invalid authentication cannot have SUCCESS status")

        if self.error_code is not None and self.is_valid:
            raise ValueError("Valid authentication cannot have error code")

        if self.error_message is not None and self.is_valid:
            raise ValueError("Valid authentication cannot have error message")

        return self

    @property
    def is_expired(self) -> bool:
        """Check if authentication token is expired."""
        if self.token_expiry is None:
            return False
        return datetime.now(timezone.utc) > self.token_expiry

    @property
    def expires_soon(self) -> bool:
        """Check if authentication token expires soon (within 1 hour)."""
        if self.token_expiry is None:
            return False
        return datetime.now(timezone.utc) + timedelta(hours=1) > self.token_expiry


class ValidationResult(BaseModel):
    """
    Validation Result Model

    This model represents the result of a validation operation,
    such as certificate validation, permission validation, or
    input data validation.

    Attributes:
        is_valid: Whether validation was successful
        status: Validation status (valid, invalid, expired, etc.)
        field_name: Name of the field being validated
        value: Value that was validated
        error_code: Error code if validation failed
        error_message: Human-readable error message
        warnings: List of validation warnings
        metadata: Additional validation metadata
    """

    is_valid: bool = Field(..., description="Whether validation was successful")
    status: ValidationStatus = Field(..., description="Validation status")
    field_name: Optional[str] = Field(
        default=None, description="Name of the field being validated"
    )
    value: Optional[Any] = Field(default=None, description="Value that was validated")
    error_code: Optional[int] = Field(
        default=None, description="Error code if validation failed"
    )
    error_message: Optional[str] = Field(
        default=None, description="Human-readable error message"
    )
    warnings: List[str] = Field(
        default_factory=list, description="List of validation warnings"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional validation metadata"
    )
    granted_permissions: List[str] = Field(
        default_factory=list, description="List of granted permissions"
    )
    denied_permissions: List[str] = Field(
        default_factory=list, description="List of denied permissions"
    )

    @model_validator(mode="after")
    def validate_validation_result(self):
        """Validate validation result consistency."""
        if self.is_valid and self.status != ValidationStatus.VALID:
            raise ValueError("Valid validation must have VALID status")

        if not self.is_valid and self.status == ValidationStatus.VALID:
            raise ValueError("Invalid validation cannot have VALID status")

        if self.error_code is not None and self.is_valid:
            raise ValueError("Valid validation cannot have error code")

        if self.error_message is not None and self.is_valid:
            raise ValueError("Valid validation cannot have error message")

        return self


class CertificateInfo(BaseModel):
    """
    Certificate Information Model

    This model represents detailed information about a certificate,
    including subject, issuer, validity dates, and extensions.

    Attributes:
        subject: Certificate subject (CN, O, OU, etc.)
        issuer: Certificate issuer information
        serial_number: Certificate serial number
        not_before: Certificate validity start date
        not_after: Certificate validity end date
        certificate_type: Type of certificate
        key_size: RSA key size in bits
        signature_algorithm: Signature algorithm used
        subject_alt_names: List of subject alternative names
        key_usage: Key usage extensions
        extended_key_usage: Extended key usage extensions
        is_ca: Whether certificate is a CA certificate
        path_length: Maximum path length constraint
        roles: Roles extracted from certificate
        permissions: Permissions extracted from certificate
        certificate_path: Path to certificate file
        fingerprint_sha1: SHA1 fingerprint
        fingerprint_sha256: SHA256 fingerprint
    """

    subject: Dict[str, str] = Field(..., description="Certificate subject information")
    issuer: Dict[str, str] = Field(..., description="Certificate issuer information")
    serial_number: str = Field(..., description="Certificate serial number")
    not_before: datetime = Field(..., description="Certificate validity start date")
    not_after: datetime = Field(..., description="Certificate validity end date")
    certificate_type: CertificateType = Field(..., description="Type of certificate")
    key_size: int = Field(..., description="RSA key size in bits")
    signature_algorithm: str = Field(..., description="Signature algorithm used")
    subject_alt_names: List[str] = Field(
        default_factory=list, description="List of subject alternative names"
    )
    key_usage: List[str] = Field(
        default_factory=list, description="Key usage extensions"
    )
    extended_key_usage: List[str] = Field(
        default_factory=list, description="Extended key usage extensions"
    )
    is_ca: bool = Field(
        default=False, description="Whether certificate is a CA certificate"
    )
    path_length: Optional[int] = Field(
        default=None, description="Maximum path length constraint"
    )
    roles: List[str] = Field(
        default_factory=list, description="Roles extracted from certificate"
    )
    permissions: List[str] = Field(
        default_factory=list, description="Permissions extracted from certificate"
    )
    certificate_path: Optional[str] = Field(
        default=None, description="Path to certificate file"
    )
    fingerprint_sha1: Optional[str] = Field(
        default=None, description="SHA1 fingerprint"
    )
    fingerprint_sha256: Optional[str] = Field(
        default=None, description="SHA256 fingerprint"
    )

    @field_validator("key_size")
    @classmethod
    def validate_key_size(cls, v):
        """Validate key size."""
        if v < 512 or v > 8192:
            raise ValueError("Key size must be between 512 and 8192 bits")
        return v

    @property
    def is_expired(self) -> bool:
        """Check if certificate is expired."""
        now = datetime.now(timezone.utc)
        # Ensure not_after has timezone info
        not_after = (
            self.not_after.replace(tzinfo=timezone.utc)
            if self.not_after.tzinfo is None
            else self.not_after
        )
        return now > not_after

    @property
    def expires_soon(self) -> bool:
        """Check if certificate expires soon (within 30 days)."""
        now = datetime.now(timezone.utc)
        # Ensure not_after has timezone info
        not_after = (
            self.not_after.replace(tzinfo=timezone.utc)
            if self.not_after.tzinfo is None
            else self.not_after
        )
        return now + timedelta(days=30) > not_after

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until certificate expiry."""
        if self.is_expired:
            return 0
        now = datetime.now(timezone.utc)
        # Ensure not_after has timezone info
        not_after = (
            self.not_after.replace(tzinfo=timezone.utc)
            if self.not_after.tzinfo is None
            else self.not_after
        )
        delta = not_after - now
        return delta.days

    @property
    def common_name(self) -> Optional[str]:
        """Get certificate common name."""
        return self.subject.get("CN")

    @property
    def organization(self) -> Optional[str]:
        """Get certificate organization."""
        return self.subject.get("O")

    @property
    def valid(self) -> bool:
        """Check if certificate is valid (not expired)."""
        return not self.is_expired

    @property
    def revoked(self) -> bool:
        """Check if certificate is revoked."""
        # This would typically check against a CRL or OCSP
        # For now, return False as default
        return False


class CertificatePair(BaseModel):
    """
    Certificate and Key Pair Model

    This model represents a certificate and its corresponding private key,
    including file paths and metadata.

    Attributes:
        certificate_path: Path to certificate file
        private_key_path: Path to private key file
        certificate_pem: Certificate content in PEM format
        private_key_pem: Private key content in PEM format
        serial_number: Certificate serial number
        common_name: Certificate common name
        organization: Certificate organization
        not_before: Certificate validity start date
        not_after: Certificate validity end date
        certificate_type: Type of certificate
        key_size: RSA key size in bits
        roles: Roles extracted from certificate
        permissions: Permissions extracted from certificate
        metadata: Additional certificate metadata
    """

    certificate_path: str = Field(..., description="Path to certificate file")
    private_key_path: str = Field(..., description="Path to private key file")
    certificate_pem: str = Field(..., description="Certificate content in PEM format")
    private_key_pem: str = Field(..., description="Private key content in PEM format")
    serial_number: str = Field(..., description="Certificate serial number")
    common_name: str = Field(..., description="Certificate common name")
    organization: str = Field(..., description="Certificate organization")
    not_before: datetime = Field(..., description="Certificate validity start date")
    not_after: datetime = Field(..., description="Certificate validity end date")
    certificate_type: CertificateType = Field(..., description="Type of certificate")
    key_size: int = Field(..., description="RSA key size in bits")
    roles: List[str] = Field(
        default_factory=list, description="Roles extracted from certificate"
    )
    permissions: List[str] = Field(
        default_factory=list, description="Permissions extracted from certificate"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional certificate metadata"
    )

    @field_validator("certificate_pem")
    @classmethod
    def validate_certificate_pem(cls, v):
        """Validate certificate PEM format."""
        if not v.startswith("-----BEGIN CERTIFICATE-----"):
            raise ValueError("Invalid certificate PEM format")
        if not v.strip().endswith("-----END CERTIFICATE-----"):
            raise ValueError("Invalid certificate PEM format")
        return v

    @field_validator("private_key_pem")
    @classmethod
    def validate_private_key_pem(cls, v):
        """Validate private key PEM format."""
        if not v.startswith("-----BEGIN PRIVATE KEY-----") and not v.startswith(
            "-----BEGIN RSA PRIVATE KEY-----"
        ):
            raise ValueError("Invalid private key PEM format")
        if not v.strip().endswith(
            "-----END PRIVATE KEY-----"
        ) and not v.strip().endswith("-----END RSA PRIVATE KEY-----"):
            raise ValueError("Invalid private key PEM format")
        return v

    @property
    def is_expired(self) -> bool:
        """Check if certificate is expired."""
        return datetime.now(timezone.utc) > self.not_after

    @property
    def expires_soon(self) -> bool:
        """Check if certificate expires soon (within 30 days)."""
        return datetime.now(timezone.utc) + timedelta(days=30) > self.not_after


class RateLimitStatus(BaseModel):
    """
    Rate Limiting Status Model

    This model represents the current status of rate limiting for
    a specific identifier (IP, user, etc.).

    Attributes:
        identifier: Rate limiting identifier (IP, user ID, etc.)
        current_count: Current request count in window
        limit: Maximum allowed requests in window
        window_start: Start time of current window
        window_end: End time of current window
        is_exceeded: Whether rate limit is exceeded
        remaining_requests: Number of remaining requests
        reset_time: Time when rate limit resets
        window_size_seconds: Size of rate limiting window
    """

    identifier: str = Field(..., description="Rate limiting identifier")
    current_count: int = Field(..., ge=0, description="Current request count in window")
    limit: int = Field(..., ge=1, description="Maximum allowed requests in window")
    window_start: datetime = Field(..., description="Start time of current window")
    window_end: datetime = Field(..., description="End time of current window")
    is_exceeded: bool = Field(..., description="Whether rate limit is exceeded")
    remaining_requests: int = Field(
        ..., ge=0, description="Number of remaining requests"
    )
    reset_time: datetime = Field(..., description="Time when rate limit resets")
    window_size_seconds: int = Field(
        ..., ge=1, description="Size of rate limiting window"
    )

    @model_validator(mode="after")
    def validate_rate_limit_status(self):
        """Validate rate limit status consistency."""
        if self.current_count > self.limit and not self.is_exceeded:
            raise ValueError("Rate limit exceeded but is_exceeded is False")

        if self.current_count <= self.limit and self.is_exceeded:
            raise ValueError("Rate limit not exceeded but is_exceeded is True")

        if self.remaining_requests < 0:
            raise ValueError("Remaining requests cannot be negative")

        if self.remaining_requests > self.limit:
            raise ValueError("Remaining requests cannot exceed limit")

        return self

    @property
    def seconds_until_reset(self) -> int:
        """Calculate seconds until rate limit resets."""
        delta = self.reset_time - datetime.now(timezone.utc)
        return max(0, int(delta.total_seconds()))

    @property
    def utilization_percentage(self) -> float:
        """Calculate rate limit utilization percentage."""
        if self.limit == 0:
            return 0.0
        return (self.current_count / self.limit) * 100.0


class UserCredentials(BaseModel):
    """
    User Credentials Model

    This model represents user credentials for authentication,
    supporting multiple authentication methods.

    Attributes:
        username: User username
        password: User password (hashed)
        api_key: User API key
        certificate_path: Path to user certificate
        roles: List of user roles
        permissions: Set of user permissions
        is_active: Whether user account is active
        created_at: When user account was created
        last_login: When user last logged in
        metadata: Additional user metadata
    """

    username: str = Field(..., description="User username")
    password: Optional[str] = Field(default=None, description="User password (hashed)")
    api_key: Optional[str] = Field(default=None, description="User API key")
    certificate_path: Optional[str] = Field(
        default=None, description="Path to user certificate"
    )
    roles: List[str] = Field(default_factory=list, description="List of user roles")
    permissions: Set[str] = Field(
        default_factory=set, description="Set of user permissions"
    )
    is_active: bool = Field(default=True, description="Whether user account is active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="When user account was created"
    )
    last_login: Optional[datetime] = Field(
        default=None, description="When user last logged in"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional user metadata"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format."""
        if len(v.strip()) == 0:
            raise ValueError("Username cannot be empty")
        if len(v) > 100:
            raise ValueError("Username too long (max 100 characters)")
        return v.strip()

    @property
    def has_password(self) -> bool:
        """Check if user has password set."""
        return self.password is not None and len(self.password) > 0

    @property
    def has_api_key(self) -> bool:
        """Check if user has API key set."""
        return self.api_key is not None and len(self.api_key) > 0

    @property
    def has_certificate(self) -> bool:
        """Check if user has certificate set."""
        return self.certificate_path is not None and len(self.certificate_path) > 0


class RolePermissions(BaseModel):
    """
    Role Permissions Mapping Model

    This model represents the mapping between roles and their
    associated permissions, including role hierarchy.

    Attributes:
        role_name: Name of the role
        permissions: Set of permissions for this role
        parent_roles: List of parent roles
        child_roles: List of child roles
        description: Role description
        is_active: Whether role is active
        created_at: When role was created
        metadata: Additional role metadata
    """

    role_name: str = Field(..., description="Name of the role")
    permissions: Set[str] = Field(
        default_factory=set, description="Set of permissions for this role"
    )
    parent_roles: List[str] = Field(
        default_factory=list, description="List of parent roles"
    )
    child_roles: List[str] = Field(
        default_factory=list, description="List of child roles"
    )
    description: Optional[str] = Field(default=None, description="Role description")
    is_active: bool = Field(default=True, description="Whether role is active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="When role was created"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional role metadata"
    )

    @field_validator("role_name")
    @classmethod
    def validate_role_name(cls, v):
        """Validate role name format."""
        if len(v.strip()) == 0:
            raise ValueError("Role name cannot be empty")
        if len(v) > 100:
            raise ValueError("Role name too long (max 100 characters)")
        return v.strip()

    @property
    def effective_permissions(self) -> Set[str]:
        """Get effective permissions including inherited permissions."""
        # This would be calculated by traversing the role hierarchy
        # For now, return direct permissions
        return self.permissions.copy()

    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission."""
        return permission in self.effective_permissions


class CertificateChain(BaseModel):
    """
    Certificate Chain Model

    This model represents a complete certificate chain from
    end-entity certificate to root CA certificate.

    Attributes:
        certificates: List of certificates in chain (end-entity first)
        chain_length: Number of certificates in chain
        is_valid: Whether certificate chain is valid
        validation_errors: List of validation errors
        root_ca: Root CA certificate information
        intermediate_cas: List of intermediate CA certificates
        end_entity: End-entity certificate information
        trust_path: Trust path information
    """

    certificates: List[CertificateInfo] = Field(
        ..., description="List of certificates in chain"
    )
    chain_length: int = Field(..., ge=1, description="Number of certificates in chain")
    is_valid: bool = Field(..., description="Whether certificate chain is valid")
    validation_errors: List[str] = Field(
        default_factory=list, description="List of validation errors"
    )
    root_ca: Optional[CertificateInfo] = Field(
        default=None, description="Root CA certificate information"
    )
    intermediate_cas: List[CertificateInfo] = Field(
        default_factory=list, description="List of intermediate CA certificates"
    )
    end_entity: Optional[CertificateInfo] = Field(
        default=None, description="End-entity certificate information"
    )
    trust_path: Dict[str, Any] = Field(
        default_factory=dict, description="Trust path information"
    )

    @field_validator("chain_length")
    @classmethod
    def validate_chain_length(cls, v, info):
        """Validate chain length matches certificates list."""
        certificates = info.data.get("certificates", [])
        if v != len(certificates):
            raise ValueError("Chain length must match number of certificates")
        return v

    @model_validator(mode="after")
    def validate_certificate_chain(self):
        """Validate certificate chain consistency."""
        if self.certificates and not self.end_entity:
            self.end_entity = self.certificates[0]

        if self.certificates and not self.root_ca:
            self.root_ca = self.certificates[-1]

        return self

    @property
    def has_intermediate_cas(self) -> bool:
        """Check if chain has intermediate CAs."""
        return len(self.certificates) > 2

    @property
    def is_self_signed(self) -> bool:
        """Check if end-entity certificate is self-signed."""
        if not self.end_entity or not self.root_ca:
            return False
        return self.end_entity.serial_number == self.root_ca.serial_number
