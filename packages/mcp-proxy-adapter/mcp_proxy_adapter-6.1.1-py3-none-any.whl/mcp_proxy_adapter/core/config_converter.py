"""
Configuration Converter for security framework integration.

This module provides utilities to convert between mcp_proxy_adapter configuration
format and mcp_security_framework configuration format, ensuring backward compatibility.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from mcp_proxy_adapter.core.logging import logger


class ConfigConverter:
    """
    Converter for configuration formats.
    
    Provides methods to convert between mcp_proxy_adapter configuration
    and mcp_security_framework configuration formats.
    """
    
    @staticmethod
    def to_security_framework_config(mcp_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert mcp_proxy_adapter configuration to SecurityConfig format.
        
        Args:
            mcp_config: mcp_proxy_adapter configuration dictionary
            
        Returns:
            SecurityConfig compatible dictionary
        """
        try:
            # Start with default security framework config
            security_config = {
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
            
            # Convert from security section if exists
            if "security" in mcp_config:
                security_section = mcp_config["security"]
                
                # Convert auth config
                if "auth" in security_section:
                    auth_config = security_section["auth"]
                    security_config["auth"].update({
                        "enabled": auth_config.get("enabled", True),
                        "methods": auth_config.get("methods", ["api_key"]),
                        "api_keys": auth_config.get("api_keys", {}),
                        "jwt_secret": auth_config.get("jwt_secret", ""),
                        "jwt_algorithm": auth_config.get("jwt_algorithm", "HS256")
                    })
                
                # Convert SSL config
                if "ssl" in security_section:
                    ssl_config = security_section["ssl"]
                    security_config["ssl"].update({
                        "enabled": ssl_config.get("enabled", False),
                        "cert_file": ssl_config.get("cert_file"),
                        "key_file": ssl_config.get("key_file"),
                        "ca_cert": ssl_config.get("ca_cert"),
                        "min_tls_version": ssl_config.get("min_tls_version", "TLSv1.2"),
                        "verify_client": ssl_config.get("verify_client", False),
                        "client_cert_required": ssl_config.get("client_cert_required", False)
                    })
                
                # Convert permissions config
                if "permissions" in security_section:
                    permissions_config = security_section["permissions"]
                    security_config["permissions"].update({
                        "enabled": permissions_config.get("enabled", True),
                        "roles_file": permissions_config.get("roles_file", "roles.json"),
                        "default_role": permissions_config.get("default_role", "user"),
                        "deny_by_default": permissions_config.get("deny_by_default", True)
                    })
                
                # Convert rate limit config
                if "rate_limit" in security_section:
                    rate_limit_config = security_section["rate_limit"]
                    security_config["rate_limit"].update({
                        "enabled": rate_limit_config.get("enabled", True),
                        "requests_per_minute": rate_limit_config.get("requests_per_minute", 60),
                        "requests_per_hour": rate_limit_config.get("requests_per_hour", 1000),
                        "burst_limit": rate_limit_config.get("burst_limit", 10),
                        "by_ip": rate_limit_config.get("by_ip", True),
                        "by_user": rate_limit_config.get("by_user", True)
                    })
            
            # Convert from legacy SSL config if security section doesn't exist
            elif "ssl" in mcp_config:
                ssl_config = mcp_config["ssl"]
                security_config["ssl"].update({
                    "enabled": ssl_config.get("enabled", False),
                    "cert_file": ssl_config.get("cert_file"),
                    "key_file": ssl_config.get("key_file"),
                    "ca_cert": ssl_config.get("ca_cert"),
                    "min_tls_version": ssl_config.get("min_tls_version", "TLSv1.2"),
                    "verify_client": ssl_config.get("verify_client", False),
                    "client_cert_required": ssl_config.get("client_cert_required", False)
                })
                
                # Extract API keys from legacy SSL config
                if "api_keys" in ssl_config:
                    security_config["auth"]["api_keys"] = ssl_config["api_keys"]
            
            # Convert from legacy roles config
            if "roles" in mcp_config:
                roles_config = mcp_config["roles"]
                security_config["permissions"].update({
                    "enabled": roles_config.get("enabled", True),
                    "roles_file": roles_config.get("config_file", "roles.json"),
                    "default_role": "user",
                    "deny_by_default": roles_config.get("default_policy", {}).get("deny_by_default", True)
                })
            
            logger.info("Configuration converted to security framework format successfully")
            return security_config
            
        except Exception as e:
            logger.error(f"Failed to convert configuration to security framework format: {e}")
            return ConfigConverter._get_default_security_config()
    
    @staticmethod
    def from_security_framework_config(security_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert SecurityConfig format to mcp_proxy_adapter configuration.
        
        Args:
            security_config: SecurityConfig compatible dictionary
            
        Returns:
            mcp_proxy_adapter configuration dictionary
        """
        try:
            mcp_config = {
                "security": {
                    "framework": "mcp_security_framework",
                    "enabled": True
                }
            }
            
            # Convert auth config
            if "auth" in security_config:
                auth_config = security_config["auth"]
                mcp_config["security"]["auth"] = {
                    "enabled": auth_config.get("enabled", True),
                    "methods": auth_config.get("methods", ["api_key"]),
                    "api_keys": auth_config.get("api_keys", {}),
                    "jwt_secret": auth_config.get("jwt_secret", ""),
                    "jwt_algorithm": auth_config.get("jwt_algorithm", "HS256")
                }
            
            # Convert SSL config
            if "ssl" in security_config:
                ssl_config = security_config["ssl"]
                mcp_config["security"]["ssl"] = {
                    "enabled": ssl_config.get("enabled", False),
                    "cert_file": ssl_config.get("cert_file"),
                    "key_file": ssl_config.get("key_file"),
                    "ca_cert": ssl_config.get("ca_cert"),
                    "min_tls_version": ssl_config.get("min_tls_version", "TLSv1.2"),
                    "verify_client": ssl_config.get("verify_client", False),
                    "client_cert_required": ssl_config.get("client_cert_required", False)
                }
            
            # Convert permissions config
            if "permissions" in security_config:
                permissions_config = security_config["permissions"]
                mcp_config["security"]["permissions"] = {
                    "enabled": permissions_config.get("enabled", True),
                    "roles_file": permissions_config.get("roles_file", "roles.json"),
                    "default_role": permissions_config.get("default_role", "user"),
                    "deny_by_default": permissions_config.get("deny_by_default", True)
                }
            
            # Convert rate limit config
            if "rate_limit" in security_config:
                rate_limit_config = security_config["rate_limit"]
                mcp_config["security"]["rate_limit"] = {
                    "enabled": rate_limit_config.get("enabled", True),
                    "requests_per_minute": rate_limit_config.get("requests_per_minute", 60),
                    "requests_per_hour": rate_limit_config.get("requests_per_hour", 1000),
                    "burst_limit": rate_limit_config.get("burst_limit", 10),
                    "by_ip": rate_limit_config.get("by_ip", True),
                    "by_user": rate_limit_config.get("by_user", True)
                }
            
            logger.info("Configuration converted from security framework format successfully")
            return mcp_config
            
        except Exception as e:
            logger.error(f"Failed to convert configuration from security framework format: {e}")
            return ConfigConverter._get_default_mcp_config()
    
    @staticmethod
    def migrate_legacy_config(config_path: str, output_path: Optional[str] = None) -> bool:
        """
        Migrate legacy configuration to new security framework format.
        
        Args:
            config_path: Path to legacy configuration file
            output_path: Path to output migrated configuration file (optional)
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            # Read legacy configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                legacy_config = json.load(f)
            
            # Convert to new format
            new_config = ConfigConverter.to_security_framework_config(legacy_config)
            
            # Add security section to legacy config
            legacy_config["security"] = new_config
            
            # Determine output path
            if output_path is None:
                output_path = config_path.replace('.json', '_migrated.json')
            
            # Write migrated configuration
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(legacy_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration migrated successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate configuration: {e}")
            return False
    
    @staticmethod
    def validate_security_config(config: Dict[str, Any]) -> bool:
        """
        Validate security configuration format.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check if security section exists
            if "security" not in config:
                logger.error("Security section not found in configuration")
                return False
            
            security_section = config["security"]
            
            # Validate required fields
            required_sections = ["auth", "ssl", "permissions", "rate_limit"]
            for section in required_sections:
                if section not in security_section:
                    logger.error(f"Required section '{section}' not found in security configuration")
                    return False
                
                if not isinstance(security_section[section], dict):
                    logger.error(f"Section '{section}' must be a dictionary")
                    return False
            
            # Validate auth configuration
            auth_config = security_section["auth"]
            if not isinstance(auth_config.get("methods", []), list):
                logger.error("Auth methods must be a list")
                return False
            
            if not isinstance(auth_config.get("api_keys", {}), dict):
                logger.error("API keys must be a dictionary")
                return False
            
            # Validate SSL configuration
            ssl_config = security_section["ssl"]
            if not isinstance(ssl_config.get("enabled", False), bool):
                logger.error("SSL enabled must be a boolean")
                return False
            
            # Validate permissions configuration
            permissions_config = security_section["permissions"]
            if not isinstance(permissions_config.get("enabled", True), bool):
                logger.error("Permissions enabled must be a boolean")
                return False
            
            # Validate rate limit configuration
            rate_limit_config = security_section["rate_limit"]
            if not isinstance(rate_limit_config.get("enabled", True), bool):
                logger.error("Rate limit enabled must be a boolean")
                return False
            
            if not isinstance(rate_limit_config.get("requests_per_minute", 60), int):
                logger.error("Requests per minute must be an integer")
                return False
            
            logger.info("Security configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    @staticmethod
    def _get_default_security_config() -> Dict[str, Any]:
        """
        Get default security framework configuration.
        
        Returns:
            Default security framework configuration
        """
        return {
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
    
    @staticmethod
    def _get_default_mcp_config() -> Dict[str, Any]:
        """
        Get default mcp_proxy_adapter configuration.
        
        Returns:
            Default mcp_proxy_adapter configuration
        """
        return {
            "security": {
                "framework": "mcp_security_framework",
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {}
                },
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": "roles.json"
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            }
        }
