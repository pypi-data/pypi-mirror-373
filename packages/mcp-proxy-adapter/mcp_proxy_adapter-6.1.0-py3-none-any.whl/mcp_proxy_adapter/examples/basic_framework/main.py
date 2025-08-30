#!/usr/bin/env python3
"""
Basic Framework Example Application

This is a simple application that demonstrates the basic usage of MCP Proxy Adapter framework.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import sys
import argparse
from pathlib import Path

# Add the framework to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.config import Config


def main():
    """Main entry point for the basic framework example."""
    parser = argparse.ArgumentParser(description="Basic Framework Example")
    parser.add_argument("--config", "-c", required=True, help="Path to configuration file")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, help="Server port (overrides config)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Override port if specified
    if args.port:
        config.set("server.port", args.port)
    
    # Override debug if specified
    if args.debug:
        config.set("server.debug", True)
    
    # Create application
    app = create_app(app_config=config)
    
    # Get server configuration
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 8000)
    debug = config.get("server.debug", False)
    
    print(f"🚀 Starting Basic Framework Example")
    print(f"📋 Configuration: {args.config}")
    print(f"🌐 Server: {host}:{port}")
    print(f"🔧 Debug: {debug}")
    print("=" * 50)
    
    # Import uvicorn here to avoid dependency issues
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
