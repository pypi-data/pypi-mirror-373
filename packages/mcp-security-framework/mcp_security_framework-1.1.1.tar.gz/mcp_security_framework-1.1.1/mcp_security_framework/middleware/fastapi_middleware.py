"""
FastAPI Security Middleware Module

This module provides FastAPI-specific security middleware implementation
that integrates with FastAPI's middleware system and request/response
handling.

Key Features:
- FastAPI-specific request/response processing
- Integration with FastAPI middleware system
- FastAPI-specific authentication methods
- FastAPI-specific error responses
- FastAPI-specific header management
- FastAPI-specific rate limiting

Classes:
    FastAPISecurityMiddleware: FastAPI-specific security middleware
    FastAPIMiddlewareError: FastAPI middleware-specific error exception

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from ..schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    ValidationResult,
    ValidationStatus,
)
from .security_middleware import SecurityMiddleware, SecurityMiddlewareError


class FastAPIMiddlewareError(SecurityMiddlewareError):
    """Raised when FastAPI middleware encounters an error."""

    def __init__(self, message: str, error_code: int = -32008):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FastAPISecurityMiddleware(SecurityMiddleware):
    """
    FastAPI Security Middleware Class

    This class provides FastAPI-specific implementation of the security
    middleware. It integrates with FastAPI's middleware system and
    handles FastAPI Request/Response objects.

    The FastAPISecurityMiddleware implements:
    - FastAPI-specific request processing
    - FastAPI authentication method handling
    - FastAPI response creation and modification
    - FastAPI-specific error handling
    - FastAPI header management
    - FastAPI rate limiting integration

    Key Responsibilities:
    - Process FastAPI requests through security pipeline
    - Extract authentication credentials from FastAPI requests
    - Create FastAPI-specific error responses
    - Add security headers to FastAPI responses
    - Handle FastAPI-specific request/response objects
    - Integrate with FastAPI middleware system

    Attributes:
        Inherits all attributes from SecurityMiddleware
        _fastapi_app: Reference to FastAPI application (if available)

    Example:
        >>> from fastapi import FastAPI
        >>> from mcp_security_framework.middleware import FastAPISecurityMiddleware
        >>>
        >>> app = FastAPI()
        >>> security_manager = SecurityManager(config)
        >>> middleware = FastAPISecurityMiddleware(security_manager)
        >>> app.add_middleware(middleware)

    Note:
        This middleware should be added to FastAPI applications using
        the add_middleware method or as a dependency.
    """

    def __init__(self, security_manager=None, app=None):
        """
        Initialize FastAPI Security Middleware.

        Args:
            security_manager: Security manager instance containing
                all security components and configuration.
            app: FastAPI application instance (optional, for compatibility)

        Raises:
            FastAPIMiddlewareError: If initialization fails
        """
        if security_manager is None:
            raise FastAPIMiddlewareError("Security manager is required")

        super().__init__(security_manager)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.app = app

        self.logger.info("FastAPI Security Middleware initialized")

    async def __call__(self, request: Request, call_next):
        """
        Process FastAPI request through security middleware.

        This method implements the security processing pipeline for
        FastAPI requests, including rate limiting, authentication,
        authorization, and security header management.

        Args:
            request (Request): FastAPI request object
            call_next: FastAPI call_next function

        Returns:
            Response: FastAPI response object

        Raises:
            HTTPException: For security violations (rate limit, auth, permissions)
            FastAPIMiddlewareError: For middleware processing errors
        """
        try:
            # Check if public path first (no rate limiting for public paths)
            if self._is_public_path(request):
                response = await call_next(request)
                self._add_security_headers(response)
                return response

            # Check rate limit
            if not self._check_rate_limit(request):
                return self._rate_limit_response()

            # Authenticate request
            auth_result = await self._authenticate_request(request)
            if not auth_result.is_valid:
                return self._auth_error_response(auth_result)

            # Validate permissions
            if not self._validate_permissions(request, auth_result):
                return self._permission_error_response()

            # Process request
            response = await call_next(request)
            self._add_security_headers(response)

            # Log successful request
            self._log_security_event(
                "request_processed",
                {
                    "ip_address": self._get_client_ip(request),
                    "username": auth_result.username,
                    "path": str(request.url.path),
                    "method": request.method,
                    "status_code": response.status_code,
                },
            )

            return response

        except HTTPException:
            # Re-raise FastAPI HTTP exceptions
            raise
        except Exception as e:
            self.logger.error(
                "FastAPI middleware processing failed",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise FastAPIMiddlewareError(
                f"Middleware processing failed: {str(e)}", error_code=-32009
            )

    def _check_rate_limit(self, request: Request) -> bool:
        """Check rate limit for request."""
        identifier = self._get_rate_limit_identifier(request)
        return self.security_manager.check_rate_limit(identifier)

    def _is_public_path(self, request: Request) -> bool:
        """Check if request path is public."""
        path = str(request.url.path)
        return path in self.config.auth.public_paths

    async def _authenticate_request(self, request: Request) -> AuthResult:
        """Authenticate request using configured methods."""
        # Try API key authentication first
        auth_result = self._try_api_key_auth(request)
        if auth_result.is_valid:
            return auth_result

        # Try JWT authentication
        auth_result = self._try_jwt_auth(request)
        if auth_result.is_valid:
            return auth_result

        # Return failed authentication
        return AuthResult(
            is_valid=False,
            status=AuthStatus.INVALID,
            auth_method="unknown",
            error_code=-32001,
            error_message="Authentication required",
        )

    def _validate_permissions(self, request: Request, auth_result: AuthResult) -> bool:
        """Validate permissions for request."""
        # Get required permissions from request state or default
        required_permissions = self._get_required_permissions_from_state(request)
        if not required_permissions:
            return True  # No permissions required

        # Check permissions
        validation_result = self.security_manager.check_permissions(
            auth_result.roles, required_permissions
        )
        return validation_result.is_valid

    def _rate_limit_response(self) -> JSONResponse:
        """Create rate limit exceeded response."""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "error_code": -32010,
                "retry_after": 60,
            },
        )

    def _auth_error_response(self, auth_result: AuthResult) -> JSONResponse:
        """Create authentication error response."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Authentication failed",
                "error_code": auth_result.error_code,
                "error_message": auth_result.error_message,
            },
        )

    def _permission_error_response(self) -> JSONResponse:
        """Create permission denied response."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Permission denied",
                "error_code": -32004,
                "error_message": "Insufficient permissions",
            },
        )

    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    def _log_security_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log security event."""
        self.logger.info(f"Security event: {event_type}", extra=data)

    def _get_required_permissions_from_state(self, request: Request) -> List[str]:
        """Get required permissions from request state."""
        # This would typically be set by route decorators or middleware
        # For now, return empty list (no permissions required)
        return []

    def _get_required_permissions_default(self, request: Request) -> List[str]:
        """Get default required permissions for request."""
        # Default permissions based on HTTP method
        method_permissions = {
            "GET": ["read"],
            "POST": ["write"],
            "PUT": ["write"],
            "DELETE": ["delete"],
            "PATCH": ["write"],
        }
        return method_permissions.get(request.method, [])

    def _try_api_key_auth(self, request: Request) -> AuthResult:
        """Try API key authentication."""
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return self.security_manager.auth_manager.authenticate_api_key(api_key)

        # Check for API key in Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header[7:]  # Remove "Bearer " prefix
            return self.security_manager.auth_manager.authenticate_api_key(api_key)

        return AuthResult(
            is_valid=False,
            status=AuthStatus.INVALID,
            auth_method="api_key",
            error_code=-32001,
            error_message="API key not provided",
        )

    def _try_jwt_auth(self, request: Request) -> AuthResult:
        """Try JWT authentication."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return AuthResult(
                is_valid=False,
                status=AuthStatus.INVALID,
                auth_method="jwt",
                error_code=-32001,
                error_message="JWT token not provided",
            )

        token = auth_header[7:]  # Remove "Bearer " prefix
        return self.security_manager.auth_manager.authenticate_jwt_token(token)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Check for client host
        if request.client and request.client.host:
            return request.client.host

        # Fallback
        return "unknown"

    def _get_rate_limit_identifier(self, request: Request) -> str:
        """
        Get rate limit identifier from FastAPI request.

        This method extracts the rate limit identifier from the FastAPI
        request, typically using the client IP address.

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

        This method extracts required permissions from the FastAPI request,
        typically from route dependencies or request state.

        Args:
            request (Request): FastAPI request object

        Returns:
            List[str]: List of required permissions
        """
        # Try to get permissions from request state
        if hasattr(request.state, "required_permissions"):
            return request.state.required_permissions

        # Try to get permissions from route dependencies
        if hasattr(request, "route") and hasattr(request.route, "dependencies"):
            # Check if route has permission dependencies
            dependencies = request.route.dependencies
            for dep in dependencies:
                if hasattr(dep, "dependency") and hasattr(
                    dep.dependency, "required_permissions"
                ):
                    return dep.dependency.required_permissions
                # Check for permission decorators
                if hasattr(dep, "dependency") and hasattr(
                    dep.dependency, "__permissions__"
                ):
                    return dep.dependency.__permissions__

        # Default: no specific permissions required
        return []

    async def _authenticate_request(self, request: Request) -> AuthResult:
        """
        Authenticate the request using configured authentication methods.

        This method attempts to authenticate the request using all configured
        authentication methods in order until one succeeds.

        Args:
            request (Request): FastAPI request object

        Returns:
            AuthResult: Authentication result

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
                auth_result = await self._try_auth_method(request, method)
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

    async def _try_auth_method(self, request: Request, method: str) -> AuthResult:
        """
        Try authentication using specific method with FastAPI request.

        This method attempts to authenticate the FastAPI request using
        the specified authentication method.

        Args:
            request (Request): FastAPI request object
            method (str): Authentication method to try

        Returns:
            AuthResult: Authentication result
        """
        try:
            if method == "api_key":
                return await self._try_api_key_auth(request)
            elif method == "jwt":
                return await self._try_jwt_auth(request)
            elif method == "certificate":
                return await self._try_certificate_auth(request)
            elif method == "basic":
                return await self._try_basic_auth(request)
            else:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.FAILED,
                    username=None,
                    roles=[],
                    auth_method=None,
                    error_code=-32010,
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
                error_code=-32011,
                error_message=f"Authentication method {method} failed: {str(e)}",
            )

    async def _try_api_key_auth(self, request: Request) -> AuthResult:
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

    async def _try_jwt_auth(self, request: Request) -> AuthResult:
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

    async def _try_certificate_auth(self, request: Request) -> AuthResult:
        """
        Try certificate authentication with FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            AuthResult: Authentication result
        """
        # For certificate authentication, we would typically need
        # to access the client certificate from the SSL context
        # This is more complex and depends on the SSL configuration

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

    async def _try_basic_auth(self, request: Request) -> AuthResult:
        """
        Try basic authentication with FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            AuthResult: Authentication result
        """
        # Try to get basic auth from Authorization header
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

        # Basic auth implementation would go here
        # For now, return not implemented
        return AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.BASIC,
            error_code=-32016,
            error_message="Basic authentication not implemented",
        )

    def _apply_security_headers(
        self, response: Response, headers: Dict[str, str]
    ) -> None:
        """
        Apply security headers to FastAPI response.

        Args:
            response (Response): FastAPI response object
            headers (Dict[str, str]): Headers to apply
        """
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

    def _create_error_response(self, status_code: int, message: str) -> Response:
        """
        Create error response for security violations.

        Args:
            status_code (int): HTTP status code
            message (str): Error message

        Returns:
            Response: FastAPI error response
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "error": "Security violation",
                "message": message,
                "error_code": -32017,
            },
        )

    def _rate_limit_response(self) -> Response:
        """
        Create rate limit exceeded response.

        Returns:
            Response: FastAPI rate limit response
        """
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests, please try again later",
                "error_code": -32018,
            },
            headers={"Retry-After": str(self.config.rate_limit.window_size_seconds)},
        )

    def _auth_error_response(self, auth_result: AuthResult) -> Response:
        """
        Create authentication error response.

        Args:
            auth_result (AuthResult): Authentication result

        Returns:
            Response: FastAPI authentication error response
        """
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Authentication failed",
                "message": auth_result.error_message or "Invalid credentials",
                "error_code": auth_result.error_code,
                "auth_method": auth_result.auth_method,
            },
            headers={"WWW-Authenticate": "Bearer, ApiKey"},
        )

    def _permission_error_response(self) -> Response:
        """
        Create permission denied response.

        Returns:
            Response: FastAPI permission error response
        """
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Permission denied",
                "message": "Insufficient permissions to access this resource",
                "error_code": -32019,
            },
        )

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from FastAPI request.

        Args:
            request (Request): FastAPI request object

        Returns:
            str: Client IP address
        """
        # Try to get IP from X-Forwarded-For header (for proxy scenarios)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Try to get IP from X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client host
        if request.client:
            return request.client.host

        # Default fallback
        # Fallback to default IP from config or environment
        default_ip = getattr(self.config, "default_client_ip", None)
        if default_ip:
            return default_ip

        # Use environment variable or default
        import os

        from ..constants import DEFAULT_CLIENT_IP

        return os.environ.get("DEFAULT_CLIENT_IP", DEFAULT_CLIENT_IP)
