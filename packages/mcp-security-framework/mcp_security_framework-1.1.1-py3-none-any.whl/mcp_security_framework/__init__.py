"""
MCP Security Framework

Universal security framework for microservices with SSL/TLS, authentication,
authorization, and rate limiting.

This framework provides comprehensive security capabilities for Python applications,
including multi-method authentication, SSL/TLS management, role-based authorization,
and rate limiting. It supports multiple web frameworks including FastAPI, Flask,
and Django, as well as standalone usage.

Key Features:
- Multi-method Authentication (API keys, JWT tokens, X.509 certificates)
- SSL/TLS Management (Server and client certificate handling)
- Role-based Authorization (Flexible permission system with role hierarchy)
- Rate Limiting (Configurable request rate limiting)
- Framework Agnostic (Works with FastAPI, Flask, Django, and standalone)
- CLI Tools (Certificate management and security testing)
- Comprehensive Logging (Security event logging and monitoring)

Example Usage:
    >>> from mcp_security_framework import SecurityManager, SecurityConfig
    >>> from mcp_security_framework.schemas.config import AuthConfig
    >>>
    >>> config = SecurityConfig(
    ...     auth=AuthConfig(
    ...         enabled=True,
    ...         methods=["api_key"],
    ...         api_keys={"admin": "admin_key_123"}
    ...     )
    ... )
    >>>
    >>> security_manager = SecurityManager(config)
    >>> result = security_manager.validate_request({
    ...     "api_key": "admin_key_123",
    ...     "required_permissions": ["read", "write"]
    ... })
    >>>
    >>> if result.is_valid:
    ...     print("Access granted!")
    >>> else:
    ...     print(f"Access denied: {result.error_message}")

Author: Vasiliy Zdanovskiy
Version: 0.1.0
License: MIT
"""

from mcp_security_framework.core.auth_manager import AuthManager
from mcp_security_framework.core.cert_manager import CertificateManager
from mcp_security_framework.core.permission_manager import PermissionManager
from mcp_security_framework.core.rate_limiter import RateLimiter
from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.schemas.config import (
    AuthConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
)
from mcp_security_framework.schemas.models import (
    AuthResult,
    CertificateInfo,
    CertificatePair,
    ValidationResult,
)
from mcp_security_framework.schemas.responses import (
    ErrorResponse,
    SecurityResponse,
    SuccessResponse,
)

# Version information
__version__ = "0.1.0"
__author__ = "Vasiliy Zdanovskiy"
__email__ = "vasilyvz@gmail.com"
__license__ = "MIT"

# Main exports
__all__ = [
    # Core managers
    "SecurityManager",
    "AuthManager",
    "CertificateManager",
    "PermissionManager",
    "RateLimiter",
    # Configuration schemas
    "SecurityConfig",
    "AuthConfig",
    "SSLConfig",
    "PermissionConfig",
    "RateLimitConfig",
    # Data models
    "AuthResult",
    "ValidationResult",
    "CertificateInfo",
    "CertificatePair",
    # Response schemas
    "SecurityResponse",
    "ErrorResponse",
    "SuccessResponse",
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
