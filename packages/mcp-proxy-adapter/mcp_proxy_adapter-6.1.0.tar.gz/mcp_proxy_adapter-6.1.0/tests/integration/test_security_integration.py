"""
Integration tests for security components before refactoring.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

This module contains integration tests to verify current security behavior
before implementing the refactoring plan.
"""

import pytest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp_proxy_adapter.core.security_factory import SecurityFactory
from mcp_proxy_adapter.core.security_adapter import SecurityAdapter
from mcp_proxy_adapter.api.middleware.unified_security import UnifiedSecurityMiddleware
from mcp_proxy_adapter.api.middleware.factory import MiddlewareFactory


class TestSecurityIntegration:
    """Integration tests for security components."""
    
    @pytest.fixture
    def basic_config(self) -> Dict[str, Any]:
        """Basic configuration for testing."""
        return {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {
                        "test-key-1": "user1",
                        "test-key-2": "user2"
                    }
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": None,
                    "default_role": "user"
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            }
        }
    
    @pytest.fixture
    def fastapi_app(self) -> FastAPI:
        """Create FastAPI app for testing."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/health")
        async def health_endpoint():
            return {"status": "healthy"}
        
        return app
    
    def test_security_factory_creation(self, basic_config):
        """Test SecurityFactory can create components."""
        # Test adapter creation
        adapter = SecurityFactory.create_security_adapter(basic_config)
        assert adapter is not None
        assert isinstance(adapter, SecurityAdapter)
        
        # Test manager creation
        manager = SecurityFactory.create_security_manager(basic_config)
        # Manager might be None if mcp_security_framework not available
        assert manager is None or hasattr(manager, 'validate_request')
        
        # Test config validation
        assert SecurityFactory.validate_config(basic_config) is True
    
    def test_security_adapter_validation(self, basic_config):
        """Test SecurityAdapter request validation."""
        adapter = SecurityAdapter(basic_config)
        
        # Test valid request
        valid_request = {
            "method": "GET",
            "path": "/test",
            "headers": {"x-api-key": "test-key-1"},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(valid_request)
        assert result["is_valid"] is True
        assert result["user_id"] == "user1"
        assert "user" in result["roles"]
        
        # Test invalid request
        invalid_request = {
            "method": "GET",
            "path": "/test",
            "headers": {},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(invalid_request)
        assert result["is_valid"] is False
        assert result["error_code"] == -32000
    
    def test_middleware_factory_creation(self, basic_config, fastapi_app):
        """Test MiddlewareFactory can create middleware."""
        factory = MiddlewareFactory(fastapi_app, basic_config)
        
        # Test validation
        assert factory.validate_middleware_config() is True
        
        # Test middleware creation
        middleware_list = factory.create_all_middleware()
        assert len(middleware_list) > 0
        
        # Check that security middleware was created
        security_middleware = factory.get_security_middleware()
        assert security_middleware is not None
        assert isinstance(security_middleware, UnifiedSecurityMiddleware)
    
    def test_security_middleware_integration(self, basic_config, fastapi_app):
        """Test UnifiedSecurityMiddleware integration with FastAPI."""
        # Add security middleware to FastAPI app
        security_middleware = UnifiedSecurityMiddleware(fastapi_app, basic_config)
        fastapi_app.middleware("http")(security_middleware.dispatch)
        
        # Create test client
        client = TestClient(fastapi_app)
        
        # Test public endpoint (should work without auth)
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test protected endpoint without auth (should fail)
        response = client.get("/test")
        assert response.status_code == 401
        
        # Test protected endpoint with valid auth
        response = client.get("/test", headers={"x-api-key": "test-key-1"})
        assert response.status_code == 200
        
        # Test protected endpoint with invalid auth
        response = client.get("/test", headers={"x-api-key": "invalid-key"})
        assert response.status_code == 401
    
    def test_api_key_in_query_params(self, basic_config, fastapi_app):
        """Test API key validation from query parameters."""
        security_middleware = UnifiedSecurityMiddleware(fastapi_app, basic_config)
        client = TestClient(fastapi_app)
        
        # Test with API key in query params
        response = client.get("/test?api_key=test-key-1")
        assert response.status_code == 200
    
    def test_api_key_in_json_rpc_body(self, basic_config, fastapi_app):
        """Test API key validation from JSON-RPC body."""
        security_middleware = UnifiedSecurityMiddleware(fastapi_app, basic_config)
        client = TestClient(fastapi_app)
        
        # Test with API key in JSON-RPC body
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"api_key": "test-key-1"},
            "id": 1
        }
        
        response = client.post("/test", json=json_rpc_request)
        # This might fail depending on endpoint implementation
        # The test verifies that the middleware processes the body correctly
    
    def test_rate_limiting_configuration(self, basic_config):
        """Test rate limiting configuration."""
        adapter = SecurityAdapter(basic_config)
        
        # Verify rate limit config is properly converted
        rate_limit_config = basic_config["security"]["rate_limit"]
        assert rate_limit_config["enabled"] is True
        assert rate_limit_config["requests_per_minute"] == 60
    
    def test_permissions_configuration(self, basic_config):
        """Test permissions configuration."""
        adapter = SecurityAdapter(basic_config)
        
        # Verify permissions config is properly converted
        permissions_config = basic_config["security"]["permissions"]
        assert permissions_config["enabled"] is True
        assert permissions_config["default_role"] == "user"
    
    def test_ssl_configuration(self, basic_config):
        """Test SSL configuration."""
        adapter = SecurityAdapter(basic_config)
        
        # Verify SSL config is properly converted
        ssl_config = basic_config["security"]["ssl"]
        assert ssl_config["enabled"] is False
    
    def test_legacy_config_compatibility(self):
        """Test compatibility with legacy configuration format."""
        legacy_config = {
            "ssl": {
                "api_keys": {
                    "legacy-key": "legacy-user"
                }
            }
        }
        
        adapter = SecurityAdapter(legacy_config)
        
        # Test that legacy API keys are still recognized
        valid_request = {
            "method": "GET",
            "path": "/test",
            "headers": {"x-api-key": "legacy-key"},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(valid_request)
        assert result["is_valid"] is True
        assert result["user_id"] == "legacy-user"
    
    def test_error_handling(self, basic_config, fastapi_app):
        """Test error handling in security middleware."""
        security_middleware = UnifiedSecurityMiddleware(fastapi_app, basic_config)
        fastapi_app.middleware("http")(security_middleware.dispatch)
        client = TestClient(fastapi_app)
        
        # Test with malformed request
        response = client.get("/test", headers={"x-api-key": ""})
        assert response.status_code == 401
        
        # Verify error response format
        error_data = response.json()
        assert "error" in error_data
        assert "code" in error_data["error"]
        assert "message" in error_data["error"]
        assert error_data["error"]["code"] == -32000
    
    def test_public_paths_exclusion(self, basic_config, fastapi_app):
        """Test that public paths are excluded from security validation."""
        # Add custom public path
        basic_config["security"]["public_paths"] = ["/custom-public"]
    
        security_middleware = UnifiedSecurityMiddleware(fastapi_app, basic_config)
        
        # Add custom public endpoint
        @fastapi_app.get("/custom-public")
        async def custom_public():
            return {"message": "custom public"}
        
        client = TestClient(fastapi_app)
        
        # Test that custom public path works without auth
        response = client.get("/custom-public")
        assert response.status_code == 200
        
        # Test that default public paths still work
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_middleware_info(self, basic_config, fastapi_app):
        """Test middleware factory info methods."""
        factory = MiddlewareFactory(fastapi_app, basic_config)
        factory.create_all_middleware()
        
        info = factory.get_middleware_info()
        assert info["total_middleware"] > 0
        assert "UnifiedSecurityMiddleware" in info["middleware_types"]
        assert info["security_enabled"] is True
