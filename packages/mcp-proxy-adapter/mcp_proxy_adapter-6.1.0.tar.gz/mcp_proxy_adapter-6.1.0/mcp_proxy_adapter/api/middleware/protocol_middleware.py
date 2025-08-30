"""
Protocol middleware module.

This module provides middleware for validating protocol access based on configuration.
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.protocol_manager import protocol_manager
from mcp_proxy_adapter.core.logging import logger


class ProtocolMiddleware(BaseHTTPMiddleware):
    """
    Middleware for protocol validation.
    
    This middleware checks if the incoming request protocol is allowed
    based on the protocol configuration.
    """
    
    def __init__(self, app, protocol_manager_instance=None):
        """
        Initialize protocol middleware.
        
        Args:
            app: FastAPI application
            protocol_manager_instance: Protocol manager instance (optional)
        """
        super().__init__(app)
        self.protocol_manager = protocol_manager_instance or protocol_manager
    
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


def setup_protocol_middleware(app, protocol_manager_instance=None):
    """
    Setup protocol middleware for FastAPI application.
    
    Args:
        app: FastAPI application
        protocol_manager_instance: Protocol manager instance (optional)
    """
    if protocol_manager_instance is None:
        protocol_manager_instance = protocol_manager
    
    # Only add middleware if protocol management is enabled
    if protocol_manager_instance.enabled:
        app.add_middleware(ProtocolMiddleware, protocol_manager_instance=protocol_manager_instance)
        logger.info("Protocol middleware added to application")
    else:
        logger.debug("Protocol management is disabled, skipping protocol middleware") 