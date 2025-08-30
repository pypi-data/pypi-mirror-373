"""
Unit tests for UnifiedConfigAdapter.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

This module contains unit tests for the UnifiedConfigAdapter class.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from mcp_proxy_adapter.core.unified_config_adapter import (
    UnifiedConfigAdapter,
    ValidationResult
)


class TestUnifiedConfigAdapter:
    """Test cases for UnifiedConfigAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create UnifiedConfigAdapter instance."""
        return UnifiedConfigAdapter()
    
    @pytest.fixture
    def valid_config(self) -> Dict[str, Any]:
        """Valid configuration for testing."""
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
                    "roles_file": "roles.json"
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            }
        }
    
    def test_initialization(self, adapter):
        """Test adapter initialization."""
        assert adapter is not None
        assert hasattr(adapter, 'validation_errors')
        assert hasattr(adapter, 'validation_warnings')
    
    def test_validate_configuration_valid(self, adapter, valid_config):
        """Test validation of valid configuration."""
        result = adapter.validate_configuration(valid_config)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.details["has_security_section"] is True
        assert result.details["has_legacy_sections"] is False
    
    def test_validate_configuration_invalid_type(self, adapter):
        """Test validation of invalid configuration type."""
        result = adapter.validate_configuration("not a dict")
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "must be a dictionary" in result.errors[0]
    
    def test_validate_configuration_invalid_security_section(self, adapter):
        """Test validation of invalid security section."""
        config = {"security": "not a dict"}
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert len(result.errors) >= 1
        # Check for either security section error or auth section error
        error_messages = " ".join(result.errors)
        assert ("Security section must be a dictionary" in error_messages or 
                "Security section must be a dictionary" in error_messages)
    
    def test_validate_configuration_legacy_sections(self, adapter):
        """Test validation with legacy sections."""
        config = {
            "security": {"enabled": True},
            "ssl": {"enabled": False},
            "roles": {"enabled": True},
            "auth_enabled": True
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is True
        assert len(result.warnings) >= 3  # At least 3 legacy section warnings
        assert result.details["has_legacy_sections"] is True
    
    def test_validate_configuration_conflicts(self, adapter):
        """Test validation with configuration conflicts."""
        config = {
            "security": {
                "ssl": {"enabled": False},
                "auth": {"enabled": True}
            },
            "ssl": {"enabled": True},
            "auth_enabled": False
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is True
        assert len(result.warnings) >= 2  # At least 2 conflict warnings
    
    def test_validate_auth_section_invalid_methods(self, adapter):
        """Test validation of invalid auth methods."""
        config = {
            "security": {
                "auth": {
                    "methods": "not a list"
                }
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert any("Auth methods must be a list" in error for error in result.errors)
    
    def test_validate_auth_section_invalid_method(self, adapter):
        """Test validation of invalid auth method."""
        config = {
            "security": {
                "auth": {
                    "methods": ["invalid_method"]
                }
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert any("Invalid auth methods" in error for error in result.errors)
    
    def test_validate_auth_section_invalid_api_keys(self, adapter):
        """Test validation of invalid API keys."""
        config = {
            "security": {
                "auth": {
                    "api_keys": "not a dict"
                }
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert any("API keys must be a dictionary" in error for error in result.errors)
    
    def test_validate_auth_section_empty_jwt_secret(self, adapter):
        """Test validation of empty JWT secret."""
        config = {
            "security": {
                "auth": {
                    "methods": ["jwt"],
                    "jwt_secret": ""
                }
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is True
        assert any("JWT secret is empty" in warning for warning in result.warnings)
    
    def test_validate_ssl_section_invalid_type(self, adapter):
        """Test validation of invalid SSL section type."""
        config = {
            "security": {
                "ssl": "not a dict"
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert any("SSL configuration must be a dictionary" in error for error in result.errors)
    
    @patch('pathlib.Path.exists')
    def test_validate_ssl_section_missing_files(self, mock_exists, adapter):
        """Test validation of missing SSL files."""
        mock_exists.return_value = False
        
        config = {
            "security": {
                "ssl": {
                    "enabled": True,
                    "cert_file": "/path/to/cert.crt",
                    "key_file": "/path/to/key.key"
                }
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is True
        assert len(result.warnings) >= 2  # At least 2 file not found warnings
    
    def test_validate_permissions_section_invalid_type(self, adapter):
        """Test validation of invalid permissions section type."""
        config = {
            "security": {
                "permissions": "not a dict"
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert any("Permissions configuration must be a dictionary" in error for error in result.errors)
    
    @patch('pathlib.Path.exists')
    def test_validate_permissions_section_missing_roles_file(self, mock_exists, adapter):
        """Test validation of missing roles file."""
        mock_exists.return_value = False
        
        config = {
            "security": {
                "permissions": {
                    "enabled": True,
                    "roles_file": "missing_roles.json"
                }
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is True
        assert any("Roles file not found" in warning for warning in result.warnings)
    
    def test_validate_rate_limit_section_invalid_type(self, adapter):
        """Test validation of invalid rate limit section type."""
        config = {
            "security": {
                "rate_limit": "not a dict"
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert any("Rate limit configuration must be a dictionary" in error for error in result.errors)
    
    def test_validate_rate_limit_section_invalid_value(self, adapter):
        """Test validation of invalid rate limit value."""
        config = {
            "security": {
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 0
                }
            }
        }
        result = adapter.validate_configuration(config)
        
        assert result.is_valid is False
        assert any("must be greater than 0" in error for error in result.errors)
    
    def test_get_auth_config(self, adapter, valid_config):
        """Test getting auth configuration."""
        auth_config = adapter._get_auth_config(valid_config)
        
        assert isinstance(auth_config, dict)
        assert auth_config["enabled"] is True
        assert auth_config["methods"] == ["api_key"]
        assert "test-key" in auth_config["api_keys"]
    
    def test_get_auth_config_legacy(self, adapter):
        """Test getting auth configuration with legacy flag."""
        config = {
            "auth_enabled": False,
            "security": {
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"]
                }
            }
        }
        auth_config = adapter._get_auth_config(config)
        
        assert auth_config["enabled"] is False  # Legacy flag should override
    
    def test_get_ssl_config(self, adapter, valid_config):
        """Test getting SSL configuration."""
        ssl_config = adapter._get_ssl_config(valid_config)
        
        assert isinstance(ssl_config, dict)
        assert ssl_config["enabled"] is False
    
    def test_get_ssl_config_legacy(self, adapter):
        """Test getting SSL configuration with legacy section."""
        config = {
            "ssl": {
                "enabled": True,
                "cert_file": "/legacy/cert.crt"
            },
            "security": {
                "ssl": {
                    "enabled": False
                }
            }
        }
        ssl_config = adapter._get_ssl_config(config)
        
        # Legacy SSL should be merged with security SSL
        assert ssl_config["enabled"] is True
        assert ssl_config["cert_file"] == "/legacy/cert.crt"
    
    def test_get_permissions_config(self, adapter, valid_config):
        """Test getting permissions configuration."""
        permissions_config = adapter._get_permissions_config(valid_config)
        
        assert isinstance(permissions_config, dict)
        assert permissions_config["enabled"] is True
        assert permissions_config["roles_file"] == "roles.json"
    
    def test_get_permissions_config_legacy(self, adapter):
        """Test getting permissions configuration with legacy section."""
        config = {
            "roles": {
                "enabled": True,
                "config_file": "legacy_roles.json"
            },
            "security": {
                "permissions": {
                    "enabled": False,
                    "roles_file": "new_roles.json"
                }
            }
        }
        permissions_config = adapter._get_permissions_config(config)
        
        # Legacy roles should be merged with security permissions
        assert permissions_config["enabled"] is True
        assert permissions_config["config_file"] == "legacy_roles.json"
        assert permissions_config["roles_file"] == "new_roles.json"
    
    def test_get_rate_limit_config(self, adapter, valid_config):
        """Test getting rate limit configuration."""
        rate_limit_config = adapter._get_rate_limit_config(valid_config)
        
        assert isinstance(rate_limit_config, dict)
        assert rate_limit_config["enabled"] is True
        assert rate_limit_config["requests_per_minute"] == 60
    
    def test_get_rate_limit_config_legacy(self, adapter):
        """Test getting rate limit configuration with legacy flag."""
        config = {
            "rate_limit_enabled": False,
            "security": {
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            }
        }
        rate_limit_config = adapter._get_rate_limit_config(config)
        
        assert rate_limit_config["enabled"] is False  # Legacy flag should override
    
    def test_get_public_paths_default(self, adapter):
        """Test getting default public paths."""
        config = {}
        public_paths = adapter.get_public_paths(config)
        
        expected_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        assert public_paths == expected_paths
    
    def test_get_public_paths_custom(self, adapter):
        """Test getting custom public paths."""
        config = {
            "security": {
                "public_paths": ["/custom", "/api/v1/public"]
            }
        }
        public_paths = adapter.get_public_paths(config)
        
        assert public_paths == ["/custom", "/api/v1/public"]
    
    def test_get_security_enabled(self, adapter, valid_config):
        """Test checking if security is enabled."""
        assert adapter.get_security_enabled(valid_config) is True
    
    def test_get_security_enabled_disabled(self, adapter):
        """Test checking if security is disabled."""
        config = {
            "security": {
                "enabled": False
            }
        }
        assert adapter.get_security_enabled(config) is False
    
    def test_get_security_enabled_default(self, adapter):
        """Test checking security enabled with default value."""
        config = {}
        assert adapter.get_security_enabled(config) is True
    
    def test_migrate_legacy_config(self, adapter):
        """Test migrating legacy configuration."""
        legacy_config = {
            "ssl": {
                "enabled": True,
                "cert_file": "/legacy/cert.crt"
            },
            "roles": {
                "enabled": True,
                "config_file": "legacy_roles.json"
            },
            "auth_enabled": True,
            "rate_limit_enabled": False
        }
        
        migrated_config = adapter.migrate_legacy_config(legacy_config)
        
        assert "security" in migrated_config
        assert migrated_config["security"]["ssl"]["enabled"] is True
        assert migrated_config["security"]["permissions"]["enabled"] is True
        assert migrated_config["security"]["auth"]["enabled"] is True
        assert migrated_config["security"]["rate_limit"]["enabled"] is False
        
        # Legacy sections should still exist for backward compatibility
        assert "ssl" in migrated_config
        assert "roles" in migrated_config
        assert "auth_enabled" in migrated_config
        assert "rate_limit_enabled" in migrated_config
    
    def test_get_default_config(self, adapter):
        """Test getting default configuration."""
        default_config = adapter.get_default_config()
        
        assert "security" in default_config
        assert default_config["security"]["enabled"] is True
        assert "auth" in default_config["security"]
        assert "ssl" in default_config["security"]
        assert "permissions" in default_config["security"]
        assert "rate_limit" in default_config["security"]
        assert "public_paths" in default_config["security"]
    
    @patch('mcp_proxy_adapter.core.unified_config_adapter.SECURITY_FRAMEWORK_AVAILABLE', False)
    def test_convert_to_security_config_framework_unavailable(self, adapter, valid_config):
        """Test conversion when security framework is unavailable."""
        result = adapter.convert_to_security_config(valid_config)
        
        assert result is None
    
    @patch('mcp_proxy_adapter.core.unified_config_adapter.SECURITY_FRAMEWORK_AVAILABLE', True)
    @patch('mcp_proxy_adapter.core.unified_config_adapter.SecurityConfig')
    @patch('mcp_proxy_adapter.core.unified_config_adapter.AuthConfig')
    @patch('mcp_proxy_adapter.core.unified_config_adapter.SSLConfig')
    @patch('mcp_proxy_adapter.core.unified_config_adapter.PermissionConfig')
    @patch('mcp_proxy_adapter.core.unified_config_adapter.RateLimitConfig')
    def test_convert_to_security_config_success(
        self, mock_rate_limit, mock_permission, mock_ssl, 
        mock_auth, mock_security, adapter, valid_config
    ):
        """Test successful conversion to SecurityConfig."""
        # Mock the config objects
        mock_auth.return_value = Mock()
        mock_ssl.return_value = Mock()
        mock_permission.return_value = Mock()
        mock_rate_limit.return_value = Mock()
        mock_security.return_value = Mock()
        
        result = adapter.convert_to_security_config(valid_config)
        
        assert result is not None
        mock_security.assert_called_once()
    
    @patch('mcp_proxy_adapter.core.unified_config_adapter.SECURITY_FRAMEWORK_AVAILABLE', True)
    def test_convert_to_security_config_validation_failed(self, adapter):
        """Test conversion with validation failure."""
        invalid_config = {"security": "not a dict"}
        
        result = adapter.convert_to_security_config(invalid_config)
        
        assert result is None


class TestValidationResult:
    """Test cases for ValidationResult."""
    
    def test_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(
            is_valid=True,
            errors=["error1"],
            warnings=["warning1"],
            details={"key": "value"}
        )
        
        assert result.is_valid is True
        assert result.errors == ["error1"]
        assert result.warnings == ["warning1"]
        assert result.details == {"key": "value"}
    
    def test_initialization_with_none(self):
        """Test ValidationResult initialization with None values."""
        result = ValidationResult(
            is_valid=False,
            errors=None,
            warnings=None,
            details=None
        )
        
        assert result.is_valid is False
        assert result.errors == []
        assert result.warnings == []
        assert result.details == {}
    
    def test_initialization_defaults(self):
        """Test ValidationResult initialization with defaults."""
        result = ValidationResult(
            is_valid=True,
            errors=None,
            warnings=None,
            details=None
        )
        
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.details == {}
