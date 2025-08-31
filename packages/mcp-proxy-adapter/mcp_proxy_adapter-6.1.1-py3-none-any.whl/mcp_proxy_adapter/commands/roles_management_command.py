"""
Roles Management Command

This module provides commands for managing roles in the role-based access control system.
Includes commands for listing, creating, updating, deleting, and validating roles.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base import Command
from .result import CommandResult, SuccessResult, ErrorResult
from ..core.role_utils import RoleUtils
from ..core.errors import ValidationError, NotFoundError, InternalError

logger = logging.getLogger(__name__)


class RolesListResult(SuccessResult):
    """
    Result for roles list command.
    """
    
    def __init__(self, roles: List[Dict[str, Any]], total_count: int):
        """
        Initialize roles list result.
        
        Args:
            roles: List of role configurations
            total_count: Total number of roles
        """
        super().__init__()
        self.success = True
        self.roles = roles
        self.total_count = total_count
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "roles": self.roles,
            "total_count": self.total_count
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result.
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "roles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "allowed_servers": {"type": "array", "items": {"type": "string"}},
                            "allowed_clients": {"type": "array", "items": {"type": "string"}},
                            "permissions": {"type": "array", "items": {"type": "string"}},
                            "priority": {"type": "integer"}
                        }
                    }
                },
                "total_count": {"type": "integer"}
            }
        }


class RolesCreateResult(SuccessResult):
    """
    Result for roles create command.
    """
    
    def __init__(self, role_name: str, role_config: Dict[str, Any]):
        """
        Initialize roles create result.
        
        Args:
            role_name: Name of created role
            role_config: Role configuration
        """
        super().__init__()
        self.success = True
        self.role_name = role_name
        self.role_config = role_config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "role_name": self.role_name,
            "role_config": self.role_config
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result.
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "role_name": {"type": "string"},
                "role_config": {"type": "object"}
            }
        }


class RolesUpdateResult(SuccessResult):
    """
    Result for roles update command.
    """
    
    def __init__(self, role_name: str, role_config: Dict[str, Any]):
        """
        Initialize roles update result.
        
        Args:
            role_name: Name of updated role
            role_config: Updated role configuration
        """
        super().__init__()
        self.success = True
        self.role_name = role_name
        self.role_config = role_config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "role_name": self.role_name,
            "role_config": self.role_config
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result.
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "role_name": {"type": "string"},
                "role_config": {"type": "object"}
            }
        }


class RolesDeleteResult(SuccessResult):
    """
    Result for roles delete command.
    """
    
    def __init__(self, role_name: str):
        """
        Initialize roles delete result.
        
        Args:
            role_name: Name of deleted role
        """
        super().__init__()
        self.success = True
        self.role_name = role_name
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "role_name": self.role_name
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result.
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "role_name": {"type": "string"}
            }
        }


class RolesValidateResult(SuccessResult):
    """
    Result for roles validate command.
    """
    
    def __init__(self, role_name: str, is_valid: bool, validation_errors: List[str]):
        """
        Initialize roles validate result.
        
        Args:
            role_name: Name of validated role
            is_valid: Whether role is valid
            validation_errors: List of validation errors
        """
        super().__init__()
        self.success = True
        self.role_name = role_name
        self.is_valid = is_valid
        self.validation_errors = validation_errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "role_name": self.role_name,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result.
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "role_name": {"type": "string"},
                "is_valid": {"type": "boolean"},
                "validation_errors": {"type": "array", "items": {"type": "string"}}
            }
        }


class RolesManagementCommand(Command):
    """
    Command for managing roles in the role-based access control system.
    """
    
    name = "roles_management"
    version = "1.0.0"
    descr = "Manage roles in the role-based access control system"
    category = "security"
    author = "MCP Proxy Adapter Team"
    email = "team@mcp-proxy-adapter.com"
    source_url = "https://github.com/mcp-proxy-adapter"
    
    def __init__(self, roles_config_path: str = "schemas/roles_schema.json"):
        """
        Initialize roles management command.
        
        Args:
            roles_config_path: Path to roles configuration file
        """
        self.roles_config_path = roles_config_path
        self.role_utils = RoleUtils()
        self.roles_config = self._load_roles_config()
    
    def _load_roles_config(self) -> Dict[str, Any]:
        """
        Load roles configuration from file.
        
        Returns:
            Roles configuration dictionary
        """
        try:
            config_path = Path(self.roles_config_path)
            if not config_path.exists():
                logger.warning(f"Roles config file not found: {self.roles_config_path}")
                return {"roles": {}, "server_roles": {}, "role_hierarchy": {}}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load roles configuration: {e}")
            return {"roles": {}, "server_roles": {}, "role_hierarchy": {}}
    
    def _save_roles_config(self) -> None:
        """
        Save roles configuration to file.
        """
        try:
            config_path = Path(self.roles_config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.roles_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Roles configuration saved to {self.roles_config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save roles configuration: {e}")
            raise InternalError(f"Failed to save roles configuration: {e}")
    
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute roles management command.
        
        Args:
            **kwargs: Command parameters including 'action' and role-specific parameters
            
        Returns:
            Command result
        """
        try:
            action = kwargs.get("action")
            
            if action == "list":
                return await self.roles_list(**kwargs)
            elif action == "create":
                return await self.roles_create(**kwargs)
            elif action == "update":
                return await self.roles_update(**kwargs)
            elif action == "delete":
                return await self.roles_delete(**kwargs)
            elif action == "validate":
                return await self.roles_validate(**kwargs)
            else:
                raise ValidationError(f"Invalid action: {action}. "
                                   f"Valid actions: list, create, update, delete, validate")
        
        except Exception as e:
            logger.error(f"Roles management command failed: {e}")
            return ErrorResult(str(e))
    
    async def roles_list(self, **kwargs) -> RolesListResult:
        """
        List all roles.
        
        Args:
            **kwargs: Additional parameters (filter, limit, offset)
            
        Returns:
            Roles list result
        """
        roles = self.roles_config.get("roles", {})
        
        # Apply filters if specified
        filter_name = kwargs.get("filter")
        if filter_name:
            roles = {name: config for name, config in roles.items() 
                    if filter_name.lower() in name.lower()}
        
        # Convert to list format
        roles_list = []
        for name, config in roles.items():
            role_info = {
                "name": name,
                "description": config.get("description", ""),
                "allowed_servers": config.get("allowed_servers", []),
                "allowed_clients": config.get("allowed_clients", []),
                "permissions": config.get("permissions", []),
                "priority": config.get("priority", 0)
            }
            roles_list.append(role_info)
        
        # Apply pagination
        limit = kwargs.get("limit")
        offset = kwargs.get("offset", 0)
        
        if limit:
            roles_list = roles_list[offset:offset + limit]
        elif offset:
            roles_list = roles_list[offset:]
        
        return RolesListResult(roles_list, len(roles))
    
    async def roles_create(self, **kwargs) -> RolesCreateResult:
        """
        Create a new role.
        
        Args:
            **kwargs: Role parameters (role_name, description, allowed_servers, etc.)
            
        Returns:
            Roles create result
        """
        role_name = kwargs.get("role_name")
        if not role_name:
            raise ValidationError("role_name is required")
        
        # Validate role name
        if not self.role_utils.validate_single_role(role_name):
            raise ValidationError(f"Invalid role name: {role_name}")
        
        # Check if role already exists
        if role_name in self.roles_config.get("roles", {}):
            raise ValidationError(f"Role {role_name} already exists")
        
        # Create role configuration
        role_config = {
            "description": kwargs.get("description", ""),
            "allowed_servers": kwargs.get("allowed_servers", []),
            "allowed_clients": kwargs.get("allowed_clients", []),
            "permissions": kwargs.get("permissions", []),
            "priority": kwargs.get("priority", 0)
        }
        
        # Validate role configuration
        validation_errors = self._validate_role_config(role_config)
        if validation_errors:
            raise ValidationError(f"Invalid role configuration: {', '.join(validation_errors)}")
        
        # Add role to configuration
        if "roles" not in self.roles_config:
            self.roles_config["roles"] = {}
        
        self.roles_config["roles"][role_name] = role_config
        
        # Save configuration
        self._save_roles_config()
        
        logger.info(f"Role {role_name} created successfully")
        return RolesCreateResult(role_name, role_config)
    
    async def roles_update(self, **kwargs) -> RolesUpdateResult:
        """
        Update an existing role.
        
        Args:
            **kwargs: Role parameters (role_name, description, allowed_servers, etc.)
            
        Returns:
            Roles update result
        """
        role_name = kwargs.get("role_name")
        if not role_name:
            raise ValidationError("role_name is required")
        
        # Check if role exists
        if role_name not in self.roles_config.get("roles", {}):
            raise NotFoundError(f"Role {role_name} not found")
        
        # Get existing configuration
        existing_config = self.roles_config["roles"][role_name]
        
        # Update configuration with new values
        updated_config = existing_config.copy()
        for key in ["description", "allowed_servers", "allowed_clients", "permissions", "priority"]:
            if key in kwargs:
                updated_config[key] = kwargs[key]
        
        # Validate updated configuration
        validation_errors = self._validate_role_config(updated_config)
        if validation_errors:
            raise ValidationError(f"Invalid role configuration: {', '.join(validation_errors)}")
        
        # Update role configuration
        self.roles_config["roles"][role_name] = updated_config
        
        # Save configuration
        self._save_roles_config()
        
        logger.info(f"Role {role_name} updated successfully")
        return RolesUpdateResult(role_name, updated_config)
    
    async def roles_delete(self, **kwargs) -> RolesDeleteResult:
        """
        Delete a role.
        
        Args:
            **kwargs: Role parameters (role_name)
            
        Returns:
            Roles delete result
        """
        role_name = kwargs.get("role_name")
        if not role_name:
            raise ValidationError("role_name is required")
        
        # Check if role exists
        if role_name not in self.roles_config.get("roles", {}):
            raise NotFoundError(f"Role {role_name} not found")
        
        # Check if role is system role
        if self.role_utils.is_system_role(role_name):
            raise ValidationError(f"Cannot delete system role: {role_name}")
        
        # Remove role from configuration
        del self.roles_config["roles"][role_name]
        
        # Remove from role hierarchy
        if "role_hierarchy" in self.roles_config:
            if role_name in self.roles_config["role_hierarchy"]:
                del self.roles_config["role_hierarchy"][role_name]
            
            # Remove from other roles' hierarchies
            for other_role, hierarchy in self.roles_config["role_hierarchy"].items():
                if role_name in hierarchy:
                    hierarchy.remove(role_name)
        
        # Save configuration
        self._save_roles_config()
        
        logger.info(f"Role {role_name} deleted successfully")
        return RolesDeleteResult(role_name)
    
    async def roles_validate(self, **kwargs) -> RolesValidateResult:
        """
        Validate a role configuration.
        
        Args:
            **kwargs: Role parameters (role_name or role_config)
            
        Returns:
            Roles validate result
        """
        role_name = kwargs.get("role_name")
        role_config = kwargs.get("role_config")
        
        if not role_name and not role_config:
            raise ValidationError("Either role_name or role_config is required")
        
        validation_errors = []
        
        if role_name:
            # Validate existing role
            if role_name not in self.roles_config.get("roles", {}):
                validation_errors.append(f"Role {role_name} not found")
            else:
                role_config = self.roles_config["roles"][role_name]
        
        if role_config:
            # Validate role configuration
            config_errors = self._validate_role_config(role_config)
            validation_errors.extend(config_errors)
        
        is_valid = len(validation_errors) == 0
        
        return RolesValidateResult(role_name or "unknown", is_valid, validation_errors)
    
    def _validate_role_config(self, role_config: Dict[str, Any]) -> List[str]:
        """
        Validate role configuration.
        
        Args:
            role_config: Role configuration to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate description
        description = role_config.get("description", "")
        if not isinstance(description, str):
            errors.append("description must be a string")
        
        # Validate allowed_servers
        allowed_servers = role_config.get("allowed_servers", [])
        if not isinstance(allowed_servers, list):
            errors.append("allowed_servers must be a list")
        else:
            for server in allowed_servers:
                if not isinstance(server, str):
                    errors.append("allowed_servers must contain only strings")
        
        # Validate allowed_clients
        allowed_clients = role_config.get("allowed_clients", [])
        if not isinstance(allowed_clients, list):
            errors.append("allowed_clients must be a list")
        else:
            for client in allowed_clients:
                if not isinstance(client, str):
                    errors.append("allowed_clients must contain only strings")
        
        # Validate permissions
        permissions = role_config.get("permissions", [])
        if not isinstance(permissions, list):
            errors.append("permissions must be a list")
        else:
            for permission in permissions:
                if not isinstance(permission, str):
                    errors.append("permissions must contain only strings")
        
        # Validate priority
        priority = role_config.get("priority", 0)
        if not isinstance(priority, int):
            errors.append("priority must be an integer")
        elif priority < 0:
            errors.append("priority must be non-negative")
        
        return errors
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "create", "update", "delete", "validate"],
                    "description": "Action to perform"
                },
                "role_name": {
                    "type": "string",
                    "description": "Name of the role"
                },
                "description": {
                    "type": "string",
                    "description": "Role description"
                },
                "allowed_servers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of allowed servers"
                },
                "allowed_clients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of allowed clients"
                },
                "permissions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of permissions"
                },
                "priority": {
                    "type": "integer",
                    "description": "Role priority"
                },
                "role_config": {
                    "type": "object",
                    "description": "Complete role configuration"
                },
                "filter": {
                    "type": "string",
                    "description": "Filter for list action"
                },
                "limit": {
                    "type": "integer",
                    "description": "Limit for list action"
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for list action"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        } 