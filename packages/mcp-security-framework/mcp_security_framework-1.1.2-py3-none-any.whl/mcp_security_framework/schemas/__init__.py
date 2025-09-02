"""
MCP Security Framework Schemas Module

This module provides all data models and configuration schemas for the
MCP Security Framework. It includes configuration models, data models,
and response models used throughout the framework.

Key Components:
    - Configuration models for all framework components
    - Data models for authentication, certificates, and permissions
    - Response models for API responses and validation results
    - Type definitions and aliases for better code readability

Classes:
    SecurityConfig: Main security configuration class
    SSLConfig: SSL/TLS configuration settings
    AuthConfig: Authentication configuration
    CertificateConfig: Certificate management configuration
    PermissionConfig: Role and permission configuration
    RateLimitConfig: Rate limiting configuration
    LoggingConfig: Logging configuration

Models:
    AuthResult: Authentication result model
    ValidationResult: Validation result model
    CertificateInfo: Certificate information model
    CertificatePair: Certificate and key pair model
    RateLimitStatus: Rate limiting status model

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

# Configuration imports
from .config import (
    AuthConfig,
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    IntermediateCAConfig,
    LoggingConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    ServerCertConfig,
    SSLConfig,
)

# Type aliases
# Model imports
from .models import (
    ApiKey,
    AuthResult,
    CertificateChain,
    CertificateInfo,
    CertificatePair,
    CertificatePath,
    PermissionName,
    RateLimitStatus,
    RoleName,
    RolePermissions,
    UserCredentials,
    Username,
    ValidationResult,
)

# Response imports
from .responses import (
    ErrorResponse,
    SecurityResponse,
    SuccessResponse,
    ValidationResponse,
)

__all__ = [
    # Configuration classes
    "SecurityConfig",
    "SSLConfig",
    "AuthConfig",
    "CertificateConfig",
    "PermissionConfig",
    "RateLimitConfig",
    "LoggingConfig",
    "CAConfig",
    "ClientCertConfig",
    "ServerCertConfig",
    "IntermediateCAConfig",
    # Model classes
    "AuthResult",
    "ValidationResult",
    "CertificateInfo",
    "CertificatePair",
    "RateLimitStatus",
    "UserCredentials",
    "RolePermissions",
    "CertificateChain",
    # Response classes
    "SecurityResponse",
    "ErrorResponse",
    "SuccessResponse",
    "ValidationResponse",
    # Type aliases
    "ApiKey",
    "Username",
    "RoleName",
    "PermissionName",
    "CertificatePath",
]
