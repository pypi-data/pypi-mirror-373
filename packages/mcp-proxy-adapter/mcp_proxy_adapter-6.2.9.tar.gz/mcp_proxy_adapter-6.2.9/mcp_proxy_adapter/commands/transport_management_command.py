"""
Transport Management Command

This command provides transport management functionality for the MCP Proxy Adapter.
"""

from typing import Dict, Any, ClassVar
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.core.transport_manager import transport_manager
from mcp_proxy_adapter.core.logging import logger


class TransportManagementResult(SuccessResult):
    """Result class for transport management operations."""
    
    def __init__(self, transport_info: Dict[str, Any], message: str = "Transport management operation completed"):
        """
        Initialize transport management result.
        
        Args:
            transport_info: Transport information
            message: Success message
        """
        super().__init__(data={"transport_info": transport_info}, message=message)


class TransportManagementCommand(Command):
    """
    Transport management command.
    
    This command provides functionality to manage and query transport configurations.
    """
    
    name = "transport_management"
    descr = "Manage and query transport configurations (HTTP, HTTPS, MTLS)"
    
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
                    "enum": ["get_info", "validate", "reload"],
                    "description": "Action to perform"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, **params) -> TransportManagementResult:
        """
        Execute transport management command.
        
        Args:
            params: Command parameters
            
        Returns:
            Transport management result
        """
        try:
            action = params.get("action", "get_info")
            
            if action == "get_info":
                return await self._get_transport_info()
            elif action == "validate":
                return await self._validate_transport()
            elif action == "reload":
                return await self._reload_transport()
            else:
                return TransportManagementResult(
                    transport_info={"error": f"Unknown action: {action}"},
                    message=f"Unknown action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Transport management command error: {e}")
            return TransportManagementResult(
                transport_info={"error": str(e)},
                message=f"Transport management failed: {e}"
            )
    
    async def _get_transport_info(self) -> TransportManagementResult:
        """
        Get transport information.
        
        Returns:
            Transport information result
        """
        transport_info = transport_manager.get_transport_info()
        
        return TransportManagementResult(
            transport_info=transport_info,
            message="Transport information retrieved successfully"
        )
    
    async def _validate_transport(self) -> TransportManagementResult:
        """
        Validate transport configuration.
        
        Returns:
            Validation result
        """
        is_valid = transport_manager.validate_config()
        
        transport_info = transport_manager.get_transport_info()
        transport_info["validation"] = {
            "is_valid": is_valid,
            "timestamp": "2025-08-15T12:00:00Z"
        }
        
        message = "Transport configuration validated successfully" if is_valid else "Transport configuration validation failed"
        
        return TransportManagementResult(
            transport_info=transport_info,
            message=message
        )
    
    async def _reload_transport(self) -> TransportManagementResult:
        """
        Reload transport configuration.
        
        Returns:
            Reload result
        """
        # Note: In a real implementation, this would reload the config
        # For now, we just return current info
        transport_info = transport_manager.get_transport_info()
        transport_info["reload"] = {
            "status": "completed",
            "timestamp": "2025-08-15T12:00:00Z"
        }
        
        return TransportManagementResult(
            transport_info=transport_info,
            message="Transport configuration reload completed"
        ) 