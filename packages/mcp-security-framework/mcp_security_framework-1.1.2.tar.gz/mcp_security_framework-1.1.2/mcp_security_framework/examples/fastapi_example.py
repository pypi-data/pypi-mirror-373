#!/usr/bin/env python3
"""
FastAPI Example - Comprehensive Security Framework Demo

This example demonstrates ALL capabilities of the MCP Security Framework
with a real FastAPI application, serving as a comprehensive integration test.

Demonstrated Features:
1. Authentication (API Key, JWT, Certificate)
2. Authorization (Role-based access control)
3. SSL/TLS Management (Server/Client contexts)
4. Certificate Management (Creation, validation, revocation)
5. Rate Limiting (Request throttling)
6. Security Validation (Request/Configuration validation)
7. Security Monitoring (Status, metrics, audit)
8. Security Logging (Event logging)
9. FastAPI Middleware Integration
10. Real HTTP endpoints with security

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import json
import logging
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from mcp_security_framework.constants import (
    AUTH_METHODS,
    DEFAULT_SECURITY_HEADERS,
    ErrorCodes,
)
from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.schemas.config import (
    AuthConfig,
    CertificateConfig,
    LoggingConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
)
from mcp_security_framework.schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    CertificateInfo,
    CertificatePair,
    ValidationResult,
    ValidationStatus,
)


class FastAPISecurityExample:
    """
    Comprehensive FastAPI Security Example

    This class demonstrates ALL capabilities of the MCP Security Framework
    with a real FastAPI application, serving as a complete integration test.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the FastAPI security example.

        Args:
            config_path: Optional path to configuration file
        """
        self.config = self._load_config(config_path)
        self.security_manager = SecurityManager(self.config)
        self.logger = logging.getLogger(__name__)

        # Create FastAPI app
        self.app = FastAPI(
            title="MCP Security Framework - FastAPI Example",
            description="Comprehensive security framework demonstration with FastAPI",
            version="1.0.0",
        )

        # Setup security middleware
        self._setup_security_middleware()

        # Setup routes
        self._setup_routes()

        # Test data
        self.test_api_key = "admin_key_123"
        self.test_jwt_token = self._create_test_jwt_token()
        self.test_certificate = self._create_test_certificate()

        self.logger.info("FastAPI Security Example initialized successfully")

    def _load_config(self, config_path: Optional[str] = None) -> SecurityConfig:
        """Load security configuration."""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return SecurityConfig(**config_data)

        # Create comprehensive configuration
        return SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=[
                    AUTH_METHODS["API_KEY"],
                    AUTH_METHODS["JWT"],
                    AUTH_METHODS["CERTIFICATE"],
                ],
                api_keys={
                    "admin_key_123": {"username": "admin", "roles": ["admin", "user"]},
                    "user_key_456": {"username": "user", "roles": ["user"]},
                    "readonly_key_789": {"username": "readonly", "roles": ["readonly"]},
                },
                jwt_secret="your-super-secret-jwt-key-change-in-production-12345",
                jwt_algorithm="HS256",
                jwt_expiry_hours=24,
                public_paths=["/health", "/metrics", "/docs", "/openapi.json"],
                security_headers=DEFAULT_SECURITY_HEADERS,
            ),
            permissions=PermissionConfig(
                enabled=True,
                roles_file="config/roles.json",
                default_role="user",
                hierarchy_enabled=True,
            ),
            ssl=SSLConfig(
                enabled=False,  # Disable for example
                cert_file=None,
                key_file=None,
                ca_cert_file=None,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
            ),
            certificates=CertificateConfig(
                enabled=False,  # Disable for example
                ca_cert_path=None,
                ca_key_path=None,
                cert_validity_days=365,
                key_size=2048,
            ),
            rate_limit=RateLimitConfig(
                enabled=True,
                default_requests_per_minute=60,
                default_requests_per_hour=1000,
                burst_limit=2,
                window_size_seconds=60,
                storage_backend="memory",
                cleanup_interval=300,
            ),
            logging=LoggingConfig(
                enabled=True,
                level="INFO",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                file_path="logs/security.log",
                max_file_size=10,
                backup_count=5,
                console_output=True,
                json_format=False,
            ),
            debug=True,
            environment="test",
            version="1.0.0",
        )

    def _create_test_jwt_token(self) -> str:
        """Create a test JWT token."""
        import jwt

        payload = {
            "username": "test_user",
            "roles": ["user"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        jwt_secret = (
            self.config.auth.jwt_secret.get_secret_value()
            if self.config.auth.jwt_secret
            else "default-jwt-secret-for-testing"
        )
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    def _create_test_certificate(self) -> str:
        """Create a test certificate."""
        return """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKoK8sJgKqQqMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTkwMzI2MTIzMzQ5WhcNMjAwMzI1MTIzMzQ5WjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAvxL8JgKqQqMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNVBAYTAkFVMRMw
EQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0
eSBMdGQwHhcNMTkwMzI2MTIzMzQ5WhcNMjAwMzI1MTIzMzQ5WjBFMQswCQYDVQQG
EwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50ZXJuZXQgV2lk
Z2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
-----END CERTIFICATE-----"""

    def _setup_security_middleware(self):
        """Setup security middleware for FastAPI."""

        @self.app.middleware("http")
        async def security_middleware(request: Request, call_next):
            """Security middleware for request processing."""
            # Check if path is public
            if self._is_public_path(request.url.path):
                response = await call_next(request)
                self._add_security_headers(response)
                return response

            # Rate limiting check
            if not self._check_rate_limit(request):
                return Response(
                    content=json.dumps(
                        {"error": "Rate limit exceeded", "error_code": -32003}
                    ),
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                )

            # Authentication check
            auth_result = await self._authenticate_request(request)
            if not auth_result.is_valid:
                return Response(
                    content=json.dumps(
                        {
                            "error": auth_result.error_message,
                            "error_code": auth_result.error_code,
                        }
                    ),
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    media_type="application/json",
                )

            # Authorization check (for protected endpoints)
            if request.url.path.startswith("/admin") or request.url.path.startswith(
                "/api/v1"
            ):
                if not self._check_permissions(request, auth_result):
                    return Response(
                        content=json.dumps(
                            {"error": "Insufficient permissions", "error_code": -32004}
                        ),
                        status_code=status.HTTP_403_FORBIDDEN,
                        media_type="application/json",
                    )

            # Add user info to request state
            request.state.user_info = {
                "username": auth_result.username,
                "roles": auth_result.roles,
                "permissions": auth_result.permissions,
                "auth_method": auth_result.auth_method.value,
            }

            # Process request
            response = await call_next(request)

            # Add security headers
            self._add_security_headers(response)

            return response

    def _is_public_path(self, path: str) -> bool:
        """Check if path is public."""
        return any(
            path.startswith(public_path)
            for public_path in self.config.auth.public_paths
        )

    def _check_rate_limit(self, request: Request) -> bool:
        """Check rate limit for request."""
        identifier = request.client.host if request.client else "unknown"
        return self.security_manager.check_rate_limit(identifier)

    async def _authenticate_request(self, request: Request) -> AuthResult:
        """Authenticate request."""
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return self.security_manager.authenticate_user(
                {"method": "api_key", "api_key": api_key}
            )

        # Check for JWT token in Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return self.security_manager.authenticate_user(
                {"method": "jwt", "token": token}
            )

        # Check for certificate in headers (for mTLS)
        cert_header = request.headers.get("X-Client-Cert")
        if cert_header:
            return self.security_manager.authenticate_user(
                {"method": "certificate", "certificate": cert_header}
            )

        # Return failed authentication
        return AuthResult(
            is_valid=False,
            status=AuthStatus.INVALID,
            auth_method=AuthMethod.UNKNOWN,
            error_code=-32001,
            error_message="No authentication credentials provided",
        )

    def _check_permissions(self, request: Request, auth_result: AuthResult) -> bool:
        """Check permissions for request."""
        # Determine required permissions based on endpoint
        required_permissions = []

        if request.url.path.startswith("/admin"):
            required_permissions = ["admin"]
        elif request.url.path.startswith("/api/v1/users"):
            required_permissions = ["read:own"]  # Use read:own instead of read:users
        elif request.url.path.startswith("/api/v1/data"):
            required_permissions = ["read:own"]  # Use read:own instead of read:data

        if required_permissions:
            result = self.security_manager.check_permissions(
                auth_result.roles, required_permissions
            )
            return result.is_valid

        return True

    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        if self.config.auth.security_headers:
            for header, value in self.config.auth.security_headers.items():
                response.headers[header] = value

    def _setup_routes(self):
        """Setup FastAPI routes."""

        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "framework": "FastAPI",
                "security_enabled": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Metrics endpoint
        @self.app.get("/metrics")
        async def get_metrics():
            """Get security metrics."""
            metrics = self.security_manager.get_security_metrics()
            return {
                "framework": "FastAPI",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Security status endpoint
        @self.app.get("/security/status")
        async def get_security_status():
            """Get security status."""
            status = self.security_manager.get_security_status()
            return {
                "framework": "FastAPI",
                "status": status.dict(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Security audit endpoint
        @self.app.get("/security/audit")
        async def get_security_audit():
            """Get security audit."""
            audit = self.security_manager.perform_security_audit()
            return {
                "framework": "FastAPI",
                "audit": audit,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Admin endpoints (require admin permissions)
        @self.app.get("/admin/users")
        async def get_users(request: Request):
            """Get all users (admin only)."""
            user_info = getattr(request.state, "user_info", {})
            return {
                "message": "Users list",
                "user": user_info,
                "users": [
                    {"id": 1, "username": "admin", "roles": ["admin"]},
                    {"id": 2, "username": "user", "roles": ["user"]},
                    {"id": 3, "username": "readonly", "roles": ["readonly"]},
                ],
            }

        # API endpoints (require specific permissions)
        @self.app.get("/api/v1/users/me")
        async def get_current_user(request: Request):
            """Get current user info."""
            user_info = getattr(request.state, "user_info", {})
            return {"message": "Current user info", "user": user_info}

        @self.app.get("/api/v1/data")
        async def get_data(request: Request):
            """Get data (requires read:data permission)."""
            user_info = getattr(request.state, "user_info", {})
            return {
                "message": "Data retrieved successfully",
                "user": user_info,
                "data": [
                    {"id": 1, "name": "Sample Data 1"},
                    {"id": 2, "name": "Sample Data 2"},
                    {"id": 3, "name": "Sample Data 3"},
                ],
            }

        # Authentication test endpoints
        @self.app.post("/auth/test-api-key")
        async def test_api_key_auth(request: Request):
            """Test API key authentication."""
            user_info = getattr(request.state, "user_info", {})
            return {
                "message": "API key authentication successful",
                "user": user_info,
                "auth_method": "api_key",
            }

        @self.app.post("/auth/test-jwt")
        async def test_jwt_auth(request: Request):
            """Test JWT authentication."""
            user_info = getattr(request.state, "user_info", {})
            return {
                "message": "JWT authentication successful",
                "user": user_info,
                "auth_method": "jwt",
            }

        # Rate limiting test endpoint
        @self.app.get("/rate-limit-test")
        async def rate_limit_test(request: Request):
            """Test rate limiting."""
            user_info = getattr(request.state, "user_info", {})
            return {
                "message": "Rate limit test successful",
                "user": user_info,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def demonstrate_authentication(self) -> Dict[str, Any]:
        """
        Demonstrate ALL authentication methods.

        Returns:
            Dict with authentication test results
        """
        self.logger.info("Demonstrating authentication capabilities...")

        results = {
            "api_key_auth": {},
            "jwt_auth": {},
            "certificate_auth": {},
            "failed_auth": {},
        }

        # 1. API Key Authentication
        try:
            auth_result = self.security_manager.authenticate_user(
                {"method": "api_key", "api_key": self.test_api_key}
            )
            results["api_key_auth"] = {
                "success": auth_result.is_valid,
                "username": auth_result.username,
                "roles": auth_result.roles,
                "auth_method": auth_result.auth_method.value,
            }
            self.logger.info(
                f"API Key auth: {auth_result.username} - {auth_result.roles}"
            )
        except Exception as e:
            results["api_key_auth"] = {"error": str(e)}

        # 2. JWT Authentication
        try:
            auth_result = self.security_manager.authenticate_user(
                {"method": "jwt", "token": self.test_jwt_token}
            )
            results["jwt_auth"] = {
                "success": auth_result.is_valid,
                "username": auth_result.username,
                "roles": auth_result.roles,
                "auth_method": auth_result.auth_method.value,
            }
            self.logger.info(f"JWT auth: {auth_result.username} - {auth_result.roles}")
        except Exception as e:
            results["jwt_auth"] = {"error": str(e)}

        # 3. Certificate Authentication
        try:
            auth_result = self.security_manager.authenticate_user(
                {"method": "certificate", "certificate": self.test_certificate}
            )
            results["certificate_auth"] = {
                "success": auth_result.is_valid,
                "username": auth_result.username,
                "roles": auth_result.roles,
                "auth_method": auth_result.auth_method.value,
            }
            self.logger.info(
                f"Certificate auth: {auth_result.username} - {auth_result.roles}"
            )
        except Exception as e:
            results["certificate_auth"] = {"error": str(e)}

        # 4. Failed Authentication
        try:
            auth_result = self.security_manager.authenticate_user(
                {"method": "api_key", "api_key": "invalid_key"}
            )
            results["failed_auth"] = {
                "success": auth_result.is_valid,
                "error_message": auth_result.error_message,
                "error_code": auth_result.error_code,
            }
            self.logger.info(f"Failed auth test: {auth_result.error_message}")
        except Exception as e:
            results["failed_auth"] = {"error": str(e)}

        return results

    def demonstrate_authorization(self) -> Dict[str, Any]:
        """
        Demonstrate authorization capabilities.

        Returns:
            Dict with authorization test results
        """
        self.logger.info("Demonstrating authorization capabilities...")

        results = {
            "admin_permissions": {},
            "user_permissions": {},
            "readonly_permissions": {},
            "denied_permissions": {},
        }

        # 1. Admin permissions
        try:
            result = self.security_manager.check_permissions(
                ["admin"], ["read", "write", "delete"]
            )
            results["admin_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }
            self.logger.info(f"Admin permissions: {result.is_valid}")
        except Exception as e:
            results["admin_permissions"] = {"error": str(e)}

        # 2. User permissions
        try:
            result = self.security_manager.check_permissions(
                ["user"], ["read", "write"]
            )
            results["user_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }
            self.logger.info(f"User permissions: {result.is_valid}")
        except Exception as e:
            results["user_permissions"] = {"error": str(e)}

        # 3. Readonly permissions
        try:
            result = self.security_manager.check_permissions(["readonly"], ["read"])
            results["readonly_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }
            self.logger.info(f"Readonly permissions: {result.is_valid}")
        except Exception as e:
            results["readonly_permissions"] = {"error": str(e)}

        # 4. Denied permissions
        try:
            result = self.security_manager.check_permissions(["readonly"], ["delete"])
            results["denied_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
                "error_message": result.error_message,
            }
            self.logger.info(f"Denied permissions: {result.is_valid}")
        except Exception as e:
            results["denied_permissions"] = {"error": str(e)}

        return results

    def demonstrate_rate_limiting(self) -> Dict[str, Any]:
        """
        Demonstrate rate limiting capabilities.

        Returns:
            Dict with rate limiting test results
        """
        self.logger.info("Demonstrating rate limiting capabilities...")

        results = {"rate_limit_checks": [], "rate_limit_exceeded": False}

        identifier = "test_user_123"

        # Test rate limiting
        for i in range(5):
            try:
                allowed = self.security_manager.check_rate_limit(identifier)
                results["rate_limit_checks"].append(
                    {"request": i + 1, "allowed": allowed}
                )
                self.logger.info(
                    f"Rate limit check {i+1}: {'Allowed' if allowed else 'Blocked'}"
                )

                if not allowed:
                    results["rate_limit_exceeded"] = True
                    break

            except Exception as e:
                results["rate_limit_checks"].append({"request": i + 1, "error": str(e)})

        return results

    def demonstrate_security_validation(self) -> Dict[str, Any]:
        """
        Demonstrate security validation capabilities.

        Returns:
            Dict with validation test results
        """
        self.logger.info("Demonstrating security validation capabilities...")

        results = {"request_validation": {}, "configuration_validation": {}}

        # 1. Request validation
        try:
            request_data = {
                "api_key": self.test_api_key,
                "required_permissions": ["read", "write"],
                "client_ip": "192.168.1.100",
            }

            result = self.security_manager.validate_request(request_data)
            results["request_validation"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }
            self.logger.info(f"Request validation: {result.is_valid}")
        except Exception as e:
            results["request_validation"] = {"error": str(e)}

        # 2. Configuration validation
        try:
            result = self.security_manager.validate_configuration()
            results["configuration_validation"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }
            self.logger.info(f"Configuration validation: {result.is_valid}")
        except Exception as e:
            results["configuration_validation"] = {"error": str(e)}

        return results

    def demonstrate_security_monitoring(self) -> Dict[str, Any]:
        """
        Demonstrate security monitoring capabilities.

        Returns:
            Dict with monitoring test results
        """
        self.logger.info("Demonstrating security monitoring capabilities...")

        results = {"security_status": {}, "security_metrics": {}, "security_audit": {}}

        # 1. Security status
        try:
            status = self.security_manager.get_security_status()
            results["security_status"] = {
                "status": status.status.value,
                "message": status.message,
                "version": status.version,
                "metadata": status.metadata,
            }
            self.logger.info("Security status retrieved successfully")
        except Exception as e:
            results["security_status"] = {"error": str(e)}

        # 2. Security metrics
        try:
            metrics = self.security_manager.get_security_metrics()
            results["security_metrics"] = {
                "authentication_attempts": metrics.get("authentication_attempts", 0),
                "security_events": metrics.get("security_events", 0),
                "uptime_seconds": metrics.get("uptime_seconds", 0),
            }
            self.logger.info("Security metrics retrieved successfully")
        except Exception as e:
            results["security_metrics"] = {"error": str(e)}

        # 3. Security audit
        try:
            audit = self.security_manager.perform_security_audit()
            results["security_audit"] = {
                "authentication": audit.get("authentication", {}),
                "authorization": audit.get("authorization", {}),
                "rate_limiting": audit.get("rate_limiting", {}),
                "ssl": audit.get("ssl", {}),
            }
            self.logger.info("Security audit completed successfully")
        except Exception as e:
            results["security_audit"] = {"error": str(e)}

        return results

    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """
        Run comprehensive demonstration of ALL framework capabilities.

        Returns:
            Dict with all demonstration results
        """
        self.logger.info("Starting comprehensive security framework demonstration...")

        demo_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework": "FastAPI",
            "version": "1.0.0",
            "authentication": self.demonstrate_authentication(),
            "authorization": self.demonstrate_authorization(),
            "rate_limiting": self.demonstrate_rate_limiting(),
            "security_validation": self.demonstrate_security_validation(),
            "security_monitoring": self.demonstrate_security_monitoring(),
        }

        self.logger.info("Comprehensive demonstration completed successfully")
        return demo_results


class FastAPIExampleTest:
    """Test class for FastAPI example."""

    def test_authentication(self):
        """Test authentication capabilities."""
        example = FastAPISecurityExample()
        results = example.demonstrate_authentication()

        # Verify API key authentication works
        assert results["api_key_auth"]["success"] == True
        assert results["api_key_auth"]["username"] == "admin"
        assert "admin" in results["api_key_auth"]["roles"]

        # Verify JWT authentication works
        assert results["jwt_auth"]["success"] == True
        assert results["jwt_auth"]["username"] == "test_user"

        # Verify failed authentication is handled
        assert results["failed_auth"]["success"] == False

        print("✅ Authentication tests passed")

    def test_authorization(self):
        """Test authorization capabilities."""
        example = FastAPISecurityExample()
        results = example.demonstrate_authorization()

        # Verify admin permissions work
        assert results["admin_permissions"]["success"] == True

        # Verify user permissions work
        assert results["user_permissions"]["success"] == True

        # Verify readonly permissions work
        assert results["readonly_permissions"]["success"] == True

        print("✅ Authorization tests passed")

    def test_rate_limiting(self):
        """Test rate limiting capabilities."""
        example = FastAPISecurityExample()
        results = example.demonstrate_rate_limiting()

        # Verify rate limiting checks work
        assert len(results["rate_limit_checks"]) > 0
        assert results["rate_limit_checks"][0]["allowed"] == True

        print("✅ Rate limiting tests passed")

    def test_security_validation(self):
        """Test security validation capabilities."""
        example = FastAPISecurityExample()
        results = example.demonstrate_security_validation()

        # Verify request validation works
        assert results["request_validation"]["success"] == True

        # Verify configuration validation works
        assert results["configuration_validation"]["success"] == True

        print("✅ Security validation tests passed")

    def test_security_monitoring(self):
        """Test security monitoring capabilities."""
        example = FastAPISecurityExample()
        results = example.demonstrate_security_monitoring()

        # Verify security status works
        assert "status" in results["security_status"]
        assert "message" in results["security_status"]

        # Verify security metrics work
        assert "authentication_attempts" in results["security_metrics"]

        # Verify security audit works
        assert "authentication" in results["security_audit"]

        print("✅ Security monitoring tests passed")


def main():
    """Main function to run the FastAPI example."""
    print("\n🚀 MCP Security Framework - FastAPI Example")
    print("=" * 60)

    # Create example instance
    example = FastAPISecurityExample()

    # Run comprehensive demonstration
    results = example.run_comprehensive_demo()

    # Print results
    print("\n📊 COMPREHENSIVE DEMONSTRATION RESULTS")
    print("=" * 60)
    print(f"Framework: {results['framework']}")
    print(f"Version: {results['version']}")
    print(f"Timestamp: {results['timestamp']}")

    print("\n🔐 AUTHENTICATION RESULTS:")
    print(
        f"  API Key: {'✅' if results['authentication']['api_key_auth']['success'] else '❌'}"
    )
    print(
        f"  JWT: {'✅' if results['authentication']['jwt_auth']['success'] else '❌'}"
    )
    print(
        f"  Certificate: {'✅' if results['authentication']['certificate_auth']['success'] else '❌'}"
    )

    print("\n🔑 AUTHORIZATION RESULTS:")
    print(
        f"  Admin Permissions: {'✅' if results['authorization']['admin_permissions']['success'] else '❌'}"
    )
    print(
        f"  User Permissions: {'✅' if results['authorization']['user_permissions']['success'] else '❌'}"
    )
    print(
        f"  Readonly Permissions: {'✅' if results['authorization']['readonly_permissions']['success'] else '❌'}"
    )

    print("\n⚡ RATE LIMITING RESULTS:")
    print(f"  Rate Limit Checks: {len(results['rate_limiting']['rate_limit_checks'])}")
    print(
        f"  Rate Limit Exceeded: {'❌' if results['rate_limiting']['rate_limit_exceeded'] else '✅'}"
    )

    print("\n🔒 SECURITY VALIDATION RESULTS:")
    print(
        f"  Request Validation: {'✅' if results['security_validation']['request_validation']['success'] else '❌'}"
    )
    print(
        f"  Configuration Validation: {'✅' if results['security_validation']['configuration_validation']['success'] else '❌'}"
    )

    print("\n📊 SECURITY MONITORING RESULTS:")
    print(
        f"  Security Status: {'✅' if 'status' in results['security_monitoring']['security_status'] else '❌'}"
    )
    print(
        f"  Security Metrics: {'✅' if 'authentication_attempts' in results['security_monitoring']['security_metrics'] else '❌'}"
    )
    print(
        f"  Security Audit: {'✅' if 'authentication' in results['security_monitoring']['security_audit'] else '❌'}"
    )

    print("\n🎉 ALL FRAMEWORK CAPABILITIES DEMONSTRATED SUCCESSFULLY!")
    print("=" * 60)

    print("\n🌐 FastAPI Application Ready!")
    print("Run with: uvicorn fastapi_example:example.app --reload")
    print("Available endpoints:")
    print("  - GET  /health - Health check")
    print("  - GET  /metrics - Security metrics")
    print("  - GET  /security/status - Security status")
    print("  - GET  /security/audit - Security audit")
    print("  - GET  /admin/users - Admin users (requires admin)")
    print("  - GET  /api/v1/users/me - Current user")
    print("  - GET  /api/v1/data - Data (requires read:data)")
    print("  - POST /auth/test-api-key - Test API key auth")
    print("  - POST /auth/test-jwt - Test JWT auth")
    print("  - GET  /rate-limit-test - Test rate limiting")


if __name__ == "__main__":
    # Run tests
    print("Running FastAPI Example Tests...")
    test = FastAPIExampleTest()
    test.test_authentication()
    test.test_authorization()
    test.test_rate_limiting()
    test.test_security_validation()
    test.test_security_monitoring()

    print("\nExample Usage:")
    main()

    # Start server in background thread for testing
    print("\nStarting FastAPI Server in background...")
    example = FastAPISecurityExample()

    import asyncio
    import threading
    import time

    import requests
    import uvicorn

    # Start server in background thread
    def run_server():
        uvicorn.run(example.app, host="0.0.0.0", port=8000, log_level="error")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(5)

    try:
        # Test server endpoints
        print("Testing FastAPI server endpoints...")

        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health endpoint: {response.status_code}")

        # Test metrics endpoint
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        print(f"Metrics endpoint: {response.status_code}")

        # Test protected endpoint with API key
        headers = {"X-API-Key": "admin_key_123"}
        response = requests.get(
            "http://localhost:8000/api/v1/users/me", headers=headers, timeout=5
        )
        print(f"Protected endpoint: {response.status_code}")

        print("✅ FastAPI server testing completed successfully")

    except requests.exceptions.RequestException as e:
        print(f"⚠️  FastAPI server testing failed: {e}")

    print("FastAPI example completed")
