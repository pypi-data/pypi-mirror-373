"""
Validation Utilities Test Module

This module provides comprehensive unit tests for all validation
utilities in the MCP Security Framework.

Test Classes:
    TestInputValidation: Tests for input data validation
    TestFormatValidation: Tests for format validation
    TestDataNormalization: Tests for data normalization
    TestFileValidation: Tests for file validation

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import pytest

from mcp_security_framework.utils.validation_utils import (
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


class TestInputValidation:
    """Test suite for input data validation."""

    def test_validate_input_data_dict_success(self):
        """Test successful dictionary validation."""
        data = {"name": "test", "age": 25}
        result = validate_input_data(data, required_fields=["name"], data_type=dict)
        assert result is True

    def test_validate_input_data_missing_required_fields(self):
        """Test validation with missing required fields."""
        data = {"name": "test"}
        with pytest.raises(ValidationError) as exc_info:
            validate_input_data(data, required_fields=["name", "age"])

        assert "Missing required fields" in str(exc_info.value)

    def test_validate_input_data_invalid_fields(self):
        """Test validation with invalid fields."""
        data = {"name": "test", "invalid_field": "value"}
        with pytest.raises(ValidationError) as exc_info:
            validate_input_data(data, allowed_fields=["name"])

        assert "Invalid fields" in str(exc_info.value)

    def test_validate_input_data_wrong_type(self):
        """Test validation with wrong data type."""
        data = "not_a_dict"
        with pytest.raises(ValidationError) as exc_info:
            validate_input_data(data, data_type=dict)

        assert "Expected dict" in str(exc_info.value)

    def test_validate_input_data_no_constraints(self):
        """Test validation without any constraints."""
        data = {"name": "test", "age": 25}
        result = validate_input_data(data)
        assert result is True

    def test_validate_input_data_list_type(self):
        """Test validation with list data type."""
        data = [1, 2, 3]
        result = validate_input_data(data, data_type=list)
        assert result is True

    def test_validate_input_data_string_type(self):
        """Test validation with string data type."""
        data = "test_string"
        result = validate_input_data(data, data_type=str)
        assert result is True


class TestFormatValidation:
    """Test suite for format validation."""

    def test_validate_email_valid(self):
        """Test valid email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
        ]

        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        invalid_emails = [
            "",
            "invalid_email",
            "@example.com",
            "test@",
            "test..test@example.com",
        ]

        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_email_none_input(self):
        """Test email validation with None input."""
        assert validate_email(None) is False

    def test_validate_email_non_string_input(self):
        """Test email validation with non-string input."""
        assert validate_email(123) is False

    def test_validate_url_valid(self):
        """Test valid URL validation."""
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.org/path",
            "ftp://ftp.example.net",
        ]

        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_invalid(self):
        """Test invalid URL validation."""
        invalid_urls = ["", "not_a_url", "http://", "https://"]

        for url in invalid_urls:
            assert validate_url(url) is False

    def test_validate_url_allowed_schemes(self):
        """Test URL validation with allowed schemes."""
        url = "https://example.com"
        assert validate_url(url, allowed_schemes=["https"]) is True
        assert validate_url(url, allowed_schemes=["http"]) is False

    def test_validate_url_none_input(self):
        """Test URL validation with None input."""
        assert validate_url(None) is False

    def test_validate_url_non_string_input(self):
        """Test URL validation with non-string input."""
        assert validate_url(123) is False

    def test_validate_ip_address_valid(self):
        """Test valid IP address validation."""
        valid_ips = ["192.168.1.1", "10.0.0.1", "127.0.0.1", "::1", "2001:db8::1"]

        for ip in valid_ips:
            assert validate_ip_address(ip) is True

    def test_validate_ip_address_invalid(self):
        """Test invalid IP address validation."""
        invalid_ips = ["", "256.256.256.256", "192.168.1.256", "not_an_ip"]

        for ip in invalid_ips:
            assert validate_ip_address(ip) is False

    def test_validate_ip_address_specific_version(self):
        """Test IP address validation with specific version."""
        assert validate_ip_address("192.168.1.1", "ipv4") is True
        assert validate_ip_address("::1", "ipv6") is True
        assert validate_ip_address("192.168.1.1", "ipv6") is False

    def test_validate_ip_address_none_input(self):
        """Test IP address validation with None input."""
        assert validate_ip_address(None) is False

    def test_validate_ip_address_non_string_input(self):
        """Test IP address validation with non-string input."""
        assert validate_ip_address(123) is False


