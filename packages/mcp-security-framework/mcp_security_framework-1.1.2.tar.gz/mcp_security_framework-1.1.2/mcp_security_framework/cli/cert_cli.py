"""
Certificate Management CLI Module

This module provides command-line interface for certificate management
operations including creation, validation, and management of certificates.

Key Features:
- Root CA certificate creation
- Server certificate generation
- Client certificate generation
- Certificate validation and verification
- Certificate information display
- Certificate revocation

Commands:
    create-ca: Create root CA certificate
    create-server: Create server certificate
    create-client: Create client certificate
    validate: Validate certificate
    info: Display certificate information
    revoke: Revoke certificate

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import os
from pathlib import Path
from typing import Optional

import click

from ..core.cert_manager import CertificateManager
from ..schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    IntermediateCAConfig,
    ServerCertConfig,
)
from ..schemas.models import CertificateType


@click.group()
@click.option(
    "--config", "-c", "config_path", help="Path to certificate configuration file"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cert_cli(ctx, config_path: Optional[str], verbose: bool):
    """
    Certificate Management CLI

    Manage certificates including creation, validation, and management.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # Load configuration
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = json.load(f)
        ctx.obj["config"] = CertificateConfig(**config_data)
    else:
        # Use default configuration
        ctx.obj["config"] = CertificateConfig(
            cert_storage_path="./certs",
            key_storage_path="./keys",
            ca_cert_path="./certs/ca_cert.pem",
            ca_key_path="./keys/ca_key.pem",
        )

    # Create certificate manager
    ctx.obj["cert_manager"] = CertificateManager(ctx.obj["config"])


@cert_cli.command()
@click.option(
    "--common-name", "-cn", required=True, help="Common name for the CA certificate"
)
@click.option("--organization", "-o", required=True, help="Organization name")
@click.option("--country", "-c", required=True, help="Country code (e.g., US, GB)")
@click.option("--state", "-s", help="State or province")
@click.option("--locality", "-l", help="Locality or city")
@click.option("--email", "-e", help="Email address")
@click.option(
    "--validity-years", "-y", default=10, help="Certificate validity in years"
)
@click.option("--key-size", "-k", default=2048, help="RSA key size")
@click.pass_context
def create_ca(
    ctx,
    common_name: str,
    organization: str,
    country: str,
    state: Optional[str],
    locality: Optional[str],
    email: Optional[str],
    validity_years: int,
    key_size: int,
):
    """
    Create a root CA certificate.

    This command creates a new root Certificate Authority (CA) certificate
    that can be used to sign other certificates.
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        # Create CA configuration
        ca_config = CAConfig(
            common_name=common_name,
            organization=organization,
            country=country,
            state=state,
            locality=locality,
            email=email,
            validity_years=validity_years,
            key_size=key_size,
        )

        if verbose:
            click.echo(f"Creating CA certificate with configuration:")
            click.echo(f"  Common Name: {common_name}")
            click.echo(f"  Organization: {organization}")
            click.echo(f"  Country: {country}")
            click.echo(f"  Validity: {validity_years} years")
            click.echo(f"  Key Size: {key_size} bits")

        # Create CA certificate
        cert_pair = cert_manager.create_root_ca(ca_config)

        click.echo(f"✅ CA certificate created successfully!")
        click.echo(f"  Certificate: {cert_pair.certificate_path}")
        click.echo(f"  Private Key: {cert_pair.private_key_path}")
        click.echo(f"  Serial Number: {cert_pair.serial_number}")
        click.echo(f"  Valid Until: {cert_pair.not_after}")

    except Exception as e:
        click.echo(f"❌ Failed to create CA certificate: {str(e)}", err=True)
        raise click.Abort()


@cert_cli.command()
@click.option(
    "--common-name", "-cn", required=True, help="Common name for the server certificate"
)
@click.option("--organization", "-o", required=True, help="Organization name")
@click.option("--country", "-c", required=True, help="Country code (e.g., US, GB)")
@click.option("--state", "-s", help="State or province")
@click.option("--locality", "-l", help="Locality or city")
@click.option("--email", "-e", help="Email address")
@click.option("--validity-days", "-d", default=365, help="Certificate validity in days")
@click.option("--key-size", "-k", default=2048, help="RSA key size")
@click.option(
    "--san",
    multiple=True,
    help="Subject Alternative Names (can be specified multiple times)",
)
@click.pass_context
def create_server(
    ctx,
    common_name: str,
    organization: str,
    country: str,
    state: Optional[str],
    locality: Optional[str],
    email: Optional[str],
    validity_days: int,
    key_size: int,
    san: tuple,
):
    """
    Create a server certificate.

    This command creates a new server certificate signed by the configured CA.
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        # Create server configuration
        server_config = ServerCertConfig(
            common_name=common_name,
            organization=organization,
            country=country,
            state=state,
            locality=locality,
            email=email,
            validity_days=validity_days,
            key_size=key_size,
            subject_alt_names=list(san) if san else None,
        )

        if verbose:
            click.echo(f"Creating server certificate with configuration:")
            click.echo(f"  Common Name: {common_name}")
            click.echo(f"  Organization: {organization}")
            click.echo(f"  Country: {country}")
            click.echo(f"  Validity: {validity_days} days")
            click.echo(f"  Key Size: {key_size} bits")
            if san:
                click.echo(f"  SAN: {', '.join(san)}")

        # Create server certificate
        cert_pair = cert_manager.create_server_certificate(server_config)

        click.echo(f"✅ Server certificate created successfully!")
        click.echo(f"  Certificate: {cert_pair.certificate_path}")
        click.echo(f"  Private Key: {cert_pair.private_key_path}")
        click.echo(f"  Serial Number: {cert_pair.serial_number}")
        click.echo(f"  Valid Until: {cert_pair.not_after}")

    except Exception as e:
        click.echo(f"❌ Failed to create server certificate: {str(e)}", err=True)
        raise click.Abort()


