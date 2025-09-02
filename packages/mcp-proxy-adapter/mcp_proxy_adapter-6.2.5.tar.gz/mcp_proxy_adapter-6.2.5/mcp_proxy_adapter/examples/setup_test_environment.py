#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Script for setting up test environment for MCP Proxy Adapter.
Prepares the test environment with all necessary files and directories.
Uses mcp_security_framework for certificate generation.
"""
import os
import shutil
import sys
from pathlib import Path
# Import mcp_security_framework
try:
    from mcp_security_framework.core.cert_manager import CertificateManager
    from mcp_security_framework.schemas.config import CertificateConfig, CAConfig, ServerCertConfig, ClientCertConfig
    from mcp_security_framework.schemas.models import CertificateType
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    print("Warning: mcp_security_framework not available")
def setup_test_environment():
    """
    Setup test environment with all necessary files and directories.
    """
    print("🔧 Setting up test environment...")
    # Create test environment directory structure
    directories = [
        "examples/basic_framework",
        "examples/full_application",
        "scripts",
        "configs",
        "certs",
        "keys",
        "tokens",
        "logs"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    # Copy example files
    source_examples = "../mcp_proxy_adapter/examples"
    if os.path.exists(source_examples):
        # Copy basic framework
        basic_framework_src = os.path.join(source_examples, "basic_framework")
        if os.path.exists(basic_framework_src):
            shutil.copytree(basic_framework_src, "examples/basic_framework", dirs_exist_ok=True)
            print("✅ Copied basic_framework examples")
        # Copy full application
        full_application_src = os.path.join(source_examples, "full_application")
        if os.path.exists(full_application_src):
            shutil.copytree(full_application_src, "examples/full_application", dirs_exist_ok=True)
            print("✅ Copied full_application examples")
    # Copy utility scripts
    source_utils = "../mcp_proxy_adapter/utils"
    if os.path.exists(source_utils):
        config_generator_src = os.path.join(source_utils, "config_generator.py")
        if os.path.exists(config_generator_src):
            shutil.copy2(config_generator_src, "scripts/")
            print("✅ Copied config_generator.py")
    # Copy certificate generation script
    source_examples = "../mcp_proxy_adapter/examples"
    if os.path.exists(source_examples):
        cert_script_src = os.path.join(source_examples, "create_certificates_simple.py")
        if os.path.exists(cert_script_src):
            shutil.copy2(cert_script_src, "scripts/")
            print("✅ Copied create_certificates_simple.py")
        # Copy new certificate generation script
        cert_tokens_src = os.path.join(source_examples, "generate_certificates_and_tokens.py")
        if os.path.exists(cert_tokens_src):
            shutil.copy2(cert_tokens_src, "scripts/")
            print("✅ Copied generate_certificates_and_tokens.py")
    print("🎉 Test environment setup completed successfully!")
def generate_certificates_with_framework():
    """
    Generate certificates using mcp_security_framework.
    """
    if not SECURITY_FRAMEWORK_AVAILABLE:
        print("❌ mcp_security_framework not available for certificate generation")
        return False
    try:
        print("🔐 Generating certificates using mcp_security_framework...")
        # Configure certificate manager
        cert_config = CertificateConfig(
            cert_storage_path="./certs",
            key_storage_path="./keys",
            default_validity_days=365,
            key_size=2048,
            hash_algorithm="sha256"
        )
        cert_manager = CertificateManager(cert_config)
        # Generate CA certificate
        ca_config = CAConfig(
            common_name="MCP Proxy Adapter Test CA",
            organization="Test Organization",
            organizational_unit="Certificate Authority",
            country="US",
            state="Test State",
            locality="Test City",
            validity_years=10,  # Используем validity_years вместо validity_days
            key_size=2048,
            hash_algorithm="sha256"
        )
        cert_pair = cert_manager.create_root_ca(ca_config)
        if not cert_pair or not cert_pair.certificate_path:
            print(f"❌ Failed to create CA certificate: Invalid certificate pair")
            return False
        print("✅ CA certificate created successfully")
        # Find CA key file
        ca_key_path = cert_pair.private_key_path
        # Generate server certificate
        server_config = ServerCertConfig(
            common_name="localhost",
            organization="Test Organization",
            organizational_unit="Server",
            country="US",
            state="Test State",
            locality="Test City",
            validity_days=365,
            key_size=2048,
            hash_algorithm="sha256",
            subject_alt_names=["localhost", "127.0.0.1"],  # Используем subject_alt_names вместо san_dns
            ca_cert_path=cert_pair.certificate_path,
            ca_key_path=ca_key_path
        )
        cert_pair = cert_manager.create_server_certificate(server_config)
        if not cert_pair or not cert_pair.certificate_path:
            print(f"❌ Failed to create server certificate: Invalid certificate pair")
            return False
        print("✅ Server certificate created successfully")
        # Generate client certificates
        client_configs = [
            ("admin", ["admin"], ["read", "write", "execute", "delete", "admin", "register", "unregister", "heartbeat", "discover"]),
            ("user", ["user"], ["read", "execute", "register", "unregister", "heartbeat", "discover"]),
            ("readonly", ["readonly"], ["read", "discover"]),
            ("guest", ["guest"], ["read", "discover"]),
            ("proxy", ["proxy"], ["register", "unregister", "heartbeat", "discover"])
        ]
        for client_name, roles, permissions in client_configs:
            client_config = ClientCertConfig(
                common_name=f"{client_name}-client",
                organization="Test Organization",
                organizational_unit="Client",
                country="US",
                state="Test State",
                locality="Test City",
                validity_days=730,
                key_size=2048,
                hash_algorithm="sha256",
                roles=roles,
                permissions=permissions,
                ca_cert_path=cert_pair.certificate_path,
                ca_key_path=ca_key_path
            )
            cert_pair = cert_manager.create_client_certificate(client_config)
            if not cert_pair or not cert_pair.certificate_path:
                print(f"❌ Failed to create client certificate {client_name}: Invalid certificate pair")
                return False
            print(f"✅ Client certificate {client_name} created successfully")
        print("🎉 All certificates generated successfully using mcp_security_framework!")
        return True
    except Exception as e:
        print(f"❌ Error generating certificates with framework: {e}")
        return False
def main():
    """Main function for command line execution."""
    try:
        setup_test_environment()
        # Generate certificates if framework is available
        if SECURITY_FRAMEWORK_AVAILABLE:
            generate_certificates_with_framework()
        else:
            print("⚠️ Skipping certificate generation (mcp_security_framework not available)")
    except Exception as e:
        print(f"❌ Error setting up test environment: {e}", file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    exit(main())
