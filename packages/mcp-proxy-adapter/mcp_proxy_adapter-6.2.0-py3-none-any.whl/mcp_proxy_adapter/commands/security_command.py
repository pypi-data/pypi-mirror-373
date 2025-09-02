"""
Security Command - Direct Framework Integration

This command provides direct access to mcp_security_framework functionality
through JSON-RPC interface.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import Command
from .result import CommandResult, SuccessResult, ErrorResult
from mcp_proxy_adapter.core.security_integration import create_security_integration

logger = logging.getLogger(__name__)


class SecurityResult(CommandResult):
    """Result class for security operations."""
    
    def __init__(self, operation: str, success: bool, data: Dict[str, Any] = None, error: str = None):
        """
        Initialize security result.
        
        Args:
            operation: Security operation performed
            success: Whether operation was successful
            data: Operation data
            error: Error message if any
        """
        self.operation = operation
        self.success = success
        self.data = data or {}
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "success": self.success,
            "data": self.data,
            "error": self.error
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get result schema."""
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "description": "Security operation performed"},
                "success": {"type": "boolean", "description": "Whether operation was successful"},
                "data": {"type": "object", "description": "Operation data"},
                "error": {"type": "string", "description": "Error message if any"}
            },
            "required": ["operation", "success"]
        }


