"""
Unit tests for UnifiedSecurityMiddleware.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

This module contains unit tests for the UnifiedSecurityMiddleware class.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from mcp_proxy_adapter.api.middleware.unified_security import (
    UnifiedSecurityMiddleware,
    SecurityValidationError
)


class TestUnifiedSecurityMiddleware:
    """Test cases for UnifiedSecurityMiddleware."""
    
    @pytest.fixture
    def config(self) -> Dict[str, Any]:
        """Test configuration."""
        return {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {
                        "test-key": "test-user"
                    }
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": None
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                },
                "public_paths": [
                    "/health",
                    "/docs"
                ]
            }
        }
    
    @pytest.fixture
    def app(self):
        """Mock FastAPI app."""
        return Mock()
    
    @pytest.fixture
    def middleware(self, app, config):
        """Create UnifiedSecurityMiddleware instance."""
        return UnifiedSecurityMiddleware(app, config)
    
    def test_initialization(self, middleware):
        """Test middleware initialization."""
        assert middleware is not None
        assert middleware.security_enabled is True
        assert "/health" in middleware.public_paths
        assert "/docs" in middleware.public_paths
        assert hasattr(middleware, 'config_adapter')
        assert hasattr(middleware, 'rate_limit_cache')
    
    def test_initialization_security_disabled(self, app):
        """Test middleware initialization with security disabled."""
        config = {
            "security": {
                "enabled": False
            }
        }
        middleware = UnifiedSecurityMiddleware(app, config)
        
        assert middleware.security_enabled is False
    
    def test_is_public_path(self, middleware):
        """Test public path detection."""
        assert middleware._is_public_path("/health") is True
        assert middleware._is_public_path("/docs") is True
        assert middleware._is_public_path("/api/test") is False
        assert middleware._is_public_path("/health/status") is True
    
    def test_get_client_ip(self, middleware):
        """Test client IP extraction."""
        request = Mock()
        request.headers = {
            "X-Forwarded-For": "192.168.1.1, 10.0.0.1"
        }
        request.client = None
        
        ip = middleware._get_client_ip(request)
        assert ip == "192.168.1.1"
    
    def test_get_client_ip_real_ip(self, middleware):
        """Test client IP extraction with X-Real-IP header."""
        request = Mock()
        request.headers = {
            "X-Real-IP": "10.0.0.1"
        }
        request.client = None
        
        ip = middleware._get_client_ip(request)
        assert ip == "10.0.0.1"
    
    def test_get_client_ip_client_host(self, middleware):
        """Test client IP extraction from client host."""
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        
        ip = middleware._get_client_ip(request)
        assert ip == "127.0.0.1"
    
    def test_get_client_ip_unknown(self, middleware):
        """Test client IP extraction when no IP available."""
        request = Mock()
        request.headers = {}
        request.client = None
        
        ip = middleware._get_client_ip(request)
        assert ip == "unknown"
    
    def test_get_api_keys(self, middleware):
        """Test API keys extraction."""
        api_keys = middleware._get_api_keys()
        assert "test-key" in api_keys
        assert api_keys["test-key"] == "test-user"
    
    def test_validate_authentication_valid(self, middleware):
        """Test valid authentication validation."""
        request_data = {
            "headers": {"x-api-key": "test-key"},
            "query_params": {},
            "body": {}
        }
        
        result = middleware._validate_authentication(request_data)
        
        assert result["is_valid"] is True
        assert result["user_id"] == "test-user"
        assert result["roles"] == ["user"]
    
    def test_validate_authentication_invalid(self, middleware):
        """Test invalid authentication validation."""
        request_data = {
            "headers": {"x-api-key": "invalid-key"},
            "query_params": {},
            "body": {}
        }
        
        result = middleware._validate_authentication(request_data)
        
        assert result["is_valid"] is False
        assert result["user_id"] is None
        assert result["error_code"] == -32000
    
    def test_validate_authentication_query_param(self, middleware):
        """Test authentication with API key in query parameter."""
        request_data = {
            "headers": {},
            "query_params": {"api_key": "test-key"},
            "body": {}
        }
        
        result = middleware._validate_authentication(request_data)
        
        assert result["is_valid"] is True
        assert result["user_id"] == "test-user"
    
    def test_validate_authentication_json_rpc_body(self, middleware):
        """Test authentication with API key in JSON-RPC body."""
        request_data = {
            "headers": {},
            "query_params": {},
            "body": {
                "params": {
                    "api_key": "test-key"
                }
            }
        }
        
        result = middleware._validate_authentication(request_data)
        
        assert result["is_valid"] is True
        assert result["user_id"] == "test-user"
    
    def test_validate_rate_limiting_disabled(self, middleware):
        """Test rate limiting when disabled."""
        config = {
            "security": {
                "rate_limit": {
                    "enabled": False
                }
            }
        }
        middleware.config = config
        
        request_data = {
            "client_ip": "127.0.0.1"
        }
        
        result = middleware._validate_rate_limiting(request_data)
        
        assert result["is_valid"] is True
    
    def test_validate_rate_limiting_enabled(self, middleware):
        """Test rate limiting when enabled."""
        request_data = {
            "client_ip": "127.0.0.1"
        }
        
        # First request should be valid
        result = middleware._validate_rate_limiting(request_data)
        assert result["is_valid"] is True
        
        # Multiple requests should still be valid (within limit)
        for _ in range(10):
            result = middleware._validate_rate_limiting(request_data)
            assert result["is_valid"] is True
    
    def test_validate_permissions_disabled(self, middleware):
        """Test permissions when disabled."""
        config = {
            "security": {
                "permissions": {
                    "enabled": False
                }
            }
        }
        middleware.config = config
        
        auth_result = {"is_valid": True}
        request_data = {}
        
        result = middleware._validate_permissions(request_data, auth_result)
        
        assert result["is_valid"] is True
    
    def test_validate_permissions_enabled_valid(self, middleware):
        """Test permissions when enabled and user is valid."""
        auth_result = {"is_valid": True}
        request_data = {}
        
        result = middleware._validate_permissions(request_data, auth_result)
        
        assert result["is_valid"] is True
    
    def test_validate_permissions_enabled_invalid(self, middleware):
        """Test permissions when enabled and user is invalid."""
        auth_result = {"is_valid": False}
        request_data = {}
        
        result = middleware._validate_permissions(request_data, auth_result)
        
        assert result["is_valid"] is False
        assert result["error_code"] == -32002
    
    def test_get_client_identifier(self, middleware):
        """Test client identifier generation."""
        request_data = {
            "client_ip": "192.168.1.1"
        }
        
        identifier = middleware._get_client_identifier(request_data)
        assert identifier == "192.168.1.1"
    
    def test_cleanup_rate_limit_cache(self, middleware):
        """Test rate limit cache cleanup."""
        # Add some test entries - some old, some new
        middleware.rate_limit_cache = {
            "client1": {"count": 1, "timestamp": 100},   # Old (should be cleaned)
            "client2": {"count": 2, "timestamp": 2000},  # New (should remain)
            "client3": {"count": 3, "timestamp": 500}    # New (should remain)
        }
        middleware.last_cleanup = 1000
        
        # Mock current time to trigger cleanup (more than 5 minutes later)
        # Current time: 4000, last cleanup: 1000, difference: 3000 seconds (50 minutes)
        with patch('mcp_proxy_adapter.api.middleware.unified_security.time.time', return_value=4000):
            middleware._cleanup_rate_limit_cache()
        
        # Should clean up old entries (older than 1 hour from current time)
        # Current time is 4000, window_start = 4000 - 3600 = 400
        # client1: timestamp 100 < 400 (old, should be cleaned)
        # client2: timestamp 2000 > 400 (new, should remain)
        # client3: timestamp 500 > 400 (new, should remain)
        assert len(middleware.rate_limit_cache) == 2
        assert "client1" not in middleware.rate_limit_cache
        assert "client2" in middleware.rate_limit_cache
        assert "client3" in middleware.rate_limit_cache
    
    def test_cleanup_rate_limit_cache_no_cleanup_needed(self, middleware):
        """Test rate limit cache cleanup when not needed."""
        # Add some test entries
        middleware.rate_limit_cache = {
            "client1": {"count": 1, "timestamp": 1000},
            "client2": {"count": 2, "timestamp": 2000}
        }
        middleware.last_cleanup = 1000
        
        # Mock current time to NOT trigger cleanup (less than 5 minutes later)
        # Current time: 1200, last cleanup: 1000, difference: 200 seconds (3.3 minutes)
        with patch('mcp_proxy_adapter.api.middleware.unified_security.time.time', return_value=1200):
            middleware._cleanup_rate_limit_cache()
        
        # Should NOT clean up entries (cleanup not triggered)
        assert len(middleware.rate_limit_cache) == 2
        assert "client1" in middleware.rate_limit_cache
        assert "client2" in middleware.rate_limit_cache
    
    def test_get_status_code_for_error(self, middleware):
        """Test error code to status code mapping."""
        assert middleware._get_status_code_for_error(-32000) == 401  # Authentication failed
        assert middleware._get_status_code_for_error(-32001) == 429  # Rate limit exceeded
        assert middleware._get_status_code_for_error(-32002) == 403  # Permission denied
        assert middleware._get_status_code_for_error(-32603) == 500  # Internal error
        assert middleware._get_status_code_for_error(-99999) == 500  # Unknown error
    
    @pytest.mark.asyncio
    async def test_extract_request_data_get(self, middleware):
        """Test request data extraction for GET request."""
        request = Mock()
        request.method = "GET"
        request.url.path = "/api/test"
        request.headers = {"content-type": "application/json"}
        request.query_params = {"param": "value"}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.body = AsyncMock(return_value=b"")
        
        request_data = await middleware._extract_request_data(request)
        
        assert request_data["method"] == "GET"
        assert request_data["path"] == "/api/test"
        assert request_data["headers"]["content-type"] == "application/json"
        assert request_data["query_params"]["param"] == "value"
        assert request_data["client_ip"] == "127.0.0.1"
        assert request_data["body"] == {}
    
    @pytest.mark.asyncio
    async def test_extract_request_data_post_json(self, middleware):
        """Test request data extraction for POST request with JSON body."""
        request = Mock()
        request.method = "POST"
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.body = AsyncMock(return_value=b'{"key": "value"}')
        
        request_data = await middleware._extract_request_data(request)
        
        assert request_data["method"] == "POST"
        assert request_data["body"]["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_extract_request_data_post_text(self, middleware):
        """Test request data extraction for POST request with text body."""
        request = Mock()
        request.method = "POST"
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.body = AsyncMock(return_value=b"plain text body")
        
        request_data = await middleware._extract_request_data(request)
        
        assert request_data["method"] == "POST"
        assert request_data["body"] == "plain text body"
    
    def test_get_user_roles(self, middleware):
        """Test getting user roles from request state."""
        request = Mock()
        request.state.user_roles = ["user", "admin"]
        
        roles = middleware.get_user_roles(request)
        assert roles == ["user", "admin"]
    
    def test_get_user_roles_none(self, middleware):
        """Test getting user roles when not set."""
        request = Mock()
        request.state = Mock()
        delattr(request.state, 'user_roles')
        
        roles = middleware.get_user_roles(request)
        assert roles == []
    
    def test_get_user_id(self, middleware):
        """Test getting user ID from request state."""
        request = Mock()
        request.state.user_id = "test-user"
        
        user_id = middleware.get_user_id(request)
        assert user_id == "test-user"
    
    def test_get_user_id_none(self, middleware):
        """Test getting user ID when not set."""
        request = Mock()
        request.state = Mock()
        delattr(request.state, 'user_id')
        
        user_id = middleware.get_user_id(request)
        assert user_id is None
    
    def test_is_security_validated(self, middleware):
        """Test checking if security is validated."""
        request = Mock()
        request.state.security_validated = True
        
        validated = middleware.is_security_validated(request)
        assert validated is True
    
    def test_is_security_validated_false(self, middleware):
        """Test checking if security is validated when false."""
        request = Mock()
        request.state = Mock()
        delattr(request.state, 'security_validated')
        
        validated = middleware.is_security_validated(request)
        assert validated is False
    
    def test_has_role(self, middleware):
        """Test checking if user has required role."""
        request = Mock()
        request.state.user_roles = ["user", "admin"]
        
        assert middleware.has_role(request, "user") is True
        assert middleware.has_role(request, "admin") is True
        assert middleware.has_role(request, "superuser") is False
    
    def test_has_role_wildcard(self, middleware):
        """Test checking if user has wildcard role."""
        request = Mock()
        request.state.user_roles = ["*"]
        
        assert middleware.has_role(request, "any-role") is True
    
    def test_has_any_role(self, middleware):
        """Test checking if user has any of required roles."""
        request = Mock()
        request.state.user_roles = ["user", "admin"]
        
        assert middleware.has_any_role(request, ["user", "superuser"]) is True
        assert middleware.has_any_role(request, ["admin", "superuser"]) is True
        assert middleware.has_any_role(request, ["superuser", "moderator"]) is False
    
    def test_has_any_role_wildcard(self, middleware):
        """Test checking if user has wildcard role."""
        request = Mock()
        request.state.user_roles = ["*"]
        
        assert middleware.has_any_role(request, ["any-role", "another-role"]) is True
    
    def test_get_security_status(self, middleware):
        """Test getting security status."""
        status = middleware.get_security_status()
        
        assert "security_enabled" in status
        assert "security_manager_available" in status
        assert "public_paths" in status
        assert "rate_limit_cache_size" in status
        assert "config_adapter" in status
        assert status["security_enabled"] is True
        assert status["config_adapter"] == "UnifiedConfigAdapter"


class TestSecurityValidationError:
    """Test cases for SecurityValidationError."""
    
    def test_initialization(self):
        """Test SecurityValidationError initialization."""
        error = SecurityValidationError("Test error", -32000)
        
        assert error.message == "Test error"
        assert error.error_code == -32000
        assert str(error) == "Test error"
    
    def test_inheritance(self):
        """Test that SecurityValidationError inherits from Exception."""
        error = SecurityValidationError("Test error", -32000)
        
        assert isinstance(error, Exception)
        assert isinstance(error, SecurityValidationError)
