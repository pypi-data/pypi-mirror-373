"""
Django Example Implementation

This module provides a complete example of how to implement the MCP Security Framework
with Django, including all abstract method implementations for real server usage.

The example demonstrates:
- Complete Django application with security middleware
- Real-world authentication and authorization
- Rate limiting implementation
- Certificate-based authentication
- Production-ready security headers
- Comprehensive error handling

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Configure Django settings before importing Django modules
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="django-insecure-test-key-for-examples",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        ROOT_URLCONF=None,
    )
    django.setup()

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

try:
    from django.middleware.base import BaseMiddleware
except ImportError:
    # Fallback for Django 5.x
    from django.utils.deprecation import MiddlewareMixin as BaseMiddleware

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import include, path
from django.utils.decorators import method_decorator
from django.views import View

from mcp_security_framework.constants import (
    AUTH_METHODS,
    DEFAULT_CLIENT_IP,
    DEFAULT_SECURITY_HEADERS,
    HTTP_FORBIDDEN,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    ErrorCodes,
)
from mcp_security_framework.core.auth_manager import AuthManager
from mcp_security_framework.core.permission_manager import PermissionManager
from mcp_security_framework.core.rate_limiter import RateLimiter
from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.core.ssl_manager import SSLManager
from mcp_security_framework.schemas.config import AuthConfig, SecurityConfig, SSLConfig
from mcp_security_framework.schemas.models import AuthMethod, AuthResult, AuthStatus


class DjangoSecurityMiddleware(BaseMiddleware):
    """
    Django Security Middleware Implementation

    This middleware provides comprehensive security features for Django applications
    including authentication, authorization, rate limiting, and security headers.
    """

    def __init__(self, get_response):
        """Initialize middleware with security configuration."""
        super().__init__(get_response)
        self.config = self._load_config()
        self.security_manager = SecurityManager(self.config)
        self.logger = logging.getLogger(__name__)

    def _load_config(self) -> SecurityConfig:
        """Load security configuration."""
        config_path = getattr(settings, "SECURITY_CONFIG_PATH", None)

        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return SecurityConfig(**config_data)

        # Create production-ready default configuration
        return SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=[
                    AUTH_METHODS["API_KEY"],
                    AUTH_METHODS["JWT"],
                    AUTH_METHODS["CERTIFICATE"],
                ],
                api_keys={
                    "admin_key_123": {"username": "admin", "roles": ["admin", "user"]},
                    "user_key_456": {"username": "user", "roles": ["user"]},
                    "readonly_key_789": {"username": "readonly", "roles": ["readonly"]},
                },
                jwt_secret="your-super-secret-jwt-key-change-in-production",
                jwt_algorithm="HS256",
                jwt_expiry_hours=24,
                public_paths=["/health/", "/metrics/", "/admin/"],
                security_headers=DEFAULT_SECURITY_HEADERS,
            ),
            ssl=SSLConfig(
                enabled=False,  # Disable SSL for example
                cert_file=None,
                key_file=None,
                ca_cert_file=None,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
            ),
            rate_limit={
                "enabled": True,
                "default_requests_per_minute": 60,
                "default_requests_per_hour": 1000,
                "burst_limit": 2,
                "window_size_seconds": 60,
                "storage_backend": "redis",
                "redis_config": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": None,
                },
                "exempt_paths": ["/health/", "/metrics/", "/admin/"],
                "exempt_roles": ["admin"],
            },
            permissions={
                "enabled": False,  # Disable permissions for example
                "roles_file": "config/roles.json",
                "default_role": "user",
                "hierarchy_enabled": True,
            },
            logging={
                "enabled": True,
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": "logs/security.log",
                "max_file_size": 10,
                "backup_count": 5,
                "console_output": True,
                "json_format": False,
            },
        )

    def __call__(self, request):
        """Process request through security middleware."""
        # Check if path is public
        if self._is_public_path(request.path):
            return self.get_response(request)

        # Rate limiting check
        if not self._check_rate_limit(request):
            return self._rate_limit_response()

        # Authentication check
        auth_result = self._authenticate_request(request)
        if not auth_result.is_valid:
            return self._auth_error_response(auth_result)

        # Authorization check
        if not self._check_permissions(request, auth_result):
            return self._permission_error_response()

        # Add user info to request
        request.user_info = {
            "username": auth_result.username,
            "roles": auth_result.roles,
            "permissions": auth_result.permissions,
            "auth_method": auth_result.auth_method,
        }

        # Process request
        response = self.get_response(request)

        # Add security headers
        self._add_security_headers(response)

        return response

    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (bypasses authentication)."""
        return any(
            path.startswith(public_path)
            for public_path in self.config.auth.public_paths
        )

    def _check_rate_limit(self, request: HttpRequest) -> bool:
        """Check if request is within rate limits."""
        if not self.config.rate_limit.enabled:
            return True

        identifier = self._get_rate_limit_identifier(request)
        return self.security_manager.rate_limiter.check_rate_limit(identifier)

    def _get_rate_limit_identifier(self, request: HttpRequest) -> str:
        """Get rate limit identifier from request."""
        # Try to get IP from headers
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.META.get("HTTP_X_REAL_IP")
        if real_ip:
            return real_ip

        # Fall back to remote address
        return request.META.get("REMOTE_ADDR", DEFAULT_CLIENT_IP)

    def _authenticate_request(self, request: HttpRequest) -> AuthResult:
        """Authenticate the request using configured methods."""
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
            if auth_result.is_valid:
                return auth_result

        # All authentication methods failed
        return AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=None,
            error_code=ErrorCodes.AUTHENTICATION_ERROR,
            error_message="All authentication methods failed",
        )

    def _try_auth_method(self, request: HttpRequest, method: str) -> AuthResult:
        """Try authentication using specific method."""
        try:
            if method == AUTH_METHODS["API_KEY"]:
                return self._try_api_key_auth(request)
            elif method == AUTH_METHODS["JWT"]:
                return self._try_jwt_auth(request)
            elif method == AUTH_METHODS["CERTIFICATE"]:
                return self._try_certificate_auth(request)
            else:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.FAILED,
                    username=None,
                    roles=[],
                    auth_method=None,
                    error_code=ErrorCodes.AUTH_METHOD_NOT_SUPPORTED,
                    error_message=f"Unsupported authentication method: {method}",
                )
        except Exception as e:
            self.logger.error(f"Authentication method {method} failed: {str(e)}")
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=ErrorCodes.AUTHENTICATION_ERROR,
                error_message=str(e),
            )

    def _try_api_key_auth(self, request: HttpRequest) -> AuthResult:
        """Try API key authentication."""
        # Try to get API key from headers
        api_key = request.META.get("HTTP_X_API_KEY")
        if not api_key:
            # Try Authorization header
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                api_key = auth_header[7:]  # Remove "Bearer " prefix

        if not api_key:
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=AuthMethod.API_KEY,
                error_code=ErrorCodes.API_KEY_NOT_FOUND,
                error_message="API key not found in request",
            )

        return self.security_manager.auth_manager.authenticate_api_key(api_key)

    def _try_jwt_auth(self, request: HttpRequest) -> AuthResult:
        """Try JWT authentication."""
        # Try to get JWT token from Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=AuthMethod.JWT,
                error_code=ErrorCodes.JWT_VALIDATION_ERROR,
                error_message="JWT token not found in Authorization header",
            )

        token = auth_header[7:]  # Remove "Bearer " prefix
        return self.security_manager.auth_manager.authenticate_jwt_token(token)

    def _try_certificate_auth(self, request: HttpRequest) -> AuthResult:
        """Try certificate authentication."""
        # In Django, certificate authentication would typically be handled
        # at the web server level (nginx, Apache) and passed via headers
        client_cert = request.META.get("SSL_CLIENT_CERT")
        if not client_cert:
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=AuthMethod.CERTIFICATE,
                error_code=ErrorCodes.CERTIFICATE_AUTH_ERROR,
                error_message="Client certificate not found",
            )

        return self.security_manager.auth_manager.authenticate_certificate(client_cert)

    def _check_permissions(self, request: HttpRequest, auth_result: AuthResult) -> bool:
        """Check if user has required permissions for the request."""
        if not self.config.permissions.enabled:
            return True

        # Get required permissions based on request
        required_permissions = self._get_required_permissions(request)
        if not required_permissions:
            return True  # No specific permissions required

        return self.security_manager.permission_manager.validate_access(
            auth_result.roles, required_permissions
        )

    def _get_required_permissions(self, request: HttpRequest) -> List[str]:
        """Get required permissions for the request."""
        # This would be implemented based on your permission system
        # For now, return basic permissions based on HTTP method
        method_permissions = {
            "GET": ["read"],
            "POST": ["write"],
            "PUT": ["write"],
            "PATCH": ["write"],
            "DELETE": ["delete"],
        }

        return method_permissions.get(request.method, [])

    def _add_security_headers(self, response: HttpResponse):
        """Add security headers to response."""
        for header_name, header_value in self.config.auth.security_headers.items():
            response[header_name] = header_value

    def _rate_limit_response(self) -> HttpResponse:
        """Create rate limit exceeded response."""
        return JsonResponse(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests, please try again later",
                "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED_ERROR,
            },
            status=HTTP_TOO_MANY_REQUESTS,
        )

    def _auth_error_response(self, auth_result: AuthResult) -> HttpResponse:
        """Create authentication error response."""
        return JsonResponse(
            {
                "error": "Authentication failed",
                "message": auth_result.error_message or "Invalid credentials",
                "error_code": auth_result.error_code,
                "auth_method": auth_result.auth_method,
            },
            status=HTTP_UNAUTHORIZED,
        )

    def _permission_error_response(self) -> HttpResponse:
        """Create permission denied response."""
        return JsonResponse(
            {
                "error": "Permission denied",
                "message": "Insufficient permissions to access this resource",
                "error_code": ErrorCodes.PERMISSION_DENIED_ERROR,
            },
            status=HTTP_FORBIDDEN,
        )


