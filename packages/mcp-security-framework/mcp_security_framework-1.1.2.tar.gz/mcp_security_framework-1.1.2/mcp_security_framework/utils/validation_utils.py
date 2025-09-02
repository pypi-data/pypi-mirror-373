"""
Validation Utilities Module

This module provides comprehensive validation utilities for the
MCP Security Framework. It includes functions for validating
configuration files, input data, formats, and data normalization.

Key Features:
    - Configuration file validation
    - Input data validation
    - Format validation utilities
    - Data normalization functions
    - Email and URL validation
    - IP address validation
    - File path validation

Functions:
    validate_configuration_file: Validate configuration file
    validate_input_data: Validate input data
    validate_email: Validate email format
    validate_url: Validate URL format
    validate_ip_address: Validate IP address
    validate_file_path: Validate file path
    normalize_data: Normalize data format
    validate_json_schema: Validate JSON against schema

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import os
import re
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, message: str, error_code: int = -32003):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def validate_configuration_file(
    config_path: Union[str, Path], config_model: type[BaseModel]
) -> Dict[str, Any]:
    """
    Validate configuration file against Pydantic model.

    Args:
        config_path: Path to configuration file
        config_model: Pydantic model for validation

    Returns:
        Validated configuration data

    Raises:
        ValidationError: If configuration validation fails
    """
    try:
        config_path = Path(config_path)

        if not config_path.exists():
            raise ValidationError(f"Configuration file not found: {config_path}")

        if not config_path.is_file():
            raise ValidationError(f"Path is not a file: {config_path}")

        # Read configuration file
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix.lower() == ".json":
                config_data = json.load(f)
            else:
                raise ValidationError(
                    f"Unsupported configuration file format: {config_path.suffix}"
                )

        # Validate against model
        validated_config = config_model.model_validate(config_data)
        return validated_config.model_dump()

    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in configuration file: {str(e)}")
    except ValidationError as e:
        raise ValidationError(f"Configuration validation failed: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Configuration file processing failed: {str(e)}")


def validate_input_data(
    data: Any,
    required_fields: Optional[List[str]] = None,
    allowed_fields: Optional[List[str]] = None,
    data_type: Optional[type] = None,
) -> bool:
    """
    Validate input data structure and content.

    Args:
        data: Data to validate
        required_fields: List of required field names
        allowed_fields: List of allowed field names
        data_type: Expected data type

    Returns:
        True if data is valid, False otherwise

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Check data type
        if data_type and not isinstance(data, data_type):
            raise ValidationError(
                f"Expected {data_type.__name__}, got {type(data).__name__}"
            )

        # Check required fields for dictionaries
        if isinstance(data, dict) and required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {missing_fields}")

        # Check allowed fields for dictionaries
        if isinstance(data, dict) and allowed_fields:
            invalid_fields = [
                field for field in data.keys() if field not in allowed_fields
            ]
            if invalid_fields:
                raise ValidationError(f"Invalid fields: {invalid_fields}")

        return True

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Input data validation failed: {str(e)}")


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email)) and ".." not in email


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate
        allowed_schemes: List of allowed URL schemes

    Returns:
        True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)

        # Check if URL has required components
        if not parsed.scheme or not parsed.netloc:
            return False

        # Check allowed schemes
        if allowed_schemes and parsed.scheme not in allowed_schemes:
            return False

        return True
    except Exception:
        return False


def validate_ip_address(ip_address: str, ip_version: Optional[str] = None) -> bool:
    """
    Validate IP address format.

    Args:
        ip_address: IP address to validate
        ip_version: IP version to validate (ipv4, ipv6)

    Returns:
        True if IP address is valid, False otherwise
    """
    if not ip_address or not isinstance(ip_address, str):
        return False

    try:
        # Validate IPv4
        if ip_version == "ipv4" or (ip_version is None and "." in ip_address):
            socket.inet_pton(socket.AF_INET, ip_address)
            return True

        # Validate IPv6
        elif ip_version == "ipv6" or (ip_version is None and ":" in ip_address):
            socket.inet_pton(socket.AF_INET6, ip_address)
            return True

        return False
    except socket.error:
        return False


def validate_file_path(
    file_path: Union[str, Path],
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_directory: bool = False,
    must_be_readable: bool = False,
    must_be_writable: bool = False,
) -> bool:
    """
    Validate file path.

    Args:
        file_path: File path to validate
        must_exist: Whether file must exist
        must_be_file: Whether path must be a file
        must_be_directory: Whether path must be a directory
        must_be_readable: Whether file must be readable
        must_be_writable: Whether file must be writable

    Returns:
        True if path is valid, False otherwise
    """
    try:
        path = Path(file_path)

        # Check if file exists
        if must_exist and not path.exists():
            return False

        # Check if it's a file
        if must_be_file and not path.is_file():
            return False

        # Check if it's a directory
        if must_be_directory and not path.is_dir():
            return False

        # Check readability
        if must_be_readable and not os.access(path, os.R_OK):
            return False

        # Check writability
        if must_be_writable and not os.access(path, os.W_OK):
            return False

        return True
    except Exception:
        return False


