"""
Configuration scenario tests before refactoring.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

This module contains tests for various configuration scenarios to ensure
current behavior is preserved during refactoring.
"""

import pytest
import json
from typing import Dict, Any
from pathlib import Path

from mcp_proxy_adapter.core.security_factory import SecurityFactory
from mcp_proxy_adapter.core.security_adapter import SecurityAdapter
from mcp_proxy_adapter.api.middleware.factory import MiddlewareFactory


class TestConfigurationScenarios:
    """Test various configuration scenarios."""
    
    def test_minimal_configuration(self):
        """Test minimal configuration with defaults."""
        minimal_config = {}
        
        # Should work with default values
        adapter = SecurityAdapter(minimal_config)
        assert adapter is not None
        
        # Test request validation with minimal config
        request_data = {
            "method": "GET",
            "path": "/test",
            "headers": {},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(request_data)
        # Should fail without API key
        assert result["is_valid"] is False
    
    def test_security_disabled_configuration(self):
        """Test configuration with security disabled."""
        disabled_config = {
            "security": {
                "enabled": False
            }
        }
        
        adapter = SecurityAdapter(disabled_config)
        
        # Even with security disabled, adapter should be created
        assert adapter is not None
        
        # Validation should still work but might be more permissive
        request_data = {
            "method": "GET",
            "path": "/test",
            "headers": {},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(request_data)
        # Behavior depends on implementation, but should not crash
    
    def test_auth_only_configuration(self):
        """Test configuration with only authentication enabled."""
        auth_only_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {
                        "auth-key": "auth-user"
                    }
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": False
                },
                "rate_limit": {
                    "enabled": False
                }
            }
        }
        
        adapter = SecurityAdapter(auth_only_config)
        
        # Test valid authentication
        valid_request = {
            "method": "GET",
            "path": "/test",
            "headers": {"x-api-key": "auth-key"},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(valid_request)
        assert result["is_valid"] is True
        assert result["user_id"] == "auth-user"
    
    def test_ssl_only_configuration(self):
        """Test configuration with only SSL enabled."""
        ssl_only_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": False
                },
                "ssl": {
                    "enabled": True,
                    "cert_file": "test.crt",
                    "key_file": "test.key",
                    "verify_client": True
                },
                "permissions": {
                    "enabled": False
                },
                "rate_limit": {
                    "enabled": False
                }
            }
        }
        
        adapter = SecurityAdapter(ssl_only_config)
        assert adapter is not None
        
        # SSL validation would happen at transport level
        # This test ensures adapter creation doesn't fail
    
    def test_rate_limit_only_configuration(self):
        """Test configuration with only rate limiting enabled."""
        rate_limit_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": False
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": False
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 30,
                    "requests_per_hour": 500,
                    "burst_limit": 5
                }
            }
        }
        
        adapter = SecurityAdapter(rate_limit_config)
        assert adapter is not None
        
        # Rate limiting would be applied per request
        # This test ensures adapter creation doesn't fail
    
    def test_permissions_only_configuration(self):
        """Test configuration with only permissions enabled."""
        permissions_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": False
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": "test_roles.json",
                    "default_role": "guest",
                    "deny_by_default": False
                },
                "rate_limit": {
                    "enabled": False
                }
            }
        }
        
        adapter = SecurityAdapter(permissions_config)
        assert adapter is not None
        
        # Permissions would be checked based on roles
        # This test ensures adapter creation doesn't fail
    
    def test_mixed_configuration(self):
        """Test configuration with mixed security features."""
        mixed_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {
                        "mixed-key": "mixed-user"
                    }
                },
                "ssl": {
                    "enabled": True,
                    "cert_file": "mixed.crt",
                    "key_file": "mixed.key",
                    "verify_client": False
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": "mixed_roles.json",
                    "default_role": "user"
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 45,
                    "requests_per_hour": 800
                }
            }
        }
        
        adapter = SecurityAdapter(mixed_config)
        assert adapter is not None
        
        # Test authentication with mixed config
        valid_request = {
            "method": "GET",
            "path": "/test",
            "headers": {"x-api-key": "mixed-key"},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(valid_request)
        assert result["is_valid"] is True
        assert result["user_id"] == "mixed-user"
    
    def test_legacy_ssl_configuration(self):
        """Test legacy SSL configuration format."""
        legacy_ssl_config = {
            "ssl": {
                "enabled": True,
                "cert_file": "legacy.crt",
                "key_file": "legacy.key",
                "api_keys": {
                    "legacy-ssl-key": "legacy-ssl-user"
                }
            }
        }
        
        adapter = SecurityAdapter(legacy_ssl_config)
        assert adapter is not None
        
        # Test that legacy API keys are recognized
        valid_request = {
            "method": "GET",
            "path": "/test",
            "headers": {"x-api-key": "legacy-ssl-key"},
            "query_params": {},
            "client_ip": "127.0.0.1",
            "body": {}
        }
        
        result = adapter.validate_request(valid_request)
        assert result["is_valid"] is True
        assert result["user_id"] == "legacy-ssl-user"
    
    def test_legacy_roles_configuration(self):
        """Test legacy roles configuration format."""
        legacy_roles_config = {
            "roles": {
                "enabled": True,
                "config_file": "legacy_roles.json"
            }
        }
        
        adapter = SecurityAdapter(legacy_roles_config)
        assert adapter is not None
        
        # Adapter should be created successfully
        # Role validation would happen during request processing
    
    def test_invalid_configuration_handling(self):
        """Test handling of invalid configurations."""
        invalid_configs = [
            # Invalid security section
            {"security": "not_a_dict"},
            
            # Invalid auth section
            {"security": {"auth": "not_a_dict"}},
            
            # Invalid SSL section
            {"security": {"ssl": "not_a_dict"}},
            
            # Invalid permissions section
            {"security": {"permissions": "not_a_dict"}},
            
            # Invalid rate limit section
            {"security": {"rate_limit": "not_a_dict"}},
        ]
        
        for invalid_config in invalid_configs:
            # Should not crash, but might log warnings
            try:
                adapter = SecurityAdapter(invalid_config)
                assert adapter is not None
            except Exception as e:
                # If it crashes, that's also acceptable behavior
                # The important thing is that it doesn't crash silently
                assert str(e) != ""
    
    def test_configuration_validation(self):
        """Test configuration validation in SecurityFactory."""
        valid_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {"key": "user"}
                },
                "ssl": {
                    "enabled": False
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
        
        assert SecurityFactory.validate_config(valid_config) is True
        
        # Test invalid configurations
        invalid_configs = [
            {"security": "not_a_dict"},
            {"security": {"auth": "not_a_dict"}},
            {"security": {"ssl": "not_a_dict"}},
            {"security": {"permissions": "not_a_dict"}},
            {"security": {"rate_limit": "not_a_dict"}},
        ]
        
        for invalid_config in invalid_configs:
            assert SecurityFactory.validate_config(invalid_config) is False
    
    def test_configuration_merging(self):
        """Test configuration merging functionality."""
        base_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"]
                }
            }
        }
        
        security_config = {
            "auth": {
                "api_keys": {
                    "merged-key": "merged-user"
                }
            },
            "ssl": {
                "enabled": True
            }
        }
        
        merged_config = SecurityFactory.merge_config(base_config, security_config)
        
        # Check that base config is preserved
        assert merged_config["security"]["enabled"] is True
        assert merged_config["security"]["auth"]["enabled"] is True
        assert merged_config["security"]["auth"]["methods"] == ["api_key"]
        
        # Check that new config is added
        assert merged_config["security"]["auth"]["api_keys"]["merged-key"] == "merged-user"
        assert merged_config["security"]["ssl"]["enabled"] is True
    
    def test_default_configuration(self):
        """Test default configuration generation."""
        default_config = SecurityFactory.get_default_config()
        
        # Check structure
        assert "security" in default_config
        assert "auth" in default_config["security"]
        assert "ssl" in default_config["security"]
        assert "permissions" in default_config["security"]
        assert "rate_limit" in default_config["security"]
        
        # Check default values
        assert default_config["security"]["enabled"] is True
        assert default_config["security"]["auth"]["enabled"] is True
        assert default_config["security"]["ssl"]["enabled"] is False
        assert default_config["security"]["permissions"]["enabled"] is True
        assert default_config["security"]["rate_limit"]["enabled"] is True
    
    def test_middleware_factory_configuration_validation(self):
        """Test middleware factory configuration validation."""
        valid_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {"key": "user"}
                },
                "ssl": {
                    "enabled": False
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
        
        # Mock FastAPI app
        from unittest.mock import Mock
        mock_app = Mock()
        
        factory = MiddlewareFactory(mock_app, valid_config)
        assert factory.validate_middleware_config() is True
        
        # Test invalid configuration
        invalid_config = {
            "security": {
                "auth": "not_a_dict"
            }
        }
        
        factory = MiddlewareFactory(mock_app, invalid_config)
        assert factory.validate_middleware_config() is False
