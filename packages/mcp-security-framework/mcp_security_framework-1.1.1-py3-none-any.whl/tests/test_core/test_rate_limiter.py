"""
Rate Limiter Tests Module

This module provides comprehensive tests for the RateLimiter class,
covering all functionality including rate limiting, window management,
cleanup, and edge cases.

Test Coverage:
- Basic rate limiting functionality
- Window reset behavior
- Multiple identifiers
- Exempt paths and roles
- Cleanup functionality
- Thread safety
- Edge cases and error conditions

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from mcp_security_framework.core.rate_limiter import RateLimitEntry, RateLimiter
from mcp_security_framework.schemas.config import RateLimitConfig
from mcp_security_framework.schemas.models import RateLimitStatus


class TestRateLimitEntry:
    """Test suite for RateLimitEntry class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.identifier = "test_identifier"
        self.limit = 10
        self.window_size = 60
        self.entry = RateLimitEntry(self.identifier, self.limit, self.window_size)

    def test_rate_limit_entry_initialization(self):
        """Test RateLimitEntry initialization."""
        assert self.entry.identifier == self.identifier
        assert self.entry.count == 0
        assert self.entry.limit == self.limit
        assert self.entry.window_size == self.window_size
        assert isinstance(self.entry.window_start, datetime)

    def test_rate_limit_entry_increment(self):
        """Test request count increment."""
        initial_count = self.entry.count
        new_count = self.entry.increment()

        assert new_count == initial_count + 1
        assert self.entry.count == new_count

    def test_rate_limit_entry_is_expired_false(self):
        """Test is_expired returns False for non-expired entry."""
        assert not self.entry.is_expired()

    def test_rate_limit_entry_is_expired_true(self):
        """Test is_expired returns True for expired entry."""
        # Manually set window start to past
        self.entry.window_start = datetime.now(timezone.utc) - timedelta(
            seconds=self.window_size + 1
        )
        assert self.entry.is_expired()

    def test_rate_limit_entry_reset_window(self):
        """Test window reset functionality."""
        # Increment count first
        self.entry.increment()
        self.entry.increment()
        assert self.entry.count == 2

        # Store original window start
        original_start = self.entry.window_start

        # Reset window
        self.entry.reset_window()

        assert self.entry.count == 0
        assert self.entry.window_start > original_start

    def test_rate_limit_entry_get_status(self):
        """Test get_status method."""
        # Increment count
        self.entry.increment()
        self.entry.increment()

        status = self.entry.get_status()

        assert isinstance(status, RateLimitStatus)
        assert status.identifier == self.identifier
        assert status.current_count == 2
        assert status.limit == self.limit
        assert status.is_exceeded is False
        assert status.remaining_requests == self.limit - 2
        assert status.window_size_seconds == self.window_size

    def test_rate_limit_entry_get_status_exceeded(self):
        """Test get_status when limit is exceeded."""
        # Increment beyond limit
        for _ in range(self.limit + 1):
            self.entry.increment()

        status = self.entry.get_status()

        assert status.is_exceeded is True
        assert status.remaining_requests == 0
        assert status.current_count > self.limit


