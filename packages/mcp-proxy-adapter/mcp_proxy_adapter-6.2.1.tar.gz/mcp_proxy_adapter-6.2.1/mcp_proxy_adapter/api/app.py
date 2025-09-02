"""
Module for FastAPI application setup.
"""

import json
import ssl
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from mcp_proxy_adapter.api.handlers import execute_command, handle_json_rpc, handle_batch_json_rpc, get_server_health, get_commands_list
from mcp_proxy_adapter.api.middleware import setup_middleware
from mcp_proxy_adapter.api.schemas import JsonRpcRequest, JsonRpcSuccessResponse, JsonRpcErrorResponse, HealthResponse, CommandListResponse, APIToolDescription
from mcp_proxy_adapter.api.tools import get_tool_description, execute_tool
from mcp_proxy_adapter.config import config
from mcp_proxy_adapter.core.errors import MicroserviceError, NotFoundError
from mcp_proxy_adapter.core.logging import logger, RequestLogger
from mcp_proxy_adapter.core.ssl_utils import SSLUtils
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.custom_openapi import custom_openapi_with_fallback


def create_lifespan(config_path: Optional[str] = None):
    """
    Create lifespan manager for the FastAPI application.
    
    Args:
        config_path: Path to configuration file (optional)
    
    Returns:
        Lifespan context manager
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Lifespan manager for the FastAPI application. Handles startup and shutdown events.
        """
        # Startup events
        from mcp_proxy_adapter.commands.command_registry import registry
        from mcp_proxy_adapter.core.proxy_registration import register_with_proxy, unregister_from_proxy
        
        # Initialize system using unified logic
        # This will load config, register custom commands, and discover auto-commands
        # Only reload config if not already loaded from the same path
        if config_path:
            init_result = await registry.reload_system(config_path=config_path)
        else:
            init_result = await registry.reload_system()
        
        logger.info(f"Application started with {init_result['total_commands']} commands registered")
        logger.info(f"System initialization result: {init_result}")
        
        # Register with proxy if enabled
        server_config = config.get("server", {})
        server_host = server_config.get("host", "0.0.0.0")
        server_port = server_config.get("port", 8000)
        
        # Determine server URL based on SSL configuration
        # Try security framework SSL config first
        security_config = config.get("security", {})
        ssl_config = security_config.get("ssl", {})
        
        # Fallback to legacy SSL config
        if not ssl_config.get("enabled", False):
            ssl_config = config.get("ssl", {})
        
        if ssl_config.get("enabled", False):
            protocol = "https"
        else:
            protocol = "http"
        
        # Use localhost for external access if host is 0.0.0.0
        if server_host == "0.0.0.0":
            server_host = "localhost"
        
        server_url = f"{protocol}://{server_host}:{server_port}"
        
        # Attempt proxy registration
        registration_success = await register_with_proxy(server_url)
        if registration_success:
            logger.info("✅ Proxy registration completed successfully")
        else:
            logger.info("ℹ️ Proxy registration is disabled or failed")
        
        yield  # Application is running
        
        # Shutdown events
        logger.info("Application shutting down")
        
        # Unregister from proxy if enabled
        unregistration_success = await unregister_from_proxy()
        if unregistration_success:
            logger.info("✅ Proxy unregistration completed successfully")
        else:
            logger.warning("⚠️ Proxy unregistration failed or was disabled")
    
    return lifespan


