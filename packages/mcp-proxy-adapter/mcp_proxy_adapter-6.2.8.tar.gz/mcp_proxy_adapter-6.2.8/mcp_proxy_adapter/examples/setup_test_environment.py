#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Script for setting up test environment for MCP Proxy Adapter.
Prepares the test environment with all necessary files and directories.
Uses mcp_security_framework for certificate generation.

This script accepts an output directory and copies required example files
and helper scripts into that directory, creating a ready-to-use workspace.
By default, the current working directory is used, so end-users can run
it in their project root after installing this framework in a virtual
environment.
"""
import shutil
import sys
import argparse
from pathlib import Path
# Import mcp_security_framework
try:
    from mcp_security_framework.core.cert_manager import CertificateManager
    from mcp_security_framework.schemas.config import (
        CertificateConfig,
        CAConfig,
        ServerCertConfig,
        ClientCertConfig,
    )
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    print("Warning: mcp_security_framework not available")


def _get_package_paths() -> tuple[Path, Path]:
    """
    Resolve source paths for examples and utils relative to this file
    to avoid importing the package during setup.
    """
    pkg_root = Path(__file__).resolve().parents[1]
    return pkg_root / "examples", pkg_root / "utils"


def setup_test_environment(output_dir: Path) -> None:
    """
    Setup test environment under output_dir with required files
    and directories.

    All created directories and copied files are rooted at output_dir
    so users can run scripts relative to that directory.
    """
    print("🔧 Setting up test environment...")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
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
        target_dir = output_dir / directory
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {target_dir}")
    # Resolve package paths
    examples_src_root, utils_src_root = _get_package_paths()
    # Copy example files
    basic_framework_src = examples_src_root / "basic_framework"
    if basic_framework_src.exists():
        shutil.copytree(
            basic_framework_src,
            output_dir / "examples/basic_framework",
            dirs_exist_ok=True,
        )
        print("✅ Copied basic_framework examples")
    full_application_src = examples_src_root / "full_application"
    if full_application_src.exists():
        shutil.copytree(
            full_application_src,
            output_dir / "examples/full_application",
            dirs_exist_ok=True,
        )
        print("✅ Copied full_application examples")
    # Copy utility scripts
    config_generator_src = utils_src_root / "config_generator.py"
    if config_generator_src.exists():
        shutil.copy2(config_generator_src, output_dir / "scripts/")
        print("✅ Copied config_generator.py")
    # Copy certificate generation scripts
    create_certs_src = examples_src_root / "create_certificates_simple.py"
    if create_certs_src.exists():
        shutil.copy2(create_certs_src, output_dir / "scripts/")
        print("✅ Copied create_certificates_simple.py")
    cert_tokens_src = examples_src_root / "generate_certificates_and_tokens.py"
    if cert_tokens_src.exists():
        shutil.copy2(cert_tokens_src, output_dir / "scripts/")
        print("✅ Copied generate_certificates_and_tokens.py")
    print(
        "🎉 Test environment setup completed successfully at: {}".format(
            output_dir
        )
    )


def generate_certificates_with_framework(output_dir: Path) -> bool:
    """
    Generate certificates using mcp_security_framework.
    """
    if not SECURITY_FRAMEWORK_AVAILABLE:
        print(
            "❌ mcp_security_framework not available for certificate "
            "generation"
        )
        return False
    try:
        print(
            "🔐 Generating certificates using mcp_security_framework..."
        )
        # Configure certificate manager
        cert_config = CertificateConfig(
            cert_storage_path=str((output_dir / "certs").resolve()),
            key_storage_path=str((output_dir / "keys").resolve()),
            default_validity_days=365,
            key_size=2048,
            hash_algorithm="sha256",
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
            validity_years=10,  # Use validity_years instead of validity_days
            key_size=2048,
            hash_algorithm="sha256",
        )
        cert_pair = cert_manager.create_root_ca(ca_config)
        if not cert_pair or not cert_pair.certificate_path:
            print(
                "❌ Failed to create CA certificate: Invalid certificate pair"
            )
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
            subject_alt_names=[
                "localhost",
                "127.0.0.1",
            ],
            ca_cert_path=cert_pair.certificate_path,
            ca_key_path=ca_key_path,
        )
        cert_pair = cert_manager.create_server_certificate(server_config)
        if not cert_pair or not cert_pair.certificate_path:
            print(
                "❌ Failed to create server certificate: Invalid certificate "
                "pair"
            )
            return False
        print("✅ Server certificate created successfully")
        # Generate client certificates
        client_configs = [
            (
                "admin",
                ["admin"],
                [
                    "read",
                    "write",
                    "execute",
                    "delete",
                    "admin",
                    "register",
                    "unregister",
                    "heartbeat",
                    "discover",
                ],
            ),
            (
                "user",
                ["user"],
                [
                    "read",
                    "execute",
                    "register",
                    "unregister",
                    "heartbeat",
                    "discover",
                ],
            ),
            ("readonly", ["readonly"], ["read", "discover"]),
            ("guest", ["guest"], ["read", "discover"]),
            (
                "proxy",
                ["proxy"],
                ["register", "unregister", "heartbeat", "discover"],
            ),
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
                print(
                    (
                        "❌ Failed to create client certificate {}: "
                        "Invalid certificate pair"
                    ).format(client_name)
                )
                return False
            print(
                "✅ Client certificate {} created successfully".format(
                    client_name
                )
            )
        print(
            "🎉 All certificates generated successfully using "
            "mcp_security_framework!"
        )
        return True
    except Exception as e:
        print("❌ Error generating certificates with framework: {}".format(e))
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if mcp_security_framework is installed:")
        print("   pip install mcp_security_framework")
        print("\n2. Verify write permissions in output directory")
        print("\n3. Check if certs/ and keys/ directories exist")
        return False


def main() -> int:
    """Main function for command line execution."""
    parser = argparse.ArgumentParser(
        description="Setup test environment for MCP Proxy Adapter"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=".",
        help=(
            "Target directory to create the test environment "
            "(default: current directory)"
        ),
    )
    args = parser.parse_args()
    try:
        target_root = Path(args.output_dir)
        setup_test_environment(target_root)
        # Generate certificates if framework is available
        if SECURITY_FRAMEWORK_AVAILABLE:
            generate_certificates_with_framework(target_root)
        else:
            print(
                "⚠️ Skipping certificate generation (mcp_security_framework "
                "not available)"
            )
    except Exception as e:
        print(
            "❌ Error setting up test environment: {}".format(e),
            file=sys.stderr,
        )
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if output directory is writable")
        print("2. Verify mcp_security_framework installation")
        print("3. Check available disk space")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ TEST ENVIRONMENT SETUP COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Generate test configurations:")
    print("   python -m mcp_proxy_adapter.examples.generate_test_configs --output-dir configs")
    print("\n2. Generate additional certificates (if needed):")
    print("   python -m mcp_proxy_adapter.examples.generate_certificates")
    print("\n3. Run security tests:")
    print("   python -m mcp_proxy_adapter.examples.run_security_tests")
    print("\n4. Start basic framework example:")
    print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/https_simple.json")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
