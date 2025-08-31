"""
Universal client for testing all security features of the MCP Proxy Adapter.

This client provides methods to test:
- API Key authentication
- JWT authentication
- Certificate-based authentication
- mTLS authentication
- Role-based authorization
- Rate limiting
- SSL/TLS connections
"""

import asyncio
import json
import ssl
import tempfile
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import aiohttp
import aiofiles
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from datetime import datetime, timedelta


class SecurityTestClient:
    """
    Universal client for testing all security features.
    
    This client can generate certificates, create authentication tokens,
    and test various security configurations.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the security test client.
        
        Args:
            base_url: Base URL of the MCP Proxy Adapter
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.temp_dir = tempfile.mkdtemp(prefix="security_test_")
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        # Cleanup temp files
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def _get_cert_path(self, filename: str) -> str:
        """Get path for certificate file in temp directory."""
        return os.path.join(self.temp_dir, filename)
    
    async def generate_self_signed_certificate(
        self, 
        common_name: str = "test.example.com",
        country: str = "US",
        state: str = "Test State",
        locality: str = "Test City",
        organization: str = "Test Organization",
        filename_prefix: str = "test"
    ) -> Dict[str, str]:
        """
        Generate a self-signed certificate for testing.
        
        Args:
            common_name: Common name for the certificate
            country: Country code
            state: State or province
            locality: City or locality
            organization: Organization name
            filename_prefix: Prefix for generated files
            
        Returns:
            Dictionary with paths to certificate and key files
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(common_name),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and key
        cert_path = self._get_cert_path(f"{filename_prefix}_cert.pem")
        key_path = self._get_cert_path(f"{filename_prefix}_key.pem")
        
        async with aiofiles.open(cert_path, 'wb') as f:
            await f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        async with aiofiles.open(key_path, 'wb') as f:
            await f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return {
            "cert_file": cert_path,
            "key_file": key_path,
            "common_name": common_name
        }
    
    async def generate_ca_certificate(self) -> Dict[str, str]:
        """
        Generate a CA certificate for mTLS testing.
        
        Returns:
            Dictionary with paths to CA certificate and key files
        """
        return await self.generate_self_signed_certificate(
            common_name="Test CA",
            organization="Test Certificate Authority",
            filename_prefix="ca"
        )
    
    async def generate_client_certificate(
        self, 
        ca_cert_path: str,
        ca_key_path: str,
        common_name: str = "test-client.example.com"
    ) -> Dict[str, str]:
        """
        Generate a client certificate signed by CA.
        
        Args:
            ca_cert_path: Path to CA certificate
            ca_key_path: Path to CA private key
            common_name: Common name for client certificate
            
        Returns:
            Dictionary with paths to client certificate and key files
        """
        # Load CA certificate and key
        async with aiofiles.open(ca_cert_path, 'rb') as f:
            ca_cert_data = await f.read()
        ca_cert = x509.load_pem_x509_certificate(ca_cert_data)
        
        async with aiofiles.open(ca_key_path, 'rb') as f:
            ca_key_data = await f.read()
        ca_key = load_pem_private_key(ca_key_data, password=None)
        
        # Generate client key
        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create client certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Test State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Test City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Client Organization"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        client_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            client_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(common_name),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).sign(ca_key, hashes.SHA256())
        
        # Save client certificate and key
        cert_path = self._get_cert_path("client_cert.pem")
        key_path = self._get_cert_path("client_key.pem")
        
        async with aiofiles.open(cert_path, 'wb') as f:
            await f.write(client_cert.public_bytes(serialization.Encoding.PEM))
            
        async with aiofiles.open(key_path, 'wb') as f:
            await f.write(client_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return {
            "cert_file": cert_path,
            "key_file": key_path,
            "common_name": common_name
        }
    
    async def test_api_key_authentication(
        self, 
        api_key: str,
        endpoint: str = "/api/jsonrpc",
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test API key authentication.
        
        Args:
            api_key: API key to use for authentication
            endpoint: Endpoint to test
            method: HTTP method
            data: Request data
            
        Returns:
            Test result dictionary
        """
        if data is None:
            data = {
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"test": "api_key_auth"},
                "id": "test-1"
            }
        
        headers = {"X-API-Key": api_key}
        
        try:
            async with self.session.request(
                method, 
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=data
            ) as response:
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": await response.text(),
                    "success": response.status == 200
                }
        except Exception as e:
            return {
                "status_code": None,
                "error": str(e),
                "success": False
            }
    
    async def test_jwt_authentication(
        self, 
        jwt_token: str,
        endpoint: str = "/api/jsonrpc",
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test JWT authentication.
        
        Args:
            jwt_token: JWT token to use for authentication
            endpoint: Endpoint to test
            method: HTTP method
            data: Request data
            
        Returns:
            Test result dictionary
        """
        if data is None:
            data = {
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"test": "jwt_auth"},
                "id": "test-2"
            }
        
        headers = {"Authorization": f"Bearer {jwt_token}"}
        
        try:
            async with self.session.request(
                method, 
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=data
            ) as response:
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": await response.text(),
                    "success": response.status == 200
                }
        except Exception as e:
            return {
                "status_code": None,
                "error": str(e),
                "success": False
            }
    
    async def test_certificate_authentication(
        self,
        cert_file: str,
        key_file: str,
        endpoint: str = "/api/jsonrpc",
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test certificate-based authentication.
        
        Args:
            cert_file: Path to client certificate
            key_file: Path to client private key
            endpoint: Endpoint to test
            method: HTTP method
            data: Request data
            
        Returns:
            Test result dictionary
        """
        if data is None:
            data = {
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"test": "cert_auth"},
                "id": "test-3"
            }
        
        # Create SSL context with client certificate
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(cert_file, key_file)
        
        try:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.request(
                    method, 
                    f"{self.base_url}{endpoint}",
                    json=data
                ) as response:
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": await response.text(),
                        "success": response.status == 200
                    }
        except Exception as e:
            return {
                "status_code": None,
                "error": str(e),
                "success": False
            }
    
    async def test_mtls_authentication(
        self,
        client_cert_file: str,
        client_key_file: str,
        ca_cert_file: str,
        endpoint: str = "/api/jsonrpc",
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test mTLS authentication.
        
        Args:
            client_cert_file: Path to client certificate
            client_key_file: Path to client private key
            ca_cert_file: Path to CA certificate
            endpoint: Endpoint to test
            method: HTTP method
            data: Request data
            
        Returns:
            Test result dictionary
        """
        if data is None:
            data = {
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"test": "mtls_auth"},
                "id": "test-4"
            }
        
        # Create SSL context for mTLS
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(client_cert_file, client_key_file)
        ssl_context.load_verify_locations(ca_cert_file)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = False
        
        try:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.request(
                    method, 
                    f"{self.base_url}{endpoint}",
                    json=data
                ) as response:
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": await response.text(),
                        "success": response.status == 200
                    }
        except Exception as e:
            return {
                "status_code": None,
                "error": str(e),
                "success": False
            }
    
    async def test_rate_limiting(
        self,
        auth_method: str = "api_key",
        auth_value: str = "test_key",
        endpoint: str = "/api/jsonrpc",
        requests_count: int = 10,
        delay: float = 0.1
    ) -> Dict[str, Any]:
        """
        Test rate limiting.
        
        Args:
            auth_method: Authentication method ("api_key", "jwt", "cert", "mtls")
            auth_value: Authentication value (key, token, or cert file path)
            endpoint: Endpoint to test
            requests_count: Number of requests to send
            delay: Delay between requests
            
        Returns:
            Test result dictionary
        """
        results = []
        
        for i in range(requests_count):
            data = {
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"test": f"rate_limit_{i}"},
                "id": f"test-rate-{i}"
            }
            
            if auth_method == "api_key":
                result = await self.test_api_key_authentication(auth_value, endpoint, data=data)
            elif auth_method == "jwt":
                result = await self.test_jwt_authentication(auth_value, endpoint, data=data)
            elif auth_method == "cert":
                result = await self.test_certificate_authentication(auth_value, "", endpoint, data=data)
            elif auth_method == "mtls":
                result = await self.test_mtls_authentication(auth_value, "", "", endpoint, data=data)
            else:
                result = {"error": f"Unknown auth method: {auth_method}", "success": False}
            
            results.append(result)
            
            if delay > 0:
                await asyncio.sleep(delay)
        
        # Analyze results
        successful_requests = sum(1 for r in results if r.get("success", False))
        rate_limited_requests = sum(1 for r in results if r.get("status_code") == 429)
        
        return {
            "total_requests": requests_count,
            "successful_requests": successful_requests,
            "rate_limited_requests": rate_limited_requests,
            "results": results,
            "rate_limiting_detected": rate_limited_requests > 0
        }
    
    async def test_role_authorization(
        self,
        auth_method: str = "api_key",
        auth_value: str = "test_key",
        endpoint: str = "/api/jsonrpc",
        method: str = "echo",
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test role-based authorization.
        
        Args:
            auth_method: Authentication method
            auth_value: Authentication value
            endpoint: Endpoint to test
            method: Command method to test
            params: Command parameters
            
        Returns:
            Test result dictionary
        """
        if params is None:
            params = {"test": "role_auth"}
        
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "test-role-1"
        }
        
        if auth_method == "api_key":
            result = await self.test_api_key_authentication(auth_value, endpoint, data=data)
        elif auth_method == "jwt":
            result = await self.test_jwt_authentication(auth_value, endpoint, data=data)
        elif auth_method == "cert":
            result = await self.test_certificate_authentication(auth_value, "", endpoint, data=data)
        elif auth_method == "mtls":
            result = await self.test_mtls_authentication(auth_value, "", "", endpoint, data=data)
        else:
            result = {"error": f"Unknown auth method: {auth_method}", "success": False}
        
        # Check for authorization errors
        if result.get("status_code") == 403:
            result["authorization_denied"] = True
        else:
            result["authorization_denied"] = False
        
        return result
    
    async def run_comprehensive_test(
        self,
        test_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a comprehensive security test based on configuration.
        
        Args:
            test_config: Test configuration dictionary
            
        Returns:
            Comprehensive test results
        """
        results = {
            "test_name": test_config.get("name", "comprehensive_test"),
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {}
        }
        
        # Generate certificates if needed
        if test_config.get("generate_certificates", False):
            ca_cert = await self.generate_ca_certificate()
            server_cert = await self.generate_self_signed_certificate(
                filename_prefix="server"
            )
            client_cert = await self.generate_client_certificate(
                ca_cert["cert_file"],
                ca_cert["key_file"]
            )
            
            results["certificates"] = {
                "ca": ca_cert,
                "server": server_cert,
                "client": client_cert
            }
        
        # Test API Key authentication
        if test_config.get("test_api_key", False):
            api_key = test_config.get("api_key", "test_api_key")
            results["tests"]["api_key"] = await self.test_api_key_authentication(api_key)
        
        # Test JWT authentication
        if test_config.get("test_jwt", False):
            jwt_token = test_config.get("jwt_token", "test_jwt_token")
            results["tests"]["jwt"] = await self.test_jwt_authentication(jwt_token)
        
        # Test certificate authentication
        if test_config.get("test_certificate", False):
            cert_file = test_config.get("cert_file", results.get("certificates", {}).get("client", {}).get("cert_file"))
            key_file = test_config.get("key_file", results.get("certificates", {}).get("client", {}).get("key_file"))
            if cert_file and key_file:
                results["tests"]["certificate"] = await self.test_certificate_authentication(cert_file, key_file)
        
        # Test mTLS authentication
        if test_config.get("test_mtls", False):
            client_cert_file = test_config.get("client_cert_file", results.get("certificates", {}).get("client", {}).get("cert_file"))
            client_key_file = test_config.get("client_key_file", results.get("certificates", {}).get("client", {}).get("key_file"))
            ca_cert_file = test_config.get("ca_cert_file", results.get("certificates", {}).get("ca", {}).get("cert_file"))
            if client_cert_file and client_key_file and ca_cert_file:
                results["tests"]["mtls"] = await self.test_mtls_authentication(
                    client_cert_file, client_key_file, ca_cert_file
                )
        
        # Test rate limiting
        if test_config.get("test_rate_limiting", False):
            auth_method = test_config.get("rate_limit_auth_method", "api_key")
            auth_value = test_config.get("rate_limit_auth_value", "test_key")
            results["tests"]["rate_limiting"] = await self.test_rate_limiting(
                auth_method, auth_value
            )
        
        # Test role authorization
        if test_config.get("test_role_authorization", False):
            auth_method = test_config.get("role_auth_method", "api_key")
            auth_value = test_config.get("role_auth_value", "test_key")
            method = test_config.get("role_test_method", "echo")
            results["tests"]["role_authorization"] = await self.test_role_authorization(
                auth_method, auth_value, method=method
            )
        
        return results
