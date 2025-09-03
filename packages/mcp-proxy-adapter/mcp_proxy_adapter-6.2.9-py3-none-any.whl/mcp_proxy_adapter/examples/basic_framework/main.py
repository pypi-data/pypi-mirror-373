#!/usr/bin/env python3
"""
Basic Framework Example
This example demonstrates the basic usage of the MCP Proxy Adapter framework
with minimal configuration and built-in commands.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import sys
import argparse
from pathlib import Path
# Add the framework to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mcp_proxy_adapter.core.app_factory import create_and_run_server
def main():
    """Main entry point for the basic framework example."""
    parser = argparse.ArgumentParser(description="Basic Framework Example")
    parser.add_argument("--config", "-c", required=True, help="Path to configuration file")
    parser.add_argument("--host", help="Server host")
    parser.add_argument("--port", type=int, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    # Override configuration if specified
    config_overrides = {}
    if args.host:
        config_overrides["host"] = args.host
    if args.port:
        config_overrides["port"] = args.port
    if args.debug:
        config_overrides["debug"] = True
    print(f"🚀 Starting Basic Framework Example")
    print(f"📋 Configuration: {args.config}")
    print("=" * 50)
    # Use the factory method to create and run the server
    create_and_run_server(
        config_path=args.config,
        title="Basic Framework Example",
        description="Basic MCP Proxy Adapter with minimal configuration",
        version="1.0.0",
        host=config_overrides.get("host", "0.0.0.0"),
        log_level="debug" if config_overrides.get("debug", False) else "info"
    )
if __name__ == "__main__":
    main()
