#!/usr/bin/env python3
"""
Security Test Runner for MCP Proxy Adapter
This script runs comprehensive security tests against all server configurations:
- Basic HTTP
- HTTP + Token authentication
- HTTPS
- HTTPS + Token authentication
- mTLS
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
# Import security test client with proper module path
from mcp_proxy_adapter.examples.security_test_client import SecurityTestClient, TestResult
class SecurityTestRunner:
    """Main test runner for security testing."""
    def __init__(self):
        """Initialize test runner."""
        self.servers = {}
        self.test_results = {}
        self.configs = {
            "basic_http": {
                "config": "configs/http_simple.json",
                "port": 8000,
                "url": "http://localhost:8000",
                "auth": "none"
            },
            "http_token": {
                "config": "configs/http_token.json",
                "port": 8001,
                "url": "http://localhost:8001",
                "auth": "api_key"
            },
            "https": {
                "config": "configs/https_simple.json",
                "port": 8002,
                "url": "https://localhost:8002",
                "auth": "none"
            },
            "https_token": {
                "config": "configs/https_token.json",
                "port": 8003,
                "url": "https://localhost:8003",
                "auth": "api_key"
            },
            "mtls": {
                "config": "configs/mtls_no_roles.json",
                "port": 8004,
                "url": "https://localhost:8004",
                "auth": "certificate"
            }
        }
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        # Check if we're in the right directory
        if not Path("configs").exists():
            print("❌ configs directory not found. Please run from the test environment root directory.")
            return False
        # Check if certificates exist
        cert_files = [
            "certs/ca_cert.pem",
            "certs/server_cert.pem",
            "certs/server_key.pem"
        ]
        missing_certs = []
        for cert_file in cert_files:
            if not Path(cert_file).exists():
                missing_certs.append(cert_file)
        if missing_certs:
            print(f"❌ Missing certificates: {missing_certs}")
            print("💡 Run: python generate_certificates.py")
            return False
        print("✅ Prerequisites check passed")
        return True
    def start_server(self, name: str, config_path: str, port: int) -> Optional[subprocess.Popen]:
        """Start a server in background."""
        try:
            print(f"🚀 Starting {name} server on port {port}...")
            # Start server in background
            process = subprocess.Popen([
                sys.executable, "-m", "mcp_proxy_adapter.main",
                "--config", config_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Wait a bit for server to start
            time.sleep(3)
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {name} server started (PID: {process.pid})")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Failed to start {name} server:")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return None
        except Exception as e:
            print(f"❌ Error starting {name} server: {e}")
            return None
    def stop_server(self, name: str, process: subprocess.Popen):
        """Stop a server."""
        try:
            print(f"🛑 Stopping {name} server (PID: {process.pid})...")
            process.terminate()
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                print(f"✅ {name} server stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️ Force killing {name} server")
                process.kill()
                process.wait()
        except Exception as e:
            print(f"❌ Error stopping {name} server: {e}")
    async def test_server(self, name: str, config: Dict[str, Any]) -> List[TestResult]:
        """Test a specific server configuration."""
        print(f"\n🧪 Testing {name} server...")
        print("=" * 50)
        # Create client with appropriate SSL context
        if config["auth"] == "certificate":
            # For mTLS, create client with certificate-based SSL context
            client = SecurityTestClient(config["url"])
            # Override SSL context for mTLS
            client.create_ssl_context = client.create_ssl_context_for_mtls
            async with client as client_session:
                results = await client_session.run_security_tests(
                    config["url"],
                    config["auth"]
                )
        else:
            # For other auth types, use default SSL context
            async with SecurityTestClient(config["url"]) as client:
                results = await client.run_security_tests(
                    config["url"],
                    config["auth"]
                )
        # Print summary for this server
        passed = sum(1 for r in results if r.success)
        total = len(results)
        print(f"\n📊 {name} Results: {passed}/{total} tests passed")
        return results
    async def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run tests against all server configurations."""
        print("🚀 Starting comprehensive security testing")
        print("=" * 60)
        # Start all servers
        for name, config in self.configs.items():
            process = self.start_server(name, config["config"], config["port"])
            if process:
                self.servers[name] = process
            else:
                print(f"⚠️ Skipping tests for {name} due to startup failure")
        # Wait for all servers to be ready
        print("\n⏳ Waiting for servers to be ready...")
        time.sleep(5)
        # Test each server
        all_results = {}
        for name, config in self.configs.items():
            if name in self.servers:
                try:
                    results = await self.test_server(name, config)
                    all_results[name] = results
                except Exception as e:
                    print(f"❌ Error testing {name}: {e}")
                    all_results[name] = []
            else:
                print(f"⚠️ Skipping {name} tests (server not running)")
                all_results[name] = []
        return all_results
    def print_final_summary(self, all_results: Dict[str, List[TestResult]]):
        """Print final test summary."""
        print("\n" + "=" * 80)
        print("📊 FINAL SECURITY TEST SUMMARY")
        print("=" * 80)
        total_tests = 0
        total_passed = 0
        for server_name, results in all_results.items():
            if results:
                passed = sum(1 for r in results if r.success)
                total = len(results)
                total_tests += total
                total_passed += passed
                status = "✅ PASS" if passed == total else "❌ FAIL"
                print(f"{status} {server_name.upper()}: {passed}/{total} tests passed")
                # Show failed tests
                failed_tests = [r for r in results if not r.success]
                for test in failed_tests:
                    print(f"   ❌ {test.test_name}: {test.error_message}")
            else:
                print(f"⚠️ SKIP {server_name.upper()}: No tests run")
        print("\n" + "-" * 80)
        print(f"OVERALL: {total_passed}/{total_tests} tests passed")
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"SUCCESS RATE: {success_rate:.1f}%")
        # Overall status
        if total_passed == total_tests and total_tests > 0:
            print("🎉 ALL TESTS PASSED!")
            print("\n" + "=" * 60)
            print("✅ SECURITY TESTS COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print("\n📋 NEXT STEPS:")
            print("1. Start basic framework example:")
            print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/https_simple.json")
            print("\n2. Start full application example:")
            print("   python -m mcp_proxy_adapter.examples.full_application.main --config configs/mtls_with_roles.json")
            print("\n3. Test with custom configurations:")
            print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/http_simple.json")
            print("=" * 60)
        elif total_passed > 0:
            print("⚠️ SOME TESTS FAILED")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Check if certificates are generated:")
            print("   python -m mcp_proxy_adapter.examples.generate_certificates")
            print("\n2. Verify configuration files exist:")
            print("   python -m mcp_proxy_adapter.examples.generate_test_configs --output-dir configs")
            print("\n3. Check if ports are available (8000-8005, 8443-8445)")
            print("=" * 60)
        else:
            print("❌ ALL TESTS FAILED")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Run setup test environment:")
            print("   python -m mcp_proxy_adapter.examples.setup_test_environment")
            print("\n2. Generate certificates:")
            print("   python -m mcp_proxy_adapter.examples.generate_certificates")
            print("\n3. Generate configurations:")
            print("   python -m mcp_proxy_adapter.examples.generate_test_configs --output-dir configs")
            print("=" * 60)
    def cleanup(self):
        """Cleanup all running servers."""
        print("\n🧹 Cleaning up...")
        for name, process in self.servers.items():
            self.stop_server(name, process)
        self.servers.clear()
    def signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print(f"\n⚠️ Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)
    async def run(self):
        """Main run method."""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False
            # Run all tests
            all_results = await self.run_all_tests()
            # Print summary
            self.print_final_summary(all_results)
            return True
        except Exception as e:
            print(f"❌ Test runner error: {e}")
            return False
        finally:
            # Always cleanup
            self.cleanup()
def main():
    """Main function."""
    import argparse
    parser = argparse.ArgumentParser(description="Security Test Runner for MCP Proxy Adapter")
    parser.add_argument("--config", help="Test specific configuration")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't cleanup servers after tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Determine the correct configs directory
    current_dir = Path.cwd()
    if (current_dir / "configs").exists():
        # We're in the test environment root directory
        configs_dir = current_dir / "configs"
        os.chdir(current_dir)  # Stay in current directory
    elif (Path(__file__).parent.parent / "configs").exists():
        # We're running from package installation, configs is relative to examples
        configs_dir = Path(__file__).parent.parent / "configs"
        os.chdir(Path(__file__).parent.parent)  # Change to parent of examples
    else:
        # Try to find configs relative to examples directory
        examples_dir = Path(__file__).parent
        configs_dir = examples_dir / "configs"
        os.chdir(examples_dir)

    print(f"🔍 Using configs directory: {configs_dir}")
    print(f"🔍 Working directory: {Path.cwd()}")

    # Create and run test runner
    runner = SecurityTestRunner()
    try:
        success = asyncio.run(runner.run())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()
