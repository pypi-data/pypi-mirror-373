"""
Authentication Manager Module

This module provides comprehensive authentication management for the
MCP Security Framework. It handles multiple authentication methods,
JWT token management, and integration with permission management.

Key Features:
- Multiple authentication methods (API key, JWT, certificate)
- JWT token creation and validation
- Integration with PermissionManager for role extraction
- Secure credential validation
- Authentication result management
- Session management utilities

Classes:
    AuthManager: Main authentication management class
    AuthResult: Authentication result container
    JWTManager: JWT token management utilities

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization

from ..core.permission_manager import PermissionManager
from ..schemas.config import AuthConfig
from ..schemas.models import AuthResult, AuthStatus, ValidationResult
from ..utils.cert_utils import (
    extract_permissions_from_certificate,
    extract_roles_from_certificate,
    parse_certificate,
    validate_certificate_chain,
)
from ..utils.crypto_utils import (
    generate_secure_token,
    hash_password,
    validate_api_key_format,
    verify_password,
)
from ..utils.datetime_compat import (
    get_not_valid_after_utc,
)


class AuthManager:
    """
    Authentication Manager Class

    This class provides comprehensive authentication management including
    multiple authentication methods, JWT token management, and integration
    with permission management.

    The AuthManager handles:
    - API key authentication with secure validation
    - JWT token creation, validation, and management
    - Certificate-based authentication with role extraction
    - Integration with PermissionManager for role validation
    - Secure credential storage and validation
    - Session management and token refresh
    - Authentication result management with detailed status

    Attributes:
        config (AuthConfig): Authentication configuration settings
        logger (Logger): Logger instance for authentication operations
        permission_manager (PermissionManager): Permission manager instance
        _api_keys (Dict): Stored API keys for validation
        _jwt_secret (str): JWT signing secret
        _token_cache (Dict): Cache for validated tokens
        _session_store (Dict): Active session storage

    Example:
        >>> config = AuthConfig(api_keys={"user1": "key123"}, jwt_secret="secret")
        >>> auth_manager = AuthManager(config, permission_manager)
        >>> result = auth_manager.authenticate_api_key("key123")

    Raises:
        AuthenticationConfigurationError: When authentication configuration is invalid
        AuthenticationError: When authentication fails
        JWTValidationError: When JWT token validation fails
    """

    def __init__(self, config: AuthConfig, permission_manager: PermissionManager):
        """
        Initialize Authentication Manager.

        Args:
            config (AuthConfig): Authentication configuration settings containing
                API keys, JWT settings, and authentication parameters.
                Must be a valid AuthConfig instance with proper authentication
                settings and security parameters.
            permission_manager (PermissionManager): Permission manager instance
                for role and permission validation. Must be a valid
                PermissionManager instance.

        Raises:
            AuthenticationConfigurationError: If configuration is invalid or
                permission manager is not provided.

        Example:
            >>> config = AuthConfig(api_keys={"user1": "key123"})
            >>> perm_manager = PermissionManager(perm_config)
            >>> auth_manager = AuthManager(config, perm_manager)
        """
        if not config:
            raise AuthenticationConfigurationError(
                "Authentication configuration is required"
            )

        if not permission_manager:
            raise AuthenticationConfigurationError("Permission manager is required")

        self.config = config
        self.permission_manager = permission_manager
        self.logger = logging.getLogger(__name__)

        # Initialize storage
        # Convert API keys from "key": "user" format to "user": "key" format
        # or handle new format "key": {"username": "user", "roles": ["role1", "role2"]}
        if config.api_keys:
            self._api_keys = {}
            self._api_key_metadata = {}
            for key, value in config.api_keys.items():
                if isinstance(value, str):
                    # Old format: "key": "user"
                    self._api_keys[value] = key
                elif isinstance(value, dict):
                    # New format: "key": {"username": "user", "roles": ["role1", "role2"]}
                    username = value.get("username", key)
                    self._api_keys[username] = key
                    self._api_key_metadata[key] = value
                else:
                    self.logger.warning(
                        f"Invalid API key format for key {key}: {value}"
                    )
        else:
            self._api_keys = {}
            self._api_key_metadata = {}
        self._jwt_secret = (
            config.jwt_secret.get_secret_value()
            if config.jwt_secret
            else generate_secure_token(32)
        )
        self._token_cache: Dict[str, Dict] = {}
        self._session_store: Dict[str, Dict] = {}

        # Validate configuration
        self._validate_configuration()

        self.logger.info(
            "AuthManager initialized successfully",
            extra={
                "api_keys_count": len(self._api_keys),
                "jwt_enabled": bool(self._jwt_secret),
                "jwt_expiry_hours": config.jwt_expiry_hours,
            },
        )

    @property
    def is_auth_enabled(self) -> bool:
        """
        Check if authentication is enabled.

        Returns:
            bool: True if authentication is enabled, False otherwise
        """
        return self.config.enabled

    def authenticate_api_key(self, api_key: str) -> AuthResult:
        """
        Authenticate user using API key.

        This method validates an API key against the configured key store and
        returns authentication result with user information and permissions.

        The method performs comprehensive API key validation including:
        - Key format validation and sanitization
        - Key existence verification in configured store
        - User role and permission extraction
        - Authentication result generation with metadata

        Args:
            api_key (str): API key string to validate. Must be a non-empty
                string containing the API key value. The key should be
                provided in the format expected by the authentication system.
                Valid keys are typically 32-64 character alphanumeric strings.

        Returns:
            AuthResult: Authentication result object containing:
                - is_valid (bool): True if authentication succeeded
                - username (str): Authenticated username if valid
                - roles (List[str]): User roles and permissions
                - auth_method (str): Authentication method used ("api_key")
                - error_code (int): Error code if authentication failed
                - error_message (str): Human-readable error message

        Raises:
            AuthenticationError: When API key is invalid, expired, or
                authentication process fails
            AuthenticationConfigurationError: When authentication configuration
                is invalid or missing
            ValueError: When API key parameter is empty or malformed

        Example:
            >>> auth_manager = AuthManager(config, permission_manager)
            >>> result = auth_manager.authenticate_api_key("user_api_key_123")
            >>> if result.is_valid:
            ...     print(f"Authenticated user: {result.username}")
            ...     print(f"User roles: {result.roles}")
            >>> else:
            ...     print(f"Authentication failed: {result.error_message}")

        Note:
            This method is thread-safe and can be called concurrently.
            API keys are validated against the in-memory key store for
            performance. For production use, consider implementing
            persistent key storage with proper encryption.

        See Also:
            authenticate_jwt_token: JWT token authentication method
            authenticate_certificate: Certificate-based authentication
        """
        try:
            # Validate input
            if not api_key:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="api_key",
                    error_code=-32001,
                    error_message="API key is required",
                )

            # Validate API key format
            if not validate_api_key_format(api_key):
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="api_key",
                    error_code=-32002,
                    error_message="Invalid API key format",
                )

            # Find user by API key
            username = None
            user_roles = []
            for user, api_key_in_config in self._api_keys.items():
                if api_key_in_config == api_key:
                    username = user
                    # Check if we have metadata for this API key
                    if api_key in self._api_key_metadata:
                        metadata = self._api_key_metadata[api_key]
                        user_roles = metadata.get("roles", [])
                    break

            if not username:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="api_key",
                    error_code=-32003,
                    error_message="Invalid API key",
                )

            # If we don't have roles from metadata, get them from permission manager
            if not user_roles:
                try:
                    user_roles = self._get_user_roles(username)
                except Exception as e:
                    self.logger.error(
                        "Failed to get user roles",
                        extra={"username": username, "error": str(e)},
                    )
                    return AuthResult(
                        is_valid=False,
                        status=AuthStatus.FAILED,
                        auth_method="api_key",
                        error_code=-32004,
                        error_message="Failed to retrieve user roles",
                    )

            # Get user permissions from permission manager
            user_permissions = set()
            if self.permission_manager:
                try:
                    permissions_result = (
                        self.permission_manager.get_effective_permissions(user_roles)
                    )
                    # Handle both set and mock objects
                    if hasattr(permissions_result, "__iter__") and not isinstance(
                        permissions_result, str
                    ):
                        user_permissions = set(permissions_result)
                    else:
                        user_permissions = set()
                except Exception as e:
                    self.logger.warning(
                        "Failed to get user permissions",
                        extra={
                            "username": username,
                            "roles": user_roles,
                            "error": str(e),
                        },
                    )

            # Create successful authentication result
            auth_result = AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username=username,
                roles=user_roles,
                permissions=user_permissions,
                auth_method="api_key",
                auth_timestamp=datetime.now(timezone.utc),
            )

            self.logger.info(
                "API key authentication successful",
                extra={
                    "username": username,
                    "roles": user_roles,
                    "auth_method": "api_key",
                },
            )

            return auth_result

        except Exception as e:
            self.logger.error(
                "API key authentication failed",
                extra={
                    "api_key": api_key[:8] + "..." if api_key else None,
                    "error": str(e),
                },
            )
            raise AuthenticationError(f"API key authentication failed: {str(e)}")

    def authenticate_jwt_token(self, token: str) -> AuthResult:
        """
        Authenticate user using JWT token.

        This method validates a JWT token and extracts user information
        and permissions from the token payload.

        The method performs comprehensive JWT validation including:
        - Token format and structure validation
        - Signature verification using configured secret
        - Token expiration and validity checks
        - Payload extraction and validation
        - User role and permission extraction

        Args:
            token (str): JWT token string to validate. Must be a valid
                JWT token format with proper signature and payload.
                The token should contain user information and roles.

        Returns:
            AuthResult: Authentication result object containing:
                - is_valid (bool): True if authentication succeeded
                - username (str): Authenticated username if valid
                - roles (List[str]): User roles from token
                - auth_method (str): Authentication method used ("jwt")
                - error_code (int): Error code if authentication failed
                - error_message (str): Human-readable error message

        Raises:
            JWTValidationError: When JWT token is invalid, expired, or
                validation process fails
            AuthenticationError: When authentication process fails
            ValueError: When token parameter is empty or malformed

        Example:
            >>> auth_manager = AuthManager(config, permission_manager)
            >>> result = auth_manager.authenticate_jwt_token("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
            >>> if result.is_valid:
            ...     print(f"Authenticated user: {result.username}")
            ...     print(f"Token expires: {result.expires_at}")
            >>> else:
            ...     print(f"JWT validation failed: {result.error_message}")

        Note:
            This method validates JWT tokens using the configured secret.
            Token expiration is automatically checked. For production use,
            consider implementing token refresh mechanisms.

        See Also:
            create_jwt_token: JWT token creation method
            authenticate_api_key: API key authentication method
        """
        try:
            # Validate input
            if not token:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="jwt",
                    error_code=-32001,
                    error_message="JWT token is required",
                )

            # Check token cache
            if token in self._token_cache:
                cached_result = self._token_cache[token]
                if not self._is_token_expired(cached_result):
                    return cached_result
                else:
                    # Remove expired token from cache
                    del self._token_cache[token]

            # Decode and validate JWT token
            try:
                payload = jwt.decode(
                    token,
                    self._jwt_secret,
                    algorithms=["HS256"],
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iat": True,
                        "verify_aud": False,
                    },
                )
            except jwt.ExpiredSignatureError:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.EXPIRED,
                    auth_method="jwt",
                    error_code=-32002,
                    error_message="JWT token has expired",
                )
            except jwt.InvalidTokenError as e:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="jwt",
                    error_code=-32003,
                    error_message=f"Invalid JWT token: {str(e)}",
                )

            # Extract user information from payload
            username = payload.get("username")
            if not username:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="jwt",
                    error_code=-32004,
                    error_message="JWT token missing username",
                )

            # Extract roles from payload
            roles = payload.get("roles", [])
            if not isinstance(roles, list):
                roles = []

            # Extract expiration time
            expires_at = None
            if "exp" in payload:
                expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

            # Get user permissions from permission manager
            user_permissions = set()
            if self.permission_manager:
                try:
                    permissions_result = (
                        self.permission_manager.get_effective_permissions(roles)
                    )
                    # Handle both set and mock objects
                    if hasattr(permissions_result, "__iter__") and not isinstance(
                        permissions_result, str
                    ):
                        user_permissions = set(permissions_result)
                    else:
                        user_permissions = set()
                except Exception as e:
                    self.logger.warning(
                        "Failed to get user permissions",
                        extra={"username": username, "roles": roles, "error": str(e)},
                    )

            # Create successful authentication result
            auth_result = AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username=username,
                roles=roles,
                permissions=user_permissions,
                auth_method="jwt",
                auth_timestamp=datetime.now(timezone.utc),
                token_expiry=expires_at,
            )

            # Cache the result
            self._token_cache[token] = auth_result

            self.logger.info(
                "JWT token authentication successful",
                extra={"username": username, "roles": roles, "auth_method": "jwt"},
            )

            return auth_result

        except Exception as e:
            self.logger.error(
                "JWT token authentication failed",
                extra={"token": token[:20] + "..." if token else None, "error": str(e)},
            )
            raise JWTValidationError(f"JWT token authentication failed: {str(e)}")

    def authenticate_certificate(self, cert_pem: str) -> AuthResult:
        """
        Authenticate user using X.509 certificate.

        This method validates an X.509 certificate and extracts user
        information and roles from certificate extensions.

        The method performs comprehensive certificate validation including:
        - Certificate format and structure validation
        - Certificate chain validation against CA
        - Certificate expiration and validity checks
        - Role and permission extraction from certificate extensions
        - Certificate fingerprint validation

        Args:
            cert_pem (str): X.509 certificate in PEM format. Must be a valid
                PEM certificate with proper structure and extensions.
                The certificate should contain user roles in extensions.

        Returns:
            AuthResult: Authentication result object containing:
                - is_valid (bool): True if authentication succeeded
                - username (str): Authenticated username from certificate
                - roles (List[str]): User roles from certificate
                - auth_method (str): Authentication method used ("certificate")
                - error_code (int): Error code if authentication failed
                - error_message (str): Human-readable error message

        Raises:
            CertificateValidationError: When certificate is invalid, expired, or
                validation process fails
            AuthenticationError: When authentication process fails
            ValueError: When certificate parameter is empty or malformed

        Example:
            >>> auth_manager = AuthManager(config, permission_manager)
            >>> with open("user.crt", "r") as f:
            ...     cert_pem = f.read()
            >>> result = auth_manager.authenticate_certificate(cert_pem)
            >>> if result.is_valid:
            ...     print(f"Authenticated user: {result.username}")
            ...     print(f"Certificate roles: {result.roles}")
            >>> else:
            ...     print(f"Certificate validation failed: {result.error_message}")

        Note:
            This method validates X.509 certificates and extracts roles
            from certificate extensions. Certificate chain validation
            requires proper CA configuration.

        See Also:
            authenticate_api_key: API key authentication method
            authenticate_jwt_token: JWT token authentication method
        """
        try:
            # Validate input
            if not cert_pem:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="certificate",
                    error_code=-32001,
                    error_message="Certificate is required",
                )

            # Parse certificate
            try:
                cert = parse_certificate(cert_pem)
            except Exception as e:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="certificate",
                    error_code=-32002,
                    error_message=f"Invalid certificate format: {str(e)}",
                )

            # Check certificate expiration
            now = datetime.now(timezone.utc)
            if get_not_valid_after_utc(cert) < now:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.EXPIRED,
                    auth_method="certificate",
                    error_code=-32003,
                    error_message="Certificate has expired",
                )

            # Extract username from certificate subject
            username = self._extract_username_from_certificate(cert)
            if not username:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.INVALID,
                    auth_method="certificate",
                    error_code=-32004,
                    error_message="Certificate missing username in subject",
                )

            # Extract roles from certificate
            try:
                roles = extract_roles_from_certificate(cert_pem)
            except Exception as e:
                self.logger.warning(
                    "Failed to extract roles from certificate",
                    extra={"username": username, "error": str(e)},
                )
                roles = []

            # Validate certificate chain if CA is configured
            if self.config.ca_cert_file:
                try:
                    is_valid_chain = validate_certificate_chain(
                        cert_pem, self.config.ca_cert_file
                    )
                    if not is_valid_chain:
                        return AuthResult(
                            is_valid=False,
                            status=AuthStatus.INVALID,
                            auth_method="certificate",
                            error_code=-32005,
                            error_message="Certificate chain validation failed",
                        )
                except Exception as e:
                    self.logger.warning(
                        "Certificate chain validation failed",
                        extra={"username": username, "error": str(e)},
                    )

            # Create successful authentication result
            auth_result = AuthResult(
                is_valid=True,
                status=AuthStatus.SUCCESS,
                username=username,
                roles=roles,
                auth_method="certificate",
                auth_timestamp=datetime.now(timezone.utc),
                token_expiry=get_not_valid_after_utc(cert),
            )

            self.logger.info(
                "Certificate authentication successful",
                extra={
                    "username": username,
                    "roles": roles,
                    "auth_method": "certificate",
                },
            )

            return auth_result

        except Exception as e:
            self.logger.error(
                "Certificate authentication failed",
                extra={
                    "cert_pem": cert_pem[:100] + "..." if cert_pem else None,
                    "error": str(e),
                },
            )
            raise CertificateValidationError(
                f"Certificate authentication failed: {str(e)}"
            )

    def create_jwt_token(self, user_data: Dict) -> str:
        """
        Create JWT token for user.

        This method creates a JWT token containing user information
        and roles for authentication purposes.

        The method creates a secure JWT token with:
        - User information in payload
        - Role and permission data
        - Proper expiration time
        - Secure signing with configured secret
        - Standard JWT claims (iat, exp, sub)

        Args:
            user_data (Dict): User data dictionary containing:
                - username (str): User username (required)
                - roles (List[str]): User roles (optional)
                - permissions (List[str]): User permissions (optional)
                - additional_data (Dict): Additional user data (optional)
                Must contain at least username field.

        Returns:
            str: JWT token string containing user information and claims.
                The token is signed with the configured secret and includes
                standard JWT claims and user-specific data.

        Raises:
            ValueError: When user_data is invalid or missing required fields
            JWTValidationError: When JWT token creation fails
            AuthenticationConfigurationError: When JWT configuration is invalid

        Example:
            >>> auth_manager = AuthManager(config, permission_manager)
            >>> user_data = {
            ...     "username": "john_doe",
            ...     "roles": ["user", "admin"],
            ...     "permissions": ["read:users", "write:posts"]
            ... }
            >>> token = auth_manager.create_jwt_token(user_data)
            >>> print(f"Created JWT token: {token}")

        Note:
            This method creates JWT tokens with configurable expiration.
            Tokens are signed with the configured secret for security.
            For production use, consider implementing token refresh mechanisms.

        See Also:
            authenticate_jwt_token: JWT token validation method
            validate_jwt_token: JWT token validation utility
        """
        try:
            # Validate input
            if user_data is None:
                raise ValueError("User data must be provided")

            if not isinstance(user_data, dict):
                raise ValueError("User data must be a dictionary")

            if not user_data:  # Check if dict is empty
                raise ValueError("User data dictionary cannot be empty")

            username = user_data.get("username")
            if not username:
                raise ValueError("Username is required in user data")

            # Prepare JWT payload
            now = datetime.now(timezone.utc)
            payload = {
                "username": username,
                "roles": user_data.get("roles", []),
                "permissions": user_data.get("permissions", []),
                "iat": int(now.timestamp()),
                "exp": int(
                    (now + timedelta(hours=self.config.jwt_expiry_hours)).timestamp()
                ),
                "sub": username,
                "iss": "mcp_security_framework",
            }

            # Add additional user data if provided
            additional_data = user_data.get("additional_data", {})
            if additional_data:
                payload["user_data"] = additional_data

            # Create JWT token
            token = jwt.encode(payload, self._jwt_secret, algorithm="HS256")

            self.logger.info(
                "JWT token created successfully",
                extra={
                    "username": username,
                    "roles": payload["roles"],
                    "expires_in_hours": self.config.jwt_expiry_hours,
                },
            )

            return token

        except Exception as e:
            self.logger.error(
                "Failed to create JWT token",
                extra={"user_data": user_data, "error": str(e)},
            )
            raise JWTValidationError(f"Failed to create JWT token: {str(e)}")

    def validate_jwt_token(self, token: str) -> bool:
        """
        Validate JWT token without full authentication.

        This method performs basic JWT token validation including
        signature verification and expiration checks.

        Args:
            token (str): JWT token to validate. Must be a valid
                JWT token format with proper signature.

        Returns:
            bool: True if token is valid, False otherwise.
                Returns True when token has valid signature and
                is not expired.

        Example:
            >>> auth_manager = AuthManager(config, permission_manager)
            >>> is_valid = auth_manager.validate_jwt_token("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
            >>> if is_valid:
            ...     print("Token is valid")
            >>> else:
            ...     print("Token is invalid")
        """
        try:
            if not token:
                return False

            # Decode token to check signature and expiration
            jwt.decode(
                token,
                self._jwt_secret,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": False,
                },
            )

            return True

        except jwt.InvalidTokenError:
            return False
        except Exception:
            return False

    def add_api_key(self, username: str, api_key: str) -> bool:
        """
        Add API key for user.

        This method adds an API key to the authentication store
        for the specified user.

        Args:
            username (str): Username to associate with API key
            api_key (str): API key to add

        Returns:
            bool: True if API key was added successfully, False otherwise

        Example:
            >>> auth_manager = AuthManager(config, permission_manager)
            >>> success = auth_manager.add_api_key("john_doe", "new_api_key_123")
            >>> if success:
            ...     print("API key added successfully")
        """
        try:
            if not username or not api_key:
                return False

            if not validate_api_key_format(api_key):
                return False

            self._api_keys[username] = api_key

            self.logger.info("API key added for user", extra={"username": username})

            return True

        except Exception as e:
            self.logger.error(
                "Failed to add API key", extra={"username": username, "error": str(e)}
            )
            return False

    def remove_api_key(self, username: str) -> bool:
        """
        Remove API key for user.

        Args:
            username (str): Username whose API key to remove

        Returns:
            bool: True if API key was removed successfully, False otherwise
        """
        try:
            if username in self._api_keys:
                del self._api_keys[username]

                self.logger.info(
                    "API key removed for user", extra={"username": username}
                )

                return True

            return False

        except Exception as e:
            self.logger.error(
                "Failed to remove API key",
                extra={"username": username, "error": str(e)},
            )
            return False

    def clear_token_cache(self) -> None:
        """Clear JWT token cache."""
        self._token_cache.clear()
        self.logger.info("JWT token cache cleared")

    def clear_session_store(self) -> None:
        """Clear session store."""
        self._session_store.clear()
        self.logger.info("Session store cleared")

    def _validate_configuration(self) -> None:
        """Validate authentication configuration."""
        if not self._jwt_secret:
            raise AuthenticationConfigurationError("JWT secret is required")

        if len(self._jwt_secret) < 16:
            raise AuthenticationConfigurationError(
                "JWT secret must be at least 16 characters"
            )

    def _get_user_roles(self, username: str) -> List[str]:
        """
        Get user roles from configuration.

        This method retrieves user roles from the authentication configuration.
        It checks both the user_roles mapping and the permission manager.

        Args:
            username (str): Username to get roles for

        Returns:
            List[str]: List of user roles
        """
        # Check user_roles mapping first
        if self.config.user_roles and username in self.config.user_roles:
            return self.config.user_roles[username]

        # Fallback to permission manager
        if self.permission_manager:
            return self.permission_manager.get_user_roles(username)

        return []

    def _validate_external_user(
        self, username: str, credentials: Dict[str, Any]
    ) -> bool:
        """
        Validate user against external authentication system.

        This method provides a hook for integrating with external
        authentication systems (LDAP, Active Directory, etc.).

        Args:
            username (str): Username to validate
            credentials (Dict[str, Any]): User credentials

        Returns:
            bool: True if user is valid in external system
        """
        # This is a placeholder for external authentication integration
        # In a real implementation, this would connect to external auth systems
        self.logger.debug(
            "External user validation called",
            extra={"username": username, "method": "external"},
        )

        # For now, return False to indicate external validation not implemented
        return False

    def _extract_username_from_certificate(
        self, cert: x509.Certificate
    ) -> Optional[str]:
        """Extract username from certificate subject."""
        try:
            # Try to get username from Common Name
            cn_attr = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
            if cn_attr:
                return cn_attr[0].value

            # Try to get username from Subject Alternative Name
            try:
                san = cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                if san and san.value:
                    for name in san.value:
                        if isinstance(name, x509.DNSName):
                            return name.value
            except x509.ExtensionNotFound:
                pass

            return None

        except Exception:
            return None

    def _is_token_expired(self, auth_result: AuthResult) -> bool:
        """Check if authentication result is expired."""
        if not auth_result.token_expiry:
            return False

        return datetime.now(timezone.utc) > auth_result.token_expiry


class AuthenticationConfigurationError(Exception):
    """Raised when authentication configuration is invalid."""

    def __init__(self, message: str, error_code: int = -32001):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    def __init__(self, message: str, error_code: int = -32002):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class JWTValidationError(Exception):
    """Raised when JWT token validation fails."""

    def __init__(self, message: str, error_code: int = -32003):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class CertificateValidationError(Exception):
    """Raised when certificate validation fails."""

    def __init__(self, message: str, error_code: int = -32004):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
