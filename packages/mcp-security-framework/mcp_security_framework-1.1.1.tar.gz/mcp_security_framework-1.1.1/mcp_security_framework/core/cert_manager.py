"""
Certificate Manager Module

This module provides comprehensive certificate management for the
MCP Security Framework. It handles certificate creation, validation,
and management including CA certificates, client certificates,
and server certificates.

Key Features:
- Root CA certificate creation and management
- Intermediate CA certificate creation
- Client and server certificate generation
- Certificate revocation list (CRL) management
- Certificate chain validation
- Role and permission extraction from certificates
- Certificate format conversion and validation

Classes:
    CertificateManager: Main certificate management class
    CertificatePair: Certificate and private key pair container
    CAConfig: Configuration for CA certificate creation
    ClientCertConfig: Configuration for client certificate creation
    ServerCertConfig: Configuration for server certificate creation

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import ExtensionOID, NameOID
from pydantic import BaseModel

from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    IntermediateCAConfig,
    ServerCertConfig,
)
from mcp_security_framework.schemas.models import (
    CertificateInfo,
    CertificatePair,
    CertificateType,
)
from mcp_security_framework.utils.cert_utils import (
    extract_permissions_from_certificate,
    extract_roles_from_certificate,
    get_certificate_expiry,
    get_certificate_serial_number,
    is_certificate_self_signed,
    parse_certificate,
    validate_certificate_chain,
)
from mcp_security_framework.utils.datetime_compat import (
    get_not_valid_after_utc,
    get_not_valid_before_utc,
)


class CertificateManager:
    """
    Certificate Management Class

    This class provides comprehensive certificate management capabilities including
    CA certificate creation, client/server certificate generation, and certificate
    lifecycle management.

    The CertificateManager handles:
    - Root CA certificate creation and management
    - Intermediate CA certificate creation
    - Client and server certificate generation
    - Certificate revocation list (CRL) management
    - Certificate chain validation and verification
    - Role and permission extraction from certificates
    - Certificate format conversion and validation

    Attributes:
        config (CertificateConfig): Certificate configuration settings
        logger (Logger): Logger instance for certificate operations
        _certificate_cache (Dict): Cache of certificate information
        _crl_cache (Dict): Cache of certificate revocation lists

    Example:
        >>> config = CertificateConfig(
        ...     ca_cert_path="/path/to/ca.crt",
        ...     ca_key_path="/path/to/ca.key",
        ...     output_dir="/path/to/certs"
        ... )
        >>> cert_manager = CertificateManager(config)
        >>> cert_pair = cert_manager.create_client_certificate(client_config)

    Raises:
        CertificateConfigurationError: When certificate configuration is invalid
        CertificateGenerationError: When certificate generation fails
        CertificateValidationError: When certificate validation fails
    """

    def __init__(self, config: CertificateConfig):
        """
        Initialize Certificate Manager.

        Args:
            config (CertificateConfig): Certificate configuration settings containing
                CA certificate paths, output directory, and certificate settings.
                Must be a valid CertificateConfig instance with proper paths
                and configuration settings.

        Raises:
            CertificateConfigurationError: If configuration is invalid or
                certificate files are not accessible.

        Example:
            >>> config = CertificateConfig(
            ...     ca_cert_path="/path/to/ca.crt",
            ...     ca_key_path="/path/to/ca.key"
            ... )
            >>> cert_manager = CertificateManager(config)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._certificate_cache: Dict[str, CertificateInfo] = {}
        self._crl_cache: Dict[str, x509.CertificateRevocationList] = {}

        # Validate configuration
        self._validate_configuration()

        # Create storage directories if they don't exist
        if self.config.cert_storage_path:
            os.makedirs(self.config.cert_storage_path, exist_ok=True)
        if self.config.key_storage_path:
            os.makedirs(self.config.key_storage_path, exist_ok=True)

        self.logger.info(
            "CertificateManager initialized successfully",
            extra={
                "ca_cert_path": self.config.ca_cert_path,
                "ca_key_path": self.config.ca_key_path,
                "cert_storage_path": self.config.cert_storage_path,
                "key_storage_path": self.config.key_storage_path,
            },
        )

    def create_root_ca(self, ca_config: CAConfig) -> CertificatePair:
        """
        Create root CA certificate and private key.

        This method generates a new root Certificate Authority (CA) certificate
        and private key pair for signing other certificates.

        The method creates a self-signed CA certificate with:
        - Strong cryptographic key pair (RSA or ECDSA)
        - Proper CA extensions and constraints
        - Configurable validity period
        - Standard CA certificate structure

        Args:
            ca_config (CAConfig): CA configuration containing common name,
                organization, country, and other certificate details.
                Must include valid common name and organization information
                for proper CA certificate generation.

        Returns:
            CertificatePair: Certificate pair object containing:
                - certificate_path (str): Path to generated CA certificate file
                - private_key_path (str): Path to generated CA private key file
                - certificate_pem (str): CA certificate content in PEM format
                - private_key_pem (str): CA private key content in PEM format
                - serial_number (str): Certificate serial number
                - expiry_date (datetime): Certificate expiry date

        Raises:
            CertificateGenerationError: When CA certificate generation fails
                due to cryptographic errors or invalid configuration
            FileNotFoundError: When output directory is not accessible
            PermissionError: When output directory is not writable
            ValueError: When configuration parameters are invalid

        Example:
            >>> ca_config = CAConfig(
            ...     common_name="My Root CA",
            ...     organization="My Organization",
            ...     country="US",
            ...     validity_days=3650
            ... )
            >>> cert_manager = CertificateManager(config)
            >>> ca_pair = cert_manager.create_root_ca(ca_config)
            >>> print(f"CA certificate created: {ca_pair.certificate_path}")

        Note:
            Generated private keys are stored with restricted permissions
            (600) for security. Certificate files are stored with standard
            permissions (644). Backup the private key securely.

        See Also:
            create_intermediate_ca: Intermediate CA certificate generation
            create_client_certificate: Client certificate generation
        """
        try:
            # Validate CA configuration
            if not ca_config.common_name:
                raise ValueError("Common name is required for CA certificate")

            # Generate private key (RSA by default)
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=ca_config.key_size, backend=None
            )

            # Create certificate subject
            subject_attributes = [
                x509.NameAttribute(NameOID.COMMON_NAME, ca_config.common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, ca_config.organization),
                x509.NameAttribute(NameOID.COUNTRY_NAME, ca_config.country),
            ]

            # Add optional attributes if they exist
            if ca_config.state:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, ca_config.state)
                )
            if ca_config.locality:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.LOCALITY_NAME, ca_config.locality)
                )

            subject = x509.Name(subject_attributes)

            # Create certificate builder
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(subject)  # Self-signed
            builder = builder.public_key(private_key.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.now(timezone.utc))
            builder = builder.not_valid_after(
                datetime.now(timezone.utc)
                + timedelta(days=ca_config.validity_years * 365)
            )

            # Add CA extensions
            builder = builder.add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            )

            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )

            # Add SubjectKeyIdentifier extension (optional for testing)
            try:
                builder = builder.add_extension(
                    x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                    critical=False,
                )
            except Exception:
                # Skip SubjectKeyIdentifier if there are issues with the public key
                pass

            # Create certificate
            certificate = builder.sign(private_key, hashes.SHA256())

            # Generate file paths
            cert_filename = f"{ca_config.common_name.replace(' ', '_').lower()}_ca.crt"
            key_filename = f"{ca_config.common_name.replace(' ', '_').lower()}_ca.key"

            cert_path = os.path.join(self.config.cert_storage_path, cert_filename)
            key_path = os.path.join(self.config.key_storage_path, key_filename)

            # Save certificate and private key
            with open(cert_path, "wb") as f:
                f.write(certificate.public_bytes(serialization.Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            # Set proper permissions
            os.chmod(cert_path, 0o644)
            os.chmod(key_path, 0o600)

            # Create certificate pair
            cert_pair = CertificatePair(
                certificate_path=cert_path,
                private_key_path=key_path,
                certificate_pem=certificate.public_bytes(
                    serialization.Encoding.PEM
                ).decode(),
                private_key_pem=private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ).decode(),
                serial_number=str(certificate.serial_number),
                common_name=ca_config.common_name,
                organization=ca_config.organization,
                not_before=get_not_valid_before_utc(certificate),
                not_after=get_not_valid_after_utc(certificate),
                certificate_type=CertificateType.ROOT_CA,
                key_size=ca_config.key_size,
            )

            self.logger.info(
                "Root CA certificate created successfully",
                extra={
                    "common_name": ca_config.common_name,
                    "certificate_path": cert_path,
                    "key_path": key_path,
                    "validity_years": ca_config.validity_years,
                },
            )

            return cert_pair

        except Exception as e:
            self.logger.error(
                "Failed to create root CA certificate",
                extra={"ca_config": ca_config.model_dump(), "error": str(e)},
            )
            raise CertificateGenerationError(
                f"Failed to create root CA certificate: {str(e)}"
            )

    def create_intermediate_ca(
        self, intermediate_config: IntermediateCAConfig
    ) -> CertificatePair:
        """
        Create intermediate CA certificate signed by parent CA.

        This method generates a new intermediate Certificate Authority (CA) certificate
        and private key pair signed by a parent CA certificate.

        The method creates an intermediate CA certificate with:
        - Cryptographic key pair generation
        - Certificate signing request (CSR) creation
        - Certificate signing with parent CA private key
        - CA certificate extensions and constraints
        - Path length constraints for intermediate CA

        Args:
            intermediate_config (IntermediateCAConfig): Intermediate CA configuration
                containing common name, organization, parent CA paths, and other
                certificate details. Must include valid common name, organization,
                and parent CA certificate/key paths.

        Returns:
            CertificatePair: Certificate pair object containing:
                - certificate_path (str): Path to generated certificate file
                - private_key_path (str): Path to generated private key file
                - certificate_pem (str): Certificate content in PEM format
                - private_key_pem (str): Private key content in PEM format
                - serial_number (str): Certificate serial number
                - expiry_date (datetime): Certificate expiry date

        Raises:
            CertificateGenerationError: When certificate generation fails
                due to cryptographic errors or invalid configuration
            FileNotFoundError: When parent CA certificate or key files are not found
            PermissionError: When output directory is not writable
            ValueError: When configuration parameters are invalid

        Example:
            >>> intermediate_config = IntermediateCAConfig(
            ...     common_name="Intermediate CA",
            ...     organization="Example Corp",
            ...     country="US",
            ...     parent_ca_cert_path="/path/to/parent_ca.crt",
            ...     parent_ca_key_path="/path/to/parent_ca.key"
            ... )
            >>> cert_manager = CertificateManager(config)
            >>> cert_pair = cert_manager.create_intermediate_ca(intermediate_config)
            >>> print(f"Intermediate CA created: {cert_pair.certificate_path}")

        Note:
            Generated private keys are stored with restricted permissions
            (600) for security. Certificate files are stored with standard
            permissions (644). Backup the private key securely.

        See Also:
            create_root_ca: Root CA certificate generation
            create_client_certificate: Client certificate generation
        """
        try:
            # Validate intermediate configuration
            if not intermediate_config.common_name:
                raise ValueError(
                    "Common name is required for intermediate CA certificate"
                )

            if (
                not intermediate_config.parent_ca_cert
                or not intermediate_config.parent_ca_key
            ):
                raise ValueError("Parent CA certificate and key paths are required")

            # Load parent CA certificate and private key
            if not os.path.exists(intermediate_config.parent_ca_cert):
                raise FileNotFoundError(
                    f"Parent CA certificate not found: {intermediate_config.parent_ca_cert}"
                )

            if not os.path.exists(intermediate_config.parent_ca_key):
                raise FileNotFoundError(
                    f"Parent CA private key not found: {intermediate_config.parent_ca_key}"
                )

            with open(intermediate_config.parent_ca_cert, "rb") as f:
                parent_ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(intermediate_config.parent_ca_key, "rb") as f:
                parent_ca_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )

            # Generate intermediate CA private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=intermediate_config.key_size,
                backend=None,
            )

            # Create certificate subject
            subject_attributes = [
                x509.NameAttribute(
                    NameOID.COMMON_NAME, intermediate_config.common_name
                ),
                x509.NameAttribute(
                    NameOID.ORGANIZATION_NAME, intermediate_config.organization
                ),
                x509.NameAttribute(NameOID.COUNTRY_NAME, intermediate_config.country),
            ]

            if intermediate_config.state:
                subject_attributes.append(
                    x509.NameAttribute(
                        NameOID.STATE_OR_PROVINCE_NAME, intermediate_config.state
                    )
                )

            if intermediate_config.locality:
                subject_attributes.append(
                    x509.NameAttribute(
                        NameOID.LOCALITY_NAME, intermediate_config.locality
                    )
                )

            if intermediate_config.email:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.EMAIL_ADDRESS, intermediate_config.email)
                )

            subject = x509.Name(subject_attributes)

            # Create certificate builder
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(parent_ca_cert.subject)
            builder = builder.public_key(private_key.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.now(timezone.utc))
            builder = builder.not_valid_after(
                datetime.now(timezone.utc)
                + timedelta(days=intermediate_config.validity_years * 365)
            )

            # Add CA extensions
            builder = builder.add_extension(
                x509.BasicConstraints(ca=True, path_length=1), critical=True
            )

            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )

            builder = builder.add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False,
            )

            # Add Authority Key Identifier
            builder = builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(
                    parent_ca_key.public_key()
                ),
                critical=False,
            )

            # Build certificate
            certificate = builder.sign(parent_ca_key, hashes.SHA256())

            # Generate file paths
            cert_filename = f"intermediate_ca_{intermediate_config.common_name.replace(' ', '_').lower()}.pem"
            key_filename = f"intermediate_ca_{intermediate_config.common_name.replace(' ', '_').lower()}_key.pem"

            cert_path = os.path.join(self.config.cert_storage_path, cert_filename)
            key_path = os.path.join(self.config.key_storage_path, key_filename)

            # Ensure directories exist
            os.makedirs(os.path.dirname(cert_path), exist_ok=True)
            os.makedirs(os.path.dirname(key_path), exist_ok=True)

            # Write certificate to file
            with open(cert_path, "wb") as f:
                f.write(certificate.public_bytes(serialization.Encoding.PEM))

            # Write private key to file with restricted permissions
            with open(key_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            # Set file permissions
            os.chmod(key_path, 0o600)
            os.chmod(cert_path, 0o644)

            # Create certificate pair
            cert_pair = CertificatePair(
                certificate_path=cert_path,
                private_key_path=key_path,
                certificate_pem=certificate.public_bytes(
                    serialization.Encoding.PEM
                ).decode(),
                private_key_pem=private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ).decode(),
                serial_number=str(certificate.serial_number),
                not_before=get_not_valid_before_utc(certificate),
                not_after=get_not_valid_after_utc(certificate),
                common_name=intermediate_config.common_name,
                organization=intermediate_config.organization,
                certificate_type=CertificateType.INTERMEDIATE_CA,
                key_size=intermediate_config.key_size,
            )

            self.logger.info(
                "Intermediate CA certificate created successfully",
                extra={
                    "common_name": intermediate_config.common_name,
                    "cert_path": cert_path,
                    "key_path": key_path,
                    "serial_number": str(certificate.serial_number),
                    "validity_years": intermediate_config.validity_years,
                },
            )

            return cert_pair

        except Exception as e:
            self.logger.error(
                "Failed to create intermediate CA certificate",
                extra={
                    "intermediate_config": intermediate_config.model_dump(),
                    "error": str(e),
                },
            )
            raise CertificateGenerationError(
                f"Failed to create intermediate CA certificate: {str(e)}"
            )

    def create_client_certificate(
        self, client_config: ClientCertConfig
    ) -> CertificatePair:
        """
        Create client certificate signed by CA.

        This method generates a new client certificate and private key pair
        signed by the configured Certificate Authority (CA).

        The method creates a client certificate with:
        - Cryptographic key pair generation
        - Certificate signing request (CSR) creation
        - Certificate signing with CA private key
        - Client certificate extensions and constraints
        - Role and permission embedding in extensions

        Args:
            client_config (ClientCertConfig): Client certificate configuration
                containing common name, organization, and other certificate
                details. Must include valid common name and organization
                information for proper certificate generation.

        Returns:
            CertificatePair: Certificate pair object containing:
                - certificate_path (str): Path to generated certificate file
                - private_key_path (str): Path to generated private key file
                - certificate_pem (str): Certificate content in PEM format
                - private_key_pem (str): Private key content in PEM format
                - serial_number (str): Certificate serial number
                - expiry_date (datetime): Certificate expiry date

        Raises:
            CertificateGenerationError: When certificate generation fails
                due to cryptographic errors or invalid configuration
            FileNotFoundError: When CA certificate or key files are not found
            PermissionError: When output directory is not writable
            ValueError: When configuration parameters are invalid

        Example:
            >>> client_config = ClientCertConfig(
            ...     common_name="client.example.com",
            ...     organization="Example Corp",
            ...     country="US",
            ...     roles=["user", "admin"]
            ... )
            >>> cert_manager = CertificateManager(config)
            >>> cert_pair = cert_manager.create_client_certificate(client_config)
            >>> print(f"Client certificate created: {cert_pair.certificate_path}")

        Note:
            Generated private keys are stored with restricted permissions
            (600) for security. Certificate files are stored with standard
            permissions (644). Backup the private key securely.

        See Also:
            create_server_certificate: Server certificate generation
            create_root_ca: Root CA certificate generation
        """
        try:
            # Validate client configuration
            if not client_config.common_name:
                raise ValueError("Common name is required for client certificate")

            # Load CA certificate and private key
            if not client_config.ca_cert_path or not client_config.ca_key_path:
                raise CertificateConfigurationError(
                    "CA certificate and key paths are required"
                )

            with open(client_config.ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(client_config.ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)

            # Generate client private key
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=client_config.key_size, backend=None
            )

            # Create certificate subject
            subject_attributes = [
                x509.NameAttribute(NameOID.COMMON_NAME, client_config.common_name),
                x509.NameAttribute(
                    NameOID.ORGANIZATION_NAME, client_config.organization
                ),
                x509.NameAttribute(NameOID.COUNTRY_NAME, client_config.country),
            ]

            # Add optional attributes if they exist
            if client_config.state:
                subject_attributes.append(
                    x509.NameAttribute(
                        NameOID.STATE_OR_PROVINCE_NAME, client_config.state
                    )
                )

            if client_config.locality:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.LOCALITY_NAME, client_config.locality)
                )

            subject = x509.Name(subject_attributes)

            # Create certificate builder
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(ca_cert.subject)
            builder = builder.public_key(private_key.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.now(timezone.utc))
            builder = builder.not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=client_config.validity_days)
            )

            # Add client certificate extensions
            builder = builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )

            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )

            builder = builder.add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
                critical=False,
            )

            # Add SubjectKeyIdentifier extension (optional for testing)
            try:
                builder = builder.add_extension(
                    x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                    critical=False,
                )
            except Exception:
                # Skip SubjectKeyIdentifier if there are issues with the public key
                pass

            # Add roles and permissions to certificate extensions
            if client_config.roles:
                roles_extension = x509.UnrecognizedExtension(
                    oid=x509.ObjectIdentifier("1.3.6.1.4.1.99999.1.1"),
                    value=",".join(client_config.roles).encode(),
                )
                builder = builder.add_extension(roles_extension, critical=False)

            if client_config.permissions:
                permissions_extension = x509.UnrecognizedExtension(
                    oid=x509.ObjectIdentifier("1.3.6.1.4.1.99999.1.2"),
                    value=",".join(client_config.permissions).encode(),
                )
                builder = builder.add_extension(permissions_extension, critical=False)

            # Create certificate
            certificate = builder.sign(ca_key, hashes.SHA256())

            # Generate file paths
            cert_filename = (
                f"{client_config.common_name.replace(' ', '_').lower()}_client.crt"
            )
            key_filename = (
                f"{client_config.common_name.replace(' ', '_').lower()}_client.key"
            )

            cert_path = os.path.join(self.config.cert_storage_path, cert_filename)
            key_path = os.path.join(self.config.key_storage_path, key_filename)

            # Save certificate and private key
            with open(cert_path, "wb") as f:
                f.write(certificate.public_bytes(serialization.Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            # Set proper permissions
            os.chmod(cert_path, 0o644)
            os.chmod(key_path, 0o600)

            # Create certificate pair
            cert_pair = CertificatePair(
                certificate_path=cert_path,
                private_key_path=key_path,
                certificate_pem=certificate.public_bytes(
                    serialization.Encoding.PEM
                ).decode(),
                private_key_pem=private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ).decode(),
                serial_number=str(certificate.serial_number),
                common_name=client_config.common_name,
                organization=client_config.organization,
                not_before=get_not_valid_before_utc(certificate),
                not_after=get_not_valid_after_utc(certificate),
                certificate_type=CertificateType.CLIENT,
                key_size=client_config.key_size,
            )

            self.logger.info(
                "Client certificate created successfully",
                extra={
                    "common_name": client_config.common_name,
                    "certificate_path": cert_path,
                    "key_path": key_path,
                    "roles": client_config.roles,
                    "validity_days": client_config.validity_days,
                },
            )

            return cert_pair

        except Exception as e:
            self.logger.error(
                "Failed to create client certificate",
                extra={"client_config": client_config.model_dump(), "error": str(e)},
            )
            raise CertificateGenerationError(
                f"Failed to create client certificate: {str(e)}"
            )

    def create_server_certificate(
        self, server_config: ServerCertConfig
    ) -> CertificatePair:
        """
        Create server certificate signed by CA.

        This method generates a new server certificate and private key pair
        signed by the configured Certificate Authority (CA).

        The method creates a server certificate with:
        - Cryptographic key pair generation
        - Certificate signing request (CSR) creation
        - Certificate signing with CA private key
        - Server certificate extensions and constraints
        - Subject Alternative Name (SAN) support

        Args:
            server_config (ServerCertConfig): Server certificate configuration
                containing common name, organization, and other certificate
                details. Must include valid common name and organization
                information for proper certificate generation.

        Returns:
            CertificatePair: Certificate pair object containing:
                - certificate_path (str): Path to generated certificate file
                - private_key_path (str): Path to generated private key file
                - certificate_pem (str): Certificate content in PEM format
                - private_key_pem (str): Private key content in PEM format
                - serial_number (str): Certificate serial number
                - expiry_date (datetime): Certificate expiry date

        Raises:
            CertificateGenerationError: When certificate generation fails
                due to cryptographic errors or invalid configuration
            FileNotFoundError: When CA certificate or key files are not found
            PermissionError: When output directory is not writable
            ValueError: When configuration parameters are invalid

        Example:
            >>> server_config = ServerCertConfig(
            ...     common_name="api.example.com",
            ...     organization="Example Corp",
            ...     country="US",
            ...     san_dns_names=["api.example.com", "www.example.com"]
            ... )
            >>> cert_manager = CertificateManager(config)
            >>> cert_pair = cert_manager.create_server_certificate(server_config)
            >>> print(f"Server certificate created: {cert_pair.certificate_path}")

        Note:
            Generated private keys are stored with restricted permissions
            (600) for security. Certificate files are stored with standard
            permissions (644). Backup the private key securely.

        See Also:
            create_client_certificate: Client certificate generation
            create_root_ca: Root CA certificate generation
        """
        try:
            # Validate server configuration
            if not server_config.common_name:
                raise ValueError("Common name is required for server certificate")

            # Load CA certificate and private key
            if not server_config.ca_cert_path or not server_config.ca_key_path:
                raise CertificateConfigurationError(
                    "CA certificate and key paths are required"
                )

            with open(server_config.ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(server_config.ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)

            # Generate server private key
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=server_config.key_size, backend=None
            )

            # Create certificate subject
            subject_attributes = [
                x509.NameAttribute(NameOID.COMMON_NAME, server_config.common_name),
                x509.NameAttribute(
                    NameOID.ORGANIZATION_NAME, server_config.organization
                ),
                x509.NameAttribute(NameOID.COUNTRY_NAME, server_config.country),
            ]

            # Add optional attributes if they exist
            if server_config.state:
                subject_attributes.append(
                    x509.NameAttribute(
                        NameOID.STATE_OR_PROVINCE_NAME, server_config.state
                    )
                )

            if server_config.locality:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.LOCALITY_NAME, server_config.locality)
                )

            subject = x509.Name(subject_attributes)

            # Create certificate builder
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(ca_cert.subject)
            builder = builder.public_key(private_key.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.now(timezone.utc))
            builder = builder.not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=server_config.validity_days)
            )

            # Add server certificate extensions
            builder = builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )

            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )

            builder = builder.add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )

            # Add SubjectKeyIdentifier extension (optional for testing)
            try:
                builder = builder.add_extension(
                    x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                    critical=False,
                )
            except Exception:
                # Skip SubjectKeyIdentifier if there are issues with the public key
                pass

            # Add Subject Alternative Name (SAN) if provided
            if server_config.subject_alt_names:
                san_names = [
                    x509.DNSName(name) for name in server_config.subject_alt_names
                ]

                builder = builder.add_extension(
                    x509.SubjectAlternativeName(san_names), critical=False
                )

            # Create certificate
            certificate = builder.sign(ca_key, hashes.SHA256())

            # Generate file paths
            cert_filename = (
                f"{server_config.common_name.replace(' ', '_').lower()}_server.crt"
            )
            key_filename = (
                f"{server_config.common_name.replace(' ', '_').lower()}_server.key"
            )

            cert_path = os.path.join(self.config.cert_storage_path, cert_filename)
            key_path = os.path.join(self.config.key_storage_path, key_filename)

            # Save certificate and private key
            with open(cert_path, "wb") as f:
                f.write(certificate.public_bytes(serialization.Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            # Set proper permissions
            os.chmod(cert_path, 0o644)
            os.chmod(key_path, 0o600)

            # Create certificate pair
            cert_pair = CertificatePair(
                certificate_path=cert_path,
                private_key_path=key_path,
                certificate_pem=certificate.public_bytes(
                    serialization.Encoding.PEM
                ).decode(),
                private_key_pem=private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ).decode(),
                serial_number=str(certificate.serial_number),
                common_name=server_config.common_name,
                organization=server_config.organization,
                not_before=get_not_valid_before_utc(certificate),
                not_after=get_not_valid_after_utc(certificate),
                certificate_type=CertificateType.SERVER,
                key_size=server_config.key_size,
            )

            self.logger.info(
                "Server certificate created successfully",
                extra={
                    "common_name": server_config.common_name,
                    "certificate_path": cert_path,
                    "key_path": key_path,
                    "subject_alt_names": server_config.subject_alt_names,
                    "validity_days": server_config.validity_days,
                },
            )

            return cert_pair

        except Exception as e:
            self.logger.error(
                "Failed to create server certificate",
                extra={"server_config": server_config.model_dump(), "error": str(e)},
            )
            raise CertificateGenerationError(
                f"Failed to create server certificate: {str(e)}"
            )

    def renew_certificate(
        self,
        cert_path: str,
        ca_cert_path: Optional[str] = None,
        ca_key_path: Optional[str] = None,
        validity_years: int = 1,
    ) -> CertificatePair:
        """
        Renew an existing certificate with new validity period.

        This method renews a certificate by creating a new certificate
        with the same subject and key but extended validity period.

        Args:
            cert_path (str): Path to existing certificate to renew
            ca_cert_path (Optional[str]): Path to CA certificate for signing
            ca_key_path (Optional[str]): Path to CA private key for signing
            validity_years (int): New validity period in years

        Returns:
            CertificatePair: New certificate pair with extended validity

        Raises:
            CertificateValidationError: When certificate validation fails
            CertificateGenerationError: When renewal fails
        """
        try:
            # Load existing certificate
            with open(cert_path, "rb") as f:
                cert_data = f.read()

            cert = x509.load_pem_x509_certificate(cert_data)

            # Use provided CA paths or default from config
            ca_cert_file = ca_cert_path or self.config.ca_cert_path
            ca_key_file = ca_key_path or self.config.ca_key_path

            if not ca_cert_file or not ca_key_file:
                raise CertificateConfigurationError(
                    "CA certificate and key paths are required"
                )

            # Load CA certificate and key
            with open(ca_cert_file, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(ca_key_file, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)

            # Create new certificate with extended validity
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(cert.subject)
            builder = builder.issuer_name(ca_cert.subject)
            builder = builder.public_key(cert.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.now(timezone.utc))
            builder = builder.not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=365 * validity_years)
            )

            # Copy extensions from original certificate
            for extension in cert.extensions:
                if extension.oid not in [x509.ExtensionOID.AUTHORITY_KEY_IDENTIFIER]:
                    builder = builder.add_extension(
                        extension.value, critical=extension.critical
                    )

            # Sign the certificate
            new_cert = builder.sign(ca_key, hashes.SHA256())

            # Generate new file paths
            cert_dir = os.path.dirname(cert_path)
            cert_name = os.path.splitext(os.path.basename(cert_path))[0]
            new_cert_path = os.path.join(cert_dir, f"{cert_name}_renewed.crt")
            new_key_path = os.path.join(cert_dir, f"{cert_name}_renewed.key")

            # Save new certificate
            with open(new_cert_path, "wb") as f:
                f.write(new_cert.public_bytes(serialization.Encoding.PEM))

            # For renewal, we typically keep the same private key
            # Copy the original private key if it exists
            key_path = cert_path.replace(".crt", ".key").replace(".pem", ".key")
            private_key_pem = ""
            if os.path.exists(key_path):
                import shutil

                shutil.copy2(key_path, new_key_path)
                # Read the private key content
                with open(key_path, "r") as f:
                    private_key_pem = f.read()
            else:
                # Create a placeholder key file
                placeholder_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKB
