"""
Certificate Utilities

This module provides utilities for working with certificates including creation,
validation, and role extraction. Integrates with mcp_security_framework.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
import os
import ipaddress
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import mcp_security_framework
try:
    from mcp_security_framework.core.cert_manager import CertificateManager
    from mcp_security_framework.schemas.config import (
        CertificateConfig,
        CAConfig,
        ClientCertConfig,
        ServerCertConfig
    )
    from mcp_security_framework.schemas.models import CertificateType
    from mcp_security_framework.utils.cert_utils import (
        parse_certificate,
        extract_roles_from_certificate,
        extract_permissions_from_certificate,
        validate_certificate_chain,
        get_certificate_expiry
    )
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    # Fallback to cryptography if mcp_security_framework is not available
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

from .auth_validator import AuthValidator
from .role_utils import RoleUtils

logger = logging.getLogger(__name__)


class CertificateUtils:
    """
    Utilities for working with certificates.
    
    Provides methods for creating CA, server, and client certificates,
    as well as validation and role extraction using mcp_security_framework.
    """
    
    # Default certificate validity period (1 year)
    DEFAULT_VALIDITY_DAYS = 365
    
    # Default key size
    DEFAULT_KEY_SIZE = 2048
    
    # Custom OID for roles (same as in RoleUtils)
    ROLE_EXTENSION_OID = "1.3.6.1.4.1.99999.1"
    
    @staticmethod
    def create_ca_certificate(common_name: str, output_dir: str, 
                            validity_days: int = DEFAULT_VALIDITY_DAYS,
                            key_size: int = DEFAULT_KEY_SIZE) -> Dict[str, str]:
        """
        Create a CA certificate and private key using mcp_security_framework.
        
        Args:
            common_name: Common name for the CA certificate
            output_dir: Directory to save certificate and key files
            validity_days: Certificate validity period in days
            key_size: RSA key size in bits
            
        Returns:
            Dictionary with paths to created files
            
        Raises:
            ValueError: If parameters are invalid
            OSError: If files cannot be created
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return CertificateUtils._create_ca_certificate_fallback(
                common_name, output_dir, validity_days, key_size
            )
        
        try:
            # Validate parameters
            if not common_name or not common_name.strip():
                raise ValueError("Common name cannot be empty")
            
            if validity_days <= 0:
                raise ValueError("Validity days must be positive")
            
            if key_size < 1024:
                raise ValueError("Key size must be at least 1024 bits")
            
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Configure CA using mcp_security_framework
            ca_config = CAConfig(
                common_name=common_name,
                organization="MCP Proxy Adapter CA",
                organizational_unit="Certificate Authority",
                country="US",
                state="Default State",
                locality="Default City",
                validity_days=validity_days,
                key_size=key_size,
                key_type="RSA"
            )
            
            # Create certificate manager
            cert_config = CertificateConfig(
                output_dir=output_dir,
                ca_cert_path=str(Path(output_dir) / f"{common_name}.crt"),
                ca_key_path=str(Path(output_dir) / f"{common_name}.key")
            )
            
            cert_manager = CertificateManager(cert_config)
            
            # Generate CA certificate
            ca_pair = cert_manager.create_ca_certificate(ca_config)
            
            return {
                "cert_path": str(ca_pair.cert_path),
                "key_path": str(ca_pair.key_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to create CA certificate: {e}")
            raise
    
    @staticmethod
    def _create_ca_certificate_fallback(common_name: str, output_dir: str, 
                                      validity_days: int, key_size: int) -> Dict[str, str]:
        """Fallback method using cryptography directly."""
        try:
            # Validate parameters
            if not common_name or not common_name.strip():
                raise ValueError("Common name cannot be empty")
            
            if validity_days <= 0:
                raise ValueError("Validity days must be positive")
            
            if key_size < 1024:
                raise ValueError("Key size must be at least 1024 bits")
            
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Create certificate subject
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MCP Proxy Adapter CA"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Certificate Authority"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            ])
            
            # Create certificate
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now(timezone.utc)
            ).not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=validity_days)
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=True,
                    crl_sign=True,
                    digital_signature=True,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            ).sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            cert_path = Path(output_dir) / f"{common_name}.crt"
            key_path = Path(output_dir) / f"{common_name}.key"
            
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            return {
                "cert_path": str(cert_path),
                "key_path": str(key_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to create CA certificate (fallback): {e}")
            raise
    
    @staticmethod
    def create_server_certificate(common_name: str, roles: List[str],
                                ca_cert_path: str, ca_key_path: str,
                                output_dir: str,
                                validity_days: int = DEFAULT_VALIDITY_DAYS,
                                key_size: int = DEFAULT_KEY_SIZE) -> Dict[str, str]:
        """
        Create a server certificate signed by CA.
        
        Args:
            common_name: Common name for the server certificate
            roles: List of roles to include in certificate
            ca_cert_path: Path to CA certificate
            ca_key_path: Path to CA private key
            output_dir: Directory to save certificate and key files
            validity_days: Certificate validity period in days
            key_size: RSA key size in bits
            
        Returns:
            Dictionary with paths to created files
            
        Raises:
            ValueError: If parameters are invalid
            FileNotFoundError: If CA files not found
            OSError: If files cannot be created
        """
        try:
            # Validate parameters
            if not common_name or not common_name.strip():
                raise ValueError("Common name cannot be empty")
            
            if not roles:
                roles = ["server"]
            
            if not Path(ca_cert_path).exists():
                raise FileNotFoundError(f"CA certificate not found: {ca_cert_path}")
            
            if not Path(ca_key_path).exists():
                raise FileNotFoundError(f"CA key not found: {ca_key_path}")
            
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Load CA certificate and key
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())
            
            with open(ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Generate server private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MCP Proxy Adapter"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Server"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            ])
            
            # Create certificate
            cert_builder = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now(timezone.utc)
            ).not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=validity_days)
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=False,
                    crl_sign=False,
                    digital_signature=True,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                    content_commitment=False
                ),
                critical=True
            ).add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False
            ).add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                critical=False
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(common_name),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    x509.IPAddress(ipaddress.IPv6Address("::1"))
                ]),
                critical=False
            )
            
            # Add roles extension
            if roles:
                roles_data = ",".join(roles).encode('utf-8')
                roles_oid = x509.ObjectIdentifier(CertificateUtils.ROLE_EXTENSION_OID)
                cert_builder = cert_builder.add_extension(
                    x509.UnrecognizedExtension(roles_oid, roles_data),
                    critical=False
                )
            
            cert = cert_builder.sign(ca_key, hashes.SHA256())
            
            # Save certificate and key
            cert_path = os.path.join(output_dir, "server.crt")
            key_path = os.path.join(output_dir, "server.key")
            
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info(f"Server certificate created: {cert_path}")
            
            return {
                "cert_path": cert_path,
                "key_path": key_path,
                "common_name": common_name,
                "roles": roles,
                "validity_days": validity_days
            }
            
        except Exception as e:
            logger.error(f"Failed to create server certificate: {e}")
            raise
    
    @staticmethod
    def create_client_certificate(common_name: str, ca_cert_path: str, ca_key_path: str,
                                output_dir: str, roles: List[str] = None,
                                validity_days: int = DEFAULT_VALIDITY_DAYS,
                                key_size: int = DEFAULT_KEY_SIZE) -> Dict[str, str]:
        """
        Create a client certificate and private key using mcp_security_framework.
        
        Args:
            common_name: Common name for the client certificate
            ca_cert_path: Path to CA certificate
            ca_key_path: Path to CA private key
            output_dir: Directory to save certificate and key files
            roles: List of roles to include in certificate
            validity_days: Certificate validity period in days
            key_size: RSA key size in bits
            
        Returns:
            Dictionary with paths to created files
            
        Raises:
            ValueError: If parameters are invalid
            OSError: If files cannot be created
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return CertificateUtils._create_client_certificate_fallback(
                common_name, ca_cert_path, ca_key_path, output_dir, roles, validity_days, key_size
            )
        
        try:
            # Validate parameters
            if not common_name or not common_name.strip():
                raise ValueError("Common name cannot be empty")
            
            if not Path(ca_cert_path).exists():
                raise ValueError(f"CA certificate not found: {ca_cert_path}")
            
            if not Path(ca_key_path).exists():
                raise ValueError(f"CA private key not found: {ca_key_path}")
            
            if validity_days <= 0:
                raise ValueError("Validity days must be positive")
            
            if key_size < 1024:
                raise ValueError("Key size must be at least 1024 bits")
            
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Configure client certificate using mcp_security_framework
            client_config = ClientCertConfig(
                common_name=common_name,
                organization="MCP Proxy Adapter Client",
                organizational_unit="Client Certificates",
                country="US",
                state="Default State",
                locality="Default City",
                validity_days=validity_days,
                key_size=key_size,
                key_type="RSA",
                roles=roles or [],
                permissions=[]  # Permissions can be added later if needed
            )
            
            # Create certificate manager
            cert_config = CertificateConfig(
                output_dir=output_dir,
                ca_cert_path=ca_cert_path,
                ca_key_path=ca_key_path
            )
            
            cert_manager = CertificateManager(cert_config)
            
            # Generate client certificate
            client_pair = cert_manager.create_client_certificate(client_config)
            
            return {
                "cert_path": str(client_pair.cert_path),
                "key_path": str(client_pair.key_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to create client certificate: {e}")
            raise
    
    @staticmethod
    def _create_client_certificate_fallback(common_name: str, ca_cert_path: str, ca_key_path: str,
                                          output_dir: str, roles: List[str] = None,
                                          validity_days: int = DEFAULT_VALIDITY_DAYS,
                                          key_size: int = DEFAULT_KEY_SIZE) -> Dict[str, str]:
        """Fallback method using cryptography directly."""
        try:
            # Validate parameters
            if not common_name or not common_name.strip():
                raise ValueError("Common name cannot be empty")
            
            if not Path(ca_cert_path).exists():
                raise ValueError(f"CA certificate not found: {ca_cert_path}")
            
            if not Path(ca_key_path).exists():
                raise ValueError(f"CA private key not found: {ca_key_path}")
            
            if validity_days <= 0:
                raise ValueError("Validity days must be positive")
            
            if key_size < 1024:
                raise ValueError("Key size must be at least 1024 bits")
            
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Load CA certificate and key
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())
            
            with open(ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Generate client private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MCP Proxy Adapter Client"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Client Certificates"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            ])
            
            # Create certificate
            cert_builder = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now(timezone.utc)
            ).not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=validity_days)
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=False,
                    crl_sign=False,
                    digital_signature=True,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            ).add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
                critical=False
            )
            
            # Add roles extension if provided
            if roles:
                roles_str = ",".join(roles)
                roles_oid = x509.ObjectIdentifier(CertificateUtils.ROLE_EXTENSION_OID)
                cert_builder = cert_builder.add_extension(
                    x509.UnrecognizedExtension(roles_oid, roles_str.encode()),
                    critical=False
                )
            
            cert = cert_builder.sign(ca_key, hashes.SHA256())
            
            # Save certificate and key
            cert_path = Path(output_dir) / f"{common_name}.crt"
            key_path = Path(output_dir) / f"{common_name}.key"
            
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            return {
                "cert_path": str(cert_path),
                "key_path": str(key_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to create client certificate (fallback): {e}")
            raise
    
    @staticmethod
    def extract_roles_from_certificate(cert_path: str) -> List[str]:
        """
        Extract roles from certificate using mcp_security_framework.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            List of roles found in certificate
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return RoleUtils.extract_roles_from_certificate(cert_path)
        
        try:
            return extract_roles_from_certificate(cert_path)
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate: {e}")
            return []
    
    @staticmethod
    def extract_roles_from_certificate_object(cert) -> List[str]:
        """
        Extract roles from certificate object using mcp_security_framework.
        
        Args:
            cert: Certificate object
            
        Returns:
            List of roles found in certificate
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return RoleUtils.extract_roles_from_certificate_object(cert)
        
        try:
            # Convert certificate object to PEM format for mcp_security_framework
            cert_pem = cert.public_bytes(serialization.Encoding.PEM)
            return extract_roles_from_certificate(cert_pem)
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate object: {e}")
            return []
    
    @staticmethod
    def extract_permissions_from_certificate(cert_path: str) -> List[str]:
        """
        Extract permissions from certificate using mcp_security_framework.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            List of permissions found in certificate
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, permissions extraction not supported")
            return []
        
        try:
            return extract_permissions_from_certificate(cert_path)
        except Exception as e:
            logger.error(f"Failed to extract permissions from certificate: {e}")
            return []
    
    @staticmethod
    def validate_certificate_chain(cert_path: str, ca_cert_path: str) -> bool:
        """
        Validate certificate chain using mcp_security_framework.
        
        Args:
            cert_path: Path to certificate to validate
            ca_cert_path: Path to CA certificate
            
        Returns:
            True if chain is valid, False otherwise
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback validation")
            return CertificateUtils._validate_certificate_chain_fallback(cert_path, ca_cert_path)
        
        try:
            return validate_certificate_chain(cert_path, ca_cert_path)
        except Exception as e:
            logger.error(f"Failed to validate certificate chain: {e}")
            return False
    
    @staticmethod
    def _validate_certificate_chain_fallback(cert_path: str, ca_cert_path: str) -> bool:
        """Fallback certificate chain validation using cryptography."""
        try:
            # Load certificates
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())
            
            # Simple validation: check if certificate is issued by CA
            return cert.issuer == ca_cert.subject
            
        except Exception as e:
            logger.error(f"Failed to validate certificate chain (fallback): {e}")
            return False
    
    @staticmethod
    def get_certificate_expiry(cert_path: str) -> Optional[datetime]:
        """
        Get certificate expiry date using mcp_security_framework.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Certificate expiry date or None if not available
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return CertificateUtils._get_certificate_expiry_fallback(cert_path)
        
        try:
            expiry_info = get_certificate_expiry(cert_path)
            if isinstance(expiry_info, dict) and 'expiry_date' in expiry_info:
                return expiry_info['expiry_date']
            return None
        except Exception as e:
            logger.error(f"Failed to get certificate expiry: {e}")
            return None
    
    @staticmethod
    def _get_certificate_expiry_fallback(cert_path: str) -> Optional[datetime]:
        """Fallback method to get certificate expiry using cryptography."""
        try:
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            
            return cert.not_valid_after
            
        except Exception as e:
            logger.error(f"Failed to get certificate expiry (fallback): {e}")
            return None
    
    @staticmethod
    def validate_certificate(cert_path: str) -> bool:
        """
        Validate certificate using AuthValidator.
        
        Args:
            cert_path: Path to certificate to validate
            
        Returns:
            True if certificate is valid, False otherwise
        """
        try:
            validator = AuthValidator()
            result = validator.validate_certificate(cert_path)
            return result.is_valid
        except Exception as e:
            logger.error(f"Failed to validate certificate: {e}")
            return False
    
    @staticmethod
    def get_certificate_info(cert_path: str) -> Dict[str, Any]:
        """
        Get certificate information.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Dictionary with certificate information
        """
        try:
            with open(cert_path, "rb") as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Extract roles
            roles = CertificateUtils.extract_roles_from_certificate_object(cert)
            
            # Convert subject and issuer to dictionaries
            subject_dict = {}
            for name_attribute in cert.subject:
                subject_dict[str(name_attribute.oid)] = str(name_attribute.value)
            
            issuer_dict = {}
            for name_attribute in cert.issuer:
                issuer_dict[str(name_attribute.oid)] = str(name_attribute.value)
            
            return {
                "subject": subject_dict,
                "issuer": issuer_dict,
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before.isoformat(),
                "not_valid_after": cert.not_valid_after.isoformat(),
                "roles": roles,
                "is_ca": cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.BASIC_CONSTRAINTS
                ).value.ca if cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.BASIC_CONSTRAINTS
                ) else False
            }
            
        except Exception as e:
            logger.error(f"Failed to get certificate info: {e}")
            return {}

    @staticmethod
    def generate_private_key(key_type: str, key_size: int, output_path: str) -> Dict[str, Any]:
        """
        Generate a private key.
        
        Args:
            key_type: Type of key (RSA, ECDSA)
            key_size: Key size in bits
            output_path: Path to save the private key
            
        Returns:
            Dictionary with generation result
        """
        try:
            # Validate key type
            if key_type not in ["RSA", "ECDSA"]:
                return {
                    "success": False,
                    "error": "Key type must be RSA or ECDSA"
                }
            
            # Validate key size
            if key_type == "RSA" and key_size < 1024:
                return {
                    "success": False,
                    "error": "Key size must be at least 1024 bits"
                }
            
            if key_type == "ECDSA" and key_size not in [256, 384, 521]:
                return {
                    "success": False,
                    "error": "ECDSA key size must be 256, 384, or 521 bits"
                }
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate private key
            if key_type == "RSA":
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size
                )
            else:  # ECDSA
                from cryptography.hazmat.primitives.asymmetric import ec
                if key_size == 256:
                    curve = ec.SECP256R1()
                elif key_size == 384:
                    curve = ec.SECP384R1()
                else:  # 521
                    curve = ec.SECP521R1()
                
                private_key = ec.generate_private_key(curve)
            
            # Save private key
            with open(output_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            return {
                "success": True,
                "key_type": key_type,
                "key_size": key_size,
                "key_path": output_path
            }
            
        except Exception as e:
            logger.error(f"Failed to generate private key: {e}")
            return {
                "success": False,
                "error": f"Key generation failed: {str(e)}"
            }

    @staticmethod
    def validate_private_key(key_path: str) -> Dict[str, Any]:
        """
        Validate a private key.
        
        Args:
            key_path: Path to private key file
            
        Returns:
            Dictionary with validation result
        """
        try:
            if not os.path.exists(key_path):
                return {
                    "success": False,
                    "error": "Key file not found"
                }
            
            with open(key_path, "rb") as f:
                key_data = f.read()
            
            # Try to load the private key
            try:
                private_key = serialization.load_pem_private_key(key_data, password=None)
                
                # Get key info
                if isinstance(private_key, rsa.RSAPrivateKey):
                    key_type = "RSA"
                    key_size = private_key.key_size
                else:
                    key_type = "ECDSA"
                    key_size = private_key.key_size
                
                return {
                    "success": True,
                    "key_type": key_type,
                    "key_size": key_size,
                    "created_date": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Invalid private key: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Failed to validate private key: {e}")
            return {
                "success": False,
                "error": f"Key validation failed: {str(e)}"
            }

    @staticmethod
    def create_encrypted_backup(key_path: str, backup_path: str, password: str) -> Dict[str, Any]:
        """
        Create an encrypted backup of a private key.
        
        Args:
            key_path: Path to private key file
            backup_path: Path to save encrypted backup
            password: Password for encryption
            
        Returns:
            Dictionary with backup result
        """
        try:
            if not os.path.exists(key_path):
                return {
                    "success": False,
                    "error": "Key file not found"
                }
            
            # Read the private key
            with open(key_path, "rb") as f:
                key_data = f.read()
            
            # Load the private key
            private_key = serialization.load_pem_private_key(key_data, password=None)
            
            # Create encrypted backup
            encrypted_key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
            )
            
            # Save encrypted backup
            with open(backup_path, "wb") as f:
                f.write(encrypted_key)
            
            return {
                "success": True,
                "backup_path": backup_path
            }
            
        except Exception as e:
            logger.error(f"Failed to create encrypted backup: {e}")
            return {
                "success": False,
                "error": f"Encryption failed: {str(e)}"
            }

    @staticmethod
    def restore_encrypted_backup(backup_path: str, key_path: str, password: str) -> Dict[str, Any]:
        """
        Restore a private key from encrypted backup.
        
        Args:
            backup_path: Path to encrypted backup file
            key_path: Path to save restored key
            password: Password for decryption
            
        Returns:
            Dictionary with restore result
        """
        try:
            if not os.path.exists(backup_path):
                return {
                    "success": False,
                    "error": "Backup file not found"
                }
            
            # Read the encrypted backup
            with open(backup_path, "rb") as f:
                encrypted_data = f.read()
            
            # Load the encrypted private key
            private_key = serialization.load_pem_private_key(
                encrypted_data, 
                password=password.encode()
            )
            
            # Save the decrypted key
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            return {
                "success": True,
                "key_path": key_path
            }
            
        except Exception as e:
            logger.error(f"Failed to restore encrypted backup: {e}")
            return {
                "success": False,
                "error": f"Decryption failed: {str(e)}"
            }

    @staticmethod
    def create_ssl_context(cert_file: str, key_file: str, ca_file: Optional[str] = None) -> Any:
        """
        Create SSL context for server or client.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            ca_file: Path to CA certificate file (optional)
            
        Returns:
            SSL context object
        """
        try:
            import ssl
            
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Load certificate and key
            context.load_cert_chain(cert_file, key_file)
            
            # Load CA certificate if provided
            if ca_file and os.path.exists(ca_file):
                context.load_verify_locations(ca_file)
                context.verify_mode = ssl.CERT_REQUIRED
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            raise 