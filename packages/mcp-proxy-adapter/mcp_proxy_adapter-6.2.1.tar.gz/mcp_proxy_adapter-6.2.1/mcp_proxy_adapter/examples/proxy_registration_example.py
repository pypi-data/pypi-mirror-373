"""
Proxy Registration Example
This example demonstrates how to use the MCP Proxy Adapter framework
for proxy registration with different authentication methods.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import aiohttp
from aiohttp import ClientTimeout, TCPConnector
import ssl
from mcp_proxy_adapter.core.logging import logger
class ProxyRegistrationExample:
    """Example client for testing proxy registration functionality."""
    def __init__(self, server_url: str, auth_token: Optional[str] = None):
        """
        Initialize example client.
        Args:
            server_url: Server URL
            auth_token: Authentication token
        """
        self.server_url = server_url
        self.auth_token = auth_token
        self.session: Optional[aiohttp.ClientSession] = None
        # Test data
        self.test_servers = [
            {
                "server_id": "example-server-1",
                "server_url": "http://localhost:8001",
                "server_name": "Example Server 1",
                "description": "Example server for registration testing",
                "version": "1.0.0",
                "capabilities": ["jsonrpc", "rest"],
                "endpoints": {
                    "jsonrpc": "/api/jsonrpc",
                    "rest": "/cmd",
                    "health": "/health"
                },
                "auth_method": "api_key",
                "security_enabled": True
            },
            {
                "server_id": "example-server-2",
                "server_url": "http://localhost:8002",
                "server_name": "Example Server 2",
                "description": "Another example server",
                "version": "1.0.0",
                "capabilities": ["jsonrpc", "rest", "security"],
                "endpoints": {
                    "jsonrpc": "/api/jsonrpc",
                    "rest": "/cmd",
                    "health": "/health"
                },
                "auth_method": "certificate",
                "security_enabled": True
            }
        ]
    async def __aenter__(self):
        """Async context manager entry."""
        # Create SSL context for HTTPS
        ssl_context = None
        if self.server_url.startswith("https"):
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        # Create connector
        connector = TCPConnector(ssl=ssl_context) if ssl_context else None
        # Create session
        timeout = ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.auth_token:
            headers["X-API-Key"] = self.auth_token
        return headers
    async def test_registration(self, server_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test registration with authentication.
        Args:
            server_data: Server registration data
        Returns:
            Test result
        """
        try:
            # Prepare JSON-RPC request
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "proxy_registration",
                "params": {
                    "operation": "register",
                    **server_data
                }
            }
            logger.info(f"Testing registration for server: {server_data['server_id']}")
            logger.debug(f"Request data: {json.dumps(request_data, indent=2)}")
            # Make request
            async with self.session.post(
                f"{self.server_url}/cmd",
                json=request_data,
                headers=self._get_headers()
            ) as response:
                result = await response.json()
                logger.info(f"Response status: {response.status}")
                logger.debug(f"Response: {json.dumps(result, indent=2)}")
                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "result": result,
                    "server_id": server_data["server_id"]
                }
        except Exception as e:
            logger.error(f"Registration test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "server_id": server_data["server_id"]
            }
    async def test_discovery(self) -> Dict[str, Any]:
        """
        Test discovery operation.
        Returns:
            Test result
        """
        try:
            # Prepare JSON-RPC request
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "proxy_registration",
                "params": {
                    "operation": "discover"
                }
            }
            logger.info("Testing discovery operation")
            # Make request
            async with self.session.post(
                f"{self.server_url}/cmd",
                json=request_data,
                headers=self._get_headers()
            ) as response:
                result = await response.json()
                logger.info(f"Response status: {response.status}")
                logger.debug(f"Response: {json.dumps(result, indent=2)}")
                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "result": result
                }
        except Exception as e:
            logger.error(f"Discovery test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    async def test_heartbeat(self, server_key: str) -> Dict[str, Any]:
        """
        Test heartbeat operation.
        Args:
            server_key: Server key for heartbeat
        Returns:
            Test result
        """
        try:
            # Prepare JSON-RPC request
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "proxy_registration",
                "params": {
                    "operation": "heartbeat",
                    "server_key": server_key,
                    "timestamp": 1234567890,
                    "status": "healthy"
                }
            }
            logger.info(f"Testing heartbeat for server: {server_key}")
            # Make request
            async with self.session.post(
                f"{self.server_url}/cmd",
                json=request_data,
                headers=self._get_headers()
            ) as response:
                result = await response.json()
                logger.info(f"Response status: {response.status}")
                logger.debug(f"Response: {json.dumps(result, indent=2)}")
                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "result": result,
                    "server_key": server_key
                }
        except Exception as e:
            logger.error(f"Heartbeat test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "server_key": server_key
            }
