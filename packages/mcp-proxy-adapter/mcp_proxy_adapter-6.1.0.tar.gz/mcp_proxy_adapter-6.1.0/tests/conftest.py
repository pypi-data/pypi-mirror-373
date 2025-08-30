"""
Test configuration and fixtures for mcp_proxy_adapter.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import Body
from fastapi.responses import JSONResponse
from mcp_proxy_adapter.core.errors import MicroserviceError, NotFoundError

# Import after patching config
from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import MicroserviceError

# Test configuration with security disabled
TEST_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": True,
        "log_level": "DEBUG"
    },
    "logging": {
        "level": "DEBUG",
        "file": None,
        "log_dir": "./logs",
        "log_file": "test.log",
        "error_log_file": "test_error.log",
        "access_log_file": "test_access.log",
        "max_file_size": "10MB",
        "backup_count": 5,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "console_output": True,
        "file_output": False
    },
    "commands": {
        "auto_discovery": True,
        "commands_directory": "./commands",
        "catalog_directory": "./catalog",
        "plugin_servers": [],
        "auto_install_dependencies": True
    },
    "ssl": {
        "enabled": False,
        "mode": "http_only",
        "cert_file": None,
        "key_file": None,
        "ca_cert": None,
        "verify_client": False,
        "client_cert_required": False,
        "cipher_suites": ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"],
        "min_tls_version": "TLSv1.2",
        "max_tls_version": "1.3",
        "token_auth": {
            "enabled": False,
            "header_name": "Authorization",
            "token_prefix": "Bearer",
            "tokens_file": "tokens.json",
            "token_expiry": 3600,
            "jwt_secret": "",
            "jwt_algorithm": "HS256"
        }
    },
    "roles": {
        "enabled": False,
        "config_file": "schemas/roles_schema.json",
        "default_policy": {
            "deny_by_default": False,
            "require_role_match": False,
            "case_sensitive": False,
            "allow_wildcard": True
        },
        "auto_load": False,
        "validation_enabled": False
    },
    "transport": {
        "type": "http",
        "port": None,
        "ssl": {
            "enabled": False,
            "cert_file": None,
            "key_file": None,
            "ca_cert": None,
            "verify_client": False,
            "client_cert_required": False
        }
    },
    "proxy": {
        "enabled": False,
        "url": None,
        "timeout": 30,
        "retry_attempts": 3,
        "retry_delay": 1
    },
    "debug": {
        "enabled": True,
        "level": "DEBUG"
    },
    "security": {
        "framework": "mcp_security_framework",
        "enabled": False,  # Disable security for tests
        "debug": True,
        "environment": "test",
        "version": "1.0.0",
        "auth": {
            "enabled": False,  # Disable auth for tests
            "methods": [],
            "api_keys": {},
            "user_roles": {},
            "jwt_secret": "",
            "jwt_algorithm": "HS256",
            "jwt_expiry_hours": 24,
            "certificate_auth": False,
            "certificate_roles_oid": "1.3.6.1.4.1.99999.1.1",
            "certificate_permissions_oid": "1.3.6.1.4.1.99999.1.2",
            "basic_auth": False,
            "oauth2_config": None,
            "public_paths": ["/health", "/docs", "/openapi.json", "/cmd", "/api/jsonrpc"],
            "security_headers": None
        },
        "ssl": {
            "enabled": False,
            "cert_file": None,
            "key_file": None,
            "ca_cert_file": None,
            "client_cert_file": None,
            "client_key_file": None,
            "verify_mode": "CERT_NONE",
            "min_tls_version": "TLSv1.2",
            "max_tls_version": None,
            "cipher_suite": None,
            "check_hostname": False,
            "check_expiry": False,
            "expiry_warning_days": 30
        },
        "certificates": {
            "enabled": False,
            "ca_cert_path": None,
            "ca_key_path": None,
            "cert_storage_path": "./certs",
            "key_storage_path": "./keys",
            "default_validity_days": 365,
            "key_size": 2048,
            "hash_algorithm": "sha256",
            "crl_enabled": False,
            "crl_path": None,
            "crl_validity_days": 30,
            "auto_renewal": False,
            "renewal_threshold_days": 30
        },
        "permissions": {
            "enabled": False,  # Disable permissions for tests
            "roles_file": "schemas/roles_schema.json",
            "default_role": "guest",
            "admin_role": "admin",
            "role_hierarchy": {},
            "permission_cache_enabled": False,
            "permission_cache_ttl": 300,
            "wildcard_permissions": True,
            "strict_mode": False,
            "roles": None
        },
        "rate_limit": {
            "enabled": False,  # Disable rate limiting for tests
            "default_requests_per_minute": 60,
            "default_requests_per_hour": 1000,
            "burst_limit": 2,
            "window_size_seconds": 60,
            "storage_backend": "memory",
            "redis_config": None,
            "cleanup_interval": 300,
            "exempt_paths": ["/health", "/docs", "/openapi.json", "/cmd", "/api/jsonrpc"],
            "exempt_roles": ["admin"]
        },
        "logging": {
            "enabled": True,
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "file_path": None,
            "max_file_size": 10,
            "backup_count": 5,
            "console_output": True,
            "json_format": False,
            "include_timestamp": True,
            "include_level": True,
            "include_module": True
        }
    }
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return TEST_CONFIG.copy()

@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    with patch("mcp_proxy_adapter.config.config") as mock_config:
        mock_config.get.return_value = TEST_CONFIG
        mock_config.config_data = TEST_CONFIG
        yield mock_config

@pytest.fixture
def app():
    """Create test application with security disabled."""
    # Create a simple FastAPI app without security middleware for testing
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="MCP Proxy Adapter - Test",
        description="Test application without security",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.post("/cmd")
    async def cmd_endpoint_wrapper(command_data: Dict[str, Any] = Body(...)):
        """CMD endpoint without security."""
        try:
            # Determine request format (CommandRequest or JSON-RPC)
            if "jsonrpc" in command_data and "method" in command_data:
                # JSON-RPC format - not supported in this test version
                return JSONResponse(
                    status_code=400,
                    content={"error": "JSON-RPC format not supported in test"}
                )
            
            # CommandRequest format
            if "command" not in command_data:
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": -32600,
                            "message": "Отсутствует обязательное поле 'command'"
                        }
                    }
                )
            
            command_name = command_data["command"]
            params = command_data.get("params", {})
            
            # Check if command exists - use imported registry
            from mcp_proxy_adapter.api.handlers import registry as handlers_registry
            if not handlers_registry.command_exists(command_name):
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": -32601,
                            "message": f"Команда '{command_name}' не найдена"
                        }
                    }
                )
            
            # Execute command - use imported execute_command
            from mcp_proxy_adapter.api.handlers import execute_command as handlers_execute_command
            try:
                result = await handlers_execute_command(command_name, params, None)
                return {"result": result}
            except MicroserviceError as e:
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": e.to_dict()
                    }
                )
            except NotFoundError as e:
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": -32601,
                            "message": str(e)
                        }
                    }
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
            )
    
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def mock_registry():
    """Mock for command registry."""
    with patch("mcp_proxy_adapter.api.app.registry") as mock_reg:
        yield mock_reg

@pytest.fixture
def mock_execute_command():
    """Mock for execute_command function."""
    with patch("mcp_proxy_adapter.api.app.execute_command") as mock_exec:
        yield mock_exec

@pytest.fixture
async def clean_registry():
    """Clean registry before and after tests."""
    # Clear registry before test
    registry.clear()
    yield registry
    # Clear registry after test
    registry.clear()
