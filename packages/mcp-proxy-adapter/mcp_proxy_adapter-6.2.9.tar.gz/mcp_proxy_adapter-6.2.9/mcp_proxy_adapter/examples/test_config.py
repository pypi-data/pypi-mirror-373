#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Script for testing MCP Proxy Adapter configurations.
Tests a specific configuration by creating an application and validating it.
Uses mcp_security_framework for security validation.
"""
import json
import os
import sys
import argparse
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
# Import mcp_security_framework
try:
    from mcp_security_framework import SecurityManager
    from mcp_security_framework.schemas.config import SecurityConfig
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    print("Warning: mcp_security_framework not available")
# Add parent directory to path to import mcp_proxy_adapter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
def validate_security_config(config: Dict[str, Any]) -> bool:
    """
    Validate security configuration using mcp_security_framework.
    Args:
        config: Configuration dictionary
    Returns:
        True if validation passed, False otherwise
    """
    if not SECURITY_FRAMEWORK_AVAILABLE:
        print("⚠️ Skipping security validation (mcp_security_framework not available)")
        return True
    try:
        security_section = config.get("security", {})
        if not security_section.get("enabled", False):
            print("🔓 Security framework disabled in configuration")
            return True
        print("🔒 Validating security configuration with mcp_security_framework...")
        # Create SecurityConfig from configuration
        security_config = SecurityConfig(
            auth=security_section.get("auth", {}),
            ssl=security_section.get("ssl", {}),
            permissions=security_section.get("permissions", {}),
            rate_limit=security_section.get("rate_limit", {})
        )
        # Create SecurityManager for validation
        security_manager = SecurityManager(security_config)
        # Validate configuration
        validation_result = security_manager.validate_configuration()
        if validation_result.is_valid:
            print("✅ Security configuration validation passed")
            return True
        else:
            print("❌ Security configuration validation failed:")
            for error in validation_result.errors:
                print(f"  - {error}")
            return False
    except Exception as e:
        print(f"❌ Error validating security configuration: {e}")
        return False
def test_configuration(config_path: str, timeout: int = 30) -> bool:
    """
    Test a configuration by creating an application and validating it.
    Args:
        config_path: Path to configuration file
        timeout: Timeout in seconds for server startup
    Returns:
        True if test passed, False otherwise
    """
    print(f"🧪 Testing configuration: {config_path}")
    print("=" * 60)
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        # Import required modules
        from mcp_proxy_adapter.core.app_factory import create_application
        from mcp_proxy_adapter.core.app_runner import ApplicationRunner
        # Create application
        print("🔧 Creating application...")
        app = create_application(config)
        print("✅ Application created successfully")
        # Create runner and validate configuration
        print("🔍 Validating configuration...")
        runner = ApplicationRunner(app, config)
        errors = runner.validate_configuration()
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        print("✅ Configuration validation passed")
        # Validate security configuration
        if not validate_security_config(config):
            return False
        # Test server startup (without actually starting)
        print("🚀 Testing server startup...")
        server_config = config.get("server", {})
        host = server_config.get("host", "127.0.0.1")
        port = server_config.get("port", 8000)
        print(f"✅ Server configuration: {host}:{port}")
        # Test SSL configuration if enabled
        ssl_config = config.get("ssl", {})
        if ssl_config.get("enabled", False):
            print("🔐 SSL configuration:")
            print(f"  - Certificate: {ssl_config.get('cert_file', 'N/A')}")
            print(f"  - Key: {ssl_config.get('key_file', 'N/A')}")
            print(f"  - Client verification: {ssl_config.get('verify_client', False)}")
        # Test security configuration if enabled
        security_config = config.get("security", {})
        if security_config.get("enabled", False):
            print("🔒 Security configuration:")
            auth_config = security_config.get("auth", {})
            if auth_config.get("enabled", False):
                methods = auth_config.get("methods", [])
                print(f"  - Authentication methods: {methods}")
            permissions_config = security_config.get("permissions", {})
            if permissions_config.get("enabled", False):
                print(f"  - Roles file: {permissions_config.get('roles_file', 'N/A')}")
        # Test protocol configuration
        protocols_config = config.get("protocols", {})
        if protocols_config.get("enabled", False):
            allowed_protocols = protocols_config.get("allowed_protocols", [])
            print(f"🌐 Allowed protocols: {allowed_protocols}")
        print("=" * 60)
        print("✅ Configuration test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
def main():
    """Main function for command line execution."""
    parser = argparse.ArgumentParser(description="Test MCP Proxy Adapter configuration")
    parser.add_argument("--config", "-c", required=True, help="Path to configuration file")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Timeout in seconds")
    args = parser.parse_args()
    if not os.path.exists(args.config):
        print(f"❌ Configuration file not found: {args.config}")
        return 1
    success = test_configuration(args.config, args.timeout)
    return 0 if success else 1
if __name__ == "__main__":
    exit(main())
