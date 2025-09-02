"""
Transport manager module.

This module provides transport management functionality for the MCP Proxy Adapter.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from mcp_proxy_adapter.core.logging import logger


class TransportType(Enum):
    """Transport types enumeration."""
    HTTP = "http"
    HTTPS = "https"
    MTLS = "mtls"


@dataclass
class TransportConfig:
    """Transport configuration data class."""
    type: TransportType
    port: Optional[int]
    ssl_enabled: bool
    cert_file: Optional[str]
    key_file: Optional[str]
    ca_cert: Optional[str]
    verify_client: bool
    client_cert_required: bool


class TransportManager:
    """
    Transport manager for handling different transport types.
    
    This class manages transport configuration and provides utilities
    for determining ports and SSL settings based on transport type.
    """
    
    # Default ports for transport types
    DEFAULT_PORTS = {
        TransportType.HTTP: 8000,
        TransportType.HTTPS: 8443,
        TransportType.MTLS: 9443
    }
    
    def __init__(self):
        """Initialize transport manager."""
        self._config: Optional[TransportConfig] = None
        self._current_transport: Optional[TransportType] = None
    
    def load_config(self, config: Dict[str, Any]) -> bool:
        """
        Load transport configuration from config dict.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if config loaded successfully, False otherwise
        """
        try:
            transport_config = config.get("transport", {})
            
            # Get transport type
            transport_type_str = transport_config.get("type", "http").lower()
            try:
                transport_type = TransportType(transport_type_str)
            except ValueError:
                logger.error(f"Invalid transport type: {transport_type_str}")
                return False
            
            # Get port (use default if not specified)
            port = transport_config.get("port")
            if port is None:
                port = self.DEFAULT_PORTS.get(transport_type, 8000)
            
            # Get SSL configuration
            ssl_config = transport_config.get("ssl", {})
            ssl_enabled = ssl_config.get("enabled", False)
            
            # Validate SSL requirements
            if transport_type in [TransportType.HTTPS, TransportType.MTLS] and not ssl_enabled:
                logger.error(f"SSL must be enabled for transport type: {transport_type.value}")
                return False
            
            if transport_type == TransportType.HTTP and ssl_enabled:
                logger.warning("SSL enabled for HTTP transport - this may cause issues")
            
            # Create transport config
            self._config = TransportConfig(
                type=transport_type,
                port=port,
                ssl_enabled=ssl_enabled,
                cert_file=ssl_config.get("cert_file") if ssl_enabled else None,
                key_file=ssl_config.get("key_file") if ssl_enabled else None,
                ca_cert=ssl_config.get("ca_cert") if ssl_enabled else None,
                verify_client=ssl_config.get("verify_client", False),
                client_cert_required=ssl_config.get("client_cert_required", False)
            )
            
            self._current_transport = transport_type
            
            logger.info(f"Transport config loaded: {transport_type.value} on port {port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load transport config: {e}")
            return False
    
    def get_transport_type(self) -> Optional[TransportType]:
        """
        Get current transport type.
        
        Returns:
            Current transport type or None if not configured
        """
        return self._current_transport
    
    def get_port(self) -> Optional[int]:
        """
        Get configured port.
        
        Returns:
            Port number or None if not configured
        """
        return self._config.port if self._config else None
    
    def is_ssl_enabled(self) -> bool:
        """
        Check if SSL is enabled.
        
        Returns:
            True if SSL is enabled, False otherwise
        """
        return self._config.ssl_enabled if self._config else False
    
    def get_ssl_config(self) -> Optional[Dict[str, Any]]:
        """
        Get SSL configuration.
        
        Returns:
            SSL configuration dict or None if SSL not enabled
        """
        if not self._config or not self._config.ssl_enabled:
            return None
        
        return {
            "cert_file": self._config.cert_file,
            "key_file": self._config.key_file,
            "ca_cert": self._config.ca_cert,
            "verify_client": self._config.verify_client,
            "client_cert_required": self._config.client_cert_required
        }
    
    def is_mtls(self) -> bool:
        """
        Check if current transport is MTLS.
        
        Returns:
            True if MTLS transport, False otherwise
        """
        return self._current_transport == TransportType.MTLS
    
    def is_https(self) -> bool:
        """
        Check if current transport is HTTPS.
        
        Returns:
            True if HTTPS transport, False otherwise
        """
        return self._current_transport == TransportType.HTTPS
    
    def is_http(self) -> bool:
        """
        Check if current transport is HTTP.
        
        Returns:
            True if HTTP transport, False otherwise
        """
        return self._current_transport == TransportType.HTTP
    
    def get_transport_info(self) -> Dict[str, Any]:
        """
        Get transport information.
        
        Returns:
            Dictionary with transport information
        """
        if not self._config:
            return {"error": "Transport not configured"}
        
        return {
            "type": self._config.type.value,
            "port": self._config.port,
            "ssl_enabled": self._config.ssl_enabled,
            "is_mtls": self.is_mtls(),
            "is_https": self.is_https(),
            "is_http": self.is_http(),
            "ssl_config": self.get_ssl_config()
        }
    
    def validate_config(self) -> bool:
        """
        Validate current transport configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self._config:
            logger.error("Transport not configured")
            return False
        
        # Validate SSL requirements
        if self._config.type in [TransportType.HTTPS, TransportType.MTLS]:
            if not self._config.ssl_enabled:
                logger.error(f"SSL must be enabled for {self._config.type.value}")
                return False
            
            if not self._config.cert_file or not self._config.key_file:
                logger.error(f"SSL certificate and key required for {self._config.type.value}")
                return False
        
        # Validate SSL files exist
        if not self.validate_ssl_files():
            return False
        
        # Validate MTLS requirements
        if self._config.type == TransportType.MTLS:
            if not self._config.verify_client:
                logger.warning("MTLS transport should have client verification enabled")
            
            if not self._config.ca_cert:
                logger.warning("CA certificate recommended for MTLS transport")
        
        logger.info(f"Transport configuration validated: {self._config.type.value}")
        return True
    
    def validate_ssl_files(self) -> bool:
        """
        Check if SSL files exist.
        
        Returns:
            True if all SSL files exist, False otherwise
        """
        if not self._config or not self._config.ssl_enabled:
            return True
        
        files_to_check = []
        if self._config.cert_file:
            files_to_check.append(self._config.cert_file)
        if self._config.key_file:
            files_to_check.append(self._config.key_file)
        if self._config.ca_cert:
            files_to_check.append(self._config.ca_cert)
        
        for file_path in files_to_check:
            if not Path(file_path).exists():
                logger.error(f"SSL file not found: {file_path}")
                return False
        
        logger.info(f"All SSL files validated successfully: {files_to_check}")
        return True
    
    def get_hypercorn_config(self) -> Dict[str, Any]:
        """
        Get configuration for hypercorn.
        
        Returns:
            Hypercorn configuration dictionary
        """
        config = {
            "host": "0.0.0.0",  # Can be moved to settings
            "port": self.get_port(),
            "log_level": "info"
        }
        
        if self.is_ssl_enabled():
            ssl_config = self.get_ssl_config()
            if ssl_config:
                from mcp_proxy_adapter.core.ssl_utils import SSLUtils
                hypercorn_ssl = SSLUtils.get_ssl_config_for_hypercorn(ssl_config)
                config.update(hypercorn_ssl)
        
        return config


# Global transport manager instance
transport_manager = TransportManager() 