"""
Configuration Models Module

This module provides comprehensive configuration models for all components
of the MCP Security Framework. It includes Pydantic models for validation
and type safety across the entire framework.

Key Features:
    - Type-safe configuration validation
    - Default values for common use cases
    - Comprehensive field validation
    - Nested configuration support
    - Environment variable support

Classes:
    SecurityConfig: Main security configuration
    SSLConfig: SSL/TLS configuration
    AuthConfig: Authentication configuration
    CertificateConfig: Certificate management configuration
    PermissionConfig: Role and permission configuration
    RateLimitConfig: Rate limiting configuration
    LoggingConfig: Logging configuration
    CAConfig: Certificate Authority configuration
    ClientCertConfig: Client certificate configuration
    ServerCertConfig: Server certificate configuration
    IntermediateCAConfig: Intermediate CA configuration

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import SecretStr


class TLSVersion(str, Enum):
    """TLS version enumeration."""

    TLS_1_0 = "TLSv1.0"
    TLS_1_1 = "TLSv1.1"
    TLS_1_2 = "TLSv1.2"
    TLS_1_3 = "TLSv1.3"


class AuthMethod(str, Enum):
    """Authentication method enumeration."""

    API_KEY = "api_key"
    JWT = "jwt"
    CERTIFICATE = "certificate"
    BASIC = "basic"
    OAUTH2 = "oauth2"


class LogLevel(str, Enum):
    """Logging level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SSLConfig(BaseModel):
    """
    SSL/TLS Configuration Model

    This model defines SSL/TLS configuration settings for secure
    communication including certificate paths, TLS versions, and
    verification settings.

    Attributes:
        enabled: Whether SSL/TLS is enabled
        cert_file: Path to server certificate file
        key_file: Path to server private key file
        ca_cert_file: Path to CA certificate file
        verify_mode: SSL verification mode
        min_tls_version: Minimum TLS version to support
        max_tls_version: Maximum TLS version to support
        cipher_suite: Custom cipher suite configuration
        check_hostname: Whether to check hostname in certificates
        check_expiry: Whether to check certificate expiry
        expiry_warning_days: Days before expiry to warn
    """

    enabled: bool = Field(default=False, description="Whether SSL/TLS is enabled")
    cert_file: Optional[str] = Field(
        default=None, description="Path to server certificate file"
    )
    key_file: Optional[str] = Field(
        default=None, description="Path to server private key file"
    )
    ca_cert_file: Optional[str] = Field(
        default=None, description="Path to CA certificate file"
    )
    client_cert_file: Optional[str] = Field(
        default=None, description="Path to client certificate file"
    )
    client_key_file: Optional[str] = Field(
        default=None, description="Path to client private key file"
    )
    verify_mode: str = Field(
        default="CERT_REQUIRED", description="SSL verification mode"
    )
    min_tls_version: TLSVersion = Field(
        default=TLSVersion.TLS_1_2, description="Minimum TLS version"
    )
    max_tls_version: Optional[TLSVersion] = Field(
        default=None, description="Maximum TLS version"
    )
    cipher_suite: Optional[str] = Field(
        default=None, description="Custom cipher suite configuration"
    )
    check_hostname: bool = Field(
        default=True, description="Whether to check hostname in certificates"
    )
    check_expiry: bool = Field(
        default=True, description="Whether to check certificate expiry"
    )
    expiry_warning_days: int = Field(
        default=30, ge=1, le=365, description="Days before expiry to warn"
    )

    @field_validator(
        "cert_file", "key_file", "ca_cert_file", "client_cert_file", "client_key_file"
    )
    @classmethod
    def validate_file_paths(cls, v):
        """Validate that file paths exist when SSL is enabled."""
        if v is not None and not Path(v).exists():
            raise ValueError(f"File does not exist: {v}")
        return v

    @field_validator("verify_mode")
    @classmethod
    def validate_verify_mode(cls, v):
        """Validate SSL verification mode."""
        valid_modes = ["CERT_NONE", "CERT_OPTIONAL", "CERT_REQUIRED"]
        if v not in valid_modes:
            raise ValueError(f"Invalid verify_mode. Must be one of: {valid_modes}")
        return v

    @model_validator(mode="after")
    def validate_ssl_configuration(self):
        """Validate SSL configuration consistency."""
        if self.enabled:
            if not self.cert_file or not self.key_file:
                raise ValueError(
                    "SSL enabled but certificate and key files are required"
                )
        return self


