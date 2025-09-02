"""
MCP Security Framework Middleware Package

This package provides comprehensive security middleware implementations
for various web frameworks, including FastAPI, Flask, and others.

Key Features:
- Framework-agnostic base middleware
- Framework-specific implementations
- Specialized middleware components
- Factory functions for easy integration
- Comprehensive security processing

Modules:
    security_middleware: Base security middleware class
    fastapi_middleware: FastAPI-specific implementation
    flask_middleware: Flask-specific implementation
    auth_middleware: Authentication-only middleware
    rate_limit_middleware: Rate limiting-only middleware
    mtls_middleware: mTLS-specific middleware

Factory Functions:
    create_fastapi_security_middleware: Create FastAPI security middleware
    create_flask_security_middleware: Create Flask security middleware
    create_auth_middleware: Create authentication-only middleware
    create_rate_limit_middleware: Create rate limiting middleware
    create_mtls_middleware: Create mTLS middleware

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from typing import Optional

from ..core.security_manager import SecurityManager
from ..schemas.config import SecurityConfig
from .auth_middleware import AuthMiddleware, AuthMiddlewareError
from .fastapi_middleware import FastAPIMiddlewareError, FastAPISecurityMiddleware
from .flask_middleware import FlaskMiddlewareError, FlaskSecurityMiddleware
from .mtls_middleware import MTLSMiddleware, MTLSMiddlewareError
from .rate_limit_middleware import RateLimitMiddleware, RateLimitMiddlewareError
from .security_middleware import SecurityMiddleware, SecurityMiddlewareError


def create_fastapi_security_middleware(
    security_manager: SecurityManager,
) -> FastAPISecurityMiddleware:
    """
    Create FastAPI security middleware.

    Args:
        security_manager (SecurityManager): Security manager instance

    Returns:
        FastAPISecurityMiddleware: Configured FastAPI security middleware

    Raises:
        FastAPIMiddlewareError: If middleware creation fails

    Example:
        >>> from mcp_security_framework.middleware import create_fastapi_security_middleware
        >>> from fastapi import FastAPI
        >>>
        >>> app = FastAPI()
        >>> security_manager = SecurityManager(config)
        >>> middleware = create_fastapi_security_middleware(security_manager)
        >>> app.add_middleware(middleware)
    """
    return FastAPISecurityMiddleware(security_manager)


def create_flask_security_middleware(
    security_manager: SecurityManager,
) -> FlaskSecurityMiddleware:
    """
    Create Flask security middleware.

    Args:
        security_manager (SecurityManager): Security manager instance

    Returns:
        FlaskSecurityMiddleware: Configured Flask security middleware

    Raises:
        FlaskMiddlewareError: If middleware creation fails

    Example:
        >>> from mcp_security_framework.middleware import create_flask_security_middleware
        >>> from flask import Flask
        >>>
        >>> app = Flask(__name__)
        >>> security_manager = SecurityManager(config)
        >>> middleware = create_flask_security_middleware(security_manager)
        >>> app.wsgi_app = middleware(app.wsgi_app)
    """
    return FlaskSecurityMiddleware(security_manager)


def create_auth_middleware(
    security_manager: SecurityManager, framework: str = "fastapi", cache_ttl: int = 300
) -> AuthMiddleware:
    """
    Create authentication-only middleware for specified framework.

    Args:
        security_manager (SecurityManager): Security manager instance
        framework (str): Target framework ("fastapi", "flask", "django")
        cache_ttl (int): Cache TTL in seconds (default: 300)

    Returns:
        AuthMiddleware: Framework-specific authentication middleware

    Raises:
        ValueError: If framework is not supported
        AuthMiddlewareError: If middleware creation fails

    Example:
        >>> from mcp_security_framework.middleware import create_auth_middleware
        >>>
        >>> security_manager = SecurityManager(config)
        >>> auth_middleware = create_auth_middleware(security_manager, "fastapi")
    """
    if framework == "fastapi":
        from .fastapi_auth_middleware import FastAPIAuthMiddleware

        return FastAPIAuthMiddleware(security_manager.config, security_manager)
    elif framework == "flask":
        from .flask_auth_middleware import FlaskAuthMiddleware

        return FlaskAuthMiddleware(security_manager.config, security_manager)
    else:
        raise ValueError(f"Unsupported framework: {framework}")


def create_rate_limit_middleware(
    security_manager: SecurityManager,
) -> RateLimitMiddleware:
    """
    Create rate limiting middleware.

    Args:
        security_manager (SecurityManager): Security manager instance

    Returns:
        RateLimitMiddleware: Configured rate limiting middleware

    Raises:
        RateLimitMiddlewareError: If middleware creation fails

    Example:
        >>> from mcp_security_framework.middleware import create_rate_limit_middleware
        >>>
        >>> security_manager = SecurityManager(config)
        >>> rate_limit_middleware = create_rate_limit_middleware(security_manager)
    """
    return RateLimitMiddleware(security_manager)


def create_mtls_middleware(security_manager: SecurityManager) -> MTLSMiddleware:
    """
    Create mTLS middleware.

    Args:
        security_manager (SecurityManager): Security manager instance

    Returns:
        MTLSMiddleware: Configured mTLS middleware

    Raises:
        MTLSMiddlewareError: If middleware creation fails

    Example:
        >>> from mcp_security_framework.middleware import create_mtls_middleware
        >>>
        >>> security_manager = SecurityManager(config)
        >>> mtls_middleware = create_mtls_middleware(security_manager)
    """
    return MTLSMiddleware(security_manager)


def create_security_middleware(
    security_manager: SecurityManager, framework: str = "fastapi"
) -> SecurityMiddleware:
    """
    Create security middleware for specified framework.

    Args:
        security_manager (SecurityManager): Security manager instance
        framework (str): Target framework ("fastapi", "flask", etc.)

    Returns:
        SecurityMiddleware: Configured security middleware

    Raises:
        SecurityMiddlewareError: If middleware creation fails

    Example:
        >>> from mcp_security_framework.middleware import create_security_middleware
        >>>
        >>> security_manager = SecurityManager(config)
        >>> middleware = create_security_middleware(security_manager, "fastapi")
    """
    framework = framework.lower()

    if framework == "fastapi":
        return create_fastapi_security_middleware(security_manager)
    elif framework == "flask":
        return create_flask_security_middleware(security_manager)
    else:
        raise SecurityMiddlewareError(
            f"Unsupported framework: {framework}", error_code=-32041
        )


# Export all middleware classes and exceptions
__all__ = [
    # Base classes
    "SecurityMiddleware",
    "SecurityMiddlewareError",
    # FastAPI middleware
    "FastAPISecurityMiddleware",
    "FastAPIMiddlewareError",
    # Flask middleware
    "FlaskSecurityMiddleware",
    "FlaskMiddlewareError",
    # Specialized middleware
    "AuthMiddleware",
    "AuthMiddlewareError",
    "RateLimitMiddleware",
    "RateLimitMiddlewareError",
    "MTLSMiddleware",
    "MTLSMiddlewareError",
    # Factory functions
    "create_fastapi_security_middleware",
    "create_flask_security_middleware",
    "create_auth_middleware",
    "create_rate_limit_middleware",
    "create_mtls_middleware",
    "create_security_middleware",
]
