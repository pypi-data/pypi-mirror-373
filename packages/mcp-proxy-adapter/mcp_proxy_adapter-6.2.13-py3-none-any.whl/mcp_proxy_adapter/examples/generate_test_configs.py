#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Script for generating test configurations for MCP Proxy Adapter.
Generates 6 different configuration types for testing various security scenarios.
"""
import json
import os
import argparse
from typing import Dict, Any
def generate_http_simple_config(port: int = 8000) -> Dict[str, Any]:
    """Generate HTTP configuration without authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {"enabled": False},
        "security": {"enabled": False},
        "registration": {
            "enabled": True,
            "auth_method": "token",
            "server_url": "http://127.0.0.1:3004/proxy",
            "token": {"enabled": True, "token": "proxy_registration_token_123"},
            "proxy_info": {
                "name": "mcp_example_server",
                "capabilities": ["jsonrpc", "rest", "proxy_registration"],
                "endpoints": {"jsonrpc": "/api/jsonrpc", "rest": "/cmd", "health": "/health"}
            },
            "heartbeat": {"enabled": True, "interval": 30}
        },
        "protocols": {"enabled": True, "allowed_protocols": ["http"]}
    }
def generate_http_token_config(port: int = 8001) -> Dict[str, Any]:
    """Generate HTTP configuration with token authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {"enabled": False},
        "security": {
            "enabled": True,
            "auth": {"enabled": True, "methods": ["api_key"]},
            "permissions": {"enabled": True, "roles_file": "./roles.json"}
        },
        "protocols": {"enabled": True, "allowed_protocols": ["http"]}
    }
def generate_https_simple_config(port: int = 8002) -> Dict[str, Any]:
    """Generate HTTPS configuration without client certificate verification and authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": "./certs/server_cert.pem",
            "key_file": "./certs/server_key.pem"
        },
        "security": {"enabled": False},
        "protocols": {"enabled": True, "allowed_protocols": ["http", "https"]}
    }
def generate_https_token_config(port: int = 8003) -> Dict[str, Any]:
    """Generate HTTPS configuration without client certificate verification with token authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": "./certs/server_cert.pem",
            "key_file": "./certs/server_key.pem"
        },
        "security": {
            "enabled": True,
            "auth": {"enabled": True, "methods": ["api_key"]},
            "permissions": {"enabled": True, "roles_file": "./roles.json"}
        },
        "protocols": {"enabled": True, "allowed_protocols": ["http", "https"]}
    }
def generate_mtls_no_roles_config(port: int = 8004) -> Dict[str, Any]:
    """Generate mTLS configuration without roles."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": "./certs/server_cert.pem",
            "key_file": "./certs/server_key.pem",
            "ca_cert": "./certs/ca_cert.pem",
            "verify_client": True
        },
        "security": {
            "enabled": True,
            "auth": {"enabled": True, "methods": ["certificate"]},
            "permissions": {"enabled": False, "roles_file": "./roles.json"}
        },
        "protocols": {"enabled": True, "allowed_protocols": ["https", "mtls"]}
    }
