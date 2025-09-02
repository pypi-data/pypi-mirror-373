"""
Application Factory for MCP Proxy Adapter

This module provides a factory function for creating and running MCP Proxy Adapter servers
with proper configuration validation and initialization.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI
from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.core.logging import setup_logging, get_logger
from mcp_proxy_adapter.config import config
from mcp_proxy_adapter.commands.builtin_commands import register_builtin_commands

logger = get_logger("app_factory")


def create_and_run_server(
    config_path: Optional[str] = None,
    log_config_path: Optional[str] = None,
    title: str = "MCP Proxy Adapter Server",
    description: str = "Model Context Protocol Proxy Adapter with Security Framework",
    version: str = "1.0.0",
    host: str = "0.0.0.0",
    log_level: str = "info",
    engine: Optional[str] = None
) -> None:
    """
    Create and run MCP Proxy Adapter server with proper validation.
    
    This factory function validates all configuration files, sets up logging,
    initializes the application, and starts the server with optimal settings.
    
    Args:
        config_path: Path to configuration file (JSON)
        log_config_path: Path to logging configuration file (optional)
        title: Application title for OpenAPI schema
        description: Application description for OpenAPI schema
        version: Application version
        host: Server host address
        port: Server port
        log_level: Logging level
        engine: Specific server engine to use (optional)
        
    Raises:
        SystemExit: If configuration validation fails or server cannot start
    """
    print("🚀 MCP Proxy Adapter Server Factory")
    print("=" * 60)
    print(f"📋 Title: {title}")
    print(f"📝 Description: {description}")
    print(f"🔢 Version: {version}")
    print(f"🌐 Host: {host}")
    print(f"📊 Log Level: {log_level}")
    print("=" * 60)
    print()
    
    # 1. Validate and load configuration file
    app_config = None
    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"❌ Configuration file not found: {config_path}")
            print("   Please provide a valid path to config.json")
            sys.exit(1)
        
        try:
            config.load_from_file(str(config_file))
            app_config = config.get_all()
            print(f"✅ Configuration loaded from: {config_path}")
            
            # Debug: Check what config.get_all() actually returns
            print(f"🔍 Debug: config.get_all() keys: {list(app_config.keys())}")
            if "security" in app_config:
                security_ssl = app_config["security"].get("ssl", {})
                print(f"🔍 Debug: config.get_all() security.ssl: {security_ssl}")
            
            # Debug: Check if root ssl section exists after loading
            if "ssl" in app_config:
                print(f"🔍 Debug: Root SSL section after loading: enabled={app_config['ssl'].get('enabled', False)}")
                print(f"🔍 Debug: Root SSL section after loading: cert_file={app_config['ssl'].get('cert_file')}")
                print(f"🔍 Debug: Root SSL section after loading: key_file={app_config['ssl'].get('key_file')}")
            else:
                print(f"🔍 Debug: No root SSL section after loading")
            
            # Debug: Check app_config immediately after get_all()
            if app_config and "security" in app_config:
                ssl_config = app_config["security"].get("ssl", {})
                print(f"🔍 Debug: app_config after get_all(): SSL enabled={ssl_config.get('enabled', False)}")
                print(f"🔍 Debug: app_config after get_all(): SSL cert_file={ssl_config.get('cert_file')}")
                print(f"🔍 Debug: app_config after get_all(): SSL key_file={ssl_config.get('key_file')}")
            
            # Debug: Check SSL configuration after loading
            if app_config and "security" in app_config:
                ssl_config = app_config["security"].get("ssl", {})
                print(f"🔍 Debug: SSL config after loading: enabled={ssl_config.get('enabled', False)}")
                print(f"🔍 Debug: SSL config after loading: cert_file={ssl_config.get('cert_file')}")
                print(f"🔍 Debug: SSL config after loading: key_file={ssl_config.get('key_file')}")
                
                # Debug: Check if SSL config is correct
                if ssl_config.get('enabled', False):
                    print(f"🔍 Debug: SSL config is enabled and correct")
                else:
                    print(f"🔍 Debug: SSL config is disabled or incorrect")
                    # Try to get SSL config from root level
                    root_ssl = app_config.get("ssl", {})
                    print(f"🔍 Debug: Root SSL config: enabled={root_ssl.get('enabled', False)}")
                    print(f"🔍 Debug: Root SSL config: cert_file={root_ssl.get('cert_file')}")
                    print(f"🔍 Debug: Root SSL config: key_file={root_ssl.get('key_file')}")
            
            # Validate security framework configuration only if enabled
            security_config = app_config.get("security", {})
            if security_config.get("enabled", False):
                framework = security_config.get("framework", "mcp_security_framework")
                print(f"🔒 Security framework: {framework}")
                
                # Debug: Check SSL config before validation
                ssl_config = security_config.get("ssl", {})
                print(f"🔍 Debug: SSL config before validation: enabled={ssl_config.get('enabled', False)}")
                
                # Validate security configuration
                from mcp_proxy_adapter.core.unified_config_adapter import UnifiedConfigAdapter
                adapter = UnifiedConfigAdapter()
                validation_result = adapter.validate_configuration(app_config)
                
                # Debug: Check SSL config after validation
                ssl_config = app_config.get("security", {}).get("ssl", {})
                print(f"🔍 Debug: SSL config after validation: enabled={ssl_config.get('enabled', False)}")
                
                if not validation_result.is_valid:
                    print("❌ Security configuration validation failed:")
                    for error in validation_result.errors:
                        print(f"   - {error}")
                    sys.exit(1)
                
                if validation_result.warnings:
                    print("⚠️  Security configuration warnings:")
                    for warning in validation_result.warnings:
                        print(f"   - {warning}")
                
                print("✅ Security configuration validated successfully")
            else:
                print("🔓 Security framework disabled")
                
        except Exception as e:
            print(f"❌ Failed to load configuration from {config_path}: {e}")
            sys.exit(1)
    else:
        print("⚠️  No configuration file provided, using defaults")
        app_config = config.get_all()
    
    # 2. Setup logging
    try:
        if log_config_path:
            log_config_file = Path(log_config_path)
            if not log_config_file.exists():
                print(f"❌ Log configuration file not found: {log_config_path}")
                sys.exit(1)
            setup_logging(log_config_path=str(log_config_file))
            print(f"✅ Logging configured from: {log_config_path}")
        else:
            setup_logging()
            print("✅ Logging configured with defaults")
    except Exception as e:
        print(f"❌ Failed to setup logging: {e}")
        sys.exit(1)
    
    # 3. Register built-in commands
    try:
        builtin_count = register_builtin_commands()
        print(f"✅ Registered {builtin_count} built-in commands")
    except Exception as e:
        print(f"❌ Failed to register built-in commands: {e}")
        sys.exit(1)
    
    # 4. Create FastAPI application with configuration
    try:
        # Debug: Check app_config before passing to create_app
        if app_config and "security" in app_config:
            ssl_config = app_config["security"].get("ssl", {})
            print(f"🔍 Debug: app_config before create_app: SSL enabled={ssl_config.get('enabled', False)}")
            print(f"🔍 Debug: app_config before create_app: SSL cert_file={ssl_config.get('cert_file')}")
            print(f"🔍 Debug: app_config before create_app: SSL key_file={ssl_config.get('key_file')}")
        
        app = create_app(
            title=title,
            description=description,
            version=version,
            app_config=app_config,  # Pass configuration to create_app
            config_path=config_path  # Pass config path to preserve SSL settings
        )
        print("✅ FastAPI application created successfully")
    except Exception as e:
        print(f"❌ Failed to create FastAPI application: {e}")
        sys.exit(1)
    
    # 5. Create server configuration
    # Get port from config if available, otherwise use default
    server_port = app_config.get("server", {}).get("port", 8000) if app_config else 8000
    print(f"🔌 Port: {server_port}")
    
    server_config = {
        "host": host,
        "port": server_port,
        "log_level": log_level,
        "reload": False
    }
    
    # Add SSL configuration if present
    print(f"🔍 Debug: app_config keys: {list(app_config.keys()) if app_config else 'None'}")
    
    # Check for SSL config in root section first (higher priority)
    if app_config and "ssl" in app_config:
        print(f"🔍 Debug: SSL config found in root: {app_config['ssl']}")
        print(f"🔍 Debug: SSL enabled: {app_config['ssl'].get('enabled', False)}")
        if app_config["ssl"].get("enabled", False):
            ssl_config = app_config["ssl"]
            # Add SSL config directly to server_config for Hypercorn
            server_config["certfile"] = ssl_config.get("cert_file")
            server_config["keyfile"] = ssl_config.get("key_file")
            server_config["ca_certs"] = ssl_config.get("ca_cert_file")
            server_config["verify_mode"] = ssl_config.get("verify_mode")
            print(f"🔒 SSL enabled: {ssl_config.get('cert_file', 'N/A')}")
            print(f"🔒 SSL enabled: cert={ssl_config.get('cert_file')}, key={ssl_config.get('key_file')}")
            print(f"🔒 Server config SSL: certfile={server_config.get('certfile')}, keyfile={server_config.get('keyfile')}, ca_certs={server_config.get('ca_certs')}, verify_mode={server_config.get('verify_mode')}")
    
    # Check for SSL config in security section (fallback)
    if app_config and "security" in app_config:
        security_config = app_config["security"]
        print(f"🔍 Debug: security_config keys: {list(security_config.keys())}")
        if "ssl" in security_config:
            print(f"🔍 Debug: SSL config found in security: {security_config['ssl']}")
            print(f"🔍 Debug: SSL enabled: {security_config['ssl'].get('enabled', False)}")
            if security_config["ssl"].get("enabled", False):
                ssl_config = security_config["ssl"]
                # Add SSL config directly to server_config for Hypercorn
                server_config["certfile"] = ssl_config.get("cert_file")
                server_config["keyfile"] = ssl_config.get("key_file")
                server_config["ca_certs"] = ssl_config.get("ca_cert_file")
                server_config["verify_mode"] = ssl_config.get("verify_mode")
                print(f"🔒 SSL enabled: {ssl_config.get('cert_file', 'N/A')}")
                print(f"🔒 SSL enabled: cert={ssl_config.get('cert_file')}, key={ssl_config.get('key_file')}")
                print(f"🔒 Server config SSL: certfile={server_config.get('certfile')}, keyfile={server_config.get('keyfile')}, ca_certs={server_config.get('ca_certs')}, verify_mode={server_config.get('verify_mode')}")
        print(f"🔍 Debug: SSL config found in root: {app_config['ssl']}")
        print(f"🔍 Debug: SSL enabled: {app_config['ssl'].get('enabled', False)}")
        if app_config["ssl"].get("enabled", False):
            ssl_config = app_config["ssl"]
            # Add SSL config directly to server_config for Hypercorn
            server_config["certfile"] = ssl_config.get("cert_file")
            server_config["keyfile"] = ssl_config.get("key_file")
            server_config["ca_certs"] = ssl_config.get("ca_cert_file")
            server_config["verify_mode"] = ssl_config.get("verify_mode")
            print(f"🔒 SSL enabled: {ssl_config.get('cert_file', 'N/A')}")
            print(f"🔒 SSL enabled: cert={ssl_config.get('cert_file')}, key={ssl_config.get('key_file')}")
            print(f"🔒 Server config SSL: certfile={server_config.get('certfile')}, keyfile={server_config.get('keyfile')}, ca_certs={server_config.get('ca_certs')}, verify_mode={server_config.get('verify_mode')}")
    
    # 6. Start server
    try:
        print("🚀 Starting server...")
        print("   Use Ctrl+C to stop the server")
        print("=" * 60)
        
        # Use hypercorn directly
        import hypercorn.asyncio
        import hypercorn.config
        import asyncio
        
        # Configure hypercorn
        config_hypercorn = hypercorn.config.Config()
        config_hypercorn.bind = [f"{server_config['host']}:{server_config['port']}"]
        config_hypercorn.loglevel = server_config.get("log_level", "info")
        
        # Add SSL configuration if present
        if "certfile" in server_config:
            config_hypercorn.certfile = server_config["certfile"]
        if "keyfile" in server_config:
            config_hypercorn.keyfile = server_config["keyfile"]
        if "ca_certs" in server_config:
            config_hypercorn.ca_certs = server_config["ca_certs"]
        if "verify_mode" in server_config:
            import ssl
            config_hypercorn.verify_mode = ssl.CERT_REQUIRED
        
        # Determine if SSL is enabled
        ssl_enabled = any(key in server_config for key in ["certfile", "keyfile"])
        
        if ssl_enabled:
            print(f"🔐 Starting HTTPS server with hypercorn...")
        else:
            print(f"🌐 Starting HTTP server with hypercorn...")
        
        # Run the server
        asyncio.run(hypercorn.asyncio.serve(app, config_hypercorn))
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def validate_config_file(config_path: str) -> bool:
    """
    Validate configuration file exists and is readable.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"❌ Configuration file not found: {config_path}")
            return False
        
        # Try to load configuration to validate JSON format
        config.load_from_file(str(config_file))
        return True
        
    except Exception as e:
        print(f"❌ Configuration file validation failed: {e}")
        return False


