#!/usr/bin/env python3
"""
Test Examples Script
This script tests all examples with different configurations.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import json
import os
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Any, List
# Configuration for testing
CONFIGS = {
    "basic_framework": {
        "http_simple": {"port": 8000, "ssl": False, "auth": False},
        "https_simple": {"port": 8443, "ssl": True, "auth": False},
        "http_auth": {"port": 8001, "ssl": False, "auth": True},
        "https_auth": {"port": 8444, "ssl": True, "auth": True},
        "mtls_no_roles": {"port": 9443, "ssl": True, "auth": True, "mtls": True},
        "mtls_with_roles": {"port": 9444, "ssl": True, "auth": True, "mtls": True}
    },
    "full_application": {
        "http_simple": {"port": 9000, "ssl": False, "auth": False},
        "https_simple": {"port": 9445, "ssl": True, "auth": False},
        "http_auth": {"port": 9001, "ssl": False, "auth": True},
        "https_auth": {"port": 9446, "ssl": True, "auth": True},
        "mtls_no_roles": {"port": 9447, "ssl": True, "auth": True, "mtls": True},
        "mtls_with_roles": {"port": 9448, "ssl": True, "auth": True, "mtls": True}
    }
}
API_KEYS = {
    "admin": "admin-secret-key-123",
    "user": "user-secret-key-456"
}
class ExampleTester:
    """Test examples with different configurations."""
    def __init__(self):
        self.examples_dir = Path(__file__).parent
        self.results = {}
        self.processes = []
    def generate_certificates(self):
        """Generate certificates for testing."""
        print("🔐 Generating certificates...")
        cert_script = self.examples_dir.parent / "generate_certificates.py"
        if cert_script.exists():
            result = subprocess.run([sys.executable, str(cert_script)],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Certificates generated successfully")
                return True
            else:
                print(f"❌ Certificate generation failed: {result.stderr}")
                return False
        else:
            print("⚠️ Certificate generation script not found, using existing certificates")
            return True
    def start_server(self, example_type: str, config_name: str) -> subprocess.Popen:
        """Start a server with specific configuration."""
        config_path = self.examples_dir / example_type / "configs" / f"{config_name}.json"
        main_script = self.examples_dir / example_type / "main.py"
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        if not main_script.exists():
            raise FileNotFoundError(f"Main script not found: {main_script}")
        cmd = [
            sys.executable, str(main_script),
            "--config", str(config_path)
        ]
        print(f"🚀 Starting {example_type} server with {config_name} config...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for server to start
        time.sleep(5)
        return process
    def test_health_endpoint(self, port: int, ssl: bool = False, auth: bool = False,
                           api_key: str = None) -> Dict[str, Any]:
        """Test health endpoint."""
        protocol = "https" if ssl else "http"
        url = f"{protocol}://localhost:{port}/health"
        headers = {}
        if auth and api_key:
            headers["X-API-Key"] = api_key
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    def test_echo_command(self, port: int, ssl: bool = False, auth: bool = False,
                         api_key: str = None) -> Dict[str, Any]:
        """Test echo command."""
        protocol = "https" if ssl else "http"
        url = f"{protocol}://localhost:{port}/cmd"
        headers = {"Content-Type": "application/json"}
        if auth and api_key:
            headers["X-API-Key"] = api_key
        data = {
            "jsonrpc": "2.0",
            "method": "echo",
            "params": {"message": "Hello from test!"},
            "id": 1
        }
        try:
            response = requests.post(url, json=data, headers=headers, verify=False, timeout=10)
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    def test_full_application_commands(self, port: int, ssl: bool = False, auth: bool = False,
                                     api_key: str = None) -> Dict[str, Any]:
        """Test full application specific commands."""
        protocol = "https" if ssl else "http"
        url = f"{protocol}://localhost:{port}/cmd"
        headers = {"Content-Type": "application/json"}
        if auth and api_key:
            headers["X-API-Key"] = api_key
        results = {}
        # Test custom echo command
        data = {
            "jsonrpc": "2.0",
            "method": "custom_echo",
            "params": {"message": "Custom echo test", "repeat": 3},
            "id": 1
        }
        try:
            response = requests.post(url, json=data, headers=headers, verify=False, timeout=10)
            results["custom_echo"] = {
                "success": True,
                "status_code": response.status_code,
                "response": response.json()
            }
        except Exception as e:
            results["custom_echo"] = {
                "success": False,
                "error": str(e)
            }
        # Test dynamic calculator command
        data = {
            "jsonrpc": "2.0",
            "method": "dynamic_calculator",
            "params": {"operation": "add", "a": 10, "b": 5},
            "id": 2
        }
        try:
            response = requests.post(url, json=data, headers=headers, verify=False, timeout=10)
            results["dynamic_calculator"] = {
                "success": True,
                "status_code": response.status_code,
                "response": response.json()
            }
        except Exception as e:
            results["dynamic_calculator"] = {
                "success": False,
                "error": str(e)
            }
        return results
    def run_tests(self):
        """Run all tests."""
        print("🧪 Starting Example Tests")
        print("=" * 60)
        # Generate certificates first
        if not self.generate_certificates():
            print("❌ Certificate generation failed, skipping tests")
            return
        for example_type, configs in CONFIGS.items():
            print(f"\n📁 Testing {example_type.upper()}")
            print("-" * 40)
            for config_name, config_info in configs.items():
                print(f"\n🔧 Testing {config_name} configuration...")
                try:
                    # Start server
                    process = self.start_server(example_type, config_name)
                    self.processes.append(process)
                    port = config_info["port"]
                    ssl = config_info.get("ssl", False)
                    auth = config_info.get("auth", False)
                    # Test health endpoint
                    print(f"  📊 Testing health endpoint...")
                    health_result = self.test_health_endpoint(port, ssl, auth)
                    print(f"    Health: {'✅' if health_result['success'] else '❌'}")
                    # Test echo command
                    print(f"  📝 Testing echo command...")
                    if auth:
                        # Test with admin key
                        echo_result = self.test_echo_command(port, ssl, auth, API_KEYS["admin"])
                    else:
                        echo_result = self.test_echo_command(port, ssl, auth)
                    print(f"    Echo: {'✅' if echo_result['success'] else '❌'}")
                    # Test full application specific commands
                    if example_type == "full_application":
                        print(f"  🔧 Testing full application commands...")
                        app_results = self.test_full_application_commands(port, ssl, auth,
                                                                        API_KEYS["admin"] if auth else None)
                        for cmd_name, result in app_results.items():
                            print(f"    {cmd_name}: {'✅' if result['success'] else '❌'}")
                    # Store results
                    self.results[f"{example_type}_{config_name}"] = {
                        "health": health_result,
                        "echo": echo_result,
                        "config_info": config_info
                    }
                    if example_type == "full_application":
                        self.results[f"{example_type}_{config_name}"]["app_commands"] = app_results
                except Exception as e:
                    print(f"  ❌ Error testing {config_name}: {e}")
                    self.results[f"{example_type}_{config_name}"] = {
                        "error": str(e),
                        "config_info": config_info
                    }
                finally:
                    # Stop server
                    if process:
                        process.terminate()
                        process.wait()
                        time.sleep(2)
        self.print_results()
    def print_results(self):
        """Print test results."""
        print("\n📊 Test Results Summary")
        print("=" * 60)
        total_tests = len(self.results)
        successful_tests = 0
        for test_name, result in self.results.items():
            print(f"\n🔍 {test_name}")
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
                continue
            # Check health test
            health_success = result.get("health", {}).get("success", False)
            print(f"  Health: {'✅' if health_success else '❌'}")
            # Check echo test
            echo_success = result.get("echo", {}).get("success", False)
            print(f"  Echo: {'✅' if echo_success else '❌'}")
            # Check app commands for full application
            if "app_commands" in result:
                app_success = all(cmd_result.get("success", False)
                                for cmd_result in result["app_commands"].values())
                print(f"  App Commands: {'✅' if app_success else '❌'}")
            # Overall test success
            test_success = health_success and echo_success
            if test_success:
                successful_tests += 1
        print(f"\n🎯 Overall Results: {successful_tests}/{total_tests} tests passed")
        if successful_tests == total_tests:
            print("🎉 All tests passed!")
        else:
            print("⚠️ Some tests failed. Check the details above.")
    def cleanup(self):
        """Cleanup processes."""
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                process.wait()
def main():
    """Main function."""
    import sys
    tester = ExampleTester()
    try:
        tester.run_tests()
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
    finally:
        tester.cleanup()
if __name__ == "__main__":
    main()
