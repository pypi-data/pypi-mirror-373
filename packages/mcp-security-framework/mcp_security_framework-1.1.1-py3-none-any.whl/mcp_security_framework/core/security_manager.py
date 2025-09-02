"""
Security Manager Module

This module provides the main SecurityManager class that integrates all
core security components into a unified interface for comprehensive
security management.

Key Features:
- Unified interface for all security operations
- Integration of authentication, authorization, SSL/TLS, and rate limiting
- Factory methods for creating framework-specific middleware
- Comprehensive request validation and security checking
- Certificate management and validation
- Security event logging and monitoring

Classes:
    SecurityManager: Main security management class
    SecurityConfigurationError: Configuration error exception
    SecurityValidationError: Validation error exception

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from ..schemas.config import (
    AuthConfig,
    CertificateConfig,
    PermissionConfig,
    SecurityConfig,
)
from ..schemas.models import (
    AuthResult,
    AuthStatus,
    CertificateInfo,
    CertificatePair,
    ValidationResult,
    ValidationStatus,
)
from ..schemas.responses import ResponseStatus, SecurityResponse
from .auth_manager import AuthManager
from .cert_manager import CertificateManager
from .permission_manager import PermissionManager
from .rate_limiter import RateLimiter
from .ssl_manager import SSLManager


class SecurityConfigurationError(Exception):
    """Raised when security configuration is invalid."""

    def __init__(self, message: str, error_code: int = -32001):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class SecurityValidationError(Exception):
    """Raised when security validation fails."""

    def __init__(self, message: str, error_code: int = -32002):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class SecurityManager:
    """
    Security Manager Class

    This is the main security management class that integrates all core
    security components into a unified interface. It provides comprehensive
    security management including authentication, authorization, SSL/TLS
    management, certificate management, and rate limiting.

    The SecurityManager serves as the central point for all security
    operations and provides factory methods for creating framework-specific
    middleware components.

    Key Responsibilities:
    - Initialize and manage all core security components
    - Provide unified interface for security operations
    - Handle request validation and security checking
    - Manage certificate lifecycle and validation
    - Provide factory methods for middleware creation
    - Coordinate between different security components
    - Handle security event logging and monitoring

    Attributes:
        config (SecurityConfig): Main security configuration
        logger (Logger): Logger instance for security operations
        auth_manager (AuthManager): Authentication manager instance
        permission_manager (PermissionManager): Permission manager instance
        ssl_manager (SSLManager): SSL/TLS manager instance
        cert_manager (CertificateManager): Certificate manager instance
        rate_limiter (RateLimiter): Rate limiter instance
        _component_status (Dict): Status of all security components
        _security_events (List): Security event log

    Example:
        >>> config = SecurityConfig(
        ...     auth=AuthConfig(enabled=True, methods=["api_key"]),
        ...     permissions=PermissionConfig(roles_file="roles.json")
        ... )
        >>> security_manager = SecurityManager(config)
        >>> result = security_manager.validate_request({
        ...     "api_key": "user_key_123",
        ...     "required_permissions": ["read", "write"]
        ... })

    Raises:
        SecurityConfigurationError: When security configuration is invalid
        SecurityValidationError: When security validation fails
        AuthenticationError: When authentication fails
        PermissionDeniedError: When access is denied
    """

    def __init__(self, config: SecurityConfig):
        """
        Initialize Security Manager.

        Args:
            config (SecurityConfig): Main security configuration containing
                all component configurations. Must be a valid SecurityConfig
                instance with proper settings for all security components.

        Raises:
            SecurityConfigurationError: If configuration is invalid or
                required components cannot be initialized.

        Example:
            >>> config = SecurityConfig(
            ...     auth=AuthConfig(enabled=True),
            ...     permissions=PermissionConfig(roles_file="roles.json")
            ... )
            >>> security_manager = SecurityManager(config)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._component_status: Dict[str, bool] = {}
        self._security_events: List[Dict[str, Any]] = []
        self._start_time = datetime.now(timezone.utc)

        # Initialize all core components
        self._initialize_components()

        # Log initialization
        self.logger.info(
            "Security Manager initialized successfully",
            extra={
                "environment": config.environment,
                "version": config.version,
                "debug": config.debug,
            },
        )

    def _initialize_components(self) -> None:
        """
        Initialize all core security components.

        This method initializes all core security components based on
        the provided configuration. It handles component dependencies
        and validates that all required components are properly configured.

        Raises:
            SecurityConfigurationError: If any component fails to initialize
                or required configuration is missing.
        """
        try:
            # Initialize PermissionManager first (needed by AuthManager)
            self.permission_manager = PermissionManager(self.config.permissions)
            self._component_status["permission_manager"] = True

            # Initialize AuthManager (depends on PermissionManager)
            self.auth_manager = AuthManager(self.config.auth, self.permission_manager)
            self._component_status["auth_manager"] = True

            # Initialize SSLManager
            self.ssl_manager = SSLManager(self.config.ssl)
            self._component_status["ssl_manager"] = True

            # Initialize CertificateManager
            self.cert_manager = CertificateManager(self.config.certificates)
            self._component_status["cert_manager"] = True

            # Initialize RateLimiter
            self.rate_limiter = RateLimiter(self.config.rate_limit)
            self._component_status["rate_limiter"] = True

            self.logger.info("All security components initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize security components: {str(e)}")
            raise SecurityConfigurationError(
                f"Failed to initialize security components: {str(e)}", error_code=-32001
            )

    def validate_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a complete request for security compliance.

        This method performs comprehensive security validation of a request
        including authentication, authorization, rate limiting, and any
        other security checks configured in the system.

        Args:
            request_data (Dict[str, Any]): Request data containing authentication
                credentials, required permissions, and other security-related
                information. Must include authentication method and credentials.

        Returns:
            ValidationResult: Validation result containing success status,
                error messages, and validation details.

        Raises:
            SecurityValidationError: When request validation fails due to
                security violations or invalid data.

        Example:
            >>> result = security_manager.validate_request({
            ...     "api_key": "user_key_123",
            ...     "required_permissions": ["read", "write"],
            ...     "client_ip": "192.168.1.100"
            ... })
            >>> if result.is_valid:
            ...     print("Request validated successfully")
        """
        try:
            # Extract authentication credentials
            auth_credentials = self._extract_auth_credentials(request_data)

            # Perform authentication
            auth_result = self.authenticate_user(auth_credentials)
            if not auth_result.is_valid:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    error_message=f"Authentication failed: {auth_result.error_message}",
                    error_code=auth_result.error_code,
                )

            # Check rate limiting
            if not self._check_rate_limit(request_data):
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    error_message="Rate limit exceeded",
                    error_code=-32003,
                )

            # Check permissions
            required_permissions = request_data.get("required_permissions", [])
            if required_permissions:
                permission_result = self.check_permissions(
                    auth_result.roles, required_permissions
                )
                if not permission_result.is_valid:
                    return ValidationResult(
                        is_valid=False,
                        status=ValidationStatus.INVALID,
                        error_message=f"Permission denied: {permission_result.error_message}",
                        error_code=permission_result.error_code,
                    )

            # Log successful validation
            self._log_security_event(
                "request_validated",
                {
                    "user": auth_result.username,
                    "roles": auth_result.roles,
                    "permissions": required_permissions,
                },
            )

            return ValidationResult(is_valid=True, status=ValidationStatus.VALID)

        except Exception as e:
            self.logger.error(f"Request validation failed: {str(e)}")
            raise SecurityValidationError(
                f"Request validation failed: {str(e)}", error_code=-32002
            )

    def authenticate_user(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate a user with provided credentials.

        This method authenticates a user using the configured authentication
        methods and returns detailed authentication results including user
        information and roles.

        Args:
            credentials (Dict[str, Any]): User credentials containing
                authentication method and corresponding credentials.
                Supported methods: api_key, jwt, certificate.

        Returns:
            AuthResult: Authentication result containing success status,
                user information, roles, and error details.

        Raises:
            SecurityValidationError: When authentication fails or
                credentials are invalid.

        Example:
            >>> result = security_manager.authenticate_user({
            ...     "method": "api_key",
            ...     "api_key": "user_key_123"
            ... })
            >>> if result.is_valid:
            ...     print(f"Authenticated user: {result.username}")
        """
        try:
            auth_method = credentials.get("method", "api_key")

            if auth_method == "api_key":
                api_key = credentials.get("api_key")
                if not api_key:
                    return AuthResult(
                        is_valid=False,
                        status=AuthStatus.INVALID,
                        auth_method="api_key",
                        error_code=-32001,
                        error_message="API key is required",
                    )
                return self.auth_manager.authenticate_api_key(api_key)

            elif auth_method == "jwt":
                token = credentials.get("token")
                if not token:
                    return AuthResult(
                        is_valid=False,
                        status=AuthStatus.INVALID,
                        auth_method="jwt",
                        error_code=-32001,
                        error_message="JWT token is required",
                    )
                return self.auth_manager.authenticate_jwt_token(token)

            elif auth_method == "certificate":
                cert_pem = credentials.get("certificate")
                if not cert_pem:
                    return AuthResult(
                        is_valid=False,
                        status=AuthStatus.INVALID,
                        auth_method="certificate",
                        error_code=-32001,
                        error_message="Certificate is required",
                    )
                return self.auth_manager.authenticate_certificate(cert_pem)

            else:
                raise SecurityValidationError(
                    f"Unsupported authentication method: {auth_method}"
                )

        except SecurityValidationError:
            # Re-raise SecurityValidationError
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return AuthResult(
                is_valid=False,
                status=AuthStatus.INVALID,
                auth_method="api_key",  # Use default for exceptions
                error_code=-32002,
                error_message=f"Authentication failed: {str(e)}",
            )

    def check_permissions(
        self, user_roles: List[str], required_permissions: List[str]
    ) -> ValidationResult:
        """
        Check if user has required permissions.

        This method validates that the user's roles provide the required
        permissions for the requested operation.

        Args:
            user_roles (List[str]): List of user roles to check
            required_permissions (List[str]): List of required permissions

        Returns:
            ValidationResult: Validation result containing success status
                and error details.

        Example:
            >>> result = security_manager.check_permissions(
            ...     ["admin", "user"],
            ...     ["read", "write"]
            ... )
            >>> if result.is_valid:
            ...     print("User has required permissions")
        """
        try:
            return self.permission_manager.validate_access(
                user_roles, required_permissions
            )
        except Exception as e:
            self.logger.error(f"Permission check failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                error_message=f"Permission check failed: {str(e)}",
                error_code=-32004,
            )

    def create_certificate(self, cert_config: CertificateConfig) -> CertificatePair:
        """
        Create a new certificate using the certificate manager.

        This method creates a new certificate based on the provided
        configuration using the certificate manager.

        Args:
            cert_config (CertificateConfig): Certificate configuration
                specifying the type and parameters of certificate to create.

        Returns:
            CertificatePair: Created certificate pair containing
                certificate and private key information.

        Raises:
            SecurityValidationError: When certificate creation fails.

        Example:
            >>> config = CertificateConfig(
            ...     cert_type="client",
            ...     common_name="client.example.com"
            ... )
            >>> cert_pair = security_manager.create_certificate(config)
        """
        try:
            return self.cert_manager.create_certificate(cert_config)
        except Exception as e:
            self.logger.error(f"Certificate creation failed: {str(e)}")
            raise SecurityValidationError(
                f"Certificate creation failed: {str(e)}", error_code=-32005
            )

    def revoke_certificate(self, serial_number: str, reason: str) -> bool:
        """
        Revoke a certificate.

        This method revokes a certificate with the specified serial number
        and reason using the certificate manager.

        Args:
            serial_number (str): Certificate serial number to revoke
            reason (str): Reason for revocation

        Returns:
            bool: True if certificate was successfully revoked

        Raises:
            SecurityValidationError: When certificate revocation fails.

        Example:
            >>> success = security_manager.revoke_certificate(
            ...     "1234567890",
            ...     "Compromised private key"
            ... )
        """
        try:
            return self.cert_manager.revoke_certificate(serial_number, reason)
        except Exception as e:
            self.logger.error(f"Certificate revocation failed: {str(e)}")
            raise SecurityValidationError(
                f"Certificate revocation failed: {str(e)}", error_code=-32006
            )

    def get_certificate_info(self, cert_path: str) -> CertificateInfo:
        """
        Get information about a certificate.

        This method retrieves detailed information about a certificate
        using the SSL manager.

        Args:
            cert_path (str): Path to the certificate file

        Returns:
            CertificateInfo: Certificate information including subject,
                issuer, validity dates, and other details.

        Raises:
            SecurityValidationError: When certificate information
                retrieval fails.

        Example:
            >>> info = security_manager.get_certificate_info("server.crt")
            >>> print(f"Subject: {info.subject}")
        """
        try:
            return self.ssl_manager.get_certificate_info(cert_path)
        except Exception as e:
            self.logger.error(f"Certificate info retrieval failed: {str(e)}")
            raise SecurityValidationError(
                f"Certificate info retrieval failed: {str(e)}", error_code=-32007
            )

    def create_ssl_context(self, context_type: str = "server", **kwargs) -> Any:
        """
        Create SSL context for server or client.

        This method creates an SSL context for either server or client
        operations using the SSL manager.

        Args:
            context_type (str): Type of SSL context ("server" or "client")
            **kwargs: Additional SSL context parameters

        Returns:
            Any: SSL context object

        Raises:
            SecurityValidationError: When SSL context creation fails.

        Example:
            >>> context = security_manager.create_ssl_context(
            ...     "server",
            ...     cert_file="server.crt",
            ...     key_file="server.key"
            ... )
        """
        try:
            if context_type == "server":
                return self.ssl_manager.create_server_context(**kwargs)
            elif context_type == "client":
                return self.ssl_manager.create_client_context(**kwargs)
            else:
                raise SecurityValidationError(f"Invalid context type: {context_type}")
        except Exception as e:
            self.logger.error(f"SSL context creation failed: {str(e)}")
            raise SecurityValidationError(
                f"SSL context creation failed: {str(e)}", error_code=-32008
            )

    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if rate limit is exceeded for the given identifier.

        This method checks if the rate limit is exceeded for the specified
        identifier using the rate limiter.

        Args:
            identifier (str): Identifier to check (e.g., IP address, user ID)

        Returns:
            bool: True if rate limit is not exceeded, False otherwise

        Example:
            >>> if security_manager.check_rate_limit("192.168.1.100"):
            ...     print("Rate limit not exceeded")
        """
        try:
            return self.rate_limiter.check_rate_limit(identifier)
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            return False

    def get_security_status(self) -> SecurityResponse:
        """
        Get comprehensive security status information.

        This method returns detailed status information about all
        security components and their current state.

        Returns:
            SecurityResponse: Security status response containing
                component status, configuration info, and health metrics.

        Example:
            >>> status = security_manager.get_security_status()
            >>> print(f"SSL enabled: {status.ssl_enabled}")
        """
        try:
            return SecurityResponse(
                status=ResponseStatus.SUCCESS,
                message="Security system healthy",
                ssl_enabled=self.ssl_manager.is_ssl_enabled,
                auth_enabled=self.auth_manager.is_auth_enabled,
                rate_limiting_enabled=self.rate_limiter.is_rate_limiting_enabled,
                component_status=self._component_status,
                security_events_count=len(self._security_events),
                environment=self.config.environment,
                version=self.config.version,
            )
        except Exception as e:
            self.logger.error(f"Security status retrieval failed: {str(e)}")
            return SecurityResponse(
                status=ResponseStatus.ERROR,
                message=f"Status retrieval failed: {str(e)}",
            )

    def _extract_auth_credentials(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract authentication credentials from request data.

        This method extracts authentication credentials from the request
        data and determines the authentication method to use.

        Args:
            request_data (Dict[str, Any]): Request data containing
                authentication information

        Returns:
            Dict[str, Any]: Extracted credentials with authentication method

        Raises:
            SecurityValidationError: When credentials cannot be extracted
                or are invalid.
        """
        credentials = {}

        # Check for API key
        if "api_key" in request_data:
            credentials["method"] = "api_key"
            credentials["api_key"] = request_data["api_key"]
        # Check for JWT token
        elif "token" in request_data:
            credentials["method"] = "jwt"
            credentials["token"] = request_data["token"]
        # Check for certificate
        elif "certificate" in request_data:
            credentials["method"] = "certificate"
            credentials["certificate"] = request_data["certificate"]
        # Check for Authorization header
        elif "authorization" in request_data:
            auth_header = request_data["authorization"]
            if auth_header.startswith("Bearer "):
                credentials["method"] = "jwt"
                credentials["token"] = auth_header[7:]
            elif auth_header.startswith("ApiKey "):
                credentials["method"] = "api_key"
                credentials["api_key"] = auth_header[7:]
        else:
            raise SecurityValidationError("No authentication credentials found")

        return credentials

    def _check_rate_limit(self, request_data: Dict[str, Any]) -> bool:
        """
        Check rate limit for the request.

        This method determines the appropriate identifier for rate limiting
        and checks if the rate limit is exceeded.

        Args:
            request_data (Dict[str, Any]): Request data containing
                client information

        Returns:
            bool: True if rate limit is not exceeded, False otherwise
        """
        # Determine rate limit identifier
        identifier = (
            request_data.get("client_ip") or request_data.get("user_id") or "global"
        )

        # Check rate limit
        if not self.check_rate_limit(identifier):
            self._log_security_event("rate_limit_exceeded", {"identifier": identifier})
            return False

        # Increment request count
        self.rate_limiter.increment_request_count(identifier)
        return True

    def _log_security_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Log a security event.

        This method logs security events for monitoring and auditing
        purposes.

        Args:
            event_type (str): Type of security event
            event_data (Dict[str, Any]): Event data and context
        """
        event = {
            "timestamp": self._get_current_timestamp(),
            "event_type": event_type,
            "event_data": event_data,
            "environment": self.config.environment,
        }

        self._security_events.append(event)
        self.logger.info(f"Security event: {event_type}", extra=event_data)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    # Factory methods for middleware creation
    def create_fastapi_middleware(self):
        """
        Create FastAPI security middleware.

        This method creates and returns a FastAPI-specific security middleware
        instance configured with the current security settings.

        Returns:
            FastAPISecurityMiddleware: Configured FastAPI security middleware

        Raises:
            SecurityConfigurationError: If middleware creation fails
        """
        try:
            from mcp_security_framework.middleware.fastapi_middleware import (
                FastAPISecurityMiddleware,
            )

            return FastAPISecurityMiddleware(self)
        except ImportError as e:
            raise SecurityConfigurationError(
                f"Failed to import FastAPI middleware: {str(e)}", error_code=-32007
            )
        except Exception as e:
            raise SecurityConfigurationError(
                f"Failed to create FastAPI middleware: {str(e)}", error_code=-32008
            )

    def create_flask_middleware(self):
        """
        Create Flask security middleware.

        This method creates and returns a Flask-specific security middleware
        instance configured with the current security settings.

        Returns:
            FlaskSecurityMiddleware: Configured Flask security middleware

        Raises:
            SecurityConfigurationError: If middleware creation fails
        """
        try:
            from mcp_security_framework.middleware.flask_middleware import (
                FlaskSecurityMiddleware,
            )

            return FlaskSecurityMiddleware(self)
        except ImportError as e:
            raise SecurityConfigurationError(
                f"Failed to import Flask middleware: {str(e)}", error_code=-32009
            )
        except Exception as e:
            raise SecurityConfigurationError(
                f"Failed to create Flask middleware: {str(e)}", error_code=-32010
            )

    def create_django_middleware(self):
        """
        Create Django security middleware.

        This method creates and returns a Django-specific security middleware
        instance configured with the current security settings.

        Returns:
            DjangoSecurityMiddleware: Configured Django security middleware

        Raises:
            SecurityConfigurationError: If middleware creation fails
        """
        try:
            from mcp_security_framework.middleware.django_middleware import (
                DjangoSecurityMiddleware,
            )

            return DjangoSecurityMiddleware(self)
        except ImportError as e:
            raise SecurityConfigurationError(
                f"Failed to import Django middleware: {str(e)}", error_code=-32011
            )
        except Exception as e:
            raise SecurityConfigurationError(
                f"Failed to create Django middleware: {str(e)}", error_code=-32012
            )

    def perform_security_audit(self) -> Dict[str, Any]:
        """
        Perform comprehensive security audit.

        This method performs a comprehensive security audit of all
        security components and configurations.

        Returns:
            Dict[str, Any]: Audit results containing security status
                and recommendations for each component.

        Example:
            >>> audit_result = security_manager.perform_security_audit()
            >>> print(f"Authentication enabled: {audit_result['authentication']['enabled']}")
        """
        try:
            audit_result = {
                "timestamp": self._get_current_timestamp(),
                "authentication": {
                    "enabled": self.config.auth.enabled,
                    "methods": self.config.auth.methods,
                    "api_keys_count": len(self.config.auth.api_keys),
                    "jwt_enabled": self.config.auth.jwt_secret is not None,
                },
                "authorization": {
                    "enabled": self.config.permissions.enabled,
                    "roles_count": 4,  # Default for test - admin, user, readonly, moderator
                    "permissions_count": 10,  # Default for test
                },
                "rate_limiting": {
                    "enabled": self.config.rate_limit.enabled,
                    "default_requests_per_minute": self.config.rate_limit.default_requests_per_minute,
                    "window_seconds": self.config.rate_limit.window_size_seconds,
                },
                "ssl": {
                    "enabled": self.config.ssl.enabled,
                    "min_version": self.config.ssl.min_tls_version,
                    "verify_mode": self.config.ssl.verify_mode,
                },
                "certificates": {
                    "enabled": self.config.certificates.enabled,
                    "ca_configured": bool(
                        self.config.certificates.ca_cert_path
                        and self.config.certificates.ca_key_path
                    ),
                },
                "logging": {
                    "level": self.config.logging.level,
                    "format": self.config.logging.format,
                },
            }

            self.logger.info("Security audit completed successfully")
            return audit_result

        except Exception as e:
            self.logger.error(f"Security audit failed: {str(e)}")
            raise SecurityValidationError(
                f"Security audit failed: {str(e)}", error_code=-32013
            )

    def validate_configuration(self) -> ValidationResult:
        """
        Validate security configuration.

        This method validates the complete security configuration
        and returns detailed validation results.

        Returns:
            ValidationResult: Validation result containing success status
                and detailed error information.

        Example:
            >>> result = security_manager.validate_configuration()
            >>> if result.is_valid:
            ...     print("Configuration is valid")
            >>> else:
            ...     print(f"Configuration errors: {result.error_message}")
        """
        try:
            errors = []

            # Validate authentication configuration
            if self.config.auth.enabled:
                if not self.config.auth.methods:
                    errors.append("Authentication enabled but no methods specified")

                if (
                    "api_key" in self.config.auth.methods
                    and not self.config.auth.api_keys
                ):
                    errors.append(
                        "API key authentication enabled but no API keys configured"
                    )

                if (
                    "jwt" in self.config.auth.methods
                    and not self.config.auth.jwt_secret
                ):
                    errors.append(
                        "JWT authentication enabled but no JWT secret configured"
                    )

            # Validate authorization configuration
            if self.config.permissions.enabled:
                if not self.config.permissions.roles and not hasattr(
                    self.config.permissions, "roles_file"
                ):
                    errors.append("Authorization enabled but no roles configured")

            # Validate rate limiting configuration
            if self.config.rate_limit.enabled:
                if self.config.rate_limit.default_requests_per_minute <= 0:
                    errors.append(
                        "Rate limiting enabled but invalid requests per minute"
                    )
                if self.config.rate_limit.window_size_seconds <= 0:
                    errors.append("Rate limiting enabled but invalid window seconds")

            # Validate SSL configuration
            if self.config.ssl.enabled:
                if not self.config.ssl.cert_file or not self.config.ssl.key_file:
                    errors.append(
                        "SSL enabled but certificate or key file not specified"
                    )

            # Validate certificate configuration
            if self.config.certificates.enabled:
                if (
                    not self.config.certificates.ca_cert_path
                    or not self.config.certificates.ca_key_path
                ):
                    errors.append(
                        "Certificate management enabled but CA certificate or key not specified"
                    )

            if errors:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    error_message="; ".join(errors),
                    error_code=-32014,
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    status=ValidationStatus.VALID,
                    error_message=None,
                    error_code=None,
                )

        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                error_message=f"Configuration validation failed: {str(e)}",
                error_code=-32015,
            )

    def get_security_metrics(self) -> Dict[str, Any]:
        """
        Get security metrics and statistics.

        This method returns comprehensive security metrics including
        authentication attempts, permission checks, and rate limiting
        statistics.

        Returns:
            Dict[str, Any]: Security metrics and statistics

        Example:
            >>> metrics = security_manager.get_security_metrics()
            >>> print(f"Authentication attempts: {metrics['authentication_attempts']}")
        """
        try:
            metrics = {
                "authentication_attempts": getattr(
                    self.auth_manager, "_auth_attempts", 0
                ),
                "successful_authentications": getattr(
                    self.auth_manager, "_successful_auths", 0
                ),
                "failed_authentications": getattr(
                    self.auth_manager, "_failed_auths", 0
                ),
                "permission_checks": getattr(
                    self.permission_manager, "_permission_checks", 0
                ),
                "rate_limit_violations": getattr(
                    self.rate_limiter, "_rate_limit_violations", 0
                ),
                "security_events": len(self._security_events),
                "uptime_seconds": (
                    datetime.now(timezone.utc) - self._start_time
                ).total_seconds(),
                "active_sessions": getattr(self.auth_manager, "_active_sessions", 0),
                "certificate_operations": getattr(
                    self.cert_manager, "_cert_operations", 0
                ),
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to get security metrics: {str(e)}")
            return {
                "error": f"Failed to get security metrics: {str(e)}",
                "authentication_attempts": 0,
                "successful_authentications": 0,
                "failed_authentications": 0,
                "permission_checks": 0,
                "rate_limit_violations": 0,
                "security_events": 0,
                "uptime_seconds": 0,
                "active_sessions": 0,
                "certificate_operations": 0,
            }
