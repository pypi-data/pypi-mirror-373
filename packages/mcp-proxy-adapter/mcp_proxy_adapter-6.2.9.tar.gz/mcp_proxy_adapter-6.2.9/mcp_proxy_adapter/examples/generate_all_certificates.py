#!/usr/bin/env python3
"""
Generate All Certificates for Security Testing
This script generates all necessary certificates for comprehensive security testing:
- Root CA certificate and key
- Server certificates for HTTPS and mTLS
- Client certificates for different roles (admin, user, readonly, etc.)
- Test certificates for negative scenarios
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
class CertificateGenerator:
    """Generate all certificates for security testing."""
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.certs_dir = self.project_root / "mcp_proxy_adapter" / "examples" / "certs"
        self.keys_dir = self.project_root / "mcp_proxy_adapter" / "examples" / "keys"
        # Create directories if they don't exist
        self.certs_dir.mkdir(parents=True, exist_ok=True)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        # Certificate configuration
        self.ca_config = {
            "common_name": "MCP Proxy Adapter Test CA",
            "organization": "Test Organization",
            "country": "US",
            "state": "Test State",
            "city": "Test City",
            "validity_years": 10
        }
        self.server_config = {
            "common_name": "mcp-proxy-adapter-test.local",
            "organization": "Test Organization",
            "country": "US",
            "state": "Test State",
            "city": "Test City",
            "validity_years": 2,
            "san": ["localhost", "127.0.0.1", "mcp-proxy-adapter-test.local"]
        }
        # Client certificates configuration
        self.client_certs = {
            "admin": {
                "common_name": "admin-client",
                "organization": "Test Organization",
                "roles": ["admin"],
                "permissions": ["*"]
            },
            "user": {
                "common_name": "user-client",
                "organization": "Test Organization",
                "roles": ["user"],
                "permissions": ["read", "write"]
            },
            "readonly": {
                "common_name": "readonly-client",
                "organization": "Test Organization",
                "roles": ["readonly"],
                "permissions": ["read"]
            },
            "guest": {
                "common_name": "guest-client",
                "organization": "Test Organization",
                "roles": ["guest"],
                "permissions": ["read"]
            },
            "proxy": {
                "common_name": "proxy-client",
                "organization": "Test Organization",
                "roles": ["proxy"],
                "permissions": ["register", "discover"]
            }
        }
        # Negative test certificates
        self.negative_certs = {
            "expired": {
                "common_name": "expired-client",
                "organization": "Test Organization",
                "validity_days": 1  # Will expire quickly
            },
            "wrong_org": {
                "common_name": "wrong-org-client",
                "organization": "Wrong Organization",
                "roles": ["user"]
            },
            "no_roles": {
                "common_name": "no-roles-client",
                "organization": "Test Organization",
                "roles": []
            },
            "invalid_roles": {
                "common_name": "invalid-roles-client",
                "organization": "Test Organization",
                "roles": ["invalid_role"]
            }
        }
    def run_command(self, cmd: List[str], description: str) -> bool:
        """Run a command and handle errors."""
        try:
            print(f"🔧 {description}...")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed:")
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Error: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ {description} failed: {e}")
            return False
    def create_ca_certificate(self) -> bool:
        """Create Root CA certificate and key."""
        ca_cert_path = self.certs_dir / "ca_cert.pem"
        ca_key_path = self.keys_dir / "ca_key.pem"
        if ca_cert_path.exists() and ca_key_path.exists():
            print(f"ℹ️ CA certificate already exists: {ca_cert_path}")
            return True
        cmd = [
            sys.executable, "-m", "mcp_security_framework.cli.cert_cli", "create-ca",
            "-cn", self.ca_config["common_name"],
            "-o", self.ca_config["organization"],
            "-c", self.ca_config["country"],
            "-s", self.ca_config["state"],
            "-l", self.ca_config["city"],
            "-y", str(self.ca_config["validity_years"])
        ]
        success = self.run_command(cmd, "Creating Root CA certificate")
        if success:
            # Move files to correct locations
            default_ca_cert = Path("./certs") / f"{self.ca_config['common_name'].lower().replace(' ', '_')}_ca.crt"
            default_ca_key = Path("./keys") / f"{self.ca_config['common_name'].lower().replace(' ', '_')}_ca.key"
            if default_ca_cert.exists():
                self.run_command(["mv", str(default_ca_cert), str(ca_cert_path)], "Moving CA certificate")
            if default_ca_key.exists():
                self.run_command(["mv", str(default_ca_key), str(ca_key_path)], "Moving CA key")
        return success
    def create_server_certificate(self) -> bool:
        """Create server certificate for HTTPS and mTLS."""
        server_cert_path = self.certs_dir / "server_cert.pem"
        server_key_path = self.certs_dir / "server_key.pem"
        if server_cert_path.exists() and server_key_path.exists():
            print(f"ℹ️ Server certificate already exists: {server_cert_path}")
            return True
        # Create server certificate
        cmd = [
            sys.executable, "-m", "mcp_security_framework.cli.cert_cli", "create-server",
            "-cn", self.server_config["common_name"],
            "-o", self.server_config["organization"],
            "-c", self.server_config["country"],
            "-s", self.server_config["state"],
            "-l", self.server_config["city"],
            "-d", str(self.server_config["validity_years"] * 365)  # Convert years to days
        ]
        # Add SAN if supported
        if self.server_config["san"]:
            for san in self.server_config["san"]:
                cmd.extend(["--san", san])
        success = self.run_command(cmd, "Creating server certificate")
        if success:
            # Move files to correct locations
            default_server_cert = Path("./certs") / f"{self.server_config['common_name'].lower().replace('.', '_')}_server.crt"
            default_server_key = Path("./keys") / f"{self.server_config['common_name'].lower().replace('.', '_')}_server.key"
            if default_server_cert.exists():
                self.run_command(["mv", str(default_server_cert), str(server_cert_path)], "Moving server certificate")
            if default_server_key.exists():
                self.run_command(["mv", str(default_server_key), str(server_key_path)], "Moving server key")
        return success
    def create_client_certificate(self, name: str, config: Dict) -> bool:
        """Create client certificate with specific configuration."""
        cert_path = self.certs_dir / f"{name}_cert.pem"
        key_path = self.certs_dir / f"{name}_key.pem"
        if cert_path.exists() and key_path.exists():
            print(f"ℹ️ Client certificate {name} already exists: {cert_path}")
            return True
        cmd = [
            sys.executable, "-m", "mcp_security_framework.cli.cert_cli", "create-client",
            "-cn", config["common_name"],
            "-o", config["organization"],
            "-c", self.ca_config["country"],
            "-s", self.ca_config["state"],
            "-l", self.ca_config["city"],
            "-d", "730"  # 2 years in days
        ]
        # Add roles if specified
        if "roles" in config and config["roles"]:
            for role in config["roles"]:
                cmd.extend(["--roles", role])
        # Add permissions if specified
        if "permissions" in config and config["permissions"]:
            for permission in config["permissions"]:
                cmd.extend(["--permissions", permission])
        # Add custom validity for negative tests
        if "validity_days" in config:
            cmd[cmd.index("-d") + 1] = str(config["validity_days"])
        success = self.run_command(cmd, f"Creating client certificate: {name}")
        if success:
            # Move files to correct locations
            default_client_cert = Path("./certs") / f"{config['common_name'].lower().replace('-', '_')}_client.crt"
            default_client_key = Path("./keys") / f"{config['common_name'].lower().replace('-', '_')}_client.key"
            if default_client_cert.exists():
                self.run_command(["mv", str(default_client_cert), str(cert_path)], f"Moving {name} certificate")
            if default_client_key.exists():
                self.run_command(["mv", str(default_client_key), str(key_path)], f"Moving {name} key")
        return success
    def create_legacy_certificates(self) -> bool:
        """Create legacy certificate files for compatibility."""
        legacy_files = [
            ("client.crt", "client.key"),
            ("client_admin.crt", "client_admin.key"),
            ("admin.crt", "admin.key"),
            ("user.crt", "user.key"),
            ("readonly.crt", "readonly.key")
        ]
        success = True
        for cert_file, key_file in legacy_files:
            cert_path = self.certs_dir / cert_file
            key_path = self.certs_dir / key_file
            if not cert_path.exists() or not key_path.exists():
                # Copy from existing certificates
                if cert_file == "client.crt" and (self.certs_dir / "user_cert.pem").exists():
                    self.run_command(["cp", str(self.certs_dir / "user_cert.pem"), str(cert_path)], f"Creating {cert_file}")
                    self.run_command(["cp", str(self.certs_dir / "user_key.pem"), str(key_path)], f"Creating {key_file}")
                elif cert_file == "client_admin.crt" and (self.certs_dir / "admin_cert.pem").exists():
                    self.run_command(["cp", str(self.certs_dir / "admin_cert.pem"), str(cert_path)], f"Creating {cert_file}")
                    self.run_command(["cp", str(self.certs_dir / "admin_key.pem"), str(key_path)], f"Creating {key_file}")
                elif cert_file == "admin.crt" and (self.certs_dir / "admin_cert.pem").exists():
                    self.run_command(["cp", str(self.certs_dir / "admin_cert.pem"), str(cert_path)], f"Creating {cert_file}")
                    self.run_command(["cp", str(self.certs_dir / "admin_key.pem"), str(key_path)], f"Creating {key_file}")
                elif cert_file == "user.crt" and (self.certs_dir / "user_cert.pem").exists():
                    self.run_command(["cp", str(self.certs_dir / "user_cert.pem"), str(cert_path)], f"Creating {cert_file}")
                    self.run_command(["cp", str(self.certs_dir / "user_key.pem"), str(key_path)], f"Creating {key_file}")
                elif cert_file == "readonly.crt" and (self.certs_dir / "readonly_cert.pem").exists():
                    self.run_command(["cp", str(self.certs_dir / "readonly_cert.pem"), str(cert_path)], f"Creating {cert_file}")
                    self.run_command(["cp", str(self.certs_dir / "readonly_key.pem"), str(key_path)], f"Creating {key_file}")
        return success
    def create_certificate_config(self) -> bool:
        """Create certificate configuration file."""
        config_path = self.certs_dir / "cert_config.json"
        config = {
            "ca_cert_path": str(self.certs_dir / "ca_cert.pem"),
            "ca_key_path": str(self.keys_dir / "ca_key.pem"),
            "cert_storage_path": str(self.certs_dir),
            "key_storage_path": str(self.keys_dir),
            "default_validity_days": 365,
            "key_size": 2048,
            "hash_algorithm": "sha256"
        }
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Created certificate config: {config_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create certificate config: {e}")
            return False
    def validate_certificates(self) -> bool:
        """Validate all created certificates."""
        print("\n🔍 Validating certificates...")
        cert_files = [
            "ca_cert.pem",
            "server_cert.pem",
            "admin_cert.pem",
            "user_cert.pem",
            "readonly_cert.pem",
            "guest_cert.pem",
            "proxy_cert.pem"
        ]
        success = True
        for cert_file in cert_files:
            cert_path = self.certs_dir / cert_file
            if cert_path.exists():
                try:
                    result = subprocess.run(
                        ["openssl", "x509", "-in", str(cert_path), "-text", "-noout"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"✅ {cert_file}: Valid")
                except subprocess.CalledProcessError:
                    print(f"❌ {cert_file}: Invalid")
                    success = False
            else:
                print(f"⚠️ {cert_file}: Not found")
        return success
    def generate_all(self) -> bool:
        """Generate all certificates."""
        print("🔐 Generating All Certificates for Security Testing")
        print("=" * 60)
        success = True
        # 1. Create CA certificate
        if not self.create_ca_certificate():
            success = False
            print("❌ Cannot continue without CA certificate")
            return False
        # 2. Create server certificate
        if not self.create_server_certificate():
            success = False
        # 3. Create client certificates for different roles
        print("\n👥 Creating client certificates...")
        for name, config in self.client_certs.items():
            if not self.create_client_certificate(name, config):
                success = False
        # 4. Create negative test certificates
        print("\n🚫 Creating negative test certificates...")
        for name, config in self.negative_certs.items():
            if not self.create_client_certificate(name, config):
                success = False
        # 5. Create legacy certificates for compatibility
        print("\n🔄 Creating legacy certificates...")
        if not self.create_legacy_certificates():
            success = False
        # 6. Create certificate configuration
        if not self.create_certificate_config():
            success = False
        # 7. Validate certificates
        if not self.validate_certificates():
            success = False
        # Print summary
        print("\n" + "=" * 60)
        print("📊 CERTIFICATE GENERATION SUMMARY")
        print("=" * 60)
        if success:
            print("✅ All certificates generated successfully!")
            print(f"📁 Certificates directory: {self.certs_dir}")
            print(f"🔑 Keys directory: {self.keys_dir}")
            print("\n📋 Generated certificates:")
            cert_files = list(self.certs_dir.glob("*.pem")) + list(self.certs_dir.glob("*.crt"))
            for cert_file in sorted(cert_files):
                print(f"   - {cert_file.name}")
            key_files = list(self.keys_dir.glob("*.pem")) + list(self.keys_dir.glob("*.key"))
            for key_file in sorted(key_files):
                print(f"   - {key_file.name}")
        else:
            print("❌ Some certificates failed to generate")
            print("Check the error messages above")
        return success
def main():
    """Main function."""
    generator = CertificateGenerator()
    try:
        success = generator.generate_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Certificate generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Certificate generation failed: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()
