"""
Module with load command implementation.
"""

from typing import Dict, Any, Optional, List

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult
from mcp_proxy_adapter.commands.command_registry import registry


class LoadResult(SuccessResult):
    """
    Result of the load command execution.
    """
    
    def __init__(self, success: bool, commands_loaded: int, loaded_commands: list, source: str, error: Optional[str] = None):
        """
        Initialize load command result.
        
        Args:
            success: Whether loading was successful
            commands_loaded: Number of commands loaded
            loaded_commands: List of loaded command names
            source: Source path or URL
            error: Error message if loading failed
        """
        data = {
            "success": success,
            "commands_loaded": commands_loaded,
            "loaded_commands": loaded_commands,
            "source": source
        }
        if error:
            data["error"] = error
            
        message = f"Loaded {commands_loaded} commands from {source}"
        if error:
            message = f"Failed to load commands from {source}: {error}"
            
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
                        "commands_loaded": {"type": "integer"},
                        "loaded_commands": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "source": {"type": "string"},
                        "error": {"type": "string"}
                    },
                    "required": ["success", "commands_loaded", "loaded_commands", "source"]
                }
            },
            "required": ["data"]
        }


class LoadCommand(Command):
    """
    Command that loads commands from local path or URL.
    
    This command allows dynamic loading of command modules from either local file system
    or remote HTTP/HTTPS URLs. The command automatically detects whether the source
    is a local path or URL and handles the loading accordingly.
    
    For local paths, the command loads Python modules ending with '_command.py'.
    For URLs, the command downloads the Python code and loads it as a temporary module.
    
    The loaded commands are registered in the command registry and become immediately
    available for execution. Only commands that inherit from the base Command class
    and are properly structured will be loaded and registered.
    
    Security considerations:
    - Local paths are validated for existence and proper naming
    - URLs are downloaded with timeout protection
    - Temporary files are automatically cleaned up after loading
    - Only files ending with '_command.py' are accepted
    
    Examples:
    - Load from local file: "./my_command.py"
    - Load from URL: "https://example.com/remote_command.py"
    """
    
    name = "load"
    result_class = LoadResult
    
    async def execute(self, source: str, **kwargs) -> LoadResult:
        """
        Execute load command.
        
        Args:
            source: Source path or URL to load command from
            **kwargs: Additional parameters
            
        Returns:
            LoadResult: Load command result
        """
        # Load command from source
        result = registry.load_command_from_source(source)
        
        return LoadResult(
            success=result.get("success", False),
            commands_loaded=result.get("commands_loaded", 0),
            loaded_commands=result.get("loaded_commands", []),
            source=result.get("source", source),
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
                "source": {
                    "type": "string",
                    "description": "Source path or URL to load command from (must end with '_command.py')",
                    "examples": [
                        "./my_command.py",
                        "https://example.com/remote_command.py"
                    ]
                }
            },
            "required": ["source"]
        }
    
    @classmethod
    def _generate_examples(cls, params: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate custom examples for load command.
        
        Args:
            params: Information about command parameters
            
        Returns:
            List of examples
        """
        examples = [
            {
                "command": cls.name,
                "params": {"source": "./custom_command.py"},
                "description": "Load a command from local file system"
            },
            {
                "command": cls.name,
                "params": {"source": "https://raw.githubusercontent.com/user/repo/main/remote_command.py"},
                "description": "Load a command from GitHub raw content"
            },
            {
                "command": cls.name,
                "params": {"source": "https://example.com/api/commands/test_command.py"},
                "description": "Load a command from remote API endpoint"
            }
        ]
        
        return examples 