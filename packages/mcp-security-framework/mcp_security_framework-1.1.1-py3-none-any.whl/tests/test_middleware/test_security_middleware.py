"""
Security Middleware Tests

This module provides comprehensive unit tests for the base SecurityMiddleware
class and its abstract methods.

Test Coverage:
- SecurityMiddleware initialization and configuration
- Rate limiting functionality
- Authentication process
- Permission validation
- Public path checking
- Security headers management
- Error handling and logging
- Abstract method validation

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.middleware.security_middleware import (
    SecurityMiddleware,
    SecurityMiddlewareError,
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


class MockSecurityMiddleware(SecurityMiddleware):
    """
    Mock implementation of SecurityMiddleware for testing.

    This class implements all abstract methods to allow testing
    of the base SecurityMiddleware functionality.
    """

    def __call__(self, request: Any, call_next: Any) -> Any:
        """Mock implementation of __call__ method."""
        # Check rate limit
        if not self._check_rate_limit(request):
            return self._create_error_response(429, "Rate limit exceeded")

        # Check if public path
        if self._is_public_path(request):
            response = call_next(request)
            self._add_security_headers(response)
            return response

        # Authenticate request
        auth_result = self._authenticate_request(request)
        if not auth_result.is_valid:
            return self._create_error_response(401, "Authentication failed")

        # Validate permissions
        if not self._validate_permissions(request, auth_result):
            return self._create_error_response(403, "Permission denied")

        # Process request
        response = call_next(request)
        self._add_security_headers(response)
        return response

    def _get_rate_limit_identifier(self, request: Any) -> str:
        """Mock implementation to get rate limit identifier."""
        return getattr(request, "client_ip", "127.0.0.1")

    def _get_request_path(self, request: Any) -> str:
        """Mock implementation to get request path."""
        return getattr(request, "path", "/")

    def _get_required_permissions(self, request: Any) -> List[str]:
        """Mock implementation to get required permissions."""
        return getattr(request, "required_permissions", [])

    def _try_auth_method(self, request: Any, method: str) -> AuthResult:
        """Mock implementation to try authentication method."""
        if method == "api_key":
            api_key = getattr(request, "api_key", None)
            if api_key == "valid_key":
                return AuthResult(
                    is_valid=True,
                    status=AuthStatus.SUCCESS,
                    username="test_user",
                    roles=["user"],
                    auth_method=AuthMethod.API_KEY,
                )
        return AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY if method == "api_key" else None,
            error_code=-32005,
            error_message="Authentication failed",
        )

    def _apply_security_headers(self, response: Any, headers: Dict[str, str]) -> None:
        """Mock implementation to apply security headers."""
        if hasattr(response, "headers"):
            response.headers.update(headers)

    def _create_error_response(self, status_code: int, message: str) -> Any:
        """Mock implementation to create error response."""
        response = Mock()
        response.status_code = status_code
        response.body = message
        return response


class TestSecurityMiddleware:
    """Test suite for SecurityMiddleware class."""

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

        # Setup rate_limiter mock
        self.mock_security_manager.rate_limiter = Mock()

        # Create mock request
        self.mock_request = Mock()
        self.mock_request.client_ip = "127.0.0.1"
        self.mock_request.path = "/api/test"
        self.mock_request.required_permissions = ["read"]

        # Create middleware instance
        self.middleware = MockSecurityMiddleware(self.mock_security_manager)

    def test_initialization_success(self):
        """Test successful middleware initialization."""
        assert self.middleware.security_manager == self.mock_security_manager
        assert self.middleware.config == self.mock_security_manager.config
        assert len(self.middleware._public_paths) == 2
        assert "/health" in self.middleware._public_paths
        assert "/docs" in self.middleware._public_paths

    def test_initialization_invalid_security_manager(self):
        """Test initialization with invalid security manager."""
        with pytest.raises(SecurityMiddlewareError) as exc_info:
            MockSecurityMiddleware("invalid_manager")

        assert "Invalid security manager" in str(exc_info.value)
        assert exc_info.value.error_code == -32003

    def test_check_rate_limit_disabled(self):
        """Test rate limiting when disabled."""
        self.mock_security_manager.config.rate_limit.enabled = False
        result = self.middleware._check_rate_limit(self.mock_request)
        assert result is True

    def test_check_rate_limit_enabled_success(self):
        """Test successful rate limit check."""
        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True
        result = self.middleware._check_rate_limit(self.mock_request)
        assert result is True
        self.mock_security_manager.rate_limiter.check_rate_limit.assert_called_once_with(
            "127.0.0.1"
        )

    def test_check_rate_limit_enabled_exceeded(self):
        """Test rate limit exceeded."""
        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = False
        result = self.middleware._check_rate_limit(self.mock_request)
        assert result is False

    def test_check_rate_limit_no_identifier(self):
        """Test rate limiting with no identifier."""
        self.mock_request.client_ip = None
        result = self.middleware._check_rate_limit(self.mock_request)
        assert result is True

    def test_check_rate_limit_exception(self):
        """Test rate limiting with exception."""
        self.mock_security_manager.rate_limiter.check_rate_limit.side_effect = (
            Exception("Rate limit error")
        )

        with pytest.raises(SecurityMiddlewareError) as exc_info:
            self.middleware._check_rate_limit(self.mock_request)

        assert "Rate limit check failed" in str(exc_info.value)
        assert exc_info.value.error_code == -32004

    def test_authenticate_request_disabled(self):
        """Test authentication when disabled."""
        self.mock_security_manager.config.auth.enabled = False
        result = self.middleware._authenticate_request(self.mock_request)

        assert result.is_valid is True
        assert result.status == AuthStatus.SUCCESS
        assert result.username == "anonymous"
        assert result.auth_method is None

    def test_authenticate_request_success(self):
        """Test successful authentication."""
        self.mock_request.api_key = "valid_key"
        result = self.middleware._authenticate_request(self.mock_request)

        assert result.is_valid is True
        assert result.username == "test_user"
        assert result.auth_method == "api_key"
        assert result.roles == ["user"]

    def test_authenticate_request_failure(self):
        """Test authentication failure."""
        self.mock_request.api_key = "invalid_key"
        result = self.middleware._authenticate_request(self.mock_request)

        assert result.is_valid is False
        assert result.error_code == -32005
        assert "All authentication methods failed" in result.error_message

    def test_authenticate_request_exception(self):
        """Test authentication with exception."""
        # Mock security manager to raise exception
        self.mock_security_manager.authenticate_user.side_effect = Exception(
            "Authentication error"
        )

        result = self.middleware._authenticate_request(self.mock_request)

        # Should handle exception gracefully
        assert result.is_valid is False
        assert result.error_code == -32005
        assert "All authentication methods failed" in result.error_message

    def test_validate_permissions_success(self):
        """Test successful permission validation."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["admin"],
            auth_method=AuthMethod.API_KEY,
        )

        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=True, status=ValidationStatus.VALID
        )

        result = self.middleware._validate_permissions(self.mock_request, auth_result)
        assert result is True

    def test_validate_permissions_failure(self):
        """Test permission validation failure."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )

        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            error_code=-32007,
            error_message="Insufficient permissions",
        )

        result = self.middleware._validate_permissions(self.mock_request, auth_result)
        assert result is False

    def test_validate_permissions_no_auth(self):
        """Test permission validation with invalid auth."""
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=None,
            error_code=-32005,
            error_message="Authentication failed",
        )

        result = self.middleware._validate_permissions(self.mock_request, auth_result)
        assert result is False

    def test_validate_permissions_no_required_permissions(self):
        """Test permission validation with no required permissions."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )

        self.mock_request.required_permissions = []
        result = self.middleware._validate_permissions(self.mock_request, auth_result)
        assert result is True

    def test_validate_permissions_exception(self):
        """Test permission validation with exception."""
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )

        self.mock_security_manager.check_permissions.side_effect = Exception(
            "Permission error"
        )

        with pytest.raises(SecurityMiddlewareError) as exc_info:
            self.middleware._validate_permissions(self.mock_request, auth_result)

        assert "Permission validation failed" in str(exc_info.value)
        assert exc_info.value.error_code == -32007

    def test_is_public_path_true(self):
        """Test public path check returning True."""
        self.mock_request.path = "/health"
        result = self.middleware._is_public_path(self.mock_request)
        assert result is True

    def test_is_public_path_false(self):
        """Test public path check returning False."""
        self.mock_request.path = "/api/private"
        result = self.middleware._is_public_path(self.mock_request)
        assert result is False

    def test_is_public_path_no_path(self):
        """Test public path check with no path."""
        self.mock_request.path = None
        result = self.middleware._is_public_path(self.mock_request)
        assert result is False

    def test_is_public_path_exception(self):
        """Test public path check with exception."""
        self.mock_request.path = Exception("Path error")
        result = self.middleware._is_public_path(self.mock_request)
        assert result is False

    def test_add_security_headers_success(self):
        """Test adding security headers successfully."""
        mock_response = Mock()
        mock_response.headers = {}

        self.middleware._add_security_headers(mock_response)

        # Check that standard security headers were added
        assert "X-Content-Type-Options" in mock_response.headers
        assert "X-Frame-Options" in mock_response.headers
        assert "X-XSS-Protection" in mock_response.headers

    def test_add_security_headers_with_custom_headers(self):
        """Test adding security headers with custom headers from config."""
        self.mock_security_manager.config.auth.security_headers = {
            "Custom-Security-Header": "custom_value"
        }

        mock_response = Mock()
        mock_response.headers = {}

        self.middleware._add_security_headers(mock_response)

        assert "Custom-Security-Header" in mock_response.headers
        assert mock_response.headers["Custom-Security-Header"] == "custom_value"

    def test_add_security_headers_exception(self):
        """Test adding security headers with exception."""
        mock_response = Mock()
        mock_response.headers = Exception("Header error")

        # Should not raise exception, just log error
        self.middleware._add_security_headers(mock_response)

    def test_log_security_event_success(self):
        """Test logging security event successfully."""
        details = {
            "timestamp": "2024-01-01T00:00:00Z",
            "ip_address": "127.0.0.1",
            "username": "test_user",
            "path": "/api/test",
            "method": "GET",
        }

        with patch.object(self.middleware.logger, "info") as mock_logger:
            self.middleware._log_security_event("test_event", details)
            mock_logger.assert_called_once()

    def test_log_security_event_exception(self):
        """Test logging security event with exception."""
        details = Exception("Event error")

        # Should not raise exception, just log error
        self.middleware._log_security_event("test_event", details)

    def test_middleware_call_success(self):
        """Test successful middleware call."""
        mock_call_next = Mock()
        mock_response = Mock()
        mock_response.headers = {}
        mock_call_next.return_value = mock_response

        self.mock_request.api_key = "valid_key"
        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True
        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=True, status=ValidationStatus.VALID
        )

        result = self.middleware(self.mock_request, mock_call_next)

        assert result == mock_response
        mock_call_next.assert_called_once_with(self.mock_request)

    def test_middleware_call_rate_limit_exceeded(self):
        """Test middleware call with rate limit exceeded."""
        mock_call_next = Mock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = False

        result = self.middleware(self.mock_request, mock_call_next)

        assert result.status_code == 429
        assert "Rate limit exceeded" in result.body
        mock_call_next.assert_not_called()

    def test_middleware_call_public_path(self):
        """Test middleware call with public path."""
        mock_call_next = Mock()
        mock_response = Mock()
        mock_response.headers = {}
        mock_call_next.return_value = mock_response

        self.mock_request.path = "/health"
        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        result = self.middleware(self.mock_request, mock_call_next)

        assert result == mock_response
        mock_call_next.assert_called_once_with(self.mock_request)

    def test_middleware_call_authentication_failed(self):
        """Test middleware call with authentication failure."""
        mock_call_next = Mock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True
        self.mock_request.api_key = "invalid_key"

        result = self.middleware(self.mock_request, mock_call_next)

        assert result.status_code == 401
        assert "Authentication failed" in result.body
        mock_call_next.assert_not_called()

    def test_middleware_call_permission_denied(self):
        """Test middleware call with permission denied."""
        mock_call_next = Mock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True
        self.mock_request.api_key = "valid_key"
        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            error_code=-32007,
            error_message="Permission denied",
        )

        result = self.middleware(self.mock_request, mock_call_next)

        assert result.status_code == 403
        assert "Permission denied" in result.body
        mock_call_next.assert_not_called()

    def test_abstract_methods_validation(self):
        """Test that abstract methods are properly defined."""
        # Verify that all abstract methods are defined in the base class
        abstract_methods = [
            "_get_rate_limit_identifier",
            "_get_request_path",
            "_get_required_permissions",
            "_try_auth_method",
            "_apply_security_headers",
            "_create_error_response",
        ]

        for method_name in abstract_methods:
            assert hasattr(SecurityMiddleware, method_name)
            method = getattr(SecurityMiddleware, method_name)
            assert hasattr(method, "__isabstractmethod__")
            assert method.__isabstractmethod__ is True
