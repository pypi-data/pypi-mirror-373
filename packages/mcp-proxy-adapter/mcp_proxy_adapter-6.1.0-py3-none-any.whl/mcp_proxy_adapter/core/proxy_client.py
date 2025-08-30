"""
Proxy Client Module

This module provides a client for registering with MCP proxy servers
using mcp_security_framework for secure authentication and connections.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import asyncio
import json
import time
import ssl
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urljoin, urlparse
from pathlib import Path

import aiohttp
from aiohttp import ClientTimeout, TCPConnector

# Import framework components
try:
    from mcp_security_framework.core.client_security import ClientSecurityManager
    from mcp_security_framework.schemas.config import ClientSecurityConfig
    from mcp_security_framework.schemas.models import AuthResult, ValidationResult
    from mcp_security_framework.utils.crypto_utils import generate_api_key, create_jwt_token
    from mcp_security_framework.utils.cert_utils import validate_certificate_format
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    ClientSecurityManager = None
    ClientSecurityConfig = None
    AuthResult = None
    ValidationResult = None

from mcp_proxy_adapter.core.logging import logger


class ProxyClientError(Exception):
    """Exception raised when proxy client operations fail."""
    pass


class ProxyClient:
    """
    Client for registering with MCP proxy servers.
    
    Provides secure registration, heartbeat, and discovery functionality
    using mcp_security_framework for authentication and SSL/TLS.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize proxy client.
        
        Args:
            config: Client configuration
        """
        self.config = config
        self.registration_config = config.get("registration", {})
        
        # Basic settings
        self.proxy_url = self.registration_config.get("server_url")
        self.server_id = self.registration_config.get("proxy_info", {}).get("name", "mcp_proxy_adapter")
        self.server_name = self.registration_config.get("proxy_info", {}).get("name", "MCP Proxy Adapter")
        self.description = self.registration_config.get("proxy_info", {}).get("description", "")
        
        # Authentication settings
        self.auth_method = self.registration_config.get("auth_method", "none")
        self.auth_config = self._get_auth_config()
        
        # Heartbeat settings
        heartbeat_config = self.registration_config.get("heartbeat", {})
        self.heartbeat_interval = heartbeat_config.get("interval", 300)
        self.heartbeat_timeout = heartbeat_config.get("timeout", 30)
        self.retry_attempts = heartbeat_config.get("retry_attempts", 3)
        self.retry_delay = heartbeat_config.get("retry_delay", 60)
        
        # Auto discovery settings
        discovery_config = self.registration_config.get("auto_discovery", {})
        self.discovery_enabled = discovery_config.get("enabled", False)
        self.discovery_urls = discovery_config.get("discovery_urls", [])
        self.discovery_interval = discovery_config.get("discovery_interval", 3600)
        
        # Initialize security manager
        self.security_manager = self._create_security_manager()
        
        # State
        self.registered = False
        self.server_key: Optional[str] = None
        self.server_url: Optional[str] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.discovery_task: Optional[asyncio.Task] = None
        
        logger.info("Proxy client initialized with security framework integration")
    
    def _get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration based on auth method."""
        if self.auth_method == "certificate":
            return self.registration_config.get("certificate", {})
        elif self.auth_method == "token":
            return self.registration_config.get("token", {})
        elif self.auth_method == "api_key":
            return self.registration_config.get("api_key", {})
        else:
            return {}
    
    def _create_security_manager(self) -> Optional[ClientSecurityManager]:
        """Create client security manager."""
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using basic client")
            return None
        
        try:
            # Create client security configuration
            client_security_config = self.registration_config.get("client_security", {})
            
            if not client_security_config.get("enabled", False):
                logger.info("Client security disabled in configuration")
                return None
            
            # Create security config
            security_config = {
                "security": {
                    "ssl": {
                        "enabled": client_security_config.get("ssl_enabled", False),
                        "client_cert_file": client_security_config.get("certificate_auth", {}).get("cert_file"),
                        "client_key_file": client_security_config.get("certificate_auth", {}).get("key_file"),
                        "ca_cert_file": client_security_config.get("certificate_auth", {}).get("ca_cert_file"),
                        "verify_mode": "CERT_REQUIRED",
                        "min_tls_version": "TLSv1.2",
                        "check_hostname": True,
                        "check_expiry": True
                    },
                    "auth": {
                        "enabled": True,
                        "methods": client_security_config.get("auth_methods", ["api_key"]),
                        "api_keys": {
                            client_security_config.get("api_key_auth", {}).get("key", "default"): {
                                "roles": ["proxy_client"],
                                "permissions": ["register", "heartbeat", "discover"]
                            }
                        }
                    }
                }
            }
            
            return ClientSecurityManager(security_config)
            
        except Exception as e:
            logger.error(f"Failed to create security manager: {e}")
            return None
    
    def set_server_url(self, server_url: str) -> None:
        """
        Set the server URL for registration.
        
        Args:
            server_url: The URL where this server is accessible.
        """
        self.server_url = server_url
        logger.info(f"Proxy client server URL set to: {server_url}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for requests.
        
        Returns:
            Dictionary of authentication headers
        """
        headers = {"Content-Type": "application/json"}
        
        if not self.security_manager:
            return headers
        
        try:
            if self.auth_method == "certificate":
                return self.security_manager.get_client_auth_headers("certificate")
            elif self.auth_method == "token":
                token = self.auth_config.get("token")
                return self.security_manager.get_client_auth_headers("jwt", token=token)
            elif self.auth_method == "api_key":
                api_key = self.auth_config.get("key")
                return self.security_manager.get_client_auth_headers("api_key", api_key=api_key)
            else:
                return headers
        except Exception as e:
            logger.error(f"Failed to get auth headers: {e}")
            return headers
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for secure connections.
        
        Returns:
            SSL context or None if SSL not needed
        """
        if not self.security_manager:
            return None
        
        try:
            return self.security_manager.create_client_ssl_context()
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            return None
    
    async def register(self) -> bool:
        """
        Register with the proxy server.
        
        Returns:
            True if registration was successful, False otherwise.
        """
        if not self.proxy_url:
            logger.error("Proxy URL not configured")
            return False
        
        if not self.server_url:
            logger.error("Server URL not set")
            return False
        
        # Prepare registration data
        proxy_info = self.registration_config.get("proxy_info", {})
        registration_data = {
            "server_id": self.server_id,
            "server_url": self.server_url,
            "server_name": self.server_name,
            "description": self.description,
            "version": proxy_info.get("version", "1.0.0"),
            "capabilities": proxy_info.get("capabilities", ["jsonrpc", "rest"]),
            "endpoints": proxy_info.get("endpoints", {
                "jsonrpc": "/api/jsonrpc",
                "rest": "/cmd",
                "health": "/health"
            }),
            "auth_method": self.auth_method,
            "security_enabled": self.security_manager is not None
        }
        
        logger.info(f"Attempting to register with proxy at {self.proxy_url}")
        logger.debug(f"Registration data: {registration_data}")
        
        for attempt in range(self.retry_attempts):
            try:
                success, result = await self._make_request("/register", registration_data)
                
                if success:
                    self.registered = True
                    self.server_key = result.get("server_key")
                    logger.info(f"✅ Successfully registered with proxy. Server key: {self.server_key}")
                    
                    # Start heartbeat and discovery
                    await self._start_background_tasks()
                    
                    return True
                else:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    logger.warning(f"❌ Registration attempt {attempt + 1} failed: {error_msg}")
                    
                    if attempt < self.retry_attempts - 1:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"❌ Registration attempt {attempt + 1} failed with exception: {e}")
                
                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
        
        logger.error(f"❌ Failed to register with proxy after {self.retry_attempts} attempts")
        return False
    
    async def unregister(self) -> bool:
        """
        Unregister from the proxy server.
        
        Returns:
            True if unregistration was successful, False otherwise.
        """
        if not self.registered or not self.server_key:
            logger.info("Not registered with proxy, skipping unregistration")
            return True
        
        # Stop background tasks
        await self._stop_background_tasks()
        
        # Extract copy_number from server_key
        try:
            copy_number = int(self.server_key.split("_")[-1])
        except (ValueError, IndexError):
            copy_number = 1
        
        unregistration_data = {
            "server_id": self.server_id,
            "copy_number": copy_number
        }
        
        logger.info(f"Attempting to unregister from proxy at {self.proxy_url}")
        
        try:
            success, result = await self._make_request("/unregister", unregistration_data)
            
            if success:
                unregistered = result.get("unregistered", False)
                if unregistered:
                    logger.info("✅ Successfully unregistered from proxy")
                else:
                    logger.warning("⚠️ Server was not found in proxy registry")
                
                self.registered = False
                self.server_key = None
                return True
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                logger.error(f"❌ Failed to unregister from proxy: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Unregistration failed with exception: {e}")
            return False
    
    async def send_heartbeat(self) -> bool:
        """
        Send heartbeat to proxy server.
        
        Returns:
            True if heartbeat was successful, False otherwise.
        """
        if not self.server_key:
            return False
        
        heartbeat_data = {
            "server_id": self.server_id,
            "server_key": self.server_key,
            "timestamp": int(time.time()),
            "status": "healthy"
        }
        
        try:
            success, result = await self._make_request("/heartbeat", heartbeat_data)
            
            if success:
                logger.debug("Heartbeat sent successfully")
                return True
            else:
                logger.warning(f"Heartbeat failed: {result.get('error', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            return False
    
    async def discover_proxies(self) -> List[Dict[str, Any]]:
        """
        Discover available proxy servers.
        
        Returns:
            List of discovered proxy servers.
        """
        if not self.discovery_enabled:
            return []
        
        discovered_proxies = []
        
        for discovery_url in self.discovery_urls:
            try:
                success, result = await self._make_request("/discover", {}, base_url=discovery_url)
                
                if success:
                    proxies = result.get("proxies", [])
                    discovered_proxies.extend(proxies)
                    logger.info(f"Discovered {len(proxies)} proxies from {discovery_url}")
                else:
                    logger.warning(f"Discovery failed for {discovery_url}")
                    
            except Exception as e:
                logger.error(f"Discovery error for {discovery_url}: {e}")
        
        return discovered_proxies
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any], base_url: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Make HTTP request to proxy server.
        
        Args:
            endpoint: API endpoint
            data: Request data
            base_url: Base URL (optional, uses self.proxy_url if not provided)
            
        Returns:
            Tuple of (success, result)
        """
        url = urljoin(base_url or self.proxy_url, endpoint)
        
        # Get authentication headers
        headers = self._get_auth_headers()
        
        # Create SSL context if needed
        ssl_context = self._create_ssl_context()
        
        # Create connector with SSL context
        connector = None
        if ssl_context:
            connector = TCPConnector(ssl=ssl_context)
        
        try:
            timeout = ClientTimeout(total=self.heartbeat_timeout)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=timeout
                ) as response:
                    result = await response.json()
                    
                    # Validate response if security manager available
                    if self.security_manager:
                        self.security_manager.validate_server_response(dict(response.headers))
                    
                    return response.status == 200, result
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return False, {"error": {"message": str(e)}}
        finally:
            if connector:
                await connector.close()
    
    async def _start_background_tasks(self) -> None:
        """Start heartbeat and discovery background tasks."""
        # Start heartbeat
        if self.registration_config.get("heartbeat", {}).get("enabled", True):
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("Heartbeat task started")
        
        # Start discovery
        if self.discovery_enabled:
            self.discovery_task = asyncio.create_task(self._discovery_loop())
            logger.info("Discovery task started")
    
    async def _stop_background_tasks(self) -> None:
        """Stop background tasks."""
        # Stop heartbeat
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("Heartbeat task stopped")
        
        # Stop discovery
        if self.discovery_task and not self.discovery_task.done():
            self.discovery_task.cancel()
            try:
                await self.discovery_task
            except asyncio.CancelledError:
                pass
            logger.info("Discovery task stopped")
    
    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop to keep registration alive."""
        while self.registered:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if not self.registered:
                    break
                
                # Send heartbeat
                success = await self.send_heartbeat()
                if not success:
                    logger.warning("Heartbeat failed, attempting to re-register")
                    await self.register()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def _discovery_loop(self) -> None:
        """Discovery loop to find new proxy servers."""
        while self.registered:
            try:
                await asyncio.sleep(self.discovery_interval)
                
                if not self.registered:
                    break
                
                # Discover proxies
                proxies = await self.discover_proxies()
                if proxies:
                    logger.info(f"Discovered {len(proxies)} proxy servers")
                    
                    # Register with new proxies if configured
                    if self.registration_config.get("auto_discovery", {}).get("register_on_discovery", False):
                        for proxy in proxies:
                            proxy_url = proxy.get("url")
                            if proxy_url and proxy_url != self.proxy_url:
                                logger.info(f"Attempting to register with discovered proxy: {proxy_url}")
                                # Store original URL and try to register with new proxy
                                original_url = self.proxy_url
                                self.proxy_url = proxy_url
                                await self.register()
                                self.proxy_url = original_url
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Discovery error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current client status.
        
        Returns:
            Dictionary with client status information.
        """
        status = {
            "enabled": self.registration_config.get("enabled", False),
            "registered": self.registered,
            "server_key": self.server_key,
            "server_url": self.server_url,
            "proxy_url": self.proxy_url,
            "server_id": self.server_id,
            "auth_method": self.auth_method,
            "heartbeat_active": self.heartbeat_task is not None and not self.heartbeat_task.done(),
            "discovery_active": self.discovery_task is not None and not self.discovery_task.done()
        }
        
        # Add security information
        if self.security_manager:
            status["security_enabled"] = True
            status["ssl_enabled"] = self.security_manager.is_ssl_enabled()
            status["auth_methods"] = self.security_manager.get_supported_auth_methods()
        else:
            status["security_enabled"] = False
        
        return status


# Global proxy client instance
proxy_client: Optional[ProxyClient] = None


def initialize_proxy_client(config: Dict[str, Any]) -> None:
    """
    Initialize global proxy client.
    
    Args:
        config: Application configuration
    """
    global proxy_client
    proxy_client = ProxyClient(config)


async def register_with_proxy(server_url: str) -> bool:
    """
    Register with proxy server.
    
    Args:
        server_url: The URL where this server is accessible.
        
    Returns:
        True if registration was successful, False otherwise.
    """
    if not proxy_client:
        logger.error("Proxy client not initialized")
        return False
    
    proxy_client.set_server_url(server_url)
    return await proxy_client.register()


async def unregister_from_proxy() -> bool:
    """
    Unregister from proxy server.
    
    Returns:
        True if unregistration was successful, False otherwise.
    """
    if not proxy_client:
        logger.error("Proxy client not initialized")
        return False
    
    return await proxy_client.unregister()


def get_proxy_client_status() -> Dict[str, Any]:
    """
    Get proxy client status.
    
    Returns:
        Dictionary with client status information.
    """
    if not proxy_client:
        return {"error": "Proxy client not initialized"}
    
    return proxy_client.get_status()