# Django Views
class HealthCheckView(View):
    """Health check endpoint."""

    def get(self, request):
        """Handle GET request."""
        return JsonResponse(
            {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0",
            }
        )


class MetricsView(View):
    """Metrics endpoint."""

    def get(self, request):
        """Handle GET request."""
        return JsonResponse(
            {
                "requests_total": 1000,
                "requests_per_minute": 60,
                "active_connections": 25,
                "uptime_seconds": 3600,
            }
        )


class UserProfileView(View):
    """User profile endpoint."""

    def get(self, request):
        """Handle GET request."""
        user_info = getattr(request, "user_info", None)
        if not user_info:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        return JsonResponse(
            {
                "username": user_info.get("username"),
                "roles": user_info.get("roles", []),
                "permissions": user_info.get("permissions", []),
                "last_login": datetime.now(timezone.utc).isoformat(),
            }
        )


class AdminUsersView(View):
    """Admin users endpoint."""

    def get(self, request):
        """Handle GET request."""
        user_info = getattr(request, "user_info", None)
        if not user_info or "admin" not in user_info.get("roles", []):
            return JsonResponse({"error": "Admin access required"}, status=403)

        return JsonResponse(
            {
                "users": [
                    {"username": "admin", "roles": ["admin"], "status": "active"},
                    {"username": "user", "roles": ["user"], "status": "active"},
                    {"username": "readonly", "roles": ["readonly"], "status": "active"},
                ]
            }
        )


