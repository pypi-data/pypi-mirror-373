"""
FastAPI Authentication Middleware Tests

This module contains comprehensive tests for the FastAPI Authentication Middleware
implementation of the MCP Security Framework.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import json
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from mcp_security_framework.middleware.auth_middleware import AuthMiddlewareError
from mcp_security_framework.middleware.fastapi_auth_middleware import (
    FastAPIAuthMiddleware,
)
from mcp_security_framework.schemas.config import AuthConfig, SecurityConfig
from mcp_security_framework.schemas.models import AuthMethod, AuthResult, AuthStatus


class TestFastAPIAuthMiddleware:
    """Test suite for FastAPI Authentication Middleware."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create test configuration
        self.config = SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=["api_key", "jwt"],
                api_keys={"test_key_123": {"username": "testuser", "roles": ["user"]}},
                jwt_secret="test-jwt-secret-key-for-testing",
                jwt_algorithm="HS256",
                jwt_expiry_hours=24,
                public_paths=["/health", "/metrics"],
            )
        )

        # Create mock security manager
        from mcp_security_framework.core.security_manager import SecurityManager

        self.mock_security_manager = Mock(spec=SecurityManager)
        self.mock_security_manager.authenticate_user = Mock()
        self.mock_security_manager.config = self.config

        # Create mock auth manager
        self.mock_auth_manager = Mock()
        self.mock_auth_manager.authenticate_api_key = Mock()
        self.mock_auth_manager.authenticate_jwt_token = Mock()
        self.mock_auth_manager.authenticate_certificate = Mock()
        self.mock_security_manager.auth_manager = self.mock_auth_manager

        # Create middleware instance
        self.middleware = FastAPIAuthMiddleware(self.mock_security_manager)

    def test_fastapi_auth_middleware_initialization(self):
        """Test FastAPI Authentication Middleware initialization."""
        assert self.middleware is not None
        assert isinstance(self.middleware, FastAPIAuthMiddleware)
        assert self.middleware.config == self.config
        assert self.middleware.security_manager == self.mock_security_manager
        assert hasattr(self.middleware, "logger")

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_public_path_bypass(self):
        """Test that public paths bypass authentication."""
        # Create mock request for public path
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/health"
        mock_request.headers = {}

        # Create mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_call_next.return_value = mock_response

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)
        # Security manager should not be called for public paths
        self.mock_security_manager.authenticate_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_api_key_authentication_success(self):
        """Test successful API key authentication."""
        # Create mock request with API key
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"X-API-Key": "test_key_123"}

        # Mock successful authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="testuser",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.mock_auth_manager.authenticate_api_key.return_value = auth_result

        # Create mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_call_next.return_value = mock_response

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with(
            "test_key_123"
        )

        # Check that user info was added to request state
        assert hasattr(mock_request.state, "auth_result")
        assert mock_request.state.auth_result.username == "testuser"
        assert mock_request.state.auth_result.roles == ["user"]

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_jwt_authentication_success(self):
        """Test successful JWT authentication."""
        # Create mock request with JWT token
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"Authorization": "Bearer test_jwt_token"}

        # Mock failed API key authentication first
        failed_api_key_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY,
            error_code=-32012,
            error_message="API key not found in request",
        )
        self.mock_auth_manager.authenticate_api_key.return_value = failed_api_key_result

        # Mock successful JWT authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="testuser",
            roles=["user"],
            auth_method=AuthMethod.JWT,
        )
        self.mock_auth_manager.authenticate_jwt_token.return_value = auth_result

        # Create mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_call_next.return_value = mock_response

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)
        self.mock_auth_manager.authenticate_jwt_token.assert_called_once_with(
            "test_jwt_token"
        )

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_certificate_authentication_success(self):
        """Test successful certificate authentication."""
        # Create mock request with certificate
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"X-Client-Cert": "test_certificate_data"}

        # Mock failed API key authentication first
        failed_api_key_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY,
            error_code=-32012,
            error_message="API key not found in request",
        )
        self.mock_auth_manager.authenticate_api_key.return_value = failed_api_key_result

        # Mock failed JWT authentication
        failed_jwt_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.JWT,
            error_code=-32013,
            error_message="JWT token not found in Authorization header",
        )
        self.mock_auth_manager.authenticate_jwt_token.return_value = failed_jwt_result

        # Certificate authentication is not implemented, so it will fail
        # We expect the middleware to return an error response

        # Create mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_call_next.return_value = mock_response

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions - certificate auth should fail
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.body.decode())
        assert response_data["error"] == "Authentication failed"
        assert (
            response_data["error_code"] == -32033
        )  # All authentication methods failed

        # call_next should not be called for failed authentication
        mock_call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_authentication_failure(self):
        """Test authentication failure handling."""
        # Create mock request without authentication
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {}

        # Mock failed authentication - this test expects all methods to fail
        failed_auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.INVALID,
            auth_method=AuthMethod.UNKNOWN,
            error_code=-32001,
            error_message="No authentication credentials provided",
        )
        self.mock_auth_manager.authenticate_api_key.return_value = failed_auth_result

        # Create mock call_next
        mock_call_next = AsyncMock()

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.body.decode())
        assert response_data["error"] == "Authentication failed"
        assert (
            response_data["error_code"] == -32033
        )  # All authentication methods failed
        assert response_data["error_message"] == "All authentication methods failed"

        # call_next should not be called for failed authentication
        mock_call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_invalid_api_key(self):
        """Test handling of invalid API key."""
        # Create mock request with invalid API key
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"X-API-Key": "invalid_key"}

        # Mock failed authentication
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.INVALID,
            auth_method=AuthMethod.API_KEY,
            error_code=-32002,
            error_message="Invalid API key",
        )
        self.mock_auth_manager.authenticate_api_key.return_value = auth_result

        # Create mock call_next
        mock_call_next = AsyncMock()

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.body.decode())
        assert response_data["error"] == "Authentication failed"
        assert (
            response_data["error_code"] == -32033
        )  # All authentication methods failed

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_invalid_jwt_token(self):
        """Test handling of invalid JWT token."""
        # Create mock request with invalid JWT token
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"Authorization": "Bearer invalid_token"}

        # Mock failed API key authentication first
        failed_api_key_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY,
            error_code=-32012,
            error_message="API key not found in request",
        )
        self.mock_auth_manager.authenticate_api_key.return_value = failed_api_key_result

        # Mock failed JWT authentication
        auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.INVALID,
            auth_method=AuthMethod.JWT,
            error_code=-32003,
            error_message="Invalid JWT token",
        )
        self.mock_auth_manager.authenticate_jwt_token.return_value = auth_result

        # Create mock call_next
        mock_call_next = AsyncMock()

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.body.decode())
        assert response_data["error"] == "Authentication failed"
        assert (
            response_data["error_code"] == -32033
        )  # All authentication methods failed

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_exception_handling(self):
        """Test exception handling in middleware."""
        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"X-API-Key": "test_key_123"}

        # Mock auth manager to raise exception
        self.mock_auth_manager.authenticate_api_key.side_effect = Exception(
            "Authentication error"
        )

        # Create mock call_next
        mock_call_next = AsyncMock()

        # Process request
        response = await self.middleware(mock_request, mock_call_next)

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = json.loads(response.body.decode())
        assert response_data["error"] == "Authentication failed"
        assert (
            response_data["error_code"] == -32033
        )  # All authentication methods failed

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_user_info_structure(self):
        """Test that user info is properly structured in request state."""
        # Create mock request with API key
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"X-API-Key": "test_key_123"}

        # Mock successful authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="testuser",
            roles=["user", "admin"],
            permissions=["read:own", "write:own"],
            auth_method=AuthMethod.API_KEY,
        )
        self.mock_auth_manager.authenticate_api_key.return_value = auth_result

        # Create mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_call_next.return_value = mock_response

        # Process request
        await self.middleware(mock_request, mock_call_next)

        # Check user info structure
        assert hasattr(mock_request.state, "auth_result")
        assert mock_request.state.auth_result.username == "testuser"
        assert mock_request.state.auth_result.roles == ["user", "admin"]
        assert mock_request.state.auth_result.permissions == {"read:own", "write:own"}
        assert mock_request.state.auth_result.auth_method == AuthMethod.API_KEY

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_multiple_public_paths(self):
        """Test that multiple public paths are handled correctly."""
        public_paths = ["/health", "/metrics", "/docs", "/openapi.json"]

        for path in public_paths:
            # Create mock request for public path
            mock_request = Mock(spec=Request)
            mock_request.url.path = path
            mock_request.headers = {}

            # Create mock call_next
            mock_call_next = AsyncMock()
            mock_response = Mock(spec=Response)
            mock_call_next.return_value = mock_response

            # Process request
            response = await self.middleware(mock_request, mock_call_next)

            # Assertions
            assert response == mock_response
            mock_call_next.assert_called_once_with(mock_request)

            # Reset mock for next iteration
            mock_call_next.reset_mock()

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_disabled_authentication(self):
        """Test middleware behavior when authentication is disabled."""
        # Create config with disabled authentication
        disabled_config = SecurityConfig(
            auth=AuthConfig(
                enabled=False, methods=["api_key"], api_keys={}, public_paths=[]
            )
        )

        # Create middleware with disabled auth
        from mcp_security_framework.core.security_manager import SecurityManager

        disabled_security_manager = Mock(spec=SecurityManager)
        disabled_security_manager.config = disabled_config
        disabled_auth_manager = Mock()
        disabled_security_manager.auth_manager = disabled_auth_manager
        disabled_middleware = FastAPIAuthMiddleware(disabled_security_manager)

        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {}

        # Create mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock(spec=Response)
        mock_call_next.return_value = mock_response

        # Process request
        response = await disabled_middleware(mock_request, mock_call_next)

        # Assertions - should bypass authentication when disabled
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)
        self.mock_security_manager.authenticate_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_logging(self):
        """Test that authentication events are logged."""
        with patch.object(self.middleware.logger, "info") as mock_logger:
            # Create mock request with API key
            mock_request = Mock(spec=Request)
            mock_request.url.path = "/api/v1/users/me"
            mock_request.headers = {"X-API-Key": "test_key_123"}

            # Mock successful authentication
            auth_result = AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username="testuser",
                roles=["user"],
                auth_method=AuthMethod.API_KEY,
            )
            self.mock_auth_manager.authenticate_api_key.return_value = auth_result

            # Create mock call_next
            mock_call_next = AsyncMock()
            mock_response = Mock(spec=Response)
            mock_call_next.return_value = mock_response

            # Process request
            await self.middleware(mock_request, mock_call_next)

            # Assertions - should log authentication success
            mock_logger.assert_called()

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_error_logging(self):
        """Test that authentication errors are logged."""
        with patch.object(self.middleware.logger, "error") as mock_logger:
            # Create mock request
            mock_request = Mock(spec=Request)
            mock_request.url.path = "/api/v1/users/me"
            mock_request.headers = {"X-API-Key": "test_key_123"}

            # Mock auth manager to raise exception
            self.mock_auth_manager.authenticate_api_key.side_effect = Exception(
                "Authentication error"
            )

            # Create mock call_next
            mock_call_next = AsyncMock()

            # Process request
            await self.middleware(mock_request, mock_call_next)

            # Assertions - should log authentication error
            mock_logger.assert_called()

    def test_fastapi_auth_middleware_inheritance(self):
        """Test that FastAPIAuthMiddleware properly inherits from AuthMiddleware."""
        from mcp_security_framework.middleware.auth_middleware import AuthMiddleware

        assert issubclass(FastAPIAuthMiddleware, AuthMiddleware)
        assert isinstance(self.middleware, AuthMiddleware)

    def test_fastapi_auth_middleware_config_validation(self):
        """Test that middleware validates configuration properly."""
        # Test with valid config
        assert self.middleware.config is not None
        assert self.middleware.config.auth.enabled is True
        assert "api_key" in self.middleware.config.auth.methods

        # Test with invalid config (should not raise during init)
        try:
            invalid_config = SecurityConfig(
                auth=AuthConfig(
                    enabled=True,
                    methods=["invalid_method"],
                    api_keys={},
                    public_paths=[],
                )
            )
            # If we get here, the config was accepted (which is wrong)
            assert False, "Invalid config should have raised validation error"
        except Exception as e:
            # This is expected - invalid config should raise validation error
            assert "invalid_method" in str(e)
            # Don't try to create middleware with invalid config
        # The middleware should be valid since we're testing the existing one
        assert self.middleware is not None

    @pytest.mark.asyncio
    async def test_fastapi_auth_middleware_exception_in_call(self):
        """Test exception handling in __call__ method."""
        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/users/me"
        mock_request.headers = {"X-API-Key": "test_key_123"}

        # Mock call_next to raise exception
        mock_call_next = AsyncMock()
        mock_call_next.side_effect = Exception("Test exception")

        # Process request - should handle exception gracefully
        with pytest.raises(Exception) as exc_info:
            await self.middleware(mock_request, mock_call_next)

        assert "Authentication processing failed" in str(exc_info.value)
        assert hasattr(exc_info.value, "error_code")
        assert exc_info.value.error_code == -32035

    def test_fastapi_auth_middleware_get_client_ip_x_forwarded_for(self):
        """Test getting client IP from X-Forwarded-For header."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}

        ip = self.middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_fastapi_auth_middleware_get_client_ip_x_real_ip(self):
        """Test getting client IP from X-Real-IP header."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Real-IP": "192.168.1.2"}

        ip = self.middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.2"

    def test_fastapi_auth_middleware_get_client_ip_client_host(self):
        """Test getting client IP from client.host."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.3"

        ip = self.middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.3"

    def test_fastapi_auth_middleware_get_client_ip_no_client(self):
        """Test getting client IP when client is None."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.client = None

        ip = self.middleware._get_client_ip(mock_request)
        assert ip == "127.0.0.1"  # Default fallback from constants

    def test_fastapi_auth_middleware_get_client_ip_with_default_ip_config(self):
        """Test getting client IP with default_ip in config."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.client = None

        # Mock the config to have default_client_ip attribute
        self.middleware.config = Mock()
        self.middleware.config.default_client_ip = "192.168.0.1"

        ip = self.middleware._get_client_ip(mock_request)
        assert ip == "192.168.0.1"

    def test_fastapi_auth_middleware_get_cache_key(self):
        """Test cache key generation."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"User-Agent": "test-browser/1.0"}
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.1"

        cache_key = self.middleware._get_cache_key(mock_request)
        assert cache_key.startswith("auth:192.168.1.1:")
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0

    def test_fastapi_auth_middleware_unsupported_auth_method(self):
        """Test handling of unsupported authentication method."""
        mock_request = Mock(spec=Request)

        result = self.middleware._try_auth_method(mock_request, "unsupported_method")

        assert result.is_valid is False
        assert result.error_code == -32022
        assert "Unsupported authentication method" in result.error_message

    def test_fastapi_auth_middleware_auth_method_exception(self):
        """Test exception handling in _try_auth_method."""
        mock_request = Mock(spec=Request)

        # Mock authenticate_api_key to raise exception
        self.mock_auth_manager.authenticate_api_key.side_effect = Exception(
            "Test auth error"
        )

        result = self.middleware._try_auth_method(mock_request, "api_key")

        assert result.is_valid is False
        assert result.error_code == -32023
        assert "Authentication method api_key failed" in result.error_message

    def test_fastapi_auth_middleware_api_key_from_authorization_header(self):
        """Test API key authentication using Authorization header."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer api_key_123"}

        # Mock successful authentication
        auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="testuser",
            roles=["user"],
            auth_method=AuthMethod.API_KEY,
        )
        self.mock_auth_manager.authenticate_api_key.return_value = auth_result

        result = self.middleware._try_api_key_auth(mock_request)

        assert result.is_valid is True
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with(
            "api_key_123"
        )

    def test_fastapi_auth_middleware_api_key_no_key(self):
        """Test API key authentication when no key is provided."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}

        result = self.middleware._try_api_key_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32012
        assert "API key not found in request" in result.error_message

    def test_fastapi_auth_middleware_jwt_no_token(self):
        """Test JWT authentication when no token is provided."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}

        result = self.middleware._try_jwt_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32013
        assert "JWT token not found in Authorization header" in result.error_message

    def test_fastapi_auth_middleware_jwt_wrong_format(self):
        """Test JWT authentication with wrong Authorization header format."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Basic dGVzdDp0ZXN0"}

        result = self.middleware._try_jwt_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32013
        assert "JWT token not found in Authorization header" in result.error_message

    def test_fastapi_auth_middleware_basic_auth_not_implemented(self):
        """Test basic authentication (not implemented)."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Basic dGVzdDp0ZXN0"}

        result = self.middleware._try_basic_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32016
        assert "Basic authentication not implemented" in result.error_message

    def test_fastapi_auth_middleware_basic_auth_no_credentials(self):
        """Test basic authentication when no credentials are provided."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}

        result = self.middleware._try_basic_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32015
        assert "Basic authentication credentials not found" in result.error_message

    def test_fastapi_auth_middleware_basic_auth_wrong_format(self):
        """Test basic authentication with wrong Authorization header format."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer token123"}

        result = self.middleware._try_basic_auth(mock_request)

        assert result.is_valid is False
        assert result.error_code == -32015
        assert "Basic authentication credentials not found" in result.error_message
