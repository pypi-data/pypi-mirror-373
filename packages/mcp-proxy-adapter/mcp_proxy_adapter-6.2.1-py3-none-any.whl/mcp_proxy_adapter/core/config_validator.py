"""
Configuration validator for strict validation before startup.

This module provides strict validation of configuration to prevent startup
with invalid or insecure configurations.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from mcp_proxy_adapter.core.logging import logger


class ConfigValidator:
    """
    Strict configuration validator.
    
    Validates configuration before startup and prevents startup
    with invalid or insecure configurations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize configuration validator.
        
        Args:
            config: Configuration dictionary to validate
        """
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """
        Validate all configuration sections.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Validate basic structure
        if not self._validate_basic_structure():
            return False
        
        # Validate server configuration
        if not self._validate_server_config():
            return False
        
        # Validate security configuration
        if not self._validate_security_config():
            return False
        
        # Validate commands configuration
        if not self._validate_commands_config():
            return False
        
        # Validate SSL configuration
        if not self._validate_ssl_config():
            return False
        
        # Validate roles configuration
        if not self._validate_roles_config():
            return False
        
        # Log warnings if any
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"Configuration warning: {warning}")
        
        # Return success only if no errors
        return len(self.errors) == 0
    
    def _validate_basic_structure(self) -> bool:
        """Validate basic configuration structure."""
        required_sections = ["server", "logging", "commands"]
        
        for section in required_sections:
            if section not in self.config:
                self.errors.append(f"Missing required configuration section: {section}")
        
        return len(self.errors) == 0
    
    def _validate_server_config(self) -> bool:
        """Validate server configuration."""
        server_config = self.config.get("server", {})
        
        # Validate host
        host = server_config.get("host")
        if not host:
            self.errors.append("Server host is required")
        
        # Validate port
        port = server_config.get("port")
        if not isinstance(port, int) or port < 1 or port > 65535:
            self.errors.append("Server port must be an integer between 1 and 65535")
        
        return len(self.errors) == 0
    
    def _validate_security_config(self) -> bool:
        """Validate security configuration."""
        security_config = self.config.get("security", {})
        
        # Check if security is enabled
        security_enabled = security_config.get("enabled", True)
        auth_enabled = self.config.get("auth_enabled", False)
        
        if security_enabled and auth_enabled:
            # Validate auth configuration
            auth_config = security_config.get("auth", {})
            if not auth_config.get("enabled", False):
                self.errors.append("Security is enabled but auth is disabled")
                return False
            
            # Validate API keys if auth is enabled
            if auth_config.get("enabled", False):
                api_keys = auth_config.get("api_keys", {})
                if not api_keys:
                    self.errors.append("API keys are required when authentication is enabled")
                    return False
                
                # Validate API key format
                for key, value in api_keys.items():
                    if not key or not value:
                        self.errors.append("API keys must have non-empty key and value")
                        return False
        
        return len(self.errors) == 0
    
    def _validate_commands_config(self) -> bool:
        """Validate commands configuration."""
        commands_config = self.config.get("commands", {})
        
        # Validate commands directory if auto_discovery is enabled
        if commands_config.get("auto_discovery", True):
            commands_dir = commands_config.get("commands_directory", "./commands")
            if not os.path.exists(commands_dir):
                self.warnings.append(f"Commands directory does not exist: {commands_dir}")
        
        return True
    
    def _validate_ssl_config(self) -> bool:
        """Validate SSL configuration."""
        ssl_config = self.config.get("ssl", {})
        ssl_enabled = ssl_config.get("enabled", False)
        
        if ssl_enabled:
            # Validate certificate files
            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            
            if not cert_file or not key_file:
                self.errors.append("SSL certificate and key files are required when SSL is enabled")
                return False
            
            if not os.path.exists(cert_file):
                self.errors.append(f"SSL certificate file not found: {cert_file}")
            
            if not os.path.exists(key_file):
                self.errors.append(f"SSL private key file not found: {key_file}")
        
        return len(self.errors) == 0
    
    def _validate_roles_config(self) -> bool:
        """Validate roles configuration."""
        roles_config = self.config.get("roles", {})
        roles_enabled = roles_config.get("enabled", False)
        
        if roles_enabled:
            config_file = roles_config.get("config_file")
            if not config_file:
                self.errors.append("Roles config file is required when roles are enabled")
                return False
            
            if not os.path.exists(config_file):
                self.errors.append(f"Roles config file not found: {config_file}")
                return False
            
            # Validate roles schema file
            try:
                with open(config_file, 'r') as f:
                    roles_schema = json.load(f)
                
                if "roles" not in roles_schema:
                    self.errors.append("Roles config file must contain 'roles' section")
                    return False
                
            except (json.JSONDecodeError, IOError) as e:
                self.errors.append(f"Failed to read roles config file: {e}")
                return False
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self.warnings.copy()
    
    def print_validation_report(self):
        """Print validation report."""
        if self.errors:
            logger.error("Configuration validation failed:")
            for error in self.errors:
                logger.error(f"  - {error}")
        
        if self.warnings:
            logger.warning("Configuration warnings:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            logger.info("Configuration validation passed")
