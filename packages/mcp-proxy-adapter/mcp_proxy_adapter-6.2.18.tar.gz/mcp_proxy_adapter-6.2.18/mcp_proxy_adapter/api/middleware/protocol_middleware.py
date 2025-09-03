"""
Protocol middleware module.

This module provides middleware for validating protocol access based on configuration.
"""

from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.protocol_manager import get_protocol_manager
from mcp_proxy_adapter.core.logging import logger


class ProtocolMiddleware(BaseHTTPMiddleware):
    """
    Middleware for protocol validation.
    
    This middleware checks if the incoming request protocol is allowed
    based on the protocol configuration.
    """
    
    def __init__(self, app, app_config: Optional[Dict[str, Any]] = None):
        """
        Initialize protocol middleware.
        
        Args:
            app: FastAPI application
            app_config: Application configuration dictionary (optional)
        """
        super().__init__(app)
        self.app_config = app_config
        # Get protocol manager with current configuration
        self.protocol_manager = get_protocol_manager(app_config)
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        Update configuration and reload protocol manager.
        
        Args:
            new_config: New configuration dictionary
        """
        self.app_config = new_config
        self.protocol_manager = get_protocol_manager(new_config)
        logger.info("Protocol middleware configuration updated")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through protocol middleware.
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint function
            
        Returns:
            Response object
        """
        try:
            # Get protocol from request
            protocol = self._get_request_protocol(request)
            
            # Check if protocol is allowed
            if not self.protocol_manager.is_protocol_allowed(protocol):
                logger.warning(f"Protocol '{protocol}' not allowed for request to {request.url.path}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Protocol not allowed",
                        "message": f"Protocol '{protocol}' is not allowed. Allowed protocols: {self.protocol_manager.get_allowed_protocols()}",
                        "allowed_protocols": self.protocol_manager.get_allowed_protocols()
                    }
                )
            
            # Continue processing
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Protocol middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Protocol validation error",
                    "message": str(e)
                }
            )
    
    def _get_request_protocol(self, request: Request) -> str:
        """
        Extract protocol from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Protocol name (http, https, mtls)
        """
        # Check if request is secure (HTTPS)
        if request.url.scheme:
            scheme = request.url.scheme.lower()
            
            # If HTTPS, check if client certificate is provided (MTLS)
            if scheme == "https":
                # Check for client certificate in headers or SSL context
                if hasattr(request, 'scope') and 'ssl' in request.scope:
                    ssl_context = request.scope.get('ssl')
                    if ssl_context and hasattr(ssl_context, 'getpeercert'):
                        try:
                            cert = ssl_context.getpeercert()
                            if cert:
                                return "mtls"
                        except:
                            pass
                
                # Check for client certificate in headers
                if request.headers.get("ssl-client-cert") or request.headers.get("x-client-cert"):
                    return "mtls"
                
                return "https"
            
            return scheme
        
        # Fallback to checking headers
        if request.headers.get("x-forwarded-proto"):
            return request.headers.get("x-forwarded-proto").lower()
        
        # Default to HTTP
        return "http"


def setup_protocol_middleware(app, app_config: Optional[Dict[str, Any]] = None):
    """
    Setup protocol middleware for FastAPI application.
    
    Args:
        app: FastAPI application
        app_config: Application configuration dictionary (optional)
    """
    # Check if protocol management is enabled
    if app_config is None:
        from mcp_proxy_adapter.config import config
        app_config = config.get_all()
    
    protocols_config = app_config.get("protocols", {})
    enabled = protocols_config.get("enabled", True)
    
    if enabled:
        # Create protocol middleware with current configuration
        middleware = ProtocolMiddleware(app, app_config)
        app.add_middleware(ProtocolMiddleware, app_config=app_config)
        logger.info("Protocol middleware added to application")
    else:
        logger.info("Protocol management is disabled, skipping protocol middleware") 