class TestDataNormalization:
    """Test suite for data normalization."""

    def test_normalize_data_string(self):
        """Test string normalization."""
        assert normalize_data("  test  ", "string") == "test"
        assert normalize_data(None, "string") == ""
        assert normalize_data(123, "string") == "123"

    def test_normalize_data_integer(self):
        """Test integer normalization."""
        assert normalize_data("123", "integer") == 123
        assert normalize_data(123.45, "integer") == 123
        assert normalize_data(None, "integer") == 0

    def test_normalize_data_float(self):
        """Test float normalization."""
        assert normalize_data("123.45", "float") == 123.45
        assert normalize_data(123, "float") == 123.0
        assert normalize_data(None, "float") == 0.0

    def test_normalize_data_boolean(self):
        """Test boolean normalization."""
        assert normalize_data("true", "boolean") is True
        assert normalize_data("false", "boolean") is False
        assert normalize_data("1", "boolean") is True
        assert normalize_data("0", "boolean") is False
        assert normalize_data(None, "boolean") is False

    def test_normalize_data_boolean_true_values(self):
        """Test boolean normalization with various true values."""
        assert normalize_data(True, "boolean") is True
        assert normalize_data(1, "boolean") is True
        assert normalize_data("yes", "boolean") is True
        assert normalize_data("on", "boolean") is True

    def test_normalize_data_boolean_false_values(self):
        """Test boolean normalization with various false values."""
        assert normalize_data(False, "boolean") is False
        assert normalize_data(0, "boolean") is False
        assert normalize_data("", "boolean") is False

    def test_normalize_data_unsupported_type(self):
        """Test normalization with unsupported type."""
        with pytest.raises(ValidationError) as exc_info:
            normalize_data("test", "unsupported")

        assert "Unsupported data type" in str(exc_info.value)

    def test_sanitize_string(self):
        """Test string sanitization."""
        assert sanitize_string("  test  ") == "test"
        assert (
            sanitize_string("test<script>alert('xss')</script>") == "testalert('xss')"
        )
        assert sanitize_string("test\n\t\r") == "test"

    def test_sanitize_string_custom_chars(self):
        """Test string sanitization with custom allowed characters."""
        result = sanitize_string("test123", r"[a-z]")
        assert result == "test123"

    def test_sanitize_string_none_input(self):
        """Test string sanitization with None input."""
        assert sanitize_string(None) == ""

    def test_sanitize_string_non_string_input(self):
        """Test string sanitization with non-string input."""
        assert sanitize_string(123) == ""


class TestValidationFunctions:
    """Test suite for validation functions."""

    def test_validate_string_length(self):
        """Test string length validation."""
        assert validate_string_length("test", min_length=3, max_length=5) is True
        assert validate_string_length("test", min_length=5) is False
        assert validate_string_length("test", max_length=3) is False

    def test_validate_string_length_none_input(self):
        """Test string length validation with None input."""
        assert validate_string_length(None, min_length=3) is False

    def test_validate_string_length_non_string_input(self):
        """Test string length validation with non-string input."""
        assert validate_string_length(123, min_length=3) is False

    def test_validate_numeric_range(self):
        """Test numeric value range validation."""
        assert validate_numeric_range(5, min_value=1, max_value=10) is True
        assert validate_numeric_range(5, min_value=10) is False
        assert validate_numeric_range(5, max_value=3) is False

    def test_validate_numeric_range_none_input(self):
        """Test numeric range validation with None input."""
        assert validate_numeric_range(None, min_value=1) is False

    def test_validate_numeric_range_non_numeric_input(self):
        """Test numeric range validation with non-numeric input."""
        assert validate_numeric_range("not_a_number", min_value=1) is False

    def test_validate_list_content(self):
        """Test list content and structure validation."""
        assert validate_list_content([1, 2, 3], min_items=2, max_items=5) is True
        assert validate_list_content([1, 2, 3], allowed_values=[1, 2, 3, 4]) is True
        assert validate_list_content([1, 2, 3], allowed_values=[1, 2]) is False

    def test_validate_list_content_none_input(self):
        """Test list content validation with None input."""
        assert validate_list_content(None, min_items=2) is False

    def test_validate_list_content_non_list_input(self):
        """Test list content validation with non-list input."""
        assert validate_list_content("not_a_list", min_items=2) is False

    def test_validate_list_content_too_few_items(self):
        """Test list content validation with too few items."""
        assert validate_list_content([1], min_items=2) is False

    def test_validate_list_content_too_many_items(self):
        """Test list content validation with too many items."""
        assert validate_list_content([1, 2, 3], max_items=2) is False

    def test_validate_json_schema_success(self):
        """Test successful JSON schema validation."""
        data = {"name": "test", "age": 25}
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }

        assert validate_json_schema(data, schema) is True

    def test_validate_json_schema_missing_required(self):
        """Test JSON schema validation with missing required field."""
        data = {"age": 25}
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_json_schema(data, schema)

        assert "Missing required field" in str(exc_info.value)

    def test_validate_json_schema_wrong_type(self):
        """Test JSON schema validation with wrong type."""
        data = {"name": 123}
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}

        with pytest.raises(ValidationError) as exc_info:
            validate_json_schema(data, schema)

        assert "must be a string" in str(exc_info.value)

    def test_validate_json_schema_not_dict(self):
        """Test JSON schema validation with non-dict data."""
        data = "not_a_dict"
        schema = {"type": "object"}

        with pytest.raises(ValidationError) as exc_info:
            validate_json_schema(data, schema)

        assert "Data must be a dictionary" in str(exc_info.value)

    def test_validate_json_schema_integer_type(self):
        """Test JSON schema validation with integer type."""
        data = {"age": 25}
        schema = {"type": "object", "properties": {"age": {"type": "integer"}}}

        assert validate_json_schema(data, schema) is True

    def test_validate_json_schema_number_type(self):
        """Test JSON schema validation with number type."""
        data = {"price": 25.50}
        schema = {"type": "object", "properties": {"price": {"type": "number"}}}

        assert validate_json_schema(data, schema) is True

    def test_validate_json_schema_boolean_type(self):
        """Test JSON schema validation with boolean type."""
        data = {"active": True}
        schema = {"type": "object", "properties": {"active": {"type": "boolean"}}}

        assert validate_json_schema(data, schema) is True

    def test_validate_json_schema_array_type(self):
        """Test JSON schema validation with array type."""
        data = {"items": [1, 2, 3]}
        schema = {"type": "object", "properties": {"items": {"type": "array"}}}

        assert validate_json_schema(data, schema) is True

    def test_validate_json_schema_object_type(self):
        """Test JSON schema validation with object type."""
        data = {"user": {"name": "test"}}
        schema = {"type": "object", "properties": {"user": {"type": "object"}}}

        assert validate_json_schema(data, schema) is True