def generate_mtls_with_roles_config(port: int = 8005) -> Dict[str, Any]:
    """Generate mTLS configuration with roles."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": "./certs/server_cert.pem",
            "key_file": "./certs/server_key.pem",
            "ca_cert": "./certs/ca_cert.pem",
            "verify_client": True
        },
        "registration": {
            "enabled": True,
            "auth_method": "token",
            "server_url": "http://127.0.0.1:3004/proxy",
            "token": {"enabled": True, "token": "proxy_registration_token_123"},
            "proxy_info": {
                "name": "mcp_example_server",
                "capabilities": ["jsonrpc", "rest", "security", "proxy_registration"],
                "endpoints": {"jsonrpc": "/api/jsonrpc", "rest": "/cmd", "health": "/health"}
            },
            "heartbeat": {"enabled": True, "interval": 30}
        },
        "security": {
            "enabled": True,
            "auth": {"enabled": True, "methods": ["certificate"]},
            "permissions": {"enabled": True, "roles_file": "./roles.json"}
        },
        "protocols": {"enabled": True, "allowed_protocols": ["https", "mtls"]}
    }
def generate_roles_config() -> Dict[str, Any]:
    """Generate roles configuration for testing."""
    return {
        "admin": {
            "description": "Administrator role with full access",
            "permissions": [
                "read",
                "write",
                "execute",
                "delete",
                "admin",
                "register",
                "unregister",
                "heartbeat",
                "discover"
            ],
            "tokens": []
        },
        "user": {
            "description": "User role with limited access",
            "permissions": [
                "read",
                "execute",
                "register",
                "unregister",
                "heartbeat",
                "discover"
            ],
            "tokens": []
        },
        "readonly": {
            "description": "Read-only role",
            "permissions": [
                "read",
                "discover"
            ],
            "tokens": []
        },
        "guest": {
            "description": "Guest role with read-only access",
            "permissions": [
                "read",
                "discover"
            ],
            "tokens": []
        },
        "proxy": {
            "description": "Proxy role for registration",
            "permissions": [
                "register",
                "unregister",
                "heartbeat",
                "discover"
            ],
            "tokens": []
        }
    }
def generate_all_configs(output_dir: str) -> None:
    """Generate all 6 configuration types and save them to files."""
    configs = {
        "http_simple": generate_http_simple_config(8000),
        "http_token": generate_http_token_config(8001),
        "https_simple": generate_https_simple_config(8002),
        "https_token": generate_https_token_config(8003),
        "mtls_no_roles": generate_mtls_no_roles_config(8004),
        "mtls_with_roles": generate_mtls_with_roles_config(8005)
    }
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Generate each configuration
    for name, config in configs.items():
        filename = os.path.join(output_dir, f"{name}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Generated: {filename}")
    # Generate roles configuration
    roles_config = generate_roles_config()
    roles_filename = os.path.join(output_dir, "roles.json")
    with open(roles_filename, 'w', encoding='utf-8') as f:
        json.dump(roles_config, f, indent=2, ensure_ascii=False)
    print(f"Generated: {roles_filename}")
    # Also create roles.json in certs directory for compatibility
    certs_dir = os.path.join(os.path.dirname(output_dir), "certs")
    if os.path.exists(certs_dir):
        certs_roles_filename = os.path.join(certs_dir, "roles.json")
        with open(certs_roles_filename, 'w', encoding='utf-8') as f:
            json.dump(roles_config, f, indent=2, ensure_ascii=False)
        print(f"Generated: {certs_roles_filename}")
    print(f"\nGenerated {len(configs)} configuration files and roles.json in {output_dir}")
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURATION GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Run security tests:")
    print("   python -m mcp_proxy_adapter.examples.run_security_tests")
    print("\n2. Start basic framework example:")
    print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/https_simple.json")
    print("\n3. Start full application example:")
    print("   python -m mcp_proxy_adapter.examples.full_application.main --config configs/mtls_with_roles.json")
    print("=" * 60)
def main():
    """Main function for command line execution."""
    parser = argparse.ArgumentParser(
        description="Generate test configurations for MCP Proxy Adapter"
    )
    parser.add_argument(
        "--output-dir",
        default="./configs",
        help="Output directory for configuration files (default: ./configs)"
    )
    args = parser.parse_args()
    try:
        generate_all_configs(args.output_dir)
        print("Configuration generation completed successfully!")
    except Exception as e:
        print(f"\n❌ CONFIGURATION GENERATION FAILED: {e}")
        print("=" * 60)
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if output directory is writable")
        print("2. Verify JSON encoding support")
        print("3. Check available disk space")
        print("=" * 60)
        return 1
    return 0
if __name__ == "__main__":
    exit(main())
