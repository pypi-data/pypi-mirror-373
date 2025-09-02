"""
Command Permission Middleware

This middleware checks permissions for specific commands based on user roles.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import json
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from mcp_proxy_adapter.core.logging import logger


class CommandPermissionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for checking command permissions.
    
    This middleware checks if the authenticated user has the required
    permissions to execute specific commands.
    """
    
    def __init__(self, app, config: Dict[str, Any]):
        """
        Initialize command permission middleware.
        
        Args:
            app: FastAPI application
            config: Configuration dictionary
        """
        super().__init__(app)
        self.config = config
        
        # Define command permissions
        self.command_permissions = {
            "echo": ["read"],
            "health": ["read"],
            "role_test": ["read"],
            "config": ["read"],
            "help": ["read"],
            # Add more commands as needed
        }
        
        logger.info("Command permission middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process request and check command permissions.
        
        Args:
            request: Request object
            call_next: Next handler
            
        Returns:
            Response object
        """
        # Only check permissions for /cmd endpoint
        if request.url.path != "/cmd":
            return await call_next(request)
        
        try:
            # Get request body
            body = await request.body()
            if not body:
                return await call_next(request)
            
            # Parse JSON-RPC request
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return await call_next(request)
            
            # Extract method (command name)
            method = data.get("method")
            if not method:
                return await call_next(request)
            
            # Check if method requires permissions
            if method not in self.command_permissions:
                return await call_next(request)
            
            required_permissions = self.command_permissions[method]
            
            # Get user info from request state
            user_info = getattr(request.state, "user", None)
            if not user_info:
                logger.warning(f"No user info found for command {method}")
                return await call_next(request)
            
            user_roles = user_info.get("roles", [])
            user_permissions = user_info.get("permissions", [])
            
            logger.debug(f"Checking permissions for {method}: user_roles={user_roles}, required={required_permissions}")
            
            # Check if user has required permissions
            has_permission = self._check_permissions(user_roles, user_permissions, required_permissions)
            
            if not has_permission:
                logger.warning(f"Permission denied for {method}: user_roles={user_roles}, required={required_permissions}")
                
                # Return permission denied response
                error_response = {
                    "error": {
                        "code": 403,
                        "message": f"Permission denied: {method} requires {required_permissions}",
                        "type": "permission_denied"
                    }
                }
                
                return Response(
                    content=json.dumps(error_response),
                    status_code=403,
                    media_type="application/json"
                )
            
            logger.debug(f"Permission granted for {method}")
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Error in command permission middleware: {e}")
            return await call_next(request)
    
    def _check_permissions(self, user_roles: list, user_permissions: list, required_permissions: list) -> bool:
        """
        Check if user has required permissions.
        
        Args:
            user_roles: User roles
            user_permissions: User permissions
            required_permissions: Required permissions
            
        Returns:
            True if user has required permissions
        """
        # Admin has all permissions
        if "admin" in user_roles or "*" in user_permissions:
            return True
        
        # Check if user has all required permissions
        for required in required_permissions:
            if required not in user_permissions:
                return False
        
        return True