def normalize_data(data: Any, data_type: str = "string") -> Any:
    """
    Normalize data format.

    Args:
        data: Data to normalize
        data_type: Target data type (string, integer, float, boolean)

    Returns:
        Normalized data

    Raises:
        ValidationError: If normalization fails
    """
    try:
        if data_type == "string":
            if data is None:
                return ""
            return str(data).strip()

        elif data_type == "integer":
            if data is None:
                return 0
            return int(float(data))

        elif data_type == "float":
            if data is None:
                return 0.0
            return float(data)

        elif data_type == "boolean":
            if data is None:
                return False
            if isinstance(data, bool):
                return data
            if isinstance(data, str):
                return data.lower() in ("true", "1", "yes", "on")
            return bool(data)

        else:
            raise ValidationError(f"Unsupported data type: {data_type}")

    except (ValueError, TypeError) as e:
        raise ValidationError(f"Data normalization failed: {str(e)}")


def validate_json_schema(data: Dict, schema: Dict) -> bool:
    """
    Validate JSON data against schema.

    Args:
        data: JSON data to validate
        schema: JSON schema for validation

    Returns:
        True if data matches schema, False otherwise

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Simple schema validation (basic implementation)
        # In production, use jsonschema library for full validation

        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        # Check field types
        properties = schema.get("properties", {})
        for field_name, field_value in data.items():
            if field_name in properties:
                field_schema = properties[field_name]
                expected_type = field_schema.get("type")

                if expected_type == "string" and not isinstance(field_value, str):
                    raise ValidationError(f"Field {field_name} must be a string")
                elif expected_type == "integer" and not isinstance(field_value, int):
                    raise ValidationError(f"Field {field_name} must be an integer")
                elif expected_type == "number" and not isinstance(
                    field_value, (int, float)
                ):
                    raise ValidationError(f"Field {field_name} must be a number")
                elif expected_type == "boolean" and not isinstance(field_value, bool):
                    raise ValidationError(f"Field {field_name} must be a boolean")
                elif expected_type == "array" and not isinstance(field_value, list):
                    raise ValidationError(f"Field {field_name} must be an array")
                elif expected_type == "object" and not isinstance(field_value, dict):
                    raise ValidationError(f"Field {field_name} must be an object")

        return True

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"JSON schema validation failed: {str(e)}")


def validate_string_length(
    value: str, min_length: Optional[int] = None, max_length: Optional[int] = None
) -> bool:
    """
    Validate string length.

    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length

    Returns:
        True if string length is valid, False otherwise
    """
    if not isinstance(value, str):
        return False

    length = len(value)

    if min_length is not None and length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True


def validate_numeric_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
) -> bool:
    """
    Validate numeric value range.

    Args:
        value: Numeric value to validate
        min_value: Minimum value
        max_value: Maximum value

    Returns:
        True if value is in range, False otherwise
    """
    if not isinstance(value, (int, float)):
        return False

    if min_value is not None and value < min_value:
        return False

    if max_value is not None and value > max_value:
        return False

    return True


def validate_list_content(
    value: List,
    allowed_values: Optional[List] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
) -> bool:
    """
    Validate list content and structure.

    Args:
        value: List to validate
        allowed_values: List of allowed values
        min_items: Minimum number of items
        max_items: Maximum number of items

    Returns:
        True if list is valid, False otherwise
    """
    if not isinstance(value, list):
        return False

    # Check item count
    if min_items is not None and len(value) < min_items:
        return False

    if max_items is not None and len(value) > max_items:
        return False

    # Check allowed values
    if allowed_values is not None:
        for item in value:
            if item not in allowed_values:
                return False

    return True


def sanitize_string(value: str, allowed_chars: Optional[str] = None) -> str:
    """
    Sanitize string by removing or replacing invalid characters.

    Args:
        value: String to sanitize
        allowed_chars: String of allowed characters (regex pattern)

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""

    if allowed_chars is None:
        # Default: allow alphanumeric, spaces, and common punctuation
        allowed_chars = r"[a-zA-Z0-9\s\-_.,!?@#$%&*()+=:;]"

    # Remove characters not in allowed set
    sanitized = re.sub(f"[^{allowed_chars}]", "", value)

    # Remove HTML tags and scripts
    sanitized = re.sub(r"<[^>]*>", "", sanitized)

    # Remove extra whitespace
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    return sanitized


def validate_file_extension(
    file_path: Union[str, Path], allowed_extensions: List[str]
) -> bool:
    """
    Validate file extension.

    Args:
        file_path: File path to validate
        allowed_extensions: List of allowed file extensions

    Returns:
        True if file extension is allowed, False otherwise
    """
    try:
        path = Path(file_path)
        extension = path.suffix.lower()

        # Normalize allowed extensions (remove leading dot if present)
        normalized_extensions = []
        for ext in allowed_extensions:
            ext_lower = ext.lower()
            if ext_lower.startswith("."):
                normalized_extensions.append(ext_lower)
            else:
                normalized_extensions.append("." + ext_lower)

        return extension in normalized_extensions
    except Exception:
        return False


def validate_directory_structure(
    directory_path: Union[str, Path],
    required_files: Optional[List[str]] = None,
    required_directories: Optional[List[str]] = None,
) -> bool:
    """
    Validate directory structure.

    Args:
        directory_path: Directory path to validate
        required_files: List of required files
        required_directories: List of required subdirectories

    Returns:
        True if directory structure is valid, False otherwise
    """
    try:
        directory = Path(directory_path)

        if not directory.exists() or not directory.is_dir():
            return False

        # Check required files
        if required_files:
            for file_name in required_files:
                file_path = directory / file_name
                if not file_path.exists() or not file_path.is_file():
                    return False

        # Check required directories
        if required_directories:
            for dir_name in required_directories:
                dir_path = directory / dir_name
                if not dir_path.exists() or not dir_path.is_dir():
                    return False

        return True
    except Exception:
        return False