class SecurityCommand(Command):
    """
    Security command using mcp_security_framework.
    
    Provides direct access to security framework functionality:
    - Authentication (API key, JWT, certificate)
    - Certificate management
    - Permission management
    - Rate limiting
    """
    
    # Command metadata
    name = "security"
    version = "1.0.0"
    descr = "Security operations using mcp_security_framework"
    category = "security"
    author = "MCP Proxy Adapter Team"
    email = "team@mcp-proxy-adapter.com"
    source_url = "https://github.com/mcp-proxy-adapter"
    result_class = SecurityResult
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize security command."""
        super().__init__()
        self.config = config
        self.security_integration = create_security_integration(config)
        
        if not self.security_integration:
            logger.warning("Security framework not available, security command will fail")
    
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute security command.
        
        Args:
            **kwargs: Command parameters including:
                - action: Action to perform (auth, cert, permission, rate_limit, status)
                - method: Authentication method (api_key, jwt, certificate)
                - api_key: API key for authentication
                - token: JWT token for authentication
                - cert_path: Certificate path for operations
                - common_name: Common name for certificate creation
                - user_id: User ID for permission operations
                - permission: Permission to check
                - role: Role for operations
                - identifier: Identifier for rate limiting
                
        Returns:
            CommandResult with security operation status
        """
        if not self.security_integration:
            return SecurityResult(
                operation="security",
                success=False,
                error="Security framework not available"
            )
        
        action = kwargs.get("action", "status")
        
        try:
            if action == "auth":
                return await self._handle_auth(kwargs)
            elif action == "cert":
                return await self._handle_certificate(kwargs)
            elif action == "permission":
                return await self._handle_permission(kwargs)
            elif action == "rate_limit":
                return await self._handle_rate_limit(kwargs)
            elif action == "status":
                return await self._handle_status(kwargs)
            else:
                return SecurityResult(
                    operation=action,
                    success=False,
                    error=f"Unknown action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Security command error: {e}")
            return SecurityResult(
                operation=action,
                success=False,
                error=f"Security operation failed: {str(e)}"
            )
    
    async def _handle_auth(self, kwargs: Dict[str, Any]) -> SecurityResult:
        """Handle authentication operations."""
        method = kwargs.get("method", "api_key")
        
        if method == "api_key":
            api_key = kwargs.get("api_key")
            if not api_key:
                return SecurityResult(
                    operation="auth_api_key",
                    success=False,
                    error="API key required"
                )
            
            result = await self.security_integration.authenticate_api_key(api_key)
            return SecurityResult(
                operation="auth_api_key",
                success=result.is_valid,
                data={
                    "user_id": result.user_id,
                    "roles": result.roles,
                    "permissions": result.permissions
                },
                error=result.error_message if not result.is_valid else None
            )
        
        elif method == "jwt":
            token = kwargs.get("token")
            if not token:
                return SecurityResult(
                    operation="auth_jwt",
                    success=False,
                    error="JWT token required"
                )
            
            result = await self.security_integration.authenticate_jwt(token)
            return SecurityResult(
                operation="auth_jwt",
                success=result.is_valid,
                data={
                    "user_id": result.user_id,
                    "roles": result.roles,
                    "permissions": result.permissions
                },
                error=result.error_message if not result.is_valid else None
            )
        
        elif method == "certificate":
            cert_path = kwargs.get("cert_path")
            if not cert_path:
                return SecurityResult(
                    operation="auth_certificate",
                    success=False,
                    error="Certificate path required"
                )
            
            # Read certificate data
            try:
                with open(cert_path, 'rb') as f:
                    cert_data = f.read()
                
                result = await self.security_integration.authenticate_certificate(cert_data)
                return SecurityResult(
                    operation="auth_certificate",
                    success=result.is_valid,
                    data={
                        "user_id": result.user_id,
                        "roles": result.roles,
                        "permissions": result.permissions
                    },
                    error=result.error_message if not result.is_valid else None
                )
            except Exception as e:
                return SecurityResult(
                    operation="auth_certificate",
                    success=False,
                    error=f"Failed to read certificate: {str(e)}"
                )
        
        else:
            return SecurityResult(
                operation="auth",
                success=False,
                error=f"Unknown authentication method: {method}"
            )
    
    async def _handle_certificate(self, kwargs: Dict[str, Any]) -> SecurityResult:
        """Handle certificate operations."""
        cert_action = kwargs.get("cert_action", "validate")
        
        if cert_action == "create_ca":
            common_name = kwargs.get("common_name")
            if not common_name:
                return SecurityResult(
                    operation="cert_create_ca",
                    success=False,
                    error="Common name required"
                )
            
            try:
                cert_pair = await self.security_integration.create_ca_certificate(common_name)
                return SecurityResult(
                    operation="cert_create_ca",
                    success=True,
                    data={
                        "cert_path": str(cert_pair.cert_path),
                        "key_path": str(cert_pair.key_path),
                        "common_name": common_name
                    }
                )
            except Exception as e:
                return SecurityResult(
                    operation="cert_create_ca",
                    success=False,
                    error=f"Failed to create CA certificate: {str(e)}"
                )
        
        elif cert_action == "create_client":
            common_name = kwargs.get("common_name")
            if not common_name:
                return SecurityResult(
                    operation="cert_create_client",
                    success=False,
                    error="Common name required"
                )
            
            try:
                cert_pair = await self.security_integration.create_client_certificate(common_name)
                return SecurityResult(
                    operation="cert_create_client",
                    success=True,
                    data={
                        "cert_path": str(cert_pair.cert_path),
                        "key_path": str(cert_pair.key_path),
                        "common_name": common_name
                    }
                )
            except Exception as e:
                return SecurityResult(
                    operation="cert_create_client",
                    success=False,
                    error=f"Failed to create client certificate: {str(e)}"
                )
        
        elif cert_action == "validate":
            cert_path = kwargs.get("cert_path")
            if not cert_path:
                return SecurityResult(
                    operation="cert_validate",
                    success=False,
                    error="Certificate path required"
                )
            
            try:
                is_valid = await self.security_integration.validate_certificate(cert_path)
                return SecurityResult(
                    operation="cert_validate",
                    success=is_valid,
                    data={"cert_path": cert_path, "valid": is_valid}
                )
            except Exception as e:
                return SecurityResult(
                    operation="cert_validate",
                    success=False,
                    error=f"Failed to validate certificate: {str(e)}"
                )
        
        elif cert_action == "extract_roles":
            cert_path = kwargs.get("cert_path")
            if not cert_path:
                return SecurityResult(
                    operation="cert_extract_roles",
                    success=False,
                    error="Certificate path required"
                )
            
            try:
                roles = await self.security_integration.extract_roles_from_certificate(cert_path)
                return SecurityResult(
                    operation="cert_extract_roles",
                    success=True,
                    data={"cert_path": cert_path, "roles": roles}
                )
            except Exception as e:
                return SecurityResult(
                    operation="cert_extract_roles",
                    success=False,
                    error=f"Failed to extract roles: {str(e)}"
                )
        
        else:
            return SecurityResult(
                operation="cert",
                success=False,
                error=f"Unknown certificate action: {cert_action}"
            )
    
    async def _handle_permission(self, kwargs: Dict[str, Any]) -> SecurityResult:
        """Handle permission operations."""
        perm_action = kwargs.get("perm_action", "check")
        user_id = kwargs.get("user_id")
        
        if not user_id:
            return SecurityResult(
                operation="permission",
                success=False,
                error="User ID required"
            )
        
        if perm_action == "check":
            permission = kwargs.get("permission")
            if not permission:
                return SecurityResult(
                    operation="permission_check",
                    success=False,
                    error="Permission required"
                )
            
            try:
                has_permission = await self.security_integration.check_permission(user_id, permission)
                return SecurityResult(
                    operation="permission_check",
                    success=True,
                    data={
                        "user_id": user_id,
                        "permission": permission,
                        "has_permission": has_permission
                    }
                )
            except Exception as e:
                return SecurityResult(
                    operation="permission_check",
                    success=False,
                    error=f"Failed to check permission: {str(e)}"
                )
        
        elif perm_action == "get_roles":
            try:
                roles = await self.security_integration.get_user_roles(user_id)
                return SecurityResult(
                    operation="permission_get_roles",
                    success=True,
                    data={"user_id": user_id, "roles": roles}
                )
            except Exception as e:
                return SecurityResult(
                    operation="permission_get_roles",
                    success=False,
                    error=f"Failed to get user roles: {str(e)}"
                )
        
        elif perm_action == "add_role":
            role = kwargs.get("role")
            if not role:
                return SecurityResult(
                    operation="permission_add_role",
                    success=False,
                    error="Role required"
                )
            
            try:
                success = await self.security_integration.add_user_role(user_id, role)
                return SecurityResult(
                    operation="permission_add_role",
                    success=success,
                    data={"user_id": user_id, "role": role, "added": success}
                )
            except Exception as e:
                return SecurityResult(
                    operation="permission_add_role",
                    success=False,
                    error=f"Failed to add role: {str(e)}"
                )
        
        else:
            return SecurityResult(
                operation="permission",
                success=False,
                error=f"Unknown permission action: {perm_action}"
            )
    
    async def _handle_rate_limit(self, kwargs: Dict[str, Any]) -> SecurityResult:
        """Handle rate limiting operations."""
        identifier = kwargs.get("identifier")
        if not identifier:
            return SecurityResult(
                operation="rate_limit",
                success=False,
                error="Identifier required"
            )
        
        try:
            # Check rate limit
            is_allowed = await self.security_integration.check_rate_limit(identifier)
            
            if is_allowed:
                # Increment counter
                await self.security_integration.increment_rate_limit(identifier)
            
            # Get rate limit info
            info = await self.security_integration.get_rate_limit_info(identifier)
            
            return SecurityResult(
                operation="rate_limit_check",
                success=True,
                data={
                    "identifier": identifier,
                    "allowed": is_allowed,
                    "info": info
                }
            )
        except Exception as e:
            return SecurityResult(
                operation="rate_limit_check",
                success=False,
                error=f"Failed to check rate limit: {str(e)}"
            )
    
    async def _handle_status(self, kwargs: Dict[str, Any]) -> SecurityResult:
        """Handle status operations."""
        try:
            security_config = self.security_integration.get_security_config()
            
            return SecurityResult(
                operation="status",
                success=True,
                data={
                    "security_enabled": self.security_integration.is_security_enabled(),
                    "public_paths": self.security_integration.get_public_paths(),
                    "auth_enabled": security_config.auth.enabled,
                    "ssl_enabled": security_config.ssl.enabled,
                    "permissions_enabled": security_config.permissions.enabled,
                    "rate_limit_enabled": security_config.rate_limit.enabled,
                    "certificates_enabled": security_config.certificates.enabled
                }
            )
        except Exception as e:
            return SecurityResult(
                operation="status",
                success=False,
                error=f"Failed to get status: {str(e)}"
            )
