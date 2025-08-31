"""
Role Test Command

This command tests role-based access control by checking user permissions.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult


logger = logging.getLogger(__name__)


class RoleTestCommandResult(SuccessResult):
    """Result for role test command."""
    
    def __init__(self, user_role: str, permissions: list, action: str, allowed: bool):
        """
        Initialize role test result.
        
        Args:
            user_role: User's role
            permissions: User's permissions
            action: Action being tested
            allowed: Whether action is allowed
        """
        super().__init__()
        self.user_role = user_role
        self.permissions = permissions
        self.action = action
        self.allowed = allowed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": True,
            "data": {
                "user_role": self.user_role,
                "permissions": self.permissions,
                "action": self.action,
                "allowed": self.allowed
            },
            "message": f"Action '{self.action}' {'allowed' if self.allowed else 'denied'} for role '{self.user_role}'"
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "user_role": {"type": "string"},
                        "permissions": {"type": "array", "items": {"type": "string"}},
                        "action": {"type": "string"},
                        "allowed": {"type": "boolean"}
                    }
                },
                "message": {"type": "string"}
            }
        }


class RoleTestCommand(Command):
    """Test role-based access control."""
    
    name = "roletest"
    descr = "Test role-based access control"
    category = "security"
    author = "Vasiliy Zdanovskiy"
    email = "vasilyvz@gmail.com"
    
    async def execute(self, **kwargs) -> RoleTestCommandResult:
        """
        Execute role test command.
        
        Args:
            **kwargs: Command parameters including context
            
        Returns:
            RoleTestCommandResult
        """
        # Extract parameters
        action = kwargs.get("action", "read")
        context = kwargs.get("context", {})
        
        # Get user info from context
        user_role = "guest"  # Default
        permissions = ["read"]  # Default
        
        if context:
            user_info = context.get("user", {})
            user_role = user_info.get("role", "guest")
            permissions = user_info.get("permissions", ["read"])
        
        # Check if action is allowed
        allowed = self._check_permission(action, permissions)
        
        logger.info(f"Role test: user={user_role}, action={action}, allowed={allowed}")
        
        return RoleTestCommandResult(user_role, permissions, action, allowed)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for command parameters."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to test",
                    "default": "read"
                }
            },
            "additionalProperties": False
        }
    
    def _check_permission(self, action: str, permissions: list) -> bool:
        """
        Check if action is allowed for given permissions.
        
        Args:
            action: Action to check
            permissions: User permissions
            
        Returns:
            True if allowed, False otherwise
        """
        # Admin has all permissions
        if "*" in permissions:
            return True
        
        # Check specific permission
        return action in permissions
