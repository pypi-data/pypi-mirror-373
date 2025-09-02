"""
Certificate Management Command

This module provides commands for certificate management including creation,
validation, revocation, and information retrieval.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base import Command
from .result import CommandResult, SuccessResult, ErrorResult
from ..core.certificate_utils import CertificateUtils
from ..core.auth_validator import AuthValidator
from ..core.role_utils import RoleUtils

logger = logging.getLogger(__name__)


class CertificateResult:
    """
    Result class for certificate operations.
    
    Contains certificate information and operation status.
    """
    
    def __init__(self, cert_path: str, cert_type: str, common_name: str,
                 roles: Optional[List[str]] = None, expiry_date: Optional[str] = None,
                 serial_number: Optional[str] = None, status: str = "valid",
                 error: Optional[str] = None):
        """
        Initialize certificate result.
        
        Args:
            cert_path: Path to certificate file
            cert_type: Type of certificate (CA, server, client)
            common_name: Common name of the certificate
            roles: List of roles assigned to certificate
            expiry_date: Certificate expiry date
            serial_number: Certificate serial number
            status: Certificate status (valid, expired, revoked, error)
            error: Error message if any
        """
        self.cert_path = cert_path
        self.cert_type = cert_type
        self.common_name = common_name
        self.roles = roles or []
        self.expiry_date = expiry_date
        self.serial_number = serial_number
        self.status = status
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "cert_path": self.cert_path,
            "cert_type": self.cert_type,
            "common_name": self.common_name,
            "roles": self.roles,
            "expiry_date": self.expiry_date,
            "serial_number": self.serial_number,
            "status": self.status,
            "error": self.error
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for this result.
        
        Returns:
            JSON schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "cert_path": {"type": "string", "description": "Path to certificate file"},
                "cert_type": {"type": "string", "enum": ["CA", "server", "client"], 
                             "description": "Type of certificate"},
                "common_name": {"type": "string", "description": "Common name of certificate"},
                "roles": {"type": "array", "items": {"type": "string"}, 
                         "description": "List of roles assigned to certificate"},
                "expiry_date": {"type": "string", "description": "Certificate expiry date"},
                "serial_number": {"type": "string", "description": "Certificate serial number"},
                "status": {"type": "string", "enum": ["valid", "expired", "revoked", "error"], 
                          "description": "Certificate status"},
                "error": {"type": "string", "description": "Error message if any"}
            },
            "required": ["cert_path", "cert_type", "common_name", "status"]
        }


class CertificateManagementCommand(Command):
    """
    Command for certificate management.
    
    Provides methods for creating, managing, and validating certificates.
    """
    
    # Command metadata
    name = "certificate_management"
    version = "1.0.0"
    descr = "Certificate creation, validation, and management"
    category = "security"
    author = "MCP Proxy Adapter Team"
    email = "team@mcp-proxy-adapter.com"
    source_url = "https://github.com/mcp-proxy-adapter"
    result_class = CertificateResult
    
    def __init__(self):
        """Initialize certificate management command."""
        super().__init__()
        self.certificate_utils = CertificateUtils()
        self.auth_validator = AuthValidator()
        self.role_utils = RoleUtils()
    
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute certificate management command.
        
        Args:
            **kwargs: Command parameters including:
                - action: Action to perform (cert_create_ca, cert_create_server, cert_create_client, cert_revoke, cert_list, cert_info)
                - common_name: Common name for certificate creation
                - roles: List of roles for certificate creation
                - ca_cert_path: CA certificate path for server/client certificate creation
                - ca_key_path: CA key path for server/client certificate creation
                - output_dir: Output directory for certificate creation
                - validity_days: Certificate validity period in days
                - key_size: Key size in bits for CA certificate creation
                - cert_path: Certificate path for revocation and info
                - cert_dir: Directory for certificate listing
                
        Returns:
            CommandResult with certificate operation status
        """
        action = kwargs.get("action", "cert_list")
        
        if action == "cert_create_ca":
            common_name = kwargs.get("common_name")
            output_dir = kwargs.get("output_dir")
            validity_days = kwargs.get("validity_days", 365)
            key_size = kwargs.get("key_size", 2048)
            return await self.cert_create_ca(common_name, output_dir, validity_days, key_size)
        elif action == "cert_create_server":
            common_name = kwargs.get("common_name")
            roles = kwargs.get("roles", [])
            ca_cert_path = kwargs.get("ca_cert_path")
            ca_key_path = kwargs.get("ca_key_path")
            output_dir = kwargs.get("output_dir")
            validity_days = kwargs.get("validity_days", 365)
            return await self.cert_create_server(common_name, roles, ca_cert_path, ca_key_path, output_dir, validity_days)
        elif action == "cert_create_client":
            common_name = kwargs.get("common_name")
            roles = kwargs.get("roles", [])
            ca_cert_path = kwargs.get("ca_cert_path")
            ca_key_path = kwargs.get("ca_key_path")
            output_dir = kwargs.get("output_dir")
            validity_days = kwargs.get("validity_days", 365)
            return await self.cert_create_client(common_name, roles, ca_cert_path, ca_key_path, output_dir, validity_days)
        elif action == "cert_revoke":
            cert_path = kwargs.get("cert_path")
            return await self.cert_revoke(cert_path)
        elif action == "cert_list":
            cert_dir = kwargs.get("cert_dir", "/tmp")
            return await self.cert_list(cert_dir)
        elif action == "cert_info":
            cert_path = kwargs.get("cert_path")
            return await self.cert_info(cert_path)
        else:
            return ErrorResult(
                message=f"Unknown action: {action}. Supported actions: cert_create_ca, cert_create_server, cert_create_client, cert_revoke, cert_list, cert_info"
            )
    
    async def cert_create_ca(self, common_name: str, output_dir: str,
                           validity_days: int = 365, key_size: int = 2048) -> CommandResult:
        """
        Create a CA certificate and private key.
        
        Args:
            common_name: Common name for the CA certificate
            output_dir: Directory to save certificate and key files
            validity_days: Certificate validity period in days
            key_size: RSA key size in bits
            
        Returns:
            CommandResult with CA certificate creation status
        """
        try:
            logger.info(f"Creating CA certificate: {common_name}")
            
            # Validate parameters
            if not common_name or not common_name.strip():
                return ErrorResult(
                    message="Common name cannot be empty"
                )
            
            if validity_days <= 0:
                return ErrorResult(
                    message="Validity days must be positive"
                )
            
            if key_size < 1024:
                return ErrorResult(
                    message="Key size must be at least 1024 bits"
                )
            
            # Create CA certificate
            result = self.certificate_utils.create_ca_certificate(
                common_name, output_dir, validity_days, key_size
            )
            
            # Validate created certificate (CA certificates don't need server validation)
            cert_path = result.get("cert_path")
            if cert_path and os.path.exists(cert_path):
                # For CA certificates, we only check if the file exists and is readable
                try:
                    with open(cert_path, 'rb') as f:
                        cert_data = f.read()
                    if not cert_data:
                        return ErrorResult(
                            message="Created CA certificate file is empty"
                        )
                except Exception as e:
                    return ErrorResult(
                        message=f"Created CA certificate file is not readable: {str(e)}"
                    )
            
            cert_result = CertificateResult(
                cert_path=result.get("cert_path", ""),
                cert_type="CA",
                common_name=common_name,
                status="valid"
            )
            
            logger.info(f"CA certificate created successfully: {result.get('cert_path')}")
            return SuccessResult(
                data={
                    "certificate": cert_result.to_dict(),
                    "files": result
                }
            )
            
        except Exception as e:
            logger.error(f"CA certificate creation failed: {e}")
            return ErrorResult(
                message=f"CA certificate creation failed: {str(e)}"
            )
    
    async def cert_create_server(self, common_name: str, roles: List[str],
                               ca_cert_path: str, ca_key_path: str,
                               output_dir: str, validity_days: int = 365) -> CommandResult:
        """
        Create a server certificate signed by CA.
        
        Args:
            common_name: Common name for the server certificate
            roles: List of roles to assign to the certificate
            ca_cert_path: Path to CA certificate file
            ca_key_path: Path to CA private key file
            output_dir: Directory to save certificate and key files
            validity_days: Certificate validity period in days
            
        Returns:
            CommandResult with server certificate creation status
        """
        try:
            logger.info(f"Creating server certificate: {common_name}")
            
            # Validate parameters
            if not common_name or not common_name.strip():
                return ErrorResult(
                    message="Common name cannot be empty"
                )
            
            if not roles:
                return ErrorResult(
                    message="At least one role must be specified"
                )
            
            # Validate roles
            if not self.role_utils.validate_roles(roles):
                return ErrorResult(
                    message="Invalid roles specified"
                )
            
            # Check CA files
            if not os.path.exists(ca_cert_path):
                return ErrorResult(
                    message=f"CA certificate not found: {ca_cert_path}"
                )
            
            if not os.path.exists(ca_key_path):
                return ErrorResult(
                    message=f"CA private key not found: {ca_key_path}"
                )
            
            # Create server certificate
            result = self.certificate_utils.create_server_certificate(
                common_name, roles, ca_cert_path, ca_key_path, output_dir, validity_days
            )
            
            # Validate created certificate
            cert_path = result.get("cert_path")
            if cert_path and os.path.exists(cert_path):
                validation = self.auth_validator.validate_certificate(cert_path)
                if not validation.is_valid:
                    return ErrorResult(
                        message=f"Created server certificate validation failed: {validation.error_message}"
                    )
            
            cert_result = CertificateResult(
                cert_path=result.get("cert_path", ""),
                cert_type="server",
                common_name=common_name,
                roles=roles,
                status="valid"
            )
            
            logger.info(f"Server certificate created successfully: {result.get('cert_path')}")
            return SuccessResult(
                data={
                    "certificate": cert_result.to_dict(),
                    "files": result
                }
            )
            
        except Exception as e:
            logger.error(f"Server certificate creation failed: {e}")
            return ErrorResult(
                message=f"Server certificate creation failed: {str(e)}"
            )
    
    async def cert_create_client(self, common_name: str, roles: List[str],
                               ca_cert_path: str, ca_key_path: str,
                               output_dir: str, validity_days: int = 365) -> CommandResult:
        """
        Create a client certificate signed by CA.
        
        Args:
            common_name: Common name for the client certificate
            roles: List of roles to assign to the certificate
            ca_cert_path: Path to CA certificate file
            ca_key_path: Path to CA private key file
            output_dir: Directory to save certificate and key files
            validity_days: Certificate validity period in days
            
        Returns:
            CommandResult with client certificate creation status
        """
        try:
            logger.info(f"Creating client certificate: {common_name}")
            
            # Validate parameters
            if not common_name or not common_name.strip():
                return ErrorResult(
                    message="Common name cannot be empty"
                )
            
            if not roles:
                return ErrorResult(
                    message="At least one role must be specified"
                )
            
            # Validate roles
            if not self.role_utils.validate_roles(roles):
                return ErrorResult(
                    message="Invalid roles specified"
                )
            
            # Check CA files
            if not os.path.exists(ca_cert_path):
                return ErrorResult(
                    message=f"CA certificate not found: {ca_cert_path}"
                )
            
            if not os.path.exists(ca_key_path):
                return ErrorResult(
                    message=f"CA private key not found: {ca_key_path}"
                )
            
            # Create client certificate
            result = self.certificate_utils.create_client_certificate(
                common_name, roles, ca_cert_path, ca_key_path, output_dir, validity_days
            )
            
            # Validate created certificate
            cert_path = result.get("cert_path")
            if cert_path and os.path.exists(cert_path):
                validation = self.auth_validator.validate_certificate(cert_path)
                if not validation.is_valid:
                    return ErrorResult(
                        message=f"Created client certificate validation failed: {validation.error_message}"
                    )
            
            cert_result = CertificateResult(
                cert_path=result.get("cert_path", ""),
                cert_type="client",
                common_name=common_name,
                roles=roles,
                status="valid"
            )
            
            logger.info(f"Client certificate created successfully: {result.get('cert_path')}")
            return SuccessResult(
                data={
                    "certificate": cert_result.to_dict(),
                    "files": result
                }
            )
            
        except Exception as e:
            logger.error(f"Client certificate creation failed: {e}")
            return ErrorResult(
                message=f"Client certificate creation failed: {str(e)}"
            )
    
    async def cert_revoke(self, cert_path: str) -> CommandResult:
        """
        Revoke a certificate.
        
        Args:
            cert_path: Path to certificate file to revoke
            
        Returns:
            CommandResult with revocation status
        """
        try:
            logger.info(f"Revoking certificate: {cert_path}")
            
            # Validate parameters
            if not cert_path or not os.path.exists(cert_path):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_path}"
                )
            
            # Get certificate info before revocation
            cert_info = self.certificate_utils.get_certificate_info(cert_path)
            if not cert_info:
                return ErrorResult(
                    message="Could not read certificate information"
                )
            
            # Revoke certificate
            result = self.certificate_utils.revoke_certificate(cert_path)
            
            cert_result = CertificateResult(
                cert_path=cert_path,
                cert_type=cert_info.get("type", "unknown"),
                common_name=cert_info.get("common_name", ""),
                roles=cert_info.get("roles", []),
                serial_number=cert_info.get("serial_number"),
                status="revoked"
            )
            
            logger.info(f"Certificate revoked successfully: {cert_path}")
            return SuccessResult(
                data={
                    "certificate": cert_result.to_dict(),
                    "revocation_result": result
                }
            )
            
        except Exception as e:
            logger.error(f"Certificate revocation failed: {e}")
            return ErrorResult(
                message=f"Certificate revocation failed: {str(e)}"
            )
    
    async def cert_list(self, cert_dir: str) -> CommandResult:
        """
        List all certificates in a directory.
        
        Args:
            cert_dir: Directory to scan for certificates
            
        Returns:
            CommandResult with list of certificates
        """
        try:
            logger.info(f"Listing certificates in directory: {cert_dir}")
            
            # Validate parameters
            if not cert_dir or not os.path.exists(cert_dir):
                return ErrorResult(
                    message=f"Directory not found: {cert_dir}"
                )
            
            if not os.path.isdir(cert_dir):
                return ErrorResult(
                    message=f"Path is not a directory: {cert_dir}"
                )
            
            # List certificates
            certificates = []
            cert_extensions = ['.crt', '.pem', '.cer', '.der']
            
            for file_path in Path(cert_dir).rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in cert_extensions:
                    try:
                        cert_info = self.certificate_utils.get_certificate_info(str(file_path))
                        if cert_info:
                            cert_result = CertificateResult(
                                cert_path=str(file_path),
                                cert_type=cert_info.get("type", "unknown"),
                                common_name=cert_info.get("common_name", ""),
                                roles=cert_info.get("roles", []),
                                expiry_date=cert_info.get("expiry_date"),
                                serial_number=cert_info.get("serial_number"),
                                status=cert_info.get("status", "valid")
                            )
                            certificates.append(cert_result.to_dict())
                    except Exception as e:
                        logger.warning(f"Could not read certificate {file_path}: {e}")
                        # Add certificate with error status
                        cert_result = CertificateResult(
                            cert_path=str(file_path),
                            cert_type="unknown",
                            common_name="",
                            status="error",
                            error=str(e)
                        )
                        certificates.append(cert_result.to_dict())
            
            logger.info(f"Found {len(certificates)} certificates in {cert_dir}")
            return SuccessResult(
                data={
                    "certificates": certificates,
                    "total_count": len(certificates),
                    "directory": cert_dir
                }
            )
            
        except Exception as e:
            logger.error(f"Certificate listing failed: {e}")
            return ErrorResult(
                message=f"Certificate listing failed: {str(e)}"
            )
    
    async def cert_info(self, cert_path: str) -> CommandResult:
        """
        Get detailed information about a certificate.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            CommandResult with certificate information
        """
        try:
            logger.info(f"Getting certificate info: {cert_path}")
            
            # Validate parameters
            if not cert_path or not os.path.exists(cert_path):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_path}"
                )
            
            # Get certificate information
            cert_info = self.certificate_utils.get_certificate_info(cert_path)
            if not cert_info:
                return ErrorResult(
                    message="Could not read certificate information"
                )
            
            # Validate certificate
            validation = self.auth_validator.validate_certificate(cert_path)
            status = "valid" if validation.is_valid else "error"
            
            cert_result = CertificateResult(
                cert_path=cert_path,
                cert_type=cert_info.get("type", "unknown"),
                common_name=cert_info.get("common_name", ""),
                roles=cert_info.get("roles", []),
                expiry_date=cert_info.get("expiry_date"),
                serial_number=cert_info.get("serial_number"),
                status=status,
                error=None if validation.is_valid else validation.error_message
            )
            
            logger.info(f"Certificate info retrieved successfully: {cert_path}")
            return SuccessResult(
                data={
                    "certificate": cert_result.to_dict(),
                    "validation": {
                        "is_valid": validation.is_valid,
                        "error_code": validation.error_code,
                        "error_message": validation.error_message,
                        "roles": validation.roles
                    },
                    "details": cert_info
                }
            )
            
        except Exception as e:
            logger.error(f"Certificate info retrieval failed: {e}")
            return ErrorResult(
                message=f"Certificate info retrieval failed: {str(e)}"
            ) 