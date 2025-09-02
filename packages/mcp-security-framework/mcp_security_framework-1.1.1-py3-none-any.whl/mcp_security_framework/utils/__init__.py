"""
MCP Security Framework Utilities Module

This module provides comprehensive utilities for the MCP Security Framework
including cryptographic functions, certificate utilities, and validation
utilities.

Key Components:
    - Cryptographic utilities for hashing, signing, and JWT operations
    - Certificate utilities for parsing and validation
    - Validation utilities for data and configuration validation

Functions:
    crypto_utils: Cryptographic operations and utilities
    cert_utils: Certificate parsing and validation utilities
    validation_utils: Data validation and normalization utilities

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

# Certificate utilities
from .cert_utils import (
    CertificateError,
    convert_certificate_format,
    extract_certificate_info,
    extract_permissions_from_certificate,
    extract_public_key,
    extract_roles_from_certificate,
    get_certificate_expiry,
    get_certificate_serial_number,
    is_certificate_self_signed,
    parse_certificate,
    validate_certificate_chain,
    validate_certificate_format,
    validate_certificate_purpose,
)

# Crypto utilities
from .crypto_utils import (
    CryptoError,
    create_jwt_token,
    generate_api_key,
    generate_hmac,
    generate_random_bytes,
    generate_rsa_key_pair,
    hash_data,
    hash_password,
    sign_data,
    verify_hmac,
    verify_jwt_token,
    verify_password,
    verify_signature,
)

# Validation utilities
from .validation_utils import (
    ValidationError,
    normalize_data,
    sanitize_string,
    validate_configuration_file,
    validate_directory_structure,
    validate_email,
    validate_file_extension,
    validate_file_path,
    validate_input_data,
    validate_ip_address,
    validate_json_schema,
    validate_list_content,
    validate_numeric_range,
    validate_string_length,
    validate_url,
)

__all__ = [
    # Crypto utilities
    "CryptoError",
    "create_jwt_token",
    "generate_api_key",
    "generate_hmac",
    "generate_random_bytes",
    "generate_rsa_key_pair",
    "hash_data",
    "hash_password",
    "sign_data",
    "verify_hmac",
    "verify_jwt_token",
    "verify_password",
    "verify_signature",
    # Certificate utilities
    "CertificateError",
    "convert_certificate_format",
    "extract_certificate_info",
    "extract_permissions_from_certificate",
    "extract_public_key",
    "extract_roles_from_certificate",
    "get_certificate_expiry",
    "get_certificate_serial_number",
    "is_certificate_self_signed",
    "parse_certificate",
    "validate_certificate_chain",
    "validate_certificate_format",
    "validate_certificate_purpose",
    # Validation utilities
    "ValidationError",
    "normalize_data",
    "sanitize_string",
    "validate_configuration_file",
    "validate_directory_structure",
    "validate_email",
    "validate_file_extension",
    "validate_file_path",
    "validate_input_data",
    "validate_ip_address",
    "validate_json_schema",
    "validate_list_content",
    "validate_numeric_range",
    "validate_string_length",
    "validate_url",
]
