"""
Direct Security Framework Integration

This module provides direct integration with mcp_security_framework,
replacing all project security methods with framework calls.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Direct imports from framework
try:
    from mcp_security_framework import (
        SecurityManager, AuthManager, CertificateManager, 
        PermissionManager, RateLimiter
    )
    from mcp_security_framework.schemas.config import (
        SecurityConfig, AuthConfig, SSLConfig, PermissionConfig, 
        RateLimitConfig, CertificateConfig, LoggingConfig
    )
    from mcp_security_framework.schemas.models import (
        AuthResult, ValidationResult, CertificateInfo, CertificatePair
    )
    from mcp_security_framework.middleware.fastapi_middleware import FastAPISecurityMiddleware
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    SecurityManager = None
    SecurityConfig = None
    AuthManager = None
    CertificateManager = None
    PermissionManager = None
    RateLimiter = None
    FastAPISecurityMiddleware = None

from mcp_proxy_adapter.core.logging import logger


class SecurityIntegration:
    """
    Direct integration with mcp_security_framework.
    
    This class replaces all project security methods with direct calls
    to the security framework components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize security integration.
        
        Args:
            config: Configuration dictionary
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            raise ImportError("mcp_security_framework is not available")
        
        self.config = config
        self.security_config = self._create_security_config()
        
        # Initialize framework components
        self.security_manager = SecurityManager(self.security_config)
        self.permission_manager = PermissionManager(self.security_config.permissions)
        self.auth_manager = AuthManager(self.security_config.auth, self.permission_manager)
        self.certificate_manager = CertificateManager(self.security_config.certificates)
        self.rate_limiter = RateLimiter(self.security_config.rate_limit)
        
        logger.info("Security integration initialized with mcp_security_framework")
    
    def _create_security_config(self) -> SecurityConfig:
        """Create SecurityConfig from project configuration."""
        # self.config is already the security section passed from unified_security.py
        security_section = self.config
        
        # Create SSL config
        ssl_config = SSLConfig(
            enabled=security_section.get("ssl", {}).get("enabled", False),
            cert_file=security_section.get("ssl", {}).get("cert_file"),
            key_file=security_section.get("ssl", {}).get("key_file"),
            ca_cert_file=security_section.get("ssl", {}).get("ca_cert_file"),
            client_cert_file=security_section.get("ssl", {}).get("client_cert_file"),
            client_key_file=security_section.get("ssl", {}).get("client_key_file"),
            verify_mode=security_section.get("ssl", {}).get("verify_mode", "CERT_REQUIRED"),
            min_tls_version=security_section.get("ssl", {}).get("min_tls_version", "TLSv1.2"),
            check_hostname=security_section.get("ssl", {}).get("check_hostname", True),
            check_expiry=security_section.get("ssl", {}).get("check_expiry", True),
            expiry_warning_days=security_section.get("ssl", {}).get("expiry_warning_days", 30)
        )
        
        # Create auth config
        auth_config = AuthConfig(
            enabled=security_section.get("auth", {}).get("enabled", True),
            methods=security_section.get("auth", {}).get("methods", ["api_key"]),
            api_keys=security_section.get("auth", {}).get("api_keys", {}),
            user_roles=security_section.get("auth", {}).get("user_roles", {}),
            jwt_secret=security_section.get("auth", {}).get("jwt_secret"),
            jwt_algorithm=security_section.get("auth", {}).get("jwt_algorithm", "HS256"),
            jwt_expiry_hours=security_section.get("auth", {}).get("jwt_expiry_hours", 24),
            certificate_auth=security_section.get("auth", {}).get("certificate_auth", False),
            public_paths=security_section.get("auth", {}).get("public_paths", [])
        )
        
        # Create permission config - handle null values properly
        permissions_section = security_section.get("permissions", {})
        roles_file = permissions_section.get("roles_file")

        # If roles_file is None or empty string, don't pass it to avoid framework errors
        if roles_file is None or roles_file == "":
            logger.warning("roles_file is None or empty, permissions will use default configuration")
            roles_file = None
        
        permission_config = PermissionConfig(
            enabled=permissions_section.get("enabled", True),
            roles_file=roles_file,
            default_role=permissions_section.get("default_role", "guest"),
            admin_role=permissions_section.get("admin_role", "admin"),
            role_hierarchy=permissions_section.get("role_hierarchy", {}),
            permission_cache_enabled=permissions_section.get("permission_cache_enabled", True),
            permission_cache_ttl=permissions_section.get("permission_cache_ttl", 300),
            wildcard_permissions=permissions_section.get("wildcard_permissions", False),
            strict_mode=permissions_section.get("strict_mode", True),
            roles=permissions_section.get("roles")
        )
        
        # Create rate limit config
        rate_limit_config = RateLimitConfig(
            enabled=security_section.get("rate_limit", {}).get("enabled", True),
            default_requests_per_minute=security_section.get("rate_limit", {}).get("default_requests_per_minute", 60),
            default_requests_per_hour=security_section.get("rate_limit", {}).get("default_requests_per_hour", 1000),
            burst_limit=security_section.get("rate_limit", {}).get("burst_limit", 2),
            window_size_seconds=security_section.get("rate_limit", {}).get("window_size_seconds", 60),
            storage_backend=security_section.get("rate_limit", {}).get("storage_backend", "memory"),
            exempt_paths=security_section.get("rate_limit", {}).get("exempt_paths", []),
            exempt_roles=security_section.get("rate_limit", {}).get("exempt_roles", [])
        )
        
        # Create certificate config
        certificate_config = CertificateConfig(
            enabled=security_section.get("certificates", {}).get("enabled", False),
            ca_cert_path=security_section.get("certificates", {}).get("ca_cert_path"),
            ca_key_path=security_section.get("certificates", {}).get("ca_key_path"),
            cert_storage_path=security_section.get("certificates", {}).get("cert_storage_path", "./certs"),
            key_storage_path=security_section.get("certificates", {}).get("key_storage_path", "./keys"),
            default_validity_days=security_section.get("certificates", {}).get("default_validity_days", 365),
            key_size=security_section.get("certificates", {}).get("key_size", 2048),
            hash_algorithm=security_section.get("certificates", {}).get("hash_algorithm", "sha256")
        )
        
        # Create logging config
        logging_config = LoggingConfig(
            enabled=security_section.get("logging", {}).get("enabled", True),
            level=security_section.get("logging", {}).get("level", "INFO"),
            format=security_section.get("logging", {}).get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            console_output=security_section.get("logging", {}).get("console_output", True),
            file_path=security_section.get("logging", {}).get("file_path")
        )
        
        # Create main security config
        return SecurityConfig(
            ssl=ssl_config,
            auth=auth_config,
            permissions=permission_config,
            rate_limit=rate_limit_config,
            certificates=certificate_config,
            logging=logging_config,
            debug=security_section.get("debug", False),
            environment=security_section.get("environment", "dev"),
            version=security_section.get("version", "1.0.0")
        )
    
    # Authentication methods - direct calls to AuthManager
    async def authenticate_api_key(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        return await self.auth_manager.authenticate_api_key(api_key)
    
    async def authenticate_jwt(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        return await self.auth_manager.authenticate_jwt(token)
    
    async def authenticate_certificate(self, cert_data: bytes) -> AuthResult:
        """Authenticate using certificate."""
        return await self.auth_manager.authenticate_certificate(cert_data)
    
    async def validate_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """Validate request using security manager."""
        return await self.security_manager.validate_request(request_data)
    
    # Certificate methods - direct calls to CertificateManager
    async def create_ca_certificate(self, common_name: str, **kwargs) -> CertificatePair:
        """Create CA certificate."""
        return await self.certificate_manager.create_ca_certificate(common_name, **kwargs)
    
    async def create_client_certificate(self, common_name: str, **kwargs) -> CertificatePair:
        """Create client certificate."""
        return await self.certificate_manager.create_client_certificate(common_name, **kwargs)
    
    async def create_server_certificate(self, common_name: str, **kwargs) -> CertificatePair:
        """Create server certificate."""
        return await self.certificate_manager.create_server_certificate(common_name, **kwargs)
    
    async def validate_certificate(self, cert_path: str) -> bool:
        """Validate certificate."""
        return await self.certificate_manager.validate_certificate(cert_path)
    
    async def extract_roles_from_certificate(self, cert_path: str) -> List[str]:
        """Extract roles from certificate."""
        return await self.certificate_manager.extract_roles_from_certificate(cert_path)
    
    async def revoke_certificate(self, cert_path: str) -> bool:
        """Revoke certificate."""
        return await self.certificate_manager.revoke_certificate(cert_path)
    
    # Permission methods - direct calls to PermissionManager
    async def check_permission(self, user_id: str, permission: str) -> bool:
        """Check user permission."""
        return await self.permission_manager.check_permission(user_id, permission)
    
    async def get_user_roles(self, user_id: str) -> List[str]:
        """Get user roles."""
        return await self.permission_manager.get_user_roles(user_id)
    
    async def add_user_role(self, user_id: str, role: str) -> bool:
        """Add role to user."""
        return await self.permission_manager.add_user_role(user_id, role)
    
    async def remove_user_role(self, user_id: str, role: str) -> bool:
        """Remove role from user."""
        return await self.permission_manager.remove_user_role(user_id, role)
    
    # Rate limiting methods - direct calls to RateLimiter
    async def check_rate_limit(self, identifier: str, limit_type: str = "per_minute") -> bool:
        """Check rate limit."""
        return await self.rate_limiter.check_rate_limit(identifier, limit_type)
    
    async def increment_rate_limit(self, identifier: str) -> None:
        """Increment rate limit counter."""
        await self.rate_limiter.increment_rate_limit(identifier)
    
    async def get_rate_limit_info(self, identifier: str) -> Dict[str, Any]:
        """Get rate limit information."""
        return await self.rate_limiter.get_rate_limit_info(identifier)
    
    # Middleware creation - direct use of framework middleware
    def create_fastapi_middleware(self, app) -> FastAPISecurityMiddleware:
        """Create FastAPI security middleware."""
        return FastAPISecurityMiddleware(app, self.security_config)
    
    # Utility methods
    def is_security_enabled(self) -> bool:
        """Check if security is enabled."""
        return self.security_config.auth.enabled or self.security_config.ssl.enabled
    
    def get_public_paths(self) -> List[str]:
        """Get public paths that bypass authentication."""
        return self.security_config.auth.public_paths
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.security_config


# Factory function for easy integration
def create_security_integration(config: Dict[str, Any]) -> SecurityIntegration:
    """
    Create security integration instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        SecurityIntegration instance
        
    Raises:
        RuntimeError: If security integration cannot be created
    """
    try:
        return SecurityIntegration(config)
    except ImportError as e:
        logger.error(f"mcp_security_framework not available: {e}")
        raise RuntimeError("Security framework is required but not available") from e
    except Exception as e:
        logger.error(f"Failed to create security integration: {e}")
        raise RuntimeError(f"Security integration failed: {e}") from e
