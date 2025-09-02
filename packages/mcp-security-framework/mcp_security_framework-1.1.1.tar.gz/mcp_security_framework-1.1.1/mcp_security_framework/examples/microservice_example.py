"""
Microservice Example Implementation

This module provides a complete example of how to implement the MCP Security Framework
in a microservice architecture, including all abstract method implementations.

The example demonstrates:
- Microservice with security framework
- Service-to-service authentication
- Rate limiting for microservices
- Certificate-based service authentication
- Production-ready security features
- Comprehensive error handling

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import aiohttp

from mcp_security_framework.constants import (
    AUTH_METHODS,
    DEFAULT_CLIENT_IP,
    DEFAULT_SECURITY_HEADERS,
    HTTP_FORBIDDEN,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    ErrorCodes,
)
from mcp_security_framework.core.auth_manager import AuthManager
from mcp_security_framework.core.permission_manager import PermissionManager
from mcp_security_framework.core.rate_limiter import RateLimiter
from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.core.ssl_manager import SSLManager
from mcp_security_framework.schemas.config import AuthConfig, SecurityConfig, SSLConfig
from mcp_security_framework.schemas.models import AuthMethod, AuthResult, AuthStatus


class MicroserviceExample:
    """
    Complete Microservice Example with Security Framework Implementation

    This class demonstrates a production-ready microservice
    with comprehensive security features including:
    - Service-to-service authentication
    - API gateway integration
    - Rate limiting for microservices
    - Certificate-based service authentication
    - Comprehensive logging and monitoring
    - Health checks and metrics
    """

    def __init__(self, service_name: str, config_path: Optional[str] = None):
        """
        Initialize microservice example with security configuration.

        Args:
            service_name: Name of the microservice
            config_path: Path to security configuration file
        """
        self.service_name = service_name
        self.config = self._load_config(config_path)
        self.security_manager = SecurityManager(self.config)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self._setup_service_registry()

    def _load_config(self, config_path: Optional[str]) -> SecurityConfig:
        """
        Load security configuration from file or create default.

        Args:
            config_path: Path to configuration file

        Returns:
            SecurityConfig: Loaded configuration
        """
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return SecurityConfig(**config_data)

        # Create production-ready microservice configuration
        return SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=[
                    AUTH_METHODS["API_KEY"],
                    AUTH_METHODS["JWT"],
                    AUTH_METHODS["CERTIFICATE"],
                ],
                api_keys={
                    "service_key_123": {
                        "username": "user-service",
                        "roles": ["service", "user"],
                    },
                    "service_key_456": {
                        "username": "order-service",
                        "roles": ["service", "order"],
                    },
                    "service_key_789": {
                        "username": "payment-service",
                        "roles": ["service", "payment"],
                    },
                },
                jwt_secret="your-super-secret-jwt-key-change-in-production",
                jwt_algorithm="HS256",
                jwt_expiry_hours=24,
                public_paths=["/health", "/metrics", "/ready"],
                security_headers=DEFAULT_SECURITY_HEADERS,
            ),
            ssl=SSLConfig(
                enabled=False,  # Disable SSL for example
                cert_file=None,
                key_file=None,
                ca_cert_file=None,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
            ),
            rate_limit={
                "enabled": True,
                "default_requests_per_minute": 1000,  # Higher for microservices
                "default_requests_per_hour": 10000,
                "burst_limit": 5,
                "window_size_seconds": 60,
                "storage_backend": "redis",
                "redis_config": {
                    "host": "redis-cluster",
                    "port": 6379,
                    "db": 0,
                    "password": None,
                },
                "exempt_paths": ["/health", "/metrics", "/ready"],
                "exempt_roles": ["service"],
            },
            permissions={
                "enabled": True,
                "roles_file": "config/roles.json",
                "default_role": "service",
                "hierarchy_enabled": True,
            },
            logging={
                "enabled": True,
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": f"logs/{self.service_name}.log",
                "max_file_size": 10,
                "backup_count": 5,
                "console_output": True,
                "json_format": True,  # JSON format for microservices
            },
        )

    def _setup_logging(self):
        """Setup logging configuration."""
        if self.config.logging.enabled:
            logging.basicConfig(
                level=getattr(logging, self.config.logging.level),
                format=self.config.logging.format,
                handlers=[
                    (
                        logging.FileHandler(self.config.logging.file_path)
                        if self.config.logging.file_path
                        else logging.NullHandler()
                    ),
                    (
                        logging.StreamHandler()
                        if self.config.logging.console_output
                        else logging.NullHandler()
                    ),
                ],
            )

    def _setup_service_registry(self):
        """Setup service registry for microservice discovery."""
        self.service_registry = {
            "user-service": {
                "url": "https://user-service:8080",
                "health_check": "/health",
                "api_key": "service_key_123",
            },
            "order-service": {
                "url": "https://order-service:8081",
                "health_check": "/health",
                "api_key": "service_key_456",
            },
            "payment-service": {
                "url": "https://payment-service:8082",
                "health_check": "/health",
                "api_key": "service_key_789",
            },
        }

    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Call another microservice with security.

        Args:
            service_name: Name of the service to call
            endpoint: Service endpoint
            method: HTTP method
            data: Request data

        Returns:
            Dict[str, Any]: Service response
        """
        try:
            if service_name not in self.service_registry:
                raise ValueError(f"Service {service_name} not found in registry")

            service_info = self.service_registry[service_name]
            url = f"{service_info['url']}{endpoint}"

            # Get service API key
            api_key = service_info["api_key"]

            # Prepare headers with authentication
            headers = {
                "X-API-Key": api_key,
                "X-Service-Name": self.service_name,
                "X-Request-ID": self._generate_request_id(),
                "Content-Type": "application/json",
            }

            # Make request with SSL context
            ssl_context = None
            if self.config.ssl.enabled:
                ssl_context = self.security_manager.ssl_manager.create_client_context()

            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(
                        url, headers=headers, ssl=ssl_context
                    ) as response:
                        return await response.json()
                elif method.upper() == "POST":
                    async with session.post(
                        url, headers=headers, json=data, ssl=ssl_context
                    ) as response:
                        return await response.json()
                elif method.upper() == "PUT":
                    async with session.put(
                        url, headers=headers, json=data, ssl=ssl_context
                    ) as response:
                        return await response.json()
                elif method.upper() == "DELETE":
                    async with session.delete(
                        url, headers=headers, ssl=ssl_context
                    ) as response:
                        return await response.json()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

        except Exception as e:
            self.logger.error(f"Service call failed: {str(e)}")
            return {
                "error": "Service call failed",
                "message": str(e),
                "service": service_name,
                "endpoint": endpoint,
            }

    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracing."""
        import uuid

        return str(uuid.uuid4())

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a microservice request with full security validation.

        Args:
            request_data: Request data including credentials and action

        Returns:
            Dict[str, Any]: Response data
        """
        try:
            # Extract request components
            credentials = request_data.get("credentials", {})
            action = request_data.get("action", "")
            resource = request_data.get("resource", "")
            identifier = request_data.get("identifier", DEFAULT_CLIENT_IP)
            request_id = request_data.get("request_id", self._generate_request_id())

            # Step 1: Rate limiting check
            if not self.check_rate_limit(identifier):
                return {
                    "success": False,
                    "error": "Rate limit exceeded",
                    "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED_ERROR,
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Step 2: Authentication
            auth_result = self.authenticate_user(credentials)
            if not auth_result.is_valid:
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "error_code": auth_result.error_code,
                    "error_message": auth_result.error_message,
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Step 3: Authorization
            required_permissions = self._get_required_permissions(action, resource)
            if not self.check_permissions(auth_result.roles, required_permissions):
                return {
                    "success": False,
                    "error": "Insufficient permissions",
                    "error_code": ErrorCodes.PERMISSION_DENIED_ERROR,
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Step 4: Process the action
            result = await self._execute_action(
                action, resource, request_data.get("data", {})
            )

            # Step 5: Log security event
            self._log_security_event(
                "request_processed",
                {
                    "username": auth_result.username,
                    "action": action,
                    "resource": resource,
                    "success": True,
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            return {
                "success": True,
                "data": result,
                "user": {
                    "username": auth_result.username,
                    "roles": auth_result.roles,
                    "auth_method": auth_result.auth_method,
                },
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Request processing failed: {str(e)}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": ErrorCodes.GENERAL_ERROR,
                "request_id": (
                    request_id
                    if "request_id" in locals()
                    else self._generate_request_id()
                ),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def authenticate_user(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate user with provided credentials.

        Args:
            credentials: User credentials (api_key, jwt_token, or certificate)

        Returns:
            AuthResult: Authentication result
        """
        try:
            if "api_key" in credentials:
                return self.security_manager.auth_manager.authenticate_api_key(
                    credentials["api_key"]
                )
            elif "jwt_token" in credentials:
                return self.security_manager.auth_manager.authenticate_jwt_token(
                    credentials["jwt_token"]
                )
            elif "certificate" in credentials:
                return self.security_manager.auth_manager.authenticate_certificate(
                    credentials["certificate"]
                )
            else:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.FAILED,
                    username=None,
                    roles=[],
                    auth_method=None,
                    error_code=ErrorCodes.AUTHENTICATION_ERROR,
                    error_message="No valid credentials provided",
                )
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=ErrorCodes.AUTHENTICATION_ERROR,
                error_message=str(e),
            )

    def check_permissions(
        self, user_roles: List[str], required_permissions: List[str]
    ) -> bool:
        """
        Check if user has required permissions.

        Args:
            user_roles: User roles
            required_permissions: Required permissions

        Returns:
            bool: True if user has required permissions
        """
        try:
            return self.security_manager.permission_manager.validate_access(
                user_roles, required_permissions
            )
        except Exception as e:
            self.logger.error(f"Permission check failed: {str(e)}")
            return False

    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if request is within rate limits.

        Args:
            identifier: Request identifier (IP, user ID, etc.)

        Returns:
            bool: True if request is within rate limits
        """
        try:
            return self.security_manager.rate_limiter.check_rate_limit(identifier)
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            return True  # Allow request if rate limiting fails

    async def _execute_action(
        self, action: str, resource: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the requested action.

        Args:
            action: Action to perform
            resource: Resource to access
            data: Action data

        Returns:
            Dict[str, Any]: Action result
        """
        # Simulate different microservice actions
        if action == "get_user":
            # Call user service
            return await self.call_service(
                "user-service", f"/api/v1/users/{data.get('user_id')}"
            )
        elif action == "create_order":
            # Call order service
            return await self.call_service(
                "order-service", "/api/v1/orders", "POST", data
            )
        elif action == "process_payment":
            # Call payment service
            return await self.call_service(
                "payment-service", "/api/v1/payments", "POST", data
            )
        elif action == "read":
            return {"resource": resource, "data": {"example": "data"}}
        elif action == "write":
            return {"resource": resource, "data": data, "status": "written"}
        else:
            return {"error": f"Unknown action: {action}"}

    def _get_required_permissions(self, action: str, resource: str) -> List[str]:
        """
        Get required permissions for action and resource.

        Args:
            action: Action to perform
            resource: Resource to access

        Returns:
            List[str]: Required permissions
        """
        # Define permission mappings for microservices
        permission_mappings = {
            "get_user": ["read", "user"],
            "create_order": ["write", "order"],
            "process_payment": ["write", "payment"],
            "read": ["read"],
            "write": ["read", "write"],
            "delete": ["read", "write", "delete"],
        }

        return permission_mappings.get(action, ["read"])

    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log security event.

        Args:
            event_type: Type of security event
            details: Event details
        """
        try:
            self.logger.info(
                f"Security event: {event_type}",
                extra={
                    "event_type": event_type,
                    "service": self.service_name,
                    "timestamp": details.get("timestamp"),
                    "username": details.get("username"),
                    "action": details.get("action"),
                    "resource": details.get("resource"),
                    "success": details.get("success"),
                    "request_id": details.get("request_id"),
                    **details,
                },
            )
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the microservice.

        Returns:
            Dict[str, Any]: Health check result
        """
        try:
            # Check security manager health
            security_healthy = self.security_manager is not None

            # Check rate limiter health
            rate_limit_healthy = self.security_manager.rate_limiter is not None

            # Check service registry health
            registry_healthy = len(self.service_registry) > 0

            # Check SSL configuration
            ssl_healthy = self.config.ssl.enabled and os.path.exists(
                self.config.ssl.cert_file
            )

            overall_healthy = all(
                [security_healthy, rate_limit_healthy, registry_healthy, ssl_healthy]
            )

            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "service": self.service_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": {
                    "security_manager": security_healthy,
                    "rate_limiter": rate_limit_healthy,
                    "service_registry": registry_healthy,
                    "ssl_configuration": ssl_healthy,
                },
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get microservice metrics.

        Returns:
            Dict[str, Any]: Metrics data
        """
        try:
            # Get rate limiter metrics
            rate_limit_stats = self.security_manager.rate_limiter.get_statistics()

            # Get security manager status
            security_status = self.get_security_status()

            return {
                "service": self.service_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "rate_limiting": rate_limit_stats,
                "security": security_status,
                "service_registry": {
                    "registered_services": len(self.service_registry),
                    "services": list(self.service_registry.keys()),
                },
            }
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {str(e)}")
            return {
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def get_security_status(self) -> Dict[str, Any]:
        """
        Get security framework status.

        Returns:
            Dict[str, Any]: Security status information
        """
        return {
            "service": self.service_name,
            "ssl_enabled": self.config.ssl.enabled,
            "auth_enabled": self.config.auth.enabled,
            "rate_limiting_enabled": self.config.rate_limit.enabled,
            "permissions_enabled": self.config.permissions.enabled,
            "logging_enabled": self.config.logging.enabled,
            "auth_methods": self.config.auth.methods,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Example usage and testing
class MicroserviceExampleTest:
    """Test class for microservice example functionality."""

    @staticmethod
    async def test_authentication():
        """Test authentication functionality."""
        example = MicroserviceExample("test-service")

        # Test API key authentication
        credentials = {"api_key": "service_key_123"}
        auth_result = example.authenticate_user(credentials)
        assert auth_result.is_valid
        assert auth_result.username == "user-service"
        assert "service" in auth_result.roles

        print("✅ API Key authentication test passed")

    @staticmethod
    async def test_permissions():
        """Test permission checking."""
        example = MicroserviceExample("test-service")

        # Test service permissions
        service_roles = ["service"]
        user_roles = ["user"]
        admin_roles = ["admin"]

        # Service should have service permissions
        assert example.check_permissions(service_roles, ["read", "write"])

        # User should have user permissions
        assert example.check_permissions(user_roles, ["read"])

        # Admin should have all permissions
        assert example.check_permissions(admin_roles, ["read", "write", "delete"])

        print("✅ Permission checking test passed")

    @staticmethod
    async def test_rate_limiting():
        """Test rate limiting functionality."""
        example = MicroserviceExample("test-service")

        # Test rate limiting
        identifier = "test_service"
        for i in range(5):
            is_allowed = example.check_rate_limit(identifier)
            print(f"Request {i+1}: {'Allowed' if is_allowed else 'Blocked'}")

        print("✅ Rate limiting test completed")

    @staticmethod
    async def test_health_check():
        """Test health check functionality."""
        example = MicroserviceExample("test-service")

        health = await example.health_check()
        assert "status" in health
        assert "service" in health
        assert health["service"] == "test-service"

        print("✅ Health check test passed")

    @staticmethod
    async def test_metrics():
        """Test metrics functionality."""
        example = MicroserviceExample("test-service")

        metrics = await example.get_metrics()
        assert "service" in metrics
        assert "timestamp" in metrics
        assert metrics["service"] == "test-service"

        print("✅ Metrics test passed")


async def main():
    """Main function for testing and example usage."""
    # Run tests
    print("Running Microservice Example Tests...")
    await MicroserviceExampleTest.test_authentication()
    await MicroserviceExampleTest.test_permissions()
    await MicroserviceExampleTest.test_rate_limiting()
    await MicroserviceExampleTest.test_health_check()
    await MicroserviceExampleTest.test_metrics()

    # Example usage
    print("\nExample Usage:")
    example = MicroserviceExample("user-service")

    # Process a request
    request_data = {
        "credentials": {"api_key": "service_key_123"},
        "action": "get_user",
        "resource": "user_data",
        "identifier": "192.168.1.100",
        "data": {"user_id": "123"},
    }

    result = await example.process_request(request_data)
    print(f"Request result: {result}")

    # Get health status
    health = await example.health_check()
    print(f"Health status: {health}")

    # Get metrics
    metrics = await example.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())

    # Start HTTP server in background for testing
    print("\nStarting Microservice HTTP Server in background...")

    import json
    import threading
    import time
    from http.server import BaseHTTPRequestHandler, HTTPServer

    import requests

    class MicroserviceHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "healthy", "service": "user-service"}
                self.wfile.write(json.dumps(response).encode())

            elif self.path == "/metrics":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "service": "user-service",
                    "requests_total": 50,
                    "requests_per_minute": 5,
                }
                self.wfile.write(json.dumps(response).encode())

            elif self.path == "/api/v1/users/123":
                api_key = self.headers.get("X-API-Key")
                if not api_key:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = {"error": "API key required"}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = {
                        "success": True,
                        "data": {
                            "user_id": "123",
                            "username": "test_user",
                            "email": "test@example.com",
                        },
                        "service": "user-service",
                    }
                    self.wfile.write(json.dumps(response).encode())

            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # Suppress logging
            pass

    def run_server():
        """Run the HTTP server."""
        server = HTTPServer(("0.0.0.0", 8081), MicroserviceHandler)
        server.serve_forever()

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    try:
        # Test server endpoints
        print("Testing Microservice server endpoints...")

        # Test health endpoint
        response = requests.get("http://localhost:8081/health", timeout=5)
        print(f"Health endpoint: {response.status_code}")

        # Test metrics endpoint
        response = requests.get("http://localhost:8081/metrics", timeout=5)
        print(f"Metrics endpoint: {response.status_code}")

        # Test API endpoint with API key
        headers = {"X-API-Key": "service_key_123"}
        response = requests.get(
            "http://localhost:8081/api/v1/users/123", headers=headers, timeout=5
        )
        print(f"API endpoint: {response.status_code}")

        print("✅ Microservice server testing completed successfully")

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Microservice server testing failed: {e}")

    print("Microservice example completed")
