"""
Custom ASGI application for mTLS support.

This module provides a custom ASGI application that properly handles
client certificates in mTLS connections.
"""

import ssl
import logging
from typing import Dict, Any, Optional
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Send, Scope

logger = logging.getLogger(__name__)


class MTLSASGIApp:
    """
    Custom ASGI application that properly handles mTLS client certificates.
    
    This wrapper ensures that client certificates are properly extracted
    and made available to the FastAPI application.
    """
    
    def __init__(self, app: ASGIApp, ssl_config: Dict[str, Any]):
        """
        Initialize MTLS ASGI application.
        
        Args:
            app: The underlying ASGI application (FastAPI)
            ssl_config: SSL configuration for mTLS
        """
        self.app = app
        self.ssl_config = ssl_config
        self.verify_client = ssl_config.get("verify_client", False)
        self.client_cert_required = ssl_config.get("client_cert_required", False)
        
        logger.info(f"MTLS ASGI app initialized: verify_client={self.verify_client}, "
                   f"client_cert_required={self.client_cert_required}")
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handle ASGI request with mTLS support.
        
        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        try:
            # Extract client certificate from SSL context
            if scope["type"] == "http" and "ssl" in scope:
                client_cert = self._extract_client_certificate(scope)
                if client_cert:
                    # Store certificate in scope for middleware access
                    scope["client_certificate"] = client_cert
                    logger.debug(f"Client certificate extracted: {client_cert.get('subject', {})}")
                elif self.client_cert_required:
                    logger.warning("Client certificate required but not provided")
                    # Return 401 Unauthorized
                    await self._send_unauthorized_response(send)
                    return
            
            # Call the underlying application
            await self.app(scope, receive, send)
            
        except Exception as e:
            logger.error(f"Error in MTLS ASGI app: {e}")
            await self._send_error_response(send, str(e))
    
    def _extract_client_certificate(self, scope: Scope) -> Optional[Dict[str, Any]]:
        """
        Extract client certificate from SSL context.
        
        Args:
            scope: ASGI scope
            
        Returns:
            Client certificate data or None
        """
        try:
            ssl_context = scope.get("ssl")
            if not ssl_context:
                return None
            
            # Get peer certificate
            cert = ssl_context.getpeercert()
            if cert:
                return cert
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract client certificate: {e}")
            return None
    
    async def _send_unauthorized_response(self, send: Send) -> None:
        """
        Send 401 Unauthorized response.
        
        Args:
            send: ASGI send callable
        """
        response = {
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", b"163"),
            ],
        }
        await send(response)
        
        body = b'{"jsonrpc": "2.0", "error": {"code": -32001, "message": "Unauthorized: Client certificate required"}, "id": null}'
        await send({"type": "http.response.body", "body": body})
    
    async def _send_error_response(self, send: Send, error_message: str) -> None:
        """
        Send error response.
        
        Args:
            send: ASGI send callable
            error_message: Error message
        """
        response = {
            "type": "http.response.start",
            "status": 500,
            "headers": [
                (b"content-type", b"application/json"),
            ],
        }
        await send(response)
        
        body = f'{{"jsonrpc": "2.0", "error": {{"code": -32603, "message": "Internal error: {error_message}"}}, "id": null}}'.encode()
        await send({"type": "http.response.body", "body": body})


def create_mtls_asgi_app(app: ASGIApp, ssl_config: Dict[str, Any]) -> ASGIApp:
    """
    Create MTLS-enabled ASGI application.
    
    Args:
        app: The underlying ASGI application (FastAPI)
        ssl_config: SSL configuration for mTLS
        
    Returns:
        MTLS-enabled ASGI application
    """
    if ssl_config.get("mode") == "mtls" or ssl_config.get("verify_client", False):
        logger.info("Creating MTLS-enabled ASGI application")
        return MTLSASGIApp(app, ssl_config)
    else:
        logger.info("Creating standard ASGI application (no mTLS)")
        return app
