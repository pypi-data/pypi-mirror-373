"""
Protocol management command module.

This module provides commands for managing and querying protocol configurations,
including HTTP, HTTPS, and MTLS protocols.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.core.protocol_manager import protocol_manager
from mcp_proxy_adapter.core.logging import logger


@dataclass
class ProtocolInfo:
    """Protocol information data class."""
    name: str
    enabled: bool
    allowed: bool
    port: Optional[int]
    requires_ssl: bool
    ssl_context_available: bool


@dataclass
class ProtocolManagementResult:
    """Result data for protocol management operations."""
    protocols: Dict[str, Dict[str, Any]]
    allowed_protocols: List[str]
    validation_errors: List[str]
    total_protocols: int
    enabled_protocols: int


class ProtocolManagementCommand(Command):
    """
    Command for managing and querying protocol configurations.
    
    This command provides functionality to:
    - Get information about all configured protocols
    - Check protocol validation status
    - Get allowed protocols list
    - Validate protocol configurations
    """
    
    name = "protocol_management"
    descr = "Manage and query protocol configurations (HTTP, HTTPS, MTLS)"
        
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get command schema.
        
        Returns:
            Command schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get_info", "validate_config", "get_allowed", "check_protocol"],
                    "description": "Action to perform"
                },
                "protocol": {
                    "type": "string",
                    "enum": ["http", "https", "mtls"],
                    "description": "Protocol to check (for check_protocol action)"
                }
            },
            "required": ["action"]
        }
        
    async def execute(self, **kwargs) -> SuccessResult | ErrorResult:
        """
        Execute protocol management command.
        
        Args:
            action: Action to perform (get_info, validate_config, get_allowed, check_protocol)
            protocol: Protocol name for check_protocol action
            
        Returns:
            Command execution result
        """
        try:
            action = kwargs.get("action")
            
            if action == "get_info":
                return await self._get_protocol_info()
            elif action == "validate_config":
                return await self._validate_configuration()
            elif action == "get_allowed":
                return await self._get_allowed_protocols()
            elif action == "check_protocol":
                protocol = kwargs.get("protocol")
                if not protocol:
                    return ErrorResult("Protocol parameter required for check_protocol action")
                return await self._check_protocol(protocol)
            else:
                return ErrorResult(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Protocol management command error: {e}")
            return ErrorResult(f"Protocol management error: {str(e)}")
    
    async def _get_protocol_info(self) -> SuccessResult:
        """
        Get information about all protocols.
        
        Returns:
            Success result with protocol information
        """
        try:
            protocol_info = protocol_manager.get_protocol_info()
            allowed_protocols = protocol_manager.get_allowed_protocols()
            validation_errors = protocol_manager.validate_protocol_configuration()
            
            enabled_count = sum(1 for info in protocol_info.values() if info["enabled"])
            
            result_data = ProtocolManagementResult(
                protocols=protocol_info,
                allowed_protocols=allowed_protocols,
                validation_errors=validation_errors,
                total_protocols=len(protocol_info),
                enabled_protocols=enabled_count
            )
            
            return SuccessResult(
                data={
                    "protocol_info": result_data.protocols,
                    "allowed_protocols": result_data.allowed_protocols,
                    "validation_errors": result_data.validation_errors,
                    "total_protocols": result_data.total_protocols,
                    "enabled_protocols": result_data.enabled_protocols,
                    "protocols_enabled": protocol_manager.enabled
                },
                message="Protocol information retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error getting protocol info: {e}")
            return ErrorResult(f"Failed to get protocol info: {str(e)}")
    
    async def _validate_configuration(self) -> SuccessResult:
        """
        Validate protocol configuration.
        
        Returns:
            Success result with validation results
        """
        try:
            validation_errors = protocol_manager.validate_protocol_configuration()
            is_valid = len(validation_errors) == 0
            
            return SuccessResult(
                data={
                    "is_valid": is_valid,
                    "validation_errors": validation_errors,
                    "error_count": len(validation_errors)
                },
                message=f"Configuration validation {'passed' if is_valid else 'failed'}"
            )
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return ErrorResult(f"Failed to validate configuration: {str(e)}")
    
    async def _get_allowed_protocols(self) -> SuccessResult:
        """
        Get list of allowed protocols.
        
        Returns:
            Success result with allowed protocols
        """
        try:
            allowed_protocols = protocol_manager.get_allowed_protocols()
            
            return SuccessResult(
                data={
                    "allowed_protocols": allowed_protocols,
                    "count": len(allowed_protocols)
                },
                message="Allowed protocols retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error getting allowed protocols: {e}")
            return ErrorResult(f"Failed to get allowed protocols: {str(e)}")
    
    async def _check_protocol(self, protocol: str) -> SuccessResult:
        """
        Check specific protocol configuration.
        
        Args:
            protocol: Protocol name to check
            
        Returns:
            Success result with protocol check results
        """
        try:
            protocol_lower = protocol.lower()
            
            if protocol_lower not in ["http", "https", "mtls"]:
                return ErrorResult(f"Unknown protocol: {protocol}")
            
            is_allowed = protocol_manager.is_protocol_allowed(protocol_lower)
            port = protocol_manager.get_protocol_port(protocol_lower)
            config = protocol_manager.get_protocol_config(protocol_lower)
            
            ssl_context_available = None
            if protocol_lower in ["https", "mtls"]:
                ssl_context_available = protocol_manager.get_ssl_context_for_protocol(protocol_lower) is not None
            
            return SuccessResult(
                data={
                    "protocol": protocol_lower,
                    "is_allowed": is_allowed,
                    "port": port,
                    "enabled": config.get("enabled", False),
                    "requires_ssl": protocol_lower in ["https", "mtls"],
                    "ssl_context_available": ssl_context_available,
                    "configuration": config
                },
                message=f"Protocol '{protocol}' check completed"
            )
            
        except Exception as e:
            logger.error(f"Error checking protocol {protocol}: {e}")
            return ErrorResult(f"Failed to check protocol {protocol}: {str(e)}") 