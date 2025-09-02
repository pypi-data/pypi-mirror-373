"""
Security Middleware Module

This module provides the base SecurityMiddleware class that serves as the
foundation for all framework-specific security middleware implementations.

Key Features:
- Abstract base class for all security middleware
- Common security logic and request processing
- Framework-agnostic security operations
- Unified interface for authentication and authorization
- Rate limiting and security header management
- Security event logging and monitoring

Classes:
    SecurityMiddleware: Abstract base class for security middleware
    SecurityMiddlewareError: Middleware-specific error exception

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ..core.security_manager import SecurityManager
from ..schemas.config import SecurityConfig
from ..schemas.models import AuthResult, AuthStatus, ValidationResult, ValidationStatus
from ..schemas.responses import ResponseStatus, SecurityResponse


class SecurityMiddlewareError(Exception):
    """Raised when security middleware encounters an error."""

    def __init__(self, message: str, error_code: int = -32003):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class SecurityMiddleware(ABC):
    """
    Abstract Security Middleware Class

    This is the base class for all framework-specific security middleware
    implementations. It provides common security logic and a unified
    interface for request processing, authentication, authorization,
    and rate limiting.

    The SecurityMiddleware implements the security processing pipeline:
    1. Rate limiting check
    2. Public path validation
    3. Authentication
    4. Authorization
    5. Security headers addition
    6. Response processing

    Key Responsibilities:
    - Process incoming requests through security pipeline
    - Handle authentication using multiple methods
    - Validate user permissions and access rights
    - Implement rate limiting and abuse prevention
    - Add security headers to responses
    - Log security events and violations
    - Provide framework-specific request/response handling

    Attributes:
        security_manager (SecurityManager): Main security manager instance
        config (SecurityConfig): Security configuration
        logger (Logger): Logger instance for middleware operations
        _public_paths (List[str]): List of public paths that bypass security
        _rate_limit_cache (Dict): Cache for rate limiting data
        _auth_cache (Dict): Cache for authentication results

    Example:
        >>> config = SecurityConfig(auth=AuthConfig(enabled=True))
        >>> security_manager = SecurityManager(config)
        >>> middleware = FastAPISecurityMiddleware(security_manager)
        >>> app.add_middleware(middleware)

    Note:
        This is an abstract base class. Implementations must provide
        framework-specific request/response handling methods.
    """

    def __init__(self, security_manager: SecurityManager):
        """
        Initialize Security Middleware.

        Args:
            security_manager (SecurityManager): Security manager instance
                containing all security components and configuration.
                Must be a properly initialized SecurityManager with
                valid configuration.

        Raises:
            SecurityMiddlewareError: If security manager is invalid or
                configuration is missing.

        Example:
            >>> security_manager = SecurityManager(config)
            >>> middleware = FastAPISecurityMiddleware(security_manager)
        """
        if not isinstance(security_manager, SecurityManager):
            raise SecurityMiddlewareError(
                "Invalid security manager: must be SecurityManager instance",
                error_code=-32003,
            )

        self.security_manager = security_manager
        self.config = security_manager.config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize caches and state
        self._public_paths = self.config.auth.public_paths if self.config.auth else []
        self._rate_limit_cache: Dict[str, Dict[str, Any]] = {}
        self._auth_cache: Dict[str, AuthResult] = {}

        self.logger.info(
            "Security middleware initialized",
            extra={
                "middleware_type": self.__class__.__name__,
                "auth_enabled": self.config.auth.enabled if self.config.auth else False,
                "public_paths_count": len(self._public_paths),
            },
        )

    @abstractmethod
    def __call__(self, request: Any, call_next: Any) -> Any:
        """
        Process request through security middleware.

        This is the main entry point for the middleware. It implements
        the security processing pipeline and delegates framework-specific
        operations to abstract methods.

        Args:
            request: Framework-specific request object
            call_next: Framework-specific call_next function

        Returns:
            Framework-specific response object

        Raises:
            SecurityMiddlewareError: If security processing fails
            AuthenticationError: If authentication fails
            PermissionDeniedError: If authorization fails
            RateLimitExceededError: If rate limit is exceeded
        """
        pass

    def _check_rate_limit(self, request: Any) -> bool:
        """
        Check if request is within rate limits.

        This method checks if the current request exceeds rate limits
        based on the request identifier (IP, user, etc.).

        Args:
            request: Framework-specific request object

        Returns:
            bool: True if request is within rate limits, False otherwise

        Raises:
            SecurityMiddlewareError: If rate limiting check fails
        """
        try:
            if not self.config.rate_limit.enabled:
                return True

            identifier = self._get_rate_limit_identifier(request)
            if not identifier:
                self.logger.warning("Could not determine rate limit identifier")
                return True

            # Check rate limit using security manager
            is_allowed = self.security_manager.rate_limiter.check_rate_limit(identifier)

            if not is_allowed:
                self.logger.warning(
                    "Rate limit exceeded",
                    extra={
                        "identifier": identifier,
                        "rate_limit": self.config.rate_limit.default_requests_per_minute,
                        "window_seconds": self.config.rate_limit.window_size_seconds,
                    },
                )

            return is_allowed

        except Exception as e:
            self.logger.error(
                "Rate limit check failed", extra={"error": str(e)}, exc_info=True
            )
            raise SecurityMiddlewareError(
                f"Rate limit check failed: {str(e)}", error_code=-32004
            )

    def _authenticate_request(self, request: Any) -> AuthResult:
        """
        Authenticate the request using configured methods.

        This method attempts to authenticate the request using all
        configured authentication methods in order of preference.

        Args:
            request: Framework-specific request object

        Returns:
            AuthResult: Authentication result with user information

        Raises:
            SecurityMiddlewareError: If authentication process fails
        """
        try:
            if not self.config.auth.enabled:
                return AuthResult(
                    is_valid=True,
                    status=AuthStatus.SUCCESS,
                    username="anonymous",
                    roles=[],
                    auth_method=None,
                )

            # Try each authentication method in order
            for method in self.config.auth.methods:
                auth_result = self._try_auth_method(request, method)
                # Handle async methods
                if hasattr(auth_result, "__await__"):
                    import asyncio

                    try:
                        auth_result = asyncio.run(auth_result)
                    except RuntimeError:
                        # If we're already in an event loop, use create_task
                        loop = asyncio.get_event_loop()
                        auth_result = loop.run_until_complete(auth_result)

                if auth_result.is_valid:
                    self.logger.info(
                        "Authentication successful",
                        extra={
                            "username": auth_result.username,
                            "auth_method": auth_result.auth_method,
                            "user_roles": auth_result.roles,
                        },
                    )
                    return auth_result

            # All authentication methods failed
            self.logger.warning(
                "All authentication methods failed",
                extra={"auth_methods": self.config.auth.methods},
            )

            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=-32005,
                error_message="All authentication methods failed",
            )

        except Exception as e:
            self.logger.error(
                "Authentication process failed", extra={"error": str(e)}, exc_info=True
            )
            raise SecurityMiddlewareError(
                f"Authentication process failed: {str(e)}", error_code=-32006
            )

    def _validate_permissions(self, request: Any, auth_result: AuthResult) -> bool:
        """
        Validate user permissions for the requested resource.

        This method checks if the authenticated user has the required
        permissions to access the requested resource.

        Args:
            request: Framework-specific request object
            auth_result (AuthResult): Authentication result with user info

        Returns:
            bool: True if user has required permissions, False otherwise

        Raises:
            SecurityMiddlewareError: If permission validation fails
        """
        try:
            if not auth_result.is_valid:
                return False

            # Get required permissions for the request
            required_permissions = self._get_required_permissions(request)
            if not required_permissions:
                # No specific permissions required
                return True

            # Check permissions using security manager
            validation_result = self.security_manager.check_permissions(
                auth_result.roles, required_permissions
            )

            if not validation_result.is_valid:
                self.logger.warning(
                    "Permission validation failed",
                    extra={
                        "username": auth_result.username,
                        "user_roles": auth_result.roles,
                        "required_permissions": required_permissions,
                        "error_message": validation_result.error_message,
                    },
                )

            return validation_result.is_valid

        except Exception as e:
            self.logger.error(
                "Permission validation failed", extra={"error": str(e)}, exc_info=True
            )
            raise SecurityMiddlewareError(
                f"Permission validation failed: {str(e)}", error_code=-32007
            )

    def _is_public_path(self, request: Any) -> bool:
        """
        Check if the request path is public (bypasses security).

        Args:
            request: Framework-specific request object

        Returns:
            bool: True if path is public, False otherwise
        """
        try:
            path = self._get_request_path(request)
            if not path:
                return False

            # Check if path matches any public path pattern
            for public_path in self._public_paths:
                if path == public_path or path.startswith(public_path):
                    return True

            return False

        except Exception as e:
            self.logger.error(
                "Public path check failed", extra={"error": str(e)}, exc_info=True
            )
            return False

    def _add_security_headers(self, response: Any) -> None:
        """
        Add security headers to the response.

        Args:
            response: Framework-specific response object
        """
        try:
            # Add standard security headers
            headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": "default-src 'self'",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }

            # Add custom security headers from config
            if self.config.auth and self.config.auth.security_headers:
                headers.update(self.config.auth.security_headers)

            # Apply headers using framework-specific method
            self._apply_security_headers(response, headers)

        except Exception as e:
            self.logger.error(
                "Failed to add security headers", extra={"error": str(e)}, exc_info=True
            )

    def _log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log security event for monitoring and auditing.

        Args:
            event_type (str): Type of security event
            details (Dict[str, Any]): Event details
        """
        try:
            self.logger.info(
                f"Security event: {event_type}",
                extra={
                    "event_type": event_type,
                    "timestamp": details.get("timestamp"),
                    "ip_address": details.get("ip_address"),
                    "username": details.get("username"),
                    "path": details.get("path"),
                    "method": details.get("method"),
                    **details,
                },
            )
        except Exception as e:
            self.logger.error(
                "Failed to log security event", extra={"error": str(e)}, exc_info=True
            )

    # Abstract methods for framework-specific implementations

    @abstractmethod
    def _get_rate_limit_identifier(self, request: Any) -> str:
        """
        Get rate limit identifier from request.

        Args:
            request: Framework-specific request object

        Returns:
            str: Rate limit identifier (IP, user ID, etc.)
        """
        pass

    @abstractmethod
    def _get_request_path(self, request: Any) -> str:
        """
        Get request path from request object.

        Args:
            request: Framework-specific request object

        Returns:
            str: Request path
        """
        pass

    @abstractmethod
    def _get_required_permissions(self, request: Any) -> List[str]:
        """
        Get required permissions for the request.

        Args:
            request: Framework-specific request object

        Returns:
            List[str]: List of required permissions
        """
        pass

    @abstractmethod
    def _try_auth_method(self, request: Any, method: str) -> AuthResult:
        """
        Try authentication using specific method.

        Args:
            request: Framework-specific request object
            method (str): Authentication method to try

        Returns:
            AuthResult: Authentication result
        """
        pass

    @abstractmethod
    def _apply_security_headers(self, response: Any, headers: Dict[str, str]) -> None:
        """
        Apply security headers to response.

        Args:
            response: Framework-specific response object
            headers (Dict[str, str]): Headers to apply
        """
        pass

    @abstractmethod
    def _create_error_response(self, status_code: int, message: str) -> Any:
        """
        Create error response for security violations.

        Args:
            status_code (int): HTTP status code
            message (str): Error message

        Returns:
            Framework-specific error response object
        """
        pass
