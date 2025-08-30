#!/usr/bin/env python3
"""
Simple Certificate Creation Script

This script creates basic certificates for testing using OpenSSL directly.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import os
import subprocess
import sys
from pathlib import Path


class SimpleCertificateCreator:
    """Create certificates using OpenSSL directly."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.certs_dir = self.project_root / "mcp_proxy_adapter" / "examples" / "certs"
        self.keys_dir = self.project_root / "mcp_proxy_adapter" / "examples" / "keys"
        
        # Create directories
        self.certs_dir.mkdir(parents=True, exist_ok=True)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
    
    def run_command(self, cmd: list, description: str) -> bool:
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
        """Create CA certificate using OpenSSL."""
        ca_cert_path = self.certs_dir / "ca_cert.pem"
        ca_key_path = self.keys_dir / "ca_key.pem"
        
        if ca_cert_path.exists() and ca_key_path.exists():
            print(f"ℹ️ CA certificate already exists: {ca_cert_path}")
            return True
        
        # Create CA private key
        key_cmd = [
            "openssl", "genrsa", "-out", str(ca_key_path), "2048"
        ]
        if not self.run_command(key_cmd, "Creating CA private key"):
            return False
        
        # Create CA certificate
        cert_cmd = [
            "openssl", "req", "-new", "-x509", "-days", "3650",
            "-key", str(ca_key_path),
            "-out", str(ca_cert_path),
            "-subj", "/C=US/ST=Test State/L=Test City/O=Test Organization/CN=MCP Proxy Adapter Test CA"
        ]
        return self.run_command(cert_cmd, "Creating CA certificate")
    
    def create_server_certificate(self) -> bool:
        """Create server certificate using OpenSSL."""
        server_cert_path = self.certs_dir / "server_cert.pem"
        server_key_path = self.certs_dir / "server_key.pem"
        
        if server_cert_path.exists() and server_key_path.exists():
            print(f"ℹ️ Server certificate already exists: {server_cert_path}")
            return True
        
        # Create server private key
        key_cmd = [
            "openssl", "genrsa", "-out", str(server_key_path), "2048"
        ]
        if not self.run_command(key_cmd, "Creating server private key"):
            return False
        
        # Create server certificate signing request
        csr_path = self.certs_dir / "server.csr"
        csr_cmd = [
            "openssl", "req", "-new",
            "-key", str(server_key_path),
            "-out", str(csr_path),
            "-subj", "/C=US/ST=Test State/L=Test City/O=Test Organization/CN=localhost"
        ]
        if not self.run_command(csr_cmd, "Creating server CSR"):
            return False
        
        # Create server certificate
        cert_cmd = [
            "openssl", "x509", "-req", "-days", "730",
            "-in", str(csr_path),
            "-CA", str(self.certs_dir / "ca_cert.pem"),
            "-CAkey", str(self.keys_dir / "ca_key.pem"),
            "-CAcreateserial",
            "-out", str(server_cert_path)
        ]
        success = self.run_command(cert_cmd, "Creating server certificate")
        
        # Clean up CSR
        if csr_path.exists():
            csr_path.unlink()
        
        return success
    
    def create_client_certificate(self, name: str, common_name: str) -> bool:
        """Create client certificate using OpenSSL."""
        cert_path = self.certs_dir / f"{name}_cert.pem"
        key_path = self.certs_dir / f"{name}_key.pem"
        
        if cert_path.exists() and key_path.exists():
            print(f"ℹ️ Client certificate {name} already exists: {cert_path}")
            return True
        
        # Create client private key
        key_cmd = [
            "openssl", "genrsa", "-out", str(key_path), "2048"
        ]
        if not self.run_command(key_cmd, f"Creating {name} private key"):
            return False
        
        # Create client certificate signing request
        csr_path = self.certs_dir / f"{name}.csr"
        csr_cmd = [
            "openssl", "req", "-new",
            "-key", str(key_path),
            "-out", str(csr_path),
            "-subj", f"/C=US/ST=Test State/L=Test City/O=Test Organization/CN={common_name}"
        ]
        if not self.run_command(csr_cmd, f"Creating {name} CSR"):
            return False
        
        # Create client certificate
        cert_cmd = [
            "openssl", "x509", "-req", "-days", "730",
            "-in", str(csr_path),
            "-CA", str(self.certs_dir / "ca_cert.pem"),
            "-CAkey", str(self.keys_dir / "ca_key.pem"),
            "-CAcreateserial",
            "-out", str(cert_path)
        ]
        success = self.run_command(cert_cmd, f"Creating {name} certificate")
        
        # Clean up CSR
        if csr_path.exists():
            csr_path.unlink()
        
        return success
    
    def create_legacy_certificates(self) -> bool:
        """Create legacy certificate files for compatibility."""
        legacy_files = [
            ("client.crt", "client.key", "client"),
            ("client_admin.crt", "client_admin.key", "admin"),
            ("admin.crt", "admin.key", "admin"),
            ("user.crt", "user.key", "user"),
            ("readonly.crt", "readonly.key", "readonly")
        ]
        
        success = True
        for cert_file, key_file, source_name in legacy_files:
            cert_path = self.certs_dir / cert_file
            key_path = self.certs_dir / key_file
            
            if not cert_path.exists() or not key_path.exists():
                source_cert = self.certs_dir / f"{source_name}_cert.pem"
                source_key = self.certs_dir / f"{source_name}_key.pem"
                
                if source_cert.exists() and source_key.exists():
                    self.run_command(["cp", str(source_cert), str(cert_path)], f"Creating {cert_file}")
                    self.run_command(["cp", str(source_key), str(key_path)], f"Creating {key_file}")
                else:
                    print(f"⚠️ Source certificate {source_name} not found for {cert_file}")
                    success = False
        
        return success
    
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
    
    def create_all(self) -> bool:
        """Create all certificates."""
        print("🔐 Creating All Certificates for Security Testing")
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
        
        # 3. Create client certificates
        print("\n👥 Creating client certificates...")
        client_certs = [
            ("admin", "admin-client"),
            ("user", "user-client"),
            ("readonly", "readonly-client"),
            ("guest", "guest-client"),
            ("proxy", "proxy-client")
        ]
        
        for name, common_name in client_certs:
            if not self.create_client_certificate(name, common_name):
                success = False
        
        # 4. Create legacy certificates
        print("\n🔄 Creating legacy certificates...")
        if not self.create_legacy_certificates():
            success = False
        
        # 5. Validate certificates
        if not self.validate_certificates():
            success = False
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 CERTIFICATE CREATION SUMMARY")
        print("=" * 60)
        
        if success:
            print("✅ All certificates created successfully!")
            print(f"📁 Certificates directory: {self.certs_dir}")
            print(f"🔑 Keys directory: {self.keys_dir}")
            print("\n📋 Created certificates:")
            
            cert_files = list(self.certs_dir.glob("*.pem")) + list(self.certs_dir.glob("*.crt"))
            for cert_file in sorted(cert_files):
                print(f"   - {cert_file.name}")
            
            key_files = list(self.keys_dir.glob("*.pem")) + list(self.keys_dir.glob("*.key"))
            for key_file in sorted(key_files):
                print(f"   - {key_file.name}")
        else:
            print("❌ Some certificates failed to create")
            print("Check the error messages above")
        
        return success


def main():
    """Main function."""
    creator = SimpleCertificateCreator()
    
    try:
        success = creator.create_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Certificate creation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Certificate creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
