"""Main entry point for MCP Proxy Adapter CLI.

This module provides a command-line interface for running
MCP Proxy Adapter applications.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from mcp_proxy_adapter.api.app import create_app


def main():
    """Main CLI entry point."""
    print("MCP Proxy Adapter v6.2.15")
    print("========================")
    print()
    print("Usage:")
    print("  python -m mcp_proxy_adapter")
    print("  # or")
    print("  mcp-proxy-adapter")
    print()
    print("For more information, see:")
    print("  https://github.com/maverikod/mcp-proxy-adapter#readme")


if __name__ == "__main__":
    main()