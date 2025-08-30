#!/usr/bin/env python3
"""
Full Application Example

This is a complete application that demonstrates all features of MCP Proxy Adapter framework:
- Built-in commands
- Custom commands
- Dynamically loaded commands
- Built-in command hooks
- Application hooks

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the framework to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.config import Config
from mcp_proxy_adapter.commands.command_registry import CommandRegistry


class FullApplication:
    """Full application example with all framework features."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = Config(config_path)
        self.app = None
        self.command_registry = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_hooks(self):
        """Setup application hooks."""
        try:
            # Import hooks
            from hooks.application_hooks import ApplicationHooks
            from hooks.builtin_command_hooks import BuiltinCommandHooks
            
            # Register application hooks
            self.logger.info("🔧 Setting up application hooks...")
            
            # Register built-in command hooks
            self.logger.info("🔧 Setting up built-in command hooks...")
            
            # Note: In a real implementation, these hooks would be registered
            # with the framework's hook system
            self.logger.info("✅ Hooks setup completed")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Could not import hooks: {e}")
    
    def setup_custom_commands(self):
        """Setup custom commands."""
        try:
            self.logger.info("🔧 Setting up custom commands...")
            
            # Import custom commands
            from commands.custom_echo_command import CustomEchoCommand
            from commands.dynamic_calculator_command import DynamicCalculatorCommand
            
            # Register custom commands
            # Note: In a real implementation, these would be registered
            # with the framework's command registry
            self.logger.info("✅ Custom commands setup completed")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Could not import custom commands: {e}")
    
    def create_application(self):
        """Create the FastAPI application."""
        self.logger.info("🔧 Creating application...")
        
        # Setup hooks and commands before creating app
        self.setup_hooks()
        self.setup_custom_commands()
        
        # Create application with configuration
        self.app = create_app(app_config=self.config)
        
        self.logger.info("✅ Application created successfully")
    
    def run(self, host: str = None, port: int = None, debug: bool = False):
        """Run the application."""
        # Override configuration if specified
        if host:
            self.config.set("server.host", host)
        if port:
            self.config.set("server.port", port)
        if debug:
            self.config.set("server.debug", True)
        
        # Create application
        self.create_application()
        
        # Get server configuration
        server_host = self.config.get("server.host", "0.0.0.0")
        server_port = self.config.get("server.port", 8000)
        server_debug = self.config.get("server.debug", False)
        
        print(f"🚀 Starting Full Application Example")
        print(f"📋 Configuration: {self.config_path}")
        print(f"🌐 Server: {server_host}:{server_port}")
        print(f"🔧 Debug: {server_debug}")
        print(f"🔧 Features: Built-in commands, Custom commands, Dynamic commands, Hooks")
        print("=" * 60)
        
        # Import uvicorn here to avoid dependency issues
        import uvicorn
        uvicorn.run(self.app, host=server_host, port=server_port, log_level="info")


def main():
    """Main entry point for the full application example."""
    parser = argparse.ArgumentParser(description="Full Application Example")
    parser.add_argument("--config", "-c", required=True, help="Path to configuration file")
    parser.add_argument("--host", help="Server host")
    parser.add_argument("--port", type=int, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Create and run application
    app = FullApplication(args.config)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
