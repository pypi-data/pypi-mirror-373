"""
MTLS ASGI Application Wrapper

This module provides an ASGI application wrapper that extracts client certificates
from the SSL context and makes them available to FastAPI middleware.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Version: 1.0.0
"""

import logging
import ssl
from typing import Dict, Any, Optional
from cryptography import x509

logger = logging.getLogger(__name__)


class MTLSASGIApp:
    """
    ASGI application wrapper for mTLS support.
    
    Extracts client certificates from SSL context and stores them in ASGI scope
    for access by FastAPI middleware.
    """
    
    def __init__(self, app, ssl_config: Dict[str, Any]):
        """
        Initialize MTLS ASGI app.
        
        Args:
            app: The underlying ASGI application
            ssl_config: SSL configuration dictionary
        """
        self.app = app
        self.ssl_config = ssl_config
        self.client_cert_required = ssl_config.get("client_cert_required", True)
        
        logger.info(f"MTLS ASGI app initialized: client_cert_required={self.client_cert_required}")
    
    async def __call__(self, scope: Dict[str, Any], receive, send):
        """
        Handle ASGI request with mTLS support.
        
        Args:
            scope: ASGI scope dictionary
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
    
    def _extract_client_certificate(self, scope: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract client certificate from SSL context.
        
        Args:
            scope: ASGI scope dictionary
            
        Returns:
            Certificate dictionary or None if not found
        """
        try:
            ssl_context = scope.get("ssl")
            if not ssl_context:
                logger.debug("No SSL context found in scope")
                return None
            
            # Try to get peer certificate
            if hasattr(ssl_context, 'getpeercert'):
                cert_data = ssl_context.getpeercert(binary_form=True)
                if cert_data:
                    # Parse certificate
                    cert = x509.load_der_x509_certificate(cert_data)
                    return self._cert_to_dict(cert)
                else:
                    logger.debug("No certificate data in SSL context")
                    return None
            else:
                logger.debug("SSL context has no getpeercert method")
                return None
                
        except Exception as e:
            logger.error(f"Failed to extract client certificate: {e}")
            return None
    
    def _cert_to_dict(self, cert: x509.Certificate) -> Dict[str, Any]:
        """
        Convert x509 certificate to dictionary.
        
        Args:
            cert: x509 certificate object
            
        Returns:
            Certificate dictionary
        """
        try:
            # Extract subject
            subject = {}
            for name in cert.subject:
                subject[name.oid._name] = name.value
            
            # Extract issuer
            issuer = {}
            for name in cert.issuer:
                issuer[name.oid._name] = name.value
            
            return {
                "subject": subject,
                "issuer": issuer,
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before.isoformat(),
                "not_valid_after": cert.not_valid_after.isoformat(),
                "version": cert.version.value,
                "signature_algorithm_oid": cert.signature_algorithm_oid._name,
                "public_key": {
                    "key_size": cert.public_key().key_size if hasattr(cert.public_key(), 'key_size') else None,
                    "public_numbers": str(cert.public_key().public_numbers()) if hasattr(cert.public_key(), 'public_numbers') else None
                }
            }
        except Exception as e:
            logger.error(f"Failed to convert certificate to dict: {e}")
            return {"error": str(e)}
    
    async def _send_unauthorized_response(self, send):
        """Send 401 Unauthorized response."""
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", b"0")
            ]
        })
        await send({
            "type": "http.response.body",
            "body": b""
        })
    
    async def _send_error_response(self, send, error_message: str):
        """Send error response."""
        body = f'{{"error": "{error_message}"}}'.encode('utf-8')
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode())
            ]
        })
        await send({
            "type": "http.response.body",
            "body": body
        })


def create_mtls_asgi_app(app, ssl_config: Dict[str, Any]):
    """
    Create MTLS ASGI application wrapper.
    
    Args:
        app: The underlying ASGI application
        ssl_config: SSL configuration dictionary
        
    Returns:
        MTLS ASGI app wrapper
    """
    return MTLSASGIApp(app, ssl_config)
