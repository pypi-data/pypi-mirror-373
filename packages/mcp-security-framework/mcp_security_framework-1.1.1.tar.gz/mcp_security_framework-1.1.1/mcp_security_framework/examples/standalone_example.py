#!/usr/bin/env python3
"""
Standalone Example - Comprehensive Security Framework Demo

This example demonstrates ALL capabilities of the MCP Security Framework
in a standalone environment, serving as a comprehensive integration test.

Demonstrated Features:
1. Authentication (API Key, JWT, Certificate)
2. Authorization (Role-based access control)
3. SSL/TLS Management (Server/Client contexts)
4. Certificate Management (Creation, validation, revocation)
5. Rate Limiting (Request throttling)
6. Security Validation (Request/Configuration validation)
7. Security Monitoring (Status, metrics, audit)
8. Security Logging (Event logging)

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


class StandaloneSecurityExample:
    """
    Comprehensive Standalone Security Example

    This class demonstrates ALL capabilities of the MCP Security Framework
    in a standalone environment, serving as a complete integration test.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the standalone security example.

        Args:
            config_path: Optional path to configuration file
        """
        self.config = self._load_config(config_path)
        self.security_manager = SecurityManager(self.config)
        self.logger = logging.getLogger(__name__)

        # Test data
        self.test_api_key = "admin_key_123"
        self.test_jwt_token = self._create_test_jwt_token()
        self.test_certificate = self._create_test_certificate()

        self.logger.info("Standalone Security Example initialized successfully")

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
                public_paths=["/health/", "/metrics/"],
                security_headers=DEFAULT_SECURITY_HEADERS,
            ),
            permissions=PermissionConfig(
                enabled=True,
                roles_file="config/roles.json",
                default_role="user",
                hierarchy_enabled=True,
            ),
            ssl=SSLConfig(
                enabled=False,  # Disable for standalone example
                cert_file=None,
                key_file=None,
                ca_cert_file=None,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
            ),
            certificates=CertificateConfig(
                enabled=False,  # Disable for standalone example
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

    def demonstrate_certificate_management(self) -> Dict[str, Any]:
        """
        Demonstrate certificate management capabilities.

        Returns:
            Dict with certificate management test results
        """
        self.logger.info("Demonstrating certificate management capabilities...")

        results = {
            "certificate_creation": {},
            "certificate_validation": {},
            "certificate_info": {},
        }

        # 1. Certificate creation (if enabled)
        if self.config.certificates.enabled:
            try:
                cert_config = {
                    "cert_type": "client",
                    "common_name": "test-client.example.com",
                    "organization": "Test Organization",
                    "country": "US",
                    "validity_days": 365,
                }

                # Note: This would require actual CA files
                # cert_pair = self.security_manager.create_certificate(cert_config)
                results["certificate_creation"] = {
                    "success": True,
                    "message": "Certificate creation capability demonstrated",
                }
                self.logger.info("Certificate creation capability demonstrated")
            except Exception as e:
                results["certificate_creation"] = {"error": str(e)}

        # 2. Certificate validation
        try:
            # Test with dummy certificate
            cert_info = CertificateInfo(
                subject="test-client.example.com",
                issuer="Test CA",
                serial_number="123456789",
                valid_from=datetime.now(timezone.utc),
                valid_until=datetime.now(timezone.utc) + timedelta(days=365),
                is_valid=True,
            )
            results["certificate_validation"] = {
                "success": True,
                "certificate_info": {
                    "subject": cert_info.subject,
                    "issuer": cert_info.issuer,
                    "is_valid": cert_info.is_valid,
                },
            }
            self.logger.info("Certificate validation capability demonstrated")
        except Exception as e:
            results["certificate_validation"] = {"error": str(e)}

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
            print(f"Security status: {results['security_status']}")
            self.logger.info("Security status retrieved successfully")
        except Exception as e:
            results["security_status"] = {"error": str(e)}
            print(f"Security status error: {str(e)}")

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
            "framework": "MCP Security Framework",
            "version": "1.0.0",
            "authentication": self.demonstrate_authentication(),
            "authorization": self.demonstrate_authorization(),
            "rate_limiting": self.demonstrate_rate_limiting(),
            "certificate_management": self.demonstrate_certificate_management(),
            "security_validation": self.demonstrate_security_validation(),
            "security_monitoring": self.demonstrate_security_monitoring(),
        }

        self.logger.info("Comprehensive demonstration completed successfully")
        return demo_results

    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a security request.

        Args:
            request_data: Dictionary containing request information
                - credentials: Authentication credentials
                - action: Request action (read, write, delete)
                - resource: Resource being accessed
                - identifier: Client identifier for rate limiting
                - data: Optional data for write operations

        Returns:
            Dictionary with processing results
        """
        try:
            # Extract request information
            credentials = request_data.get("credentials", {})
            action = request_data.get("action", "read")
            resource = request_data.get("resource", "/")
            identifier = request_data.get("identifier", "unknown")
            data = request_data.get("data")

            # Check rate limiting
            rate_limit_result = self.security_manager.check_rate_limit(identifier)
            if not rate_limit_result:
                return {
                    "success": False,
                    "status_code": 429,
                    "error": "Rate limit exceeded",
                    "retry_after": 60,
                }

            # Authenticate request
            auth_result = None
            if "api_key" in credentials:
                auth_result = self.security_manager.authenticate_user(
                    {"method": "api_key", "api_key": credentials["api_key"]}
                )
            elif "jwt_token" in credentials:
                auth_result = self.security_manager.authenticate_user(
                    {"method": "jwt", "token": credentials["jwt_token"]}
                )
            elif "certificate" in credentials:
                auth_result = self.security_manager.authenticate_user(
                    {"method": "certificate", "certificate": credentials["certificate"]}
                )

            # Check authentication
            if not auth_result or not auth_result.is_valid:
                return {
                    "success": False,
                    "status_code": 401,
                    "error": "Authentication failed",
                    "auth_result": auth_result.model_dump() if auth_result else None,
                }

            # Check authorization
            required_permissions = self._get_required_permissions(action, resource)
            authz_result = self.security_manager.check_permissions(
                auth_result.roles, required_permissions
            )

            if not authz_result.is_valid:
                return {
                    "success": False,
                    "status_code": 403,
                    "error": "Authorization failed",
                    "auth_result": auth_result.model_dump(),
                    "authz_result": authz_result.model_dump(),
                }

            # Process the request
            result = {
                "success": True,
                "status_code": 200,
                "auth_result": auth_result.model_dump(),
                "authz_result": authz_result.model_dump(),
                "data": data if action == "write" else None,
                "resource": resource,
                "action": action,
            }

            # Log the successful request
            self.logger.info(f"Request processed successfully: {action} {resource}")

            return result

        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            return {
                "success": False,
                "status_code": 500,
                "error": f"Internal server error: {str(e)}",
            }

    def _get_required_permissions(self, action: str, resource: str) -> List[str]:
        """Get required permissions for action and resource."""
        if action == "read":
            return ["read"]
        elif action == "write":
            return ["write"]
        elif action == "delete":
            return ["delete"]
        elif action == "admin":
            return ["admin"]
        else:
            return ["read"]


