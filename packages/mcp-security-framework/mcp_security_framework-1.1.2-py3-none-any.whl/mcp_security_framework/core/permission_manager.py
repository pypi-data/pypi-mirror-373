"""
Permission Manager Module

This module provides comprehensive role and permission management for the
MCP Security Framework. It handles role hierarchies, permission caching,
and access validation with support for wildcard permissions.

Key Features:
- Role hierarchy management
- Permission caching for performance
- Wildcard permission support
- JSON-based role configuration
- Access validation utilities
- Role and permission CRUD operations

Classes:
    PermissionManager: Main permission management class
    RoleHierarchy: Internal role hierarchy representation
    PermissionCache: Permission caching implementation

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..schemas.config import PermissionConfig
from ..schemas.models import ValidationResult, ValidationStatus
from ..utils.validation_utils import validate_configuration_file


class PermissionManager:
    """
    Permission Manager Class

    This class provides comprehensive role and permission management including
    role hierarchies, permission caching, and access validation.

    The PermissionManager handles:
    - Loading role configurations from JSON files
    - Managing role hierarchies and inheritance
    - Caching permissions for performance optimization
    - Validating access based on user roles and required permissions
    - Supporting wildcard permissions and complex permission patterns
    - CRUD operations for roles and permissions

    Attributes:
        config (PermissionConfig): Permission configuration settings
        logger (Logger): Logger instance for permission operations
        _roles (Dict): Loaded role configurations
        _hierarchy (Dict): Role hierarchy relationships
        _permission_cache (Dict): Cache of effective permissions
        _cache_enabled (bool): Whether permission caching is enabled

    Example:
        >>> config = PermissionConfig(roles_file="roles.json", cache_enabled=True)
        >>> perm_manager = PermissionManager(config)
        >>> result = perm_manager.validate_access(["admin"], ["read:users"])

    Raises:
        PermissionConfigurationError: When permission configuration is invalid
        RoleNotFoundError: When specified role is not found
        PermissionValidationError: When permission validation fails
    """

    def __init__(self, config: PermissionConfig):
        """
        Initialize Permission Manager.

        Args:
            config (PermissionConfig): Permission configuration settings containing
                roles file path, cache settings, and validation options.
                Must be a valid PermissionConfig instance with proper roles
                file path and configuration settings.

        Raises:
            PermissionConfigurationError: If configuration is invalid or roles
                file cannot be loaded.

        Example:
            >>> config = PermissionConfig(roles_file="roles.json")
            >>> perm_manager = PermissionManager(config)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._roles: Dict = {}
        self._hierarchy: Dict = {}
        self._permission_cache: Dict = {}
        self._cache_enabled = config.permission_cache_enabled

        # Load roles configuration
        self._load_roles_configuration()

        # Build role hierarchy
        self._build_role_hierarchy()

        self.logger.info(
            "PermissionManager initialized successfully",
            extra={
                "roles_count": len(self._roles),
                "cache_enabled": self._cache_enabled,
            },
        )

    def validate_access(
        self, user_roles: List[str], required_permissions: List[str]
    ) -> ValidationResult:
        """
        Validate user access to resource based on roles and required permissions.

        This method checks if the user's roles provide the required permissions
        for accessing a specific resource. It considers role hierarchies and
        supports wildcard permissions.

        Args:
            user_roles (List[str]): List of user role names. Must be valid
                role names that exist in the loaded configuration.
            required_permissions (List[str]): List of required permission names.
                Can include wildcard patterns like "read:*" or "admin:*".

        Returns:
            ValidationResult: Validation result containing:
                - is_valid (bool): True if access is granted
                - user_roles (List[str]): User roles used for validation
                - required_permissions (List[str]): Required permissions
                - effective_permissions (Set[str]): Effective permissions
                - missing_permissions (Set[str]): Missing permissions
                - error_code (int): Error code if validation failed
                - error_message (str): Human-readable error message

        Raises:
            RoleNotFoundError: When any user role is not found in configuration
            PermissionValidationError: When permission validation fails

        Example:
            >>> result = perm_manager.validate_access(
            ...     ["admin", "user"],
            ...     ["read:users", "write:posts"]
            ... )
            >>> if result.is_valid:
            ...     print("Access granted")
            >>> else:
            ...     print(f"Access denied: {result.error_message}")
        """
        try:
            # Validate input parameters
            if not user_roles:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    error_code=-32001,
                    error_message="No user roles provided",
                )

            if not required_permissions:
                return ValidationResult(is_valid=True, status=ValidationStatus.VALID)

            # Validate that all user roles exist
            invalid_roles = [role for role in user_roles if role not in self._roles]
            if invalid_roles:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    error_code=-32002,
                    error_message=f"Invalid roles: {invalid_roles}",
                )

            # Get effective permissions for user roles
            effective_permissions = self.get_effective_permissions(user_roles)

            # Check if all required permissions are satisfied
            missing_permissions = set()
            for required_perm in required_permissions:
                if not self._permission_matches(required_perm, effective_permissions):
                    missing_permissions.add(required_perm)

            is_valid = len(missing_permissions) == 0

            if is_valid:
                return ValidationResult(
                    is_valid=True,
                    status=ValidationStatus.VALID,
                    granted_permissions=list(effective_permissions),
                    denied_permissions=[],
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    error_code=-32003,
                    error_message=f"Missing permissions: {missing_permissions}",
                    granted_permissions=list(effective_permissions),
                    denied_permissions=list(missing_permissions),
                )

        except Exception as e:
            self.logger.error(
                "Permission validation failed",
                extra={
                    "user_roles": user_roles,
                    "required_permissions": required_permissions,
                    "error": str(e),
                },
            )
            raise PermissionValidationError(f"Permission validation failed: {str(e)}")

    def get_effective_permissions(self, user_roles: List[str]) -> Set[str]:
        """
        Get effective permissions for user roles including inherited permissions.

        This method calculates the effective permissions for a set of user roles,
        taking into account role hierarchies and inheritance.

        Args:
            user_roles (List[str]): List of user role names

        Returns:
            Set[str]: Set of effective permissions for the user roles

        Raises:
            RoleNotFoundError: When any user role is not found
        """
        if not user_roles:
            return set()

        # Validate that all roles exist
        invalid_roles = [role for role in user_roles if role not in self._roles]
        if invalid_roles:
            raise RoleNotFoundError(f"Invalid roles: {invalid_roles}")

        # Create cache key
        cache_key = tuple(sorted(user_roles))

        # Check cache first
        if self._cache_enabled and cache_key in self._permission_cache:
            return self._permission_cache[cache_key]

        # Calculate effective permissions
        effective_permissions = set()
        for role in user_roles:
            role_permissions = self._get_role_permissions_with_inheritance(role)
            effective_permissions.update(role_permissions)

        # Cache the result
        if self._cache_enabled:
            self._permission_cache[cache_key] = effective_permissions

        return effective_permissions

    def check_role_hierarchy(self, child_role: str, parent_role: str) -> bool:
        """
        Check if child role inherits from parent role through hierarchy.

        This method checks if a child role inherits from a parent role,
        either directly or through the role hierarchy.

        Args:
            child_role (str): Child role name
            parent_role (str): Parent role name

        Returns:
            bool: True if child role inherits from parent role

        Raises:
            RoleNotFoundError: When either role is not found
        """
        if child_role not in self._roles:
            raise RoleNotFoundError(f"Child role not found: {child_role}")

        if parent_role not in self._roles:
            raise RoleNotFoundError(f"Parent role not found: {parent_role}")

        if child_role == parent_role:
            return True

        return self._check_hierarchy_inheritance(child_role, parent_role)

    def add_role_permission(self, role: str, permission: str) -> bool:
        """
        Add permission to role.

        This method adds a permission to a specific role and clears
        the permission cache to ensure consistency.

        Args:
            role (str): Role name
            permission (str): Permission to add

        Returns:
            bool: True if permission was added successfully

        Raises:
            RoleNotFoundError: When role is not found
        """
        if role not in self._roles:
            raise RoleNotFoundError(f"Role not found: {role}")

        try:
            if "permissions" not in self._roles[role]:
                self._roles[role]["permissions"] = []

            if permission not in self._roles[role]["permissions"]:
                self._roles[role]["permissions"].append(permission)

                # Clear cache for this role
                self._clear_role_cache(role)

                self.logger.info(
                    "Permission added to role",
                    extra={"role": role, "permission": permission},
                )
                return True
            else:
                self.logger.warning(
                    "Permission already exists in role",
                    extra={"role": role, "permission": permission},
                )
                return False

        except Exception as e:
            self.logger.error(
                "Failed to add permission to role",
                extra={"role": role, "permission": permission, "error": str(e)},
            )
            return False

    def remove_role_permission(self, role: str, permission: str) -> bool:
        """
        Remove permission from role.

        This method removes a permission from a specific role and clears
        the permission cache to ensure consistency.

        Args:
            role (str): Role name
            permission (str): Permission to remove

        Returns:
            bool: True if permission was removed successfully

        Raises:
            RoleNotFoundError: When role is not found
        """
        if role not in self._roles:
            raise RoleNotFoundError(f"Role not found: {role}")

        try:
            if "permissions" in self._roles[role]:
                if permission in self._roles[role]["permissions"]:
                    self._roles[role]["permissions"].remove(permission)

                    # Clear cache for this role
                    self._clear_role_cache(role)

                    self.logger.info(
                        "Permission removed from role",
                        extra={"role": role, "permission": permission},
                    )
                    return True
                else:
                    self.logger.warning(
                        "Permission not found in role",
                        extra={"role": role, "permission": permission},
                    )
                    return False
            else:
                self.logger.warning("Role has no permissions", extra={"role": role})
                return False

        except Exception as e:
            self.logger.error(
                "Failed to remove permission from role",
                extra={"role": role, "permission": permission, "error": str(e)},
            )
            return False

    def reload_roles_configuration(self) -> bool:
        """
        Reload roles configuration from file.

        This method reloads the roles configuration from the configured
        file and rebuilds the role hierarchy.

        Returns:
            bool: True if configuration was reloaded successfully
        """
        try:
            # Clear existing data
            self._roles.clear()
            self._hierarchy.clear()
            self._permission_cache.clear()

            # Reload configuration
            self._load_roles_configuration()
            self._build_role_hierarchy()

            self.logger.info("Roles configuration reloaded successfully")
            return True

        except Exception as e:
            self.logger.error(
                "Failed to reload roles configuration", extra={"error": str(e)}
            )
            return False

    def get_user_roles(self, username: str) -> List[str]:
        """
        Get roles for a specific user.

        This method retrieves the roles assigned to a specific user.
        It checks the user-role mapping in the configuration and
        returns the associated roles.

        Args:
            username (str): Username to get roles for

        Returns:
            List[str]: List of roles assigned to the user

        Raises:
            RoleNotFoundError: When user is not found in configuration
        """
        try:
            # Check if user-role mapping exists in configuration
            if hasattr(self.config, "user_roles") and self.config.user_roles:
                if username in self.config.user_roles:
                    return self.config.user_roles[username]

            # Check if user has default role mapping
            if hasattr(self.config, "default_user_role"):
                return [self.config.default_user_role]

            # If no explicit mapping, check if user exists in any role
            for role_name, role_config in self._roles.items():
                if hasattr(role_config, "users") and username in role_config.get(
                    "users", []
                ):
                    return [role_name]

            # Return empty list if no roles found
            self.logger.warning(
                f"No roles found for user '{username}'", extra={"username": username}
            )
            return []

        except Exception as e:
            self.logger.error(
                f"Failed to get roles for user '{username}'",
                extra={"username": username, "error": str(e)},
            )
            raise RoleNotFoundError(
                f"Failed to get roles for user '{username}': {str(e)}"
            )

    def get_role_permissions(self, role: str) -> List[str]:
        """
        Get direct permissions for a specific role.

        This method returns the direct permissions assigned to a role,
        excluding inherited permissions from parent roles.

        Args:
            role (str): Role name to get permissions for

        Returns:
            List[str]: List of direct permissions for the role

        Raises:
            RoleNotFoundError: When role is not found in configuration
        """
        if role not in self._roles:
            raise RoleNotFoundError(f"Role not found: {role}")

        return self._roles[role].get("permissions", []).copy()

    def get_all_roles(self) -> List[str]:
        """
        Get list of all available roles.

        Returns:
            List[str]: List of all role names in the configuration
        """
        return list(self._roles.keys())

    def get_role_hierarchy(self) -> Dict[str, List[str]]:
        """
        Get complete role hierarchy.

        Returns:
            Dict[str, List[str]]: Dictionary mapping roles to their parent roles
        """
        return self._hierarchy.copy()

    def export_roles_config(self) -> Dict:
        """
        Export current roles configuration.

        This method exports the current roles configuration including
        all roles, permissions, and hierarchy relationships.

        Returns:
            Dict: Complete roles configuration dictionary containing:
                - roles: Dictionary of role definitions
                - permissions: Dictionary of permission descriptions
                - hierarchy: Role hierarchy relationships

        Example:
            >>> config = perm_manager.export_roles_config()
            >>> with open('exported_roles.json', 'w') as f:
            ...     json.dump(config, f, indent=2)
        """
        exported_config = {
            "roles": {},
            "permissions": {},
            "hierarchy": self._hierarchy.copy(),
        }

        # Export roles with their permissions
        for role_name, role_data in self._roles.items():
            exported_config["roles"][role_name] = {
                "description": role_data.get("description", ""),
                "permissions": role_data.get("permissions", []),
                "parent_roles": self._hierarchy.get(role_name, []),
            }

        # Collect all unique permissions
        all_permissions = set()
        for role_data in self._roles.values():
            permissions = role_data.get("permissions", [])
            all_permissions.update(permissions)

        # Create permission descriptions
        for permission in all_permissions:
            if permission not in exported_config["permissions"]:
                # Generate default description based on permission name
                description = permission.replace(":", " ").replace("_", " ").title()
                exported_config["permissions"][permission] = description

        self.logger.info(
            "Roles configuration exported",
            extra={
                "roles_count": len(exported_config["roles"]),
                "permissions_count": len(exported_config["permissions"]),
            },
        )

        return exported_config

    def clear_cache(self) -> None:
        """Clear permission cache."""
        self._permission_cache.clear()
        self.logger.info("Permission cache cleared")

    def clear_permission_cache(self) -> None:
        """Clear permission cache."""
        self._permission_cache.clear()
        self.logger.info("Permission cache cleared")

    def _load_roles_configuration(self) -> None:
        """Load roles configuration from file."""
        try:
            roles_file = Path(self.config.roles_file)

            if not roles_file.exists():
                raise PermissionConfigurationError(
                    f"Roles file not found: {roles_file}"
                )

            with open(roles_file, "r", encoding="utf-8") as f:
                roles_data = json.load(f)
                # Handle both direct roles dict and nested "roles" key
                if "roles" in roles_data:
                    self._roles = roles_data["roles"]
                else:
                    self._roles = roles_data

            # Validate roles structure
            self._validate_roles_structure()

            self.logger.info(
                "Roles configuration loaded", extra={"roles_count": len(self._roles)}
            )

        except json.JSONDecodeError as e:
            raise PermissionConfigurationError(f"Invalid JSON in roles file: {str(e)}")
        except Exception as e:
            raise PermissionConfigurationError(
                f"Failed to load roles configuration: {str(e)}"
            )

    def _validate_roles_structure(self) -> None:
        """Validate roles configuration structure."""
        for role_name, role_data in self._roles.items():
            if not isinstance(role_data, dict):
                raise PermissionConfigurationError(f"Invalid role data for {role_name}")

            if "permissions" in role_data and not isinstance(
                role_data["permissions"], list
            ):
                raise PermissionConfigurationError(
                    f"Invalid permissions for role {role_name}"
                )

            if "inherits" in role_data and not isinstance(role_data["inherits"], list):
                raise PermissionConfigurationError(
                    f"Invalid inheritance for role {role_name}"
                )

    def _build_role_hierarchy(self) -> None:
        """Build role hierarchy from configuration."""
        self._hierarchy.clear()

        for role_name, role_data in self._roles.items():
            parent_roles = role_data.get("inherits", [])
            self._hierarchy[role_name] = parent_roles.copy()

    def _get_role_permissions_with_inheritance(self, role: str) -> Set[str]:
        """Get permissions for role including inherited permissions."""
        permissions = set()

        # Add direct permissions
        direct_permissions = self._roles[role].get("permissions", [])
        permissions.update(direct_permissions)

        # Add inherited permissions
        parent_roles = self._hierarchy.get(role, [])
        for parent_role in parent_roles:
            if parent_role in self._roles:
                parent_permissions = self._get_role_permissions_with_inheritance(
                    parent_role
                )
                permissions.update(parent_permissions)

        return permissions

    def _check_hierarchy_inheritance(self, child_role: str, parent_role: str) -> bool:
        """Check if child role inherits from parent role through hierarchy."""
        parent_roles = self._hierarchy.get(child_role, [])

        # Check direct parents
        if parent_role in parent_roles:
            return True

        # Check indirect parents
        for direct_parent in parent_roles:
            if self._check_hierarchy_inheritance(direct_parent, parent_role):
                return True

        return False

    def _permission_matches(
        self, required_perm: str, available_permissions: Set[str]
    ) -> bool:
        """Check if required permission matches any available permission."""
        # Direct match
        if required_perm in available_permissions:
            return True

        # Check for universal permission "*" (all permissions)
        if "*" in available_permissions:
            return True

        # Wildcard match
        if "*" in required_perm:
            perm_parts = required_perm.split(":")
            if len(perm_parts) == 2:
                action, resource = perm_parts

                # Check action wildcard
                if action == "*":
                    for perm in available_permissions:
                        if perm.endswith(f":{resource}"):
                            return True

                # Check resource wildcard
                elif resource == "*":
                    for perm in available_permissions:
                        if perm.startswith(f"{action}:"):
                            return True

        return False

    def _clear_role_cache(self, role: str) -> None:
        """Clear cache entries that include the specified role."""
        if not self._cache_enabled:
            return

        keys_to_remove = []
        for cache_key in self._permission_cache.keys():
            if role in cache_key:
                keys_to_remove.append(cache_key)

        for key in keys_to_remove:
            del self._permission_cache[key]

    def _load_external_permissions(self) -> Dict[str, List[str]]:
        """
        Load permissions from external systems.

        This is a placeholder method for external permission loading.
        In a real implementation, this would connect to external systems
        like LDAP, Active Directory, or other identity providers.

        Returns:
            Dict[str, List[str]]: Dictionary mapping role names to permission lists
        """
        # Placeholder implementation - return empty dict
        return {}


class PermissionConfigurationError(Exception):
    """Raised when permission configuration is invalid."""

    def __init__(self, message: str, error_code: int = -32001):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class RoleNotFoundError(Exception):
    """Raised when a specified role is not found."""

    def __init__(self, message: str, error_code: int = -32002):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class PermissionValidationError(Exception):
    """Raised when permission validation fails."""

    def __init__(self, message: str, error_code: int = -32003):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
