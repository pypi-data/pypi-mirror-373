"""
Config command implementation for managing service configuration.
"""

from typing import Dict, Any, Optional

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.config import config as config_instance


class ConfigResult(SuccessResult):
    """
    Config operation result.
    """
    
    def __init__(self, config: Dict[str, Any], operation: str, message: str = None):
        """
        Initialize config result.
        
        Args:
            config: Configuration values
            operation: Operation performed
            message: Optional message
        """
        super().__init__(data={
            "config": config,
            "operation": operation
        }, message=message)


class ConfigCommand(Command):
    """
    Command for managing service configuration.
    """
    name = "config"
    description = "Get or set configuration values"
    result_class = ConfigResult
    
    async def execute(self, operation: str = "get", path: str = None, value: Any = None) -> ConfigResult:
        """
        Execute the command.
        
        Args:
            operation: Operation to perform (get, set)
            path: Configuration path (dot notation)
            value: Value to set (for set operation)
            
        Returns:
            Config operation result
        """
        message = None
        result_config = {}
        
        if operation == "get":
            if path:
                # Get specific config value
                result_config = {path: config_instance.get(path)}
            else:
                # Get all config
                result_config = config_instance.get_all()
            message = f"Configuration retrieved successfully"
            
        elif operation == "set":
            if path and value is not None:
                # Set config value
                config_instance.set(path, value)
                # Save config
                config_instance.save()
                result_config = {path: value}
                message = f"Configuration updated successfully"
            else:
                # Error - missing required parameters
                raise ValueError("Both 'path' and 'value' are required for 'set' operation")
                
        else:
            # Invalid operation
            raise ValueError(f"Invalid operation: {operation}. Valid operations: get, set")
        
        return ConfigResult(
            config=result_config,
            operation=operation,
            message=message
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Returns JSON schema for command parameters validation.
        
        Returns:
            Dictionary with JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string", 
                    "enum": ["get", "set"],
                    "default": "get",
                    "description": "Operation to perform (get or set)"
                },
                "path": {
                    "type": "string",
                    "description": "Configuration path in dot notation (e.g. 'server.host')"
                },
                "value": {
                    "description": "Value to set (required for 'set' operation)"
                }
            },
            "required": ["operation"],
            "additionalProperties": False
        } 