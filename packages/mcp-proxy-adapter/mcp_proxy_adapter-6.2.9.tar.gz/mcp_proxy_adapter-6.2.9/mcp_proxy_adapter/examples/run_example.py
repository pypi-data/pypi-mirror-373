#!/usr/bin/env python3
"""
Example Runner Script
This script provides a simple way to run the examples.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import sys
import subprocess
import argparse
from pathlib import Path
def run_basic_example(config_name: str, port: int = None):
    """Run basic framework example."""
    config_path = Path(__file__).parent / "basic_framework" / "configs" / f"{config_name}.json"
    main_script = Path(__file__).parent / "basic_framework" / "main.py"
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    cmd = [sys.executable, str(main_script), "--config", str(config_path)]
    if port:
        cmd.extend(["--port", str(port)])
    print(f"🚀 Running basic framework example with {config_name} configuration...")
    return subprocess.run(cmd).returncode == 0
def run_full_example(config_name: str, port: int = None):
    """Run full application example."""
    config_path = Path(__file__).parent / "full_application" / "configs" / f"{config_name}.json"
    main_script = Path(__file__).parent / "full_application" / "main.py"
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    cmd = [sys.executable, str(main_script), "--config", str(config_path)]
    if port:
        cmd.extend(["--port", str(port)])
    print(f"🚀 Running full application example with {config_name} configuration...")
    return subprocess.run(cmd).returncode == 0
def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run MCP Proxy Adapter Examples")
    parser.add_argument("example", choices=["basic", "full"], help="Example type")
    parser.add_argument("config", help="Configuration name (e.g., http_simple, https_auth)")
    parser.add_argument("--port", type=int, help="Override port")
    args = parser.parse_args()
    # Available configurations
    configs = [
        "http_simple", "https_simple", "http_auth",
        "https_auth", "mtls_no_roles", "mtls_with_roles"
    ]
    if args.config not in configs:
        print(f"❌ Unknown configuration: {args.config}")
        print(f"Available configurations: {', '.join(configs)}")
        return 1
    # Run the appropriate example
    if args.example == "basic":
        success = run_basic_example(args.config, args.port)
    else:
        success = run_full_example(args.config, args.port)
    return 0 if success else 1
if __name__ == "__main__":
    sys.exit(main())
