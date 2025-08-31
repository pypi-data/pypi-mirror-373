"""
Transport Middleware Module

This module provides middleware for transport validation in the MCP Proxy Adapter.
"""

from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from mcp_proxy_adapter.core.transport_manager import transport_manager
from mcp_proxy_adapter.core.logging import logger


class TransportMiddleware(BaseHTTPMiddleware):
    """Middleware for transport validation."""
    
    def __init__(self, app, transport_manager_instance=None):
        """
        Initialize transport middleware.
        
        Args:
            app: FastAPI application
            transport_manager_instance: Transport manager instance (optional)
        """
        super().__init__(app)
        self.transport_manager = transport_manager_instance or transport_manager
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through transport middleware.
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint
            
        Returns:
            Response from next middleware/endpoint or error response
        """
        # Determine transport type from request
        transport_type = self._get_request_transport_type(request)
        
        # Check if request matches configured transport
        if not self._is_transport_allowed(transport_type):
            configured_type = self.transport_manager.get_transport_type()
            configured_type_str = configured_type.value if configured_type else "not configured"
            logger.warning(f"Transport not allowed: {transport_type} for {request.url}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Transport not allowed",
                    "message": f"Transport '{transport_type}' is not allowed. Configured transport: {configured_type_str}",
                    "configured_transport": configured_type_str,
                    "request_url": str(request.url)
                }
            )
        
        # Add transport info to request state
        request.state.transport_type = transport_type
        request.state.transport_allowed = True
        
        response = await call_next(request)
        return response
    
    def _get_request_transport_type(self, request: Request) -> str:
        """
        Determine transport type from request.
        
        Args:
            request: Incoming request
            
        Returns:
            Transport type string
        """
        if request.url.scheme == "https":
            # Check for client certificate for MTLS
            if self._has_client_certificate(request):
                return "mtls"
            return "https"
        return "http"
    
    def _has_client_certificate(self, request: Request) -> bool:
        """
        Check if request has client certificate.
        
        Args:
            request: Incoming request
            
        Returns:
            True if client certificate is present, False otherwise
        """
        # Check for client certificate in request headers or SSL context
        # This is a simplified check - in production, you might need more sophisticated detection
        client_cert_header = request.headers.get("ssl-client-cert")
        if client_cert_header:
            return True
        
        # Check if request has SSL client certificate context
        if hasattr(request, "client") and request.client:
            # In a real implementation, you would check the SSL context
            # For now, we'll assume HTTPS with client cert is MTLS
            return self.transport_manager.is_mtls()
        
        return False
    
    def _is_transport_allowed(self, transport_type: str) -> bool:
        """
        Check if transport type is allowed.
        
        Args:
            transport_type: Transport type to check
            
        Returns:
            True if transport is allowed, False otherwise
        """
        configured_type = self.transport_manager.get_transport_type()
        if not configured_type:
            logger.error("Transport not configured")
            return False
        
        return transport_type == configured_type.value 