@cert_cli.command()
@click.option(
    "--common-name", "-cn", required=True, help="Common name for the client certificate"
)
@click.option("--organization", "-o", required=True, help="Organization name")
@click.option("--country", "-c", required=True, help="Country code (e.g., US, GB)")
@click.option("--state", "-s", help="State or province")
@click.option("--locality", "-l", help="Locality or city")
@click.option("--email", "-e", help="Email address")
@click.option("--validity-days", "-d", default=365, help="Certificate validity in days")
@click.option("--key-size", "-k", default=2048, help="RSA key size")
@click.option(
    "--roles",
    multiple=True,
    help="Roles to assign to the client (can be specified multiple times)",
)
@click.option(
    "--permissions",
    multiple=True,
    help="Permissions to assign to the client (can be specified multiple times)",
)
@click.pass_context
def create_client(
    ctx,
    common_name: str,
    organization: str,
    country: str,
    state: Optional[str],
    locality: Optional[str],
    email: Optional[str],
    validity_days: int,
    key_size: int,
    roles: tuple,
    permissions: tuple,
):
    """
    Create a client certificate.

    This command creates a new client certificate signed by the configured CA.
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        # Create client configuration
        client_config = ClientCertConfig(
            common_name=common_name,
            organization=organization,
            country=country,
            state=state,
            locality=locality,
            email=email,
            validity_days=validity_days,
            key_size=key_size,
            roles=list(roles) if roles else None,
            permissions=list(permissions) if permissions else None,
        )

        if verbose:
            click.echo(f"Creating client certificate with configuration:")
            click.echo(f"  Common Name: {common_name}")
            click.echo(f"  Organization: {organization}")
            click.echo(f"  Country: {country}")
            click.echo(f"  Validity: {validity_days} days")
            click.echo(f"  Key Size: {key_size} bits")
            if roles:
                click.echo(f"  Roles: {', '.join(roles)}")
            if permissions:
                click.echo(f"  Permissions: {', '.join(permissions)}")

        # Create client certificate
        cert_pair = cert_manager.create_client_certificate(client_config)

        click.echo(f"✅ Client certificate created successfully!")
        click.echo(f"  Certificate: {cert_pair.certificate_path}")
        click.echo(f"  Private Key: {cert_pair.private_key_path}")
        click.echo(f"  Serial Number: {cert_pair.serial_number}")
        click.echo(f"  Valid Until: {cert_pair.not_after}")

    except Exception as e:
        click.echo(f"❌ Failed to create client certificate: {str(e)}", err=True)
        raise click.Abort()


@cert_cli.command()
@click.argument("cert_path", type=click.Path(exists=True))
@click.option(
    "--ca-cert",
    type=click.Path(exists=True),
    help="Path to CA certificate for validation",
)
@click.pass_context
def validate(ctx, cert_path: str, ca_cert: Optional[str]):
    """
    Validate a certificate.

    This command validates a certificate and optionally checks it against a CA.
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Validating certificate: {cert_path}")
            if ca_cert:
                click.echo(f"Using CA certificate: {ca_cert}")

        # Validate certificate
        is_valid = cert_manager.validate_certificate_chain(cert_path, ca_cert)

        if is_valid:
            click.echo(f"✅ Certificate is valid!")
        else:
            click.echo(f"❌ Certificate validation failed!", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Certificate validation failed: {str(e)}", err=True)
        raise click.Abort()


@cert_cli.command()
@click.argument("cert_path", type=click.Path(exists=True))
@click.pass_context
def info(ctx, cert_path: str):
    """
    Display certificate information.

    This command displays detailed information about a certificate.
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Getting certificate information: {cert_path}")

        # Get certificate info
        cert_info = cert_manager.get_certificate_info(cert_path)

        click.echo(f"Certificate Information:")
        click.echo(f"  Subject: {cert_info.subject}")
        click.echo(f"  Issuer: {cert_info.issuer}")
        click.echo(f"  Serial Number: {cert_info.serial_number}")
        click.echo(f"  Valid From: {cert_info.not_before}")
        click.echo(f"  Valid Until: {cert_info.not_after}")
        click.echo(f"  Key Size: {cert_info.key_size} bits")
        click.echo(f"  Certificate Type: {cert_info.certificate_type}")

        if cert_info.subject_alt_names:
            click.echo(
                f"  Subject Alternative Names: {', '.join(cert_info.subject_alt_names)}"
            )

    except Exception as e:
        click.echo(f"❌ Failed to get certificate information: {str(e)}", err=True)
        raise click.Abort()


@cert_cli.command()
@click.option(
    "--common-name",
    "-cn",
    required=True,
    help="Common name for the intermediate CA certificate",
)
@click.option("--organization", "-o", required=True, help="Organization name")
@click.option("--country", "-c", required=True, help="Country code (e.g., US, GB)")
@click.option("--state", "-s", help="State or province")
@click.option("--locality", "-l", help="Locality or city")
@click.option("--email", "-e", help="Email address")
@click.option("--validity-years", "-y", default=5, help="Certificate validity in years")
@click.option("--key-size", "-k", default=2048, help="RSA key size")
@click.option(
    "--parent-ca-cert", "-p", required=True, help="Path to parent CA certificate"
)
@click.option(
    "--parent-ca-key", "-pk", required=True, help="Path to parent CA private key"
)
@click.pass_context
def create_intermediate_ca(
    ctx,
    common_name: str,
    organization: str,
    country: str,
    state: Optional[str],
    locality: Optional[str],
    email: Optional[str],
    validity_years: int,
    key_size: int,
    parent_ca_cert: str,
    parent_ca_key: str,
):
    """
    Create an intermediate CA certificate.

    This command creates a new intermediate Certificate Authority (CA) certificate
    signed by a parent CA certificate.
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        # Create intermediate CA configuration
        intermediate_config = IntermediateCAConfig(
            common_name=common_name,
            organization=organization,
            country=country,
            state=state,
            locality=locality,
            email=email,
            validity_years=validity_years,
            key_size=key_size,
            parent_ca_cert=parent_ca_cert,
            parent_ca_key=parent_ca_key,
        )

        if verbose:
            click.echo(f"Creating intermediate CA certificate with configuration:")
            click.echo(f"  Common Name: {common_name}")
            click.echo(f"  Organization: {organization}")
            click.echo(f"  Country: {country}")
            click.echo(f"  Validity: {validity_years} years")
            click.echo(f"  Key Size: {key_size} bits")
            click.echo(f"  Parent CA Cert: {parent_ca_cert}")
            click.echo(f"  Parent CA Key: {parent_ca_key}")

        # Create intermediate CA certificate
        cert_pair = cert_manager.create_intermediate_ca(intermediate_config)

        click.echo(f"✅ Intermediate CA certificate created successfully!")
        click.echo(f"  Certificate: {cert_pair.certificate_path}")
        click.echo(f"  Private Key: {cert_pair.private_key_path}")
        click.echo(f"  Serial Number: {cert_pair.serial_number}")
        click.echo(f"  Valid Until: {cert_pair.not_after}")

    except Exception as e:
        click.echo(
            f"❌ Failed to create intermediate CA certificate: {str(e)}", err=True
        )
        raise click.Abort()


@cert_cli.command()
@click.option("--ca-cert", "-c", required=True, help="Path to CA certificate")
@click.option("--ca-key", "-k", required=True, help="Path to CA private key")
@click.option("--output", "-o", help="Output path for CRL file")
@click.option("--validity-days", "-d", default=30, help="CRL validity in days")
@click.pass_context
def create_crl(
    ctx, ca_cert: str, ca_key: str, output: Optional[str], validity_days: int
):
    """
    Create a Certificate Revocation List (CRL).

    This command creates a Certificate Revocation List (CRL) from the CA
    certificate and private key.
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Creating CRL with configuration:")
            click.echo(f"  CA Certificate: {ca_cert}")
            click.echo(f"  CA Private Key: {ca_key}")
            click.echo(f"  Validity: {validity_days} days")
            if output:
                click.echo(f"  Output: {output}")

        # Create CRL
        crl_path = cert_manager.create_crl(ca_cert, ca_key, output, validity_days)

        click.echo(f"✅ CRL created successfully!")
        click.echo(f"  CRL Path: {crl_path}")
        click.echo(f"  Validity: {validity_days} days")

    except Exception as e:
        click.echo(f"❌ Failed to create CRL: {str(e)}", err=True)
        raise click.Abort()


@cert_cli.command()
@click.argument("serial_number")
@click.option("--reason", "-r", default="unspecified", help="Reason for revocation")
@click.pass_context
def revoke(ctx, serial_number: str, reason: str):
    """
    Revoke a certificate.

    This command revokes a certificate by adding it to the Certificate
    Revocation List (CRL).
    """
    try:
        config = ctx.obj["config"]
        cert_manager = ctx.obj["cert_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Revoking certificate with serial number: {serial_number}")
            click.echo(f"Reason: {reason}")

        # Revoke certificate
        success = cert_manager.revoke_certificate(serial_number, reason)

        if success:
            click.echo(f"✅ Certificate revoked successfully!")
        else:
            click.echo(f"❌ Failed to revoke certificate!", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Failed to revoke certificate: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cert_cli()