class TestFileValidation:
    """Test suite for file validation."""

    def test_validate_file_extension(self):
        """Test file extension validation."""
        assert validate_file_extension("test.txt", [".txt", ".pdf"]) is True
        assert validate_file_extension("test.txt", [".pdf", ".doc"]) is False

    def test_validate_file_extension_case_insensitive(self):
        """Test file extension validation with case insensitive."""
        assert validate_file_extension("test.TXT", [".txt", ".pdf"]) is True
        assert validate_file_extension("test.txt", [".TXT", ".PDF"]) is True

    def test_validate_file_extension_without_dot(self):
        """Test file extension validation without leading dot."""
        assert validate_file_extension("test.txt", ["txt", "pdf"]) is True
        assert validate_file_extension("test.txt", ["pdf", "doc"]) is False

    def test_validate_file_extension_exception_handling(self):
        """Test file extension validation with exception handling."""
        assert validate_file_extension(None, [".txt"]) is False
        assert validate_file_extension(123, [".txt"]) is False

    def test_validate_file_path(self):
        """Test file path validation."""
        # Test with non-existent path
        assert validate_file_path("/non/existent/path", must_exist=False) is True
        assert validate_file_path("/non/existent/path", must_exist=True) is False

    def test_validate_file_path_exception_handling(self):
        """Test file path validation with exception handling."""
        assert validate_file_path(None) is False
        assert validate_file_path(123) is False

    def test_validate_directory_structure(self):
        """Test directory structure validation."""
        # Test with non-existent directory
        assert validate_directory_structure("/non/existent/dir") is False

    def test_validate_directory_structure_exception_handling(self):
        """Test directory structure validation with exception handling."""
        assert validate_directory_structure(None) is False
        assert validate_directory_structure(123) is False


class TestConfigurationValidation:
    """Test suite for configuration file validation."""

    def test_validate_configuration_file_not_found(self, tmp_path):
        """Test configuration file validation with non-existent file."""
        config_path = tmp_path / "nonexistent.json"

        with pytest.raises(ValidationError) as exc_info:
            validate_configuration_file(config_path, None)

        assert "Configuration file not found" in str(exc_info.value)

    def test_validate_configuration_file_not_file(self, tmp_path):
        """Test configuration file validation with directory instead of file."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with pytest.raises(ValidationError) as exc_info:
            validate_configuration_file(config_dir, None)

        assert "Path is not a file" in str(exc_info.value)

    def test_validate_configuration_file_unsupported_format(self, tmp_path):
        """Test configuration file validation with unsupported format."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("test: data")

        with pytest.raises(ValidationError) as exc_info:
            validate_configuration_file(config_path, None)

        assert "Unsupported configuration file format" in str(exc_info.value)

    def test_validate_configuration_file_invalid_json(self, tmp_path):
        """Test configuration file validation with invalid JSON."""
        config_path = tmp_path / "config.json"
        config_path.write_text("{ invalid json }")

        with pytest.raises(ValidationError) as exc_info:
            validate_configuration_file(config_path, None)

        assert "Invalid JSON in configuration file" in str(exc_info.value)