def create_ssl_context(app_config: Optional[Dict[str, Any]] = None) -> Optional[ssl.SSLContext]:
    """
    Create SSL context based on configuration.
    
    Args:
        app_config: Application configuration dictionary (optional)
    
    Returns:
        SSL context if SSL is enabled and properly configured, None otherwise
    """
    current_config = app_config if app_config is not None else config.get_all()
    
    # Try security framework SSL config first
    security_config = current_config.get("security", {})
    ssl_config = security_config.get("ssl", {})
    
    # Fallback to legacy SSL config
    if not ssl_config.get("enabled", False):
        ssl_config = current_config.get("ssl", {})
    
    if not ssl_config.get("enabled", False):
        logger.info("SSL is disabled in configuration")
        return None
    
    cert_file = ssl_config.get("cert_file")
    key_file = ssl_config.get("key_file")
    
    if not cert_file or not key_file:
        logger.warning("SSL enabled but certificate or key file not specified")
        return None
    
    try:
        # Create SSL context using SSLUtils
        ssl_context = SSLUtils.create_ssl_context(
            cert_file=cert_file,
            key_file=key_file,
            ca_cert=ssl_config.get("ca_cert"),
            verify_client=ssl_config.get("verify_client", False),
            cipher_suites=ssl_config.get("cipher_suites", []),
            min_tls_version=ssl_config.get("min_tls_version", "1.2"),
            max_tls_version=ssl_config.get("max_tls_version", "1.3")
        )
        
        logger.info(f"SSL context created successfully for mode: {ssl_config.get('mode', 'https_only')}")
        return ssl_context
        
    except Exception as e:
        logger.error(f"Failed to create SSL context: {e}")
        return None