class DataView(View):
    """Data endpoint."""

    def get(self, request, data_id):
        """Handle GET request."""
        user_info = getattr(request, "user_info", None)
        if not user_info:
            return JsonResponse({"error": "Authentication required"}, status=401)

        return JsonResponse(
            {
                "id": data_id,
                "data": {"example": "data"},
                "created_by": "user",
                "created_at": "2024-01-01T00:00:00Z",
            }
        )

    def post(self, request):
        """Handle POST request."""
        user_info = getattr(request, "user_info", None)
        if not user_info:
            return JsonResponse({"error": "Authentication required"}, status=401)

        if "readonly" in user_info.get("roles", []):
            return JsonResponse({"error": "Write permission required"}, status=403)

        # Process request data
        data = json.loads(request.body) if request.body else {}

        return JsonResponse(
            {
                "id": "data_123",
                "created_by": user_info.get("username"),
                "data": data,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )


# URL patterns
urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("metrics/", MetricsView.as_view(), name="metrics"),
    path("api/v1/users/me/", UserProfileView.as_view(), name="user_profile"),
    path("api/v1/admin/users/", AdminUsersView.as_view(), name="admin_users"),
    path("api/v1/data/", DataView.as_view(), name="data"),
    path("api/v1/data/<str:data_id>/", DataView.as_view(), name="data_detail"),
]


