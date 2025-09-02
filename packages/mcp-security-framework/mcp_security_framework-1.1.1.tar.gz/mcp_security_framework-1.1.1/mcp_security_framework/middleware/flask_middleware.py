"""
Flask Security Middleware Module

This module provides Flask-specific security middleware implementation
that integrates with Flask's WSGI system and request/response handling.

Key Features:
- Flask-specific request/response processing
- Integration with Flask WSGI system
- Flask-specific authentication methods
- Flask-specific error responses
- Flask-specific header management
- Flask-specific rate limiting

Classes:
    FlaskSecurityMiddleware: Flask-specific security middleware
    FlaskMiddlewareError: Flask middleware-specific error exception

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from flask import Request, Response, current_app, jsonify, make_response, request

from ..schemas.models import AuthMethod, AuthResult, AuthStatus
from .security_middleware import SecurityMiddleware, SecurityMiddlewareError


class FlaskMiddlewareError(SecurityMiddlewareError):
    """Raised when Flask middleware encounters an error."""

    def __init__(self, message: str, error_code: int = -32020):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FlaskSecurityMiddleware(SecurityMiddleware):
    """
    Flask Security Middleware Class

    This class provides Flask-specific implementation of the security
    middleware. It integrates with Flask's WSGI system and handles
    Flask Request/Response objects.

    The FlaskSecurityMiddleware implements:
    - Flask-specific request processing
    - Flask authentication method handling
    - Flask response creation and modification
    - Flask-specific error handling
    - Flask header management
    - Flask rate limiting integration

    Key Responsibilities:
    - Process Flask requests through security pipeline
    - Extract authentication credentials from Flask requests
    - Create Flask-specific error responses
    - Add security headers to Flask responses
    - Handle Flask-specific request/response objects
    - Integrate with Flask WSGI system

    Attributes:
        Inherits all attributes from SecurityMiddleware
        _flask_app: Reference to Flask application (if available)

    Example:
        >>> from flask import Flask
        >>> from mcp_security_framework.middleware import FlaskSecurityMiddleware
        >>>
        >>> app = Flask(__name__)
        >>> security_manager = SecurityManager(config)
        >>> middleware = FlaskSecurityMiddleware(security_manager)
        >>> app.wsgi_app = middleware(app.wsgi_app)

    Note:
        This middleware should be integrated with Flask applications
        by wrapping the WSGI application.
    """

    def __init__(self, security_manager):
        """
        Initialize Flask Security Middleware.

        Args:
            security_manager: Security manager instance containing
                all security components and configuration.

        Raises:
            FlaskMiddlewareError: If initialization fails
        """
        super().__init__(security_manager)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.logger.info("Flask Security Middleware initialized")

    def __call__(self, environ: Dict[str, Any], start_response) -> List[bytes]:
        """
        Process Flask request through security middleware.

        This method implements the security processing pipeline for
        Flask requests, including rate limiting, authentication,
        authorization, and security header management.

        Args:
            environ (Dict[str, Any]): WSGI environment dictionary
            start_response: WSGI start_response callable

        Returns:
            List[bytes]: WSGI response body

        Raises:
            FlaskMiddlewareError: For middleware processing errors
        """
        try:
            # Create Flask request object from WSGI environ
            flask_request = Request(environ)

            # Check rate limit
            if not self._check_rate_limit(flask_request):
                return self._rate_limit_response(start_response)

            # Check if public path
            if self._is_public_path(flask_request):
                # Process request normally
                return self._process_request(environ, start_response, flask_request)

            # Authenticate request
            auth_result = self._authenticate_request(flask_request)
            if not auth_result.is_valid:
                return self._auth_error_response(auth_result, start_response)

            # Validate permissions
            if not self._validate_permissions(flask_request, auth_result):
                return self._permission_error_response(start_response)

            # Process request
            return self._process_request(
                environ, start_response, flask_request, auth_result
            )

        except Exception as e:
            self.logger.error(
                "Flask middleware processing failed",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise FlaskMiddlewareError(
                f"Middleware processing failed: {str(e)}", error_code=-32021
            )

    def _process_request(
        self,
        environ: Dict[str, Any],
        start_response,
        flask_request: Request,
        auth_result: AuthResult = None,
    ) -> List[bytes]:
        """
        Process the actual request through the WSGI application.

        Args:
            environ (Dict[str, Any]): WSGI environment
            start_response: WSGI start_response callable
            flask_request (Request): Flask request object
            auth_result (AuthResult): Authentication result (optional)

        Returns:
            List[bytes]: WSGI response body
        """
        # Store auth result in request context for later use
        if auth_result:
            flask_request.auth_result = auth_result

        # Call the original WSGI application
        def custom_start_response(status, headers, exc_info=None):
            # Add security headers
            security_headers = self._get_security_headers()
            headers.extend(security_headers)

            # Log successful request
            if auth_result:
                self._log_security_event(
                    "request_processed",
                    {
                        "ip_address": self._get_client_ip(flask_request),
                        "username": auth_result.username,
                        "path": flask_request.path,
                        "method": flask_request.method,
                        "status_code": int(status.split()[0]),
                    },
                )

            return start_response(status, headers, exc_info)

        # Get the original WSGI app from the middleware chain
        app = current_app._get_current_object()
        return app(environ, custom_start_response)

    def _get_rate_limit_identifier(self, request: Request) -> str:
        """
        Get rate limit identifier from Flask request.

        This method extracts the rate limit identifier from the Flask
        request, typically using the client IP address.

        Args:
            request (Request): Flask request object

        Returns:
            str: Rate limit identifier (IP address)
        """
        return self._get_client_ip(request)

    def _get_request_path(self, request: Request) -> str:
        """
        Get request path from Flask request.

        Args:
            request (Request): Flask request object

        Returns:
            str: Request path
        """
        return request.path

    def _get_required_permissions(self, request: Request) -> List[str]:
        """
        Get required permissions for Flask request.

        This method extracts required permissions from the Flask request,
        typically from route decorators or request context.

        Args:
            request (Request): Flask request object

        Returns:
            List[str]: List of required permissions
        """
        # Try to get permissions from request context
        if hasattr(request, "required_permissions"):
            return request.required_permissions

        # Try to get permissions from route decorators
        if hasattr(request, "endpoint"):
            # Check if endpoint has permission decorators
            endpoint = request.endpoint
            if (
                hasattr(endpoint, "required_permissions")
                and endpoint.required_permissions is not None
            ):
                return endpoint.required_permissions
            # Check for permission decorators
            if (
                hasattr(endpoint, "__permissions__")
                and endpoint.__permissions__ is not None
            ):
                return endpoint.__permissions__
            # Check for role-based decorators
            if (
                hasattr(endpoint, "required_roles")
                and endpoint.required_roles is not None
            ):
                return endpoint.required_roles

        # Default: no specific permissions required
        return []

    def _try_auth_method(self, request: Request, method: str) -> AuthResult:
        """
        Try authentication using specific method with Flask request.

        This method attempts to authenticate the Flask request using
        the specified authentication method.

        Args:
            request (Request): Flask request object
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
        Try API key authentication with Flask request.

        Args:
            request (Request): Flask request object

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
                error_code=-32024,
                error_message="API key not found in request",
            )

        # Authenticate using security manager
        return self.security_manager.auth_manager.authenticate_api_key(api_key)

    def _try_jwt_auth(self, request: Request) -> AuthResult:
        """
        Try JWT authentication with Flask request.

        Args:
            request (Request): Flask request object

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
                error_code=-32025,
                error_message="JWT token not found in Authorization header",
            )

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Authenticate using security manager
        return self.security_manager.auth_manager.authenticate_jwt_token(token)

    def _try_certificate_auth(self, request: Request) -> AuthResult:
        """
        Try certificate authentication with Flask request.

        Args:
            request (Request): Flask request object

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
            error_code=-32026,
            error_message="Certificate authentication not implemented",
        )

    def _try_basic_auth(self, request: Request) -> AuthResult:
        """
        Try basic authentication with Flask request.

        Args:
            request (Request): Flask request object

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
                error_code=-32027,
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
            error_code=-32028,
            error_message="Basic authentication not implemented",
        )

    def _apply_security_headers(
        self, response: Response, headers: Dict[str, str]
    ) -> None:
        """
        Apply security headers to Flask response.

        Args:
            response (Response): Flask response object
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
            Response: Flask error response
        """
        return make_response(
            jsonify(
                {
                    "error": "Security violation",
                    "message": message,
                    "error_code": -32029,
                }
            ),
            status_code,
        )

    def _rate_limit_response(self, start_response) -> List[bytes]:
        """
        Create rate limit exceeded response.

        Args:
            start_response: WSGI start_response callable

        Returns:
            List[bytes]: WSGI response body
        """
        response_data = {
            "error": "Rate limit exceeded",
            "message": "Too many requests, please try again later",
            "error_code": -32030,
        }

        response_body = json.dumps(response_data).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response_body))),
            ("Retry-After", str(self.config.rate_limit.window_size_seconds)),
        ]

        start_response("429 Too Many Requests", headers)
        return [response_body]

    def _auth_error_response(
        self, auth_result: AuthResult, start_response
    ) -> List[bytes]:
        """
        Create authentication error response.

        Args:
            auth_result (AuthResult): Authentication result
            start_response: WSGI start_response callable

        Returns:
            List[bytes]: WSGI response body
        """
        response_data = {
            "error": "Authentication failed",
            "message": auth_result.error_message or "Invalid credentials",
            "error_code": auth_result.error_code,
            "auth_method": auth_result.auth_method,
        }

        response_body = json.dumps(response_data).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response_body))),
            ("WWW-Authenticate", "Bearer, ApiKey"),
        ]

        start_response("401 Unauthorized", headers)
        return [response_body]

    def _permission_error_response(self, start_response) -> List[bytes]:
        """
        Create permission denied response.

        Args:
            start_response: WSGI start_response callable

        Returns:
            List[bytes]: WSGI response body
        """
        response_data = {
            "error": "Permission denied",
            "message": "Insufficient permissions to access this resource",
            "error_code": -32031,
        }

        response_body = json.dumps(response_data).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response_body))),
        ]

        start_response("403 Forbidden", headers)
        return [response_body]

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from Flask request.

        Args:
            request (Request): Flask request object

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

        # Fall back to remote address
        if request.remote_addr:
            return request.remote_addr

        # Default fallback
        # Fallback to default IP from config or environment
        default_ip = getattr(self.config, "default_client_ip", None)
        if default_ip:
            return default_ip

        # Use environment variable or default
        import os

        from ..constants import DEFAULT_CLIENT_IP

        return os.environ.get("DEFAULT_CLIENT_IP", DEFAULT_CLIENT_IP)

    def _get_security_headers(self) -> List[tuple]:
        """
        Get security headers to add to responses.

        Returns:
            List[tuple]: List of (header_name, header_value) tuples
        """
        headers = [
            ("X-Content-Type-Options", "nosniff"),
            ("X-Frame-Options", "DENY"),
            ("X-XSS-Protection", "1; mode=block"),
            ("Strict-Transport-Security", "max-age=31536000; includeSubDomains"),
            ("Content-Security-Policy", "default-src 'self'"),
            ("Referrer-Policy", "strict-origin-when-cross-origin"),
        ]

        # Add custom security headers from config
        if self.config.auth and self.config.auth.security_headers:
            for header_name, header_value in self.config.auth.security_headers.items():
                headers.append((header_name, header_value))

        return headers