def create_app(title: Optional[str] = None, description: Optional[str] = None, version: Optional[str] = None, app_config: Optional[Dict[str, Any]] = None, config_path: Optional[str] = None) -> FastAPI:
    """
    Creates and configures FastAPI application.

    Args:
        title: Application title (default: "MCP Proxy Adapter")
        description: Application description (default: "JSON-RPC API for interacting with MCP Proxy")
        version: Application version (default: "1.0.0")
        app_config: Application configuration dictionary (optional)
        config_path: Path to configuration file (optional)

    Returns:
        Configured FastAPI application.
        
    Raises:
        SystemExit: If authentication is enabled but required files are missing (security issue)
    """
    # Use provided configuration or fallback to global config
    if app_config is not None:
        if hasattr(app_config, 'get_all'):
            current_config = app_config.get_all()
        elif hasattr(app_config, 'keys'):
            current_config = app_config
        else:
            current_config = config.get_all()
    else:
        current_config = config.get_all()
    
    # Debug: Check what config is passed to create_app
    if app_config:
        if hasattr(app_config, 'keys'):
            print(f"🔍 Debug: create_app received app_config keys: {list(app_config.keys())}")
            if "security" in app_config:
                ssl_config = app_config["security"].get("ssl", {})
                print(f"🔍 Debug: create_app SSL config: enabled={ssl_config.get('enabled', False)}")
                print(f"🔍 Debug: create_app SSL config: cert_file={ssl_config.get('cert_file')}")
                print(f"🔍 Debug: create_app SSL config: key_file={ssl_config.get('key_file')}")
        else:
            print(f"🔍 Debug: create_app received app_config type: {type(app_config)}")
    else:
        print("🔍 Debug: create_app received no app_config, using global config")
    
    # Security check: Validate all authentication configurations before startup
    security_errors = []
    
    print(f"🔍 Debug: current_config keys: {list(current_config.keys())}")
    if "security" in current_config:
        print(f"🔍 Debug: security config: {current_config['security']}")
    if "roles" in current_config:
        print(f"🔍 Debug: roles config: {current_config['roles']}")
    
    # Check security framework configuration only if enabled
    security_config = current_config.get("security", {})
    if security_config.get("enabled", False):
        # Validate security framework configuration
        from mcp_proxy_adapter.core.unified_config_adapter import UnifiedConfigAdapter
        adapter = UnifiedConfigAdapter()
        validation_result = adapter.validate_configuration(current_config)
        
        if not validation_result.is_valid:
            security_errors.extend(validation_result.errors)
        
        # Check SSL configuration within security framework
        ssl_config = security_config.get("ssl", {})
        if ssl_config.get("enabled", False):
            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            
            print(f"🔍 Debug: api/app.py security.ssl: cert_file={cert_file}, key_file={key_file}")
            print(f"🔍 Debug: api/app.py security.ssl: cert_file exists={Path(cert_file).exists() if cert_file else 'None'}")
            print(f"🔍 Debug: api/app.py security.ssl: key_file exists={Path(key_file).exists() if key_file else 'None'}")
            
            if cert_file and not Path(cert_file).exists():
                security_errors.append(f"SSL is enabled but certificate file not found: {cert_file}")
            
            if key_file and not Path(key_file).exists():
                security_errors.append(f"SSL is enabled but private key file not found: {key_file}")
            
            # Check mTLS configuration
            ca_cert_file = ssl_config.get("ca_cert_file")
            if ca_cert_file and not Path(ca_cert_file).exists():
                security_errors.append(f"mTLS is enabled but CA certificate file not found: {ca_cert_file}")
    
    # Legacy configuration checks for backward compatibility
    roles_config = current_config.get("roles", {})
    print(f"🔍 Debug: roles_config = {roles_config}")
    if roles_config.get("enabled", False):
        roles_config_path = roles_config.get("config_file", "schemas/roles_schema.json")
        print(f"🔍 Debug: Checking roles file: {roles_config_path}")
        if not Path(roles_config_path).exists():
            security_errors.append(f"Roles are enabled but schema file not found: {roles_config_path}")
    
    # Check new security framework permissions configuration
    security_config = current_config.get("security", {})
    permissions_config = security_config.get("permissions", {})
    if permissions_config.get("enabled", False):
        roles_file = permissions_config.get("roles_file")
        if roles_file and not Path(roles_file).exists():
            security_errors.append(f"Permissions are enabled but roles file not found: {roles_file}")
    
    legacy_ssl_config = current_config.get("ssl", {})
    if legacy_ssl_config.get("enabled", False):
        # Check SSL certificate files
        cert_file = legacy_ssl_config.get("cert_file")
        key_file = legacy_ssl_config.get("key_file")
        
        print(f"🔍 Debug: api/app.py legacy.ssl: cert_file={cert_file}, key_file={key_file}")
        print(f"🔍 Debug: api/app.py legacy.ssl: cert_file exists={Path(cert_file).exists() if cert_file else 'None'}")
        print(f"🔍 Debug: api/app.py legacy.ssl: key_file exists={Path(key_file).exists() if key_file else 'None'}")
        
        if cert_file and not Path(cert_file).exists():
            security_errors.append(f"Legacy SSL is enabled but certificate file not found: {cert_file}")
        
        if key_file and not Path(key_file).exists():
            security_errors.append(f"Legacy SSL is enabled but private key file not found: {key_file}")
        
        # Check mTLS configuration
        if legacy_ssl_config.get("mode") == "mtls":
            ca_cert = legacy_ssl_config.get("ca_cert")
            if ca_cert and not Path(ca_cert).exists():
                security_errors.append(f"Legacy mTLS is enabled but CA certificate file not found: {ca_cert}")
    
    # Check token authentication configuration
    token_auth_config = legacy_ssl_config.get("token_auth", {})
    if token_auth_config.get("enabled", False):
        tokens_file = token_auth_config.get("tokens_file", "tokens.json")
        if not Path(tokens_file).exists():
            security_errors.append(f"Token authentication is enabled but tokens file not found: {tokens_file}")
    
    # Check general authentication
    if current_config.get("auth_enabled", False):
        # If auth is enabled, check if any authentication method is properly configured
        ssl_enabled = legacy_ssl_config.get("enabled", False)
        roles_enabled = roles_config.get("enabled", False)
        token_auth_enabled = token_auth_config.get("enabled", False)
        
        if not (ssl_enabled or roles_enabled or token_auth_enabled):
            security_errors.append("Authentication is enabled but no authentication method is properly configured")
    
    # If there are security errors, block startup
    if security_errors:
        logger.critical("CRITICAL SECURITY ERROR: Authentication configuration issues detected:")
        for error in security_errors:
            logger.critical(f"  - {error}")
        logger.critical("Server startup blocked for security reasons.")
        logger.critical("Please fix authentication configuration or disable authentication features.")
        raise SystemExit(1)
    
    # Use provided parameters or defaults
    app_title = title or "MCP Proxy Adapter"
    app_description = description or "JSON-RPC API for interacting with MCP Proxy"
    app_version = version or "1.0.0"
    
    # Create application
    app = FastAPI(
        title=app_title,
        description=app_description,
        version=app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=create_lifespan(config_path),
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify concrete domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup middleware using the new middleware package
    setup_middleware(app, current_config)
    
    # Use custom OpenAPI schema
    app.openapi = lambda: custom_openapi_with_fallback(app)
    
    # Explicit endpoint for OpenAPI schema
    @app.get("/openapi.json")
    async def get_openapi_schema():
        """
        Returns optimized OpenAPI schema compatible with MCP-Proxy.
        """
        return custom_openapi_with_fallback(app)

    # JSON-RPC handler
    @app.post("/api/jsonrpc", response_model=Union[JsonRpcSuccessResponse, JsonRpcErrorResponse, List[Union[JsonRpcSuccessResponse, JsonRpcErrorResponse]]])
    async def jsonrpc_endpoint(request: Request, request_data: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(...)):
        """
        Endpoint for handling JSON-RPC requests.
        Supports both single and batch requests.
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        # Create request logger for this endpoint
        req_logger = RequestLogger(__name__, request_id) if request_id else logger
        
        # Check if it's a batch request
        if isinstance(request_data, list):
            # Process batch request
            if len(request_data) == 0:
                # Empty batch request is invalid
                req_logger.warning("Invalid Request: Empty batch request")
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32600,
                            "message": "Invalid Request. Empty batch request"
                        },
                        "id": None
                    }
                )
            return await handle_batch_json_rpc(request_data, request)
        else:
            # Process single request
            return await handle_json_rpc(request_data, request_id, request)

    # Command execution endpoint (/cmd)
    @app.post("/cmd")
    async def cmd_endpoint(request: Request, command_data: Dict[str, Any] = Body(...)):
        """
        Universal endpoint for executing commands.
        Supports two formats:
        1. CommandRequest:
        {
            "command": "command_name",
            "params": {
                // Command parameters
            }
        }
        
        2. JSON-RPC:
        {
            "jsonrpc": "2.0",
            "method": "command_name",
            "params": {
                // Command parameters
            },
            "id": 123
        }
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        # Create request logger for this endpoint
        req_logger = RequestLogger(__name__, request_id) if request_id else logger
        
        try:
            # Determine request format (CommandRequest or JSON-RPC)
            if "jsonrpc" in command_data and "method" in command_data:
                # JSON-RPC format
                return await handle_json_rpc(command_data, request_id, request)
            
            # CommandRequest format
            if "command" not in command_data:
                req_logger.warning("Missing required field 'command'")
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
            
            req_logger.debug(f"Executing command via /cmd: {command_name}, params: {params}")
            
            # Check if command exists
            if not registry.command_exists(command_name):
                req_logger.warning(f"Command '{command_name}' not found")
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": -32601,
                            "message": f"Команда '{command_name}' не найдена"
                        }
                    }
                )
            
            # Execute command
            try:
                result = await execute_command(command_name, params, request_id, request)
                return {"result": result}
            except MicroserviceError as e:
                # Handle command execution errors
                req_logger.error(f"Error executing command '{command_name}': {str(e)}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": e.to_dict()
                    }
                )
            except NotFoundError as e:
                # Специальная обработка для help-команды: возвращаем result с пустым commands и error
                if command_name == "help":
                    return {
                        "result": {
                            "success": False,
                            "commands": {},
                            "error": str(e),
                            "note": "To get detailed information about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}"
                        }
                    }
                # Для остальных команд — стандартная ошибка
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": e.code,
                            "message": str(e)
                        }
                    }
                )
            
        except json.JSONDecodeError:
            req_logger.error("JSON decode error")
            return JSONResponse(
                status_code=200,
                content={
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
            )
        except Exception as e:
            req_logger.exception(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=200,
                content={
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": {"details": str(e)}
                    }
                }
            )

    # Direct command call
    @app.post("/api/command/{command_name}")
    async def command_endpoint(request: Request, command_name: str, params: Dict[str, Any] = Body(default={})):
        """
        Endpoint for direct command call.
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        try:
            result = await execute_command(command_name, params, request_id, request)
            return result
        except MicroserviceError as e:
            # Convert to proper HTTP status code
            status_code = 400 if e.code < 0 else e.code
            return JSONResponse(
                status_code=status_code,
                content=e.to_dict()
            )

    # Server health check
    @app.get("/health", operation_id="health_check")
    async def health_endpoint():
        """
        Health check endpoint.
        Returns server status and basic information.
        """
        return {
            "status": "ok",
            "model": "mcp-proxy-adapter",
            "version": "1.0.0"
        }
    
    # Graceful shutdown endpoint
    @app.post("/shutdown")
    async def shutdown_endpoint():
        """
        Graceful shutdown endpoint.
        Triggers server shutdown after completing current requests.
        """
        import asyncio
        
        # Schedule shutdown after a short delay to allow response
        async def delayed_shutdown():
            await asyncio.sleep(1)
            # This will trigger the lifespan shutdown event
            import os
            os._exit(0)
        
        # Start shutdown task
        asyncio.create_task(delayed_shutdown())
        
        return {
            "status": "shutting_down",
            "message": "Server shutdown initiated. New requests will be rejected."
        }

    # List of available commands
    @app.get("/api/commands", response_model=CommandListResponse)
    async def commands_list_endpoint():
        """
        Endpoint for getting list of available commands.
        """
        commands = await get_commands_list()
        return {"commands": commands}

    # Get command information by name
    @app.get("/api/commands/{command_name}")
    async def command_info_endpoint(request: Request, command_name: str):
        """
        Endpoint for getting information about a specific command.
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        # Create request logger for this endpoint
        req_logger = RequestLogger(__name__, request_id) if request_id else logger
        
        try:
            command_info = registry.get_command_info(command_name)
            return command_info
        except NotFoundError as e:
            req_logger.warning(f"Command '{command_name}' not found")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": 404,
                        "message": f"Command '{command_name}' not found"
                    }
                }
            )

    # Get API tool description
    @app.get("/api/tools/{tool_name}")
    async def tool_description_endpoint(tool_name: str, format: Optional[str] = "json"):
        """
        Получить подробное описание инструмента API.
        
        Возвращает полное описание инструмента API с доступными командами,
        их параметрами и примерами использования. Формат возвращаемых данных
        может быть JSON или Markdown (text).
        
        Args:
            tool_name: Имя инструмента API
            format: Формат вывода (json, text, markdown, html)
        """
        try:
            description = get_tool_description(tool_name, format)
            
            if format.lower() in ["text", "markdown", "html"]:
                if format.lower() == "html":
                    return Response(content=description, media_type="text/html")
                else:
                    return JSONResponse(
                        content={"description": description},
                        media_type="application/json"
                    )
            else:
                return description
                
        except NotFoundError as e:
            logger.warning(f"Tool not found: {tool_name}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": 404,
                        "message": str(e)
                    }
                }
            )
        except Exception as e:
            logger.exception(f"Error generating tool description: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": f"Error generating tool description: {str(e)}"
                    }
                }
            )

    # Execute API tool
    @app.post("/api/tools/{tool_name}")
    async def execute_tool_endpoint(tool_name: str, params: Dict[str, Any] = Body(...)):
        """
        Выполнить инструмент API с указанными параметрами.
        
        Args:
            tool_name: Имя инструмента API
            params: Параметры инструмента
        """
        try:
            result = await execute_tool(tool_name, **params)
            return result
        except NotFoundError as e:
            logger.warning(f"Tool not found: {tool_name}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": 404,
                        "message": str(e)
                    }
                }
            )
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": f"Error executing tool: {str(e)}"
                    }
                }
            )
    
    return app
