#!/usr/bin/env python3
"""
Certificate Generation Script
This script generates all necessary certificates for the examples using
mcp_security_framework certificate management tools.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import os
import subprocess
import sys
from pathlib import Path
def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
def main():
    """Generate all certificates for examples."""
    print("🔐 Certificate Generation Script")
    print("=" * 50)
    # Create directories
    cert_dir = Path("certs")
    cert_dir.mkdir(exist_ok=True)
    # Check if mcp_security_framework is available
    try:
        import mcp_security_framework
        print(f"✅ mcp_security_framework version {mcp_security_framework.__version__} found")
    except ImportError:
        print("❌ mcp_security_framework not found")
        return False
    # Generate CA certificate
    if not run_command(
        "python -m mcp_security_framework.cli.cert_cli create-ca "
        "--common-name 'MCP Proxy Adapter CA' "
        "--organization 'MCP Proxy Adapter' "
        "--country 'US' "
        "--state 'State' "
        "--locality 'City' "
        "--validity-years 10 "
        "--key-size 2048",
        "Creating root CA certificate"
    ):
        return False
    # Generate server certificate
    if not run_command(
        "python -m mcp_security_framework.cli.cert_cli -c cert_config.json create-server "
        "--common-name 'localhost' "
        "--organization 'MCP Proxy Adapter' "
        "--country 'US' "
        "--validity-days 365 "
        "--key-size 2048",
        "Creating server certificate"
    ):
        return False
    # Generate admin client certificate
    if not run_command(
        "python -m mcp_security_framework.cli.cert_cli -c cert_config.json create-client "
        "--common-name 'admin' "
        "--organization 'MCP Proxy Adapter' "
        "--country 'US' "
        "--validity-days 365 "
        "--key-size 2048 "
        "--roles 'admin' "
        "--permissions 'read,write,delete'",
        "Creating admin client certificate"
    ):
        return False
    # Generate user client certificate
    if not run_command(
        "python -m mcp_security_framework.cli.cert_cli -c cert_config.json create-client "
        "--common-name 'user' "
        "--organization 'MCP Proxy Adapter' "
        "--country 'US' "
        "--validity-days 365 "
        "--key-size 2048 "
        "--roles 'user' "
        "--permissions 'read,write'",
        "Creating user client certificate"
    ):
        return False
    # Generate readonly client certificate
    if not run_command(
        "python -m mcp_security_framework.cli.cert_cli -c cert_config.json create-client "
        "--common-name 'readonly' "
        "--organization 'MCP Proxy Adapter' "
        "--country 'US' "
        "--validity-days 365 "
        "--key-size 2048 "
        "--roles 'readonly' "
        "--permissions 'read'",
        "Creating readonly client certificate"
    ):
        return False
    print("\n🎉 All certificates generated successfully!")
    print("📁 Certificates are stored in the 'certs' directory")
    return True
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
