"""
Authentication Validation Commands

This module provides commands for validating different types of authentication:
- Universal authentication validation
- Certificate validation
- Token validation
- mTLS validation
- SSL validation

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional, Union

from ..commands.base import Command
from ..commands.result import SuccessResult, ErrorResult
from ..core.auth_validator import AuthValidator, AuthValidationResult


class AuthValidationCommand(Command):
    """
    Authentication validation commands.
    
    Provides commands for validating different types of authentication
    using the universal AuthValidator.
    """
    
    def __init__(self):
        """Initialize authentication validation command."""
        super().__init__()
        self.validator = AuthValidator()
        self.logger = logging.getLogger(__name__)
    
    async def auth_validate(self, auth_data: Dict[str, Any]) -> Union[SuccessResult, ErrorResult]:
        """
        Universal authentication validation.
        
        Validates authentication data based on the provided type.
        Supports certificate, token, mTLS, and SSL validation.
        
        Args:
            auth_data: Authentication data dictionary containing:
                - auth_type: Type of authentication (auto/certificate/token/mtls/ssl)
                - cert_path: Path to certificate file (for certificate/mtls/ssl)
                - cert_type: Type of certificate (server/client/ca)
                - token: Token string (for token validation)
                - token_type: Type of token (jwt/api)
                - client_cert: Path to client certificate (for mTLS)
                - ca_cert: Path to CA certificate (for mTLS)
                - server_cert: Path to server certificate (for SSL)
        
        Returns:
            CommandResult with validation status and extracted roles
        """
        try:
            auth_type = auth_data.get("auth_type", "auto")
            
            # Perform validation
            result = self.validator.validate_auth(auth_data, auth_type)
            
            if result.is_valid:
                return SuccessResult(
                    data={
                        "valid": True,
                        "roles": result.roles,
                        "auth_type": auth_type
                    }
                )
            else:
                error_data = result.to_json_rpc_error()
                return ErrorResult(
                    message=error_data["message"],
                    code=error_data["code"]
                )
                
        except Exception as e:
            self.logger.error(f"Authentication validation error: {e}")
            return ErrorResult(
                message=f"Internal authentication validation error: {str(e)}",
                code=-32603
            )
    
    async def auth_validate_cert(self, cert_path: str, cert_type: str = "server") -> Union[SuccessResult, ErrorResult]:
        """
        Validate certificate.
        
        Validates a certificate file and extracts roles if present.
        
        Args:
            cert_path: Path to certificate file
            cert_type: Type of certificate (server/client/ca)
        
        Returns:
            CommandResult with certificate validation status and roles
        """
        try:
            # Perform certificate validation
            result = self.validator.validate_certificate(cert_path, cert_type)
            
            if result.is_valid:
                return SuccessResult(
                    data={
                        "valid": True,
                        "cert_path": cert_path,
                        "cert_type": cert_type,
                        "roles": result.roles
                    }
                )
            else:
                error_data = result.to_json_rpc_error()
                return ErrorResult(
                    message=error_data["message"],
                    code=error_data["code"]
                )
                
        except Exception as e:
            self.logger.error(f"Certificate validation error: {e}")
            return ErrorResult(
                message=f"Internal certificate validation error: {str(e)}",
                code=-32603
            )
    
    async def auth_validate_token(self, token: str, token_type: str = "jwt") -> Union[SuccessResult, ErrorResult]:
        """
        Validate token.
        
        Validates a token and extracts roles if present.
        
        Args:
            token: Token string to validate
            token_type: Type of token (jwt/api)
        
        Returns:
            CommandResult with token validation status and roles
        """
        try:
            # Perform token validation
            result = self.validator.validate_token(token, token_type)
            
            if result.is_valid:
                return SuccessResult(
                    data={
                        "valid": True,
                        "token_type": token_type,
                        "roles": result.roles
                    }
                )
            else:
                error_data = result.to_json_rpc_error()
                return ErrorResult(
                    message=error_data["message"],
                    code=error_data["code"]
                )
                
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return ErrorResult(
                message=f"Internal token validation error: {str(e)}",
                code=-32603
            )
    
    async def auth_validate_mtls(self, client_cert: str, ca_cert: str) -> Union[SuccessResult, ErrorResult]:
        """
        Validate mTLS connection.
        
        Validates client certificate against CA certificate and extracts roles.
        
        Args:
            client_cert: Path to client certificate
            ca_cert: Path to CA certificate
        
        Returns:
            CommandResult with mTLS validation status and roles
        """
        try:
            # Perform mTLS validation
            result = self.validator.validate_mtls(client_cert, ca_cert)
            
            if result.is_valid:
                return SuccessResult(
                    data={
                        "valid": True,
                        "client_cert": client_cert,
                        "ca_cert": ca_cert,
                        "roles": result.roles
                    }
                )
            else:
                error_data = result.to_json_rpc_error()
                return ErrorResult(
                    message=error_data["message"],
                    code=error_data["code"]
                )
                
        except Exception as e:
            self.logger.error(f"mTLS validation error: {e}")
            return ErrorResult(
                message=f"Internal mTLS validation error: {str(e)}",
                code=-32603
            )
    
    async def auth_validate_ssl(self, server_cert: str) -> Union[SuccessResult, ErrorResult]:
        """
        Validate SSL connection.
        
        Validates server certificate and extracts roles if present.
        
        Args:
            server_cert: Path to server certificate
        
        Returns:
            CommandResult with SSL validation status and roles
        """
        try:
            # Perform SSL validation
            result = self.validator.validate_ssl(server_cert)
            
            if result.is_valid:
                return SuccessResult(
                    data={
                        "valid": True,
                        "server_cert": server_cert,
                        "roles": result.roles
                    }
                )
            else:
                error_data = result.to_json_rpc_error()
                return ErrorResult(
                    message=error_data["message"],
                    code=error_data["code"]
                )
                
        except Exception as e:
            self.logger.error(f"SSL validation error: {e}")
            return ErrorResult(
                message=f"Internal SSL validation error: {str(e)}",
                code=-32603
            )
    
    async def execute(self, **kwargs) -> Union[SuccessResult, ErrorResult]:
        """
        Execute authentication validation command.
        
        This is a placeholder method to satisfy the abstract base class.
        Individual validation methods should be called directly.
        
        Args:
            **kwargs: Command parameters
            
        Returns:
            Command result
        """
        return ErrorResult(
            message="Method not found. Use specific validation methods instead.",
            code=-32601
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get command schema for documentation.
        
        Returns:
            Dictionary containing command schema
        """
        return {
            "auth_validate": {
                "description": "Universal authentication validation",
                "parameters": {
                    "auth_data": {
                        "type": "object",
                        "description": "Authentication data dictionary",
                        "properties": {
                            "auth_type": {
                                "type": "string",
                                "enum": ["auto", "certificate", "token", "mtls", "ssl"],
                                "description": "Type of authentication to validate"
                            },
                            "cert_path": {
                                "type": "string",
                                "description": "Path to certificate file"
                            },
                            "cert_type": {
                                "type": "string",
                                "enum": ["server", "client", "ca"],
                                "description": "Type of certificate"
                            },
                            "token": {
                                "type": "string",
                                "description": "Token string to validate"
                            },
                            "token_type": {
                                "type": "string",
                                "enum": ["jwt", "api"],
                                "description": "Type of token"
                            },
                            "client_cert": {
                                "type": "string",
                                "description": "Path to client certificate (for mTLS)"
                            },
                            "ca_cert": {
                                "type": "string",
                                "description": "Path to CA certificate (for mTLS)"
                            },
                            "server_cert": {
                                "type": "string",
                                "description": "Path to server certificate (for SSL)"
                            }
                        }
                    }
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "roles": {"type": "array", "items": {"type": "string"}},
                        "auth_type": {"type": "string"}
                    }
                }
            },
            "auth_validate_cert": {
                "description": "Validate certificate",
                "parameters": {
                    "cert_path": {
                        "type": "string",
                        "description": "Path to certificate file"
                    },
                    "cert_type": {
                        "type": "string",
                        "enum": ["server", "client", "ca"],
                        "description": "Type of certificate"
                    }
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "cert_path": {"type": "string"},
                        "cert_type": {"type": "string"},
                        "roles": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "auth_validate_token": {
                "description": "Validate token",
                "parameters": {
                    "token": {
                        "type": "string",
                        "description": "Token string to validate"
                    },
                    "token_type": {
                        "type": "string",
                        "enum": ["jwt", "api"],
                        "description": "Type of token"
                    }
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "token_type": {"type": "string"},
                        "roles": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "auth_validate_mtls": {
                "description": "Validate mTLS connection",
                "parameters": {
                    "client_cert": {
                        "type": "string",
                        "description": "Path to client certificate"
                    },
                    "ca_cert": {
                        "type": "string",
                        "description": "Path to CA certificate"
                    }
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "client_cert": {"type": "string"},
                        "ca_cert": {"type": "string"},
                        "roles": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "auth_validate_ssl": {
                "description": "Validate SSL connection",
                "parameters": {
                    "server_cert": {
                        "type": "string",
                        "description": "Path to server certificate"
                    }
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "server_cert": {"type": "string"},
                        "roles": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        } 