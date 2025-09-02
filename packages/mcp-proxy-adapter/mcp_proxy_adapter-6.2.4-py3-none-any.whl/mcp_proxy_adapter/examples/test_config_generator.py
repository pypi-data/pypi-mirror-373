#!/usr/bin/env python3
"""
Test script for configuration generator utility.
This script tests the configuration generator to ensure it properly generates
configurations with the new protocols section and fixes for ProtocolMiddleware issues.
"""
import sys
import json
from pathlib import Path
# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from mcp_proxy_adapter.utils.config_generator import ConfigGenerator
def test_config_generator():
    """Test the configuration generator with different types."""
    generator = ConfigGenerator()
    # Test configuration types
    config_types = [
        "basic_http",
        "http_token",
        "https",
        "https_token",
        "https_no_protocol_middleware",
        "mtls",
        "mtls_no_protocol_middleware"
    ]
    print("Testing Configuration Generator")
    print("=" * 50)
    for config_type in config_types:
        print(f"\nTesting {config_type} configuration:")
        print("-" * 30)
        try:
            # Generate configuration
            config = generator._get_config_by_type(config_type)
            # Check if protocols section exists
            if "protocols" in config:
                protocols = config["protocols"]
                print(f"✅ Protocols section found:")
                print(f"   - enabled: {protocols.get('enabled', 'NOT SET')}")
                print(f"   - allowed_protocols: {protocols.get('allowed_protocols', 'NOT SET')}")
                print(f"   - default_protocol: {protocols.get('default_protocol', 'NOT SET')}")
            else:
                print("❌ Protocols section missing!")
            # Check SSL configuration
            ssl_enabled = config.get("ssl", {}).get("enabled", False)
            security_ssl_enabled = config.get("security", {}).get("ssl", {}).get("enabled", False)
            print(f"   - legacy ssl.enabled: {ssl_enabled}")
            print(f"   - security.ssl.enabled: {security_ssl_enabled}")
            # Check if configuration is valid for its type
            if config_type == "https_no_protocol_middleware" or config_type == "mtls_no_protocol_middleware":
                if protocols.get("enabled") == False:
                    print("✅ ProtocolMiddleware correctly disabled")
                else:
                    print("❌ ProtocolMiddleware should be disabled but is enabled")
            else:
                if protocols.get("enabled") == True:
                    print("✅ ProtocolMiddleware correctly enabled")
                else:
                    print("❌ ProtocolMiddleware should be enabled but is disabled")
            # Save configuration to file for inspection
            output_file = f"test_config_{config_type}.json"
            with open(output_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"   - Configuration saved to {output_file}")
        except Exception as e:
            print(f"❌ Error generating {config_type} configuration: {e}")
    print("\n" + "=" * 50)
    print("Configuration generator test completed!")
def test_config_with_comments():
    """Test configuration generation with comments."""
    generator = ConfigGenerator()
    print("\nTesting configuration with comments:")
    print("-" * 40)
    try:
        # Generate HTTPS configuration with comments
        commented_config = generator.generate_config_with_comments("https")
        print("✅ HTTPS configuration with comments generated successfully")
        # Save to file
        with open("test_https_with_comments.json", 'w') as f:
            f.write(commented_config)
        print("   - Configuration saved to test_https_with_comments.json")
    except Exception as e:
        print(f"❌ Error generating configuration with comments: {e}")
if __name__ == "__main__":
    test_config_generator()
    test_config_with_comments()
