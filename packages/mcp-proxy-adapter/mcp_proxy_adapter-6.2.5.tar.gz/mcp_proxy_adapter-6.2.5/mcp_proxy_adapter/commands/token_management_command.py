"""
Token Management Commands

This module provides commands for managing JWT and API tokens:
- Token creation
- Token validation
- Token revocation
- Token listing
- Token refresh

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .base import Command
from .result import SuccessResult, ErrorResult, CommandResult
from ..core.auth_validator import AuthValidator


class TokenManagementCommand(Command):
    """
    Token management commands.
    
    Provides commands for creating, validating, revoking, listing, and refreshing tokens.
    Supports both JWT and API tokens.
    """
    
    def __init__(self):
        """Initialize token management command."""
        super().__init__()
        self.auth_validator = AuthValidator()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        from ...config import config
        self.token_config = config.get("ssl", {}).get("token_auth", {})
        self.tokens_file = self.token_config.get("tokens_file", "tokens.json")
        self.token_expiry = self.token_config.get("token_expiry", 3600)
        self.jwt_secret = self.token_config.get("jwt_secret", "")
        self.jwt_algorithm = self.token_config.get("jwt_algorithm", "HS256")
    
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute token management command.
        
        Args:
            **kwargs: Command parameters containing:
                - method: Command method (token_create, token_validate, token_revoke, token_list, token_refresh)
                - token_type: Type of token for creation (jwt/api)
                - token_data: Token data for creation
                - token: Token string for validation/revocation/refresh
                - active_only: Boolean for token listing
        
        Returns:
            CommandResult with operation result
        """
        try:
            method = kwargs.get("method")
            
            if method == "token_create":
                token_type = kwargs.get("token_type", "api")
                token_data = kwargs.get("token_data", {})
                return await self.token_create(token_type, token_data)
            elif method == "token_validate":
                token = kwargs.get("token")
                token_type = kwargs.get("token_type", "auto")
                return await self.token_validate(token, token_type)
            elif method == "token_revoke":
                token = kwargs.get("token")
                return await self.token_revoke(token)
            elif method == "token_list":
                active_only = kwargs.get("active_only", True)
                return await self.token_list(active_only)
            elif method == "token_refresh":
                token = kwargs.get("token")
                return await self.token_refresh(token)
            else:
                return ErrorResult(
                    message=f"Unknown method: {method}",
                    code=-32601
                )
                
        except Exception as e:
            self.logger.error(f"Token management command execution error: {e}")
            return ErrorResult(
                message=f"Token management command failed: {str(e)}",
                code=-32603
            )
    
    async def token_create(self, token_type: str, token_data: Dict[str, Any]) -> Union[SuccessResult, ErrorResult]:
        """
        Create a new token.
        
        Args:
            token_type: Type of token (jwt/api)
            token_data: Token data dictionary containing:
                - roles: List of roles for the token
                - expires_in: Token expiration time in seconds (optional)
                - description: Token description (optional)
                - user_id: User ID associated with token (optional)
        
        Returns:
            CommandResult with created token information
        """
        try:
            if token_type not in ["jwt", "api"]:
                return ErrorResult(
                    message=f"Unsupported token type: {token_type}",
                    code=-32602
                )
            
            if token_type == "jwt":
                return await self._create_jwt_token(token_data)
            else:
                return await self._create_api_token(token_data)
                
        except Exception as e:
            self.logger.error(f"Token creation error: {e}")
            return ErrorResult(
                message=f"Token creation failed: {str(e)}",
                code=-32603
            )
    
    async def token_validate(self, token: str, token_type: str = "auto") -> Union[SuccessResult, ErrorResult]:
        """
        Validate a token.
        
        Args:
            token: Token string to validate
            token_type: Type of token (auto/jwt/api)
        
        Returns:
            CommandResult with validation status and token information
        """
        try:
            if not token:
                return ErrorResult(
                    message="Token not provided",
                    code=-32602
                )
            
            # Auto-detect token type if not specified
            if token_type == "auto":
                token_type = "jwt" if self._is_jwt_token(token) else "api"
            
            # Use AuthValidator for validation
            result = self.auth_validator.validate_token(token, token_type)
            
            if result.is_valid:
                return SuccessResult(
                    data={
                        "valid": True,
                        "token_type": token_type,
                        "roles": result.roles,
                        "expires_at": self._get_token_expiry(token, token_type)
                    }
                )
            else:
                error_data = result.to_json_rpc_error()
                return ErrorResult(
                    message=error_data["message"],
                    code=error_data["code"]
                )
                
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return ErrorResult(
                message=f"Token validation failed: {str(e)}",
                code=-32603
            )
    
    async def token_revoke(self, token: str) -> Union[SuccessResult, ErrorResult]:
        """
        Revoke a token.
        
        Args:
            token: Token string to revoke
        
        Returns:
            CommandResult with revocation status
        """
        try:
            if not token:
                return ErrorResult(
                    message="Token not provided",
                    code=-32602
                )
            
            # Load current tokens
            tokens = self._load_tokens()
            
            # Check if token exists
            if token not in tokens:
                return ErrorResult(
                    message="Token not found",
                    code=-32011
                )
            
            # Mark token as revoked
            tokens[token]["active"] = False
            tokens[token]["revoked_at"] = time.time()
            tokens[token]["revoked_by"] = "system"
            
            # Save updated tokens
            self._save_tokens(tokens)
            
            return SuccessResult(
                data={
                    "revoked": True,
                    "token": token,
                    "revoked_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Token revocation error: {e}")
            return ErrorResult(
                message=f"Token revocation failed: {str(e)}",
                code=-32603
            )
    
    async def token_list(self, active_only: bool = True) -> Union[SuccessResult, ErrorResult]:
        """
        List all tokens.
        
        Args:
            active_only: If True, return only active tokens
        
        Returns:
            CommandResult with list of tokens
        """
        try:
            # Load tokens
            tokens = self._load_tokens()
            
            # Filter tokens if requested
            if active_only:
                tokens = {k: v for k, v in tokens.items() if v.get("active", True)}
            
            # Prepare token list (without sensitive data)
            token_list = []
            for token_id, token_data in tokens.items():
                token_info = {
                    "id": token_id,
                    "type": token_data.get("type", "api"),
                    "roles": token_data.get("roles", []),
                    "active": token_data.get("active", True),
                    "created_at": token_data.get("created_at"),
                    "expires_at": token_data.get("expires_at"),
                    "description": token_data.get("description", ""),
                    "user_id": token_data.get("user_id")
                }
                
                if "revoked_at" in token_data:
                    token_info["revoked_at"] = token_data["revoked_at"]
                
                token_list.append(token_info)
            
            return SuccessResult(
                data={
                    "tokens": token_list,
                    "count": len(token_list),
                    "active_only": active_only
                }
            )
            
        except Exception as e:
            self.logger.error(f"Token listing error: {e}")
            return ErrorResult(
                message=f"Token listing failed: {str(e)}",
                code=-32603
            )
    
    async def token_refresh(self, token: str) -> Union[SuccessResult, ErrorResult]:
        """
        Refresh a token.
        
        Args:
            token: Token string to refresh
        
        Returns:
            CommandResult with refreshed token information
        """
        try:
            if not token:
                return ErrorResult(
                    message="Token not provided",
                    code=-32602
                )
            
            # Load current tokens
            tokens = self._load_tokens()
            
            # Check if token exists and is active
            if token not in tokens:
                return ErrorResult(
                    message="Token not found",
                    code=-32011
                )
            
            token_data = tokens[token]
            if not token_data.get("active", True):
                return ErrorResult(
                    message="Token is revoked",
                    code=-32011
                )
            
            # Check if token has expired
            if "expires_at" in token_data and time.time() > token_data["expires_at"]:
                return ErrorResult(
                    message="Token has expired",
                    code=-32010
                )
            
            # Create new token with same data
            new_token_data = {
                "type": token_data.get("type", "api"),
                "roles": token_data.get("roles", []),
                "active": True,
                "created_at": time.time(),
                "expires_at": time.time() + self.token_expiry,
                "description": token_data.get("description", ""),
                "user_id": token_data.get("user_id"),
                "refreshed_from": token
            }
            
            # Generate new token ID
            new_token_id = str(uuid.uuid4())
            tokens[new_token_id] = new_token_data
            
            # Revoke old token
            tokens[token]["active"] = False
            tokens[token]["refreshed_to"] = new_token_id
            tokens[token]["refreshed_at"] = time.time()
            
            # Save updated tokens
            self._save_tokens(tokens)
            
            return SuccessResult(
                data={
                    "refreshed": True,
                    "old_token": token,
                    "new_token": new_token_id,
                    "expires_at": new_token_data["expires_at"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Token refresh error: {e}")
            return ErrorResult(
                message=f"Token refresh failed: {str(e)}",
                code=-32603
            )
    
    async def _create_jwt_token(self, token_data: Dict[str, Any]) -> Union[SuccessResult, ErrorResult]:
        """
        Create JWT token.
        
        Args:
            token_data: Token data dictionary
        
        Returns:
            CommandResult with JWT token
        """
        try:
            # This is a placeholder for JWT creation
            # In a real implementation, you would use a JWT library like PyJWT
            
            # For now, create a simple token structure
            token_id = str(uuid.uuid4())
            expires_in = token_data.get("expires_in", self.token_expiry)
            
            jwt_token_data = {
                "jti": token_id,
                "sub": token_data.get("user_id", "system"),
                "roles": token_data.get("roles", []),
                "exp": time.time() + expires_in,
                "iat": time.time(),
                "iss": "mcp_proxy_adapter"
            }
            
            # In a real implementation, you would encode this as JWT
            # For now, return the token data
            return SuccessResult(
                data={
                    "token": token_id,
                    "token_type": "jwt",
                    "expires_at": jwt_token_data["exp"],
                    "roles": jwt_token_data["roles"],
                    "user_id": jwt_token_data["sub"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"JWT token creation error: {e}")
            return ErrorResult(
                message=f"JWT token creation failed: {str(e)}",
                code=-32603
            )
    
    async def _create_api_token(self, token_data: Dict[str, Any]) -> Union[SuccessResult, ErrorResult]:
        """
        Create API token.
        
        Args:
            token_data: Token data dictionary
        
        Returns:
            CommandResult with API token
        """
        try:
            # Generate token ID
            token_id = str(uuid.uuid4())
            expires_in = token_data.get("expires_in", self.token_expiry)
            
            # Create token data
            api_token_data = {
                "type": "api",
                "roles": token_data.get("roles", []),
                "active": True,
                "created_at": time.time(),
                "expires_at": time.time() + expires_in,
                "description": token_data.get("description", ""),
                "user_id": token_data.get("user_id")
            }
            
            # Load current tokens and add new token
            tokens = self._load_tokens()
            tokens[token_id] = api_token_data
            self._save_tokens(tokens)
            
            return SuccessResult(
                data={
                    "token": token_id,
                    "token_type": "api",
                    "expires_at": api_token_data["expires_at"],
                    "roles": api_token_data["roles"],
                    "user_id": api_token_data["user_id"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"API token creation error: {e}")
            return ErrorResult(
                message=f"API token creation failed: {str(e)}",
                code=-32603
            )
    
    def _is_jwt_token(self, token: str) -> bool:
        """
        Check if token is JWT format.
        
        Args:
            token: Token string
        
        Returns:
            True if token appears to be JWT, False otherwise
        """
        parts = token.split('.')
        return len(parts) == 3
    
    def _get_token_expiry(self, token: str, token_type: str) -> Optional[float]:
        """
        Get token expiry time.
        
        Args:
            token: Token string
            token_type: Type of token
        
        Returns:
            Expiry timestamp or None
        """
        try:
            if token_type == "api":
                tokens = self._load_tokens()
                if token in tokens:
                    return tokens[token].get("expires_at")
            
            # For JWT tokens, this would require decoding
            # For now, return None
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get token expiry: {e}")
            return None
    
    def _load_tokens(self) -> Dict[str, Any]:
        """
        Load tokens from file.
        
        Returns:
            Dictionary of tokens
        """
        try:
            if not self.tokens_file or not Path(self.tokens_file).exists():
                return {}
            
            with open(self.tokens_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to load tokens: {e}")
            return {}
    
    def _save_tokens(self, tokens: Dict[str, Any]) -> None:
        """
        Save tokens to file.
        
        Args:
            tokens: Dictionary of tokens to save
        """
        try:
            # Ensure directory exists
            Path(self.tokens_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save tokens: {e}")
            raise 