"""
Core Components Module

This module provides the core security components for the MCP Security Framework.
It includes the main business logic classes for authentication, authorization,
SSL/TLS management, certificate management, and rate limiting.

Key Components:
    - RateLimiter: Rate limiting functionality
    - PermissionManager: Role and permission management
    - SSLManager: SSL/TLS management
    - AuthManager: Authentication management
    - CertificateManager: Certificate management
    - SecurityManager: Main security manager

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from .auth_manager import AuthenticationError, AuthManager, JWTValidationError
from .cert_manager import (
    CertificateConfigurationError,
    CertificateGenerationError,
    CertificateManager,
    CertificateValidationError,
)
from .permission_manager import (
    PermissionConfigurationError,
    PermissionManager,
    PermissionValidationError,
    RoleNotFoundError,
)
from .rate_limiter import RateLimitEntry, RateLimiter
from .security_manager import (
    SecurityConfigurationError,
    SecurityManager,
    SecurityValidationError,
)
from .ssl_manager import SSLConfigurationError, SSLManager

__all__ = [
    "RateLimiter",
    "RateLimitEntry",
    "PermissionManager",
    "PermissionConfigurationError",
    "RoleNotFoundError",
    "PermissionValidationError",
    "SSLManager",
    "SSLConfigurationError",
    "CertificateValidationError",
    "AuthManager",
    "AuthenticationError",
    "JWTValidationError",
    "CertificateManager",
    "CertificateGenerationError",
    "CertificateConfigurationError",
    "SecurityManager",
    "SecurityConfigurationError",
    "SecurityValidationError",
]
