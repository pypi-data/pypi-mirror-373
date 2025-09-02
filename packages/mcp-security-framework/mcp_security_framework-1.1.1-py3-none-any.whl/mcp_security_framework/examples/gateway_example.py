"""
API Gateway Example Implementation

This module provides a complete example of how to implement the MCP Security Framework
in an API Gateway, including all abstract method implementations for real server usage.

The example demonstrates:
- API Gateway with security framework
- Request routing and load balancing
- Rate limiting at gateway level
- Certificate-based authentication
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


class APIGatewayExample:
    """
    Complete API Gateway Example with Security Framework Implementation

    This class demonstrates a production-ready API Gateway
    with comprehensive security features including:
    - Request routing and load balancing
    - Gateway-level authentication and authorization
    - Rate limiting at gateway level
    - Certificate-based authentication
    - Request/response transformation
    - Comprehensive logging and monitoring
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API Gateway example with security configuration.

        Args:
            config_path: Path to security configuration file
        """
        self.config = self._load_config(config_path)
        self.security_manager = SecurityManager(self.config)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self._setup_routing_rules()
        self._setup_load_balancer()

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

        # Create production-ready API Gateway configuration
        return SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=[
                    AUTH_METHODS["API_KEY"],
                    AUTH_METHODS["JWT"],
                    AUTH_METHODS["CERTIFICATE"],
                ],
                api_keys={
                    "gateway_key_123": {
                        "username": "gateway-admin",
                        "roles": ["gateway", "admin"],
                    },
                    "client_key_456": {
                        "username": "client-app",
                        "roles": ["client", "user"],
                    },
                    "service_key_789": {
                        "username": "internal-service",
                        "roles": ["service", "internal"],
                    },
                },
                jwt_secret="your-super-secret-jwt-key-change-in-production",
                jwt_algorithm="HS256",
                jwt_expiry_hours=24,
                public_paths=["/health", "/metrics", "/status"],
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
                "default_requests_per_minute": 500,  # Gateway-level limits
                "default_requests_per_hour": 5000,
                "burst_limit": 10,
                "window_size_seconds": 60,
                "storage_backend": "redis",
                "redis_config": {
                    "host": "redis-cluster",
                    "port": 6379,
                    "db": 0,
                    "password": None,
                },
                "exempt_paths": ["/health", "/metrics", "/status"],
                "exempt_roles": ["gateway", "admin"],
            },
            permissions={
                "enabled": True,
                "roles_file": "config/roles.json",
                "default_role": "user",
                "hierarchy_enabled": True,
            },
            logging={
                "enabled": True,
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": "logs/gateway.log",
                "max_file_size": 10,
                "backup_count": 5,
                "console_output": True,
                "json_format": True,
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

    def _setup_routing_rules(self):
        """Setup routing rules for different services."""
        self.routing_rules = {
            "/api/v1/users": {
                "service": "user-service",
                "endpoints": [
                    "https://user-service-1:8080",
                    "https://user-service-2:8080",
                ],
                "timeout": 30,
                "retries": 3,
                "required_permissions": ["read", "user"],
            },
            "/api/v1/orders": {
                "service": "order-service",
                "endpoints": [
                    "https://order-service-1:8081",
                    "https://order-service-2:8081",
                ],
                "timeout": 60,
                "retries": 3,
                "required_permissions": ["read", "write", "order"],
            },
            "/api/v1/payments": {
                "service": "payment-service",
                "endpoints": [
                    "https://payment-service-1:8082",
                    "https://payment-service-2:8082",
                ],
                "timeout": 45,
                "retries": 2,
                "required_permissions": ["write", "payment"],
            },
            "/api/v1/admin": {
                "service": "admin-service",
                "endpoints": ["https://admin-service:8083"],
                "timeout": 30,
                "retries": 1,
                "required_permissions": ["admin"],
            },
        }

    def _setup_load_balancer(self):
        """Setup load balancer for service endpoints."""
        self.load_balancer = {
            "algorithm": "round_robin",  # round_robin, least_connections, weighted
            "health_check_interval": 30,
            "health_check_timeout": 5,
            "max_failures": 3,
        }
        self.current_endpoint_index = {}  # Track current endpoint for round-robin

    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request through API Gateway with security validation.

        Args:
            request_data: Request data including path, method, headers, body

        Returns:
            Dict[str, Any]: Response data
        """
        try:
            # Extract request components
            path = request_data.get("path", "")
            method = request_data.get("method", "GET")
            headers = request_data.get("headers", {})
            body = request_data.get("body", {})
            client_ip = request_data.get("client_ip", DEFAULT_CLIENT_IP)
            request_id = request_data.get("request_id", self._generate_request_id())

            # Step 1: Rate limiting check
            if not self.check_rate_limit(client_ip):
                return self._create_error_response(
                    "Rate limit exceeded",
                    ErrorCodes.RATE_LIMIT_EXCEEDED_ERROR,
                    HTTP_TOO_MANY_REQUESTS,
                    request_id,
                )

            # Step 2: Authentication
            auth_result = self.authenticate_request(headers)
            if not auth_result.is_valid:
                return self._create_error_response(
                    "Authentication failed",
                    auth_result.error_code,
                    HTTP_UNAUTHORIZED,
                    request_id,
                    auth_result.error_message,
                )

            # Step 3: Find routing rule
            routing_rule = self._find_routing_rule(path)
            if not routing_rule:
                return self._create_error_response(
                    "Service not found", ErrorCodes.GENERAL_ERROR, 404, request_id
                )

            # Step 4: Authorization check
            if not self.check_permissions(
                auth_result.roles, routing_rule["required_permissions"]
            ):
                return self._create_error_response(
                    "Insufficient permissions",
                    ErrorCodes.PERMISSION_DENIED_ERROR,
                    HTTP_FORBIDDEN,
                    request_id,
                )

            # Step 5: Route request to backend service
            response = await self._forward_request(
                routing_rule, method, path, headers, body, request_id
            )

            # Step 6: Log security event
            self._log_security_event(
                "request_routed",
                {
                    "username": auth_result.username,
                    "path": path,
                    "method": method,
                    "service": routing_rule["service"],
                    "success": True,
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            return response

        except Exception as e:
            self.logger.error(f"Request routing failed: {str(e)}")
            return self._create_error_response(
                "Internal server error",
                ErrorCodes.GENERAL_ERROR,
                500,
                request_id if "request_id" in locals() else self._generate_request_id(),
            )

    def authenticate_request(self, headers: Dict[str, str]) -> AuthResult:
        """
        Authenticate request using headers.

        Args:
            headers: Request headers

        Returns:
            AuthResult: Authentication result
        """
        try:
            # Try API key authentication
            api_key = headers.get("X-API-Key") or headers.get(
                "Authorization", ""
            ).replace("Bearer ", "")
            if api_key:
                return self.security_manager.auth_manager.authenticate_api_key(api_key)

            # Try JWT authentication
            auth_header = headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                return self.security_manager.auth_manager.authenticate_jwt_token(token)

            # Try certificate authentication (would be handled at TLS level)
            client_cert = headers.get("X-Client-Cert")
            if client_cert:
                return self.security_manager.auth_manager.authenticate_certificate(
                    client_cert
                )

            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=ErrorCodes.AUTHENTICATION_ERROR,
                error_message="No valid authentication credentials found",
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

    def _find_routing_rule(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Find routing rule for the given path.

        Args:
            path: Request path

        Returns:
            Optional[Dict[str, Any]]: Routing rule or None
        """
        for route_path, rule in self.routing_rules.items():
            if path.startswith(route_path):
                return rule
        return None

    async def _forward_request(
        self,
        routing_rule: Dict[str, Any],
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Dict[str, Any],
        request_id: str,
    ) -> Dict[str, Any]:
        """
        Forward request to backend service.

        Args:
            routing_rule: Routing rule for the service
            method: HTTP method
            path: Request path
            headers: Request headers
            body: Request body
            request_id: Request ID

        Returns:
            Dict[str, Any]: Response from backend service
        """
        try:
            # Select endpoint using load balancer
            endpoint = self._select_endpoint(
                routing_rule["service"], routing_rule["endpoints"]
            )

            # Prepare headers for backend service
            backend_headers = {
                **headers,
                "X-Request-ID": request_id,
                "X-Gateway": "true",
                "X-Forwarded-For": headers.get("X-Forwarded-For", DEFAULT_CLIENT_IP),
                "X-Original-Path": path,
            }

            # Create SSL context if needed
            ssl_context = None
            if self.config.ssl.enabled:
                ssl_context = self.security_manager.ssl_manager.create_client_context()

            # Make request to backend service
            timeout = aiohttp.ClientTimeout(total=routing_rule["timeout"])

            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"{endpoint}{path}"

                if method.upper() == "GET":
                    async with session.get(
                        url, headers=backend_headers, ssl=ssl_context
                    ) as response:
                        return await self._process_response(response, request_id)
                elif method.upper() == "POST":
                    async with session.post(
                        url, headers=backend_headers, json=body, ssl=ssl_context
                    ) as response:
                        return await self._process_response(response, request_id)
                elif method.upper() == "PUT":
                    async with session.put(
                        url, headers=backend_headers, json=body, ssl=ssl_context
                    ) as response:
                        return await self._process_response(response, request_id)
                elif method.upper() == "DELETE":
                    async with session.delete(
                        url, headers=backend_headers, ssl=ssl_context
                    ) as response:
                        return await self._process_response(response, request_id)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

        except Exception as e:
            self.logger.error(f"Request forwarding failed: {str(e)}")
            return self._create_error_response(
                "Backend service unavailable", ErrorCodes.GENERAL_ERROR, 503, request_id
            )

    def _select_endpoint(self, service: str, endpoints: List[str]) -> str:
        """
        Select endpoint using load balancer algorithm.

        Args:
            service: Service name
            endpoints: List of available endpoints

        Returns:
            str: Selected endpoint
        """
        if not endpoints:
            raise ValueError(f"No endpoints available for service: {service}")

        if self.load_balancer["algorithm"] == "round_robin":
            # Simple round-robin implementation
            if service not in self.current_endpoint_index:
                self.current_endpoint_index[service] = 0

            endpoint = endpoints[self.current_endpoint_index[service]]
            self.current_endpoint_index[service] = (
                self.current_endpoint_index[service] + 1
            ) % len(endpoints)
            return endpoint
        else:
            # Default to first endpoint
            return endpoints[0]

    async def _process_response(
        self, response: aiohttp.ClientResponse, request_id: str
    ) -> Dict[str, Any]:
        """
        Process response from backend service.

        Args:
            response: Response from backend service
            request_id: Request ID

        Returns:
            Dict[str, Any]: Processed response
        """
        try:
            response_data = await response.json()

            # Add gateway headers
            response_headers = {
                "X-Gateway": "true",
                "X-Request-ID": request_id,
                "X-Response-Time": str(response.headers.get("X-Response-Time", "")),
                **DEFAULT_SECURITY_HEADERS,
            }

            return {
                "success": True,
                "status_code": response.status,
                "headers": response_headers,
                "data": response_data,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Response processing failed: {str(e)}")
            return self._create_error_response(
                "Response processing failed", ErrorCodes.GENERAL_ERROR, 500, request_id
            )

    def _create_error_response(
        self,
        message: str,
        error_code: int,
        status_code: int,
        request_id: str,
        details: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create error response.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            request_id: Request ID
            details: Additional error details

        Returns:
            Dict[str, Any]: Error response
        """
        return {
            "success": False,
            "error": message,
            "error_code": error_code,
            "status_code": status_code,
            "request_id": request_id,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracing."""
        import uuid

        return str(uuid.uuid4())

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
                    "gateway": "api-gateway",
                    "timestamp": details.get("timestamp"),
                    "username": details.get("username"),
                    "path": details.get("path"),
                    "method": details.get("method"),
                    "service": details.get("service"),
                    "success": details.get("success"),
                    "request_id": details.get("request_id"),
                    **details,
                },
            )
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the API Gateway.

        Returns:
            Dict[str, Any]: Health check result
        """
        try:
            # Check security manager health
            security_healthy = self.security_manager is not None

            # Check rate limiter health
            rate_limit_healthy = self.security_manager.rate_limiter is not None

            # Check routing rules
            routing_healthy = len(self.routing_rules) > 0

            # Check SSL configuration
            ssl_healthy = self.config.ssl.enabled and os.path.exists(
                self.config.ssl.cert_file
            )

            overall_healthy = all(
                [security_healthy, rate_limit_healthy, routing_healthy, ssl_healthy]
            )

            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "gateway": "api-gateway",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": {
                    "security_manager": security_healthy,
                    "rate_limiter": rate_limit_healthy,
                    "routing_rules": routing_healthy,
                    "ssl_configuration": ssl_healthy,
                },
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "gateway": "api-gateway",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get API Gateway metrics.

        Returns:
            Dict[str, Any]: Metrics data
        """
        try:
            # Get rate limiter metrics
            rate_limit_stats = self.security_manager.rate_limiter.get_statistics()

            # Get routing statistics
            routing_stats = {
                "total_routes": len(self.routing_rules),
                "services": list(
                    set(rule["service"] for rule in self.routing_rules.values())
                ),
                "load_balancer_algorithm": self.load_balancer["algorithm"],
            }

            return {
                "gateway": "api-gateway",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "rate_limiting": rate_limit_stats,
                "routing": routing_stats,
                "security": self.get_security_status(),
            }
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {str(e)}")
            return {
                "gateway": "api-gateway",
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
            "gateway": "api-gateway",
            "ssl_enabled": self.config.ssl.enabled,
            "auth_enabled": self.config.auth.enabled,
            "rate_limiting_enabled": self.config.rate_limit.enabled,
            "permissions_enabled": self.config.permissions.enabled,
            "logging_enabled": self.config.logging.enabled,
            "auth_methods": self.config.auth.methods,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Example usage and testing
class APIGatewayExampleTest:
    """Test class for API Gateway example functionality."""

    @staticmethod
    async def test_authentication():
        """Test authentication functionality."""
        gateway = APIGatewayExample()

        # Test API key authentication
        headers = {"X-API-Key": "gateway_key_123"}
        auth_result = gateway.authenticate_request(headers)
        assert auth_result.is_valid
        assert auth_result.username == "gateway-admin"
        assert "gateway" in auth_result.roles

        print("✅ API Key authentication test passed")

    @staticmethod
    async def test_permissions():
        """Test permission checking."""
        gateway = APIGatewayExample()

        # Test gateway permissions
        gateway_roles = ["gateway"]
        client_roles = ["client"]
        admin_roles = ["admin"]

        # Gateway should have gateway permissions
        assert gateway.check_permissions(gateway_roles, ["read", "write"])

        # Client should have client permissions
        assert gateway.check_permissions(client_roles, ["read"])

        # Admin should have all permissions
        assert gateway.check_permissions(admin_roles, ["read", "write", "delete"])

        print("✅ Permission checking test passed")

    @staticmethod
    async def test_rate_limiting():
        """Test rate limiting functionality."""
        gateway = APIGatewayExample()

        # Test rate limiting
        identifier = "test_client"
        for i in range(5):
            is_allowed = gateway.check_rate_limit(identifier)
            print(f"Request {i+1}: {'Allowed' if is_allowed else 'Blocked'}")

        print("✅ Rate limiting test completed")

    @staticmethod
    async def test_routing():
        """Test routing functionality."""
        gateway = APIGatewayExample()

        # Test routing rule finding
        rule = gateway._find_routing_rule("/api/v1/users")
        assert rule is not None
        assert rule["service"] == "user-service"

        rule = gateway._find_routing_rule("/api/v1/orders")
        assert rule is not None
        assert rule["service"] == "order-service"

        rule = gateway._find_routing_rule("/unknown/path")
        assert rule is None

        print("✅ Routing test passed")

    @staticmethod
    async def test_health_check():
        """Test health check functionality."""
        gateway = APIGatewayExample()

        health = await gateway.health_check()
        assert "status" in health
        assert "gateway" in health
        assert health["gateway"] == "api-gateway"

        print("✅ Health check test passed")

    @staticmethod
    async def test_metrics():
        """Test metrics functionality."""
        gateway = APIGatewayExample()

        metrics = await gateway.get_metrics()
        assert "gateway" in metrics
        assert "timestamp" in metrics
        assert metrics["gateway"] == "api-gateway"

        print("✅ Metrics test passed")


async def main():
    """Main function for testing and example usage."""
    # Run tests
    print("Running API Gateway Example Tests...")
    await APIGatewayExampleTest.test_authentication()
    await APIGatewayExampleTest.test_permissions()
    await APIGatewayExampleTest.test_rate_limiting()
    await APIGatewayExampleTest.test_routing()
    await APIGatewayExampleTest.test_health_check()
    await APIGatewayExampleTest.test_metrics()

    # Example usage
    print("\nExample Usage:")
    gateway = APIGatewayExample()

    # Route a request
    request_data = {
        "path": "/api/v1/users/123",
        "method": "GET",
        "headers": {"X-API-Key": "client_key_456", "X-Forwarded-For": "192.168.1.100"},
        "body": {},
        "client_ip": "192.168.1.100",
    }

    result = await gateway.route_request(request_data)
    print(f"Request result: {result}")

    # Get health status
    health = await gateway.health_check()
    print(f"Health status: {health}")

    # Get metrics
    metrics = await gateway.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())

    # Start HTTP server in background for testing
    print("\nStarting API Gateway HTTP Server in background...")

    import json
    import threading
    import time
    from http.server import BaseHTTPRequestHandler, HTTPServer

    import requests

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "healthy", "gateway": "api-gateway"}
                self.wfile.write(json.dumps(response).encode())

            elif self.path == "/metrics":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "gateway": "api-gateway",
                    "requests_total": 100,
                    "requests_per_minute": 10,
                }
                self.wfile.write(json.dumps(response).encode())

            elif self.path == "/proxy":
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
                        "message": "Request proxied successfully",
                        "api_key": api_key,
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
        server = HTTPServer(("0.0.0.0", 8080), GatewayHandler)
        server.serve_forever()

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    try:
        # Test server endpoints
        print("Testing API Gateway server endpoints...")

        # Test health endpoint
        response = requests.get("http://localhost:8080/health", timeout=5)
        print(f"Health endpoint: {response.status_code}")

        # Test metrics endpoint
        response = requests.get("http://localhost:8080/metrics", timeout=5)
        print(f"Metrics endpoint: {response.status_code}")

        # Test proxy endpoint with API key
        headers = {"X-API-Key": "test_key_123"}
        response = requests.get(
            "http://localhost:8080/proxy", headers=headers, timeout=5
        )
        print(f"Proxy endpoint: {response.status_code}")

        print("✅ API Gateway server testing completed successfully")

    except requests.exceptions.RequestException as e:
        print(f"⚠️  API Gateway server testing failed: {e}")

    print("API Gateway example completed")
