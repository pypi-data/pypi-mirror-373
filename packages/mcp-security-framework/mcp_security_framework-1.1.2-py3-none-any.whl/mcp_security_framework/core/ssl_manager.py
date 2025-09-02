"""
SSL/TLS Manager Module

This module provides comprehensive SSL/TLS management for the MCP Security
Framework. It handles SSL context creation, certificate validation, and
TLS configuration management.

Key Features:
- SSL context creation for servers and clients
- Certificate validation and verification
- TLS version and cipher management
- Certificate information extraction
- SSL configuration management
- Certificate chain validation

Classes:
    SSLManager: Main SSL/TLS management class
    SSLContextBuilder: Builder for SSL contexts
    CertificateValidator: Certificate validation utilities

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
import ssl
from pathlib import Path
from typing import Dict, List, Optional, Union

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from ..schemas.config import SSLConfig
from ..schemas.models import CertificateInfo
from ..utils.cert_utils import (
    extract_certificate_info,
    get_certificate_expiry,
    is_certificate_self_signed,
    parse_certificate,
    validate_certificate_chain,
)


class SSLManager:
    """
    SSL/TLS Management Class

    This class provides comprehensive SSL/TLS management capabilities including
    SSL context creation, certificate validation, and TLS configuration.

    The SSLManager handles:
    - Server and client SSL context creation
    - Certificate validation and verification
    - TLS version and cipher management
    - Certificate information extraction
    - SSL configuration management
    - Certificate chain building and validation

    Attributes:
        config (SSLConfig): SSL configuration settings
        logger (Logger): Logger instance for SSL operations
        _contexts (Dict): Cache of created SSL contexts
        _certificate_cache (Dict): Cache of certificate information

    Example:
        >>> config = SSLConfig(enabled=True, cert_file="server.crt")
        >>> ssl_manager = SSLManager(config)
        >>> context = ssl_manager.create_server_context()

    Raises:
        SSLConfigurationError: When SSL configuration is invalid
        CertificateValidationError: When certificate validation fails
    """

    def __init__(self, config: SSLConfig):
        """
        Initialize SSL Manager.

        Args:
            config (SSLConfig): SSL configuration settings containing
                certificate paths, TLS versions, and verification settings.
                Must be a valid SSLConfig instance with proper certificate
                file paths and TLS configuration.

        Raises:
            SSLConfigurationError: If configuration is invalid or certificate
                files are not accessible.

        Example:
            >>> config = SSLConfig(enabled=True, cert_file="server.crt")
            >>> ssl_manager = SSLManager(config)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._contexts: Dict[str, ssl.SSLContext] = {}
        self._certificate_cache: Dict[str, CertificateInfo] = {}

        # Validate configuration
        self._validate_configuration()

        self.logger.info(
            "SSLManager initialized successfully",
            extra={
                "enabled": config.enabled,
                "min_tls_version": config.min_tls_version,
                "verify_mode": config.verify_mode,
            },
        )

    def create_server_context(
        self,
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None,
        ca_cert_file: Optional[str] = None,
        verify_mode: Optional[str] = None,
        min_version: Optional[str] = None,
    ) -> ssl.SSLContext:
        """
        Create SSL context for server operations.

        This method creates and configures an SSL context suitable for server
        operations. It handles certificate loading, key management, and TLS
        configuration according to the provided parameters.

        Args:
            cert_file (Optional[str]): Path to server certificate file.
                If None, uses certificate from config. Must be a valid PEM
                or DER certificate file path.
            key_file (Optional[str]): Path to server private key file.
                If None, uses key from config. Must be a valid PEM or DER
                private key file path.
            ca_cert_file (Optional[str]): Path to CA certificate file for
                client certificate verification. If None, uses CA from config.
                Must be a valid PEM certificate file path.
            verify_mode (Optional[str]): SSL verification mode. Valid values:
                - "CERT_NONE": No certificate verification
                - "CERT_OPTIONAL": Certificate verification optional
                - "CERT_REQUIRED": Certificate verification required
                If None, uses verify_mode from config.
            min_version (Optional[str]): Minimum TLS version. Valid values:
                - "TLSv1.0": TLS 1.0
                - "TLSv1.1": TLS 1.1
                - "TLSv1.2": TLS 1.2
                - "TLSv1.3": TLS 1.3
                If None, uses min_tls_version from config.

        Returns:
            ssl.SSLContext: Configured SSL context for server operations.
                The context is properly configured with certificates, keys,
                and TLS settings for secure server communication.

        Raises:
            SSLConfigurationError: If SSL configuration is invalid or
                certificate/key files cannot be loaded.
            CertificateValidationError: If certificate validation fails.
            FileNotFoundError: If certificate or key files are not found.
            PermissionError: If certificate or key files are not readable.

        Example:
            >>> ssl_manager = SSLManager(config)
            >>> context = ssl_manager.create_server_context(
            ...     cert_file="server.crt",
            ...     key_file="server.key",
            ...     verify_mode="CERT_REQUIRED"
            ... )
            >>> # Use context for HTTPS server
        """
        try:
            # Use config values if not provided
            cert_file = cert_file or self.config.cert_file
            key_file = key_file or self.config.key_file
            ca_cert_file = ca_cert_file or self.config.ca_cert_file
            verify_mode = verify_mode or self.config.verify_mode
            min_version = min_version or self.config.min_tls_version

            # Validate required files
            if not cert_file:
                raise SSLConfigurationError("Server certificate file is required")
            if not key_file:
                raise SSLConfigurationError("Server private key file is required")

            # Check cache
            cache_key = f"server_{cert_file}_{key_file}_{ca_cert_file}_{verify_mode}_{min_version}"
            if cache_key in self._contexts:
                return self._contexts[cache_key]

            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

            # Configure verification mode
            context.verify_mode = self._get_verify_mode(verify_mode)

            # Set minimum TLS version
            context.minimum_version = self._get_tls_version(min_version)

            # Load certificate and key
            context.load_cert_chain(cert_file, key_file)

            # Load CA certificate if provided
            if ca_cert_file:
                context.load_verify_locations(ca_cert_file)

            # Configure cipher suites
            if self.config.cipher_suite:
                context.set_ciphers(self.config.cipher_suite)

            # Cache context
            self._contexts[cache_key] = context

            self.logger.info(
                "Server SSL context created successfully",
                extra={
                    "cert_file": cert_file,
                    "key_file": key_file,
                    "verify_mode": verify_mode,
                    "min_version": min_version,
                },
            )

            return context

        except Exception as e:
            self.logger.error(
                "Failed to create server SSL context",
                extra={"cert_file": cert_file, "key_file": key_file, "error": str(e)},
            )
            raise SSLConfigurationError(
                f"Failed to create server SSL context: {str(e)}"
            )

    def create_client_context(
        self,
        ca_cert_file: Optional[str] = None,
        client_cert_file: Optional[str] = None,
        client_key_file: Optional[str] = None,
        verify_mode: Optional[str] = None,
        min_version: Optional[str] = None,
    ) -> ssl.SSLContext:
        """
        Create SSL context for client operations.

        This method creates and configures an SSL context suitable for client
        operations. It handles certificate loading and TLS configuration for
        secure client connections.

        Args:
            ca_cert_file (Optional[str]): Path to CA certificate file for
                server certificate verification. If None, uses CA from config.
                Must be a valid PEM certificate file path.
            client_cert_file (Optional[str]): Path to client certificate file
                for client authentication. If None, uses client cert from config.
                Must be a valid PEM certificate file path.
            client_key_file (Optional[str]): Path to client private key file.
                If None, uses client key from config. Must be a valid PEM
                private key file path.
            verify_mode (Optional[str]): SSL verification mode. Valid values:
                - "CERT_NONE": No certificate verification
                - "CERT_OPTIONAL": Certificate verification optional
                - "CERT_REQUIRED": Certificate verification required
                If None, uses verify_mode from config.
            min_version (Optional[str]): Minimum TLS version. Valid values:
                - "TLSv1.0": TLS 1.0
                - "TLSv1.1": TLS 1.1
                - "TLSv1.2": TLS 1.2
                - "TLSv1.3": TLS 1.3
                If None, uses min_tls_version from config.

        Returns:
            ssl.SSLContext: Configured SSL context for client operations.
                The context is properly configured for secure client communication.

        Raises:
            SSLConfigurationError: If SSL configuration is invalid or
                certificate files cannot be loaded.
            CertificateValidationError: If certificate validation fails.
            FileNotFoundError: If certificate files are not found.
            PermissionError: If certificate files are not readable.

        Example:
            >>> ssl_manager = SSLManager(config)
            >>> context = ssl_manager.create_client_context(
            ...     ca_cert_file="ca.crt",
            ...     client_cert_file="client.crt",
            ...     client_key_file="client.key"
            ... )
            >>> # Use context for HTTPS client
        """
        try:
            # Use config values if not provided
            ca_cert_file = ca_cert_file or self.config.ca_cert_file
            client_cert_file = client_cert_file or self.config.client_cert_file
            client_key_file = client_key_file or self.config.client_key_file
            verify_mode = verify_mode or self.config.verify_mode
            min_version = min_version or self.config.min_tls_version

            # Check cache
            cache_key = f"client_{ca_cert_file}_{client_cert_file}_{client_key_file}_{verify_mode}_{min_version}"
            if cache_key in self._contexts:
                return self._contexts[cache_key]

            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

            # Configure verification mode
            context.verify_mode = self._get_verify_mode(verify_mode)

            # Set minimum TLS version
            context.minimum_version = self._get_tls_version(min_version)

            # Load CA certificate if provided
            if ca_cert_file:
                context.load_verify_locations(ca_cert_file)

            # Load client certificate and key if provided
            if client_cert_file and client_key_file:
                context.load_cert_chain(client_cert_file, client_key_file)

            # Configure cipher suites
            if self.config.cipher_suite:
                context.set_ciphers(self.config.cipher_suite)

            # Cache context
            self._contexts[cache_key] = context

            self.logger.info(
                "Client SSL context created successfully",
                extra={
                    "ca_cert_file": ca_cert_file,
                    "client_cert_file": client_cert_file,
                    "verify_mode": verify_mode,
                    "min_version": min_version,
                },
            )

            return context

        except Exception as e:
            self.logger.error(
                "Failed to create client SSL context",
                extra={
                    "ca_cert_file": ca_cert_file,
                    "client_cert_file": client_cert_file,
                    "error": str(e),
                },
            )
            raise SSLConfigurationError(
                f"Failed to create client SSL context: {str(e)}"
            )

    def validate_certificate(self, cert_path: str) -> bool:
        """
        Validate certificate file.

        This method validates a certificate file by checking its format,
        parsing it, and verifying basic certificate properties.

        Args:
            cert_path (str): Path to certificate file to validate.
                Must be a valid PEM or DER certificate file path.

        Returns:
            bool: True if certificate is valid, False otherwise.
                Returns True when certificate can be parsed and has
                valid basic properties.

        Raises:
            FileNotFoundError: If certificate file is not found.
            PermissionError: If certificate file is not readable.

        Example:
            >>> ssl_manager = SSLManager(config)
            >>> is_valid = ssl_manager.validate_certificate("server.crt")
            >>> if is_valid:
            ...     print("Certificate is valid")
            >>> else:
            ...     print("Certificate is invalid")
        """
        try:
            # Check if file exists
            if not Path(cert_path).exists():
                self.logger.error(f"Certificate file not found: {cert_path}")
                return False

            # Parse certificate
            cert = parse_certificate(cert_path)

            # Basic validation
            if not cert:
                return False

            # Check if certificate is expired
            expiry_info = get_certificate_expiry(cert_path)
            if expiry_info["is_expired"]:
                self.logger.warning(
                    "Certificate is expired",
                    extra={
                        "cert_path": cert_path,
                        "expiry_date": expiry_info["not_after"],
                    },
                )
                return False

            self.logger.info(
                "Certificate validation successful", extra={"cert_path": cert_path}
            )

            return True

        except Exception as e:
            self.logger.error(
                "Certificate validation failed",
                extra={"cert_path": cert_path, "error": str(e)},
            )
            return False

    def get_certificate_info(self, cert_path: str) -> CertificateInfo:
        """
        Get detailed certificate information.

        This method extracts comprehensive information from a certificate
        including subject, issuer, validity dates, and extensions.

        Args:
            cert_path (str): Path to certificate file. Must be a valid
                PEM or DER certificate file path.

        Returns:
            CertificateInfo: Certificate information object containing:
                - subject: Certificate subject
                - issuer: Certificate issuer
                - serial_number: Certificate serial number
                - not_before: Certificate validity start date
                - not_after: Certificate validity end date
                - key_algorithm: Public key algorithm
                - key_size: Public key size in bits
                - signature_algorithm: Signature algorithm
                - extensions: Certificate extensions
                - is_self_signed: Whether certificate is self-signed
                - fingerprint_sha1: SHA1 fingerprint
                - fingerprint_sha256: SHA256 fingerprint

        Raises:
            CertificateValidationError: If certificate cannot be parsed
                or information extraction fails.
            FileNotFoundError: If certificate file is not found.
            PermissionError: If certificate file is not readable.

        Example:
            >>> ssl_manager = SSLManager(config)
            >>> info = ssl_manager.get_certificate_info("server.crt")
            >>> print(f"Subject: {info.subject}")
            >>> print(f"Expires: {info.not_after}")
            >>> print(f"Key size: {info.key_size} bits")
        """
        try:
            # Check cache first
            if cert_path in self._certificate_cache:
                return self._certificate_cache[cert_path]

            # Extract certificate information
            cert_data = extract_certificate_info(cert_path)

            # Create CertificateInfo object
            cert_info = CertificateInfo(
                subject=cert_data.get("subject", ""),
                issuer=cert_data.get("issuer", ""),
                serial_number=cert_data.get("serial_number", ""),
                not_before=cert_data.get("not_before"),
                not_after=cert_data.get("not_after"),
                key_algorithm=cert_data.get("public_key_algorithm", ""),
                key_size=cert_data.get("key_size", 0),
                signature_algorithm=cert_data.get("signature_algorithm", ""),
                extensions=cert_data.get("extensions", {}),
                is_self_signed=is_certificate_self_signed(cert_path),
                fingerprint_sha1=cert_data.get("fingerprint_sha1", ""),
                fingerprint_sha256=cert_data.get("fingerprint_sha256", ""),
            )

            # Cache the result
            self._certificate_cache[cert_path] = cert_info

            self.logger.info(
                "Certificate information extracted successfully",
                extra={"cert_path": cert_path},
            )

            return cert_info

        except Exception as e:
            self.logger.error(
                "Failed to get certificate information",
                extra={"cert_path": cert_path, "error": str(e)},
            )
            raise CertificateValidationError(
                f"Failed to get certificate information: {str(e)}"
            )

    def validate_certificate_chain(self, cert_path: str, ca_cert_path: str) -> bool:
        """
        Validate certificate chain against CA certificate.

        This method validates a certificate chain by checking if the
        certificate is signed by the provided CA certificate.

        Args:
            cert_path (str): Path to certificate to validate. Must be a
                valid PEM or DER certificate file path.
            ca_cert_path (str): Path to CA certificate. Must be a valid
                PEM or DER certificate file path.

        Returns:
            bool: True if certificate chain is valid, False otherwise.
                Returns True when certificate is properly signed by the
                CA certificate.

        Raises:
            FileNotFoundError: If certificate files are not found.
            PermissionError: If certificate files are not readable.

        Example:
            >>> ssl_manager = SSLManager(config)
            >>> is_valid = ssl_manager.validate_certificate_chain(
            ...     "server.crt", "ca.crt"
            ... )
            >>> if is_valid:
            ...     print("Certificate chain is valid")
            >>> else:
            ...     print("Certificate chain is invalid")
        """
        try:
            # Validate certificate chain
            is_valid = validate_certificate_chain(cert_path, ca_cert_path)

            self.logger.info(
                "Certificate chain validation completed",
                extra={
                    "cert_path": cert_path,
                    "ca_cert_path": ca_cert_path,
                    "is_valid": is_valid,
                },
            )

            return is_valid

        except Exception as e:
            self.logger.error(
                "Certificate chain validation failed",
                extra={
                    "cert_path": cert_path,
                    "ca_cert_path": ca_cert_path,
                    "error": str(e),
                },
            )
            return False

    def check_certificate_expiry(self, cert_path: str) -> Dict:
        """
        Check certificate expiry information.

        This method provides detailed information about certificate
        expiry including days until expiry and expiry status.

        Args:
            cert_path (str): Path to certificate file. Must be a valid
                PEM or DER certificate file path.

        Returns:
            Dict: Certificate expiry information containing:
                - not_after: Certificate expiry date
                - not_before: Certificate validity start date
                - days_until_expiry: Days until certificate expires
                - is_expired: Whether certificate is expired
                - expires_soon: Whether certificate expires within 30 days
                - status: Expiry status (valid, expires_soon, expired)
                - total_seconds_until_expiry: Seconds until expiry

        Raises:
            CertificateValidationError: If certificate cannot be parsed
                or expiry information extraction fails.
            FileNotFoundError: If certificate file is not found.
            PermissionError: If certificate file is not readable.

        Example:
            >>> ssl_manager = SSLManager(config)
            >>> expiry_info = ssl_manager.check_certificate_expiry("server.crt")
            >>> if expiry_info["is_expired"]:
            ...     print("Certificate is expired!")
            >>> elif expiry_info["expires_soon"]:
            ...     print(f"Certificate expires in {expiry_info['days_until_expiry']} days")
        """
        try:
            expiry_info = get_certificate_expiry(cert_path)

            self.logger.info(
                "Certificate expiry check completed",
                extra={
                    "cert_path": cert_path,
                    "days_until_expiry": expiry_info["days_until_expiry"],
                    "status": expiry_info["status"],
                },
            )

            return expiry_info

        except Exception as e:
            self.logger.error(
                "Certificate expiry check failed",
                extra={"cert_path": cert_path, "error": str(e)},
            )
            raise CertificateValidationError(
                f"Certificate expiry check failed: {str(e)}"
            )

    def clear_cache(self) -> None:
        """Clear SSL context and certificate caches."""
        self._contexts.clear()
        self._certificate_cache.clear()
        self.logger.info("SSL caches cleared")

    @property
    def is_ssl_enabled(self) -> bool:
        """
        Check if SSL/TLS is enabled in the configuration.

        This property indicates whether SSL/TLS functionality is enabled
        based on the current configuration settings.

        Returns:
            bool: True if SSL/TLS is enabled, False otherwise.
                Returns True when config.enabled is True and valid
                certificate/key files are configured.

        Example:
            >>> ssl_manager = SSLManager(config)
            >>> if ssl_manager.is_ssl_enabled:
            ...     context = ssl_manager.create_server_context()
            ...     print("SSL context created successfully")
            >>> else:
            ...     print("SSL is not properly configured")
        """
        return (
            self.config.enabled
            and self.config.cert_file
            and self.config.key_file
            and Path(self.config.cert_file).exists()
            and Path(self.config.key_file).exists()
        )

    @property
    def supported_tls_versions(self) -> List[str]:
        """
        Get list of supported TLS versions.

        Returns:
            List[str]: List of supported TLS version strings.
        """
        return ["TLSv1.0", "TLSv1.1", "TLSv1.2", "TLSv1.3"]

    @property
    def default_cipher_suite(self) -> str:
        """
        Get default cipher suite configuration.

        Returns:
            str: Default cipher suite string.
        """
        return self.config.cipher_suite or "ECDHE-RSA-AES256-GCM-SHA384"

    def _validate_configuration(self) -> None:
        """Validate SSL configuration."""
        if not self.config.enabled:
            return

        # Check certificate files if SSL is enabled
        if self.config.cert_file and not Path(self.config.cert_file).exists():
            raise SSLConfigurationError(
                f"Certificate file not found: {self.config.cert_file}"
            )

        if self.config.key_file and not Path(self.config.key_file).exists():
            raise SSLConfigurationError(
                f"Private key file not found: {self.config.key_file}"
            )

        if self.config.ca_cert_file and not Path(self.config.ca_cert_file).exists():
            raise SSLConfigurationError(
                f"CA certificate file not found: {self.config.ca_cert_file}"
            )

    def _get_verify_mode(self, verify_mode: str) -> int:
        """Convert verify mode string to SSL constant."""
        verify_modes = {
            "CERT_NONE": ssl.CERT_NONE,
            "CERT_OPTIONAL": ssl.CERT_OPTIONAL,
            "CERT_REQUIRED": ssl.CERT_REQUIRED,
        }

        if verify_mode not in verify_modes:
            raise SSLConfigurationError(f"Invalid verify mode: {verify_mode}")

        return verify_modes[verify_mode]

    def _get_tls_version(self, version: str) -> int:
        """Convert TLS version string to SSL constant."""
        tls_versions = {
            "TLSv1.0": ssl.TLSVersion.TLSv1,
            "TLSv1.1": ssl.TLSVersion.TLSv1_1,
            "TLSv1.2": ssl.TLSVersion.TLSv1_2,
            "TLSv1.3": ssl.TLSVersion.TLSv1_3,
        }

        if version not in tls_versions:
            raise SSLConfigurationError(f"Invalid TLS version: {version}")

        return tls_versions[version]


class SSLConfigurationError(Exception):
    """Raised when SSL configuration is invalid."""

    def __init__(self, message: str, error_code: int = -32001):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class CertificateValidationError(Exception):
    """Raised when certificate validation fails."""

    def __init__(self, message: str, error_code: int = -32002):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
