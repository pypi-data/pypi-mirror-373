"""
Unified Configuration Adapter for mcp_security_framework integration.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

This module provides a unified adapter for converting mcp_proxy_adapter configuration
to SecurityConfig format used by mcp_security_framework.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass

# Import mcp_security_framework components
try:
    from mcp_security_framework import SecurityConfig
    from mcp_security_framework.schemas.config import (
        AuthConfig, SSLConfig, PermissionConfig, RateLimitConfig
    )
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    SecurityConfig = None
    AuthConfig = None
    SSLConfig = None
    PermissionConfig = None
    RateLimitConfig = None

from mcp_proxy_adapter.core.logging import logger


@dataclass
class ValidationResult:
    """Result of configuration validation."""
    
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    
    def __post_init__(self):
        """Initialize with empty lists if None."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.details is None:
            self.details = {}


class UnifiedConfigAdapter:
    """
    Unified adapter for converting mcp_proxy_adapter configuration to SecurityConfig.
    
    This adapter handles:
    - Legacy configuration format compatibility
    - Configuration validation
    - Conversion to mcp_security_framework format
    - Default value management
    """
    
    def __init__(self):
        """Initialize the unified configuration adapter."""
        self.validation_errors = []
        self.validation_warnings = []
    
    def convert_to_security_config(self, config: Dict[str, Any]) -> Optional[SecurityConfig]:
        """
        Convert mcp_proxy_adapter configuration to SecurityConfig.
        
        Args:
            config: mcp_proxy_adapter configuration dictionary
            
        Returns:
            SecurityConfig instance or None if conversion failed
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.error("mcp_security_framework not available, cannot convert configuration")
            return None
        
        try:
            # Validate configuration first
            validation_result = self.validate_configuration(config)
            if not validation_result.is_valid:
                logger.error(f"Configuration validation failed: {validation_result.errors}")
                return None
            
            # Convert configuration sections
            auth_config = self._convert_auth_config(config)
            ssl_config = self._convert_ssl_config(config)
            permission_config = self._convert_permission_config(config)
            rate_limit_config = self._convert_rate_limit_config(config)
            
            # Create SecurityConfig
            security_config = SecurityConfig(
                auth=auth_config,
                ssl=ssl_config,
                permissions=permission_config,
                rate_limit=rate_limit_config
            )
            
            logger.info("Configuration successfully converted to SecurityConfig")
            return security_config
            
        except Exception as e:
            logger.error(f"Failed to convert configuration: {e}")
            return None
    
    def validate_configuration(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration before conversion.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            ValidationResult with validation details
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        # Debug: Check SSL config at start of validation
        if "security" in config:
            ssl_config = config["security"].get("ssl", {})
            print(f"🔍 Debug: SSL config at start of validation: enabled={ssl_config.get('enabled', False)}")
        
        # Debug: Check if root ssl section exists
        if "ssl" in config:
            print(f"🔍 Debug: Root SSL section found: enabled={config['ssl'].get('enabled', False)}")
        
        # Check if config is a dictionary
        if not isinstance(config, dict):
            return ValidationResult(
                is_valid=False,
                errors=["Configuration must be a dictionary"],
                warnings=[],
                details={}
            )
        
        # Validate security section
        self._validate_security_section(config)
        
        # Validate legacy sections for compatibility
        self._validate_legacy_sections(config)
        
        # Check for conflicts
        self._check_configuration_conflicts(config)
        
        # Validate individual sections
        self._validate_auth_section(config)
        self._validate_ssl_section(config)
        self._validate_permissions_section(config)
        self._validate_rate_limit_section(config)
        
        return ValidationResult(
            is_valid=len(self.validation_errors) == 0,
            errors=self.validation_errors.copy(),
            warnings=self.validation_warnings.copy(),
            details={
                "has_security_section": "security" in config,
                "has_legacy_sections": any(key in config for key in ["ssl", "roles", "auth_enabled"]),
                "total_errors": len(self.validation_errors),
                "total_warnings": len(self.validation_warnings)
            }
        )
    
    def _validate_security_section(self, config: Dict[str, Any]):
        """Validate security section."""
        security_config = config.get("security", {})
        
        if not isinstance(security_config, dict):
            self.validation_errors.append("Security section must be a dictionary")
            return
        
        # Check for unknown keys in security section
        known_keys = {"enabled", "auth", "ssl", "permissions", "rate_limit", "public_paths"}
        unknown_keys = set(security_config.keys()) - known_keys
        
        if unknown_keys:
            self.validation_warnings.append(f"Unknown keys in security section: {unknown_keys}")
    
    def _validate_legacy_sections(self, config: Dict[str, Any]):
        """Validate legacy configuration sections."""
        legacy_sections = ["ssl", "roles", "auth_enabled", "rate_limit_enabled"]
        
        for section in legacy_sections:
            if section in config:
                self.validation_warnings.append(f"Legacy section '{section}' found, consider migrating to security section")
    
    def _check_configuration_conflicts(self, config: Dict[str, Any]):
        """Check for configuration conflicts."""
        security_config = config.get("security", {})
        
        # Check for SSL configuration conflicts
        if "ssl" in config and "ssl" in security_config:
            self.validation_warnings.append("SSL configuration found in both root and security sections")
        
        # Check for auth configuration conflicts
        if "auth_enabled" in config and "auth" in security_config:
            self.validation_warnings.append("Auth configuration found in both root and security sections")
    
    def _validate_auth_section(self, config: Dict[str, Any]):
        """Validate authentication section."""
        auth_config = self._get_auth_config(config)
        
        if not isinstance(auth_config, dict):
            self.validation_errors.append("Auth configuration must be a dictionary")
            return
        
        # Validate auth methods
        methods = auth_config.get("methods", [])
        if not isinstance(methods, list):
            self.validation_errors.append("Auth methods must be a list")
        else:
            valid_methods = {"api_key", "jwt", "certificate"}
            invalid_methods = set(methods) - valid_methods
            if invalid_methods:
                self.validation_errors.append(f"Invalid auth methods: {invalid_methods}")
        
        # Validate API keys
        api_keys = auth_config.get("api_keys", {})
        if not isinstance(api_keys, dict):
            self.validation_errors.append("API keys must be a dictionary")
        
        # Validate JWT configuration
        if "jwt" in methods:
            jwt_secret = auth_config.get("jwt_secret", "")
            if not jwt_secret:
                self.validation_warnings.append("JWT secret is empty or not set")
    
    def _validate_ssl_section(self, config: Dict[str, Any]):
        """Validate SSL section."""
        ssl_config = self._get_ssl_config(config)
        
        if not isinstance(ssl_config, dict):
            self.validation_errors.append("SSL configuration must be a dictionary")
            return
        
        # Validate certificate files
        if ssl_config.get("enabled", False):
            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            
            print(f"🔍 Debug: _validate_ssl_section: cert_file={cert_file}")
            print(f"🔍 Debug: _validate_ssl_section: key_file={key_file}")
            print(f"🔍 Debug: _validate_ssl_section: cert_file exists={Path(cert_file).exists() if cert_file else 'None'}")
            print(f"🔍 Debug: _validate_ssl_section: key_file exists={Path(key_file).exists() if key_file else 'None'}")
            
            if cert_file and not Path(cert_file).exists():
                self.validation_warnings.append(f"SSL certificate file not found: {cert_file}")
            
            if key_file and not Path(key_file).exists():
                self.validation_warnings.append(f"SSL key file not found: {key_file}")
    
    def _validate_permissions_section(self, config: Dict[str, Any]):
        """Validate permissions section."""
        permissions_config = self._get_permissions_config(config)
        
        if not isinstance(permissions_config, dict):
            self.validation_errors.append("Permissions configuration must be a dictionary")
            return
        
        # Validate roles file
        if permissions_config.get("enabled", False):
            roles_file = permissions_config.get("roles_file")
            if roles_file and not Path(roles_file).exists():
                self.validation_warnings.append(f"Roles file not found: {roles_file}")
    
    def _validate_rate_limit_section(self, config: Dict[str, Any]):
        """Validate rate limit section."""
        rate_limit_config = self._get_rate_limit_config(config)
        
        if not isinstance(rate_limit_config, dict):
            self.validation_errors.append("Rate limit configuration must be a dictionary")
            return
        
        # Validate rate limit values only if enabled
        if rate_limit_config.get("enabled", False):
            requests_per_minute = rate_limit_config.get("requests_per_minute", rate_limit_config.get("default_requests_per_minute", 0))
            if requests_per_minute <= 0:
                self.validation_errors.append("requests_per_minute must be greater than 0 when rate limiting is enabled")
    
    def _convert_auth_config(self, config: Dict[str, Any]) -> AuthConfig:
        """Convert authentication configuration."""
        auth_config = self._get_auth_config(config)
        
        # Get authentication methods
        methods = auth_config.get("methods", ["api_key"])
        
        # Get API keys from multiple sources
        api_keys = auth_config.get("api_keys", {})
        if not api_keys:
            # Try legacy SSL config
            legacy_ssl = config.get("ssl", {})
            api_keys = legacy_ssl.get("api_keys", {})
        
        return AuthConfig(
            enabled=auth_config.get("enabled", True),
            methods=methods,
            api_keys=api_keys,
            jwt_secret=auth_config.get("jwt_secret", ""),
            jwt_algorithm=auth_config.get("jwt_algorithm", "HS256"),
            jwt_expiration=auth_config.get("jwt_expiration", 3600)
        )
    
    def _convert_ssl_config(self, config: Dict[str, Any]) -> SSLConfig:
        """Convert SSL configuration."""
        ssl_config = self._get_ssl_config(config)
        
        return SSLConfig(
            enabled=ssl_config.get("enabled", False),
            cert_file=ssl_config.get("cert_file"),
            key_file=ssl_config.get("key_file"),
            ca_cert=ssl_config.get("ca_cert"),
            min_tls_version=ssl_config.get("min_tls_version", "TLSv1.2"),
            verify_client=ssl_config.get("verify_client", False),
            client_cert_required=ssl_config.get("client_cert_required", False),
            cipher_suites=ssl_config.get("cipher_suites", [])
        )
    
    def _convert_permission_config(self, config: Dict[str, Any]) -> PermissionConfig:
        """Convert permissions configuration."""
        permissions_config = self._get_permissions_config(config)
        
        return PermissionConfig(
            enabled=permissions_config.get("enabled", True),
            roles_file=permissions_config.get("roles_file", "roles.json"),
            default_role=permissions_config.get("default_role", "user"),
            deny_by_default=permissions_config.get("deny_by_default", True),
            role_mappings=permissions_config.get("role_mappings", {})
        )
    
    def _convert_rate_limit_config(self, config: Dict[str, Any]) -> RateLimitConfig:
        """Convert rate limit configuration."""
        rate_limit_config = self._get_rate_limit_config(config)
        
        return RateLimitConfig(
            enabled=rate_limit_config.get("enabled", False),
            requests_per_minute=rate_limit_config.get("requests_per_minute", 60),
            requests_per_hour=rate_limit_config.get("requests_per_hour", 1000),
            requests_per_day=rate_limit_config.get("requests_per_day", 10000),
            burst_limit=rate_limit_config.get("burst_limit", 10),
            by_ip=rate_limit_config.get("by_ip", True),
            by_user=rate_limit_config.get("by_user", True),
            by_endpoint=rate_limit_config.get("by_endpoint", False),
            exempt_roles=rate_limit_config.get("exempt_roles", []),
            exempt_endpoints=rate_limit_config.get("exempt_endpoints", [])
        )
    
    def _get_auth_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get authentication configuration from config."""
        security_config = config.get("security", {})
        
        # Ensure security_config is a dictionary
        if not isinstance(security_config, dict):
            return {}
        
        auth_config = security_config.get("auth", {})
        
        # Handle legacy auth_enabled flag
        if config.get("auth_enabled") is not None:
            auth_config["enabled"] = config["auth_enabled"]
        
        return auth_config
    
    def _get_ssl_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get SSL configuration from config."""
        security_config = config.get("security", {})
        
        # Ensure security_config is a dictionary
        if not isinstance(security_config, dict):
            return {}
        
        ssl_config = security_config.get("ssl", {})
        
        # Debug: Check SSL config before merging
        print(f"🔍 Debug: _get_ssl_config: security.ssl key_file={ssl_config.get('key_file')}")
        
        # Merge with legacy SSL config, but prioritize security.ssl over legacy ssl
        legacy_ssl = config.get("ssl", {})
        if legacy_ssl:
            print(f"🔍 Debug: _get_ssl_config: legacy ssl key_file={legacy_ssl.get('key_file')}")
            # Only merge legacy config if security.ssl is not enabled or missing
            if not ssl_config.get("enabled", False):
                ssl_config.update(legacy_ssl)
            else:
                # If security.ssl is enabled, only merge non-conflicting fields
                for key, value in legacy_ssl.items():
                    if key not in ssl_config or ssl_config[key] is None:
                        ssl_config[key] = value
        
        print(f"🔍 Debug: _get_ssl_config: final key_file={ssl_config.get('key_file')}")
        return ssl_config
    
    def _get_permissions_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get permissions configuration from config."""
        security_config = config.get("security", {})
        
        # Ensure security_config is a dictionary
        if not isinstance(security_config, dict):
            return {}
        
        permissions_config = security_config.get("permissions", {})
        
        # Merge with legacy roles config
        legacy_roles = config.get("roles", {})
        if legacy_roles:
            permissions_config.update(legacy_roles)
        
        return permissions_config
    
    def _get_rate_limit_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get rate limit configuration from config."""
        security_config = config.get("security", {})
        
        # Ensure security_config is a dictionary
        if not isinstance(security_config, dict):
            return {}
        
        rate_limit_config = security_config.get("rate_limit", {})
        
        # Handle legacy rate_limit_enabled flag
        if config.get("rate_limit_enabled") is not None:
            rate_limit_config["enabled"] = config["rate_limit_enabled"]
        
        return rate_limit_config
    
    def get_public_paths(self, config: Dict[str, Any]) -> List[str]:
        """
        Get public paths from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of public paths
        """
        security_config = config.get("security", {})
        
        # Ensure security_config is a dictionary
        if not isinstance(security_config, dict):
            return [
                "/health",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/favicon.ico"
            ]
        
        public_paths = security_config.get("public_paths", [])
        
        # Add default public paths if none specified
        if not public_paths:
            public_paths = [
                "/health",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/favicon.ico"
            ]
        
        return public_paths
    
    def get_security_enabled(self, config: Dict[str, Any]) -> bool:
        """
        Check if security is enabled in configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if security is enabled
        """
        security_config = config.get("security", {})
        
        # Ensure security_config is a dictionary
        if not isinstance(security_config, dict):
            return True  # Default to enabled for safety
        
        return security_config.get("enabled", True)
    
    def migrate_legacy_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate legacy configuration to new format.
        
        Args:
            config: Legacy configuration dictionary
            
        Returns:
            Migrated configuration dictionary
        """
        migrated_config = config.copy()
        
        # Create security section if it doesn't exist
        if "security" not in migrated_config:
            migrated_config["security"] = {}
        
        security_config = migrated_config["security"]
        
        # Migrate SSL configuration
        if "ssl" in migrated_config and "ssl" not in security_config:
            security_config["ssl"] = migrated_config["ssl"]
            # Don't remove legacy SSL yet for backward compatibility
        
        # Migrate roles configuration
        if "roles" in migrated_config and "permissions" not in security_config:
            security_config["permissions"] = migrated_config["roles"]
            # Don't remove legacy roles yet for backward compatibility
        
        # Migrate auth_enabled flag
        if "auth_enabled" in migrated_config and "auth" not in security_config:
            security_config["auth"] = {"enabled": migrated_config["auth_enabled"]}
        
        # Migrate rate_limit_enabled flag
        if "rate_limit_enabled" in migrated_config and "rate_limit" not in security_config:
            security_config["rate_limit"] = {"enabled": migrated_config["rate_limit_enabled"]}
        
        logger.info("Legacy configuration migrated to new format")
        return migrated_config
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {},
                    "jwt_secret": "",
                    "jwt_algorithm": "HS256",
                    "jwt_expiration": 3600
                },
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "min_tls_version": "TLSv1.2",
                    "verify_client": False,
                    "client_cert_required": False,
                    "cipher_suites": []
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": "roles.json",
                    "default_role": "user",
                    "deny_by_default": True,
                    "role_mappings": {}
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "requests_per_day": 10000,
                    "burst_limit": 10,
                    "by_ip": True,
                    "by_user": True,
                    "by_endpoint": False,
                    "exempt_roles": [],
                    "exempt_endpoints": []
                },
                "public_paths": [
                    "/health",
                    "/docs",
                    "/redoc",
                    "/openapi.json",
                    "/favicon.ico"
                ]
            }
        }
