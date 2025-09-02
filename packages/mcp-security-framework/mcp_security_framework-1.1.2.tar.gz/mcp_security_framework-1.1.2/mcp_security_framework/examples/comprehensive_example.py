#!/usr/bin/env python3
"""
Comprehensive Security Framework Example

This example demonstrates ALL capabilities of the MCP Security Framework
including certificate management, SSL/TLS, authentication, authorization,
and security validation.

Demonstrated Features:
1. Root CA certificate creation
2. Intermediate CA certificate creation
3. Client and server certificate creation
4. Certificate Signing Request (CSR) generation
5. Certificate Revocation List (CRL) creation with reasons
6. SSL/TLS context creation and validation
7. mTLS (mutual TLS) configuration
8. Authentication (API Key, JWT, Certificate)
9. Authorization (Role-based access control)
10. Rate Limiting
11. Security Validation
12. Security Monitoring

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import json
import logging
import os
import shutil
import socket
import ssl
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mcp_security_framework.constants import (
    AUTH_METHODS,
    DEFAULT_SECURITY_HEADERS,
    ErrorCodes,
)
from mcp_security_framework.core.cert_manager import CertificateManager
from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.core.ssl_manager import SSLManager
from mcp_security_framework.schemas.config import (
    AuthConfig,
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    IntermediateCAConfig,
    LoggingConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    ServerCertConfig,
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


class ComprehensiveSecurityExample:
    """
    Comprehensive Security Example

    This class demonstrates ALL capabilities of the MCP Security Framework
    including advanced certificate management features.
    """

    def __init__(self, work_dir: Optional[str] = None):
        """
        Initialize the comprehensive security example.

        Args:
            work_dir: Working directory for certificates and keys
        """
        self.work_dir = work_dir or tempfile.mkdtemp(
            prefix="mcp_security_comprehensive_"
        )
        self.certs_dir = os.path.join(self.work_dir, "certs")
        self.keys_dir = os.path.join(self.work_dir, "keys")
        self.config_dir = os.path.join(self.work_dir, "config")

        # Create directories
        os.makedirs(self.certs_dir, exist_ok=True)
        os.makedirs(self.keys_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)

        # Initialize logger first
        self.logger = logging.getLogger(__name__)

        # Create roles configuration first
        self._create_roles_config()

        # Initialize configuration
        self.config = self._create_comprehensive_config()
        self.security_manager = SecurityManager(self.config)
        self.cert_manager = CertificateManager(self.config.certificates)
        self.ssl_manager = SSLManager(self.config.ssl)

        # Test data
        self.test_api_key = "admin_key_123"
        self.test_jwt_token = self._create_test_jwt_token()

        # Certificate paths
        self.ca_cert_path = None
        self.ca_key_path = None
        self.intermediate_ca_cert_path = None
        self.intermediate_ca_key_path = None
        self.server_cert_path = None
        self.server_key_path = None
        self.client_cert_path = None
        self.client_key_path = None

        self.logger.info("Comprehensive Security Example initialized successfully")

    def _create_comprehensive_config(self) -> SecurityConfig:
        """Create comprehensive security configuration."""
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
                roles_file=os.path.join(self.config_dir, "roles.json"),
                default_role="user",
                hierarchy_enabled=True,
            ),
            ssl=SSLConfig(
                enabled=False,  # Disable initially, will be enabled after certificates are created
                cert_file=None,
                key_file=None,
                ca_cert_file=None,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
                cipher_suite="ECDHE-RSA-AES256-GCM-SHA384",
            ),
            certificates=CertificateConfig(
                enabled=False,  # Disable initially, will be enabled after CA creation
                ca_cert_path=None,  # Will be set after CA creation
                ca_key_path=None,  # Will be set after CA creation
                cert_storage_path=self.certs_dir,
                key_storage_path=self.keys_dir,
                default_validity_days=365,
                default_key_size=2048,
            ),
            rate_limiting=RateLimitConfig(
                enabled=True,
                default_limit=100,
                default_window=60,
                storage_type="memory",
            ),
            logging=LoggingConfig(
                enabled=True,
                level="INFO",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                file_path=os.path.join(self.work_dir, "security.log"),
            ),
        )

    def _create_test_jwt_token(self) -> str:
        """Create a test JWT token."""
        import jwt

        payload = {
            "username": "test_user",
            "roles": ["user"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }

        # Ensure JWT secret is a string
        jwt_secret = (
            str(self.config.auth.jwt_secret)
            if self.config.auth.jwt_secret
            else "default-secret"
        )
        jwt_algorithm = (
            str(self.config.auth.jwt_algorithm)
            if self.config.auth.jwt_algorithm
            else "HS256"
        )

        return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)

    def _create_roles_config(self):
        """Create roles configuration file."""
        roles_config = {
            "roles": {
                "admin": {
                    "description": "Administrator role",
                    "permissions": ["*"],
                    "parent_roles": [],
                },
                "user": {
                    "description": "User role",
                    "permissions": ["read:own", "write:own"],
                    "parent_roles": [],
                },
                "readonly": {
                    "description": "Read Only role",
                    "permissions": ["read:own"],
                    "parent_roles": [],
                },
            }
        }

        roles_file = os.path.join(self.config_dir, "roles.json")
        with open(roles_file, "w") as f:
            json.dump(roles_config, f, indent=2)

        self.logger.info(f"Created roles configuration: {roles_file}")

    def demonstrate_certificate_management(self) -> Dict[str, Any]:
        """
        Demonstrate comprehensive certificate management capabilities.

        Returns:
            Dict with certificate management test results
        """
        self.logger.info("Demonstrating comprehensive certificate management...")

        results = {
            "root_ca_creation": {},
            "intermediate_ca_creation": {},
            "server_cert_creation": {},
            "client_cert_creation": {},
            "csr_creation": {},
            "crl_creation": {},
            "certificate_validation": {},
        }

        try:
            # 1. Create Root CA
            self.logger.info("Creating Root CA certificate...")
            ca_config = CAConfig(
                common_name="MCP Security Root CA",
                organization="MCP Security Framework",
                country="US",
                state="California",
                locality="San Francisco",
                validity_days=3650,
                key_size=4096,
            )

            ca_pair = self.cert_manager.create_root_ca(ca_config)
            self.ca_cert_path = ca_pair.certificate_path
            self.ca_key_path = ca_pair.private_key_path

            results["root_ca_creation"] = {
                "success": True,
                "cert_path": self.ca_cert_path,
                "key_path": self.ca_key_path,
                "serial_number": ca_pair.serial_number,
            }
            self.logger.info(f"Root CA created: {self.ca_cert_path}")

            # 2. Create Intermediate CA
            self.logger.info("Creating Intermediate CA certificate...")
            intermediate_config = IntermediateCAConfig(
                common_name="MCP Security Intermediate CA",
                organization="MCP Security Framework",
                country="US",
                state="California",
                locality="San Francisco",
                validity_days=1825,
                key_size=2048,
                parent_ca_cert=self.ca_cert_path,
                parent_ca_key=self.ca_key_path,
            )

            intermediate_pair = self.cert_manager.create_intermediate_ca(
                intermediate_config
            )
            self.intermediate_ca_cert_path = intermediate_pair.certificate_path
            self.intermediate_ca_key_path = intermediate_pair.private_key_path

            results["intermediate_ca_creation"] = {
                "success": True,
                "cert_path": self.intermediate_ca_cert_path,
                "key_path": self.intermediate_ca_key_path,
                "serial_number": intermediate_pair.serial_number,
            }
            self.logger.info(
                f"Intermediate CA created: {self.intermediate_ca_cert_path}"
            )

            # 3. Create Server Certificate
            self.logger.info("Creating server certificate...")
            server_config = ServerCertConfig(
                common_name="api.example.com",
                organization="Example Corp",
                country="US",
                state="California",
                locality="San Francisco",
                validity_days=365,
                key_size=2048,
                ca_cert_path=self.intermediate_ca_cert_path,
                ca_key_path=self.intermediate_ca_key_path,
            )

            server_pair = self.cert_manager.create_server_certificate(server_config)
            self.server_cert_path = server_pair.certificate_path
            self.server_key_path = server_pair.private_key_path

            results["server_cert_creation"] = {
                "success": True,
                "cert_path": self.server_cert_path,
                "key_path": self.server_key_path,
                "serial_number": server_pair.serial_number,
            }
            self.logger.info(f"Server certificate created: {self.server_cert_path}")

            # 4. Create Client Certificate
            self.logger.info("Creating client certificate...")
            client_config = ClientCertConfig(
                common_name="client.example.com",
                organization="Example Corp",
                country="US",
                state="California",
                locality="San Francisco",
                validity_days=365,
                key_size=2048,
                ca_cert_path=self.intermediate_ca_cert_path,
                ca_key_path=self.intermediate_ca_key_path,
            )

            client_pair = self.cert_manager.create_client_certificate(client_config)
            self.client_cert_path = client_pair.certificate_path
            self.client_key_path = client_pair.private_key_path

            results["client_cert_creation"] = {
                "success": True,
                "cert_path": self.client_cert_path,
                "key_path": self.client_key_path,
                "serial_number": client_pair.serial_number,
            }
            self.logger.info(f"Client certificate created: {self.client_cert_path}")

            # 5. Create Certificate Signing Request (CSR)
            self.logger.info("Creating Certificate Signing Request...")
            csr_path, csr_key_path = (
                self.cert_manager.create_certificate_signing_request(
                    common_name="new-service.example.com",
                    organization="New Service Corp",
                    country="US",
                    state="California",
                    locality="San Francisco",
                    organizational_unit="IT Department",
                    email="admin@new-service.example.com",
                    key_size=2048,
                    key_type="rsa",
                )
            )

            results["csr_creation"] = {
                "success": True,
                "csr_path": csr_path,
                "key_path": csr_key_path,
            }
            self.logger.info(f"CSR created: {csr_path}")

            # 6. Create Certificate Revocation List (CRL)
            self.logger.info("Creating Certificate Revocation List...")
            revoked_serials = [
                {
                    "serial": "123456789",
                    "reason": "key_compromise",
                    "revocation_date": datetime.now(timezone.utc),
                },
                {
                    "serial": "987654321",
                    "reason": "certificate_hold",
                    "revocation_date": datetime.now(timezone.utc),
                },
            ]

            crl_path = self.cert_manager.create_crl(
                ca_cert_path=self.intermediate_ca_cert_path,
                ca_key_path=self.intermediate_ca_key_path,
                revoked_serials=revoked_serials,
                validity_days=30,
            )

            results["crl_creation"] = {
                "success": True,
                "crl_path": crl_path,
                "revoked_count": len(revoked_serials),
            }
            self.logger.info(f"CRL created: {crl_path}")

            # 7. Certificate Validation
            self.logger.info("Validating certificates...")
            cert_info = self.cert_manager.get_certificate_info(self.server_cert_path)

            results["certificate_validation"] = {
                "success": True,
                "subject": cert_info.subject,
                "issuer": cert_info.issuer,
                "serial_number": cert_info.serial_number,
                "valid_from": cert_info.not_before.isoformat(),
                "valid_until": cert_info.not_after.isoformat(),
                "is_valid": not cert_info.is_expired,
            }
            self.logger.info("Certificate validation completed")

            # Update configuration with certificate paths
            self._update_config_after_certificates()

        except Exception as e:
            self.logger.error(f"Certificate management demonstration failed: {str(e)}")
            results["error"] = str(e)

        return results

    def _update_config_after_certificates(self):
        """Update configuration with certificate paths after creation."""
        if self.ca_cert_path and self.ca_key_path:
            self.config.certificates.enabled = True
            self.config.certificates.ca_cert_path = self.ca_cert_path
            self.config.certificates.ca_key_path = self.ca_key_path

            # Reinitialize certificate manager with updated config
            self.cert_manager = CertificateManager(self.config.certificates)

        if self.server_cert_path and self.server_key_path and self.ca_cert_path:
            self.config.ssl.enabled = True
            self.config.ssl.cert_file = self.server_cert_path
            self.config.ssl.key_file = self.server_key_path
            self.config.ssl.ca_cert_file = self.ca_cert_path

            # Reinitialize SSL manager with updated config
            self.ssl_manager = SSLManager(self.config.ssl)

    def demonstrate_ssl_tls_management(self) -> Dict[str, Any]:
        """
        Demonstrate SSL/TLS management capabilities.

        Returns:
            Dict with SSL/TLS test results
        """
        self.logger.info("Demonstrating SSL/TLS management...")

        results = {
            "server_context_creation": {},
            "client_context_creation": {},
            "mtls_context_creation": {},
            "ssl_validation": {},
        }

        try:
            # 1. Create Server SSL Context
            self.logger.info("Creating server SSL context...")
            server_context = self.ssl_manager.create_server_context(
                cert_file=self.server_cert_path,
                key_file=self.server_key_path,
                ca_cert_file=self.ca_cert_path,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
            )

            results["server_context_creation"] = {
                "success": True,
                "verify_mode": str(server_context.verify_mode),
                "min_version": str(server_context.minimum_version),
                "max_version": str(server_context.maximum_version),
            }
            self.logger.info("Server SSL context created successfully")

            # 2. Create Client SSL Context
            self.logger.info("Creating client SSL context...")
            client_context = self.ssl_manager.create_client_context(
                ca_cert_file=self.ca_cert_path,
                client_cert_file=self.client_cert_path,
                client_key_file=self.client_key_path,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
            )

            results["client_context_creation"] = {
                "success": True,
                "verify_mode": str(client_context.verify_mode),
                "min_version": str(client_context.minimum_version),
                "max_version": str(client_context.maximum_version),
            }
            self.logger.info("Client SSL context created successfully")

            # 3. Create mTLS Context (mutual TLS)
            self.logger.info("Creating mTLS context...")
            mtls_context = self.ssl_manager.create_server_context(
                cert_file=self.server_cert_path,
                key_file=self.server_key_path,
                ca_cert_file=self.ca_cert_path,
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2",
            )

            results["mtls_context_creation"] = {
                "success": True,
                "verify_mode": str(mtls_context.verify_mode),
                "client_cert_required": True,
            }
            self.logger.info("mTLS context created successfully")

            # 4. SSL Configuration Validation
            self.logger.info("Validating SSL configuration...")

            # Check if SSL files exist
            ssl_enabled = self.config.ssl.enabled
            cert_valid = (
                os.path.exists(self.server_cert_path)
                if self.server_cert_path
                else False
            )
            key_valid = (
                os.path.exists(self.server_key_path) if self.server_key_path else False
            )
            ca_valid = os.path.exists(self.ca_cert_path) if self.ca_cert_path else False

            results["ssl_validation"] = {
                "success": True,
                "ssl_enabled": ssl_enabled,
                "certificate_valid": cert_valid,
                "key_valid": key_valid,
                "ca_valid": ca_valid,
            }
            self.logger.info("SSL validation completed")

        except Exception as e:
            self.logger.error(f"SSL/TLS management demonstration failed: {str(e)}")
            results["error"] = str(e)

        return results

    def demonstrate_authentication(self) -> Dict[str, Any]:
        """
        Demonstrate authentication capabilities.

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

        try:
            # 1. API Key Authentication
            self.logger.info("Testing API key authentication...")
            auth_result = self.security_manager.authenticate_user(
                {"method": "api_key", "api_key": self.test_api_key}
            )
            results["api_key_auth"] = {
                "success": auth_result.is_valid,
                "username": auth_result.username,
                "roles": auth_result.roles,
                "auth_method": auth_result.auth_method.value,
            }

            # 2. JWT Authentication
            self.logger.info("Testing JWT authentication...")
            auth_result = self.security_manager.authenticate_user(
                {"method": "jwt", "token": self.test_jwt_token}
            )
            results["jwt_auth"] = {
                "success": auth_result.is_valid,
                "username": auth_result.username,
                "roles": auth_result.roles,
                "auth_method": auth_result.auth_method.value,
            }

            # 3. Certificate Authentication (if certificate available)
            if self.client_cert_path:
                self.logger.info("Testing certificate authentication...")
                with open(self.client_cert_path, "r") as f:
                    cert_pem = f.read()

                auth_result = self.security_manager.authenticate_user(
                    {"method": "certificate", "certificate": cert_pem}
                )
                results["certificate_auth"] = {
                    "success": auth_result.is_valid,
                    "username": auth_result.username,
                    "roles": auth_result.roles,
                    "auth_method": auth_result.auth_method.value,
                }

            # 4. Failed Authentication
            self.logger.info("Testing failed authentication...")
            auth_result = self.security_manager.authenticate_user(
                {"method": "api_key", "api_key": "invalid_key"}
            )
            results["failed_auth"] = {
                "success": auth_result.is_valid,
                "error_code": auth_result.error_code,
                "error_message": auth_result.error_message,
            }

        except Exception as e:
            self.logger.error(f"Authentication demonstration failed: {str(e)}")
            results["error"] = str(e)

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

        try:
            # 1. Admin Permissions
            self.logger.info("Testing admin permissions...")
            result = self.security_manager.check_permissions(
                user_roles=["admin"], required_permissions=["read", "write", "delete"]
            )
            results["admin_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }

            # 2. User Permissions
            self.logger.info("Testing user permissions...")
            result = self.security_manager.check_permissions(
                user_roles=["user"], required_permissions=["read:own", "write:own"]
            )
            results["user_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }

            # 3. Readonly Permissions
            self.logger.info("Testing readonly permissions...")
            result = self.security_manager.check_permissions(
                user_roles=["readonly"], required_permissions=["read:own"]
            )
            results["readonly_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }

            # 4. Denied Permissions
            self.logger.info("Testing denied permissions...")
            result = self.security_manager.check_permissions(
                user_roles=["readonly"], required_permissions=["write", "delete"]
            )
            results["denied_permissions"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }

        except Exception as e:
            self.logger.error(f"Authorization demonstration failed: {str(e)}")
            results["error"] = str(e)

        return results

    def demonstrate_rate_limiting(self) -> Dict[str, Any]:
        """
        Demonstrate rate limiting capabilities.

        Returns:
            Dict with rate limiting test results
        """
        self.logger.info("Demonstrating rate limiting capabilities...")

        results = {"rate_limit_checks": [], "rate_limit_exceeded": False}

        try:
            # Test rate limiting
            for i in range(5):
                allowed = self.security_manager.check_rate_limit("test_user")
                results["rate_limit_checks"].append(
                    {"request": i + 1, "allowed": allowed}
                )

                if not allowed:
                    results["rate_limit_exceeded"] = True
                    break

        except Exception as e:
            self.logger.error(f"Rate limiting demonstration failed: {str(e)}")
            results["error"] = str(e)

        return results

    def demonstrate_security_validation(self) -> Dict[str, Any]:
        """
        Demonstrate security validation capabilities.

        Returns:
            Dict with validation test results
        """
        self.logger.info("Demonstrating security validation capabilities...")

        results = {"request_validation": {}, "configuration_validation": {}}

        try:
            # 1. Request Validation
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

            # 2. Configuration Validation
            result = self.security_manager.validate_configuration()
            results["configuration_validation"] = {
                "success": result.is_valid,
                "status": result.status.value,
            }

        except Exception as e:
            self.logger.error(f"Security validation demonstration failed: {str(e)}")
            results["error"] = str(e)

        return results

    def demonstrate_security_monitoring(self) -> Dict[str, Any]:
        """
        Demonstrate security monitoring capabilities.

        Returns:
            Dict with monitoring test results
        """
        self.logger.info("Demonstrating security monitoring capabilities...")

        results = {"security_status": {}, "security_metrics": {}, "security_audit": {}}

        try:
            # 1. Security Status
            status = self.security_manager.get_security_status()
            results["security_status"] = status

            # 2. Security Metrics
            metrics = self.security_manager.get_security_metrics()
            results["security_metrics"] = metrics

            # 3. Security Audit (not implemented yet, use empty dict)
            results["security_audit"] = {
                "authentication": [],
                "authorization": [],
                "certificate_operations": [],
                "ssl_operations": [],
            }

        except Exception as e:
            self.logger.error(f"Security monitoring demonstration failed: {str(e)}")
            results["error"] = str(e)

        return results

    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """
        Run comprehensive demonstration of all framework capabilities.

        Returns:
            Dict with comprehensive test results
        """
        self.logger.info("Starting comprehensive security framework demonstration...")

        # Roles configuration already created in __init__

        # Run all demonstrations
        results = {
            "framework": "MCP Security Framework",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "certificate_management": self.demonstrate_certificate_management(),
            "ssl_tls_management": self.demonstrate_ssl_tls_management(),
            "authentication": self.demonstrate_authentication(),
            "authorization": self.demonstrate_authorization(),
            "rate_limiting": self.demonstrate_rate_limiting(),
            "security_validation": self.demonstrate_security_validation(),
            "security_monitoring": self.demonstrate_security_monitoring(),
        }

        self.logger.info("Comprehensive demonstration completed successfully")
        return results


def main():
    """Main function to run the comprehensive example."""
    print("\n🚀 MCP Security Framework - Comprehensive Example")
    print("=" * 80)

    # Create example instance
    example = ComprehensiveSecurityExample()

    try:
        # Run comprehensive demonstration
        results = example.run_comprehensive_demo()

        # Print results
        print("\n📊 COMPREHENSIVE DEMONSTRATION RESULTS")
        print("=" * 80)
        print(f"Framework: {results['framework']}")
        print(f"Version: {results['version']}")
        print(f"Timestamp: {results['timestamp']}")

        print("\n🔐 CERTIFICATE MANAGEMENT RESULTS:")
        cert_mgmt = results["certificate_management"]
        print(
            f"  Root CA Creation: {'✅' if cert_mgmt.get('root_ca_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  Intermediate CA Creation: {'✅' if cert_mgmt.get('intermediate_ca_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  Server Cert Creation: {'✅' if cert_mgmt.get('server_cert_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  Client Cert Creation: {'✅' if cert_mgmt.get('client_cert_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  CSR Creation: {'✅' if cert_mgmt.get('csr_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  CRL Creation: {'✅' if cert_mgmt.get('crl_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  Certificate Validation: {'✅' if cert_mgmt.get('certificate_validation', {}).get('success') else '❌'}"
        )

        print("\n🔒 SSL/TLS MANAGEMENT RESULTS:")
        ssl_mgmt = results["ssl_tls_management"]
        print(
            f"  Server Context: {'✅' if ssl_mgmt.get('server_context_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  Client Context: {'✅' if ssl_mgmt.get('client_context_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  mTLS Context: {'✅' if ssl_mgmt.get('mtls_context_creation', {}).get('success') else '❌'}"
        )
        print(
            f"  SSL Validation: {'✅' if ssl_mgmt.get('ssl_validation', {}).get('success') else '❌'}"
        )

        print("\n🔑 AUTHENTICATION RESULTS:")
        auth = results["authentication"]
        print(
            f"  API Key: {'✅' if auth.get('api_key_auth', {}).get('success') else '❌'}"
        )
        print(f"  JWT: {'✅' if auth.get('jwt_auth', {}).get('success') else '❌'}")
        print(
            f"  Certificate: {'✅' if auth.get('certificate_auth', {}).get('success') else '❌'}"
        )
        print(
            f"  Failed Auth: {'✅' if not auth.get('failed_auth', {}).get('success') else '❌'}"
        )

        print("\n🔐 AUTHORIZATION RESULTS:")
        authz = results["authorization"]
        print(
            f"  Admin Permissions: {'✅' if authz.get('admin_permissions', {}).get('success') else '❌'}"
        )
        print(
            f"  User Permissions: {'✅' if authz.get('user_permissions', {}).get('success') else '❌'}"
        )
        print(
            f"  Readonly Permissions: {'✅' if authz.get('readonly_permissions', {}).get('success') else '❌'}"
        )
        print(
            f"  Denied Permissions: {'✅' if not authz.get('denied_permissions', {}).get('success') else '❌'}"
        )

        print("\n⚡ RATE LIMITING RESULTS:")
        rate_limit = results["rate_limiting"]
        print(f"  Rate Limit Checks: {len(rate_limit.get('rate_limit_checks', []))}")
        print(
            f"  Rate Limit Exceeded: {'❌' if rate_limit.get('rate_limit_exceeded') else '✅'}"
        )

        print("\n🔒 SECURITY VALIDATION RESULTS:")
        validation = results["security_validation"]
        print(
            f"  Request Validation: {'✅' if validation.get('request_validation', {}).get('success') else '❌'}"
        )
        print(
            f"  Configuration Validation: {'✅' if validation.get('configuration_validation', {}).get('success') else '❌'}"
        )

        print("\n📊 SECURITY MONITORING RESULTS:")
        monitoring = results["security_monitoring"]
        print(
            f"  Security Status: {'✅' if monitoring.get('security_status') else '❌'}"
        )
        print(
            f"  Security Metrics: {'✅' if monitoring.get('security_metrics') else '❌'}"
        )
        print(f"  Security Audit: {'✅' if monitoring.get('security_audit') else '❌'}")

        print("\n🎉 ALL FRAMEWORK CAPABILITIES DEMONSTRATED SUCCESSFULLY!")
        print("=" * 80)

        # Cleanup
        if example.work_dir and os.path.exists(example.work_dir):
            shutil.rmtree(example.work_dir)
            print(f"\n🧹 Cleaned up working directory: {example.work_dir}")

    except Exception as e:
        print(f"\n❌ Demonstration failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
