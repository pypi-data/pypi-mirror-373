"""
Client Security Module

This module provides client-side security integration for MCP Proxy Adapter,
using mcp_security_framework utilities for secure connections to servers.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
import ssl
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Import framework utilities
try:
    from mcp_security_framework.utils.crypto_utils import (
        generate_api_key, create_jwt_token, verify_jwt_token
    )
    from mcp_security_framework.utils.cert_utils import (
        parse_certificate, extract_roles_from_certificate,
        validate_certificate_chain, validate_certificate_format
    )
    from mcp_security_framework.core.ssl_manager import SSLManager
    from mcp_security_framework.schemas.config import SSLConfig, AuthConfig
    from mcp_security_framework.schemas.models import AuthResult, ValidationResult
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    SSLManager = None
    SSLConfig = None
    AuthConfig = None
    AuthResult = None
    ValidationResult = None

from mcp_proxy_adapter.core.logging import logger


class ClientSecurityManager:
    """
    Client-side security manager for MCP Proxy Adapter.
    
    Provides secure client connections using mcp_security_framework utilities.
    Handles authentication, certificate management, and SSL/TLS for client connections.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize client security manager.
        
        Args:
            config: Security configuration
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            raise ImportError("mcp_security_framework is not available")
        
        self.config = config
        self.security_config = config.get("security", {})
        
        # Initialize SSL manager if needed
        self.ssl_manager = None
        if self.security_config.get("ssl", {}).get("enabled", False):
            ssl_config = self._create_ssl_config()
            self.ssl_manager = SSLManager(ssl_config)
        
        logger.info("Client security manager initialized")
    
    def _create_ssl_config(self) -> SSLConfig:
        """Create SSL configuration for client connections."""
        ssl_section = self.security_config.get("ssl", {})
        
        return SSLConfig(
            enabled=ssl_section.get("enabled", False),
            cert_file=ssl_section.get("client_cert_file"),
            key_file=ssl_section.get("client_key_file"),
            ca_cert_file=ssl_section.get("ca_cert_file"),
            verify_mode=ssl_section.get("verify_mode", "CERT_REQUIRED"),
            min_tls_version=ssl_section.get("min_tls_version", "TLSv1.2"),
            check_hostname=ssl_section.get("check_hostname", True),
            check_expiry=ssl_section.get("check_expiry", True)
        )
    
    def create_client_ssl_context(self, server_hostname: Optional[str] = None) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for client connections.
        
        Args:
            server_hostname: Server hostname for SNI
            
        Returns:
            SSL context or None if SSL not enabled
        """
        if not self.ssl_manager:
            return None
        
        try:
            # Create client SSL context
            context = self.ssl_manager.create_client_context()
            
            if server_hostname:
                # Set server hostname for SNI
                context.check_hostname = True
                context.verify_mode = ssl.CERT_REQUIRED
            
            logger.info(f"Client SSL context created for {server_hostname or 'unknown server'}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create client SSL context: {e}")
            return None
    
    def generate_client_api_key(self, user_id: str, prefix: str = "mcp_proxy") -> str:
        """
        Generate API key for client authentication.
        
        Args:
            user_id: User identifier
            prefix: Key prefix
            
        Returns:
            Generated API key
        """
        try:
            api_key = generate_api_key(prefix=prefix)
            logger.info(f"Generated API key for user: {user_id}")
            return api_key
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            raise
    
    def create_client_jwt_token(self, user_id: str, roles: List[str], 
                               secret: str, algorithm: str = "HS256",
                               expiry_hours: int = 24) -> str:
        """
        Create JWT token for client authentication.
        
        Args:
            user_id: User identifier
            roles: User roles
            secret: JWT secret
            algorithm: JWT algorithm
            expiry_hours: Token expiry in hours
            
        Returns:
            JWT token
        """
        try:
            payload = {
                "user_id": user_id,
                "roles": roles,
                "type": "client_proxy"
            }
            
            token = create_jwt_token(
                payload=payload,
                secret=secret,
                algorithm=algorithm,
                expiry_hours=expiry_hours
            )
            
            logger.info(f"Created JWT token for user: {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise
    
    def validate_server_certificate(self, cert_path: str, ca_cert_path: Optional[str] = None) -> bool:
        """
        Validate server certificate before connection.
        
        Args:
            cert_path: Path to server certificate
            ca_cert_path: Path to CA certificate
            
        Returns:
            True if certificate is valid
        """
        try:
            # Validate certificate format
            if not validate_certificate_format(cert_path):
                logger.error(f"Invalid certificate format: {cert_path}")
                return False
            
            # Validate certificate chain if CA provided
            if ca_cert_path:
                if not validate_certificate_chain(cert_path, ca_cert_path):
                    logger.error(f"Invalid certificate chain: {cert_path}")
                    return False
            
            # Parse certificate and check basic properties
            cert_info = parse_certificate(cert_path)
            if not cert_info:
                logger.error(f"Failed to parse certificate: {cert_path}")
                return False
            
            logger.info(f"Server certificate validated: {cert_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate server certificate: {e}")
            return False
    
    def extract_server_roles(self, cert_path: str) -> List[str]:
        """
        Extract roles from server certificate.
        
        Args:
            cert_path: Path to server certificate
            
        Returns:
            List of roles extracted from certificate
        """
        try:
            roles = extract_roles_from_certificate(cert_path)
            logger.info(f"Extracted roles from server certificate: {roles}")
            return roles
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate: {e}")
            return []
    
    def get_client_auth_headers(self, auth_method: str = "api_key", **kwargs) -> Dict[str, str]:
        """
        Get authentication headers for client requests.
        
        Args:
            auth_method: Authentication method (api_key, jwt, certificate)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary of authentication headers
        """
        headers = {}
        
        try:
            if auth_method == "api_key":
                api_key = kwargs.get("api_key")
                if api_key:
                    headers["X-API-Key"] = api_key
                    headers["Authorization"] = f"Bearer {api_key}"
            
            elif auth_method == "jwt":
                token = kwargs.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            
            elif auth_method == "certificate":
                # Certificate authentication is handled at SSL level
                headers["X-Auth-Method"] = "certificate"
            
            # Add common proxy headers
            headers["X-Proxy-Type"] = "mcp_proxy_adapter"
            headers["X-Client-Type"] = "proxy_client"
            
            logger.debug(f"Created auth headers for method: {auth_method}")
            return headers
            
        except Exception as e:
            logger.error(f"Failed to create auth headers: {e}")
            return {}
    
    def prepare_client_connection(self, server_config: Dict[str, Any]) -> Tuple[Optional[ssl.SSLContext], Dict[str, str]]:
        """
        Prepare secure client connection to server.
        
        Args:
            server_config: Server connection configuration
            
        Returns:
            Tuple of (SSL context, auth headers)
        """
        ssl_context = None
        auth_headers = {}
        
        try:
            # Create SSL context if needed
            if server_config.get("ssl", False):
                server_hostname = server_config.get("hostname")
                ssl_context = self.create_client_ssl_context(server_hostname)
            
            # Create authentication headers
            auth_method = server_config.get("auth_method", "api_key")
            auth_headers = self.get_client_auth_headers(
                auth_method=auth_method,
                api_key=server_config.get("api_key"),
                token=server_config.get("token")
            )
            
            logger.info(f"Prepared client connection for {server_config.get('hostname', 'unknown')}")
            return ssl_context, auth_headers
            
        except Exception as e:
            logger.error(f"Failed to prepare client connection: {e}")
            return None, {}
    
    def validate_server_response(self, response_headers: Dict[str, str]) -> bool:
        """
        Validate server response for security compliance.
        
        Args:
            response_headers: Server response headers
            
        Returns:
            True if response is valid
        """
        try:
            # Check for required security headers
            required_headers = ["Content-Type"]
            for header in required_headers:
                if header not in response_headers:
                    logger.warning(f"Missing required header: {header}")
            
            # Check for security headers
            security_headers = ["X-Frame-Options", "X-Content-Type-Options"]
            for header in security_headers:
                if header in response_headers:
                    logger.debug(f"Found security header: {header}")
            
            # Validate content type
            content_type = response_headers.get("Content-Type", "")
            if "application/json" not in content_type:
                logger.warning(f"Unexpected content type: {content_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate server response: {e}")
            return False
    
    def get_client_certificate_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about client certificate.
        
        Returns:
            Certificate information or None
        """
        try:
            ssl_config = self.security_config.get("ssl", {})
            cert_path = ssl_config.get("client_cert_file")
            
            if not cert_path or not Path(cert_path).exists():
                return None
            
            cert_info = parse_certificate(cert_path)
            if cert_info:
                roles = extract_roles_from_certificate(cert_path)
                cert_info["roles"] = roles
                return cert_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get client certificate info: {e}")
            return None
    
    def is_ssl_enabled(self) -> bool:
        """Check if SSL is enabled for client connections."""
        return self.security_config.get("ssl", {}).get("enabled", False)
    
    def get_supported_auth_methods(self) -> List[str]:
        """Get list of supported authentication methods."""
        return ["api_key", "jwt", "certificate"]


# Factory function for easy integration
def create_client_security_manager(config: Dict[str, Any]) -> Optional[ClientSecurityManager]:
    """
    Create client security manager instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        ClientSecurityManager instance or None if framework not available
    """
    try:
        return ClientSecurityManager(config)
    except ImportError:
        logger.warning("mcp_security_framework not available, client security disabled")
        return None
    except Exception as e:
        logger.error(f"Failed to create client security manager: {e}")
        return None