class TestRateLimiter:
    """Test suite for RateLimiter class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.config = RateLimitConfig(
            enabled=True,
            default_requests_per_minute=10,
            window_size_seconds=60,
            cleanup_interval=300,
            exempt_paths=["/health", "/metrics"],
            exempt_roles=["admin", "monitor"],
        )
        self.rate_limiter = RateLimiter(self.config)

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self, "rate_limiter"):
            self.rate_limiter.stop_cleanup()

    def test_rate_limiter_initialization(self):
        """Test RateLimiter initialization."""
        assert self.rate_limiter.config == self.config
        assert self.rate_limiter.config.enabled is True
        assert self.rate_limiter.config.default_requests_per_minute == 10
        assert self.rate_limiter.config.window_size_seconds == 60

    def test_rate_limiter_initialization_disabled(self):
        """Test RateLimiter initialization when disabled."""
        config = RateLimitConfig(enabled=False)
        rate_limiter = RateLimiter(config)

        assert rate_limiter.config.enabled is False
        rate_limiter.stop_cleanup()

    def test_check_rate_limit_basic(self):
        """Test basic rate limit checking."""
        identifier = "test_ip"

        # First 20 requests should pass (10 * burst_limit = 20)
        for i in range(20):
            assert self.rate_limiter.check_rate_limit(identifier) is True
            self.rate_limiter.increment_request_count(identifier)

        # 21st request should fail
        assert self.rate_limiter.check_rate_limit(identifier) is False

    def test_check_rate_limit_custom_limit(self):
        """Test rate limit checking with custom limit."""
        identifier = "test_ip"
        custom_limit = 5

        # First 5 requests should pass (custom limit overrides burst_limit)
        for i in range(5):
            assert self.rate_limiter.check_rate_limit(identifier, custom_limit) is True
            self.rate_limiter.increment_request_count(identifier, custom_limit)

        # 6th request should fail
        assert self.rate_limiter.check_rate_limit(identifier, custom_limit) is False

    def test_check_rate_limit_disabled(self):
        """Test rate limit checking when disabled."""
        config = RateLimitConfig(enabled=False)
        rate_limiter = RateLimiter(config)

        identifier = "test_ip"

        # All requests should pass when disabled
        for i in range(20):
            assert rate_limiter.check_rate_limit(identifier) is True

        rate_limiter.stop_cleanup()

    def test_check_rate_limit_empty_identifier(self):
        """Test rate limit checking with empty identifier."""
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            self.rate_limiter.check_rate_limit("")

    def test_check_rate_limit_invalid_limit(self):
        """Test rate limit checking with invalid limit."""
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            self.rate_limiter.check_rate_limit("test_ip", 0)

        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            self.rate_limiter.check_rate_limit("test_ip", -1)

    def test_increment_request_count_basic(self):
        """Test basic request count increment."""
        identifier = "test_ip"

        # Increment count
        count = self.rate_limiter.increment_request_count(identifier)
        assert count == 1

        count = self.rate_limiter.increment_request_count(identifier)
        assert count == 2

    def test_increment_request_count_custom_limit(self):
        """Test request count increment with custom limit."""
        identifier = "test_ip"
        custom_limit = 5

        count = self.rate_limiter.increment_request_count(identifier, custom_limit)
        assert count == 1

    def test_increment_request_count_disabled(self):
        """Test request count increment when disabled."""
        config = RateLimitConfig(enabled=False)
        rate_limiter = RateLimiter(config)

        identifier = "test_ip"
        count = rate_limiter.increment_request_count(identifier)
        assert count == 0

        rate_limiter.stop_cleanup()

    def test_increment_request_count_empty_identifier(self):
        """Test request count increment with empty identifier."""
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            self.rate_limiter.increment_request_count("")

    def test_increment_request_count_invalid_limit(self):
        """Test request count increment with invalid limit."""
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            self.rate_limiter.increment_request_count("test_ip", 0)

    def test_reset_rate_limit(self):
        """Test rate limit reset functionality."""
        identifier = "test_ip"

        # Increment count
        self.rate_limiter.increment_request_count(identifier)
        self.rate_limiter.increment_request_count(identifier)

        # Check that limit is approaching
        assert self.rate_limiter.check_rate_limit(identifier) is True

        # Reset rate limit
        self.rate_limiter.reset_rate_limit(identifier)

        # Should be able to make requests again
        for i in range(20):  # 10 * burst_limit = 20
            assert self.rate_limiter.check_rate_limit(identifier) is True
            self.rate_limiter.increment_request_count(identifier)

    def test_reset_rate_limit_empty_identifier(self):
        """Test rate limit reset with empty identifier."""
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            self.rate_limiter.reset_rate_limit("")

    def test_get_rate_limit_status_basic(self):
        """Test basic rate limit status retrieval."""
        identifier = "test_ip"

        # Get initial status
        status = self.rate_limiter.get_rate_limit_status(identifier)

        assert isinstance(status, RateLimitStatus)
        assert status.identifier == identifier
        assert status.current_count == 0
        assert (
            status.limit
            == self.config.default_requests_per_minute * self.config.burst_limit
        )
        assert status.is_exceeded is False
        assert (
            status.remaining_requests
            == self.config.default_requests_per_minute * self.config.burst_limit
        )

    def test_get_rate_limit_status_with_increments(self):
        """Test rate limit status after increments."""
        identifier = "test_ip"

        # Increment count
        self.rate_limiter.increment_request_count(identifier)
        self.rate_limiter.increment_request_count(identifier)

        status = self.rate_limiter.get_rate_limit_status(identifier)

        assert status.current_count == 2
        assert status.is_exceeded is False
        assert (
            status.remaining_requests
            == (self.config.default_requests_per_minute * self.config.burst_limit) - 2
        )

    def test_get_rate_limit_status_exceeded(self):
        """Test rate limit status when exceeded."""
        identifier = "test_ip"

        # Increment beyond limit
        for _ in range(
            (self.config.default_requests_per_minute * self.config.burst_limit) + 1
        ):
            self.rate_limiter.increment_request_count(identifier)

        status = self.rate_limiter.get_rate_limit_status(identifier)

        assert status.is_exceeded is True
        assert status.remaining_requests == 0

    def test_get_rate_limit_status_disabled(self):
        """Test rate limit status when disabled."""
        config = RateLimitConfig(enabled=False)
        rate_limiter = RateLimiter(config)

        identifier = "test_ip"
        status = rate_limiter.get_rate_limit_status(identifier)

        assert status.current_count == 0
        assert status.is_exceeded is False
        assert status.remaining_requests == config.default_requests_per_minute

        rate_limiter.stop_cleanup()

    def test_get_rate_limit_status_empty_identifier(self):
        """Test rate limit status with empty identifier."""
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            self.rate_limiter.get_rate_limit_status("")

    def test_get_rate_limit_status_invalid_limit(self):
        """Test rate limit status with invalid limit."""
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            self.rate_limiter.get_rate_limit_status("test_ip", 0)

    def test_is_exempt_path(self):
        """Test exemption based on path."""
        identifier = "test_ip"
        exempt_path = "/health"
        non_exempt_path = "/api/data"

        assert self.rate_limiter.is_exempt(identifier, path=exempt_path) is True
        assert self.rate_limiter.is_exempt(identifier, path=non_exempt_path) is False

    def test_is_exempt_roles(self):
        """Test exemption based on roles."""
        identifier = "test_ip"
        exempt_roles = {"admin"}
        non_exempt_roles = {"user"}

        assert self.rate_limiter.is_exempt(identifier, roles=exempt_roles) is True
        assert self.rate_limiter.is_exempt(identifier, roles=non_exempt_roles) is False

    def test_is_exempt_empty_identifier(self):
        """Test exemption with empty identifier."""
        assert self.rate_limiter.is_exempt("", path="/health") is False
        assert self.rate_limiter.is_exempt("", roles={"admin"}) is False

    def test_cleanup_expired_entries(self):
        """Test cleanup of expired entries."""
        identifier = "test_ip"

        # Create an entry
        self.rate_limiter.increment_request_count(identifier)

        # Manually expire the entry
        entry = self.rate_limiter._entries[identifier]
        entry.window_start = datetime.now(timezone.utc) - timedelta(
            seconds=self.config.window_size_seconds + 1
        )

        # Cleanup should remove expired entry
        cleaned_count = self.rate_limiter.cleanup_expired_entries()

        assert cleaned_count == 1
        assert identifier not in self.rate_limiter._entries

    def test_cleanup_expired_entries_disabled(self):
        """Test cleanup when rate limiting is disabled."""
        config = RateLimitConfig(enabled=False)
        rate_limiter = RateLimiter(config)

        cleaned_count = rate_limiter.cleanup_expired_entries()
        assert cleaned_count == 0

        rate_limiter.stop_cleanup()

    def test_get_statistics(self):
        """Test statistics retrieval."""
        identifier = "test_ip"

        # Create some entries
        self.rate_limiter.increment_request_count(identifier)
        self.rate_limiter.increment_request_count("another_ip")

        stats = self.rate_limiter.get_statistics()

        assert stats["enabled"] is True
        assert stats["active_entries"] == 2
        assert (
            stats["default_requests_per_minute"]
            == self.config.default_requests_per_minute
        )
        assert stats["window_size_seconds"] == self.config.window_size_seconds
        assert stats["storage_backend"] == self.config.storage_backend
        assert stats["cleanup_interval"] == self.config.cleanup_interval

    def test_window_reset_behavior(self):
        """Test window reset behavior."""
        identifier = "test_ip"

        # Use a short window for testing
        config = RateLimitConfig(
            enabled=True,
            default_requests_per_minute=5,
            burst_limit=1,  # Set burst_limit to 1 for this test
            window_size_seconds=1,  # 1 second window
        )
        rate_limiter = RateLimiter(config)

        # Make requests up to limit
        for i in range(5):
            assert rate_limiter.check_rate_limit(identifier) is True
            rate_limiter.increment_request_count(identifier)

        # Next request should be blocked
        assert rate_limiter.check_rate_limit(identifier) is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be able to make requests again
        assert rate_limiter.check_rate_limit(identifier) is True

        rate_limiter.stop_cleanup()

    def test_multiple_identifiers(self):
        """Test rate limiting with multiple identifiers."""
        identifier1 = "ip_1"
        identifier2 = "ip_2"

        # Both should be able to make requests independently
        for i in range(5):
            assert self.rate_limiter.check_rate_limit(identifier1) is True
            assert self.rate_limiter.check_rate_limit(identifier2) is True
            self.rate_limiter.increment_request_count(identifier1)
            self.rate_limiter.increment_request_count(identifier2)

        # Both should still have remaining requests
        status1 = self.rate_limiter.get_rate_limit_status(identifier1)
        status2 = self.rate_limiter.get_rate_limit_status(identifier2)

        assert status1.remaining_requests == 15  # 20 - 5 = 15
        assert status2.remaining_requests == 15  # 20 - 5 = 15

    def test_thread_safety(self):
        """Test thread safety of rate limiter."""
        import threading

        identifier = "test_ip"
        results = []
        errors = []

        def make_requests():
            try:
                for i in range(5):
                    result = self.rate_limiter.check_rate_limit(identifier)
                    if result:
                        self.rate_limiter.increment_request_count(identifier)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should not have any errors
        assert len(errors) == 0

        # Should have proper rate limiting
        total_requests = sum(1 for r in results if r)
        assert (
            total_requests
            <= self.config.default_requests_per_minute * self.config.burst_limit
        )

    def test_rate_limit_status_properties(self):
        """Test RateLimitStatus properties."""
        identifier = "test_ip"

        # Get status
        status = self.rate_limiter.get_rate_limit_status(identifier)

        # Test seconds_until_reset property
        seconds_until_reset = status.seconds_until_reset
        assert isinstance(seconds_until_reset, int)
        assert seconds_until_reset >= 0

        # Test utilization_percentage property
        utilization = status.utilization_percentage
        assert isinstance(utilization, float)
        assert utilization == 0.0  # No requests made yet

        # Make some requests and check utilization
        self.rate_limiter.increment_request_count(identifier)
        self.rate_limiter.increment_request_count(identifier)

        status = self.rate_limiter.get_rate_limit_status(identifier)
        utilization = status.utilization_percentage
        assert utilization == 10.0  # 2 out of 20 requests = 10%

    @pytest.mark.slow
    def test_cleanup_thread_functionality(self):
        """Test background cleanup thread functionality."""
        identifier = "test_ip"

        # Create an entry
        self.rate_limiter.increment_request_count(identifier)

        # Manually expire the entry
        entry = self.rate_limiter._entries[identifier]
        entry.window_start = datetime.now(timezone.utc) - timedelta(
            seconds=self.config.window_size_seconds + 1
        )

        # Manually trigger cleanup
        cleaned_count = self.rate_limiter.cleanup_expired_entries()

        # Entry should be cleaned up
        assert cleaned_count == 1
        assert identifier not in self.rate_limiter._entries

    def test_rate_limiter_destruction(self):
        """Test rate limiter destruction cleanup."""
        config = RateLimitConfig(enabled=True, cleanup_interval=1)
        rate_limiter = RateLimiter(config)

        # Verify cleanup thread is running
        assert rate_limiter._cleanup_thread is not None
        assert rate_limiter._cleanup_thread.is_alive()

        # Destroy rate limiter
        rate_limiter.stop_cleanup()

        # Thread should be stopped
        assert rate_limiter._stop_cleanup is True

    def test_rate_limiter_with_burst_limit(self):
        """Test rate limiter with burst limit configuration."""
        config = RateLimitConfig(
            enabled=True,
            default_requests_per_minute=10,
            burst_limit=3,
            window_size_seconds=60,
        )
        rate_limiter = RateLimiter(config)

        identifier = "test_ip"

        # Should be able to make burst_limit * default_requests_per_minute requests
        burst_limit_total = config.burst_limit * config.default_requests_per_minute

        # Check that we can make exactly burst_limit_total requests
        for i in range(burst_limit_total):
            assert rate_limiter.check_rate_limit(identifier) is True
            rate_limiter.increment_request_count(identifier)

        # Next request should be blocked
        assert rate_limiter.check_rate_limit(identifier) is False

        rate_limiter.stop_cleanup()

    def test_rate_limiter_edge_cases(self):
        """Test rate limiter edge cases."""
        # Test with very high limits
        config = RateLimitConfig(
            enabled=True, default_requests_per_minute=10000, window_size_seconds=3600
        )
        rate_limiter = RateLimiter(config)

        identifier = "test_ip"

        # Should handle high limits correctly
        for i in range(100):
            assert rate_limiter.check_rate_limit(identifier) is True
            rate_limiter.increment_request_count(identifier)

        status = rate_limiter.get_rate_limit_status(identifier)
        assert status.current_count == 100
        assert status.remaining_requests == 19900  # 20000 - 100 = 19900

        rate_limiter.stop_cleanup()

        # Test with very low limits
        config = RateLimitConfig(
            enabled=True,
            default_requests_per_minute=1,
            burst_limit=1,  # Set burst_limit to 1 for this test
            window_size_seconds=1,
        )
        rate_limiter = RateLimiter(config)

        identifier = "test_ip"

        # First request should pass
        assert rate_limiter.check_rate_limit(identifier) is True
        rate_limiter.increment_request_count(identifier)

        # Second request should fail
        assert rate_limiter.check_rate_limit(identifier) is False

        rate_limiter.stop_cleanup()
