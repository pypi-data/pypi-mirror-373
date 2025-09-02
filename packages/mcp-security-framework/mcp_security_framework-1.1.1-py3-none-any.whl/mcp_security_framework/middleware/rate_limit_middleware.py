"""
Rate Limit Middleware Module

This module provides specialized rate limiting middleware that focuses
solely on request rate limiting without authentication or authorization.

Key Features:
- Rate limiting-only processing
- Multiple rate limiting strategies
- Rate limit result caching
- Rate limit event logging
- Framework-agnostic design

Classes:
    RateLimitMiddleware: Rate limiting-only middleware
    RateLimitMiddlewareError: Rate limit middleware-specific error exception

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from .security_middleware import SecurityMiddleware, SecurityMiddlewareError


class RateLimitMiddlewareError(SecurityMiddlewareError):
    """Raised when rate limit middleware encounters an error."""

    def __init__(self, message: str, error_code: int = -32035):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class RateLimitMiddleware(SecurityMiddleware):
    """
    Rate Limiting-Only Middleware Class

    This class provides rate limiting-only middleware that focuses
    solely on request rate limiting without performing authentication
    or authorization checks. It's useful for scenarios where rate
    limiting is handled separately from other security concerns.

    The RateLimitMiddleware implements:
    - Rate limiting-only request processing
    - Multiple rate limiting strategies
    - Rate limit result caching
    - Rate limit event logging
    - Framework-agnostic design

    Key Responsibilities:
    - Process requests through rate limiting pipeline only
    - Handle multiple rate limiting strategies
    - Cache rate limit results for performance
    - Log rate limit events and violations
    - Provide rate limit status to downstream components

    Attributes:
        Inherits all attributes from SecurityMiddleware
        _rate_limit_cache (Dict): Cache for rate limit results
        _rate_limit_strategies (Dict): Available rate limiting strategies

    Example:
        >>> from mcp_security_framework.middleware import RateLimitMiddleware
        >>>
        >>> security_manager = SecurityManager(config)
        >>> rate_limit_middleware = RateLimitMiddleware(security_manager)
        >>> app.add_middleware(rate_limit_middleware)

    Note:
        This middleware only handles rate limiting. Authentication and
        authorization should be handled separately by other middleware
        or application logic.
    """

    def __init__(self, security_manager):
        """
        Initialize Rate Limiting-Only Middleware.

        Args:
            security_manager: Security manager instance containing
                all security components and configuration.

        Raises:
            RateLimitMiddlewareError: If initialization fails
        """
        super().__init__(security_manager)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize rate limiting strategies
        self._rate_limit_strategies = {
            "ip": self._rate_limit_by_ip,
            "user": self._rate_limit_by_user,
            "global": self._rate_limit_global,
            "path": self._rate_limit_by_path,
            "method": self._rate_limit_by_method,
        }

        self.logger.info("Rate limit middleware initialized")

    @abstractmethod
    def __call__(self, request: Any, call_next: Any) -> Any:
        """
        Process request through rate limiting middleware.

        This method implements the rate limiting-only processing
        pipeline, focusing solely on request rate limiting.

        Args:
            request: Framework-specific request object
            call_next: Framework-specific call_next function

        Returns:
            Framework-specific response object

        Raises:
            RateLimitMiddlewareError: If rate limiting processing fails
        """
        pass

    def _check_rate_limit_only(self, request: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform rate limiting-only processing.

        This method handles rate limiting without authentication
        or authorization checks.

        Args:
            request: Framework-specific request object

        Returns:
            Tuple[bool, Dict[str, Any]]: (is_allowed, rate_limit_info)

        Raises:
            RateLimitMiddlewareError: If rate limiting process fails
        """
        try:
            if not self.config.rate_limit.enabled:
                return True, {
                    "strategy": "disabled",
                    "reason": "Rate limiting disabled",
                }

            # Get rate limiting strategy from config
            strategy = (
                self.config.rate_limit.strategy
                if hasattr(self.config.rate_limit, "strategy")
                else "ip"
            )

            if strategy not in self._rate_limit_strategies:
                self.logger.warning(
                    f"Unknown rate limiting strategy: {strategy}, using 'ip'"
                )
                strategy = "ip"

            # Apply rate limiting strategy
            is_allowed, rate_limit_info = self._rate_limit_strategies[strategy](request)

            # Log rate limit event
            self._log_rate_limit_event(request, is_allowed, rate_limit_info)

            return is_allowed, rate_limit_info

        except Exception as e:
            self.logger.error(
                "Rate limiting process failed", extra={"error": str(e)}, exc_info=True
            )
            raise RateLimitMiddlewareError(
                f"Rate limiting process failed: {str(e)}", error_code=-32036
            )

    def _rate_limit_by_ip(self, request: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Rate limit by IP address.

        Args:
            request: Framework-specific request object

        Returns:
            Tuple[bool, Dict[str, Any]]: (is_allowed, rate_limit_info)
        """
        identifier = self._get_rate_limit_identifier(request)
        is_allowed = self.security_manager.rate_limiter.check_rate_limit(identifier)

        return is_allowed, {
            "strategy": "ip",
            "identifier": identifier,
            "is_allowed": is_allowed,
        }

    def _rate_limit_by_user(self, request: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Rate limit by user (requires authentication).

        Args:
            request: Framework-specific request object

        Returns:
            Tuple[bool, Dict[str, Any]]: (is_allowed, rate_limit_info)
        """
        # Try to get user identifier from request
        user_id = self._get_user_identifier(request)
        if not user_id:
            # Fall back to IP-based rate limiting
            return self._rate_limit_by_ip(request)

        is_allowed = self.security_manager.rate_limiter.check_rate_limit(
            f"user:{user_id}"
        )

        return is_allowed, {
            "strategy": "user",
            "identifier": user_id,
            "is_allowed": is_allowed,
        }

    def _rate_limit_global(self, request: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Global rate limiting (all requests).

        Args:
            request: Framework-specific request object

        Returns:
            Tuple[bool, Dict[str, Any]]: (is_allowed, rate_limit_info)
        """
        is_allowed = self.security_manager.rate_limiter.check_rate_limit("global")

        return is_allowed, {
            "strategy": "global",
            "identifier": "global",
            "is_allowed": is_allowed,
        }

    def _rate_limit_by_path(self, request: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Rate limit by request path.

        Args:
            request: Framework-specific request object

        Returns:
            Tuple[bool, Dict[str, Any]]: (is_allowed, rate_limit_info)
        """
        path = self._get_request_path(request)
        identifier = f"path:{path}"
        is_allowed = self.security_manager.rate_limiter.check_rate_limit(identifier)

        return is_allowed, {
            "strategy": "path",
            "identifier": identifier,
            "path": path,
            "is_allowed": is_allowed,
        }

    def _rate_limit_by_method(self, request: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Rate limit by HTTP method.

        Args:
            request: Framework-specific request object

        Returns:
            Tuple[bool, Dict[str, Any]]: (is_allowed, rate_limit_info)
        """
        method = self._get_request_method(request)
        identifier = f"method:{method}"
        is_allowed = self.security_manager.rate_limiter.check_rate_limit(identifier)

        return is_allowed, {
            "strategy": "method",
            "identifier": identifier,
            "method": method,
            "is_allowed": is_allowed,
        }

    def _get_user_identifier(self, request: Any) -> Optional[str]:
        """
        Get user identifier from request.

        Args:
            request: Framework-specific request object

        Returns:
            Optional[str]: User identifier if available, None otherwise
        """
        # This should be implemented by framework-specific subclasses
        # For now, return None to indicate no user identifier available
        return None

    def _get_request_method(self, request: Any) -> str:
        """
        Get HTTP method from request.

        Args:
            request: Framework-specific request object

        Returns:
            str: HTTP method
        """
        # This should be implemented by framework-specific subclasses
        return "GET"

    def _log_rate_limit_event(
        self, request: Any, is_allowed: bool, rate_limit_info: Dict[str, Any]
    ) -> None:
        """
        Log rate limit event.

        Args:
            request: Framework-specific request object
            is_allowed (bool): Whether request is allowed
            rate_limit_info (Dict[str, Any]): Rate limit information
        """
        log_level = logging.WARNING if not is_allowed else logging.DEBUG

        self.logger.log(
            log_level,
            f"Rate limit event: {'allowed' if is_allowed else 'blocked'}",
            extra={
                "event_type": "rate_limit",
                "is_allowed": is_allowed,
                "ip_address": self._get_rate_limit_identifier(request),
                "path": self._get_request_path(request),
                "method": self._get_request_method(request),
                **rate_limit_info,
            },
        )

    def get_rate_limit_status(self, identifier: str) -> Dict[str, Any]:
        """
        Get current rate limit status for an identifier.

        Args:
            identifier (str): Rate limit identifier

        Returns:
            Dict[str, Any]: Rate limit status information
        """
        try:
            status = self.security_manager.rate_limiter.get_rate_limit_status(
                identifier
            )
            return {
                "identifier": identifier,
                "current_count": status.current_count,
                "limit": status.limit,
                "window_seconds": status.window_seconds,
                "remaining": status.remaining,
                "reset_time": status.reset_time,
            }
        except Exception as e:
            self.logger.error(
                "Failed to get rate limit status",
                extra={"identifier": identifier, "error": str(e)},
            )
            return {"identifier": identifier, "error": str(e)}

    def reset_rate_limit(self, identifier: str) -> bool:
        """
        Reset rate limit for an identifier.

        Args:
            identifier (str): Rate limit identifier

        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            self.security_manager.rate_limiter.reset_rate_limit(identifier)
            self.logger.info("Rate limit reset", extra={"identifier": identifier})
            return True
        except Exception as e:
            self.logger.error(
                "Failed to reset rate limit",
                extra={"identifier": identifier, "error": str(e)},
            )
            return False

    def get_rate_limit_statistics(self) -> Dict[str, Any]:
        """
        Get rate limiting statistics.

        Returns:
            Dict[str, Any]: Rate limiting statistics
        """
        try:
            # This would need to be implemented based on the rate limiter
            # implementation to provide actual statistics
            return {
                "total_requests": 0,
                "blocked_requests": 0,
                "active_identifiers": 0,
                "cache_hits": 0,
                "cache_misses": 0,
            }
        except Exception as e:
            self.logger.error(
                "Failed to get rate limit statistics", extra={"error": str(e)}
            )
            return {"error": str(e)}
