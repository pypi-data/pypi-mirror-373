"""
FastAPI Security Middleware Tests

This module provides comprehensive unit tests for the FastAPISecurityMiddleware
class and its FastAPI-specific functionality.

Test Coverage:
- FastAPISecurityMiddleware initialization
- FastAPI request processing
- FastAPI authentication methods
- FastAPI response creation
- FastAPI error handling
- FastAPI header management
- FastAPI rate limiting integration
- FastAPI-specific request/response handling

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.middleware.fastapi_middleware import (
    FastAPIMiddlewareError,
    FastAPISecurityMiddleware,
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


class TestFastAPISecurityMiddleware:
    """Test suite for FastAPISecurityMiddleware class."""

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
        self.middleware = FastAPISecurityMiddleware(self.mock_security_manager)

    def create_mock_request(
        self, path: str = "/api/test", headers: Dict[str, str] = None
    ) -> Mock:
        """Create a mock FastAPI request for testing."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = path
        mock_request.method = "GET"
        mock_request.headers = headers or {}
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        return mock_request

    def test_initialization_success(self):
        """Test successful FastAPI middleware initialization."""
        assert isinstance(self.middleware, FastAPISecurityMiddleware)
        assert self.middleware.security_manager == self.mock_security_manager
        assert self.middleware.config == self.mock_security_manager.config

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Test successful middleware call."""
        mock_request = self.create_mock_request()
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_call_next.return_value = mock_response

        # Mock successful authentication and authorization
        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        # Mock the _authenticate_request method directly
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.middleware._authenticate_request = AsyncMock(return_value=auth_result)

        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=True, status=ValidationStatus.VALID
        )

        result = await self.middleware(mock_request, mock_call_next)

        assert result == mock_response
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_call_rate_limit_exceeded(self):
        """Test middleware call with rate limit exceeded."""
        mock_request = self.create_mock_request()
        mock_call_next = AsyncMock()

        # Mock _is_public_path to return False so rate limiting is checked
        self.middleware._is_public_path = Mock(return_value=False)
        # Mock the security manager's check_rate_limit method
        self.mock_security_manager.check_rate_limit.return_value = False

        result = await self.middleware(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in result.body.decode()
        mock_call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_call_public_path(self):
        """Test middleware call with public path."""
        mock_request = self.create_mock_request(path="/health")
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_call_next.return_value = mock_response

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        result = await self.middleware(mock_request, mock_call_next)

        assert result == mock_response
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_call_authentication_failed(self):
        """Test middleware call with authentication failure."""
        mock_request = self.create_mock_request()
        mock_call_next = AsyncMock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True
        self.mock_auth_manager.authenticate_api_key.return_value = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY,
            error_code=-32005,
            error_message="Authentication failed",
        )

        result = await self.middleware(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication failed" in result.body.decode()
        mock_call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_call_permission_denied(self):
        """Test middleware call with permission denied."""
        mock_request = self.create_mock_request()
        mock_call_next = AsyncMock()

        self.mock_security_manager.rate_limiter.check_rate_limit.return_value = True

        # Mock successful authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.middleware._authenticate_request = AsyncMock(return_value=auth_result)

        # Mock the _validate_permissions method directly
        self.middleware._validate_permissions = Mock(return_value=False)

        result = await self.middleware(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == status.HTTP_403_FORBIDDEN
        assert "Permission denied" in result.body.decode()
        mock_call_next.assert_not_called()

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
        """Test getting request path from FastAPI request."""
        mock_request = self.create_mock_request(path="/api/users")
        result = self.middleware._get_request_path(mock_request)
        assert result == "/api/users"

    def test_get_required_permissions_from_state(self):
        """Test getting required permissions from request state."""
        mock_request = self.create_mock_request()
        mock_request.state.required_permissions = ["read", "write"]

        result = self.middleware._get_required_permissions(mock_request)
        assert result == ["read", "write"]

    def test_get_required_permissions_default(self):
        """Test getting required permissions when not set."""
        mock_request = self.create_mock_request()
        # Ensure state doesn't have required_permissions
        if hasattr(mock_request, "state"):
            delattr(mock_request.state, "required_permissions")
        result = self.middleware._get_required_permissions(mock_request)
        assert result == []

    @pytest.mark.asyncio
    async def test_try_api_key_auth_success(self):
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

        result = await self.middleware._try_api_key_auth(mock_request)

        assert result == expected_result
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with("valid_key")

    @pytest.mark.asyncio
    async def test_try_api_key_auth_from_authorization_header(self):
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

        result = await self.middleware._try_api_key_auth(mock_request)

        assert result == expected_result
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with(
            "api_key_123"
        )

    @pytest.mark.asyncio
    async def test_try_api_key_auth_no_key(self):
        """Test API key authentication with no key provided."""
        mock_request = self.create_mock_request()

        result = await self.middleware._try_api_key_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32012
        assert "API key not found" in result.error_message

    @pytest.mark.asyncio
    async def test_try_jwt_auth_success(self):
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

        result = await self.middleware._try_jwt_auth(mock_request)

        assert result == expected_result
        self.mock_auth_manager.authenticate_jwt_token.assert_called_once_with(
            "jwt_token_123"
        )

    @pytest.mark.asyncio
    async def test_try_jwt_auth_no_token(self):
        """Test JWT authentication with no token provided."""
        mock_request = self.create_mock_request()

        result = await self.middleware._try_jwt_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32013
        assert "JWT token not found" in result.error_message

    @pytest.mark.asyncio
    async def test_try_jwt_auth_invalid_header(self):
        """Test JWT authentication with invalid Authorization header."""
        headers = {"Authorization": "Invalid jwt_token_123"}
        mock_request = self.create_mock_request(headers=headers)

        result = await self.middleware._try_jwt_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32013
        assert "JWT token not found" in result.error_message

    @pytest.mark.asyncio
    async def test_try_certificate_auth_not_implemented(self):
        """Test certificate authentication (not implemented)."""
        mock_request = self.create_mock_request()

        result = await self.middleware._try_certificate_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32014
        assert "not implemented" in result.error_message

    @pytest.mark.asyncio
    async def test_try_basic_auth_not_implemented(self):
        """Test basic authentication (not implemented)."""
        mock_request = self.create_mock_request()

        result = await self.middleware._try_basic_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32015
        assert "not found" in result.error_message

    @pytest.mark.asyncio
    async def test_try_auth_method_unsupported(self):
        """Test authentication with unsupported method."""
        mock_request = self.create_mock_request()

        result = await self.middleware._try_auth_method(
            mock_request, "unsupported_method"
        )

        assert result.is_valid is False
        assert result.error_code == -32010
        assert "Unsupported authentication method" in result.error_message

    def test_apply_security_headers(self):
        """Test applying security headers to FastAPI response."""
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
        result = self.middleware._create_error_response(400, "Bad request")

        assert isinstance(result, JSONResponse)
        assert result.status_code == 400
        assert "Security violation" in result.body.decode()
        assert "Bad request" in result.body.decode()

    def test_rate_limit_response(self):
        """Test creating rate limit response."""
        result = self.middleware._rate_limit_response()

        assert isinstance(result, JSONResponse)
        assert result.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in result.body.decode()
        assert "Retry-After" in result.headers

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

        result = self.middleware._auth_error_response(auth_result)

        assert isinstance(result, JSONResponse)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication failed" in result.body.decode()
        assert "Invalid API key" in result.body.decode()
        assert "WWW-Authenticate" in result.headers

    def test_permission_error_response(self):
        """Test creating permission error response."""
        result = self.middleware._permission_error_response()

        assert isinstance(result, JSONResponse)
        assert result.status_code == status.HTTP_403_FORBIDDEN
        assert "Permission denied" in result.body.decode()
        assert "Insufficient permissions" in result.body.decode()

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

    def test_get_client_ip_from_client_host(self):
        """Test getting client IP from client host."""
        mock_request = self.create_mock_request()
        mock_request.client.host = "192.168.1.50"

        result = self.middleware._get_client_ip(mock_request)
        assert result == "192.168.1.50"

    def test_get_client_ip_fallback(self):
        """Test getting client IP with fallback."""
        mock_request = self.create_mock_request()
        mock_request.client = None

        result = self.middleware._get_client_ip(mock_request)
        assert result == "127.0.0.1"

    @pytest.mark.asyncio
    async def test_call_with_http_exception(self):
        """Test middleware call that raises HTTPException."""
        mock_request = self.create_mock_request()
        mock_call_next = AsyncMock()
        mock_call_next.side_effect = HTTPException(
            status_code=500, detail="Internal error"
        )

        # Mock successful authentication to reach call_next
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.middleware._authenticate_request = AsyncMock(return_value=auth_result)
        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=True, status=ValidationStatus.VALID
        )

        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(mock_request, mock_call_next)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal error"

    @pytest.mark.asyncio
    async def test_call_with_general_exception(self):
        """Test middleware call with general exception."""
        mock_request = self.create_mock_request()
        mock_call_next = AsyncMock()
        mock_call_next.side_effect = Exception("General error")

        # Mock successful authentication to reach call_next
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="test_user",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.middleware._authenticate_request = AsyncMock(return_value=auth_result)
        self.mock_security_manager.check_permissions.return_value = ValidationResult(
            is_valid=True, status=ValidationStatus.VALID
        )

        with pytest.raises(FastAPIMiddlewareError) as exc_info:
            await self.middleware(mock_request, mock_call_next)

        assert "Middleware processing failed" in str(exc_info.value)
        assert exc_info.value.error_code == -32003
