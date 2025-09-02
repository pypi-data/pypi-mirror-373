"""
Tests for Datetime Compatibility Module

This module contains tests for the datetime compatibility functions that
handle certificate datetime fields across different cryptography versions.

Test Coverage:
- Compatibility with cryptography>=42 (UTC fields)
- Compatibility with cryptography<42 (legacy fields)
- Timezone normalization
- Version detection
- Error handling

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from mcp_security_framework.utils.datetime_compat import (
    get_not_valid_after_utc,
    get_not_valid_before_utc,
    is_cryptography_42_plus,
)


class TestDatetimeCompatibility:
    """Test suite for datetime compatibility functions."""

    def test_get_not_valid_before_utc_with_utc_field(self):
        """Test get_not_valid_before_utc with cryptography>=42 UTC field."""
        # Mock certificate with UTC field (cryptography>=42)
        mock_cert = Mock()
        expected_time = datetime.now(timezone.utc)
        mock_cert.not_valid_before_utc = expected_time
        mock_cert.not_valid_before = datetime.now()  # Legacy field

        result = get_not_valid_before_utc(mock_cert)

        assert result == expected_time
        assert result.tzinfo == timezone.utc

    def test_get_not_valid_before_utc_with_legacy_field(self):
        """Test get_not_valid_before_utc with cryptography<42 legacy field."""
        # Mock certificate without UTC field (cryptography<42)
        mock_cert = Mock()
        mock_cert.not_valid_before_utc = None  # Field doesn't exist
        naive_time = datetime.now()
        mock_cert.not_valid_before = naive_time

        result = get_not_valid_before_utc(mock_cert)

        assert result.tzinfo == timezone.utc
        assert result.replace(tzinfo=None) == naive_time

    def test_get_not_valid_before_utc_with_legacy_field_already_utc(self):
        """Test get_not_valid_before_utc with legacy field that's already UTC."""
        # Mock certificate without UTC field but legacy field is already UTC
        mock_cert = Mock()
        mock_cert.not_valid_before_utc = None  # Field doesn't exist
        utc_time = datetime.now(timezone.utc)
        mock_cert.not_valid_before = utc_time

        result = get_not_valid_before_utc(mock_cert)

        assert result == utc_time
        assert result.tzinfo == timezone.utc

    def test_get_not_valid_after_utc_with_utc_field(self):
        """Test get_not_valid_after_utc with cryptography>=42 UTC field."""
        # Mock certificate with UTC field (cryptography>=42)
        mock_cert = Mock()
        expected_time = datetime.now(timezone.utc)
        mock_cert.not_valid_after_utc = expected_time
        mock_cert.not_valid_after = datetime.now()  # Legacy field

        result = get_not_valid_after_utc(mock_cert)

        assert result == expected_time
        assert result.tzinfo == timezone.utc

    def test_get_not_valid_after_utc_with_legacy_field(self):
        """Test get_not_valid_after_utc with cryptography<42 legacy field."""
        # Mock certificate without UTC field (cryptography<42)
        mock_cert = Mock()
        mock_cert.not_valid_after_utc = None  # Field doesn't exist
        naive_time = datetime.now()
        mock_cert.not_valid_after = naive_time

        result = get_not_valid_after_utc(mock_cert)

        assert result.tzinfo == timezone.utc
        assert result.replace(tzinfo=None) == naive_time

    def test_get_not_valid_after_utc_with_legacy_field_already_utc(self):
        """Test get_not_valid_after_utc with legacy field that's already UTC."""
        # Mock certificate without UTC field but legacy field is already UTC
        mock_cert = Mock()
        mock_cert.not_valid_after_utc = None  # Field doesn't exist
        utc_time = datetime.now(timezone.utc)
        mock_cert.not_valid_after = utc_time

        result = get_not_valid_after_utc(mock_cert)

        assert result == utc_time
        assert result.tzinfo == timezone.utc

    def test_is_cryptography_42_plus_basic(self):
        """Test is_cryptography_42_plus basic functionality."""
        # This test just verifies the function doesn't crash
        # and returns a boolean value
        result = is_cryptography_42_plus()

        assert isinstance(result, bool)

    def test_compatibility_integration(self):
        """Test integration of compatibility functions with real certificate-like objects."""
        # Test with object that has both fields (simulating cryptography>=42)
        mock_cert_new = Mock()
        utc_time = datetime.now(timezone.utc)
        mock_cert_new.not_valid_before_utc = utc_time
        mock_cert_new.not_valid_after_utc = utc_time

        before_result = get_not_valid_before_utc(mock_cert_new)
        after_result = get_not_valid_after_utc(mock_cert_new)

        assert before_result == utc_time
        assert after_result == utc_time

        # Test with object that has only legacy fields (simulating cryptography<42)
        mock_cert_old = Mock()
        naive_time = datetime.now()
        mock_cert_old.not_valid_before_utc = None
        mock_cert_old.not_valid_after_utc = None
        mock_cert_old.not_valid_before = naive_time
        mock_cert_old.not_valid_after = naive_time

        before_result = get_not_valid_before_utc(mock_cert_old)
        after_result = get_not_valid_after_utc(mock_cert_old)

        assert before_result.tzinfo == timezone.utc
        assert after_result.tzinfo == timezone.utc
        assert before_result.replace(tzinfo=None) == naive_time
        assert after_result.replace(tzinfo=None) == naive_time