class AuthConfig(BaseModel):
    """
    Authentication Configuration Model

    This model defines authentication configuration settings including
    API keys, JWT settings, and certificate-based authentication.

    Attributes:
        enabled: Whether authentication is enabled
        methods: List of enabled authentication methods
        api_keys: Dictionary of API keys and associated users/roles
        jwt_secret: JWT secret key for token signing
        jwt_algorithm: JWT signing algorithm
        jwt_expiry_hours: JWT token expiry time in hours
        certificate_auth: Whether certificate-based auth is enabled
        certificate_roles_oid: OID for extracting roles from certificates
        certificate_permissions_oid: OID for extracting permissions from certificates
        basic_auth: Whether basic authentication is enabled
        oauth2_config: OAuth2 configuration settings
    """

    enabled: bool = Field(default=True, description="Whether authentication is enabled")
    methods: List[AuthMethod] = Field(
        default=[AuthMethod.API_KEY], description="Enabled auth methods"
    )
    api_keys: Dict[str, Union[str, Dict[str, Any]]] = Field(
        default_factory=dict, description="API keys and associated users/roles"
    )
    user_roles: Dict[str, List[str]] = Field(
        default_factory=dict, description="User roles mapping"
    )
    jwt_secret: Optional[SecretStr] = Field(default=None, description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_expiry_hours: int = Field(
        default=24, ge=1, le=8760, description="JWT token expiry time in hours"
    )
    certificate_auth: bool = Field(
        default=False, description="Whether certificate-based auth is enabled"
    )
    certificate_roles_oid: str = Field(
        default="1.3.6.1.4.1.99999.1.1", description="OID for extracting roles"
    )
    certificate_permissions_oid: str = Field(
        default="1.3.6.1.4.1.99999.1.2", description="OID for extracting permissions"
    )
    basic_auth: bool = Field(
        default=False, description="Whether basic authentication is enabled"
    )
    oauth2_config: Optional[Dict[str, Any]] = Field(
        default=None, description="OAuth2 configuration"
    )
    public_paths: List[str] = Field(
        default_factory=list,
        description="List of public paths that bypass authentication",
    )
    security_headers: Optional[Dict[str, str]] = Field(
        default=None, description="Custom security headers to add to responses"
    )

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, v):
        """Validate JWT algorithm."""
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in valid_algorithms:
            raise ValueError(
                f"Invalid JWT algorithm. Must be one of: {valid_algorithms}"
            )
        return v

    @model_validator(mode="after")
    def validate_auth_configuration(self):
        """Validate authentication configuration consistency."""
        if self.enabled and not self.methods:
            raise ValueError("Authentication enabled but no methods specified")

        if AuthMethod.JWT in self.methods and not self.jwt_secret:
            raise ValueError("JWT authentication enabled but no JWT secret provided")

        return self


