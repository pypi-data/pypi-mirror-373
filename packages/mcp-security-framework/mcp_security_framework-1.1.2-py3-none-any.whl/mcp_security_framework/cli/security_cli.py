"""
Security Management CLI Module

This module provides command-line interface for security management
operations including authentication, authorization, and security configuration.

Key Features:
- API key management
- User authentication testing
- Permission validation
- Security configuration management
- Rate limiting management
- Security status monitoring

Commands:
    auth: Authentication operations
    permissions: Permission management
    rate-limit: Rate limiting operations
    config: Configuration management
    status: Security status monitoring

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click

from ..core.security_manager import SecurityManager
from ..schemas.config import (
    AuthConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
)
from ..schemas.models import AuthResult, AuthStatus


@click.group()
@click.option(
    "--config", "-c", "config_path", help="Path to security configuration file"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def security_cli(ctx, config_path: Optional[str], verbose: bool):
    """
    Security Management CLI

    Manage security operations including authentication, authorization,
    and security configuration.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # Load configuration
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = json.load(f)
        ctx.obj["config"] = SecurityConfig(**config_data)
    else:
        # Use default configuration
        ctx.obj["config"] = SecurityConfig(
            auth=AuthConfig(enabled=True),
            rate_limit=RateLimitConfig(enabled=True),
            ssl=SSLConfig(enabled=False),
            permissions=PermissionConfig(enabled=True),
        )

    # Create security manager
    ctx.obj["security_manager"] = SecurityManager(ctx.obj["config"])


@security_cli.group()
@click.pass_context
def auth(ctx):
    """
    Authentication operations.

    Manage authentication including API keys, user authentication,
    and authentication testing.
    """
    pass


