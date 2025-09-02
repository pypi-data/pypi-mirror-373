"""
FastAPI Authentication Middleware Module

This module provides FastAPI-specific authentication middleware implementation
for the MCP Security Framework. It handles authentication-only processing
for FastAPI applications.

Key Features:
- FastAPI-specific request/response handling
- Authentication caching and optimization
- Framework-specific error responses
- Security event logging

Classes:
    FastAPIAuthMiddleware: FastAPI authentication middleware implementation

Dependencies:
    - fastapi: For FastAPI request/response handling
    - starlette: For HTTP status codes and responses
    - pydantic: For configuration validation

Author: MCP Security Team
Version: 1.0.0
License: MIT
Created: 2024-01-15
Last Modified: 2024-01-20
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from mcp_security_framework.middleware.auth_middleware import AuthMiddleware
from mcp_security_framework.schemas.config import SecurityConfig
from mcp_security_framework.schemas.models import AuthMethod, AuthResult, AuthStatus


class FastAPIAuthMiddleware(AuthMiddleware):
    """
    FastAPI Authentication Middleware Implementation

    This class provides FastAPI-specific authentication middleware that
    handles authentication-only processing for FastAPI applications.

    The middleware implements:
    - FastAPI request/response handling
    - Authentication caching and optimization
    - Framework-specific error responses
    - Security event logging

    Attributes:
        config (SecurityConfig): Security configuration settings
        security_manager: Security manager instance
        logger (Logger): Logger instance for authentication operations
        _auth_cache (Dict): Authentication result cache

    Example:
        >>> from mcp_security_framework.middleware import create_auth_middleware
        >>> middleware = create_auth_middleware(config, framework="fastapi")
        >>> app.add_middleware(middleware)

    Raises:
        AuthMiddlewareError: When authentication processing fails
    """

    def __init__(self, security_manager: Any):
        """
        Initialize FastAPI Authentication Middleware.

        Args:
            security_manager: Security manager instance
        """
        super().__init__(security_manager)
        self.logger = logging.getLogger(__name__)

    async def __call__(self, request: Request, call_next: Any) -> Response:
        """
        Process FastAPI request through authentication middleware.

        This method implements the authentication-only processing
        pipeline for FastAPI requests, focusing solely on user
        authentication without authorization checks.

        Args:
            request (Request): FastAPI request object
            call_next: FastAPI call_next function

        Returns:
            Response: FastAPI response object

        Raises:
            AuthMiddlewareError: If authentication processing fails
        """
        try:
            # Check if path is public (bypasses authentication)
            if self._is_public_path(request):
                return await call_next(request)

            # Perform authentication
            auth_result = self._authenticate_only(request)

            if not auth_result.is_valid:
                return self._auth_error_response(auth_result)

            # Add authentication info to request state
            request.state.auth_result = auth_result
            request.state.username = auth_result.username
            request.state.user_roles = auth_result.roles
            request.state.auth_method = auth_result.auth_method

            # Process request
            response = await call_next(request)

            # Log successful authentication
            self._log_auth_event(
                "authentication_successful",
                {
                    "ip_address": self._get_client_ip(request),
                    "username": auth_result.username,
                    "path": str(request.url.path),
                    "method": request.method,
                    "auth_method": auth_result.auth_method,
                },
            )

            return response

        except Exception as e:
            self.logger.error(
                "FastAPI authentication middleware processing failed",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise AuthMiddlewareError(
                f"Authentication processing failed: {str(e)}", error_code=-32035
            )

    def _is_public_path(self, request: Request) -> bool:
        """
        Check if the request path is public (bypasses authentication).

        Args:
            request (Request): FastAPI request object

        Returns:
            bool: True if path is public, False otherwise
        """
        path = str(request.url.path)

        # Check configured public paths
        if hasattr(self.config.auth, "public_paths"):
            for public_path in self.config.auth.public_paths:
                if path.startswith(public_path):
                    return True

        # Check common public paths
        public_paths = ["/health", "/status", "/metrics", "/docs", "/openapi.json"]
        return any(path.startswith(public_path) for public_path in public_paths)

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            str: Client IP address
        """
        # Try X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Try X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Use client host
        if hasattr(request, "client") and request.client:
            return request.client.host

        # Fallback to default IP from config or environment
        default_ip = getattr(self.config, "default_client_ip", None)
        if default_ip:
            return default_ip

        # Use environment variable or default
        import os

        from ..constants import DEFAULT_CLIENT_IP

        return os.environ.get("DEFAULT_CLIENT_IP", DEFAULT_CLIENT_IP)

    def _get_cache_key(self, request: Request) -> str:
        """
        Generate cache key for authentication result.

        Args:
            request (Request): FastAPI request object

        Returns:
            str: Cache key
        """
        # Use combination of IP and user agent for cache key
        ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        return f"auth:{ip}:{hash(user_agent)}"

    def _try_auth_method(self, request: Request, method: str) -> AuthResult:
        """
        Try authentication using specific method with FastAPI request.

        Args:
            request (Request): FastAPI request object
            method (str): Authentication method to try

        Returns:
            AuthResult: Authentication result
        """
        try:
            if method == "api_key":
                return self._try_api_key_auth(request)
            elif method == "jwt":
                return self._try_jwt_auth(request)
            elif method == "certificate":
                return self._try_certificate_auth(request)
            elif method == "basic":
                return self._try_basic_auth(request)
            else:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.FAILED,
                    username=None,
                    roles=[],
                    auth_method=None,
                    error_code=-32022,
                    error_message=f"Unsupported authentication method: {method}",
                )
        except Exception as e:
            self.logger.error(
                f"Authentication method {method} failed",
                extra={"error": str(e)},
                exc_info=True,
            )
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=-32023,
                error_message=f"Authentication method {method} failed: {str(e)}",
            )

    def _try_api_key_auth(self, request: Request) -> AuthResult:
        """
        Try API key authentication with FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            AuthResult: Authentication result
        """
        # Try to get API key from headers
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            # Try Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                api_key = auth_header[7:]  # Remove "Bearer " prefix

        if not api_key:
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=AuthMethod.API_KEY,
                error_code=-32012,
                error_message="API key not found in request",
            )

        # Authenticate using security manager
        return self.security_manager.auth_manager.authenticate_api_key(api_key)

    def _try_jwt_auth(self, request: Request) -> AuthResult:
        """
        Try JWT authentication with FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            AuthResult: Authentication result
        """
        # Try to get JWT token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=AuthMethod.JWT,
                error_code=-32013,
                error_message="JWT token not found in Authorization header",
            )

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Authenticate using security manager
        return self.security_manager.auth_manager.authenticate_jwt_token(token)

    def _try_certificate_auth(self, request: Request) -> AuthResult:
        """
        Try certificate authentication with FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            AuthResult: Authentication result
        """
        # Certificate authentication is typically handled at the SSL/TLS level
        # This method would extract certificate information from the request
        # For now, return not implemented
        return AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.CERTIFICATE,
            error_code=-32014,
            error_message="Certificate authentication not implemented",
        )

    def _try_basic_auth(self, request: Request) -> AuthResult:
        """
        Try basic authentication with FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            AuthResult: Authentication result
        """
        # Try to get basic auth credentials from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=AuthMethod.BASIC,
                error_code=-32015,
                error_message="Basic authentication credentials not found",
            )

        # Basic auth is not implemented in this version
        return AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.BASIC,
            error_code=-32016,
            error_message="Basic authentication not implemented",
        )

    def _auth_error_response(self, auth_result: AuthResult) -> JSONResponse:
        """
        Create authentication error response for FastAPI.

        Args:
            auth_result (AuthResult): Authentication result with error

        Returns:
            JSONResponse: FastAPI error response
        """
        error_data = {
            "error": "Authentication failed",
            "error_code": auth_result.error_code,
            "error_message": auth_result.error_message,
            "auth_method": (
                auth_result.auth_method.value if auth_result.auth_method else None
            ),
        }

        headers = {"WWW-Authenticate": "Bearer", "Content-Type": "application/json"}

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_data,
            headers=headers,
        )

    def _log_auth_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log authentication event.

        Args:
            event_type (str): Type of authentication event
            details (Dict[str, Any]): Event details
        """
        try:
            self.logger.info(
                f"Authentication event: {event_type}",
                extra={
                    "event_type": event_type,
                    "timestamp": details.get("timestamp"),
                    "ip_address": details.get("ip_address"),
                    "username": details.get("username"),
                    "path": details.get("path"),
                    "method": details.get("method"),
                    "auth_method": details.get("auth_method"),
                    **details,
                },
            )
        except Exception as e:
            self.logger.error(
                "Failed to log authentication event",
                extra={"error": str(e)},
                exc_info=True,
            )

    # Abstract method implementations

    def _get_rate_limit_identifier(self, request: Request) -> str:
        """
        Get rate limit identifier from FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            str: Rate limit identifier (IP address)
        """
        return self._get_client_ip(request)

    def _get_request_path(self, request: Request) -> str:
        """
        Get request path from FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            str: Request path
        """
        return str(request.url.path)

    def _get_required_permissions(self, request: Request) -> List[str]:
        """
        Get required permissions for FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            List[str]: List of required permissions
        """
        # For authentication-only middleware, no permissions are required
        return []

    def _apply_security_headers(
        self, response: Response, headers: Dict[str, str]
    ) -> None:
        """
        Apply security headers to FastAPI response.

        Args:
            response (Response): FastAPI response object
            headers (Dict[str, str]): Headers to apply
        """
        for header, value in headers.items():
            response.headers[header] = value

    def _create_error_response(self, status_code: int, message: str) -> JSONResponse:
        """
        Create error response for FastAPI.

        Args:
            status_code (int): HTTP status code
            message (str): Error message

        Returns:
            JSONResponse: FastAPI error response object
        """
        return JSONResponse(
            status_code=status_code, content={"error": message, "error_code": -32000}
        )


class AuthMiddlewareError(Exception):
    """
    Authentication Middleware Error

    This exception is raised when authentication middleware processing fails.

    Attributes:
        message (str): Error message
        error_code (int): Error code for programmatic handling
    """

    def __init__(self, message: str, error_code: int = -32030):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