class CertificateConfig(BaseModel):
    """
    Certificate Management Configuration Model

    This model defines certificate management configuration settings
    including CA settings, certificate storage, and validation options.

    Attributes:
        enabled: Whether certificate management is enabled
        ca_cert_path: Path to CA certificate
        ca_key_path: Path to CA private key
        cert_storage_path: Path for certificate storage
        key_storage_path: Path for private key storage
        default_validity_days: Default certificate validity in days
        key_size: RSA key size for generated certificates
        hash_algorithm: Hash algorithm for certificate signing
        crl_enabled: Whether CRL is enabled
        crl_path: Path for CRL storage
        crl_validity_days: CRL validity period in days
        auto_renewal: Whether automatic certificate renewal is enabled
        renewal_threshold_days: Days before expiry to renew
    """

    enabled: bool = Field(
        default=False, description="Whether certificate management is enabled"
    )
    ca_cert_path: Optional[str] = Field(
        default=None, description="Path to CA certificate"
    )
    ca_key_path: Optional[str] = Field(
        default=None, description="Path to CA private key"
    )
    cert_storage_path: str = Field(
        default="./certs", description="Path for certificate storage"
    )
    key_storage_path: str = Field(
        default="./keys", description="Path for private key storage"
    )
    default_validity_days: int = Field(
        default=365, ge=1, le=3650, description="Default certificate validity in days"
    )
    key_size: int = Field(
        default=2048,
        ge=1024,
        le=4096,
        description="RSA key size for generated certificates",
    )
    hash_algorithm: str = Field(
        default="sha256", description="Hash algorithm for certificate signing"
    )
    crl_enabled: bool = Field(default=False, description="Whether CRL is enabled")
    crl_path: Optional[str] = Field(default=None, description="Path for CRL storage")
    crl_validity_days: int = Field(
        default=30, ge=1, le=365, description="CRL validity period in days"
    )
    auto_renewal: bool = Field(
        default=False, description="Whether automatic certificate renewal is enabled"
    )
    renewal_threshold_days: int = Field(
        default=30, ge=1, le=90, description="Days before expiry to renew"
    )

    @field_validator("hash_algorithm")
    @classmethod
    def validate_hash_algorithm(cls, v):
        """Validate hash algorithm."""
        valid_algorithms = ["sha1", "sha256", "sha384", "sha512"]
        if v not in valid_algorithms:
            raise ValueError(
                f"Invalid hash algorithm. Must be one of: {valid_algorithms}"
            )
        return v

    @model_validator(mode="after")
    def validate_certificate_configuration(self):
        """Validate certificate configuration consistency."""
        if self.enabled:
            if not self.ca_cert_path or not self.ca_key_path:
                raise ValueError(
                    "Certificate management enabled but CA certificate and key paths are required"
                )

        if self.crl_enabled and not self.crl_path:
            raise ValueError("CRL enabled but CRL path is required")

        return self


class PermissionConfig(BaseModel):
    """
    Permission and Role Configuration Model

    This model defines role and permission configuration settings
    including role definitions, permission mappings, and hierarchy.

    Attributes:
        enabled: Whether permission management is enabled
        roles_file: Path to roles configuration file
        default_role: Default role for unauthenticated users
        admin_role: Administrator role name
        role_hierarchy: Role hierarchy configuration
        permission_cache_enabled: Whether permission caching is enabled
        permission_cache_ttl: Permission cache TTL in seconds
        wildcard_permissions: Whether wildcard permissions are enabled
        strict_mode: Whether strict permission checking is enabled
    """

    enabled: bool = Field(
        default=True, description="Whether permission management is enabled"
    )
    roles_file: Optional[str] = Field(
        default=None, description="Path to roles configuration file"
    )
    default_role: str = Field(
        default="guest", description="Default role for unauthenticated users"
    )
    admin_role: str = Field(default="admin", description="Administrator role name")
    role_hierarchy: Dict[str, List[str]] = Field(
        default_factory=dict, description="Role hierarchy configuration"
    )
    permission_cache_enabled: bool = Field(
        default=True, description="Whether permission caching is enabled"
    )
    permission_cache_ttl: int = Field(
        default=300, ge=1, le=3600, description="Permission cache TTL in seconds"
    )
    wildcard_permissions: bool = Field(
        default=False, description="Whether wildcard permissions are enabled"
    )
    strict_mode: bool = Field(
        default=True, description="Whether strict permission checking is enabled"
    )
    roles: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Role definitions and their permissions"
    )

    @field_validator("roles_file")
    @classmethod
    def validate_roles_file(cls, v):
        """Validate roles file path."""
        if v is not None and not Path(v).exists():
            raise ValueError(f"Roles file does not exist: {v}")
        return v


