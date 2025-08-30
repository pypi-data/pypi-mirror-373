"""
Module with plugins command implementation.
"""

from typing import Dict, Any, Optional, List

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.config import config as config_instance


class PluginsResult(SuccessResult):
    """
    Result of the plugins command execution.
    """
    
    def __init__(self, success: bool, plugins_server: str, plugins: list, total_plugins: int, error: Optional[str] = None):
        """
        Initialize plugins command result.
        
        Args:
            success: Whether operation was successful
            plugins_server: URL of the plugins server
            plugins: List of available plugins
            total_plugins: Total number of plugins
            error: Error message if operation failed
        """
        data = {
            "success": success,
            "plugins_server": plugins_server,
            "plugins": plugins,
            "total_plugins": total_plugins
        }
        if error:
            data["error"] = error
            
        message = f"Found {total_plugins} plugins from {plugins_server}"
        if error:
            message = f"Failed to load plugins from {plugins_server}: {error}"
            
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
                        "plugins_server": {"type": "string"},
                        "plugins": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "url": {"type": "string"},
                                    "version": {"type": "string"},
                                    "author": {"type": "string"}
                                }
                            }
                        },
                        "total_plugins": {"type": "integer"},
                        "error": {"type": "string"}
                    },
                    "required": ["success", "plugins_server", "plugins", "total_plugins"]
                }
            },
            "required": ["data"]
        }


class PluginsCommand(Command):
    """
    Command that reads and displays available plugins from a plugins server.
    
    This command fetches a JSON file from a configured plugins server URL that contains
    a list of available plugins. Each plugin in the list typically contains metadata
    such as name, description, URL, version, and author information.
    
    The plugins server URL is configured in the system configuration under
    'commands.plugins_server'. The JSON file should contain an array of plugin objects
    with the following structure:
    
    {
        "plugins": [
            {
                "name": "plugin_name",
                "description": "Plugin description",
                "url": "https://server.com/plugin.py",
                "version": "1.0.0",
                "author": "Author Name"
            }
        ]
    }
    
    This command is useful for:
    - Discovering available plugins without manually browsing the server
    - Getting metadata about plugins before loading them
    - Building plugin management interfaces
    - Checking plugin availability and versions
    
    The command will return the list of all available plugins along with their
    metadata, making it easy to choose which plugins to load.
    """
    
    name = "plugins"
    result_class = PluginsResult
    
    async def execute(self, **kwargs) -> PluginsResult:
        """
        Execute plugins command.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            PluginsResult: Plugins command result
        """
        try:
            # Get configuration from the global config instance
            plugins_server_url = config_instance.get("commands.plugins_server")
            
            if not plugins_server_url:
                return PluginsResult(
                    success=False,
                    plugins_server="",
                    plugins=[],
                    total_plugins=0,
                    error="Plugins server URL not configured"
                )
            
            # Import requests if available
            try:
                import requests
            except ImportError:
                return PluginsResult(
                    success=False,
                    plugins_server=plugins_server_url,
                    plugins=[],
                    total_plugins=0,
                    error="requests library not available"
                )
            
            # Fetch plugins list
            response = requests.get(plugins_server_url, timeout=30)
            response.raise_for_status()
            
            # Parse JSON response
            plugins_data = response.json()
            
            # Handle different JSON formats
            if isinstance(plugins_data, list):
                # Direct array format
                plugins_list = plugins_data
            elif "plugins" in plugins_data:
                # Standard plugins format
                plugins_list = plugins_data.get("plugins", [])
            elif "plugin" in plugins_data:
                # Single plugin format (like from plugins.techsup.od.ua/)
                plugins_list = [{
                    "name": plugins_data.get("plugin", "").replace(".py", ""),
                    "description": plugins_data.get("descr", ""),
                    "url": f"{plugins_server_url.rstrip('/')}/{plugins_data.get('plugin', '')}",
                    "version": "1.0.0",
                    "author": "Unknown",
                    "category": plugins_data.get("category", "")
                }]
            else:
                # Unknown format, try to extract any plugin-like data
                plugins_list = []
                for key, value in plugins_data.items():
                    if isinstance(value, dict) and any(k in value for k in ["name", "plugin", "url"]):
                        plugins_list.append(value)
            
            return PluginsResult(
                success=True,
                plugins_server=plugins_server_url,
                plugins=plugins_list,
                total_plugins=len(plugins_list)
            )
            
        except Exception as e:
            return PluginsResult(
                success=False,
                plugins_server=plugins_server_url if 'plugins_server_url' in locals() else "",
                plugins=[],
                total_plugins=0,
                error=str(e)
            )
    
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Get command metadata.
        
        Returns:
            Dict[str, Any]: Command metadata
        """
        return {
            "name": cls.name,
            "summary": "Command that reads and displays available plugins from a plugins server",
            "description": cls.__doc__,
            "parameters": {},
            "examples": cls._generate_examples({}),
            "schema": cls.result_class.get_schema()
        }
    
    @classmethod
    def _generate_examples(cls, params: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate examples for the command.
        
        Args:
            params: Command parameters schema
            
        Returns:
            List[Dict[str, Any]]: List of examples
        """
        examples = [
            {"command": cls.name, "description": "Get list of available plugins from configured server"},
            {"command": cls.name, "description": "Discover plugins without parameters"},
            {"command": cls.name, "description": "Check plugin availability and metadata"}
        ]
        return examples 