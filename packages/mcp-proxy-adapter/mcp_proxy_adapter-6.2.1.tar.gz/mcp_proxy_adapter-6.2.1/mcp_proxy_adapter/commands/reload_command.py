"""
Reload command for configuration and command discovery.

This command allows reloading configuration and rediscovering commands
without restarting the server.
"""

from typing import Any, Dict, Optional

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.logging import logger


class ReloadResult:
    """
    Result of reload operation.
    """
    
    def __init__(
        self,
        config_reloaded: bool,
        builtin_commands: int,
        custom_commands: int,
        loaded_commands: int,
        remote_commands: int = 0,
        total_commands: int = 0,
        server_restart_required: bool = True,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Initialize reload result.
        
        Args:
            config_reloaded: Whether configuration was reloaded successfully
            builtin_commands: Number of built-in commands registered
            custom_commands: Number of custom commands registered
            loaded_commands: Number of commands loaded from directory
            total_commands: Total number of commands after reload
            server_restart_required: Whether server restart is required
            success: Whether reload was successful
            error_message: Error message if reload failed
        """
        self.config_reloaded = config_reloaded
        self.builtin_commands = builtin_commands
        self.custom_commands = custom_commands
        self.loaded_commands = loaded_commands
        self.remote_commands = remote_commands
        self.total_commands = total_commands
        self.server_restart_required = server_restart_required
        self.success = success
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dictionary representation of the result.
        """
        return {
            "success": self.success,
            "config_reloaded": self.config_reloaded,
            "builtin_commands": self.builtin_commands,
            "custom_commands": self.custom_commands,
            "loaded_commands": self.loaded_commands,
            "remote_commands": self.remote_commands,
            "total_commands": self.total_commands,
            "server_restart_required": self.server_restart_required,
            "message": "Server restart required to apply configuration changes",
            "error_message": self.error_message
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for the result.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether reload was successful"
                },
                "config_reloaded": {
                    "type": "boolean",
                    "description": "Whether configuration was reloaded successfully"
                },
                "builtin_commands": {
                    "type": "integer",
                    "description": "Number of built-in commands registered"
                },
                "custom_commands": {
                    "type": "integer",
                    "description": "Number of custom commands registered"
                },
                "loaded_commands": {
                    "type": "integer",
                    "description": "Number of commands loaded from directory"
                },
                "remote_commands": {
                    "type": "integer",
                    "description": "Number of commands loaded from remote plugins"
                },
                "total_commands": {
                    "type": "integer",
                    "description": "Total number of commands after reload"
                },
                "server_restart_required": {
                    "type": "boolean",
                    "description": "Whether server restart is required to apply changes"
                },
                "message": {
                    "type": "string",
                    "description": "Information message about the reload operation"
                },
                "error_message": {
                    "type": ["string", "null"],
                    "description": "Error message if reload failed"
                }
            },
            "required": [
                "success", "config_reloaded", "builtin_commands", "custom_commands",
                "loaded_commands", "remote_commands", "total_commands", "server_restart_required"
            ]
        }


class ReloadCommand(Command):
    """
    Command for reloading configuration and rediscovering commands.
    Uses the unified initialization logic.
    """
    
    name = "reload"
    
    async def execute(self, **params) -> ReloadResult:
        """
        Execute reload command.
        
        Args:
            **params: Command parameters (config_path)
            
        Returns:
            ReloadResult with reload information
        """
        try:
            logger.info("🔄 Starting configuration and commands reload...")
            
            # Get config path from parameters
            config_path = params.get("config_path")
            if not config_path:
                logger.warning("No config_path provided, using default configuration")
            
            # Perform reload using unified initialization
            reload_info = registry.reload_system(config_path=config_path)
            
            # Create result
            result = ReloadResult(
                config_reloaded=reload_info.get("config_reloaded", False),
                builtin_commands=reload_info.get("builtin_commands", 0),
                custom_commands=reload_info.get("custom_commands", 0),
                loaded_commands=reload_info.get("loaded_commands", 0),
                remote_commands=reload_info.get("remote_commands", 0),
                total_commands=reload_info.get("total_commands", 0),
                server_restart_required=True,  # Default to True as per tests
                success=True
            )
            
            logger.info(f"✅ Reload completed successfully: {result.to_dict()}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Reload failed: {str(e)}")
            return ReloadResult(
                config_reloaded=False,
                builtin_commands=0,
                custom_commands=0,
                loaded_commands=0,
                remote_commands=0,
                total_commands=0,
                server_restart_required=False,
                success=False,
                error_message=str(e)
            )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "config_path": {
                    "type": "string",
                    "description": "Path to configuration file to reload",
                    "default": None
                }
            },
            "additionalProperties": False
        } 