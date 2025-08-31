#!/usr/bin/env python3
"""
Main entry point for MCP Proxy Adapter.

This module provides the main function for running the MCP Proxy Adapter server.
"""

import argparse
import asyncio
import uvicorn
import sys
import os
from pathlib import Path

from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.core.logging import get_logger, setup_logging
from mcp_proxy_adapter.core.settings import (
    Settings, 
    get_server_host, 
    get_server_port, 
    get_server_debug,
    get_setting
)
from mcp_proxy_adapter.core.ssl_utils import SSLUtils


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MCP Proxy Adapter Server")
    parser.add_argument(
        "--config", 
        type=str, 
        default=None,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind to (overrides config)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to (overrides config)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (overrides config)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level (overrides config)"
    )
    return parser.parse_args()


def main():
    """Run the MCP Proxy Adapter server."""
    args = parse_args()
    
    # Load configuration if specified
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            from mcp_proxy_adapter.config import config
            config.load_from_file(str(config_path))
            print(f"✅ Loaded configuration from: {config_path}")
        else:
            print(f"❌ Configuration file not found: {config_path}")
            sys.exit(1)
    else:
        print("⚠️  No configuration file specified, using defaults")
    
    # Setup logging with configuration
    setup_logging()
    logger = get_logger("mcp_proxy_adapter")
    
    # Get settings from configuration
    server_settings = Settings.get_server_settings()
    logging_settings = Settings.get_logging_settings()
    commands_settings = Settings.get_commands_settings()
    ssl_settings = Settings.get_custom_setting("ssl", {})
    security_settings = Settings.get_custom_setting("security", {})
    
    # STRICT CONFIGURATION VALIDATION
    from mcp_proxy_adapter.core.config_validator import ConfigValidator
    
    # Get full config for validation
    full_config = {
        "server": server_settings,
        "logging": logging_settings,
        "commands": commands_settings,
        "ssl": ssl_settings,
        "security": security_settings,
        "auth_enabled": Settings.get_custom_setting("auth_enabled", False),
        "roles": Settings.get_custom_setting("roles", {})
    }
    
    # Validate configuration
    validator = ConfigValidator(full_config)
    if not validator.validate_all():
        logger.critical("CRITICAL SECURITY ERROR: Configuration validation failed")
        validator.print_validation_report()
        logger.critical("Server startup blocked for security reasons.")
        logger.critical("Please fix configuration errors or disable security features.")
        sys.exit(1)
    
    logger.info("Configuration validation passed")
    
    # Load commands
    from mcp_proxy_adapter.commands.command_registry import registry
    import asyncio
    
    # Reload system to load all commands
    reload_result = asyncio.run(registry.reload_system())
    logger.info(f"Commands loaded: {reload_result}")
    
    # Override settings with command line arguments
    if args.host:
        server_settings['host'] = args.host
    if args.port:
        server_settings['port'] = args.port
    if args.debug:
        server_settings['debug'] = True
    if args.log_level:
        logging_settings['level'] = args.log_level
        server_settings['log_level'] = args.log_level
    
    # Print server header and description
    print("=" * 80)
    print("🚀 MCP PROXY ADAPTER SERVER")
    print("=" * 80)
    print("📋 Configuration:")
    print(f"   • Server: {server_settings['host']}:{server_settings['port']}")
    print(f"   • Debug: {server_settings['debug']}")
    print(f"   • Log Level: {logging_settings['level']}")
    print(f"   • Auto Discovery: {commands_settings['auto_discovery']}")
    print(f"   • SSL Enabled: {ssl_settings.get('enabled', False)}")
    print(f"   • Security Enabled: {security_settings.get('enabled', False)}")
    if ssl_settings.get('enabled', False):
        print(f"   • SSL Mode: {ssl_settings.get('mode', 'https_only')}")
    if security_settings.get('enabled', False):
        print(f"   • Security Framework: {security_settings.get('framework', 'built-in')}")
    print("=" * 80)
    print()
    
    logger.info("Starting MCP Proxy Adapter Server...")
    logger.info(f"Server configuration: {server_settings}")
    logger.info(f"Security configuration: {security_settings}")
    
    try:
        # Create application
        app = create_app(
            title="MCP Proxy Adapter Server",
            description="Model Context Protocol Proxy Adapter with Security Framework",
            version="1.0.0"
        )
        
        # Create unified server configuration
        server_config = {
            "host": server_settings['host'],
            "port": server_settings['port'],
            "log_level": server_settings.get('log_level', 'info'),
            "ssl": ssl_settings
        }
        
        # Use unified server runner
        from mcp_proxy_adapter.core.server_adapter import UnifiedServerRunner
        server_runner = UnifiedServerRunner()
        
        # Run the server with optimal engine selection
        server_runner.run_server(app, server_config)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