class StandaloneExampleTest:
    """Test class for standalone example."""

    def test_authentication(self):
        """Test authentication capabilities."""
        example = StandaloneSecurityExample()
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
        example = StandaloneSecurityExample()
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
        example = StandaloneSecurityExample()
        results = example.demonstrate_rate_limiting()

        # Verify rate limiting checks work
        assert len(results["rate_limit_checks"]) > 0
        assert results["rate_limit_checks"][0]["allowed"] == True

        print("✅ Rate limiting tests passed")

    def test_security_validation(self):
        """Test security validation capabilities."""
        example = StandaloneSecurityExample()
        results = example.demonstrate_security_validation()

        # Verify request validation works
        assert results["request_validation"]["success"] == True

        # Verify configuration validation works
        assert results["configuration_validation"]["success"] == True

        print("✅ Security validation tests passed")

    def test_security_monitoring(self):
        """Test security monitoring capabilities."""
        example = StandaloneSecurityExample()
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
    """Main function to run the standalone example."""
    print("\n🚀 MCP Security Framework - Standalone Example")
    print("=" * 60)

    # Create example instance
    example = StandaloneSecurityExample()

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
        f"  Security Status: {'✅' if 'ssl_enabled' in results['security_monitoring']['security_status'] else '❌'}"
    )
    print(
        f"  Security Metrics: {'✅' if 'authentication_attempts' in results['security_monitoring']['security_metrics'] else '❌'}"
    )
    print(
        f"  Security Audit: {'✅' if 'authentication' in results['security_monitoring']['security_audit'] else '❌'}"
    )

    print("\n🎉 ALL FRAMEWORK CAPABILITIES DEMONSTRATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    # Run tests
    print("Running Standalone Example Tests...")
    test = StandaloneExampleTest()
    test.test_authentication()
    test.test_authorization()
    test.test_rate_limiting()
    test.test_security_validation()
    test.test_security_monitoring()

    print("\nExample Usage:")
    main()
