"""
User Info Middleware

This middleware extracts user information from authentication headers
and sets it in request.state for use by commands.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from mcp_proxy_adapter.core.logging import logger


class UserInfoMiddleware(BaseHTTPMiddleware):
    """
    Middleware for setting user information in request.state.
    
    This middleware extracts user information from authentication headers
    and sets it in request.state for use by commands.
    """
    
    def __init__(self, app, config: Dict[str, Any]):
        """
        Initialize user info middleware.
        
        Args:
            app: FastAPI application
            config: Configuration dictionary
        """
        super().__init__(app)
        self.config = config
        
        # Get API keys configuration
        security_config = config.get("security", {})
        auth_config = security_config.get("auth", {})
        self.api_keys = auth_config.get("api_keys", {})
        
        logger.info("User info middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process request and set user info in request.state.
        
        Args:
            request: Request object
            call_next: Next handler
            
        Returns:
            Response object
        """
        # Extract API key from headers
        api_key = request.headers.get("X-API-Key")
        
        if api_key and api_key in self.api_keys:
            # Get user info from API key configuration
            user_config = self.api_keys[api_key]
            
            # Set user info in request.state
            request.state.user = {
                "id": api_key,
                "role": user_config.get("roles", ["guest"])[0] if user_config.get("roles") else "guest",
                "roles": user_config.get("roles", ["guest"]),
                "permissions": user_config.get("permissions", ["read"])
            }
            
            logger.debug(f"Set user info for {api_key}: {request.state.user}")
        else:
            # Set default guest user info
            request.state.user = {
                "id": None,
                "role": "guest",
                "roles": ["guest"],
                "permissions": ["read"]
            }
            
            logger.debug("Set default guest user info")
        
        return await call_next(request)
