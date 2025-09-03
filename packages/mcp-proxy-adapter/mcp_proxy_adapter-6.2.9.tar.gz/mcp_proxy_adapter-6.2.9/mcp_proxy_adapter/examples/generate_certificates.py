#!/usr/bin/env python3
"""
Certificate Generation Script
This script generates all necessary certificates for the examples using
mcp_security_framework API directly.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import os
import sys
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
        
        # Initialize certificate manager first
        cert_config = CertificateConfig(
            cert_storage_path=str(cert_dir),
            key_storage_path=str(key_dir),
            default_validity_days=365,
            key_size=2048,
            hash_algorithm="sha256"
        )
        cert_manager = CertificateManager(cert_config)
        
        # Create CA certificate using API
        ca_config = CAConfig(
            common_name="MCP Proxy Adapter CA",
            organization="MCP Proxy Adapter",
            organizational_unit="Development",
            country="US",
            state="State",
            locality="City",
            validity_years=10,
            key_size=2048,
            hash_algorithm="sha256"
        )
        
        ca_cert_pair = cert_manager.create_root_ca(ca_config)
        if not ca_cert_pair or not ca_cert_pair.certificate_path:
            print("❌ Failed to create CA certificate")
            return False
            
        ca_cert_path = ca_cert_pair.certificate_path
        ca_key_path = ca_cert_pair.private_key_path
        print(f"✅ Root CA certificate created: {ca_cert_path}")

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
        
        print("\n" + "=" * 60)
        print("✅ CERTIFICATE GENERATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\n📋 NEXT STEPS:")
        print("1. Generate test configurations:")
        print("   python -m mcp_proxy_adapter.examples.generate_test_configs --output-dir configs")
        print("\n2. Run security tests:")
        print("   python -m mcp_proxy_adapter.examples.run_security_tests")
        print("\n3. Start basic framework example:")
        print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/https_simple.json")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ CERTIFICATE GENERATION FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if mcp_security_framework is installed:")
        print("   pip install mcp_security_framework")
        print("\n2. Verify write permissions in current directory")
        print("\n3. Check if certs/ and keys/ directories exist")
        print("=" * 60)
        return False

if __name__ == "__main__":
    print("🔐 Starting certificate generation...")
    success = main()
    if success:
        print("\n✅ Script completed successfully!")
    else:
        print("\n❌ Script failed with errors!")
    sys.exit(0 if success else 1)
