"""
mTLS Middleware Module

This module provides specialized mTLS (mutual TLS) middleware that focuses
on mutual TLS authentication and certificate validation.

Key Features:
- mTLS authentication processing
- Client certificate validation
- Certificate chain verification
- Certificate-based role extraction
- mTLS event logging

Classes:
    MTLSMiddleware: mTLS-specific middleware
    MTLSMiddlewareError: mTLS middleware-specific error exception

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
import ssl
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ..schemas.models import AuthMethod, AuthResult, AuthStatus
from .security_middleware import SecurityMiddleware, SecurityMiddlewareError


class MTLSMiddlewareError(SecurityMiddlewareError):
    """Raised when mTLS middleware encounters an error."""

    def __init__(self, message: str, error_code: int = -32037):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class MTLSMiddleware(SecurityMiddleware):
    """
    mTLS (Mutual TLS) Middleware Class

    This class provides mTLS-specific middleware that focuses on mutual
    TLS authentication and certificate validation. It's designed for
    scenarios where client certificates are used for authentication.

    The MTLSMiddleware implements:
    - mTLS authentication processing
    - Client certificate validation
    - Certificate chain verification
    - Certificate-based role extraction
    - mTLS event logging

    Key Responsibilities:
    - Process requests through mTLS authentication pipeline
    - Validate client certificates
    - Verify certificate chains
    - Extract roles and permissions from certificates
    - Handle mTLS-specific error scenarios
    - Log mTLS authentication events

    Attributes:
        Inherits all attributes from SecurityMiddleware
        _certificate_cache (Dict): Cache for certificate validation results
        _ca_certificates (List): List of trusted CA certificates

    Example:
        >>> from mcp_security_framework.middleware import MTLSMiddleware
        >>>
        >>> security_manager = SecurityManager(config)
        >>> mtls_middleware = MTLSMiddleware(security_manager)
        >>> app.add_middleware(mtls_middleware)

    Note:
        This middleware requires proper SSL/TLS configuration on the
        server to handle client certificates.
    """

    def __init__(self, security_manager):
        """
        Initialize mTLS Middleware.

        Args:
            security_manager: Security manager instance containing
                all security components and configuration.

        Raises:
            MTLSMiddlewareError: If initialization fails
        """
        super().__init__(security_manager)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize certificate cache
        self._certificate_cache: Dict[str, Dict[str, Any]] = {}

        # Load CA certificates if configured
        self._ca_certificates = self._load_ca_certificates()

        self.logger.info(
            "mTLS middleware initialized",
            extra={"ca_certificates_count": len(self._ca_certificates)},
        )

    @abstractmethod
    def __call__(self, request: Any, call_next: Any) -> Any:
        """
        Process request through mTLS middleware.

        This method implements the mTLS authentication processing
        pipeline, focusing on client certificate validation.

        Args:
            request: Framework-specific request object
            call_next: Framework-specific call_next function

        Returns:
            Framework-specific response object

        Raises:
            MTLSMiddlewareError: If mTLS processing fails
        """
        pass

    def _authenticate_mtls(self, request: Any) -> AuthResult:
        """
        Perform mTLS authentication.

        This method handles mutual TLS authentication by validating
        client certificates and extracting user information.

        Args:
            request: Framework-specific request object

        Returns:
            AuthResult: Authentication result with user information

        Raises:
            MTLSMiddlewareError: If mTLS authentication fails
        """
        try:
            # Get client certificate from request
            client_cert = self._get_client_certificate(request)
            if not client_cert:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.FAILED,
                    username=None,
                    roles=[],
                    auth_method=AuthMethod.CERTIFICATE,
                    error_code=-32038,
                    error_message="No client certificate provided",
                )

            # Validate client certificate
            cert_validation = self._validate_client_certificate(client_cert)
            if not cert_validation["is_valid"]:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.FAILED,
                    username=None,
                    roles=[],
                    auth_method=AuthMethod.CERTIFICATE,
                    error_code=-32039,
                    error_message=cert_validation["error_message"],
                )

            # Extract user information from certificate
            user_info = self._extract_user_info_from_certificate(client_cert)

            # Extract roles from certificate
            roles = self._extract_roles_from_certificate(client_cert)

            self.logger.info(
                "mTLS authentication successful",
                extra={
                    "username": user_info["username"],
                    "subject": user_info["subject"],
                    "issuer": user_info["issuer"],
                    "roles": roles,
                },
            )

            return AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username=user_info["username"],
                roles=roles,
                auth_method=AuthMethod.CERTIFICATE,
            )

        except Exception as e:
            self.logger.error(
                "mTLS authentication failed", extra={"error": str(e)}, exc_info=True
            )
            raise MTLSMiddlewareError(
                f"mTLS authentication failed: {str(e)}", error_code=-32040
            )

    def _get_client_certificate(self, request: Any) -> Optional[str]:
        """
        Get client certificate from request.

        Args:
            request: Framework-specific request object

        Returns:
            Optional[str]: Client certificate in PEM format if available
        """
        # This should be implemented by framework-specific subclasses
        # to extract the client certificate from the request
        return None

    def _validate_client_certificate(self, cert_pem: str) -> Dict[str, Any]:
        """
        Validate client certificate.

        Args:
            cert_pem (str): Client certificate in PEM format

        Returns:
            Dict[str, Any]: Validation result with status and details
        """
        try:
            # Use security manager's certificate validation
            is_valid = self.security_manager.cert_manager.validate_certificate_chain(
                cert_pem, self.config.ssl.ca_cert_file if self.config.ssl else None
            )

            if is_valid:
                return {"is_valid": True, "error_message": ""}
            else:
                return {
                    "is_valid": False,
                    "error_message": "Certificate validation failed",
                }

        except Exception as e:
            return {
                "is_valid": False,
                "error_message": f"Certificate validation error: {str(e)}",
            }

    def _extract_user_info_from_certificate(self, cert_pem: str) -> Dict[str, str]:
        """
        Extract user information from certificate.

        Args:
            cert_pem (str): Client certificate in PEM format

        Returns:
            Dict[str, str]: User information extracted from certificate
        """
        try:
            # Use security manager's certificate utilities
            cert_info = self.security_manager.cert_manager.get_certificate_info(
                cert_pem
            )

            return {
                "username": cert_info.get("common_name", "unknown"),
                "subject": cert_info.get("subject", ""),
                "issuer": cert_info.get("issuer", ""),
                "serial_number": cert_info.get("serial_number", ""),
                "valid_from": str(cert_info.get("valid_from", "")),
                "valid_until": str(cert_info.get("valid_until", "")),
            }

        except Exception as e:
            self.logger.error(
                "Failed to extract user info from certificate", extra={"error": str(e)}
            )
            return {
                "username": "unknown",
                "subject": "",
                "issuer": "",
                "serial_number": "",
                "valid_from": "",
                "valid_until": "",
            }

    def _extract_roles_from_certificate(self, cert_pem: str) -> List[str]:
        """
        Extract roles from certificate.

        Args:
            cert_pem (str): Client certificate in PEM format

        Returns:
            List[str]: List of roles extracted from certificate
        """
        try:
            # Use security manager's certificate utilities
            roles = self.security_manager.cert_manager.extract_roles_from_certificate(
                cert_pem
            )
            return roles

        except Exception as e:
            self.logger.error(
                "Failed to extract roles from certificate", extra={"error": str(e)}
            )
            return []

    def _load_ca_certificates(self) -> List[str]:
        """
        Load trusted CA certificates.

        Returns:
            List[str]: List of CA certificates in PEM format
        """
        ca_certs = []

        try:
            if self.config.ssl and self.config.ssl.ca_cert_file:
                # Load CA certificate from file
                with open(self.config.ssl.ca_cert_file, "r") as f:
                    ca_certs.append(f.read())

        except Exception as e:
            self.logger.error("Failed to load CA certificates", extra={"error": str(e)})

        return ca_certs

    def _verify_certificate_chain(self, cert_pem: str) -> bool:
        """
        Verify certificate chain against trusted CAs.

        Args:
            cert_pem (str): Client certificate in PEM format

        Returns:
            bool: True if chain is valid, False otherwise
        """
        try:
            # This would implement certificate chain verification
            # against the loaded CA certificates
            return True

        except Exception as e:
            self.logger.error(
                "Certificate chain verification failed", extra={"error": str(e)}
            )
            return False

    def _check_certificate_revocation(self, cert_pem: str) -> bool:
        """
        Check if certificate is revoked.

        Args:
            cert_pem (str): Client certificate in PEM format

        Returns:
            bool: True if certificate is not revoked, False otherwise
        """
        try:
            # This would implement CRL or OCSP checking
            # For now, assume certificate is not revoked
            return True

        except Exception as e:
            self.logger.error(
                "Certificate revocation check failed", extra={"error": str(e)}
            )
            return False

    def _log_mtls_event(
        self,
        event_type: str,
        cert_info: Dict[str, Any],
        request_details: Dict[str, Any],
    ) -> None:
        """
        Log mTLS event.

        Args:
            event_type (str): Type of mTLS event
            cert_info (Dict[str, Any]): Certificate information
            request_details (Dict[str, Any]): Request details
        """
        self.logger.info(
            f"mTLS event: {event_type}",
            extra={
                "event_type": event_type,
                "username": cert_info.get("username", "unknown"),
                "subject": cert_info.get("subject", ""),
                "issuer": cert_info.get("issuer", ""),
                "serial_number": cert_info.get("serial_number", ""),
                **request_details,
            },
        )

    def get_certificate_info(self, cert_pem: str) -> Dict[str, Any]:
        """
        Get detailed certificate information.

        Args:
            cert_pem (str): Certificate in PEM format

        Returns:
            Dict[str, Any]: Detailed certificate information
        """
        try:
            return self.security_manager.cert_manager.get_certificate_info(cert_pem)
        except Exception as e:
            self.logger.error("Failed to get certificate info", extra={"error": str(e)})
            return {"error": str(e)}

    def validate_certificate_chain(self, cert_pem: str) -> bool:
        """
        Validate certificate chain.

        Args:
            cert_pem (str): Certificate in PEM format

        Returns:
            bool: True if chain is valid, False otherwise
        """
        try:
            return self.security_manager.cert_manager.validate_certificate_chain(
                cert_pem, self.config.ssl.ca_cert_file if self.config.ssl else None
            )
        except Exception as e:
            self.logger.error(
                "Certificate chain validation failed", extra={"error": str(e)}
            )
            return False
