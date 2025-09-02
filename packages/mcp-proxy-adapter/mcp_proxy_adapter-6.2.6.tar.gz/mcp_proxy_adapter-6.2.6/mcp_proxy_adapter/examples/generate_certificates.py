#!/usr/bin/env python3
"""
Certificate Generation Script
This script generates all necessary certificates for the examples using
mcp_security_framework API directly.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

def main():
    """Generate all certificates for examples."""
    print("🔐 Certificate Generation Script")
    print("=" * 50)

    # Create directories
    cert_dir = Path("certs")
    key_dir = Path("keys")
    cert_dir.mkdir(exist_ok=True)
    key_dir.mkdir(exist_ok=True)

    # Check if mcp_security_framework is available
    try:
        from mcp_security_framework.core.cert_manager import CertificateManager
        from mcp_security_framework.schemas import (
            CAConfig, ServerCertConfig, ClientCertConfig, CertificateConfig
        )
        print("✅ mcp_security_framework API available")
    except ImportError as e:
        print(f"❌ mcp_security_framework not found: {e}")
        return False

    try:
        print("🔧 Creating root CA certificate...")
        # Create CA certificate directly
        ca_config = CAConfig(
            common_name="MCP Proxy Adapter CA",
            organization="MCP Proxy Adapter",
            organizational_unit="Development",
            country="US",
            state="State",
            locality="City",
            validity_years=10,
            key_size=2048
        )

        # Use CLI to create CA first
        import subprocess
        result = subprocess.run([
            "python", "-m", "mcp_security_framework.cli.cert_cli", "create-ca",
            "--common-name", "MCP Proxy Adapter CA",
            "--organization", "MCP Proxy Adapter",
            "--country", "US",
            "--state", "State",
            "--locality", "City",
            "--validity-years", "10",
            "--key-size", "2048"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ CA creation failed: {result.stderr}")
            return False

        ca_cert_path = cert_dir / "mcp_proxy_adapter_ca_ca.crt"
        ca_key_path = key_dir / "mcp_proxy_adapter_ca_ca.key"
        print(f"✅ Root CA certificate created: {ca_cert_path}")

        # Now initialize certificate manager with existing CA
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=str(ca_cert_path),
            ca_key_path=str(ca_key_path),
            cert_storage_path=str(cert_dir),
            key_storage_path=str(key_dir)
        )

        # Initialize certificate manager
        cert_manager = CertificateManager(cert_config)

        print("🔧 Creating server certificate...")
        # Create server certificate
        server_config = ServerCertConfig(
            common_name="localhost",
            organization="MCP Proxy Adapter",
            country="US",
            validity_days=365,
            key_size=2048,
            subject_alt_names=["localhost", "127.0.0.1"],
            ca_cert_path=str(ca_cert_path),
            ca_key_path=str(ca_key_path)
        )

        server_cert_pair = cert_manager.create_server_certificate(server_config)
        print(f"✅ Server certificate created: {server_cert_pair.certificate_path}")

        print("🔧 Creating admin client certificate...")
        # Create admin client certificate
        admin_config = ClientCertConfig(
            common_name="admin",
            organization="MCP Proxy Adapter",
            country="US",
            validity_days=365,
            key_size=2048,
            roles=["admin"],
            permissions=["read", "write", "delete"],
            ca_cert_path=str(ca_cert_path),
            ca_key_path=str(ca_key_path)
        )

        admin_cert_pair = cert_manager.create_client_certificate(admin_config)
        print(f"✅ Admin client certificate created: {admin_cert_pair.certificate_path}")

        print("🔧 Creating user client certificate...")
        # Create user client certificate
        user_config = ClientCertConfig(
            common_name="user",
            organization="MCP Proxy Adapter",
            country="US",
            validity_days=365,
            key_size=2048,
            roles=["user"],
            permissions=["read", "write"],
            ca_cert_path=str(ca_cert_path),
            ca_key_path=str(ca_key_path)
        )

        user_cert_pair = cert_manager.create_client_certificate(user_config)
        print(f"✅ User client certificate created: {user_cert_pair.certificate_path}")

        print("🔧 Creating readonly client certificate...")
        # Create readonly client certificate
        readonly_config = ClientCertConfig(
            common_name="readonly",
            organization="MCP Proxy Adapter",
            country="US",
            validity_days=365,
            key_size=2048,
            roles=["readonly"],
            permissions=["read"],
            ca_cert_path=str(ca_cert_path),
            ca_key_path=str(ca_key_path)
        )

        readonly_cert_pair = cert_manager.create_client_certificate(readonly_config)
        print(f"✅ Readonly client certificate created: {readonly_cert_pair.certificate_path}")

        print("\n🎉 All certificates generated successfully!")
        print(f"📁 Certificates are stored in the '{cert_dir}' directory")
        print(f"🔑 Private keys are stored in the '{key_dir}' directory")
        print(f"🔐 CA certificate: {ca_cert_path}")
        print(f"🔐 Server certificate: {server_cert_pair.certificate_path}")
        return True

    except Exception as e:
        print(f"❌ Certificate generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