def validate_log_config_file(log_config_path: str) -> bool:
    """
    Validate logging configuration file exists and is readable.
    
    Args:
        log_config_path: Path to logging configuration file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        log_config_file = Path(log_config_path)
        if not log_config_file.exists():
            print(f"❌ Log configuration file not found: {log_config_path}")
            return False
        return True
        
    except Exception as e:
        print(f"❌ Log configuration file validation failed: {e}")
        return False


def create_application(
    config: Dict[str, Any],
    title: str = "MCP Proxy Adapter",
    description: str = "JSON-RPC API for interacting with MCP Proxy",
    version: str = "1.0.0"
) -> FastAPI:
    """
    Creates and configures FastAPI application.
    
    Args:
        config: Application configuration dictionary
        title: Application title
        description: Application description
        version: Application version
        
    Returns:
        Configured FastAPI application
    """
    from fastapi.middleware.cors import CORSMiddleware
    from mcp_proxy_adapter.api.app import create_app
    from mcp_proxy_adapter.core.logging import setup_logging
    from mcp_proxy_adapter.commands.builtin_commands import register_builtin_commands
    
    # Setup logging
    setup_logging()
    
    # Register built-in commands
    register_builtin_commands()
    
    # Create FastAPI application using existing create_app function
    app = create_app(
        title=title,
        description=description,
        version=version,
        app_config=config
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add health endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": version}
    
    return app
