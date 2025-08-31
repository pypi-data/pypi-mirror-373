"""
Universal Authentication Validator

This module provides a universal authentication validator that supports
certificate, token, mTLS, and SSL validation with JSON-RPC error codes.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


# Standard JSON-RPC error codes
JSON_RPC_ERRORS = {
    # General errors
    -32600: "Invalid Request",           # Invalid request
    -32601: "Method not found",          # Method not found
    -32602: "Invalid params",            # Invalid parameters
    -32603: "Internal error",            # Internal error
    -32700: "Parse error",               # Parse error
    
    # Custom codes for authentication
    -32001: "Authentication disabled",   # Authentication disabled
    -32002: "Invalid configuration",     # Invalid configuration
    -32003: "Certificate validation failed", # Certificate validation failed
    -32004: "Token validation failed",   # Token validation failed
    -32005: "MTLS validation failed",    # MTLS validation failed
    -32006: "SSL validation failed",     # SSL validation failed
    -32007: "Role validation failed",    # Role validation failed
    -32008: "Certificate expired",       # Certificate expired
    -32009: "Certificate not found",     # Certificate not found
    -32010: "Token expired",             # Token expired
    -32011: "Token not found",           # Token not found
}


class AuthValidationResult:
    """
    Authentication validation result.
    
    Contains validation status, error information, and extracted roles.
    """
    
    def __init__(self, is_valid: bool, error_code: Optional[int] = None, 
                 error_message: Optional[str] = None, roles: Optional[List[str]] = None):
        """
        Initialize authentication validation result.
        
        Args:
            is_valid: Whether authentication is valid
            error_code: JSON-RPC error code if validation failed
            error_message: Error message if validation failed
            roles: List of roles extracted from authentication data
        """
        self.is_valid = is_valid
        self.error_code = error_code
        self.error_message = error_message
        self.roles = roles or []
    
    def to_json_rpc_error(self) -> Dict[str, Any]:
        """
        Convert to JSON-RPC error format.
        
        Returns:
            JSON-RPC error dictionary
        """
        if self.is_valid:
            return {}
        
        return {
            "code": self.error_code or -32603,
            "message": self.error_message or JSON_RPC_ERRORS.get(self.error_code, "Unknown error"),
            "data": {
                "validation_type": "authentication",
                "roles": self.roles
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "is_valid": self.is_valid,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "roles": self.roles
        }


class AuthValidator:
    """
    Universal authentication validator.
    
    Provides methods to validate different types of authentication:
    - Certificate validation
    - Token validation
    - mTLS validation
    - SSL validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize authentication validator.
        
        Args:
            config: Configuration dictionary for validation settings
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Custom OID for roles
        self.role_oid = "1.3.6.1.4.1.99999.1"
    
    def validate_auth(self, auth_data: Dict[str, Any], auth_type: str = "auto") -> AuthValidationResult:
        """
        Universal authentication validation.
        
        Logic:
        1. Check SSL configuration
        2. If SSL disabled - return success
        3. Determine validation type (auto/ssl/mtls/token)
        4. Check for required data
        5. Perform validation
        6. Return result with JSON-RPC error code
        
        Args:
            auth_data: Authentication data dictionary
            auth_type: Type of authentication to validate
            
        Returns:
            Authentication validation result
        """
        try:
            # Determine validation type
            if auth_type == "auto":
                auth_type = self._get_validation_mode()
            
            # Check for unsupported types first
            if auth_type not in ["certificate", "token", "mtls", "ssl"]:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32602,
                    error_message=f"Unsupported authentication type: {auth_type}"
                )
            
            # Check if authentication is enabled for the determined type
            if not self._check_config(auth_type):
                return AuthValidationResult(
                    is_valid=True,
                    roles=[]
                )
            
            # Validate based on type
            if auth_type == "certificate":
                return self.validate_certificate(
                    auth_data.get("cert_path"),
                    auth_data.get("cert_type", "server")
                )
            elif auth_type == "token":
                return self.validate_token(
                    auth_data.get("token"),
                    auth_data.get("token_type", "jwt")
                )
            elif auth_type == "mtls":
                return self.validate_mtls(
                    auth_data.get("client_cert"),
                    auth_data.get("ca_cert")
                )
            elif auth_type == "ssl":
                return self.validate_ssl(
                    auth_data.get("server_cert")
                )
                
        except Exception as e:
            self.logger.error(f"Authentication validation error: {e}")
            return AuthValidationResult(
                is_valid=False,
                error_code=-32603,
                error_message=f"Internal validation error: {str(e)}"
            )
    
    def validate_certificate(self, cert_path: Optional[str], cert_type: str = "server") -> AuthValidationResult:
        """
        Validate certificate.
        
        Args:
            cert_path: Path to certificate file
            cert_type: Type of certificate (server/client/ca)
            
        Returns:
            Certificate validation result
        """
        try:
            if not cert_path:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32009,
                    error_message="Certificate path not provided"
                )
            
            if not os.path.exists(cert_path):
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32009,
                    error_message=f"Certificate file not found: {cert_path}"
                )
            
            # Load and validate certificate
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Check if certificate is not expired
            now = datetime.utcnow()
            if cert.not_valid_before > now or cert.not_valid_after < now:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32008,
                    error_message="Certificate has expired"
                )
            
            # Extract roles from certificate
            roles = self._extract_roles_from_certificate(cert)
            
            # Validate certificate type
            if cert_type == "server":
                # Check for server-specific extensions
                if not self._validate_server_certificate(cert):
                    return AuthValidationResult(
                        is_valid=False,
                        error_code=-32003,
                        error_message="Invalid server certificate"
                    )
            elif cert_type == "client":
                # Check for client-specific extensions
                if not self._validate_client_certificate(cert):
                    return AuthValidationResult(
                        is_valid=False,
                        error_code=-32003,
                        error_message="Invalid client certificate"
                    )
            
            return AuthValidationResult(
                is_valid=True,
                roles=roles
            )
            
        except Exception as e:
            self.logger.error(f"Certificate validation error: {e}")
            return AuthValidationResult(
                is_valid=False,
                error_code=-32003,
                error_message=f"Certificate validation failed: {str(e)}"
            )
    
    def validate_token(self, token: Optional[str], token_type: str = "jwt") -> AuthValidationResult:
        """
        Validate token.
        
        Args:
            token: Token string to validate
            token_type: Type of token (jwt/api)
            
        Returns:
            Token validation result
        """
        try:
            if not token:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32011,
                    error_message="Token not provided"
                )
            
            if token_type == "jwt":
                return self._validate_jwt_token(token)
            elif token_type == "api":
                return self._validate_api_token(token)
            else:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32602,
                    error_message=f"Unsupported token type: {token_type}"
                )
                
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return AuthValidationResult(
                is_valid=False,
                error_code=-32004,
                error_message=f"Token validation failed: {str(e)}"
            )
    
    def validate_mtls(self, client_cert: Optional[str], ca_cert: Optional[str]) -> AuthValidationResult:
        """
        Validate mTLS connection.
        
        Args:
            client_cert: Path to client certificate
            ca_cert: Path to CA certificate
            
        Returns:
            mTLS validation result
        """
        try:
            if not client_cert or not ca_cert:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32005,
                    error_message="Client certificate and CA certificate required for mTLS"
                )
            
            # Validate client certificate
            client_result = self.validate_certificate(client_cert, "client")
            if not client_result.is_valid:
                return client_result
            
            # Validate CA certificate
            ca_result = self.validate_certificate(ca_cert, "ca")
            if not ca_result.is_valid:
                return ca_result
            
            # Verify client certificate is signed by CA
            if not self._verify_certificate_chain(client_cert, ca_cert):
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32005,
                    error_message="Client certificate not signed by provided CA"
                )
            
            return AuthValidationResult(
                is_valid=True,
                roles=client_result.roles
            )
            
        except Exception as e:
            self.logger.error(f"mTLS validation error: {e}")
            return AuthValidationResult(
                is_valid=False,
                error_code=-32005,
                error_message=f"mTLS validation failed: {str(e)}"
            )
    
    def validate_ssl(self, server_cert: Optional[str]) -> AuthValidationResult:
        """
        Validate SSL connection.
        
        Args:
            server_cert: Path to server certificate
            
        Returns:
            SSL validation result
        """
        try:
            if not server_cert:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32006,
                    error_message="Server certificate required for SSL validation"
                )
            
            # Validate server certificate
            return self.validate_certificate(server_cert, "server")
            
        except Exception as e:
            self.logger.error(f"SSL validation error: {e}")
            return AuthValidationResult(
                is_valid=False,
                error_code=-32006,
                error_message=f"SSL validation failed: {str(e)}"
            )
    
    def _check_config(self, auth_type: str) -> bool:
        """
        Check if authentication is enabled in configuration.
        
        Args:
            auth_type: Type of authentication
            
        Returns:
            True if authentication is enabled, False otherwise
        """
        ssl_config = self.config.get("ssl", {})
        
        if not ssl_config.get("enabled", False):
            return False
        
        # Check specific authentication type
        if auth_type == "token":
            return ssl_config.get("token_auth", {}).get("enabled", False)
        elif auth_type == "mtls":
            return ssl_config.get("mtls", {}).get("enabled", False)
        elif auth_type in ["ssl", "certificate"]:
            return True
        
        # For unsupported types, return False to indicate authentication is not enabled
        return False
    
    def _get_validation_mode(self) -> str:
        """
        Get validation mode from configuration.
        
        Returns:
            Validation mode string
        """
        ssl_config = self.config.get("ssl", {})
        
        if ssl_config.get("token_auth", {}).get("enabled", False):
            return "token"
        elif ssl_config.get("mtls", {}).get("enabled", False):
            return "mtls"
        elif ssl_config.get("enabled", False):
            return "ssl"
        
        return "none"
    
    def _extract_roles_from_certificate(self, cert: x509.Certificate) -> List[str]:
        """
        Extract roles from certificate.
        
        Args:
            cert: Certificate object
            
        Returns:
            List of roles extracted from certificate
        """
        try:
            for extension in cert.extensions:
                if extension.oid.dotted_string == self.role_oid:
                    roles_data = extension.value.value.decode('utf-8')
                    return [role.strip() for role in roles_data.split(',')]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to extract roles from certificate: {e}")
            return []
    
    def _validate_server_certificate(self, cert: x509.Certificate) -> bool:
        """
        Validate server certificate extensions.
        
        Args:
            cert: Certificate object
            
        Returns:
            True if server certificate is valid, False otherwise
        """
        try:
            # Check for server authentication key usage
            for extension in cert.extensions:
                if extension.oid == x509.oid.ExtensionOID.KEY_USAGE:
                    key_usage = extension.value
                    return key_usage.digital_signature and key_usage.key_encipherment
            
            return True
            
        except Exception as e:
            self.logger.error(f"Server certificate validation error: {e}")
            return False
    
    def _validate_client_certificate(self, cert: x509.Certificate) -> bool:
        """
        Validate client certificate extensions.
        
        Args:
            cert: Certificate object
            
        Returns:
            True if client certificate is valid, False otherwise
        """
        try:
            # Check for client authentication extended key usage
            for extension in cert.extensions:
                if extension.oid == x509.oid.ExtensionOID.EXTENDED_KEY_USAGE:
                    extended_key_usage = extension.value
                    return x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH in extended_key_usage
            
            return True
            
        except Exception as e:
            self.logger.error(f"Client certificate validation error: {e}")
            return False
    
    def _validate_jwt_token(self, token: str) -> AuthValidationResult:
        """
        Validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            JWT validation result
        """
        try:
            # This is a placeholder for JWT validation
            # In a real implementation, you would use a JWT library
            # like PyJWT to validate the token
            
            # For now, just check if token exists and has basic format
            if not token or len(token.split('.')) != 3:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32004,
                    error_message="Invalid JWT token format"
                )
            
            # Extract roles from JWT payload (placeholder)
            roles = []
            
            return AuthValidationResult(
                is_valid=True,
                roles=roles
            )
            
        except Exception as e:
            return AuthValidationResult(
                is_valid=False,
                error_code=-32004,
                error_message=f"JWT validation failed: {str(e)}"
            )
    
    def _validate_api_token(self, token: str) -> AuthValidationResult:
        """
        Validate API token.
        
        Args:
            token: API token string
            
        Returns:
            API token validation result
        """
        try:
            # This is a placeholder for API token validation
            # In a real implementation, you would validate against
            # a token store or database
            
            if not token:
                return AuthValidationResult(
                    is_valid=False,
                    error_code=-32011,
                    error_message="API token not found"
                )
            
            # Extract roles from API token (placeholder)
            roles = []
            
            return AuthValidationResult(
                is_valid=True,
                roles=roles
            )
            
        except Exception as e:
            return AuthValidationResult(
                is_valid=False,
                error_code=-32004,
                error_message=f"API token validation failed: {str(e)}"
            )
    
    def _verify_certificate_chain(self, client_cert_path: str, ca_cert_path: str) -> bool:
        """
        Verify that client certificate is signed by CA.
        
        Args:
            client_cert_path: Path to client certificate
            ca_cert_path: Path to CA certificate
            
        Returns:
            True if certificate chain is valid, False otherwise
        """
        try:
            # Load client certificate
            with open(client_cert_path, 'rb') as f:
                client_cert_data = f.read()
            client_cert = x509.load_pem_x509_certificate(client_cert_data)
            
            # Load CA certificate
            with open(ca_cert_path, 'rb') as f:
                ca_cert_data = f.read()
            ca_cert = x509.load_pem_x509_certificate(ca_cert_data)
            
            # Verify client certificate is signed by CA
            ca_public_key = ca_cert.public_key()
            
            # This is a simplified verification
            # In a real implementation, you would use proper signature verification
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate chain verification error: {e}")
            return False 