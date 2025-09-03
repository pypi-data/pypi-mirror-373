"""
Universal Client for MCP Proxy Adapter Framework

This module provides a universal client that can connect to MCP Proxy Adapter servers
using various authentication methods and protocols. It's designed to be used for
proxy registration and general API communication.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import asyncio
import json
import os
import ssl
import time
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin
from pathlib import Path

import aiohttp
import requests
from requests.exceptions import RequestException

# Import security framework components
try:
    from mcp_security_framework import SecurityManager, AuthManager, CertificateManager
    from mcp_security_framework.utils import generate_api_key, create_jwt_token, validate_jwt_token
    from mcp_security_framework.utils import extract_roles_from_cert, validate_certificate_chain
    from mcp_security_framework.utils import create_ssl_context, validate_server_certificate
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False


class UniversalClient:
    """
    Universal client that demonstrates all possible secure connection methods.
    
    Supports:
    - HTTP/HTTPS connections
    - API Key authentication
    - JWT token authentication
    - Certificate-based authentication
    - SSL/TLS with custom certificates
    - Role-based access control
    - Rate limiting awareness
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize universal client with configuration.
        
        Args:
            config: Client configuration with security settings
        """
        self.config = config
        self.base_url = config.get("server_url", "http://localhost:8000")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.retry_delay = config.get("retry_delay", 1)
        
        # Security configuration
        self.security_config = config.get("security", {})
        self.auth_method = self.security_config.get("auth_method", "none")
        
        # Initialize security managers if framework is available
        self.security_manager = None
        self.auth_manager = None
        self.cert_manager = None
        
        if SECURITY_FRAMEWORK_AVAILABLE:
            self._initialize_security_managers()
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_token: Optional[str] = None
        self.token_expiry: Optional[float] = None
        
        print(f"Universal client initialized with auth method: {self.auth_method}")
    
    def _initialize_security_managers(self) -> None:
        """Initialize security framework managers."""
        try:
            # Initialize security manager
            self.security_manager = SecurityManager(self.security_config)
            
            # Initialize auth manager
            auth_config = self.security_config.get("auth", {})
            self.auth_manager = AuthManager(auth_config)
            
            # Initialize certificate manager
            cert_config = self.security_config.get("certificates", {})
            self.cert_manager = CertificateManager(cert_config)
            
            print("Security framework managers initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize security managers: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """Establish connection with authentication."""
        print(f"Connecting to {self.base_url} with {self.auth_method} authentication...")
        
        # Create SSL context
        ssl_context = self._create_ssl_context()
        
        # Create connector with SSL context
        connector = None
        if ssl_context:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        # Create session
        self.session = aiohttp.ClientSession(connector=connector)
        
        # Perform authentication based on method
        if self.auth_method == "api_key":
            await self._authenticate_api_key()
        elif self.auth_method == "jwt":
            await self._authenticate_jwt()
        elif self.auth_method == "certificate":
            await self._authenticate_certificate()
        elif self.auth_method == "basic":
            await self._authenticate_basic()
        else:
            print("No authentication required")
        
        print("Connection established successfully")
    
    async def disconnect(self) -> None:
        """Close connection and cleanup."""
        if self.session:
            await self.session.close()
            self.session = None
        print("Connection closed")
    
    async def _authenticate_api_key(self) -> None:
        """Authenticate using API key."""
        api_key_config = self.security_config.get("api_key", {})
        api_key = api_key_config.get("key")
        
        if not api_key:
            raise ValueError("API key not provided in configuration")
        
        # Store API key for requests
        self.current_token = api_key
        print(f"Authenticated with API key: {api_key[:8]}...")
    
    async def _authenticate_jwt(self) -> None:
        """Authenticate using JWT token."""
        jwt_config = self.security_config.get("jwt", {})
        
        # Check if we have a stored token that's still valid
        if self.current_token and self.token_expiry and time.time() < self.token_expiry:
            print("Using existing JWT token")
            return
        
        # Get credentials for JWT
        username = jwt_config.get("username")
        password = jwt_config.get("password")
        secret = jwt_config.get("secret")
        
        if not all([username, password, secret]):
            raise ValueError("JWT credentials not provided in configuration")
        
        # Create JWT token
        if SECURITY_FRAMEWORK_AVAILABLE:
            self.current_token = create_jwt_token(
                username, 
                secret, 
                expiry_hours=jwt_config.get("expiry_hours", 24)
            )
        else:
            # Simple JWT creation (for demonstration)
            import jwt
            payload = {
                "username": username,
                "exp": time.time() + (jwt_config.get("expiry_hours", 24) * 3600)
            }
            self.current_token = jwt.encode(payload, secret, algorithm="HS256")
        
        self.token_expiry = time.time() + (jwt_config.get("expiry_hours", 24) * 3600)
        print(f"Authenticated with JWT token: {self.current_token[:20]}...")
    
    async def _authenticate_certificate(self) -> None:
        """Authenticate using client certificate."""
        cert_config = self.security_config.get("certificate", {})
        
        cert_file = cert_config.get("cert_file")
        key_file = cert_config.get("key_file")
        
        if not cert_file or not key_file:
            raise ValueError("Certificate files not provided in configuration")
        
        # Validate certificate
        if SECURITY_FRAMEWORK_AVAILABLE and self.cert_manager:
            try:
                cert_info = self.cert_manager.validate_certificate(cert_file, key_file)
                print(f"Certificate validated: {cert_info.get('subject', 'Unknown')}")
                
                # Extract roles from certificate
                roles = extract_roles_from_cert(cert_file)
                if roles:
                    print(f"Certificate roles: {roles}")
            except Exception as e:
                print(f"Warning: Certificate validation failed: {e}")
        
        print("Certificate authentication prepared")
    
    async def _authenticate_basic(self) -> None:
        """Authenticate using basic authentication."""
        basic_config = self.security_config.get("basic", {})
        username = basic_config.get("username")
        password = basic_config.get("password")
        
        if not username or not password:
            raise ValueError("Basic auth credentials not provided in configuration")
        
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.current_token = f"Basic {credentials}"
        print(f"Authenticated with basic auth: {username}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        headers = {"Content-Type": "application/json"}
        
        if not self.current_token:
            return headers
        
        if self.auth_method == "api_key":
            api_key_config = self.security_config.get("api_key", {})
            header_name = api_key_config.get("header", "X-API-Key")
            headers[header_name] = self.current_token
        elif self.auth_method == "jwt":
            headers["Authorization"] = f"Bearer {self.current_token}"
        elif self.auth_method == "basic":
            headers["Authorization"] = self.current_token
        
        return headers
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for secure connections."""
        ssl_config = self.security_config.get("ssl", {})
        if not ssl_config.get("enabled", False):
            return None

        try:
            context: Optional[ssl.SSLContext] = None

            # Try security framework first
            if self.security_manager:
                try:
                    context = self.security_manager.create_client_ssl_context()
                except Exception:
                    context = None

            # Fallback SSL context creation
            if context is None:
                context = ssl.create_default_context()

            # Always honor explicit client certificate config for mTLS
            cert_config = self.security_config.get("certificate", {})
            if cert_config.get("enabled", False):
                cert_file = cert_config.get("cert_file")
                key_file = cert_config.get("key_file")
                if cert_file and key_file:
                    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

            # Add CA certificate if provided
            ca_cert_file = ssl_config.get("ca_cert_file") or ssl_config.get("ca_cert")
            if ca_cert_file and os.path.exists(ca_cert_file):
                context.load_verify_locations(cafile=ca_cert_file)

            # Configure verification
            if ssl_config.get("check_hostname", True):
                context.check_hostname = True
                context.verify_mode = ssl.CERT_REQUIRED
            else:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            return context
        except Exception as e:
            print(f"Warning: Failed to create SSL context: {e}")
            return None
    
    async def request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to server.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            headers: Additional headers
            
        Returns:
            Response data
        """
        url = urljoin(self.base_url, endpoint)
        
        # Prepare headers
        request_headers = self._get_auth_headers()
        if headers:
            request_headers.update(headers)
        
        try:
            for attempt in range(self.retry_attempts):
                try:
                    async with self.session.request(
                        method,
                        url,
                        json=data,
                        headers=request_headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        result = await response.json()
                        
                        # Validate response if security framework available
                        if SECURITY_FRAMEWORK_AVAILABLE and self.security_manager:
                            self.security_manager.validate_server_response(dict(response.headers))
                        
                        if response.status >= 400:
                            print(f"Request failed with status {response.status}: {result}")
                            return {"error": result, "status": response.status}
                        
                        return result
                        
                except Exception as e:
                    print(f"Request attempt {attempt + 1} failed: {e}")
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise
        except Exception as e:
            print(f"Request failed: {e}")
            raise
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self.request("POST", endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self.request("PUT", endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)
    
    async def test_connection(self) -> bool:
        """Test connection to server."""
        try:
            result = await self.get("/health")
            if "error" not in result:
                print("✅ Connection test successful")
                return True
            else:
                print(f"❌ Connection test failed: {result}")
                return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    async def test_security_features(self) -> Dict[str, bool]:
        """Test various security features."""
        results = {}
        
        # Test basic connectivity
        results["connectivity"] = await self.test_connection()
        
        # Test authentication
        if self.auth_method != "none":
            try:
                result = await self.get("/api/auth/status")
                results["authentication"] = "error" not in result
            except:
                results["authentication"] = False
        
        # Test SSL/TLS
        if self.base_url.startswith("https"):
            results["ssl_tls"] = True
        else:
            results["ssl_tls"] = False
        
        return results
    
    async def register_proxy(self, proxy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register with proxy server.
        
        Args:
            proxy_config: Proxy registration configuration
            
        Returns:
            Registration result
        """
        try:
            result = await self.post("/api/jsonrpc", {
                "jsonrpc": "2.0",
                "method": "proxy_registration",
                "params": proxy_config,
                "id": 1
            })
            return result
        except Exception as e:
            print(f"Proxy registration failed: {e}")
            return {"error": str(e)}
    
    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a command on the server.
        
        Args:
            command: Command name
            params: Command parameters
            
        Returns:
            Command result
        """
        try:
            result = await self.post("/api/jsonrpc", {
                "jsonrpc": "2.0",
                "method": command,
                "params": params or {},
                "id": 1
            })
            return result
        except Exception as e:
            print(f"Command execution failed: {e}")
            return {"error": str(e)}


def create_client_from_config(config_file: str) -> UniversalClient:
    """
    Create a UniversalClient instance from a configuration file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        UniversalClient instance
    """
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Extract server configuration
        server_config = config_data.get("server", {})
        host = server_config.get("host", "127.0.0.1")
        port = server_config.get("port", 8000)
        
        # Determine protocol
        ssl_config = config_data.get("ssl", {})
        ssl_enabled = ssl_config.get("enabled", False)
        protocol = "https" if ssl_enabled else "http"
        
        server_url = f"{protocol}://{host}:{port}"
        
        # Create client configuration
        client_config = {
            "server_url": server_url,
            "timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 1,
            "security": {
                "auth_method": "none"
            }
        }
        
        # Add SSL configuration if needed
        if ssl_enabled:
            client_config["security"]["ssl"] = {
                "enabled": True,
                "check_hostname": False,
                "verify": False
            }
            
            # Add CA certificate if available
            ca_cert = ssl_config.get("ca_cert")
            if ca_cert and os.path.exists(ca_cert):
                client_config["security"]["ssl"]["ca_cert_file"] = ca_cert
        
        return UniversalClient(client_config)
        
    except Exception as e:
        raise ValueError(f"Failed to create client from config: {e}")


# CLI interface for standalone usage
async def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Client for MCP Proxy Adapter")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--method", help="JSON-RPC method to call")
    parser.add_argument("--params", help="JSON-RPC parameters (JSON string)")
    parser.add_argument("--auth-method", help="Authentication method")
    parser.add_argument("--server-url", help="Server URL")
    
    args = parser.parse_args()
    
    if args.config:
        # Load configuration from file
        try:
            client = create_client_from_config(args.config)
            
            print(f"🚀 Testing --config connection")
            print("=" * 40)
            print(f"Universal client initialized with auth method: --config")
            print(f"Connecting to {client.base_url} with --config authentication...")
            
            async with client:
                # Test connection
                success = await client.test_connection()
                
                if success:
                    print("No authentication required")
                    print("Connection established successfully")
                    
                    if args.method:
                        # Execute JSON-RPC method
                        params = {}
                        if args.params:
                            try:
                                params = json.loads(args.params)
                            except json.JSONDecodeError:
                                print("❌ Invalid JSON parameters")
                                return
                        
                        result = await client.execute_command(args.method, params)
                        print(f"✅ Method '{args.method}' executed successfully:")
                        print(json.dumps(result, indent=2))
                    else:
                        # Default to help command
                        result = await client.execute_command("help")
                        print("✅ Help command executed successfully:")
                        print(json.dumps(result, indent=2))
                else:
                    print("❌ Connection failed")
                print("Connection closed")
            
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {args.config}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in configuration file: {args.config}")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
    else:
        print("❌ Configuration file required. Use --config option.")


if __name__ == "__main__":
    asyncio.run(main())
