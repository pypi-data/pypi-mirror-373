"""
SSL Utilities Module

This module provides utilities for SSL/TLS configuration and certificate validation.
Integrates with AuthValidator from Phase 0 for certificate validation.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import ssl
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .auth_validator import AuthValidator

logger = logging.getLogger(__name__)


class SSLUtils:
    """
    SSL utilities for creating SSL contexts and validating certificates.
    """
    
    # TLS version mapping
    TLS_VERSIONS = {
        "1.0": ssl.TLSVersion.TLSv1,
        "1.1": ssl.TLSVersion.TLSv1_1,
        "1.2": ssl.TLSVersion.TLSv1_2,
        "1.3": ssl.TLSVersion.TLSv1_3
    }
    
    # Cipher suite mapping
    CIPHER_SUITES = {
        "TLS_AES_256_GCM_SHA384": "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256": "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256": "TLS_AES_128_GCM_SHA256",
        "ECDHE-RSA-AES256-GCM-SHA384": "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES128-GCM-SHA256": "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-RSA-CHACHA20-POLY1305": "ECDHE-RSA-CHACHA20-POLY1305"
    }
    
    @staticmethod
    def create_ssl_context(cert_file: str, key_file: str, 
                          ca_cert: Optional[str] = None, 
                          verify_client: bool = False,
                          cipher_suites: Optional[List[str]] = None,
                          min_tls_version: str = "1.2",
                          max_tls_version: str = "1.3") -> ssl.SSLContext:
        """
        Create SSL context with specified configuration.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            ca_cert: Path to CA certificate file (optional)
            verify_client: Whether to verify client certificates
            cipher_suites: List of cipher suites to use
            min_tls_version: Minimum TLS version
            max_tls_version: Maximum TLS version
            
        Returns:
            Configured SSL context
            
        Raises:
            ValueError: If certificate validation fails
            FileNotFoundError: If certificate or key files not found
        """
        # Validate certificate using AuthValidator
        validator = AuthValidator()
        result = validator.validate_certificate(cert_file)
        if not result.is_valid:
            raise ValueError(f"Invalid certificate: {result.error_message}")
        
        # Check if files exist
        if not Path(cert_file).exists():
            raise FileNotFoundError(f"Certificate file not found: {cert_file}")
        if not Path(key_file).exists():
            raise FileNotFoundError(f"Key file not found: {key_file}")
        if ca_cert and not Path(ca_cert).exists():
            raise FileNotFoundError(f"CA certificate file not found: {ca_cert}")
        
        # Create SSL context
        if verify_client:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        else:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        # Load certificate and key
        context.load_cert_chain(cert_file, key_file)
        
        # Load CA certificate if provided
        if ca_cert:
            context.load_verify_locations(ca_cert)
        
        # Configure client verification
        if verify_client:
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = False
        else:
            context.verify_mode = ssl.CERT_NONE
        
        # Setup cipher suites
        SSLUtils.setup_cipher_suites(context, cipher_suites or [])
        
        # Setup TLS versions
        SSLUtils.setup_tls_versions(context, min_tls_version, max_tls_version)
        
        logger.info(f"SSL context created successfully with cert: {cert_file}")
        return context
    
    @staticmethod
    def validate_certificate(cert_file: str) -> bool:
        """
        Validate certificate using AuthValidator.
        
        Args:
            cert_file: Path to certificate file
            
        Returns:
            True if certificate is valid, False otherwise
        """
        try:
            validator = AuthValidator()
            result = validator.validate_certificate(cert_file)
            return result.is_valid
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return False
    
    @staticmethod
    def setup_cipher_suites(context: ssl.SSLContext, cipher_suites: List[str]) -> None:
        """
        Setup cipher suites for SSL context.
        
        Args:
            context: SSL context to configure
            cipher_suites: List of cipher suite names
        """
        if not cipher_suites:
            return
        
        # Convert cipher suite names to actual cipher suite strings
        actual_ciphers = []
        for cipher_name in cipher_suites:
            if cipher_name in SSLUtils.CIPHER_SUITES:
                actual_ciphers.append(SSLUtils.CIPHER_SUITES[cipher_name])
            else:
                logger.warning(f"Unknown cipher suite: {cipher_name}")
        
        if actual_ciphers:
            try:
                context.set_ciphers(":".join(actual_ciphers))
                logger.info(f"Cipher suites configured: {actual_ciphers}")
            except ssl.SSLError as e:
                logger.error(f"Failed to set cipher suites: {e}")
    
    @staticmethod
    def setup_tls_versions(context: ssl.SSLContext, min_version: str, max_version: str) -> None:
        """
        Setup TLS version range for SSL context.
        
        Args:
            context: SSL context to configure
            min_version: Minimum TLS version
            max_version: Maximum TLS version
        """
        try:
            min_tls = SSLUtils.TLS_VERSIONS.get(min_version)
            max_tls = SSLUtils.TLS_VERSIONS.get(max_version)
            
            if min_tls and max_tls:
                context.minimum_version = min_tls
                context.maximum_version = max_tls
                logger.info(f"TLS versions configured: {min_version} - {max_version}")
            else:
                logger.warning(f"Invalid TLS version range: {min_version} - {max_version}")
        except Exception as e:
            logger.error(f"Failed to set TLS versions: {e}")
    
    @staticmethod
    def check_tls_version(min_version: str, max_version: str) -> bool:
        """
        Check if TLS version range is valid.
        
        Args:
            min_version: Minimum TLS version
            max_version: Maximum TLS version
            
        Returns:
            True if version range is valid, False otherwise
        """
        min_tls = SSLUtils.TLS_VERSIONS.get(min_version)
        max_tls = SSLUtils.TLS_VERSIONS.get(max_version)
        
        if not min_tls or not max_tls:
            return False
        
        # Check if min version is less than or equal to max version
        return min_tls <= max_tls
    
    @staticmethod
    def get_ssl_config_for_hypercorn(ssl_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get SSL configuration for hypercorn from transport configuration.
        
        Args:
            ssl_config: SSL configuration from transport manager
            
        Returns:
            Configuration for hypercorn
        """
        hypercorn_ssl = {}
        
        if not ssl_config:
            return hypercorn_ssl
        
        # Basic SSL parameters
        if ssl_config.get("cert_file"):
            hypercorn_ssl["certfile"] = ssl_config["cert_file"]
        
        if ssl_config.get("key_file"):
            hypercorn_ssl["keyfile"] = ssl_config["key_file"]
        
        if ssl_config.get("ca_cert"):
            hypercorn_ssl["ca_certs"] = ssl_config["ca_cert"]
        
        # Client verification mode
        if ssl_config.get("verify_client", False):
            hypercorn_ssl["verify_mode"] = "CERT_REQUIRED"
        
        logger.info(f"Generated hypercorn SSL config: {hypercorn_ssl}")
        return hypercorn_ssl 