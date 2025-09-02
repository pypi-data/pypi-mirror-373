"""
Flask Security Middleware Tests

This module provides comprehensive unit tests for the FlaskSecurityMiddleware
class and its Flask-specific functionality.

Test Coverage:
- FlaskSecurityMiddleware initialization
- Flask request processing
- Flask authentication methods
- Flask response creation
- Flask error handling
- Flask header management
- Flask rate limiting integration
- Flask-specific request/response handling

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Request, Response

from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.middleware.flask_middleware import (
    FlaskMiddlewareError,
    FlaskSecurityMiddleware,
)
from mcp_security_framework.schemas.config import (
    AuthConfig,
    RateLimitConfig,
    SecurityConfig,
)
from mcp_security_framework.schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    ValidationResult,
    ValidationStatus,
)


class TestFlaskSecurityMiddleware:
    """Test suite for FlaskSecurityMiddleware class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create mock security manager
        self.mock_security_manager = Mock(spec=SecurityManager)
        self.mock_security_manager.config = SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=["api_key", "jwt"],
                public_paths=["/health", "/docs"],
                jwt_secret="test_jwt_secret_key",
            ),
            rate_limit=RateLimitConfig(
                enabled=True, default_requests_per_minute=100, window_size_seconds=60
            ),
        )

        # Create mock auth manager
        self.mock_auth_manager = Mock()
        self.mock_security_manager.auth_manager = self.mock_auth_manager

        # Setup rate_limiter mock
        self.mock_security_manager.rate_limiter = Mock()

        # Create middleware instance
        self.middleware = FlaskSecurityMiddleware(self.mock_security_manager)

    def create_mock_request(
        self, path: str = "/api/test", headers: Dict[str, str] = None
    ) -> Mock:
        """Create a mock Flask request for testing."""
        mock_request = Mock(spec=Request)
        mock_request.path = path
        mock_request.method = "GET"
        mock_request.headers = headers or {}
        mock_request.remote_addr = "127.0.0.1"
        return mock_request

    def create_mock_environ(
        self, path: str = "/api/test", headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create a mock WSGI environ for testing."""
        environ = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": path,
            "QUERY_STRING": "",
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "5000",
            "HTTP_HOST": "localhost:5000",
            "wsgi.url_scheme": "http",
            "wsgi.input": Mock(),
            "wsgi.errors": Mock(),
            "wsgi.version": (1, 0),
            "wsgi.run_once": False,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
        }

        # Add headers to environ
        if headers:
            for key, value in headers.items():
                environ[f'HTTP_{key.upper().replace("-", "_")}'] = value

        return environ

    def test_initialization_success(self):
        """Test successful Flask middleware initialization."""
        assert isinstance(self.middleware, FlaskSecurityMiddleware)
        assert self.middleware.security_manager == self.mock_security_manager
        assert self.middleware.config == self.mock_security_manager.config

    def test_call_success(self):
        """Test successful middleware call."""
        environ = self.create_mock_environ()
        mock_start_response = Mock()

        # Mock successful authentication and authorization
        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        # Mock successful authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.middleware._authenticate_request = Mock(return_value=auth_result)

        self.middleware._validate_permissions = Mock(return_value=True)

        # Mock successful response
        mock_response = [b'{"message": "success"}']
        self.middleware._process_request = Mock(return_value=mock_response)

        result = self.middleware(environ, mock_start_response)

        # Verify middleware processed successfully
        assert result == mock_response
        self.middleware._process_request.assert_called_once()

    def test_call_rate_limit_exceeded(self):
        """Test middleware call with rate limit exceeded."""
        environ = self.create_mock_environ()
        mock_start_response = Mock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = False

        result = self.middleware(environ, mock_start_response)

        # Verify rate limit response
        assert isinstance(result, list)
        assert len(result) == 1
        response_data = json.loads(result[0].decode("utf-8"))
        assert response_data["error"] == "Rate limit exceeded"

        # Verify start_response was called with correct status
        mock_start_response.assert_called_once()
        call_args = mock_start_response.call_args[0]
        assert call_args[0] == "429 Too Many Requests"

    def test_call_public_path(self):
        """Test middleware call with public path."""
        environ = self.create_mock_environ(path="/health")
        mock_start_response = Mock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        # Mock successful response for public path
        mock_response = [b'{"status": "healthy"}']
        self.middleware._process_request = Mock(return_value=mock_response)

        result = self.middleware(environ, mock_start_response)

        # Verify middleware processed successfully for public path
        assert result == mock_response
        self.middleware._process_request.assert_called_once()

    def test_call_authentication_failed(self):
        """Test middleware call with authentication failure."""
        environ = self.create_mock_environ()
        mock_start_response = Mock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        # Mock failed authentication
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY,
            error_code=-32005,
            error_message="Authentication failed",
        )
        self.middleware._authenticate_request = Mock(return_value=auth_result)

        result = self.middleware(environ, mock_start_response)

        # Verify authentication error response
        assert isinstance(result, list)
        assert len(result) == 1
        response_data = json.loads(result[0].decode("utf-8"))
        assert response_data["error"] == "Authentication failed"

        # Verify start_response was called with correct status
        mock_start_response.assert_called_once()
        call_args = mock_start_response.call_args[0]
        assert call_args[0] == "401 Unauthorized"

    def test_call_permission_denied(self):
        """Test middleware call with permission denied."""
        environ = self.create_mock_environ()
        mock_start_response = Mock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        # Mock successful authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.middleware._authenticate_request = Mock(return_value=auth_result)

        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            error_code=-32007,
            error_message="Permission denied",
        )

        # Mock permission error response
        mock_response = [b'{"error": "Permission denied"}']
        self.middleware._process_request = Mock(return_value=mock_response)

        result = self.middleware(environ, mock_start_response)

        # Verify permission error response
        assert result == mock_response
        self.middleware._process_request.assert_called_once()

    def test_get_rate_limit_identifier(self):
        """Test getting rate limit identifier from request."""
        mock_request = self.create_mock_request()
        result = self.middleware._get_rate_limit_identifier(mock_request)
        assert result == "127.0.0.1"

    def test_get_rate_limit_identifier_with_forwarded_for(self):
        """Test getting rate limit identifier with X-Forwarded-For header."""
        headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        mock_request = self.create_mock_request(headers=headers)
        result = self.middleware._get_rate_limit_identifier(mock_request)
        assert result == "192.168.1.1"

    def test_get_rate_limit_identifier_with_real_ip(self):
        """Test getting rate limit identifier with X-Real-IP header."""
        headers = {"X-Real-IP": "192.168.1.100"}
        mock_request = self.create_mock_request(headers=headers)
        result = self.middleware._get_rate_limit_identifier(mock_request)
        assert result == "192.168.1.100"

    def test_get_request_path(self):
        """Test getting request path from Flask request."""
        mock_request = self.create_mock_request(path="/api/users")
        result = self.middleware._get_request_path(mock_request)
        assert result == "/api/users"

    def test_get_required_permissions_from_request(self):
        """Test getting required permissions from request."""
        mock_request = self.create_mock_request()
        mock_request.required_permissions = ["read", "write"]

        result = self.middleware._get_required_permissions(mock_request)
        assert result == ["read", "write"]

    def test_get_required_permissions_default(self):
        """Test getting required permissions when not set."""
        mock_request = self.create_mock_request()
        # Create a clean endpoint mock without any attributes
        mock_endpoint = Mock()
        mock_endpoint.required_permissions = None
        mock_endpoint.required_roles = None
        mock_endpoint.__permissions__ = None
        mock_request.endpoint = mock_endpoint
        result = self.middleware._get_required_permissions(mock_request)
        assert result == []

    def test_try_api_key_auth_success(self):
        """Test successful API key authentication."""
        headers = {"X-API-Key": "valid_key"}
        mock_request = self.create_mock_request(headers=headers)

        expected_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.mock_auth_manager.authenticate_api_key.return_value = expected_result

        result = self.middleware._try_api_key_auth(mock_request)

        assert result == expected_result
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with("valid_key")

    def test_try_api_key_auth_from_authorization_header(self):
        """Test API key authentication from Authorization header."""
        headers = {"Authorization": "Bearer api_key_123"}
        mock_request = self.create_mock_request(headers=headers)

        expected_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.mock_auth_manager.authenticate_api_key.return_value = expected_result

        result = self.middleware._try_api_key_auth(mock_request)

        assert result == expected_result
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with(
            "api_key_123"
        )

    def test_try_api_key_auth_no_key(self):
        """Test API key authentication with no key provided."""
        mock_request = self.create_mock_request()

        result = self.middleware._try_api_key_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32024
        assert "API key not found" in result.error_message

    def test_try_jwt_auth_success(self):
        """Test successful JWT authentication."""
        headers = {"Authorization": "Bearer jwt_token_123"}
        mock_request = self.create_mock_request(headers=headers)

        expected_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.JWT,
        )
        self.mock_auth_manager.authenticate_jwt_token.return_value = expected_result

        result = self.middleware._try_jwt_auth(mock_request)

        assert result == expected_result
        self.mock_auth_manager.authenticate_jwt_token.assert_called_once_with(
            "jwt_token_123"
        )

    def test_try_jwt_auth_no_token(self):
        """Test JWT authentication with no token provided."""
        mock_request = self.create_mock_request()

        result = self.middleware._try_jwt_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32025
        assert "JWT token not found" in result.error_message

    def test_try_jwt_auth_invalid_header(self):
        """Test JWT authentication with invalid Authorization header."""
        headers = {"Authorization": "Invalid jwt_token_123"}
        mock_request = self.create_mock_request(headers=headers)

        result = self.middleware._try_jwt_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32025
        assert "JWT token not found" in result.error_message

    def test_try_certificate_auth_not_implemented(self):
        """Test certificate authentication (not implemented)."""
        mock_request = self.create_mock_request()

        result = self.middleware._try_certificate_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32026
        assert "not implemented" in result.error_message

    def test_try_basic_auth_not_implemented(self):
        """Test basic authentication (not implemented)."""
        mock_request = self.create_mock_request()

        result = self.middleware._try_basic_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32027
        assert "Basic authentication credentials not found" in result.error_message

    def test_try_auth_method_unsupported(self):
        """Test authentication with unsupported method."""
        mock_request = self.create_mock_request()

        result = self.middleware._try_auth_method(mock_request, "unsupported_method")

        assert result.is_valid is False
        assert result.error_code == -32022
        assert "Unsupported authentication method" in result.error_message

    def test_apply_security_headers(self):
        """Test applying security headers to Flask response."""
        mock_response = Mock(spec=Response)
        mock_response.headers = {}

        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }

        self.middleware._apply_security_headers(mock_response, headers)

        assert mock_response.headers["X-Content-Type-Options"] == "nosniff"
        assert mock_response.headers["X-Frame-Options"] == "DENY"
        assert mock_response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_create_error_response(self):
        """Test creating error response."""
        from flask import Flask

        app = Flask(__name__)

        with app.app_context():
            result = self.middleware._create_error_response(400, "Bad request")

            assert isinstance(result, Response)
            assert result.status_code == 400
            response_data = json.loads(result.get_data(as_text=True))
            assert response_data["error"] == "Security violation"
            assert response_data["message"] == "Bad request"

    def test_rate_limit_response(self):
        """Test creating rate limit response."""
        mock_start_response = Mock()

        result = self.middleware._rate_limit_response(mock_start_response)

        assert isinstance(result, list)
        assert len(result) == 1
        response_data = json.loads(result[0].decode("utf-8"))
        assert response_data["error"] == "Rate limit exceeded"

        # Verify start_response was called
        mock_start_response.assert_called_once()
        call_args = mock_start_response.call_args[0]
        assert call_args[0] == "429 Too Many Requests"

        # Check for Retry-After header
        headers = call_args[1]
        retry_after_header = next((h for h in headers if h[0] == "Retry-After"), None)
        assert retry_after_header is not None
        assert retry_after_header[1] == "60"

    def test_auth_error_response(self):
        """Test creating authentication error response."""
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY,
            error_code=-32005,
            error_message="Invalid API key",
        )

        mock_start_response = Mock()
        result = self.middleware._auth_error_response(auth_result, mock_start_response)

        assert isinstance(result, list)
        assert len(result) == 1
        response_data = json.loads(result[0].decode("utf-8"))
        assert response_data["error"] == "Authentication failed"
        assert response_data["message"] == "Invalid API key"

        # Verify start_response was called
        mock_start_response.assert_called_once()
        call_args = mock_start_response.call_args[0]
        assert call_args[0] == "401 Unauthorized"

        # Check for WWW-Authenticate header
        headers = call_args[1]
        www_auth_header = next((h for h in headers if h[0] == "WWW-Authenticate"), None)
        assert www_auth_header is not None
        assert www_auth_header[1] == "Bearer, ApiKey"

    def test_permission_error_response(self):
        """Test creating permission error response."""
        mock_start_response = Mock()

        result = self.middleware._permission_error_response(mock_start_response)

        assert isinstance(result, list)
        assert len(result) == 1
        response_data = json.loads(result[0].decode("utf-8"))
        assert response_data["error"] == "Permission denied"
        assert (
            response_data["message"]
            == "Insufficient permissions to access this resource"
        )

        # Verify start_response was called
        mock_start_response.assert_called_once()
        call_args = mock_start_response.call_args[0]
        assert call_args[0] == "403 Forbidden"

    def test_get_client_ip_from_forwarded_for(self):
        """Test getting client IP from X-Forwarded-For header."""
        headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        mock_request = self.create_mock_request(headers=headers)

        result = self.middleware._get_client_ip(mock_request)
        assert result == "192.168.1.1"

    def test_get_client_ip_from_real_ip(self):
        """Test getting client IP from X-Real-IP header."""
        headers = {"X-Real-IP": "192.168.1.100"}
        mock_request = self.create_mock_request(headers=headers)

        result = self.middleware._get_client_ip(mock_request)
        assert result == "192.168.1.100"

    def test_get_client_ip_from_remote_addr(self):
        """Test getting client IP from remote_addr."""
        mock_request = self.create_mock_request()
        mock_request.remote_addr = "192.168.1.50"

        result = self.middleware._get_client_ip(mock_request)
        assert result == "192.168.1.50"

    def test_get_client_ip_fallback(self):
        """Test getting client IP with fallback."""
        mock_request = self.create_mock_request()
        mock_request.remote_addr = None

        result = self.middleware._get_client_ip(mock_request)
        assert result == "127.0.0.1"

    def test_get_security_headers(self):
        """Test getting security headers."""
        result = self.middleware._get_security_headers()

        assert isinstance(result, list)
        assert all(isinstance(header, tuple) and len(header) == 2 for header in result)

        # Check for standard security headers
        header_names = [header[0] for header in result]
        assert "X-Content-Type-Options" in header_names
        assert "X-Frame-Options" in header_names
        assert "X-XSS-Protection" in header_names
        assert "Strict-Transport-Security" in header_names
        assert "Content-Security-Policy" in header_names
        assert "Referrer-Policy" in header_names

    def test_get_security_headers_with_custom_headers(self):
        """Test getting security headers with custom headers from config."""
        self.mock_security_manager.config.auth.security_headers = {
            "Custom-Security-Header": "custom_value"
        }

        result = self.middleware._get_security_headers()

        header_names = [header[0] for header in result]
        assert "Custom-Security-Header" in header_names

        custom_header = next(h for h in result if h[0] == "Custom-Security-Header")
        assert custom_header[1] == "custom_value"

    def test_call_with_exception(self):
        """Test middleware call with exception."""
        environ = self.create_mock_environ()
        mock_start_response = Mock()

        # Mock an exception during processing
        self.mock_security_manager.rate_limiter.check_rate_limit.side_effect = (
            Exception("Test error")
        )

        with pytest.raises(FlaskMiddlewareError) as exc_info:
            self.middleware(environ, mock_start_response)

        assert "Middleware processing failed" in str(exc_info.value)
        assert exc_info.value.error_code == -32003