class RateLimitConfig(BaseModel):
    """
    Rate Limiting Configuration Model

    This model defines rate limiting configuration settings including
    limits, windows, and storage backends.

    Attributes:
        enabled: Whether rate limiting is enabled
        default_requests_per_minute: Default requests per minute limit
        default_requests_per_hour: Default requests per hour limit
        burst_limit: Burst limit multiplier
        window_size_seconds: Rate limiting window size in seconds
        storage_backend: Rate limiting storage backend
        redis_config: Redis configuration for rate limiting
        cleanup_interval: Cleanup interval for expired entries
        exempt_paths: Paths exempt from rate limiting
        exempt_roles: Roles exempt from rate limiting
    """

    enabled: bool = Field(default=True, description="Whether rate limiting is enabled")
    default_requests_per_minute: int = Field(
        default=60, ge=1, le=10000, description="Default requests per minute limit"
    )
    default_requests_per_hour: int = Field(
        default=1000, ge=1, le=100000, description="Default requests per hour limit"
    )
    burst_limit: int = Field(
        default=2, ge=1, le=10, description="Burst limit multiplier"
    )
    window_size_seconds: int = Field(
        default=60, ge=1, le=3600, description="Rate limiting window size in seconds"
    )
    storage_backend: str = Field(
        default="memory", description="Rate limiting storage backend"
    )
    redis_config: Optional[Dict[str, Any]] = Field(
        default=None, description="Redis configuration for rate limiting"
    )
    cleanup_interval: int = Field(
        default=300, ge=1, le=3600, description="Cleanup interval for expired entries"
    )
    exempt_paths: List[str] = Field(
        default_factory=list, description="Paths exempt from rate limiting"
    )
    exempt_roles: List[str] = Field(
        default_factory=list, description="Roles exempt from rate limiting"
    )

    @field_validator("storage_backend")
    @classmethod
    def validate_storage_backend(cls, v):
        """Validate storage backend."""
        valid_backends = ["memory", "redis", "database"]
        if v not in valid_backends:
            raise ValueError(
                f"Invalid storage backend. Must be one of: {valid_backends}"
            )
        return v


class LoggingConfig(BaseModel):
    """
    Logging Configuration Model

    This model defines logging configuration settings including
    log levels, formats, and output destinations.

    Attributes:
        enabled: Whether logging is enabled
        level: Logging level
        format: Log message format
        date_format: Date format for log messages
        file_path: Path to log file
        max_file_size: Maximum log file size in MB
        backup_count: Number of backup log files
        console_output: Whether to output to console
        json_format: Whether to use JSON format
        include_timestamp: Whether to include timestamps
        include_level: Whether to include log level
        include_module: Whether to include module name
    """

    enabled: bool = Field(default=True, description="Whether logging is enabled")
    level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S", description="Date format for log messages"
    )
    file_path: Optional[str] = Field(default=None, description="Path to log file")
    max_file_size: int = Field(
        default=10, ge=1, le=1000, description="Maximum log file size in MB"
    )
    backup_count: int = Field(
        default=5, ge=0, le=100, description="Number of backup log files"
    )
    console_output: bool = Field(
        default=True, description="Whether to output to console"
    )
    json_format: bool = Field(default=False, description="Whether to use JSON format")
    include_timestamp: bool = Field(
        default=True, description="Whether to include timestamps"
    )
    include_level: bool = Field(
        default=True, description="Whether to include log level"
    )
    include_module: bool = Field(
        default=True, description="Whether to include module name"
    )