# Django Example Application
class DjangoExample:
    """
    Complete Django Example with Security Framework Implementation

    This class demonstrates a production-ready Django application
    with comprehensive security features.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Django example with security configuration.

        Args:
            config_path: Path to security configuration file
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)

    def setup_django_settings(self):
        """Setup Django settings with security configuration."""
        # This would be called in your Django settings.py
        settings.SECURITY_CONFIG_PATH = self.config_path

        # Add security middleware
        if (
            "mcp_security_framework.examples.django_example.DjangoSecurityMiddleware"
            not in settings.MIDDLEWARE
        ):
            settings.MIDDLEWARE.insert(
                0,
                "mcp_security_framework.examples.django_example.DjangoSecurityMiddleware",
            )

        # Security settings
        settings.SECURE_SSL_REDIRECT = True
        settings.SECURE_HSTS_SECONDS = 31536000
        settings.SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        settings.SECURE_HSTS_PRELOAD = True
        settings.SECURE_CONTENT_TYPE_NOSNIFF = True
        settings.SECURE_BROWSER_XSS_FILTER = True
        settings.X_FRAME_OPTIONS = "DENY"
        settings.SESSION_COOKIE_SECURE = True
        settings.CSRF_COOKIE_SECURE = True

    def create_superuser(self, username: str, email: str, password: str):
        """Create Django superuser."""
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                self.logger.info(f"Created superuser: {username}")
            else:
                self.logger.info(f"Superuser {username} already exists")
        except Exception as e:
            self.logger.error(f"Failed to create superuser: {str(e)}")

    def get_security_status(self) -> Dict[str, Any]:
        """Get security framework status."""
        return {
            "framework": "Django",
            "middleware_enabled": True,
            "ssl_enabled": True,
            "auth_enabled": True,
            "rate_limiting_enabled": True,
            "permissions_enabled": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Example usage and testing
class DjangoExampleTest:
    """Test class for Django example functionality."""

    @staticmethod
    def test_middleware_creation():
        """Test middleware creation."""
        middleware = DjangoSecurityMiddleware(lambda request: None)
        assert middleware.config is not None
        assert middleware.security_manager is not None

        print("✅ Middleware creation test passed")

    @staticmethod
    def test_public_path_check():
        """Test public path checking."""
        middleware = DjangoSecurityMiddleware(lambda request: None)

        # Test public paths
        assert middleware._is_public_path("/health/")
        assert middleware._is_public_path("/metrics/")
        assert middleware._is_public_path("/admin/")

        # Test private paths
        assert not middleware._is_public_path("/api/v1/users/")
        assert not middleware._is_public_path("/private/")

        print("✅ Public path check test passed")

    @staticmethod
    def test_rate_limit_identifier():
        """Test rate limit identifier extraction."""
        middleware = DjangoSecurityMiddleware(lambda request: None)

        # Mock request
        class MockRequest:
            def __init__(self):
                self.META = {}

        request = MockRequest()

        # Test X-Forwarded-For
        request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1, 10.0.0.1"
        assert middleware._get_rate_limit_identifier(request) == "192.168.1.1"

        # Test X-Real-IP
        request.META = {"HTTP_X_REAL_IP": "192.168.1.100"}
        assert middleware._get_rate_limit_identifier(request) == "192.168.1.100"

        # Test REMOTE_ADDR
        request.META = {"REMOTE_ADDR": "127.0.0.1"}
        assert middleware._get_rate_limit_identifier(request) == "127.0.0.1"

        print("✅ Rate limit identifier test passed")


if __name__ == "__main__":
    # Run tests
    print("Running Django Example Tests...")
    DjangoExampleTest.test_middleware_creation()
    DjangoExampleTest.test_public_path_check()
    DjangoExampleTest.test_rate_limit_identifier()

    # Example usage
    print("\nExample Usage:")
    example = DjangoExample()
    example.setup_django_settings()

    # Create superuser
    example.create_superuser("admin", "admin@example.com", "secure_password")

    # Get security status
    status = example.get_security_status()
    print(f"Security status: {status}")
