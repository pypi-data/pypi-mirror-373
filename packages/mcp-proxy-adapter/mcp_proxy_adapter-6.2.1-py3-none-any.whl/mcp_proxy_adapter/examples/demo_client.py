"""
Demo Client Script
This script demonstrates how to use the UniversalClient with different
authentication methods and connection types.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import asyncio
import json
import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from examples.universal_client import UniversalClient, create_client_config
async def demo_from_config_file(config_file: str):
    """
    Demo client using configuration from file.
    Args:
        config_file: Path to configuration file
    """
    print(f"🚀 Demo from config file: {config_file}")
    print("=" * 50)
    try:
        # Load configuration
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"Configuration loaded: {config.get('security', {}).get('auth_method', 'none')} auth")
        # Create and use client
        async with UniversalClient(config) as client:
            # Test connection
            success = await client.test_connection()
            if success:
                print("✅ Connection successful!")
                # Test security features
                security_results = await client.test_security_features()
                print("\nSecurity Features:")
                for feature, status in security_results.items():
                    status_icon = "✅" if status else "❌"
                    print(f"  {status_icon} {feature}: {status}")
                # Make API calls
                await demo_api_calls(client)
            else:
                print("❌ Connection failed")
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in configuration file: {config_file}")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
async def demo_api_calls(client: UniversalClient):
    """Demonstrate various API calls."""
    print("\n📡 API Calls Demo:")
    print("-" * 30)
    # Test health endpoint
    try:
        health = await client.get("/health")
        print(f"Health: {health}")
    except Exception as e:
        print(f"Health check failed: {e}")
    # Test status endpoint
    try:
        status = await client.get("/api/status")
        print(f"Status: {status}")
    except Exception as e:
        print(f"Status check failed: {e}")
    # Test JSON-RPC command
    try:
        command_data = {
            "jsonrpc": "2.0",
            "method": "test_command",
            "params": {
                "message": "Hello from universal client!",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            "id": 1
        }
        result = await client.post("/api/jsonrpc", command_data)
        print(f"Command Result: {result}")
    except Exception as e:
        print(f"Command execution failed: {e}")
    # Test security command if available
    try:
        security_data = {
            "jsonrpc": "2.0",
            "method": "security_command",
            "params": {
                "action": "get_status",
                "include_certificates": True
            },
            "id": 2
        }
        result = await client.post("/api/jsonrpc", security_data)
        print(f"Security Status: {result}")
    except Exception as e:
        print(f"Security command failed: {e}")
async def demo_all_configs():
    """Demo all available client configurations."""
    print("🚀 Demo All Client Configurations")
    print("=" * 50)
    config_dir = Path(__file__).parent / "client_configs"
    if not config_dir.exists():
        print(f"❌ Config directory not found: {config_dir}")
        return
    config_files = list(config_dir.glob("*.json"))
    if not config_files:
        print(f"❌ No configuration files found in {config_dir}")
        return
    print(f"Found {len(config_files)} configuration files:")
    for config_file in config_files:
        print(f"  - {config_file.name}")
    print("\n" + "=" * 50)
    for config_file in config_files:
        await demo_from_config_file(str(config_file))
        print("\n" + "-" * 50)
async def demo_programmatic_config():
    """Demo client with programmatically created configuration."""
    print("🚀 Demo Programmatic Configuration")
    print("=" * 50)
    # Create different configurations programmatically
    configs = [
        {
            "name": "API Key Client",
            "config": create_client_config(
                "http://localhost:8000",
                "api_key",
                api_key="demo_api_key_123"
            )
        },
        {
            "name": "JWT Client",
            "config": create_client_config(
                "http://localhost:8000",
                "jwt",
                username="demo_user",
                password="demo_password",
                secret="demo_jwt_secret"
            )
        },
        {
            "name": "Certificate Client",
            "config": create_client_config(
                "https://localhost:8443",
                "certificate",
                cert_file="./certs/client.crt",
                key_file="./keys/client.key",
                ca_cert_file="./certs/ca.crt"
            )
        },
        {
            "name": "Basic Auth Client",
            "config": create_client_config(
                "http://localhost:8000",
                "basic",
                username="demo_user",
                password="demo_password"
            )
        }
    ]
    for config_info in configs:
        print(f"\n📋 Testing: {config_info['name']}")
        print("-" * 30)
        try:
            async with UniversalClient(config_info["config"]) as client:
                success = await client.test_connection()
                if success:
                    print("✅ Connection successful!")
                    await demo_api_calls(client)
                else:
                    print("❌ Connection failed")
        except Exception as e:
            print(f"❌ Test failed: {e}")
async def interactive_demo():
    """Interactive demo with user input."""
    print("🚀 Interactive Client Demo")
    print("=" * 50)
    print("Available authentication methods:")
    print("1. No authentication")
    print("2. API Key")
    print("3. JWT Token")
    print("4. Certificate")
    print("5. Basic Authentication")
    try:
        choice = input("\nSelect authentication method (1-5): ").strip()
        auth_methods = {
            "1": "none",
            "2": "api_key",
            "3": "jwt",
            "4": "certificate",
            "5": "basic"
        }
        if choice not in auth_methods:
            print("❌ Invalid choice")
            return
        auth_method = auth_methods[choice]
        # Get server URL
        server_url = input("Enter server URL (default: http://localhost:8000): ").strip()
        if not server_url:
            server_url = "http://localhost:8000"
        # Create configuration based on choice
        config_kwargs = {}
        if auth_method == "api_key":
            api_key = input("Enter API key: ").strip()
            if api_key:
                config_kwargs["api_key"] = api_key
        elif auth_method == "jwt":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            secret = input("Enter JWT secret: ").strip()
            if username and password and secret:
                config_kwargs.update({
                    "username": username,
                    "password": password,
                    "secret": secret
                })
        elif auth_method == "certificate":
            cert_file = input("Enter certificate file path: ").strip()
            key_file = input("Enter key file path: ").strip()
            ca_cert_file = input("Enter CA certificate file path: ").strip()
            if cert_file and key_file:
                config_kwargs.update({
                    "cert_file": cert_file,
                    "key_file": key_file,
                    "ca_cert_file": ca_cert_file
                })
        elif auth_method == "basic":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if username and password:
                config_kwargs.update({
                    "username": username,
                    "password": password
                })
        # Create configuration
        config = create_client_config(server_url, auth_method, **config_kwargs)
        print(f"\nConfiguration created for {auth_method} authentication")
        print(f"Server URL: {server_url}")
        # Test connection
        async with UniversalClient(config) as client:
            success = await client.test_connection()
            if success:
                print("✅ Connection successful!")
                await demo_api_calls(client)
            else:
                print("❌ Connection failed")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"❌ Interactive demo failed: {e}")
def main():
    """Main demo function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "config":
            if len(sys.argv) > 2:
                config_file = sys.argv[2]
                asyncio.run(demo_from_config_file(config_file))
            else:
                print("Usage: python demo_client.py config <config_file>")
        elif command == "all":
            asyncio.run(demo_all_configs())
        elif command == "programmatic":
            asyncio.run(demo_programmatic_config())
        elif command == "interactive":
            asyncio.run(interactive_demo())
        else:
            print("Unknown command. Available commands:")
            print("  config <file>     - Demo with config file")
            print("  all               - Demo all config files")
            print("  programmatic      - Demo programmatic configs")
            print("  interactive       - Interactive demo")
    else:
        # Default: demo all configs
        asyncio.run(demo_all_configs())
if __name__ == "__main__":
    main()
