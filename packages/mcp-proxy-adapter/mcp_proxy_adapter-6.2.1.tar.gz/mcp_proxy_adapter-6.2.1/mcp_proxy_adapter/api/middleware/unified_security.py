"""
Unified Security Middleware - Direct Framework Integration

This middleware now directly uses mcp_security_framework components
instead of custom implementations.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import time
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Direct import from framework
try:
    from mcp_security_framework.middleware.fastapi_middleware import FastAPISecurityMiddleware
    from mcp_security_framework import SecurityManager
    from mcp_security_framework.schemas.config import SecurityConfig
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    FastAPISecurityMiddleware = None
    SecurityManager = None
    SecurityConfig = None

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.core.security_integration import create_security_integration


class SecurityValidationError(Exception):
    """Security validation error."""
    
    def __init__(self, message: str, error_code: int):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UnifiedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Unified security middleware using mcp_security_framework.
    
    This middleware now directly uses the security framework's FastAPI middleware
    and components instead of custom implementations.
    """
    
    def __init__(self, app, config: Dict[str, Any]):
        """
        Initialize unified security middleware.
        
        Args:
            app: FastAPI application
            config: mcp_proxy_adapter configuration dictionary
        """
        super().__init__(app)
        self.config = config
        
        # Create security integration
        try:
            self.security_integration = create_security_integration(config)
            # Use framework's FastAPI middleware
            self.framework_middleware = self.security_integration.create_fastapi_middleware(app)
            logger.info("Using mcp_security_framework FastAPI middleware")
        except Exception as e:
            logger.error(f"Security framework integration failed: {e}")
            # Instead of raising error, log warning and continue without security
            logger.warning("Continuing without security framework - some security features will be disabled")
            self.security_integration = None
            self.framework_middleware = None
        
        logger.info("Unified security middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process request using framework middleware.
        
        Args:
            request: Request object
            call_next: Next handler
            
        Returns:
            Response object
        """
        try:
            # Use framework middleware if available
            if self.framework_middleware is not None:
                return await self.framework_middleware.dispatch(request, call_next)
            else:
                # Fallback: continue without security middleware
                logger.debug("Security framework not available, continuing without security checks")
                return await call_next(request)
            
        except SecurityValidationError as e:
            # Handle security validation errors
            return await self._handle_security_error(request, e)
        except Exception as e:
            # Handle other errors
            logger.error(f"Unexpected error in unified security middleware: {e}")
            return await self._handle_general_error(request, e)
    

    
    async def _handle_security_error(self, request: Request, error: SecurityValidationError) -> Response:
        """
        Handle security validation errors.
        
        Args:
            request: Request object
            error: Security validation error
            
        Returns:
            Error response
        """
        from fastapi.responses import JSONResponse
        
        error_response = {
            "error": {
                "code": error.error_code,
                "message": error.message,
                "type": "security_validation_error"
            }
        }
        
        logger.warning(f"Security validation failed: {error.message}")
        
        return JSONResponse(
            status_code=error.error_code,
            content=error_response
        )
    
    async def _handle_general_error(self, request: Request, error: Exception) -> Response:
        """
        Handle general errors.
        
        Args:
            request: Request object
            error: General error
            
        Returns:
            Error response
        """
        from fastapi.responses import JSONResponse
        
        error_response = {
                "error": {
                "code": 500,
                    "message": "Internal server error",
                "type": "general_error"
            }
        }
        
        logger.error(f"General error in security middleware: {error}")
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
