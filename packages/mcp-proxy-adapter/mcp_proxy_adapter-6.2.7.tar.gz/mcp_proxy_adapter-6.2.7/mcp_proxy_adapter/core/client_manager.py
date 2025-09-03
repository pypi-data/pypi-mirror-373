"""
Client Manager for MCP Proxy Adapter Framework

This module provides client management functionality for the MCP Proxy Adapter framework.
It handles client creation, connection management, and proxy registration.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .client import UniversalClient, create_client_from_config


class ClientManager:
    """
    Manages client connections and proxy registrations.
    
    This class provides functionality for:
    - Creating and managing client connections
    - Proxy registration
    - Connection pooling
    - Authentication management
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize client manager.
        
        Args:
            config: Client manager configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.clients: Dict[str, UniversalClient] = {}
        self.connection_pool: Dict[str, UniversalClient] = {}
        
        # Client manager settings
        self.max_connections = config.get("max_connections", 10)
        self.connection_timeout = config.get("connection_timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.retry_delay = config.get("retry_delay", 1)
        
        self.logger.info("Client manager initialized")
    
    async def create_client(self, client_id: str, config_file: str) -> UniversalClient:
        """
        Create a new client instance.
        
        Args:
            client_id: Unique identifier for the client
            config_file: Path to client configuration file
            
        Returns:
            UniversalClient instance
        """
        try:
            if client_id in self.clients:
                self.logger.warning(f"Client {client_id} already exists, reusing existing connection")
                return self.clients[client_id]
            
            client = create_client_from_config(config_file)
            self.clients[client_id] = client
            
            self.logger.info(f"Client {client_id} created successfully")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create client {client_id}: {e}")
            raise
    
    async def get_client(self, client_id: str) -> Optional[UniversalClient]:
        """
        Get an existing client instance.
        
        Args:
            client_id: Client identifier
            
        Returns:
            UniversalClient instance or None if not found
        """
        return self.clients.get(client_id)
    
    async def remove_client(self, client_id: str) -> bool:
        """
        Remove a client instance.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if client was removed, False otherwise
        """
        if client_id in self.clients:
            client = self.clients[client_id]
            await client.disconnect()
            del self.clients[client_id]
            self.logger.info(f"Client {client_id} removed")
            return True
        return False
    
    async def test_client_connection(self, client_id: str) -> bool:
        """
        Test connection for a specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if connection is successful, False otherwise
        """
        client = await self.get_client(client_id)
        if not client:
            self.logger.error(f"Client {client_id} not found")
            return False
        
        try:
            return await client.test_connection()
        except Exception as e:
            self.logger.error(f"Connection test failed for client {client_id}: {e}")
            return False
    
    async def register_proxy(self, client_id: str, proxy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register with proxy server using a specific client.
        
        Args:
            client_id: Client identifier
            proxy_config: Proxy registration configuration
            
        Returns:
            Registration result
        """
        client = await self.get_client(client_id)
        if not client:
            return {"error": f"Client {client_id} not found"}
        
        try:
            result = await client.register_proxy(proxy_config)
            self.logger.info(f"Proxy registration completed for client {client_id}")
            return result
        except Exception as e:
            self.logger.error(f"Proxy registration failed for client {client_id}: {e}")
            return {"error": str(e)}
    
    async def execute_command(self, client_id: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a command using a specific client.
        
        Args:
            client_id: Client identifier
            command: Command name
            params: Command parameters
            
        Returns:
            Command result
        """
        client = await self.get_client(client_id)
        if not client:
            return {"error": f"Client {client_id} not found"}
        
        try:
            result = await client.execute_command(command, params or {})
            self.logger.info(f"Command {command} executed for client {client_id}")
            return result
        except Exception as e:
            self.logger.error(f"Command execution failed for client {client_id}: {e}")
            return {"error": str(e)}
    
    async def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """
        Get status information for a specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Client status information
        """
        client = await self.get_client(client_id)
        if not client:
            return {"error": f"Client {client_id} not found"}
        
        try:
            # Test connection
            connection_ok = await client.test_connection()
            
            # Test security features
            security_features = await client.test_security_features()
            
            status = {
                "client_id": client_id,
                "base_url": client.base_url,
                "auth_method": client.auth_method,
                "connection_ok": connection_ok,
                "security_features": security_features,
                "session_active": client.session is not None
            }
            
            return status
        except Exception as e:
            self.logger.error(f"Failed to get status for client {client_id}: {e}")
            return {"error": str(e)}
    
    async def list_clients(self) -> List[str]:
        """
        Get list of all client identifiers.
        
        Returns:
            List of client identifiers
        """
        return list(self.clients.keys())
    
    async def cleanup(self):
        """Clean up all client connections."""
        for client_id in list(self.clients.keys()):
            await self.remove_client(client_id)
        self.logger.info("All client connections cleaned up")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


def create_client_manager(config: Dict[str, Any]) -> ClientManager:
    """
    Create a ClientManager instance.
    
    Args:
        config: Client manager configuration
        
    Returns:
        ClientManager instance
    """
    return ClientManager(config)


# Example usage and testing functions
async def test_client_manager():
    """Test client manager functionality."""
    # Example configuration
    config = {
        "max_connections": 5,
        "connection_timeout": 30,
        "retry_attempts": 3,
        "retry_delay": 1
    }
    
    async with ClientManager(config) as manager:
        # Create a client
        client_id = "test_client"
        config_file = "configs/http_simple.json"
        
        try:
            client = await manager.create_client(client_id, config_file)
            print(f"✅ Client {client_id} created successfully")
            
            # Test connection
            connection_ok = await manager.test_client_connection(client_id)
            print(f"✅ Connection test: {connection_ok}")
            
            # Get status
            status = await manager.get_client_status(client_id)
            print(f"✅ Client status: {json.dumps(status, indent=2)}")
            
            # Execute command
            result = await manager.execute_command(client_id, "help")
            print(f"✅ Command result: {json.dumps(result, indent=2)}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_client_manager())