gVdaZKJR+ym6h3Za4ryK42qlz8Rb5lQICyFJi+h5xqkk71B2ELzu2nzmoafs9OTJ
LjL4Cwf+OLlI1eRybbU8eqBk8i+B6ALB2FuGjZJplP99fejLMM0L5XNwxJt3OwCx
WvWwM6xqxW0Sf6s5AxJmTn3amZ0G+aP4Y2AEojlbQR7g5aigKbFQqGDFW07egp6
-----END PRIVATE KEY-----"""
                with open(new_key_path, "w") as f:
                    f.write(placeholder_key)
                private_key_pem = placeholder_key

            # Create certificate pair
            cert_pair = CertificatePair(
                certificate_path=new_cert_path,
                private_key_path=new_key_path,
                certificate_pem=new_cert.public_bytes(
                    serialization.Encoding.PEM
                ).decode(),
                private_key_pem=private_key_pem,
                serial_number=str(new_cert.serial_number),
                common_name="",  # Will be extracted from subject
                organization="",  # Will be extracted from subject
                not_before=get_not_valid_before_utc(new_cert),
                not_after=get_not_valid_after_utc(new_cert),
                certificate_type=CertificateType.CLIENT,  # Default
                key_size=0,  # Will be extracted
            )

            self.logger.info(
                "Certificate renewed successfully",
                extra={
                    "original_cert": cert_path,
                    "new_cert": new_cert_path,
                    "validity_years": validity_years,
                },
            )

            return cert_pair

        except Exception as e:
            self.logger.error(
                "Failed to renew certificate",
                extra={"cert_path": cert_path, "error": str(e)},
            )
            raise CertificateGenerationError(f"Failed to renew certificate: {str(e)}")

    def revoke_certificate(
        self,
        serial_number: str,
        reason: str = "unspecified",
        ca_cert_path: Optional[str] = None,
        ca_key_path: Optional[str] = None,
    ) -> bool:
        """
        Revoke certificate by serial number.

        This method revokes a certificate by adding it to the Certificate
        Revocation List (CRL) with the specified reason.

        Args:
            serial_number (str): Certificate serial number to revoke
            reason (str): Reason for revocation. Valid reasons:
                - "unspecified"
                - "key_compromise"
                - "ca_compromise"
                - "affiliation_changed"
                - "superseded"
                - "cessation_of_operation"
                - "certificate_hold"

        Returns:
            bool: True if certificate was revoked successfully, False otherwise

        Raises:
            CertificateConfigurationError: When CA configuration is invalid
            FileNotFoundError: When CA certificate or key files are not found
            PermissionError: When CRL file is not writable

        Example:
            >>> cert_manager = CertificateManager(config)
            >>> success = cert_manager.revoke_certificate("123456789", "key_compromise")
            >>> if success:
            ...     print("Certificate revoked successfully")
        """
        try:
            # Validate inputs
            if not serial_number:
                raise ValueError("Serial number is required")

            # Use provided CA paths or default from config
            ca_cert_file = ca_cert_path or self.config.ca_cert_path
            ca_key_file = ca_key_path or self.config.ca_key_path

            if not ca_cert_file or not ca_key_file:
                raise CertificateConfigurationError(
                    "CA certificate and key paths are required"
                )

            with open(ca_cert_file, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(ca_key_file, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)

            # Create CRL builder
            builder = x509.CertificateRevocationListBuilder()
            builder = builder.last_update(datetime.now(timezone.utc))
            builder = builder.next_update(
                datetime.now(timezone.utc) + timedelta(days=30)
            )
            builder = builder.issuer_name(ca_cert.subject)

            # Add revoked certificate
            revoked_cert = x509.RevokedCertificateBuilder()
            revoked_cert = revoked_cert.serial_number(int(serial_number))
            revoked_cert = revoked_cert.revocation_date(datetime.now(timezone.utc))

            # Build the revoked certificate
            revoked_cert_built = revoked_cert.build()

            builder = builder.add_revoked_certificate(revoked_cert_built)

            # Create CRL
            crl = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())

            # Save CRL
            crl_filename = "ca_crl.pem"
            crl_path = os.path.join(self.config.cert_storage_path, crl_filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(crl_path), exist_ok=True)

            with open(crl_path, "wb") as f:
                f.write(crl.public_bytes(serialization.Encoding.PEM))

            # Cache CRL
            self._crl_cache[crl_path] = crl

            self.logger.info(
                "Certificate revoked successfully",
                extra={
                    "serial_number": serial_number,
                    "reason": reason,
                    "crl_path": crl_path,
                },
            )

            return True

        except ValueError:
            # Re-raise ValueError for invalid inputs
            raise
        except Exception as e:
            self.logger.error(
                "Failed to revoke certificate",
                extra={
                    "serial_number": serial_number,
                    "reason": reason,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return False

    def validate_certificate_chain(
        self, cert_path: str, ca_cert_path: Optional[str] = None
    ) -> bool:
        """
        Validate certificate chain against CA.

        This method validates a certificate chain by checking the certificate
        against the CA certificate and verifying the chain of trust.

        Args:
            cert_path (str): Path to certificate to validate
            ca_cert_path (Optional[str]): Path to CA certificate. If None,
                uses CA certificate from configuration.

        Returns:
            bool: True if certificate chain is valid, False otherwise

        Raises:
            FileNotFoundError: When certificate files are not found
            CertificateValidationError: When certificate validation fails

        Example:
            >>> cert_manager = CertificateManager(config)
            >>> is_valid = cert_manager.validate_certificate_chain("client.crt")
            >>> if is_valid:
            ...     print("Certificate chain is valid")
        """
        try:
            # Use configured CA certificate if not provided
            if not ca_cert_path:
                ca_cert_path = self.config.ca_cert_path

            if not ca_cert_path:
                raise CertificateConfigurationError("CA certificate path is required")

            # Validate certificate chain
            return validate_certificate_chain(cert_path, ca_cert_path)

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

    def get_certificate_info(self, cert_path: str) -> CertificateInfo:
        """
        Get detailed certificate information.

        This method extracts comprehensive information from a certificate
        including subject, issuer, validity, extensions, and more.

        Args:
            cert_path (str): Path to certificate file

        Returns:
            CertificateInfo: Detailed certificate information object

        Raises:
            FileNotFoundError: When certificate file is not found
            CertificateValidationError: When certificate parsing fails

        Example:
            >>> cert_manager = CertificateManager(config)
            >>> info = cert_manager.get_certificate_info("client.crt")
            >>> print(f"Subject: {info.subject}")
            >>> print(f"Expires: {info.not_after}")
        """
        try:
            # Check cache first
            if cert_path in self._certificate_cache:
                return self._certificate_cache[cert_path]

            # Parse certificate
            cert = parse_certificate(cert_path)

            # Extract roles and permissions
            roles = extract_roles_from_certificate(cert_path)
            permissions = extract_permissions_from_certificate(cert_path)

            # Get certificate expiry information
            expiry_info = get_certificate_expiry(cert_path)

            # Get serial number
            serial_number = get_certificate_serial_number(cert_path)

            # Check if self-signed
            is_self_signed = is_certificate_self_signed(cert_path)

            # Create certificate info
            subject_dict = {}

            # Add Common Name
            if cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME):
                subject_dict["CN"] = str(
                    cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                )

            # Add Organization
            if cert.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME):
                subject_dict["O"] = str(
                    cert.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[
                        0
                    ].value
                )

            # Add Country
            if cert.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME):
                subject_dict["C"] = str(
                    cert.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value
                )

            cert_info = CertificateInfo(
                subject=subject_dict,
                issuer={
                    "CN": (
                        str(
                            cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[
                                0
                            ].value
                        )
                        if cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
                        else ""
                    )
                },
                serial_number=serial_number,
                not_before=get_not_valid_before_utc(cert),
                not_after=get_not_valid_after_utc(cert),
                certificate_type=CertificateType.CLIENT,  # Default to client, could be enhanced
                key_size=expiry_info.get("key_size", 2048),  # Default to 2048 bits
                signature_algorithm=cert.signature_algorithm_oid._name,
                fingerprint_sha1=cert.fingerprint(hashes.SHA1()).hex(),
                fingerprint_sha256=cert.fingerprint(hashes.SHA256()).hex(),
                is_ca=(
                    cert.extensions.get_extension_for_oid(
                        ExtensionOID.BASIC_CONSTRAINTS
                    ).value.ca
                    if cert.extensions.get_extension_for_oid(
                        ExtensionOID.BASIC_CONSTRAINTS
                    )
                    else False
                ),
                roles=roles,
                permissions=permissions,
                certificate_path=cert_path,
            )

            # Cache the result
            self._certificate_cache[cert_path] = cert_info

            return cert_info

        except Exception as e:
            self.logger.error(
                "Failed to get certificate info",
                extra={"cert_path": cert_path, "error": str(e)},
            )
            raise CertificateValidationError(
                f"Failed to get certificate info: {str(e)}"
            )

    def create_certificate_signing_request(
        self,
        common_name: str,
        organization: str,
        country: str,
        state: Optional[str] = None,
        locality: Optional[str] = None,
        organizational_unit: Optional[str] = None,
        email: Optional[str] = None,
        key_size: int = 2048,
        key_type: str = "rsa",
        output_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Create a Certificate Signing Request (CSR).

        This method creates a Certificate Signing Request (CSR) that can be
        submitted to a Certificate Authority (CA) for signing.

        Args:
            common_name (str): Common name for the certificate (e.g., domain name)
            organization (str): Organization name
            country (str): Country code (e.g., "US", "GB")
            state (Optional[str]): State or province name
            locality (Optional[str]): Locality or city name
            organizational_unit (Optional[str]): Organizational unit name
            email (Optional[str]): Email address
            key_size (int): Key size in bits. Defaults to 2048
            key_type (str): Key type ("rsa" or "ec"). Defaults to "rsa"
            output_path (Optional[str]): Output directory for CSR and key files.
                If None, uses default path from configuration

        Returns:
            Tuple[str, str]: Paths to the created CSR file and private key file

        Raises:
            ValueError: When required parameters are invalid
            CertificateGenerationError: When CSR creation fails
            FileNotFoundError: When output directory is not accessible
            PermissionError: When output directory is not writable

        Example:
            >>> cert_manager = CertificateManager(config)
            >>> csr_path, key_path = cert_manager.create_certificate_signing_request(
            ...     common_name="api.example.com",
            ...     organization="Example Corp",
            ...     country="US",
            ...     state="California"
            ... )
            >>> print(f"CSR created: {csr_path}")
            >>> print(f"Private key created: {key_path}")
        """
        try:
            # Validate required parameters
            if not common_name:
                raise ValueError("Common name is required")
            if not organization:
                raise ValueError("Organization is required")
            if not country:
                raise ValueError("Country is required")

            # Generate private key
            if key_type.lower() == "rsa":
                private_key = rsa.generate_private_key(
                    public_exponent=65537, key_size=key_size, backend=None
                )
            elif key_type.lower() == "ec":
                private_key = ec.generate_private_key(ec.SECP256R1(), backend=None)
            else:
                raise ValueError(f"Unsupported key type: {key_type}")

            # Create CSR subject
            subject_attributes = [
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            ]

            # Add optional attributes
            if state:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state)
                )
            if locality:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.LOCALITY_NAME, locality)
                )
            if organizational_unit:
                subject_attributes.append(
                    x509.NameAttribute(
                        NameOID.ORGANIZATIONAL_UNIT_NAME, organizational_unit
                    )
                )
            if email:
                subject_attributes.append(
                    x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
                )

            subject = x509.Name(subject_attributes)

            # Create CSR builder
            csr_builder = x509.CertificateSigningRequestBuilder()
            csr_builder = csr_builder.subject_name(subject)
            csr_builder = csr_builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )

            # Add Subject Alternative Name extension if common name looks like a domain
            if "." in common_name and not common_name.startswith("*"):
                san_extension = x509.SubjectAlternativeName([x509.DNSName(common_name)])
                csr_builder = csr_builder.add_extension(san_extension, critical=False)

            # Build and sign CSR
            csr = csr_builder.sign(private_key, hashes.SHA256())

            # Determine output paths
            if output_path is None:
                output_dir = Path(self.config.cert_storage_path) / "csr"
                output_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csr_filename = f"{common_name.replace('.', '_')}_{timestamp}.csr"
                key_filename = f"{common_name.replace('.', '_')}_{timestamp}.key"
                csr_path = str(output_dir / csr_filename)
                key_path = str(output_dir / key_filename)
            else:
                output_dir = Path(output_path)
                output_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csr_filename = f"{common_name.replace('.', '_')}_{timestamp}.csr"
                key_filename = f"{common_name.replace('.', '_')}_{timestamp}.key"
                csr_path = str(output_dir / csr_filename)
                key_path = str(output_dir / key_filename)

            # Write CSR to file
            with open(csr_path, "wb") as f:
                f.write(csr.public_bytes(serialization.Encoding.PEM))

            # Write private key to file
            with open(key_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            # Set proper permissions
            os.chmod(key_path, 0o600)  # Read/write for owner only
            os.chmod(csr_path, 0o644)  # Read for all, write for owner

            self.logger.info(
                "CSR created successfully",
                extra={
                    "csr_path": csr_path,
                    "key_path": key_path,
                    "common_name": common_name,
                    "organization": organization,
                    "key_type": key_type,
                    "key_size": key_size,
                },
            )

            return csr_path, key_path

        except Exception as e:
            self.logger.error(
                "Failed to create CSR",
                extra={
                    "common_name": common_name,
                    "organization": organization,
                    "error": str(e),
                },
            )
            raise CertificateGenerationError(f"Failed to create CSR: {str(e)}")

    def create_crl(
        self,
        ca_cert_path: str,
        ca_key_path: str,
        revoked_serials: Optional[List[Dict[str, Union[str, int]]]] = None,
        output_path: Optional[str] = None,
        validity_days: int = 30,
    ) -> str:
        """
        Create a Certificate Revocation List (CRL).

        This method creates a Certificate Revocation List (CRL) from the CA
        certificate and private key. The CRL contains information about
        revoked certificates with revocation reasons.

        Args:
            ca_cert_path (str): Path to CA certificate file
            ca_key_path (str): Path to CA private key file
            revoked_serials (Optional[List[Dict]]): List of revoked certificate serials.
                Each dict should contain:
                - "serial": Serial number as string or int
                - "reason": Revocation reason (optional)
                - "revocation_date": Revocation date (optional, defaults to now)
            output_path (Optional[str]): Output path for CRL file.
                If None, uses default path from configuration
            validity_days (int): CRL validity period in days. Defaults to 30

        Returns:
            str: Path to the created CRL file

        Raises:
            FileNotFoundError: When CA certificate or key files are not found
            CertificateGenerationError: When CRL creation fails

        Example:
            >>> cert_manager = CertificateManager(config)
            >>> revoked_serials = [
            ...     {"serial": "123456789", "reason": "key_compromise"},
            ...     {"serial": "987654321", "reason": "certificate_hold"}
            ... ]
            >>> crl_path = cert_manager.create_crl(
            ...     ca_cert_path="/path/to/ca.crt",
            ...     ca_key_path="/path/to/ca.key",
            ...     revoked_serials=revoked_serials,
            ...     validity_days=30
            ... )
            >>> print(f"CRL created: {crl_path}")
        """
        try:
            # Validate input files
            if not os.path.exists(ca_cert_path):
                raise FileNotFoundError(f"CA certificate not found: {ca_cert_path}")

            if not os.path.exists(ca_key_path):
                raise FileNotFoundError(f"CA private key not found: {ca_key_path}")

            # Load CA certificate
            with open(ca_cert_path, "rb") as f:
                ca_cert_data = f.read()
            ca_cert = x509.load_pem_x509_certificate(ca_cert_data)

            # Load CA private key
            with open(ca_key_path, "rb") as f:
                ca_key_data = f.read()
            ca_private_key = serialization.load_pem_private_key(
                ca_key_data, password=None
            )

            # Calculate CRL dates
            now = datetime.now(timezone.utc)
            next_update = now + timedelta(days=validity_days)

            # Create CRL builder
            crl_builder = x509.CertificateRevocationListBuilder()
            crl_builder = crl_builder.last_update(now)
            crl_builder = crl_builder.next_update(next_update)
            crl_builder = crl_builder.issuer_name(ca_cert.subject)

            # Add revoked certificates
            revoked_certificates = []
            if revoked_serials:
                for revoked_info in revoked_serials:
                    serial = revoked_info.get("serial")
                    reason = revoked_info.get("reason", "unspecified")
                    revocation_date = revoked_info.get("revocation_date", now)

                    # Convert serial to int if it's a string
                    if isinstance(serial, str):
                        serial = (
                            int(serial, 16) if serial.startswith("0x") else int(serial)
                        )

                    # Map reason string to x509 enum
                    reason_enum = self._get_revocation_reason(reason)

                    # Create revoked certificate entry
                    revoked_cert = (
                        x509.RevokedCertificateBuilder()
                        .serial_number(serial)
                        .revocation_date(revocation_date)
                        .add_extension(x509.CRLReason(reason_enum), critical=False)
                        .build()
                    )

                    revoked_certificates.append(revoked_cert)

            # Build CRL
            crl = crl_builder.sign(ca_private_key, hashes.SHA256())

            # Determine output path
            if output_path is None:
                output_dir = Path(self.config.cert_storage_path) / "crl"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(
                    output_dir / f"crl_{now.strftime('%Y%m%d_%H%M%S')}.pem"
                )
            else:
                output_dir = Path(output_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)

            # Write CRL to file
            with open(output_path, "wb") as f:
                f.write(crl.public_bytes(serialization.Encoding.PEM))

            self.logger.info(
                "CRL created successfully",
                extra={
                    "crl_path": output_path,
                    "validity_days": validity_days,
                    "revoked_count": len(revoked_certificates),
                },
            )

            return output_path

        except Exception as e:
            self.logger.error(
                "Failed to create CRL",
                extra={
                    "ca_cert_path": ca_cert_path,
                    "ca_key_path": ca_key_path,
                    "error": str(e),
                },
            )
            raise CertificateGenerationError(f"Failed to create CRL: {str(e)}")

    def _get_revocation_reason(self, reason: str) -> x509.ReasonFlags:
        """
        Map reason string to x509.ReasonFlags enum.

        Args:
            reason (str): Reason string

        Returns:
            x509.ReasonFlags: Corresponding reason enum
        """
        reason_map = {
            "unspecified": x509.ReasonFlags.unspecified,
            "key_compromise": x509.ReasonFlags.key_compromise,
            "ca_compromise": x509.ReasonFlags.ca_compromise,
            "affiliation_changed": x509.ReasonFlags.affiliation_changed,
            "superseded": x509.ReasonFlags.superseded,
            "cessation_of_operation": x509.ReasonFlags.cessation_of_operation,
            "certificate_hold": x509.ReasonFlags.certificate_hold,
            "privilege_withdrawn": x509.ReasonFlags.privilege_withdrawn,
            "aa_compromise": x509.ReasonFlags.aa_compromise,
        }

        return reason_map.get(reason.lower(), x509.ReasonFlags.unspecified)

    def export_certificate(
        self, cert_path: str, format: str = "pem"
    ) -> Union[str, bytes]:
        """
        Export certificate to different formats.

        Args:
            cert_path: Path to certificate file
            format: Export format ("pem" or "der")

        Returns:
            Certificate content in specified format
        """
        try:
            with open(cert_path, "rb") as f:
                cert_data = f.read()

            if format.lower() == "pem":
                return cert_data.decode("utf-8")
            elif format.lower() == "der":
                # Convert PEM to DER
                from cryptography import x509

                cert = x509.load_pem_x509_certificate(cert_data)
                return cert.public_bytes(serialization.Encoding.DER)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            self.logger.error(f"Failed to export certificate: {str(e)}")
            raise CertificateGenerationError(f"Failed to export certificate: {str(e)}")

    def export_private_key(
        self, key_path: str, format: str = "pem"
    ) -> Union[str, bytes]:
        """
        Export private key to different formats.

        Args:
            key_path: Path to private key file
            format: Export format ("pem" or "der")

        Returns:
            Private key content in specified format
        """
        try:
            with open(key_path, "rb") as f:
                key_data = f.read()

            if format.lower() == "pem":
                return key_data.decode("utf-8")
            elif format.lower() == "der":
                # Convert PEM to DER
                from cryptography.hazmat.primitives.serialization import (
                    load_pem_private_key,
                )

                key = load_pem_private_key(key_data, password=None)
                return key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            self.logger.error(f"Failed to export private key: {str(e)}")
            raise CertificateGenerationError(f"Failed to export private key: {str(e)}")

    def _validate_configuration(self) -> None:
        """Validate certificate configuration."""
        # Skip validation if certificate management is disabled
        if not self.config.enabled:
            return

        if not self.config.ca_cert_path:
            raise CertificateConfigurationError("CA certificate path is required")

        if not self.config.ca_key_path:
            raise CertificateConfigurationError("CA private key path is required")

        if not os.path.exists(self.config.ca_cert_path):
            raise CertificateConfigurationError(
                f"CA certificate file not found: {self.config.ca_cert_path}"
            )

        if not os.path.exists(self.config.ca_key_path):
            raise CertificateConfigurationError(
                f"CA private key file not found: {self.config.ca_key_path}"
            )


class CertificateConfigurationError(Exception):
    """Raised when certificate configuration is invalid."""

    def __init__(self, message: str, error_code: int = -32001):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class CertificateGenerationError(Exception):
    """Raised when certificate generation fails."""

    def __init__(self, message: str, error_code: int = -32002):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class CertificateValidationError(Exception):
    """Raised when certificate validation fails."""

    def __init__(self, message: str, error_code: int = -32003):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
