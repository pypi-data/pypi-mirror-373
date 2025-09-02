"""
Tests for Permission Manager Module

This module contains comprehensive tests for the PermissionManager class,
including role hierarchy management, permission validation, and caching.

Test Coverage:
- PermissionManager initialization
- Role and permission validation
- Role hierarchy management
- Permission caching
- CRUD operations for roles and permissions
- Error handling and edge cases

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from mcp_security_framework.core.permission_manager import (
    PermissionConfigurationError,
    PermissionManager,
    PermissionValidationError,
    RoleNotFoundError,
)
from mcp_security_framework.schemas.config import PermissionConfig
from mcp_security_framework.schemas.models import ValidationResult


class TestPermissionManager:
    """Test suite for PermissionManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary roles configuration
        self.roles_config = {
            "admin": {
                "permissions": ["read:*", "write:*", "delete:*", "admin:*"],
                "inherits": [],
            },
            "moderator": {
                "permissions": ["read:*", "write:posts", "moderate:comments"],
                "inherits": ["user"],
            },
            "user": {
                "permissions": ["read:posts", "write:posts", "read:comments"],
                "inherits": [],
            },
            "guest": {"permissions": ["read:posts"], "inherits": []},
        }

        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(self.roles_config, self.temp_file)
        self.temp_file.close()

        # Create config
        self.config = PermissionConfig(
            roles_file=self.temp_file.name, permission_cache_enabled=True
        )

        # Create permission manager
        self.perm_manager = PermissionManager(self.config)

    def teardown_method(self):
        """Clean up after each test method."""
        # Remove temporary file
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_permission_manager_initialization(self):
        """Test PermissionManager initialization."""
        assert self.perm_manager.config == self.config
        assert self.perm_manager._cache_enabled is True
        assert len(self.perm_manager._roles) == 4
        assert "admin" in self.perm_manager._roles
        assert "moderator" in self.perm_manager._roles
        assert "user" in self.perm_manager._roles
        assert "guest" in self.perm_manager._roles

    def test_permission_manager_initialization_invalid_file(self):
        """Test PermissionManager initialization with invalid file."""
        # Create config without roles_file to bypass pydantic validation
        config = PermissionConfig(permission_cache_enabled=True)
        config.roles_file = "nonexistent.json"

        with pytest.raises(PermissionConfigurationError):
            PermissionManager(config)

    def test_permission_manager_initialization_invalid_json(self):
        """Test PermissionManager initialization with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        config = PermissionConfig(roles_file=temp_file, permission_cache_enabled=True)

        with pytest.raises(PermissionConfigurationError):
            PermissionManager(config)

        Path(temp_file).unlink()

    def test_validate_access_success(self):
        """Test successful access validation."""
        result = self.perm_manager.validate_access(["admin"], ["read:*", "write:*"])

        assert result.is_valid is True
        assert result.status.value == "valid"

    def test_validate_access_with_inheritance(self):
        """Test access validation with role inheritance."""
        result = self.perm_manager.validate_access(
            ["moderator"], ["read:*", "write:posts", "moderate:comments"]
        )

        assert result.is_valid is True
        assert result.status.value == "valid"

    def test_validate_access_denied(self):
        """Test access validation when access is denied."""
        result = self.perm_manager.validate_access(
            ["guest"], ["write:posts", "delete:posts"]
        )

        assert result.is_valid is False
        assert result.status.value == "invalid"
        assert result.error_code == -32003
        assert "Missing permissions" in result.error_message

    def test_validate_access_no_roles(self):
        """Test access validation with no user roles."""
        result = self.perm_manager.validate_access([], ["read:posts"])

        assert result.is_valid is False
        assert result.status.value == "invalid"
        assert result.error_code == -32001
        assert result.error_message == "No user roles provided"

    def test_validate_access_no_permissions(self):
        """Test access validation with no required permissions."""
        result = self.perm_manager.validate_access(["admin"], [])

        assert result.is_valid is True
        assert result.status.value == "valid"

    def test_validate_access_invalid_role(self):
        """Test access validation with invalid role."""
        result = self.perm_manager.validate_access(["invalid_role"], ["read:posts"])

        assert result.is_valid is False
        assert result.status.value == "invalid"
        assert result.error_code == -32002
        assert "Invalid roles" in result.error_message

    def test_get_effective_permissions(self):
        """Test getting effective permissions for user roles."""
        permissions = self.perm_manager.get_effective_permissions(["admin"])

        assert "read:*" in permissions
        assert "write:*" in permissions
        assert "delete:*" in permissions
        assert "admin:*" in permissions

    def test_get_effective_permissions_with_inheritance(self):
        """Test getting effective permissions with role inheritance."""
        permissions = self.perm_manager.get_effective_permissions(["moderator"])

        # Direct permissions
        assert "read:*" in permissions
        assert "write:posts" in permissions
        assert "moderate:comments" in permissions

        # Inherited permissions from user role
        assert "read:posts" in permissions
        assert "read:comments" in permissions

    def test_get_effective_permissions_multiple_roles(self):
        """Test getting effective permissions for multiple roles."""
        permissions = self.perm_manager.get_effective_permissions(["user", "guest"])

        # User permissions
        assert "read:posts" in permissions
        assert "write:posts" in permissions
        assert "read:comments" in permissions

        # Guest permissions
        assert "read:posts" in permissions  # Duplicate, but should be in set

    def test_get_effective_permissions_invalid_role(self):
        """Test getting effective permissions with invalid role."""
        with pytest.raises(RoleNotFoundError):
            self.perm_manager.get_effective_permissions(["invalid_role"])

    def test_check_role_hierarchy(self):
        """Test role hierarchy checking."""
        # Direct inheritance
        assert self.perm_manager.check_role_hierarchy("moderator", "user") is True

        # Self inheritance
        assert self.perm_manager.check_role_hierarchy("admin", "admin") is True

        # No inheritance
        assert self.perm_manager.check_role_hierarchy("user", "admin") is False
        assert self.perm_manager.check_role_hierarchy("guest", "moderator") is False

    def test_check_role_hierarchy_invalid_roles(self):
        """Test role hierarchy checking with invalid roles."""
        with pytest.raises(RoleNotFoundError):
            self.perm_manager.check_role_hierarchy("invalid_role", "admin")

        with pytest.raises(RoleNotFoundError):
            self.perm_manager.check_role_hierarchy("admin", "invalid_role")

    def test_add_role_permission(self):
        """Test adding permission to role."""
        success = self.perm_manager.add_role_permission("user", "new:permission")

        assert success is True
        assert "new:permission" in self.perm_manager._roles["user"]["permissions"]

    def test_add_role_permission_already_exists(self):
        """Test adding permission that already exists."""
        # Add permission first time
        success1 = self.perm_manager.add_role_permission("user", "test:permission")
        assert success1 is True

        # Try to add same permission again
        success2 = self.perm_manager.add_role_permission("user", "test:permission")
        assert success2 is False

    def test_add_role_permission_invalid_role(self):
        """Test adding permission to invalid role."""
        with pytest.raises(RoleNotFoundError):
            self.perm_manager.add_role_permission("invalid_role", "test:permission")

    def test_remove_role_permission(self):
        """Test removing permission from role."""
        # Add permission first
        self.perm_manager.add_role_permission("user", "test:permission")

        # Remove permission
        success = self.perm_manager.remove_role_permission("user", "test:permission")

        assert success is True
        assert "test:permission" not in self.perm_manager._roles["user"]["permissions"]

    def test_remove_role_permission_not_exists(self):
        """Test removing permission that doesn't exist."""
        success = self.perm_manager.remove_role_permission(
            "user", "nonexistent:permission"
        )
        assert success is False

    def test_remove_role_permission_invalid_role(self):
        """Test removing permission from invalid role."""
        with pytest.raises(RoleNotFoundError):
            self.perm_manager.remove_role_permission("invalid_role", "test:permission")

    def test_reload_roles_configuration(self):
        """Test reloading roles configuration."""
        # Modify the temporary file
        new_config = {"new_role": {"permissions": ["new:permission"], "inherits": []}}

        with open(self.temp_file.name, "w") as f:
            json.dump(new_config, f)

        # Reload configuration
        success = self.perm_manager.reload_roles_configuration()

        assert success is True
        assert "new_role" in self.perm_manager._roles
        assert "new:permission" in self.perm_manager._roles["new_role"]["permissions"]
        assert "admin" not in self.perm_manager._roles  # Old roles should be gone

    def test_get_role_permissions(self):
        """Test getting direct permissions for a role."""
        permissions = self.perm_manager.get_role_permissions("admin")

        assert "read:*" in permissions
        assert "write:*" in permissions
        assert "delete:*" in permissions
        assert "admin:*" in permissions

    def test_get_role_permissions_invalid_role(self):
        """Test getting permissions for invalid role."""
        with pytest.raises(RoleNotFoundError):
            self.perm_manager.get_role_permissions("invalid_role")

    def test_get_all_roles(self):
        """Test getting all available roles."""
        roles = self.perm_manager.get_all_roles()

        assert "admin" in roles
        assert "moderator" in roles
        assert "user" in roles
        assert "guest" in roles
        assert len(roles) == 4

    def test_get_role_hierarchy(self):
        """Test getting role hierarchy."""
        hierarchy = self.perm_manager.get_role_hierarchy()

        assert hierarchy["admin"] == []
        assert hierarchy["moderator"] == ["user"]
        assert hierarchy["user"] == []
        assert hierarchy["guest"] == []

    def test_clear_cache(self):
        """Test clearing permission cache."""
        # Get permissions to populate cache
        self.perm_manager.get_effective_permissions(["admin"])

        # Clear cache
        self.perm_manager.clear_cache()

        assert len(self.perm_manager._permission_cache) == 0

    def test_permission_caching(self):
        """Test permission caching functionality."""
        # First call should populate cache
        permissions1 = self.perm_manager.get_effective_permissions(["admin"])

        # Second call should use cache
        permissions2 = self.perm_manager.get_effective_permissions(["admin"])

        assert permissions1 == permissions2
        assert len(self.perm_manager._permission_cache) > 0

    def test_wildcard_permission_matching(self):
        """Test wildcard permission matching."""
        # Test action wildcard
        result = self.perm_manager.validate_access(["user"], ["*:posts"])
        assert result.is_valid is True
        assert result.status.value == "valid"

        # Test resource wildcard
        result = self.perm_manager.validate_access(["admin"], ["read:*"])
        assert result.is_valid is True
        assert result.status.value == "valid"

        # Test no match
        result = self.perm_manager.validate_access(["guest"], ["write:*"])
        assert result.is_valid is False
        assert result.status.value == "invalid"

    def test_permission_manager_with_cache_disabled(self):
        """Test PermissionManager with caching disabled."""
        config = PermissionConfig(
            roles_file=self.temp_file.name, permission_cache_enabled=False
        )

        perm_manager = PermissionManager(config)

        # Get permissions multiple times
        permissions1 = perm_manager.get_effective_permissions(["admin"])
        permissions2 = perm_manager.get_effective_permissions(["admin"])

        assert permissions1 == permissions2
        assert len(perm_manager._permission_cache) == 0  # No caching


class TestPermissionManagerErrors:
    """Test suite for PermissionManager error handling."""

    def test_permission_configuration_error(self):
        """Test PermissionConfigurationError."""
        error = PermissionConfigurationError("Test error", error_code=-32001)

        assert error.message == "Test error"
        assert error.error_code == -32001
        assert str(error) == "Test error"

    def test_role_not_found_error(self):
        """Test RoleNotFoundError."""
        error = RoleNotFoundError("Role not found", error_code=-32002)

        assert error.message == "Role not found"
        assert error.error_code == -32002
        assert str(error) == "Role not found"

    def test_permission_validation_error(self):
        """Test PermissionValidationError."""
        error = PermissionValidationError("Validation failed", error_code=-32003)

        assert error.message == "Validation failed"
        assert error.error_code == -32003
        assert str(error) == "Validation failed"
