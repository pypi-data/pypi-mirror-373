"""
Module with unload command implementation.
"""

from typing import Dict, Any, Optional, List

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult
from mcp_proxy_adapter.commands.command_registry import registry


class UnloadResult(SuccessResult):
    """
    Result of the unload command execution.
    """
    
    def __init__(self, success: bool, command_name: str, message: str, error: Optional[str] = None):
        """
        Initialize unload command result.
        
        Args:
            success: Whether unloading was successful
            command_name: Name of the command that was unloaded
            message: Result message
            error: Error message if unloading failed
        """
        data = {
            "success": success,
            "command_name": command_name
        }
        if error:
            data["error"] = error
            
        super().__init__(data=data, message=message)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result validation.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "command_name": {"type": "string"},
                        "error": {"type": "string"}
                    },
                    "required": ["success", "command_name"]
                }
            },
            "required": ["data"]
        }


class UnloadCommand(Command):
    """
    Command that unloads loaded commands from registry.
    
    This command allows removal of dynamically loaded commands from the command registry.
    Only commands that were loaded via the 'load' command or from the commands directory
    can be unloaded. Built-in commands and custom commands registered with higher priority
    cannot be unloaded using this command.
    
    When a command is unloaded:
    - The command class is removed from the loaded commands registry
    - Any command instances are also removed
    - The command becomes unavailable for execution
    - Built-in and custom commands with the same name remain unaffected
    
    This is useful for:
    - Removing outdated or problematic commands
    - Managing memory usage by unloading unused commands
    - Testing different versions of commands
    - Cleaning up temporary commands loaded for testing
    
    Note: Unloading a command does not affect other commands and does not require
    a system restart. The command can be reloaded later if needed.
    """
    
    name = "unload"
    result_class = UnloadResult
    
    async def execute(self, command_name: str, **kwargs) -> UnloadResult:
        """
        Execute unload command.
        
        Args:
            command_name: Name of the command to unload
            **kwargs: Additional parameters
            
        Returns:
            UnloadResult: Unload command result
        """
        # Unload command from registry
        result = registry.unload_command(command_name)
        
        return UnloadResult(
            success=result.get("success", False),
            command_name=result.get("command_name", command_name),
            message=result.get("message", "Unknown result"),
            error=result.get("error")
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "command_name": {
                    "type": "string",
                    "description": "Name of the command to unload (must be a loaded command)"
                }
            },
            "required": ["command_name"]
        }
    
    @classmethod
    def _generate_examples(cls, params: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate custom examples for unload command.
        
        Args:
            params: Information about command parameters
            
        Returns:
            List of examples
        """
        examples = [
            {
                "command": cls.name,
                "params": {"command_name": "test_command"},
                "description": "Unload a previously loaded test command"
            },
            {
                "command": cls.name,
                "params": {"command_name": "remote_command"},
                "description": "Unload a command that was loaded from URL"
            },
            {
                "command": cls.name,
                "params": {"command_name": "custom_command"},
                "description": "Unload a custom command loaded from local file"
            }
        ]
        
        return examples 