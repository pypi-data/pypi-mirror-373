#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Script for generating certificates and tokens for MCP Proxy Adapter configurations.
Generates all necessary certificates, keys, and tokens based on configuration requirements.
Uses mcp_security_framework for certificate generation.
"""
import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
# Import mcp_security_framework
try:
    from mcp_security_framework.core.cert_manager import CertificateManager
    from mcp_security_framework.schemas.config import CertificateConfig, CAConfig, ServerCertConfig, ClientCertConfig
    from mcp_security_framework.schemas.models import CertificateType
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    print("Warning: mcp_security_framework not available, falling back to OpenSSL")
def generate_ca_certificate(output_dir: str) -> str:
    """
    Generate CA certificate and key using mcp_security_framework.
    Args:
        output_dir: Output directory for certificates
    Returns:
        Path to CA certificate file
    """
    ca_dir = os.path.join(output_dir, "certs")
    os.makedirs(ca_dir, exist_ok=True)
    if SECURITY_FRAMEWORK_AVAILABLE:
        try:
            # Configure CA certificate
            ca_config = CAConfig(
                common_name="MCP Proxy Adapter CA",
                organization="MCP Proxy Adapter",
                organizational_unit="Certificate Authority",
                country="US",
                state="State",
                locality="City",
                validity_years=10,  # Используем validity_years вместо validity_days
                key_size=2048,
                hash_algorithm="sha256"
            )
            # Create certificate manager
            cert_config = CertificateConfig(
                cert_storage_path=ca_dir,
                key_storage_path=ca_dir,
                default_validity_days=3650,
                key_size=2048,
                hash_algorithm="sha256"
            )
            cert_manager = CertificateManager(cert_config)
            # Create CA certificate
            cert_pair = cert_manager.create_root_ca(ca_config)
            if cert_pair and cert_pair.certificate_path:
                print(f"✅ Generated CA certificate using mcp_security_framework")
                return cert_pair.certificate_path
            else:
                print(f"❌ Failed to create CA certificate: Invalid certificate pair")
                return None
        except Exception as e:
            print(f"❌ Error creating CA certificate with framework: {e}")
            return None
    else:
        # Fallback to OpenSSL
        ca_key = os.path.join(ca_dir, "ca.key")
        ca_cert = os.path.join(ca_dir, "ca.crt")
        # Generate CA private key
        subprocess.run([
            "openssl", "genrsa", "-out", ca_key, "2048"
        ], check=True, capture_output=True)
        # Generate CA certificate
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-days", "365", "-key", ca_key,
            "-out", ca_cert, "-subj", "/C=US/ST=State/L=City/O=Organization/CN=CA"
        ], check=True, capture_output=True)
        print(f"✅ Generated CA certificate using OpenSSL: {ca_cert}")
        return ca_cert
def generate_server_certificate(output_dir: str, ca_cert: str) -> tuple[str, str]:
    """
    Generate server certificate and key using mcp_security_framework.
    Args:
        output_dir: Output directory for certificates
        ca_cert: Path to CA certificate
    Returns:
        Tuple of (certificate_path, key_path)
    """
    certs_dir = os.path.join(output_dir, "certs")
    keys_dir = os.path.join(output_dir, "keys")
    os.makedirs(certs_dir, exist_ok=True)
    os.makedirs(keys_dir, exist_ok=True)
    if SECURITY_FRAMEWORK_AVAILABLE:
        try:
            # Find CA key file
            ca_key = None
            if ca_cert.endswith('.crt'):
                ca_key = ca_cert.replace('.crt', '.key')
            elif ca_cert.endswith('.pem'):
                ca_key = ca_cert.replace('.pem', '_key.pem')
            if not os.path.exists(ca_key):
                print(f"❌ CA key file not found: {ca_key}")
                return None, None
            # Configure server certificate
            server_config = ServerCertConfig(
                common_name="localhost",
                organization="MCP Proxy Adapter",
                organizational_unit="Server",
                country="US",
                state="State",
                locality="City",
                validity_days=365,
                key_size=2048,
                hash_algorithm="sha256",
                subject_alt_names=["localhost", "127.0.0.1"],  # Используем subject_alt_names вместо san_dns
                ca_cert_path=ca_cert,
                ca_key_path=ca_key
            )
            # Create certificate manager
            cert_config = CertificateConfig(
                cert_storage_path=certs_dir,
                key_storage_path=keys_dir,
                default_validity_days=365,
                key_size=2048,
                hash_algorithm="sha256"
            )
            cert_manager = CertificateManager(cert_config)
            # Create server certificate
            cert_pair = cert_manager.create_server_certificate(server_config)
            if cert_pair and cert_pair.certificate_path and cert_pair.private_key_path:
                print(f"✅ Generated server certificate using mcp_security_framework")
                return (cert_pair.certificate_path, cert_pair.private_key_path)
            else:
                print(f"❌ Failed to create server certificate: Invalid certificate pair")
                return None, None
        except Exception as e:
            print(f"❌ Error creating server certificate with framework: {e}")
            return None, None
    else:
        # Fallback to OpenSSL
        ca_key = ca_cert.replace(".crt", ".key")
        server_key = os.path.join(keys_dir, "server.key")
        server_csr = os.path.join(certs_dir, "server.csr")
        server_cert = os.path.join(certs_dir, "server.crt")
        # Generate server private key
        subprocess.run([
            "openssl", "genrsa", "-out", server_key, "2048"
        ], check=True, capture_output=True)
        # Generate server certificate signing request
        subprocess.run([
            "openssl", "req", "-new", "-key", server_key, "-out", server_csr,
            "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        ], check=True, capture_output=True)
        # Sign server certificate with CA
        subprocess.run([
            "openssl", "x509", "-req", "-in", server_csr, "-CA", ca_cert,
            "-CAkey", ca_key, "-CAcreateserial", "-out", server_cert, "-days", "365"
        ], check=True, capture_output=True)
        # Clean up CSR
        os.remove(server_csr)
        print(f"✅ Generated server certificate using OpenSSL: {server_cert}")
        return server_cert, server_key
def generate_client_certificate(output_dir: str, ca_cert: str, client_name: str = "client",
                               roles: List[str] = None, permissions: List[str] = None) -> tuple[str, str]:
    """
    Generate client certificate and key using mcp_security_framework.
    Args:
        output_dir: Output directory for certificates
        ca_cert: Path to CA certificate
        client_name: Name of the client
        roles: List of roles for the client
        permissions: List of permissions for the client
    Returns:
        Tuple of (certificate_path, key_path)
    """
    certs_dir = os.path.join(output_dir, "certs")
    keys_dir = os.path.join(output_dir, "keys")
    os.makedirs(certs_dir, exist_ok=True)
    os.makedirs(keys_dir, exist_ok=True)
    if SECURITY_FRAMEWORK_AVAILABLE:
        try:
            # Find CA key file
            ca_key = None
            if ca_cert.endswith('.crt'):
                ca_key = ca_cert.replace('.crt', '.key')
            elif ca_cert.endswith('.pem'):
                ca_key = ca_cert.replace('.pem', '_key.pem')
            if not os.path.exists(ca_key):
                print(f"❌ CA key file not found: {ca_key}")
                return None, None
            # Configure client certificate
            client_config = ClientCertConfig(
                common_name=f"{client_name}-client",
                organization="MCP Proxy Adapter",
                organizational_unit="Client",
                country="US",
                state="State",
                locality="City",
                validity_days=730,
                key_size=2048,
                hash_algorithm="sha256",
                roles=roles or [],
                permissions=permissions or [],
                ca_cert_path=ca_cert,
                ca_key_path=ca_key
            )
            # Create certificate manager
            cert_config = CertificateConfig(
                cert_storage_path=certs_dir,
                key_storage_path=keys_dir,
                default_validity_days=730,
                key_size=2048,
                hash_algorithm="sha256"
            )
            cert_manager = CertificateManager(cert_config)
            # Create client certificate
            cert_pair = cert_manager.create_client_certificate(client_config)
            if cert_pair and cert_pair.certificate_path and cert_pair.private_key_path:
                print(f"✅ Generated client certificate {client_name} using mcp_security_framework")
                return (cert_pair.certificate_path, cert_pair.private_key_path)
            else:
                print(f"❌ Failed to create client certificate {client_name}: Invalid certificate pair")
                return None, None
        except Exception as e:
            print(f"❌ Error creating client certificate {client_name} with framework: {e}")
            return None, None
    else:
        # Fallback to OpenSSL
        ca_key = ca_cert.replace(".crt", ".key")
        client_key = os.path.join(keys_dir, f"{client_name}.key")
        client_csr = os.path.join(certs_dir, f"{client_name}.csr")
        client_cert = os.path.join(certs_dir, f"{client_name}.crt")
        # Generate client private key
        subprocess.run([
            "openssl", "genrsa", "-out", client_key, "2048"
        ], check=True, capture_output=True)
        # Generate client certificate signing request
        subprocess.run([
            "openssl", "req", "-new", "-key", client_key, "-out", client_csr,
            "-subj", f"/C=US/ST=State/L=City/O=Organization/CN={client_name}-client"
        ], check=True, capture_output=True)
        # Sign client certificate with CA
        subprocess.run([
            "openssl", "x509", "-req", "-in", client_csr, "-CA", ca_cert,
            "-CAkey", ca_key, "-CAcreateserial", "-out", client_cert, "-days", "730"
        ], check=True, capture_output=True)
        # Clean up CSR
        os.remove(client_csr)
        print(f"✅ Generated client certificate {client_name} using OpenSSL: {client_cert}")
        return client_cert, client_key
def generate_tokens(output_dir: str) -> Dict[str, str]:
    """
    Generate API tokens for different roles.
    Args:
        output_dir: Output directory for tokens
    Returns:
        Dictionary of role -> token mappings
    """
    tokens_dir = os.path.join(output_dir, "tokens")
    os.makedirs(tokens_dir, exist_ok=True)
    tokens = {
        "admin": "test-token-123",
        "user": "user-token-456",
        "readonly": "readonly-token-123",
        "guest": "guest-token-123",
        "proxy": "proxy-token-123"
    }
    # Save tokens to file
    tokens_file = os.path.join(tokens_dir, "tokens.json")
    with open(tokens_file, 'w') as f:
        json.dump(tokens, f, indent=2)
    print(f"✅ Generated tokens: {tokens_file}")
    return tokens
def generate_roles_config(output_dir: str) -> Dict[str, Any]:
    """
    Generate roles configuration file.
    Args:
        output_dir: Output directory for configs
    Returns:
        Roles configuration dictionary
    """
    roles_config = {
        "admin": {
            "permissions": ["read", "write", "execute", "delete", "admin", "register", "unregister", "heartbeat", "discover"],
            "tokens": []
        },
        "user": {
            "permissions": ["read", "execute", "register", "unregister", "heartbeat", "discover"],
            "tokens": []
        },
        "readonly": {
            "permissions": ["read", "discover"],
            "tokens": []
        },
        "guest": {
            "permissions": ["read", "discover"],
            "tokens": []
        },
        "proxy": {
            "permissions": ["register", "unregister", "heartbeat", "discover"],
            "tokens": []
        }
    }
    # Save roles config to file
    roles_file = os.path.join(output_dir, "roles.json")
    with open(roles_file, 'w') as f:
        json.dump(roles_config, f, indent=2)
    print(f"✅ Generated roles configuration: {roles_file}")
    return roles_config
def main():
    """Main function for certificate and token generation."""
    parser = argparse.ArgumentParser(description="Generate certificates and tokens")
    parser.add_argument("--output-dir", "-o", default="./certs", help="Output directory")
    parser.add_argument("--framework", action="store_true", help="Use mcp_security_framework")
    args = parser.parse_args()
    print("🔐 Certificate and Token Generation Script")
    print("=" * 50)
    if args.framework and not SECURITY_FRAMEWORK_AVAILABLE:
        print("❌ mcp_security_framework not available")
        return 1
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    try:
        # 1. Generate CA certificate
        print("\n🔧 Generating CA certificate...")
        ca_cert = generate_ca_certificate(args.output_dir)
        if not ca_cert:
            print("❌ Failed to generate CA certificate")
            return 1
        # 2. Generate server certificate
        print("\n🔧 Generating server certificate...")
        server_cert, server_key = generate_server_certificate(args.output_dir, ca_cert)
        if not server_cert or not server_key:
            print("❌ Failed to generate server certificate")
            return 1
        # 3. Generate client certificates
        print("\n🔧 Generating client certificates...")
        client_configs = [
            ("admin", ["admin"], ["read", "write", "execute", "delete", "admin", "register", "unregister", "heartbeat", "discover"]),
            ("user", ["user"], ["read", "execute", "register", "unregister", "heartbeat", "discover"]),
            ("readonly", ["readonly"], ["read", "discover"]),
            ("guest", ["guest"], ["read", "discover"]),
            ("proxy", ["proxy"], ["register", "unregister", "heartbeat", "discover"])
        ]
        for client_name, roles, permissions in client_configs:
            client_cert, client_key = generate_client_certificate(
                args.output_dir, ca_cert, client_name, roles, permissions
            )
            if not client_cert or not client_key:
                print(f"❌ Failed to generate client certificate {client_name}")
                return 1
        # 4. Generate tokens
        print("\n🔧 Generating tokens...")
        tokens = generate_tokens(args.output_dir)
        # 5. Generate roles configuration
        print("\n🔧 Generating roles configuration...")
        roles_config = generate_roles_config(args.output_dir)
        print("\n🎉 All certificates and tokens generated successfully!")
        print(f"📁 Output directory: {args.output_dir}")
        return 0
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return 1
if __name__ == "__main__":
    exit(main())