class SecurityConfig(BaseModel):
    """
    Main Security Configuration Model

    This is the main configuration model that combines all security
    component configurations into a single, comprehensive configuration.

    Attributes:
        ssl: SSL/TLS configuration
        auth: Authentication configuration
        certificates: Certificate management configuration
        permissions: Permission and role configuration
        rate_limit: Rate limiting configuration
        logging: Logging configuration
        debug: Whether debug mode is enabled
        environment: Environment name (dev, staging, prod)
        version: Configuration version
    """

    ssl: SSLConfig = Field(
        default_factory=SSLConfig, description="SSL/TLS configuration"
    )
    auth: AuthConfig = Field(
        default_factory=AuthConfig, description="Authentication configuration"
    )
    certificates: CertificateConfig = Field(
        default_factory=CertificateConfig,
        description="Certificate management configuration",
    )
    permissions: PermissionConfig = Field(
        default_factory=PermissionConfig,
        description="Permission and role configuration",
    )
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig, description="Rate limiting configuration"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig, description="Logging configuration"
    )
    debug: bool = Field(default=False, description="Whether debug mode is enabled")
    environment: str = Field(default="dev", description="Environment name")
    version: str = Field(default="1.0.0", description="Configuration version")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment name."""
        valid_environments = [
            "dev",
            "development",
            "staging",
            "prod",
            "production",
            "test",
        ]
        if v not in valid_environments:
            raise ValueError(
                f"Invalid environment. Must be one of: {valid_environments}"
            )
        return v


# Certificate-specific configuration models
class CAConfig(BaseModel):
    """
    Certificate Authority Configuration Model

    This model defines configuration for creating and managing
    Certificate Authority (CA) certificates.

    Attributes:
        common_name: CA common name
        organization: Organization name
        organizational_unit: Organizational unit
        country: Country code
        state: State or province
        locality: City or locality
        email: Contact email
        validity_years: CA certificate validity in years
        key_size: RSA key size
        hash_algorithm: Hash algorithm for signing
    """

    common_name: str = Field(..., description="CA common name")
    organization: str = Field(..., description="Organization name")
    organizational_unit: Optional[str] = Field(
        default=None, description="Organizational unit"
    )
    country: str = Field(
        default="US", min_length=2, max_length=2, description="Country code"
    )
    state: Optional[str] = Field(default=None, description="State or province")
    locality: Optional[str] = Field(default=None, description="City or locality")
    email: Optional[str] = Field(default=None, description="Contact email")
    validity_years: int = Field(
        default=10, ge=1, le=50, description="CA certificate validity in years"
    )
    key_size: int = Field(default=4096, ge=2048, le=8192, description="RSA key size")
    hash_algorithm: str = Field(
        default="sha256", description="Hash algorithm for signing"
    )


class IntermediateCAConfig(CAConfig):
    """
    Intermediate Certificate Authority Configuration Model

    This model extends CAConfig for intermediate CA certificates
    with additional settings specific to intermediate CAs.

    Attributes:
        parent_ca_cert: Path to parent CA certificate
        parent_ca_key: Path to parent CA private key
        path_length: Maximum path length constraint
    """

    parent_ca_cert: str = Field(..., description="Path to parent CA certificate")
    parent_ca_key: str = Field(..., description="Path to parent CA private key")
    path_length: int = Field(
        default=0, ge=0, le=10, description="Maximum path length constraint"
    )


class ClientCertConfig(BaseModel):
    """
    Client Certificate Configuration Model

    This model defines configuration for creating client certificates
    including subject information and certificate extensions.

    Attributes:
        common_name: Client certificate common name
        organization: Organization name
        organizational_unit: Organizational unit
        country: Country code
        state: State or province
        locality: City or locality
        email: Contact email
        validity_days: Certificate validity in days
        key_size: RSA key size
        roles: List of roles to include in certificate
        permissions: List of permissions to include in certificate
        ca_cert_path: Path to signing CA certificate
        ca_key_path: Path to signing CA private key
    """

    common_name: str = Field(..., description="Client certificate common name")
    organization: str = Field(..., description="Organization name")
    organizational_unit: Optional[str] = Field(
        default=None, description="Organizational unit"
    )
    country: str = Field(
        default="US", min_length=2, max_length=2, description="Country code"
    )
    state: Optional[str] = Field(default=None, description="State or province")
    locality: Optional[str] = Field(default=None, description="City or locality")
    email: Optional[str] = Field(default=None, description="Contact email")
    validity_days: int = Field(
        default=365, ge=1, le=3650, description="Certificate validity in days"
    )
    key_size: int = Field(default=2048, ge=1024, le=4096, description="RSA key size")
    roles: List[str] = Field(
        default_factory=list, description="List of roles to include in certificate"
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="List of permissions to include in certificate",
    )
    ca_cert_path: str = Field(..., description="Path to signing CA certificate")
    ca_key_path: str = Field(..., description="Path to signing CA private key")


class ServerCertConfig(ClientCertConfig):
    """
    Server Certificate Configuration Model

    This model extends ClientCertConfig for server certificates
    with additional settings specific to server certificates.

    Attributes:
        subject_alt_names: List of subject alternative names
        key_usage: Key usage extensions
        extended_key_usage: Extended key usage extensions
    """

    subject_alt_names: List[str] = Field(
        default_factory=list, description="List of subject alternative names"
    )
    key_usage: List[str] = Field(
        default=["digitalSignature", "keyEncipherment"],
        description="Key usage extensions",
    )
    extended_key_usage: List[str] = Field(
        default=["serverAuth"], description="Extended key usage extensions"
    )
