"""
Constants Module

This module contains all constants used throughout the MCP Security Framework.
It centralizes configuration values, error codes, and default settings to
eliminate hardcoded values from the codebase.

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

# Network and IP Constants
DEFAULT_CLIENT_IP = "127.0.0.1"
DEFAULT_SERVER_HOST = "localhost"
DEFAULT_SERVER_PORT = 8000

# Rate Limiting Constants
DEFAULT_REQUESTS_PER_MINUTE = 60
DEFAULT_REQUESTS_PER_HOUR = 1000
MAX_REQUESTS_PER_MINUTE = 10000
MAX_REQUESTS_PER_HOUR = 100000
DEFAULT_BURST_LIMIT = 2
MAX_BURST_LIMIT = 10
DEFAULT_WINDOW_SIZE_SECONDS = 60
MAX_WINDOW_SIZE_SECONDS = 3600
DEFAULT_CLEANUP_INTERVAL = 300
MAX_CLEANUP_INTERVAL = 3600

# Security Constants
DEFAULT_CACHE_TTL = 300  # 5 minutes
DEFAULT_FAILED_AUTH_CACHE_TTL = 60  # 1 minute
DEFAULT_RATE_LIMIT_CACHE_TTL = 60  # 1 minute

# Cryptographic Constants
PBKDF2_ITERATIONS = 100000
DEFAULT_SALT_LENGTH = 32
DEFAULT_API_KEY_LENGTH = 32
DEFAULT_RSA_KEY_SIZE = 2048
MAX_RSA_KEY_SIZE = 4096
MIN_RSA_KEY_SIZE = 2048

# Certificate Constants
DEFAULT_CERTIFICATE_VALIDITY_DAYS = 365
MAX_CERTIFICATE_VALIDITY_DAYS = 3650  # 10 years
DEFAULT_KEY_SIZE = 2048

# Logging Constants
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_MAX_FILE_SIZE_MB = 10
MAX_MAX_FILE_SIZE_MB = 1000
DEFAULT_BACKUP_COUNT = 5
MAX_BACKUP_COUNT = 100

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500


# Error Codes
class ErrorCodes:
    """Error codes for the MCP Security Framework."""

    # SSL/TLS Errors (-32001 to -32009)
    SSL_CONFIGURATION_ERROR = -32001
    CERTIFICATE_VALIDATION_ERROR = -32002
    SSL_CONTEXT_CREATION_ERROR = -32003
    SSL_HANDSHAKE_ERROR = -32004

    # Authentication Errors (-32010 to -32019)
    AUTHENTICATION_ERROR = -32010
    AUTHENTICATION_CONFIGURATION_ERROR = -32011
    API_KEY_NOT_FOUND = -32012
    JWT_VALIDATION_ERROR = -32013
    CERTIFICATE_AUTH_ERROR = -32014
    BASIC_AUTH_ERROR = -32015
    AUTH_METHOD_NOT_SUPPORTED = -32016

    # Authorization Errors (-32020 to -32029)
    PERMISSION_DENIED_ERROR = -32020
    INSUFFICIENT_PERMISSIONS = -32021
    ROLE_NOT_FOUND = -32022
    PERMISSION_NOT_FOUND = -32023

    # Rate Limiting Errors (-32030 to -32039)
    RATE_LIMIT_EXCEEDED_ERROR = -32030
    RATE_LIMIT_CONFIGURATION_ERROR = -32031
    RATE_LIMIT_STORAGE_ERROR = -32032

    # Middleware Errors (-32040 to -32049)
    SECURITY_MIDDLEWARE_ERROR = -32040
    AUTH_MIDDLEWARE_ERROR = -32041
    MTLS_MIDDLEWARE_ERROR = -32042
    RATE_LIMIT_MIDDLEWARE_ERROR = -32043

    # Certificate Management Errors (-32050 to -32059)
    CERTIFICATE_GENERATION_ERROR = -32050
    CERTIFICATE_REVOCATION_ERROR = -32051
    CERTIFICATE_STORAGE_ERROR = -32052
    CA_CONFIGURATION_ERROR = -32053

    # Crypto Errors (-32060 to -32069)
    CRYPTO_ERROR = -32060
    KEY_GENERATION_ERROR = -32061
    HASHING_ERROR = -32062
    ENCRYPTION_ERROR = -32063

    # Configuration Errors (-32070 to -32079)
    CONFIGURATION_ERROR = -32070
    VALIDATION_ERROR = -32071
    SERIALIZATION_ERROR = -32072

    # General Errors (-32080 to -32099)
    GENERAL_ERROR = -32080
    NOT_IMPLEMENTED_ERROR = -32081
    UNSUPPORTED_OPERATION_ERROR = -32082


# Security Headers
DEFAULT_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

# Authentication Methods
AUTH_METHODS = {
    "API_KEY": "api_key",
    "JWT": "jwt",
    "CERTIFICATE": "certificate",
    "BASIC": "basic",
    "OAUTH2": "oauth2",
}

# Storage Backends
STORAGE_BACKENDS = {"MEMORY": "memory", "REDIS": "redis", "DATABASE": "database"}

# Hash Algorithms
HASH_ALGORITHMS = {"SHA256": "sha256", "SHA512": "sha512", "MD5": "md5"}

# TLS Versions
TLS_VERSIONS = {
    "TLSv1.0": "TLSv1.0",
    "TLSv1.1": "TLSv1.1",
    "TLSv1.2": "TLSv1.2",
    "TLSv1.3": "TLSv1.3",
}

# Certificate Revocation Reasons
CERTIFICATE_REVOCATION_REASONS = {
    "UNSPECIFIED": "unspecified",
    "KEY_COMPROMISE": "key_compromise",
    "CA_COMPROMISE": "ca_compromise",
    "AFFILIATION_CHANGED": "affiliation_changed",
    "SUPERSEDED": "superseded",
    "CESSATION_OF_OPERATION": "cessation_of_operation",
    "CERTIFICATE_HOLD": "certificate_hold",
}

# Log Levels
LOG_LEVELS = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARNING": "WARNING",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL",
}

# Time Constants (in seconds)
TIME_CONSTANTS = {
    "MINUTE": 60,
    "HOUR": 3600,
    "DAY": 86400,
    "WEEK": 604800,
    "MONTH": 2592000,  # 30 days
    "YEAR": 31536000,  # 365 days
}

# Cache Keys
CACHE_KEY_PREFIXES = {
    "AUTH": "auth",
    "RATE_LIMIT": "rate_limit",
    "PERMISSION": "permission",
    "CERTIFICATE": "certificate",
}

# Environment Variables
ENV_VARS = {
    "DEFAULT_CLIENT_IP": "DEFAULT_CLIENT_IP",
    "DEFAULT_SERVER_HOST": "DEFAULT_SERVER_HOST",
    "DEFAULT_SERVER_PORT": "DEFAULT_SERVER_PORT",
    "LOG_LEVEL": "LOG_LEVEL",
    "ENVIRONMENT": "ENVIRONMENT",
}