@auth.command()
@click.option("--username", "-u", required=True, help="Username for the API key")
@click.option("--api-key", "-k", required=True, help="API key value")
@click.pass_context
def add_api_key(ctx, username: str, api_key: str):
    """
    Add an API key for a user.

    This command adds an API key to the authentication system
    for the specified user.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Adding API key for user: {username}")

        # Add API key
        success = security_manager.auth_manager.add_api_key(username, api_key)

        if success:
            click.echo(f"✅ API key added successfully for user: {username}")
        else:
            click.echo(f"❌ Failed to add API key for user: {username}", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Failed to add API key: {str(e)}", err=True)
        raise click.Abort()


@auth.command()
@click.option("--username", "-u", required=True, help="Username to remove API key for")
@click.pass_context
def remove_api_key(ctx, username: str):
    """
    Remove an API key for a user.

    This command removes an API key from the authentication system
    for the specified user.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Removing API key for user: {username}")

        # Remove API key
        success = security_manager.auth_manager.remove_api_key(username)

        if success:
            click.echo(f"✅ API key removed successfully for user: {username}")
        else:
            click.echo(f"❌ Failed to remove API key for user: {username}", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Failed to remove API key: {str(e)}", err=True)
        raise click.Abort()


@auth.command()
@click.option("--api-key", "-k", required=True, help="API key to test")
@click.pass_context
def test_api_key(ctx, api_key: str):
    """
    Test API key authentication.

    This command tests if an API key is valid and returns
    authentication information.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Testing API key authentication")

        # Test API key
        auth_result = security_manager.auth_manager.authenticate_api_key(api_key)

        if auth_result.is_valid:
            click.echo(f"✅ API key authentication successful!")
            click.echo(f"  Username: {auth_result.username}")
            click.echo(f"  Roles: {', '.join(auth_result.roles)}")
            click.echo(f"  Auth Method: {auth_result.auth_method}")
        else:
            click.echo(f"❌ API key authentication failed!", err=True)
            click.echo(f"  Error: {auth_result.error_message}")
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ API key authentication failed: {str(e)}", err=True)
        raise click.Abort()


@auth.command()
@click.option("--token", "-t", required=True, help="JWT token to test")
@click.pass_context
def test_jwt(ctx, token: str):
    """
    Test JWT token authentication.

    This command tests if a JWT token is valid and returns
    authentication information.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Testing JWT token authentication")

        # Test JWT token
        auth_result = security_manager.auth_manager.authenticate_jwt_token(token)

        if auth_result.is_valid:
            click.echo(f"✅ JWT token authentication successful!")
            click.echo(f"  Username: {auth_result.username}")
            click.echo(f"  Roles: {', '.join(auth_result.roles)}")
            click.echo(f"  Auth Method: {auth_result.auth_method}")
        else:
            click.echo(f"❌ JWT token authentication failed!", err=True)
            click.echo(f"  Error: {auth_result.error_message}")
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ JWT token authentication failed: {str(e)}", err=True)
        raise click.Abort()


@security_cli.group()
@click.pass_context
def permissions(ctx):
    """
    Permission management operations.

    Manage permissions including role assignment, permission validation,
    and permission testing.
    """
    pass


@permissions.command()
@click.option(
    "--username", "-u", required=True, help="Username to check permissions for"
)
@click.option(
    "--permissions",
    "-p",
    multiple=True,
    required=True,
    help="Permissions to check (can be specified multiple times)",
)
@click.pass_context
def check(ctx, username: str, permissions: tuple):
    """
    Check user permissions.

    This command checks if a user has the specified permissions.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]
        permissions_list = list(permissions)

        if verbose:
            click.echo(f"Checking permissions for user: {username}")
            click.echo(f"Required permissions: {', '.join(permissions_list)}")

        # Get user roles
        user_roles = security_manager.auth_manager._get_user_roles(username)

        if verbose:
            click.echo(f"User roles: {', '.join(user_roles)}")

        # Check permissions
        has_permissions = security_manager.permission_manager.validate_access(
            user_roles, permissions_list
        )

        if has_permissions.is_valid:
            click.echo(f"✅ User has all required permissions!")
            click.echo(f"  Username: {username}")
            click.echo(f"  Roles: {', '.join(user_roles)}")
            click.echo(f"  Permissions: {', '.join(permissions_list)}")
        else:
            click.echo(f"❌ User does not have required permissions!", err=True)
            click.echo(f"  Username: {username}")
            click.echo(f"  Roles: {', '.join(user_roles)}")
            click.echo(
                f"  Missing permissions: {', '.join(has_permissions.missing_permissions)}"
            )
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Permission check failed: {str(e)}", err=True)
        raise click.Abort()


@permissions.command()
@click.option("--role", "-r", required=True, help="Role name")
@click.pass_context
def list_role_permissions(ctx, role: str):
    """
    List permissions for a role.

    This command displays all permissions assigned to a specific role.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Listing permissions for role: {role}")

        # Get role permissions
        permissions = security_manager.permission_manager.get_role_permissions(role)

        if permissions:
            click.echo(f"Permissions for role '{role}':")
            for permission in permissions:
                click.echo(f"  - {permission}")
        else:
            click.echo(f"No permissions found for role: {role}")

    except Exception as e:
        click.echo(f"❌ Failed to list role permissions: {str(e)}", err=True)
        raise click.Abort()


@security_cli.group()
@click.pass_context
def rate_limit(ctx):
    """
    Rate limiting operations.

    Manage rate limiting including checking limits, resetting limits,
    and monitoring rate limit status.
    """
    pass


@rate_limit.command()
@click.option(
    "--identifier",
    "-i",
    required=True,
    help="Rate limit identifier (IP, user ID, etc.)",
)
@click.pass_context
def check(ctx, identifier: str):
    """
    Check rate limit status.

    This command checks the current rate limit status for an identifier.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Checking rate limit for identifier: {identifier}")

        # Check rate limit
        is_allowed = security_manager.rate_limiter.check_rate_limit(identifier)

        if is_allowed:
            click.echo(f"✅ Rate limit check passed for: {identifier}")
        else:
            click.echo(f"❌ Rate limit exceeded for: {identifier}", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Rate limit check failed: {str(e)}", err=True)
        raise click.Abort()


@rate_limit.command()
@click.option(
    "--identifier", "-i", required=True, help="Rate limit identifier to reset"
)
@click.pass_context
def reset(ctx, identifier: str):
    """
    Reset rate limit for an identifier.

    This command resets the rate limit counter for an identifier.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Resetting rate limit for identifier: {identifier}")

        # Reset rate limit
        security_manager.rate_limiter.reset_rate_limit(identifier)

        click.echo(f"✅ Rate limit reset successfully for: {identifier}")

    except Exception as e:
        click.echo(f"❌ Failed to reset rate limit: {str(e)}", err=True)
        raise click.Abort()


@rate_limit.command()
@click.option(
    "--identifier", "-i", required=True, help="Rate limit identifier to get status for"
)
@click.pass_context
def status(ctx, identifier: str):
    """
    Get rate limit status for an identifier.

    This command displays detailed rate limit status information.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo(f"Getting rate limit status for identifier: {identifier}")

        # Get rate limit status
        status = security_manager.rate_limiter.get_rate_limit_status(identifier)

        click.echo(f"Rate Limit Status for '{identifier}':")
        click.echo(f"  Current Count: {status.current_count}")
        click.echo(f"  Limit: {status.limit}")
        click.echo(f"  Window Start: {status.window_start}")
        click.echo(f"  Window End: {status.window_end}")
        click.echo(f"  Is Allowed: {status.is_allowed}")

    except Exception as e:
        click.echo(f"❌ Failed to get rate limit status: {str(e)}", err=True)
        raise click.Abort()


@security_cli.group()
@click.pass_context
def config(ctx):
    """
    Configuration management operations.

    Manage security configuration including validation, export,
    and configuration testing.
    """
    pass


@config.command()
@click.pass_context
def validate(ctx):
    """
    Validate security configuration.

    This command validates the current security configuration
    and reports any issues.
    """
    try:
        config = ctx.obj["config"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo("Validating security configuration...")

        # Validate configuration
        issues = []

        # Check authentication configuration
        if config.auth and config.auth.enabled:
            if not config.auth.methods:
                issues.append("Authentication enabled but no methods specified")

        # Check rate limiting configuration
        if config.rate_limit and config.rate_limit.enabled:
            if config.rate_limit.default_requests_per_minute <= 0:
                issues.append(
                    "Invalid rate limit: requests per minute must be positive"
                )

        # Check SSL configuration
        if config.ssl and config.ssl.enabled:
            if not config.ssl.cert_file or not config.ssl.key_file:
                issues.append("SSL enabled but certificate or key file not specified")

        if issues:
            click.echo(f"❌ Configuration validation failed!", err=True)
            for issue in issues:
                click.echo(f"  - {issue}")
            raise click.Abort()
        else:
            click.echo(f"✅ Configuration validation passed!")

    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {str(e)}", err=True)
        raise click.Abort()


@config.command()
@click.option(
    "--output", "-o", type=click.Path(), help="Output file path (default: stdout)"
)
@click.pass_context
def export(ctx, output: Optional[str]):
    """
    Export security configuration.

    This command exports the current security configuration
    to JSON format.
    """
    try:
        config = ctx.obj["config"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo("Exporting security configuration...")

        # Export configuration
        config_json = config.model_dump_json(indent=2)

        if output:
            with open(output, "w") as f:
                f.write(config_json)
            click.echo(f"✅ Configuration exported to: {output}")
        else:
            click.echo(config_json)

    except Exception as e:
        click.echo(f"❌ Failed to export configuration: {str(e)}", err=True)
        raise click.Abort()


@security_cli.command()
@click.option(
    "--output", "-o", type=click.Path(), help="Output file path for roles configuration"
)
@click.option(
    "--template", "-t", is_flag=True, help="Generate template roles configuration"
)
@click.pass_context
def generate_roles(ctx, output: Optional[str], template: bool):
    """
    Generate roles configuration file.

    This command generates a roles configuration file with default
    roles and permissions or a template for customization.
    """
    try:
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo("Generating roles configuration...")

        if template:
            # Generate template roles configuration
            template_roles = {
                "roles": {
                    "admin": {
                        "description": "Administrator role with full access",
                        "permissions": ["*"],
                        "parent_roles": [],
                    },
                    "user": {
                        "description": "Standard user role",
                        "permissions": ["read:own", "write:own"],
                        "parent_roles": [],
                    },
                    "guest": {
                        "description": "Guest role with limited access",
                        "permissions": ["read:public"],
                        "parent_roles": [],
                    },
                },
                "permissions": {
                    "read:own": "Read own resources",
                    "write:own": "Write own resources",
                    "read:public": "Read public resources",
                    "*": "All permissions (wildcard)",
                },
            }

            roles_json = json.dumps(template_roles, indent=2)

            if output:
                with open(output, "w") as f:
                    f.write(roles_json)
                click.echo(f"✅ Template roles configuration generated: {output}")
            else:
                click.echo(roles_json)
        else:
            # Generate current roles configuration
            roles_config = security_manager.permission_manager.export_roles_config()

            if output:
                with open(output, "w") as f:
                    json.dump(roles_config, f, indent=2)
                click.echo(f"✅ Current roles configuration exported: {output}")
            else:
                click.echo(json.dumps(roles_config, indent=2))

    except Exception as e:
        click.echo(f"❌ Failed to generate roles configuration: {str(e)}", err=True)
        raise click.Abort()


@security_cli.command()
@click.option(
    "--output", "-o", type=click.Path(), help="Output file path for audit report"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format for audit report",
)
@click.pass_context
def security_audit(ctx, output: Optional[str], format: str):
    """
    Perform security audit.

    This command performs a comprehensive security audit of the
    system configuration and components.
    """
    try:
        config = ctx.obj["config"]
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo("Performing security audit...")

        # Perform security audit
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "authentication": {
                    "enabled": config.auth.enabled if config.auth else False,
                    "methods": config.auth.methods if config.auth else [],
                    "issues": [],
                },
                "rate_limiting": {
                    "enabled": (
                        config.rate_limit.enabled if config.rate_limit else False
                    ),
                    "default_limit": (
                        config.rate_limit.default_requests_per_minute
                        if config.rate_limit
                        else None
                    ),
                    "issues": [],
                },
                "ssl_tls": {
                    "enabled": config.ssl.enabled if config.ssl else False,
                    "cert_file": config.ssl.cert_file if config.ssl else None,
                    "key_file": config.ssl.key_file if config.ssl else None,
                    "issues": [],
                },
                "permissions": {
                    "enabled": (
                        config.permissions.enabled if config.permissions else False
                    ),
                    "roles_file": (
                        config.permissions.roles_file if config.permissions else None
                    ),
                    "issues": [],
                },
            },
            "components": {
                "auth_manager": {
                    "status": (
                        "✅ Initialized"
                        if security_manager.auth_manager
                        else "❌ Not Initialized"
                    ),
                    "api_keys_count": (
                        len(security_manager.auth_manager.api_keys)
                        if security_manager.auth_manager
                        else 0
                    ),
                },
                "permission_manager": {
                    "status": (
                        "✅ Initialized"
                        if security_manager.permission_manager
                        else "❌ Not Initialized"
                    ),
                    "roles_count": (
                        len(security_manager.permission_manager.roles)
                        if security_manager.permission_manager
                        else 0
                    ),
                },
                "rate_limiter": {
                    "status": (
                        "✅ Initialized"
                        if security_manager.rate_limiter
                        else "❌ Not Initialized"
                    )
                },
                "ssl_manager": {
                    "status": (
                        "✅ Initialized"
                        if security_manager.ssl_manager
                        else "❌ Not Initialized"
                    )
                },
                "cert_manager": {
                    "status": (
                        "✅ Initialized"
                        if security_manager.cert_manager
                        else "❌ Not Initialized"
                    )
                },
            },
            "recommendations": [],
        }

        # Add security recommendations
        if not config.auth.enabled:
            audit_results["recommendations"].append(
                "Enable authentication for better security"
            )

        if not config.rate_limit.enabled:
            audit_results["recommendations"].append(
                "Enable rate limiting to prevent abuse"
            )

        if not config.ssl.enabled:
            audit_results["recommendations"].append(
                "Enable SSL/TLS for secure communication"
            )

        if not config.permissions.enabled:
            audit_results["recommendations"].append(
                "Enable permissions for access control"
            )

        # Output audit results
        if format == "json":
            audit_json = json.dumps(audit_results, indent=2)
            if output:
                with open(output, "w") as f:
                    f.write(audit_json)
                click.echo(f"✅ Security audit report saved: {output}")
            else:
                click.echo(audit_json)
        else:
            # Text format
            click.echo("Security Audit Report")
            click.echo("=" * 50)
            click.echo(f"Timestamp: {audit_results['timestamp']}")
            click.echo()

            click.echo("Configuration:")
            click.echo("-" * 20)
            auth_config = audit_results["configuration"]["authentication"]
            click.echo(
                f"Authentication: {'✅ Enabled' if auth_config['enabled'] else '❌ Disabled'}"
            )
            if auth_config["methods"]:
                click.echo(f"  Methods: {', '.join(auth_config['methods'])}")

            rate_config = audit_results["configuration"]["rate_limiting"]
            click.echo(
                f"Rate Limiting: {'✅ Enabled' if rate_config['enabled'] else '❌ Disabled'}"
            )
            if rate_config["default_limit"]:
                click.echo(
                    f"  Default Limit: {rate_config['default_limit']} requests/minute"
                )

            ssl_config = audit_results["configuration"]["ssl_tls"]
            click.echo(
                f"SSL/TLS: {'✅ Enabled' if ssl_config['enabled'] else '❌ Disabled'}"
            )

            perm_config = audit_results["configuration"]["permissions"]
            click.echo(
                f"Permissions: {'✅ Enabled' if perm_config['enabled'] else '❌ Disabled'}"
            )

            click.echo()
            click.echo("Components:")
            click.echo("-" * 20)
            for name, status in audit_results["components"].items():
                click.echo(f"{name.replace('_', ' ').title()}: {status['status']}")
                if "api_keys_count" in status:
                    click.echo(f"  API Keys: {status['api_keys_count']}")
                if "roles_count" in status:
                    click.echo(f"  Roles: {status['roles_count']}")

            if audit_results["recommendations"]:
                click.echo()
                click.echo("Recommendations:")
                click.echo("-" * 20)
                for rec in audit_results["recommendations"]:
                    click.echo(f"• {rec}")

            if output:
                with open(output, "w") as f:
                    f.write(json.dumps(audit_results, indent=2))
                click.echo(f"\n✅ Detailed audit report saved: {output}")

    except Exception as e:
        click.echo(f"❌ Failed to perform security audit: {str(e)}", err=True)
        raise click.Abort()


@security_cli.command()
@click.pass_context
def status(ctx):
    """
    Display security status.

    This command displays the current status of all security
    components and their configuration.
    """
    try:
        config = ctx.obj["config"]
        security_manager = ctx.obj["security_manager"]
        verbose = ctx.obj["verbose"]

        if verbose:
            click.echo("Getting security status...")

        click.echo("Security Status:")
        click.echo("=" * 50)

        # Authentication status
        auth_enabled = config.auth.enabled if config.auth else False
        auth_methods = config.auth.methods if config.auth else []
        click.echo(f"Authentication: {'✅ Enabled' if auth_enabled else '❌ Disabled'}")
        if auth_methods:
            click.echo(f"  Methods: {', '.join(auth_methods)}")

        # Rate limiting status
        rate_limit_enabled = config.rate_limit.enabled if config.rate_limit else False
        click.echo(
            f"Rate Limiting: {'✅ Enabled' if rate_limit_enabled else '❌ Disabled'}"
        )
        if rate_limit_enabled and config.rate_limit:
            click.echo(
                f"  Default Limit: {config.rate_limit.default_requests_per_minute} requests/minute"
            )

        # SSL/TLS status
        ssl_enabled = config.ssl.enabled if config.ssl else False
        click.echo(f"SSL/TLS: {'✅ Enabled' if ssl_enabled else '❌ Disabled'}")

        # Permissions status
        permissions_enabled = (
            config.permissions.enabled if config.permissions else False
        )
        click.echo(
            f"Permissions: {'✅ Enabled' if permissions_enabled else '❌ Disabled'}"
        )

        # Component status
        click.echo("\nComponent Status:")
        click.echo("-" * 30)

        # Check if components are properly initialized
        components = [
            ("Auth Manager", security_manager.auth_manager),
            ("Permission Manager", security_manager.permission_manager),
            ("Rate Limiter", security_manager.rate_limiter),
            ("SSL Manager", security_manager.ssl_manager),
            ("Certificate Manager", security_manager.cert_manager),
        ]

        for name, component in components:
            if component:
                click.echo(f"{name}: ✅ Initialized")
            else:
                click.echo(f"{name}: ❌ Not Initialized")

    except Exception as e:
        click.echo(f"❌ Failed to get security status: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    security_cli()