async def run_proxy_registration_example():
    """Run proxy registration example."""
    logger.info("🚀 Starting proxy registration example")
    # Test configurations
    test_configs = [
        {
            "name": "Admin Token",
            "server_url": "http://localhost:8002",
            "auth_token": "test-token-123"
        },
        {
            "name": "User Token",
            "server_url": "http://localhost:8002",
            "auth_token": "user-token-456"
        },
        {
            "name": "Readonly Token",
            "server_url": "http://localhost:8002",
            "auth_token": "readonly-token-123"
        }
    ]
    results = []
    for config in test_configs:
        logger.info(f"\n📋 Testing: {config['name']}")
        logger.info(f"Server URL: {config['server_url']}")
        logger.info(f"Auth Token: {config['auth_token']}")
        async with ProxyRegistrationExample(
            config['server_url'],
            config['auth_token']
        ) as client:
            # Test registration
            for server_data in client.test_servers:
                result = await client.test_registration(server_data)
                results.append({
                    "test": f"{config['name']} - Registration",
                    "server_id": server_data["server_id"],
                    **result
                })
                # If registration successful, test heartbeat
                if result["success"] and "result" in result:
                    server_key = result["result"].get("result", {}).get("server_key")
                    if server_key:
                        heartbeat_result = await client.test_heartbeat(server_key)
                        results.append({
                            "test": f"{config['name']} - Heartbeat",
                            "server_key": server_key,
                            **heartbeat_result
                        })
            # Test discovery
            discovery_result = await client.test_discovery()
            results.append({
                "test": f"{config['name']} - Discovery",
                **discovery_result
            })
    # Test without authentication
    logger.info(f"\n📋 Testing: No Authentication")
    async with ProxyRegistrationExample("http://localhost:8002") as client:
        for server_data in client.test_servers:
            result = await client.test_registration(server_data)
            results.append({
                "test": "No Auth - Registration",
                "server_id": server_data["server_id"],
                **result
            })
    # Print results
    logger.info("\n" + "="*80)
    logger.info("📊 EXAMPLE RESULTS")
    logger.info("="*80)
    passed = 0
    failed = 0
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        logger.info(f"{status} {result['test']}")
        if result["success"]:
            passed += 1
        else:
            failed += 1
        if "error" in result:
            logger.error(f"   Error: {result['error']}")
        elif "result" in result:
            result_data = result["result"]
            if "error" in result_data:
                logger.error(f"   API Error: {result_data['error']}")
            elif "result" in result_data:
                api_result = result_data["result"]
                if "server_key" in api_result:
                    logger.info(f"   Server Key: {api_result['server_key']}")
                if "message" in api_result:
                    logger.info(f"   Message: {api_result['message']}")
    logger.info("\n" + "="*80)
    logger.info(f"📈 SUMMARY: {passed} passed, {failed} failed")
    logger.info("="*80)
    return passed, failed
def main():
    """Main function for the example."""
    logger.info("🔧 MCP Proxy Adapter - Proxy Registration Example")
    logger.info("="*60)
    # Check if server is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8002))
    sock.close()
    if result != 0:
        logger.error("❌ Server is not running on localhost:8002")
        logger.info("💡 Please start the server first:")
        logger.info("   cd mcp_proxy_adapter/examples")
        logger.info("   python -m mcp_proxy_adapter.main --config server_configs/config_proxy_registration.json")
        sys.exit(1)
    logger.info("✅ Server is running on localhost:8002")
    logger.info("🚀 Starting proxy registration example...")
    # Run example
    passed, failed = asyncio.run(run_proxy_registration_example())
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
if __name__ == "__main__":
    main()
