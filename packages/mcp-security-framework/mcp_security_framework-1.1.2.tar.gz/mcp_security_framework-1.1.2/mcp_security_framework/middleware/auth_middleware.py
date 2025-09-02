"""
Authentication Middleware Module

This module provides specialized authentication-only middleware that
focuses solely on user authentication without authorization checks.

Key Features:
- Authentication-only processing
- Multiple authentication method support
- Authentication result caching
- Authentication event logging
- Framework-agnostic design

Classes:
    AuthMiddleware: Authentication-only middleware
    AuthMiddlewareError: Authentication middleware-specific error exception

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..schemas.models import AuthResult, AuthStatus
from .security_middleware import SecurityMiddleware, SecurityMiddlewareError


class AuthMiddlewareError(SecurityMiddlewareError):
    """Raised when authentication middleware encounters an error."""

    def __init__(self, message: str, error_code: int = -32032):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthMiddleware(SecurityMiddleware):
    """
    Authentication-Only Middleware Class

    This class provides authentication-only middleware that focuses
    solely on user authentication without performing authorization
    checks. It's useful for scenarios where authentication and
    authorization are handled separately.

    The AuthMiddleware implements:
    - Authentication-only request processing
    - Multiple authentication method support
    - Authentication result caching
    - Authentication event logging
    - Framework-agnostic design

    Key Responsibilities:
    - Process requests through authentication pipeline only
    - Handle multiple authentication methods
    - Cache authentication results for performance
    - Log authentication events and failures
    - Provide authentication status to downstream components

    Attributes:
        Inherits all attributes from SecurityMiddleware
        _auth_cache (Dict): Cache for authentication results
        _cache_ttl (int): Time-to-live for cached results

    Example:
        >>> from mcp_security_framework.middleware import AuthMiddleware
        >>>
        >>> security_manager = SecurityManager(config)
        >>> auth_middleware = AuthMiddleware(security_manager)
        >>> app.add_middleware(auth_middleware)

    Note:
        This middleware only handles authentication. Authorization
        should be handled separately by other middleware or
        application logic.
    """

    def __init__(self, security_manager, cache_ttl: int = 300):
        """
        Initialize Authentication-Only Middleware.

        Args:
            security_manager: Security manager instance containing
                all security components and configuration.
            cache_ttl (int): Time-to-live for cached authentication
                results in seconds. Defaults to 300 seconds (5 minutes).

        Raises:
            AuthMiddlewareError: If initialization fails
        """
        super().__init__(security_manager)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._cache_ttl = cache_ttl

        self.logger.info(
            "Authentication middleware initialized", extra={"cache_ttl": cache_ttl}
        )

    @abstractmethod
    def __call__(self, request: Any, call_next: Any) -> Any:
        """
        Process request through authentication middleware.

        This method implements the authentication-only processing
        pipeline, focusing solely on user authentication.

        Args:
            request: Framework-specific request object
            call_next: Framework-specific call_next function

        Returns:
            Framework-specific response object

        Raises:
            AuthMiddlewareError: If authentication processing fails
        """
        pass

    def _authenticate_only(self, request: Any) -> AuthResult:
        """
        Perform authentication-only processing.

        This method handles authentication without authorization
        checks, making it suitable for scenarios where auth and
        authz are separated.

        Args:
            request: Framework-specific request object

        Returns:
            AuthResult: Authentication result with user information

        Raises:
            AuthMiddlewareError: If authentication process fails
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

            # Check cache first
            cache_key = self._get_cache_key(request)
            if cache_key in self._auth_cache:
                cached_result = self._auth_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    self.logger.debug(
                        "Using cached authentication result",
                        extra={"username": cached_result.username},
                    )
                    return cached_result

            # Try each authentication method in order
            for method in self.config.auth.methods:
                auth_result = self._try_auth_method(request, method)
                if auth_result.is_valid:
                    # Cache successful authentication result
                    self._cache_auth_result(cache_key, auth_result)

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

            failed_result = AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=-32033,
                error_message="All authentication methods failed",
            )

            # Cache failed result briefly to prevent repeated attempts
            self._cache_auth_result(cache_key, failed_result, ttl=60)
            return failed_result

        except Exception as e:
            self.logger.error(
                "Authentication process failed", extra={"error": str(e)}, exc_info=True
            )
            raise AuthMiddlewareError(
                f"Authentication process failed: {str(e)}", error_code=-32034
            )

    def _get_cache_key(self, request: Any) -> str:
        """
        Generate cache key for authentication result.

        Args:
            request: Framework-specific request object

        Returns:
            str: Cache key for authentication result
        """
        # Use a combination of IP and user agent for cache key
        ip = self._get_rate_limit_identifier(request)
        user_agent = self._get_user_agent(request)
        return f"auth:{ip}:{user_agent}"

    def _is_cache_valid(self, auth_result: AuthResult) -> bool:
        """
        Check if cached authentication result is still valid.

        Args:
            auth_result (AuthResult): Cached authentication result

        Returns:
            bool: True if cache is valid, False otherwise
        """
        # For now, assume cache is valid if it exists
        # In a real implementation, you might check timestamps
        return True

    def _cache_auth_result(
        self, cache_key: str, auth_result: AuthResult, ttl: int = None
    ) -> None:
        """
        Cache authentication result.

        Args:
            cache_key (str): Cache key for the result
            auth_result (AuthResult): Authentication result to cache
            ttl (int): Time-to-live in seconds (optional)
        """
        if ttl is None:
            ttl = self._cache_ttl

        # In a real implementation, you would store with timestamp
        self._auth_cache[cache_key] = auth_result

    def _clear_auth_cache(self) -> None:
        """Clear all cached authentication results."""
        self._auth_cache.clear()
        self.logger.info("Authentication cache cleared")

    def _get_user_agent(self, request: Any) -> str:
        """
        Get user agent from request.

        Args:
            request: Framework-specific request object

        Returns:
            str: User agent string
        """
        # This should be implemented by framework-specific subclasses
        return "unknown"

    def _log_auth_event(
        self, event_type: str, auth_result: AuthResult, request_details: Dict[str, Any]
    ) -> None:
        """
        Log authentication event.

        Args:
            event_type (str): Type of authentication event
            auth_result (AuthResult): Authentication result
            request_details (Dict[str, Any]): Request details
        """
        self.logger.info(
            f"Authentication event: {event_type}",
            extra={
                "event_type": event_type,
                "username": auth_result.username,
                "auth_method": auth_result.auth_method,
                "is_valid": auth_result.is_valid,
                "error_code": auth_result.error_code,
                "error_message": auth_result.error_message,
                **request_details,
            },
        )
