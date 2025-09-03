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
from mcp_proxy_adapter.core.app_factory import create_and_run_server
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
    def setup_proxy_endpoints(self):
        """Setup proxy registration endpoints."""
        try:
            self.logger.info("🔧 Setting up proxy endpoints...")
            # Import proxy endpoints
            from proxy_endpoints import router as proxy_router
            # Add proxy router to the application
            self.app.include_router(proxy_router)
            self.logger.info("✅ Proxy endpoints setup completed")
        except ImportError as e:
            self.logger.warning(f"⚠️ Could not import proxy endpoints: {e}")
    def create_application(self):
        """Create the FastAPI application."""
        self.logger.info("🔧 Creating application...")
        # Setup hooks and commands before creating app
        self.setup_hooks()
        self.setup_custom_commands()
        # Create application with configuration
        self.app = create_app(app_config=self.config)
        # Setup proxy endpoints after app creation
        self.setup_proxy_endpoints()
        self.logger.info("✅ Application created successfully")
    def run(self, host: str = None, port: int = None, debug: bool = False):
        """Run the application using the factory method."""
        # Override configuration if specified
        config_overrides = {}
        if host:
            config_overrides["host"] = host
        if port:
            config_overrides["port"] = port
        if debug:
            config_overrides["debug"] = True
        print(f"🚀 Starting Full Application Example")
        print(f"📋 Configuration: {self.config_path}")
        print(f"🔧 Features: Built-in commands, Custom commands, Dynamic commands, Hooks, Proxy endpoints")
        print("=" * 60)
        # Create application with configuration
        self.create_application()
        # Get server configuration
        server_host = self.config.get("server.host", "0.0.0.0")
        server_port = self.config.get("server.port", 8000)
        server_debug = self.config.get("server.debug", False)
        # Get SSL configuration
        ssl_enabled = self.config.get("ssl.enabled", False)
        ssl_cert_file = self.config.get("ssl.cert_file")
        ssl_key_file = self.config.get("ssl.key_file")
        ssl_ca_cert = self.config.get("ssl.ca_cert")
        verify_client = self.config.get("ssl.verify_client", False)
        print(f"🌐 Server: {server_host}:{server_port}")
        print(f"🔧 Debug: {server_debug}")
        if ssl_enabled:
            print(f"🔐 SSL: Enabled")
            print(f"   Certificate: {ssl_cert_file}")
            print(f"   Key: {ssl_key_file}")
            if ssl_ca_cert:
                print(f"   CA: {ssl_ca_cert}")
            print(f"   Client verification: {verify_client}")
        print("=" * 60)
        # Use hypercorn directly to run the application with proxy endpoints
        try:
            import hypercorn.asyncio
            import hypercorn.config
            import asyncio
            # Configure hypercorn
            config_hypercorn = hypercorn.config.Config()
            config_hypercorn.bind = [f"{server_host}:{server_port}"]
            config_hypercorn.loglevel = "debug" if server_debug else "info"
            if ssl_enabled and ssl_cert_file and ssl_key_file:
                config_hypercorn.certfile = ssl_cert_file
                config_hypercorn.keyfile = ssl_key_file
                if ssl_ca_cert:
                    config_hypercorn.ca_certs = ssl_ca_cert
                if verify_client:
                    import ssl
                    config_hypercorn.verify_mode = ssl.CERT_REQUIRED
                print(f"🔐 Starting HTTPS server with hypercorn...")
            else:
                print(f"🌐 Starting HTTP server with hypercorn...")
            # Run the server
            asyncio.run(hypercorn.asyncio.serve(self.app, config_hypercorn))
        except ImportError:
            print("❌ hypercorn not installed. Installing...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "hypercorn"])
            print("✅ hypercorn installed. Please restart the application.")
            return
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
# Create global app instance for import
app = None

def get_app():
    """Get the FastAPI application instance."""
    global app
    if app is None:
        # Create a default configuration for import
        config = Config("configs/mtls_with_roles.json")  # Default config
        app_instance = FullApplication("configs/mtls_with_roles.json")
        app_instance.create_application()
        app = app_instance.app
    return app

if __name__ == "__main__":
    main()
