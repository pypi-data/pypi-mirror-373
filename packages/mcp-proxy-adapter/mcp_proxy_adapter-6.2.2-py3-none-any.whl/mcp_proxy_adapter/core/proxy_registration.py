"""
Module for proxy registration functionality with security framework integration.

This module handles automatic registration and unregistration of the server
with the MCP proxy server during startup and shutdown, using mcp_security_framework
for secure connections and authentication.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import asyncio
import json
import time
import ssl
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urljoin

import aiohttp
import requests
from requests.exceptions import RequestException

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.core.client_security import create_client_security_manager


class ProxyRegistrationError(Exception):
    """Exception raised when proxy registration fails."""
    pass


class ProxyRegistrationManager:
    """
    Manager for proxy registration functionality with security framework integration.
    
    Handles automatic registration and unregistration of the server
    with the MCP proxy server using secure authentication methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the proxy registration manager.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.registration_config = config.get("registration", {})
        
        # Basic registration settings
        self.proxy_url = self.registration_config.get("server_url", "https://proxy-registry.example.com")
        self.server_id = self.registration_config.get("proxy_info", {}).get("name", "mcp_proxy_adapter")
        self.server_name = self.registration_config.get("proxy_info", {}).get("name", "MCP Proxy Adapter")
        self.description = self.registration_config.get("proxy_info", {}).get("description", "JSON-RPC API for interacting with MCP Proxy")
        
        # Heartbeat settings
        heartbeat_config = self.registration_config.get("heartbeat", {})
        self.timeout = heartbeat_config.get("timeout", 30)
        self.retry_attempts = heartbeat_config.get("retry_attempts", 3)
        self.retry_delay = heartbeat_config.get("retry_delay", 60)
        self.heartbeat_interval = heartbeat_config.get("interval", 300)
        
        # Auto registration settings
        self.auto_register = self.registration_config.get("enabled", False)
        self.auto_unregister = True  # Always unregister on shutdown
        
        # Initialize client security manager
        self.client_security = create_client_security_manager(config)
        
        # Registration state
        self.registered = False
        self.server_key: Optional[str] = None
        self.server_url: Optional[str] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        logger.info("Proxy registration manager initialized with security framework integration")
        
    def is_enabled(self) -> bool:
        """
        Check if proxy registration is enabled.
        
        Returns:
            True if registration is enabled, False otherwise.
        """
        return self.registration_config.get("enabled", False)
    
    def set_server_url(self, server_url: str) -> None:
        """
        Set the server URL for registration.
        
        Args:
            server_url: The URL where this server is accessible.
        """
        self.server_url = server_url
        logger.info(f"Proxy registration server URL set to: {server_url}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for registration requests.
        
        Returns:
            Dictionary of authentication headers
        """
        if not self.client_security:
            return {"Content-Type": "application/json"}
        
        auth_method = self.registration_config.get("auth_method", "certificate")
        
        if auth_method == "certificate":
            return self.client_security.get_client_auth_headers("certificate")
        elif auth_method == "token":
            token_config = self.registration_config.get("token", {})
            token = token_config.get("token")
            return self.client_security.get_client_auth_headers("jwt", token=token)
        elif auth_method == "api_key":
            api_key_config = self.registration_config.get("api_key", {})
            api_key = api_key_config.get("key")
            return self.client_security.get_client_auth_headers("api_key", api_key=api_key)
        else:
            return {"Content-Type": "application/json"}
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for secure connections.
        
        Returns:
            SSL context or None if SSL not needed
        """
        if not self.client_security:
            return None
        
        try:
            # Check if SSL is enabled for registration
            cert_config = self.registration_config.get("certificate", {})
            if cert_config.get("enabled", False):
                return self.client_security.create_client_ssl_context()
            
            return None
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            return None
    
    async def register_server(self) -> bool:
        """
        Register the server with the proxy using secure authentication.
        
        Returns:
            True if registration was successful, False otherwise.
        """
        if not self.is_enabled():
            logger.info("Proxy registration is disabled in configuration")
            return False
            
        if not self.server_url:
            logger.error("Server URL not set, cannot register with proxy")
            return False
        
        # Prepare registration data with proxy info
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
            })
        }
        
        logger.info(f"Attempting to register server with proxy at {self.proxy_url}")
        logger.debug(f"Registration data: {registration_data}")
        
        for attempt in range(self.retry_attempts):
            try:
                success, result = await self._make_secure_registration_request(registration_data)
                
                if success:
                    self.registered = True
                    self.server_key = result.get("server_key")
                    logger.info(f"✅ Successfully registered with proxy. Server key: {self.server_key}")
                    
                    # Start heartbeat if enabled
                    if self.registration_config.get("heartbeat", {}).get("enabled", True):
                        await self._start_heartbeat()
                    
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
    
    async def unregister_server(self) -> bool:
        """
        Unregister the server from the proxy.
        
        Returns:
            True if unregistration was successful, False otherwise.
        """
        if not self.is_enabled():
            logger.info("Proxy registration is disabled, skipping unregistration")
            return True
            
        if not self.registered or not self.server_key:
            logger.info("Server not registered with proxy, skipping unregistration")
            return True
        
        # Stop heartbeat
        await self._stop_heartbeat()
        
        # Extract copy_number from server_key (format: server_id_copy_number)
        try:
            copy_number = int(self.server_key.split("_")[-1])
        except (ValueError, IndexError):
            copy_number = 1
        
        unregistration_data = {
            "server_id": self.server_id,
            "copy_number": copy_number
        }
        
        logger.info(f"Attempting to unregister server from proxy at {self.proxy_url}")
        logger.debug(f"Unregistration data: {unregistration_data}")
        
        try:
            success, result = await self._make_secure_unregistration_request(unregistration_data)
            
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
    
    async def _make_secure_registration_request(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Make secure registration request to proxy using security framework.
        
        Args:
            data: Registration data.
            
        Returns:
            Tuple of (success, result).
        """
        url = urljoin(self.proxy_url, "/register")
        
        # Get authentication headers
        headers = self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        # Create SSL context if needed
        ssl_context = self._create_ssl_context()
        
        # Create connector with SSL context
        connector = None
        if ssl_context:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    result = await response.json()
                    
                    # Validate response headers if security framework available
                    if self.client_security:
                        self.client_security.validate_server_response(dict(response.headers))
                    
                    return response.status == 200, result
        finally:
            if connector:
                await connector.close()
    
    async def _make_secure_unregistration_request(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Make secure unregistration request to proxy using security framework.
        
        Args:
            data: Unregistration data.
            
        Returns:
            Tuple of (success, result).
        """
        url = urljoin(self.proxy_url, "/unregister")
        
        # Get authentication headers
        headers = self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        # Create SSL context if needed
        ssl_context = self._create_ssl_context()
        
        # Create connector with SSL context
        connector = None
        if ssl_context:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    result = await response.json()
                    
                    # Validate response headers if security framework available
                    if self.client_security:
                        self.client_security.validate_server_response(dict(response.headers))
                    
                    return response.status == 200, result
        finally:
            if connector:
                await connector.close()
    
    async def _start_heartbeat(self) -> None:
        """Start heartbeat task for keeping registration alive."""
        if self.heartbeat_task and not self.heartbeat_task.done():
            return
        
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Heartbeat task started")
    
    async def _stop_heartbeat(self) -> None:
        """Stop heartbeat task."""
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("Heartbeat task stopped")
    
    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop to keep registration alive."""
        while self.registered:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if not self.registered:
                    break
                
                # Send heartbeat
                success = await self._send_heartbeat()
                if not success:
                    logger.warning("Heartbeat failed, attempting to re-register")
                    await self.register_server()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def _send_heartbeat(self) -> bool:
        """Send heartbeat to proxy server."""
        if not self.server_key:
            return False
        
        heartbeat_data = {
            "server_id": self.server_id,
            "server_key": self.server_key,
            "timestamp": int(time.time())
        }
        
        url = urljoin(self.proxy_url, "/heartbeat")
        
        # Get authentication headers
        headers = self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        # Create SSL context if needed
        ssl_context = self._create_ssl_context()
        
        # Create connector with SSL context
        connector = None
        if ssl_context:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    url,
                    json=heartbeat_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        logger.debug("Heartbeat sent successfully")
                        return True
                    else:
                        logger.warning(f"Heartbeat failed with status: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            return False
        finally:
            if connector:
                await connector.close()
    
    def get_registration_status(self) -> Dict[str, Any]:
        """
        Get current registration status.
        
        Returns:
            Dictionary with registration status information.
        """
        status = {
            "enabled": self.is_enabled(),
            "registered": self.registered,
            "server_key": self.server_key,
            "server_url": self.server_url,
            "proxy_url": self.proxy_url,
            "server_id": self.server_id,
            "heartbeat_active": self.heartbeat_task is not None and not self.heartbeat_task.done()
        }
        
        # Add security information if available
        if self.client_security:
            status["security_enabled"] = True
            status["ssl_enabled"] = self.client_security.is_ssl_enabled()
            status["auth_methods"] = self.client_security.get_supported_auth_methods()
            
            cert_info = self.client_security.get_client_certificate_info()
            if cert_info:
                status["client_certificate"] = cert_info
        else:
            status["security_enabled"] = False
        
        return status


# Global proxy registration manager instance (will be initialized with config)
proxy_registration_manager: Optional[ProxyRegistrationManager] = None


def initialize_proxy_registration(config: Dict[str, Any]) -> None:
    """
    Initialize global proxy registration manager.
    
    Args:
        config: Application configuration
    """
    global proxy_registration_manager
    proxy_registration_manager = ProxyRegistrationManager(config)


async def register_with_proxy(server_url: str) -> bool:
    """
    Register the server with the proxy.
    
    Args:
        server_url: The URL where this server is accessible.
        
    Returns:
        True if registration was successful, False otherwise.
    """
    if not proxy_registration_manager:
        logger.error("Proxy registration manager not initialized")
        return False
    
    proxy_registration_manager.set_server_url(server_url)
    return await proxy_registration_manager.register_server()


async def unregister_from_proxy() -> bool:
    """
    Unregister the server from the proxy.
    
    Returns:
        True if unregistration was successful, False otherwise.
    """
    if not proxy_registration_manager:
        logger.error("Proxy registration manager not initialized")
        return False
    
    return await proxy_registration_manager.unregister_server()


def get_proxy_registration_status() -> Dict[str, Any]:
    """
    Get current proxy registration status.
    
    Returns:
        Dictionary with registration status information.
    """
    if not proxy_registration_manager:
        return {"error": "Proxy registration manager not initialized"}
    
    return proxy_registration_manager.get_registration_status() 