"""
Security Factory for creating security components.

This module provides factory methods for creating security adapters, managers,
and middleware components with proper configuration and error handling.
"""

import logging
from typing import Dict, Any, Optional

from mcp_proxy_adapter.core.logging import logger
from .security_adapter import SecurityAdapter


class SecurityFactory:
    """
    Factory for creating security components.
    
    Provides static methods to create security adapters, managers,
    and middleware components with proper configuration handling.
    """
    
    @staticmethod
    def create_security_adapter(config: Dict[str, Any]) -> SecurityAdapter:
        """
        Create SecurityAdapter from configuration.
        
        Args:
            config: mcp_proxy_adapter configuration dictionary
            
        Returns:
            SecurityAdapter instance
        """
        try:
            adapter = SecurityAdapter(config)
            logger.info("Security adapter created successfully")
            return adapter
        except Exception as e:
            logger.error(f"Failed to create security adapter: {e}")
            raise
    
    @staticmethod
    def create_security_manager(config: Dict[str, Any]):
        """
        Create SecurityManager from configuration.
        
        Args:
            config: mcp_proxy_adapter configuration dictionary
            
        Returns:
            SecurityManager instance or None if not available
        """
        try:
            adapter = SecurityFactory.create_security_adapter(config)
            return adapter.security_manager
        except Exception as e:
            logger.error(f"Failed to create security manager: {e}")
            return None
    
    @staticmethod
    def create_middleware(config: Dict[str, Any], framework: str = "fastapi"):
        """
        Create framework-specific security middleware.
        
        Args:
            config: mcp_proxy_adapter configuration dictionary
            framework: Framework type (fastapi, flask, etc.)
            
        Returns:
            Middleware instance or None if creation failed
        """
        try:
            adapter = SecurityFactory.create_security_adapter(config)
            middleware = adapter.create_middleware(framework)
            
            if middleware:
                logger.info(f"Security middleware created for {framework}")
            else:
                logger.warning(f"Failed to create security middleware for {framework}")
            
            return middleware
            
        except Exception as e:
            logger.error(f"Failed to create security middleware: {e}")
            return None
    
    @staticmethod
    def create_fastapi_middleware(config: Dict[str, Any]):
        """
        Create FastAPI-specific security middleware.
        
        Args:
            config: mcp_proxy_adapter configuration dictionary
            
        Returns:
            FastAPI middleware instance or None if creation failed
        """
        return SecurityFactory.create_middleware(config, "fastapi")
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate security configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check if security section exists
            security_config = config.get("security", {})
            
            # Validate required fields
            if not isinstance(security_config, dict):
                logger.error("Security configuration must be a dictionary")
                return False
            
            # Validate auth configuration
            auth_config = security_config.get("auth", {})
            if not isinstance(auth_config, dict):
                logger.error("Auth configuration must be a dictionary")
                return False
            
            # Validate SSL configuration
            ssl_config = security_config.get("ssl", {})
            if not isinstance(ssl_config, dict):
                logger.error("SSL configuration must be a dictionary")
                return False
            
            # Validate permissions configuration
            permissions_config = security_config.get("permissions", {})
            if not isinstance(permissions_config, dict):
                logger.error("Permissions configuration must be a dictionary")
                return False
            
            # Validate rate limit configuration
            rate_limit_config = security_config.get("rate_limit", {})
            if not isinstance(rate_limit_config, dict):
                logger.error("Rate limit configuration must be a dictionary")
                return False
            
            logger.info("Security configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """
        Get default security configuration.
        
        Returns:
            Default security configuration dictionary
        """
        return {
            "security": {
                "framework": "mcp_security_framework",
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {},
                    "jwt_secret": "",
                    "jwt_algorithm": "HS256"
                },
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "min_tls_version": "TLSv1.2",
                    "verify_client": False,
                    "client_cert_required": False
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": "roles.json",
                    "default_role": "user",
                    "deny_by_default": True
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "burst_limit": 10,
                    "by_ip": True,
                    "by_user": True
                }
            }
        }
    
    @staticmethod
    def merge_config(base_config: Dict[str, Any], security_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge security configuration into base configuration.
        
        Args:
            base_config: Base configuration dictionary
            security_config: Security configuration to merge
            
        Returns:
            Merged configuration dictionary
        """
        try:
            # Create a copy of base config
            merged_config = base_config.copy()
            
            # Merge security configuration
            if "security" not in merged_config:
                merged_config["security"] = {}
            
            # Deep merge security configuration
            SecurityFactory._deep_merge(merged_config["security"], security_config)
            
            logger.info("Security configuration merged successfully")
            return merged_config
            
        except Exception as e:
            logger.error(f"Failed to merge security configuration: {e}")
            return base_config
    
    @staticmethod
    def _deep_merge(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """
        Deep merge two dictionaries.
        
        Args:
            base_dict: Base dictionary to update
            update_dict: Dictionary with updates
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                SecurityFactory._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
