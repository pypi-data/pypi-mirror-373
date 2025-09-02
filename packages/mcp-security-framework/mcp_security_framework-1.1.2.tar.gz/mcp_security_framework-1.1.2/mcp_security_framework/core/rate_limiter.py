"""
Rate Limiter Module

This module provides comprehensive rate limiting functionality for the
MCP Security Framework. It implements flexible rate limiting with support
for multiple identifiers, configurable windows, and various storage backends.

Key Features:
- Configurable rate limiting windows
- Support for multiple identifiers (IP, user, global)
- Burst limit support
- In-memory storage backend
- Cleanup of expired entries
- Rate limit status tracking

Classes:
    RateLimiter: Main rate limiting class
    RateLimitEntry: Internal rate limit entry
    RateLimitStorage: Abstract storage interface

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Set

from ..schemas.config import RateLimitConfig
from ..schemas.models import RateLimitStatus


class RateLimitEntry:
    """
    Rate Limit Entry Class

    This class represents a single rate limit entry for tracking
    requests within a specific time window.

    Attributes:
        identifier: Rate limiting identifier
        count: Current request count
        window_start: Start time of current window
        window_size: Size of window in seconds
        limit: Maximum allowed requests
    """

    def __init__(self, identifier: str, limit: int, window_size: int):
        """
        Initialize rate limit entry.

        Args:
            identifier: Rate limiting identifier
            limit: Maximum allowed requests
            window_size: Window size in seconds
        """
        self.identifier = identifier
        self.count = 0
        self.window_start = datetime.now(timezone.utc)
        self.window_size = window_size
        self.limit = limit

    def is_expired(self) -> bool:
        """
        Check if the rate limit entry is expired.

        Returns:
            bool: True if entry is expired, False otherwise
        """
        now = datetime.now(timezone.utc)
        return (now - self.window_start).total_seconds() >= self.window_size

    def reset_window(self) -> None:
        """Reset the rate limit window."""
        self.count = 0
        self.window_start = datetime.now(timezone.utc)

    def increment(self) -> int:
        """
        Increment request count.

        Returns:
            int: New request count
        """
        self.count += 1
        return self.count

    def get_status(self) -> RateLimitStatus:
        """
        Get current rate limit status.

        Returns:
            RateLimitStatus: Current rate limit status
        """
        now = datetime.now(timezone.utc)
        window_end = self.window_start.replace(tzinfo=timezone.utc) + timedelta(
            seconds=self.window_size
        )

        is_exceeded = self.count > self.limit
        remaining_requests = max(0, self.limit - self.count)

        return RateLimitStatus(
            identifier=self.identifier,
            current_count=self.count,
            limit=self.limit,
            window_start=self.window_start,
            window_end=window_end,
            is_exceeded=is_exceeded,
            remaining_requests=remaining_requests,
            reset_time=window_end,
            window_size_seconds=self.window_size,
        )


class RateLimiter:
    """
    Rate Limiter Class

    This class provides comprehensive rate limiting functionality with
    support for multiple identifiers, configurable windows, and various
    storage backends.

    The RateLimiter implements:
    - Configurable rate limiting windows
    - Support for multiple identifiers (IP, user, global)
    - Burst limit support
    - In-memory storage backend
    - Cleanup of expired entries
    - Rate limit status tracking

    Attributes:
        config: Rate limiting configuration
        logger: Logger instance for rate limiting operations
        _entries: Dictionary of rate limit entries
        _lock: Thread lock for thread safety
        _cleanup_thread: Background cleanup thread
        _stop_cleanup: Flag to stop cleanup thread
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize Rate Limiter.

        Args:
            config: Rate limiting configuration containing limits,
                window sizes, and storage settings. Must be a valid
                RateLimitConfig instance with proper rate limiting
                parameters.

        Raises:
            ValueError: If configuration is invalid

        Example:
            >>> config = RateLimitConfig(enabled=True, default_requests_per_minute=60)
            >>> rate_limiter = RateLimiter(config)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize storage
        self._entries: Dict[str, RateLimitEntry] = {}
        self._lock = threading.RLock()

        # Initialize cleanup thread
        self._stop_cleanup = False
        self._cleanup_thread = None

        if self.config.enabled:
            self._start_cleanup_thread()

        self.logger.info(
            "Rate limiter initialized",
            extra={
                "enabled": config.enabled,
                "default_requests_per_minute": config.default_requests_per_minute,
                "window_size_seconds": config.window_size_seconds,
                "storage_backend": config.storage_backend,
            },
        )

    @property
    def is_rate_limiting_enabled(self) -> bool:
        """
        Check if rate limiting is enabled.

        Returns:
            bool: True if rate limiting is enabled, False otherwise
        """
        return self.config.enabled

    def check_rate_limit(self, identifier: str, limit: Optional[int] = None) -> bool:
        """
        Check if rate limit is exceeded for the given identifier.

        This method checks if the rate limit is exceeded for the specified
        identifier. It automatically handles window resets and burst limits.

        Args:
            identifier: Rate limiting identifier (IP, user ID, etc.)
                Must be a non-empty string identifying the request source.
            limit: Custom limit for this check. If None, uses default
                limit from configuration. Must be a positive integer.

        Returns:
            bool: True if rate limit is not exceeded, False if exceeded.
                Returns True when the request can proceed, False when
                rate limit is exceeded.

        Raises:
            ValueError: If identifier is empty or limit is invalid

        Example:
            >>> rate_limiter = RateLimiter(config)
            >>> if rate_limiter.check_rate_limit("192.168.1.1"):
            ...     # Process request
            ...     pass
            >>> else:
            ...     # Rate limit exceeded
            ...     pass
        """
        if not identifier:
            raise ValueError("Identifier cannot be empty")

        if limit is not None and limit <= 0:
            raise ValueError("Limit must be a positive integer")

        if not self.config.enabled:
            return True

        # Use default limit if not specified
        if limit is None:
            limit = self.config.default_requests_per_minute * self.config.burst_limit

        with self._lock:
            entry = self._get_or_create_entry(identifier, limit)

            # Check if window needs to be reset
            if entry.is_expired():
                entry.reset_window()
                self.logger.debug(
                    "Rate limit window reset",
                    extra={"identifier": identifier, "limit": limit},
                )

            # Check if rate limit is exceeded (including the current request)
            is_exceeded = entry.count >= limit

            if is_exceeded:
                self.logger.warning(
                    "Rate limit exceeded",
                    extra={
                        "identifier": identifier,
                        "current_count": entry.count,
                        "limit": limit,
                    },
                )
            else:
                self.logger.debug(
                    "Rate limit check passed",
                    extra={
                        "identifier": identifier,
                        "current_count": entry.count,
                        "limit": limit,
                    },
                )

            return not is_exceeded

    def increment_request_count(
        self, identifier: str, limit: Optional[int] = None
    ) -> int:
        """
        Increment request count for the given identifier.

        This method increments the request count for the specified identifier
        and returns the new count. It automatically handles window resets.

        Args:
            identifier: Rate limiting identifier (IP, user ID, etc.)
                Must be a non-empty string identifying the request source.
            limit: Custom limit for this increment. If None, uses default
                limit from configuration. Must be a positive integer.

        Returns:
            int: New request count after increment.
                Returns the updated count for the current window.

        Raises:
            ValueError: If identifier is empty or limit is invalid

        Example:
            >>> rate_limiter = RateLimiter(config)
            >>> new_count = rate_limiter.increment_request_count("192.168.1.1")
            >>> print(f"New request count: {new_count}")
        """
        if not identifier:
            raise ValueError("Identifier cannot be empty")

        if limit is not None and limit <= 0:
            raise ValueError("Limit must be a positive integer")

        if not self.config.enabled:
            return 0

        # Use default limit if not specified
        if limit is None:
            limit = self.config.default_requests_per_minute * self.config.burst_limit

        with self._lock:
            entry = self._get_or_create_entry(identifier, limit)

            # Check if window needs to be reset
            if entry.is_expired():
                entry.reset_window()
                self.logger.debug(
                    "Rate limit window reset before increment",
                    extra={"identifier": identifier, "limit": limit},
                )

            # Increment count
            new_count = entry.increment()

            self.logger.debug(
                "Request count incremented",
                extra={
                    "identifier": identifier,
                    "new_count": new_count,
                    "limit": limit,
                },
            )

            return new_count

    def reset_rate_limit(self, identifier: str) -> None:
        """
        Reset rate limit for the given identifier.

        This method completely resets the rate limit for the specified
        identifier, clearing all request counts and starting a new window.

        Args:
            identifier: Rate limiting identifier (IP, user ID, etc.)
                Must be a non-empty string identifying the request source.

        Raises:
            ValueError: If identifier is empty

        Example:
            >>> rate_limiter = RateLimiter(config)
            >>> rate_limiter.reset_rate_limit("192.168.1.1")
        """
        if not identifier:
            raise ValueError("Identifier cannot be empty")

        with self._lock:
            if identifier in self._entries:
                del self._entries[identifier]
                self.logger.info("Rate limit reset", extra={"identifier": identifier})

    def get_rate_limit_status(
        self, identifier: str, limit: Optional[int] = None
    ) -> RateLimitStatus:
        """
        Get current rate limit status for the given identifier.

        This method returns detailed information about the current rate
        limit status for the specified identifier.

        Args:
            identifier: Rate limiting identifier (IP, user ID, etc.)
                Must be a non-empty string identifying the request source.
            limit: Custom limit for status check. If None, uses default
                limit from configuration. Must be a positive integer.

        Returns:
            RateLimitStatus: Current rate limit status containing count,
                limit, window information, and reset time.

        Raises:
            ValueError: If identifier is empty or limit is invalid

        Example:
            >>> rate_limiter = RateLimiter(config)
            >>> status = rate_limiter.get_rate_limit_status("192.168.1.1")
            >>> print(f"Current count: {status.current_count}")
            >>> print(f"Remaining requests: {status.remaining_requests}")
        """
        if not identifier:
            raise ValueError("Identifier cannot be empty")

        if limit is not None and limit <= 0:
            raise ValueError("Limit must be a positive integer")

        if not self.config.enabled:
            # Return default status when rate limiting is disabled
            now = datetime.now(timezone.utc)
            return RateLimitStatus(
                identifier=identifier,
                current_count=0,
                limit=limit or self.config.default_requests_per_minute,
                window_start=now,
                window_end=now,
                is_exceeded=False,
                remaining_requests=limit or self.config.default_requests_per_minute,
                reset_time=now,
                window_size_seconds=self.config.window_size_seconds,
            )

        # Use default limit if not specified
        if limit is None:
            limit = self.config.default_requests_per_minute * self.config.burst_limit

        with self._lock:
            entry = self._get_or_create_entry(identifier, limit)

            # Check if window needs to be reset
            if entry.is_expired():
                entry.reset_window()
                self.logger.debug(
                    "Rate limit window reset during status check",
                    extra={"identifier": identifier, "limit": limit},
                )

            return entry.get_status()

    def is_exempt(
        self,
        identifier: str,
        path: Optional[str] = None,
        roles: Optional[Set[str]] = None,
    ) -> bool:
        """
        Check if the identifier is exempt from rate limiting.

        This method checks if the identifier, path, or roles are exempt
        from rate limiting based on configuration.

        Args:
            identifier: Rate limiting identifier (IP, user ID, etc.)
                Must be a non-empty string identifying the request source.
            path: Request path to check for exemption
                Optional path to check against exempt_paths configuration.
            roles: User roles to check for exemption
                Optional set of roles to check against exempt_roles configuration.

        Returns:
            bool: True if exempt from rate limiting, False otherwise.
                Returns True when the request should bypass rate limiting.

        Example:
            >>> rate_limiter = RateLimiter(config)
            >>> is_exempt = rate_limiter.is_exempt("192.168.1.1", "/health")
            >>> if is_exempt:
            ...     # Skip rate limiting
            ...     pass
        """
        if not identifier:
            return False

        # Check exempt paths
        if path and path in self.config.exempt_paths:
            self.logger.debug(
                "Rate limit exempt due to path",
                extra={"identifier": identifier, "path": path},
            )
            return True

        # Check exempt roles
        if roles and any(role in self.config.exempt_roles for role in roles):
            self.logger.debug(
                "Rate limit exempt due to role",
                extra={"identifier": identifier, "roles": list(roles)},
            )
            return True

        return False

    def cleanup_expired_entries(self) -> int:
        """
        Clean up expired rate limit entries.

        This method removes all expired rate limit entries to prevent
        memory leaks and maintain performance.

        Returns:
            int: Number of entries cleaned up.
                Returns the count of removed expired entries.

        Example:
            >>> rate_limiter = RateLimiter(config)
            >>> cleaned_count = rate_limiter.cleanup_expired_entries()
            >>> print(f"Cleaned up {cleaned_count} expired entries")
        """
        if not self.config.enabled:
            return 0

        with self._lock:
            expired_identifiers = [
                identifier
                for identifier, entry in self._entries.items()
                if entry.is_expired()
            ]

            for identifier in expired_identifiers:
                del self._entries[identifier]

            if expired_identifiers:
                self.logger.info(
                    "Cleaned up expired rate limit entries",
                    extra={
                        "cleaned_count": len(expired_identifiers),
                        "remaining_entries": len(self._entries),
                    },
                )

            return len(expired_identifiers)

    def get_statistics(self) -> Dict[str, any]:
        """
        Get rate limiter statistics.

        This method returns comprehensive statistics about the rate limiter
        including entry counts, memory usage, and performance metrics.

        Returns:
            Dict[str, any]: Rate limiter statistics containing entry counts,
                memory usage, and performance information.

        Example:
            >>> rate_limiter = RateLimiter(config)
            >>> stats = rate_limiter.get_statistics()
            >>> print(f"Active entries: {stats['active_entries']}")
        """
        with self._lock:
            active_entries = len(self._entries)
            expired_entries = sum(
                1 for entry in self._entries.values() if entry.is_expired()
            )

            return {
                "enabled": self.config.enabled,
                "active_entries": active_entries,
                "expired_entries": expired_entries,
                "total_entries": active_entries + expired_entries,
                "default_requests_per_minute": self.config.default_requests_per_minute,
                "window_size_seconds": self.config.window_size_seconds,
                "storage_backend": self.config.storage_backend,
                "cleanup_interval": self.config.cleanup_interval,
            }

    def _get_or_create_entry(self, identifier: str, limit: int) -> RateLimitEntry:
        """
        Get or create a rate limit entry for the identifier.

        Args:
            identifier: Rate limiting identifier
            limit: Request limit

        Returns:
            RateLimitEntry: Rate limit entry for the identifier
        """
        if identifier not in self._entries:
            self._entries[identifier] = RateLimitEntry(
                identifier, limit, self.config.window_size_seconds
            )

        return self._entries[identifier]

    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread."""
        if self._cleanup_thread is not None:
            return

        self._stop_cleanup = False
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker, daemon=True, name="RateLimiterCleanup"
        )
        self._cleanup_thread.start()

        self.logger.info(
            "Started rate limiter cleanup thread",
            extra={"cleanup_interval": self.config.cleanup_interval},
        )

    def _cleanup_worker(self) -> None:
        """Background cleanup worker thread."""
        while not self._stop_cleanup:
            try:
                time.sleep(self.config.cleanup_interval)
                if not self._stop_cleanup:
                    self.cleanup_expired_entries()
            except Exception as e:
                self.logger.error(
                    "Error in cleanup worker", extra={"error": str(e)}, exc_info=True
                )

    def stop_cleanup(self) -> None:
        """Stop background cleanup thread."""
        self._stop_cleanup = True
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)

        self.logger.info("Stopped rate limiter cleanup thread")

    def __del__(self):
        """Cleanup on destruction."""
        self.stop_cleanup()
