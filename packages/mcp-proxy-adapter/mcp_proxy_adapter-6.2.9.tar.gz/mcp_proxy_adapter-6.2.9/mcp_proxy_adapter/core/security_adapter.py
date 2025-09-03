"""
Security Adapter for mcp_security_framework integration.

This module provides an adapter layer between mcp_proxy_adapter and mcp_security_framework,
handling configuration conversion and request validation.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import mcp_security_framework components
try:
    from mcp_security_framework import SecurityManager, SecurityConfig
    from mcp_security_framework.schemas.config import (
        AuthConfig, SSLConfig, PermissionConfig, RateLimitConfig
    )
    # Note: SecurityRequest and SecurityResult are not available in current version
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    # Fallback for when mcp_security_framework is not available
    SECURITY_FRAMEWORK_AVAILABLE = False
    SecurityManager = None
    SecurityConfig = None
    AuthConfig = None
    SSLConfig = None
    PermissionConfig = None
    RateLimitConfig = None

from mcp_proxy_adapter.core.logging import logger


class SecurityAdapter:
    """
    Adapter for integrating with mcp_security_framework.
    
    Provides methods to convert mcp_proxy_adapter configuration to SecurityConfig
    and handle request validation through the security framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize security adapter.
        
        Args:
            config: mcp_proxy_adapter configuration dictionary
        """
        self.config = config
        self.security_manager = None
        
        if SECURITY_FRAMEWORK_AVAILABLE:
            self.security_manager = self._create_security_manager()
            logger.info("Security adapter initialized with mcp_security_framework")
        else:
            logger.warning("mcp_security_framework not available, using fallback mode")
    
    def _create_security_manager(self) -> Optional[SecurityManager]:
        """
        Create SecurityManager from mcp_proxy_adapter configuration.
        
        Returns:
            SecurityManager instance or None if framework not available
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            return None
        
        try:
            security_config = self._convert_config()
            return SecurityManager(security_config)
        except Exception as e:
            logger.error(f"Failed to create SecurityManager: {e}")
            return None
    
    def _convert_config(self) -> SecurityConfig:
        """
        Convert mcp_proxy_adapter configuration to SecurityConfig.
        
        Returns:
            SecurityConfig instance
        """
        # Get security configuration section
        security_config = self.config.get("security", {})
        
        # Convert auth configuration
        auth_config = self._convert_auth_config(security_config)
        
        # Convert SSL configuration
        ssl_config = self._convert_ssl_config(security_config)
        
        # Convert permissions configuration
        permission_config = self._convert_permission_config(security_config)
        
        # Convert rate limit configuration
        rate_limit_config = self._convert_rate_limit_config(security_config)
        
        return SecurityConfig(
            auth=auth_config,
            ssl=ssl_config,
            permissions=permission_config,
            rate_limit=rate_limit_config
        )
    
    def _convert_auth_config(self, security_config: Dict[str, Any]) -> AuthConfig:
        """
        Convert authentication configuration.
        
        Args:
            security_config: Security configuration section
            
        Returns:
            AuthConfig instance
        """
        auth_config = security_config.get("auth", {})
        
        # Get authentication methods
        methods = auth_config.get("methods", ["api_key"])
        
        # Get API keys from legacy config if not in security section
        api_keys = auth_config.get("api_keys", {})
        if not api_keys:
            # Try to get from legacy SSL config
            legacy_ssl = self.config.get("ssl", {})
            if "api_keys" in legacy_ssl:
                api_keys = legacy_ssl["api_keys"]
        
        return AuthConfig(
            enabled=auth_config.get("enabled", True),
            methods=methods,
            api_keys=api_keys,
            jwt_secret=auth_config.get("jwt_secret", ""),
            jwt_algorithm=auth_config.get("jwt_algorithm", "HS256")
        )
    
    def _convert_ssl_config(self, security_config: Dict[str, Any]) -> SSLConfig:
        """
        Convert SSL configuration.
        
        Args:
            security_config: Security configuration section
            
        Returns:
            SSLConfig instance
        """
        ssl_config = security_config.get("ssl", {})
        
        # Fallback to legacy SSL config if not in security section
        if not ssl_config:
            ssl_config = self.config.get("ssl", {})
        
        return SSLConfig(
            enabled=ssl_config.get("enabled", False),
            cert_file=ssl_config.get("cert_file"),
            key_file=ssl_config.get("key_file"),
            ca_cert=ssl_config.get("ca_cert"),
            min_tls_version=ssl_config.get("min_tls_version", "TLSv1.2"),
            verify_client=ssl_config.get("verify_client", False),
            client_cert_required=ssl_config.get("client_cert_required", False)
        )
    
    def _convert_permission_config(self, security_config: Dict[str, Any]) -> PermissionConfig:
        """
        Convert permissions configuration.
        
        Args:
            security_config: Security configuration section
            
        Returns:
            PermissionConfig instance
        """
        permission_config = security_config.get("permissions", {})
        
        # Fallback to legacy roles config if not in security section
        if not permission_config:
            roles_config = self.config.get("roles", {})
            permission_config = {
                "enabled": roles_config.get("enabled", True),
                "roles_file": roles_config.get("config_file", "roles.json"),
                "default_role": "user"
            }
        
        return PermissionConfig(
            enabled=permission_config.get("enabled", True),
            roles_file=permission_config.get("roles_file", "roles.json"),
            default_role=permission_config.get("default_role", "user"),
            deny_by_default=permission_config.get("deny_by_default", True)
        )
    
    def _convert_rate_limit_config(self, security_config: Dict[str, Any]) -> RateLimitConfig:
        """
        Convert rate limit configuration.
        
        Args:
            security_config: Security configuration section
            
        Returns:
            RateLimitConfig instance
        """
        rate_limit_config = security_config.get("rate_limit", {})
        
        return RateLimitConfig(
            enabled=rate_limit_config.get("enabled", True),
            requests_per_minute=rate_limit_config.get("requests_per_minute", 60),
            requests_per_hour=rate_limit_config.get("requests_per_hour", 1000),
            burst_limit=rate_limit_config.get("burst_limit", 10),
            by_ip=rate_limit_config.get("by_ip", True),
            by_user=rate_limit_config.get("by_user", True)
        )
    
    def validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate request through mcp_security_framework.
        
        Args:
            request_data: Request data dictionary
            
        Returns:
            Validation result dictionary
        """
        logger.debug(f"Security manager available: {self.security_manager is not None}")
        if not self.security_manager:
            # Fallback validation when framework is not available
            logger.debug("Using fallback validation")
            return self._fallback_validation(request_data)
        
        try:
            # Convert request data to SecurityRequest
            security_request = self._create_security_request(request_data)
            
            # Validate through security framework
            result = self.security_manager.validate_request(security_request)
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {
                "is_valid": False,
                "error_code": -32603,
                "error_message": f"Security validation error: {str(e)}",
                "roles": [],
                "user_id": None
            }
    
    def _create_security_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create request data for security validation.
        
        Args:
            request_data: Request data dictionary
            
        Returns:
            Request data dictionary for security validation
        """
        return {
            "method": request_data.get("method", "GET"),
            "path": request_data.get("path", "/"),
            "headers": request_data.get("headers", {}),
            "query_params": request_data.get("query_params", {}),
            "client_ip": request_data.get("client_ip", "unknown"),
            "body": request_data.get("body", {})
        }
    
    def _fallback_validation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback validation when mcp_security_framework is not available.
        
        Args:
            request_data: Request data dictionary
            
        Returns:
            Validation result dictionary
        """
        # Simple API key validation as fallback
        headers = request_data.get("headers", {})
        query_params = request_data.get("query_params", {})
        body = request_data.get("body", {})
        
        # Check for API key in headers (FastAPI converts headers to lowercase)
        api_key = headers.get("x-api-key") or headers.get("X-API-Key")
        logger.debug(f"API key from headers: {api_key}")
        
        # Check for API key in query parameters
        if not api_key:
            api_key = query_params.get("api_key")
            logger.debug(f"API key from query params: {api_key}")
        
        # Check for API key in JSON-RPC body
        if not api_key and isinstance(body, dict):
            api_key = body.get("params", {}).get("api_key")
            logger.debug(f"API key from body: {api_key}")
        
        # Get API keys from config
        api_keys = self._get_api_keys()
        logger.debug(f"Available API keys: {list(api_keys.keys())}")
        
        if api_key and api_key in api_keys:
            return {
                "is_valid": True,
                "error_code": None,
                "error_message": None,
                "roles": ["user"],
                "user_id": api_keys[api_key]
            }
        else:
            return {
                "is_valid": False,
                "error_code": -32000,
                "error_message": "API key not provided or invalid",
                "roles": [],
                "user_id": None
            }
    
    def _get_api_keys(self) -> Dict[str, str]:
        """
        Get API keys from configuration.
        
        Returns:
            Dictionary mapping API keys to usernames
        """
        # Try security config first
        security_config = self.config.get("security", {})
        auth_config = security_config.get("auth", {})
        api_keys = auth_config.get("api_keys", {})
        
        logger.debug(f"Security config: {security_config}")
        logger.debug(f"Auth config: {auth_config}")
        logger.debug(f"API keys from security config: {api_keys}")
        
        # Fallback to legacy SSL config
        if not api_keys:
            ssl_config = self.config.get("ssl", {})
            api_keys = ssl_config.get("api_keys", {})
            logger.debug(f"API keys from SSL config: {api_keys}")
        
        logger.info(f"Total API keys loaded: {len(api_keys)}")
        return api_keys
    
    def create_middleware(self, framework: str = "fastapi"):
        """
        Create framework-specific middleware.
        
        Args:
            framework: Framework type (fastapi, flask, etc.)
            
        Returns:
            Middleware instance
        """
        if not self.security_manager:
            logger.warning("Cannot create middleware: security framework not available")
            return None
        
        try:
            if framework == "fastapi":
                from mcp_security_framework.middleware import create_fastapi_security_middleware
                return create_fastapi_security_middleware(self.security_manager)
            else:
                raise ValueError(f"Unsupported framework: {framework}")
        except Exception as e:
            logger.error(f"Failed to create middleware: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if security framework is available.
        
        Returns:
            True if framework is available, False otherwise
        """
        return SECURITY_FRAMEWORK_AVAILABLE and self.security_manager is not None
