"""
Module for registering and managing commands.

Example: Registering a command instance (for dependency injection)
---------------------------------------------------------------

.. code-block:: python

    from mcp_proxy_adapter.commands.command_registry import registry
    from my_commands import MyCommand
    
    # Suppose MyCommand requires a service dependency
    service = MyService()
    my_command_instance = MyCommand(service=service)
    registry.register(my_command_instance)

    # Now, when the command is executed, the same instance (with dependencies) will be used
"""

import importlib
import importlib.util
import inspect
import os
import pkgutil
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.hooks import hooks
from mcp_proxy_adapter.commands.catalog_manager import CatalogManager
from mcp_proxy_adapter.config import config
from mcp_proxy_adapter.core.errors import NotFoundError
from mcp_proxy_adapter.core.logging import logger

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available, HTTP/HTTPS loading will not work")

T = TypeVar("T", bound=Command)


class CommandRegistry:
    """
    Registry for registering and finding commands.
    """
    
    def __init__(self):
        """
        Initialize command registry.
        """
        self._builtin_commands: Dict[str, Type[Command]] = {}  # Built-in framework commands
        self._custom_commands: Dict[str, Type[Command]] = {}   # Custom commands (highest priority)
        self._loaded_commands: Dict[str, Type[Command]] = {}   # Commands loaded from directory
        self._instances: Dict[str, Command] = {}  # Command instances
    
    def register_builtin(self, command: Union[Type[Command], Command]) -> None:
        """
        Register a built-in framework command.

        Args:
            command: Command class or instance to register.

        Raises:
            ValueError: If command with the same name is already registered.
        """
        command_name = self._get_command_name(command)
        
        # Check for conflicts with other built-in commands
        if command_name in self._builtin_commands:
            logger.error(f"Built-in command '{command_name}' is already registered, skipping")
            raise ValueError(f"Built-in command '{command_name}' is already registered")
        
        # Built-in commands can override loaded commands
        # Remove any existing loaded commands with the same name
        if command_name in self._loaded_commands:
            logger.info(f"Built-in command '{command_name}' overrides loaded command")
            del self._loaded_commands[command_name]
        
        self._register_command(command, self._builtin_commands, "built-in")
    
    def register_custom(self, command: Union[Type[Command], Command]) -> None:
        """
        Register a custom command with highest priority.

        Args:
            command: Command class or instance to register.

        Raises:
            ValueError: If command with the same name is already registered.
        """
        command_name = self._get_command_name(command)
        
        # Check for conflicts with other custom commands
        if command_name in self._custom_commands:
            logger.error(f"Custom command '{command_name}' is already registered, skipping")
            raise ValueError(f"Custom command '{command_name}' is already registered")
        
        # Custom commands can override built-in and loaded commands
        # Remove any existing commands with the same name from other types
        if command_name in self._builtin_commands:
            logger.info(f"Custom command '{command_name}' overrides built-in command")
            del self._builtin_commands[command_name]
        
        if command_name in self._loaded_commands:
            logger.info(f"Custom command '{command_name}' overrides loaded command")
            del self._loaded_commands[command_name]
        
        self._register_command(command, self._custom_commands, "custom")
    
    def register_loaded(self, command: Union[Type[Command], Command]) -> None:
        """
        Register a command loaded from directory.

        Args:
            command: Command class or instance to register.

        Returns:
            bool: True if registered, False if skipped due to conflict.
        """
        command_name = self._get_command_name(command)
        
        # Check for conflicts with custom and built-in commands
        if command_name in self._custom_commands:
            logger.warning(f"Loaded command '{command_name}' conflicts with custom command, skipping")
            return False
        
        if command_name in self._builtin_commands:
            logger.warning(f"Loaded command '{command_name}' conflicts with built-in command, skipping")
            return False
        
        # Check for conflicts within loaded commands
        if command_name in self._loaded_commands:
            logger.warning(f"Loaded command '{command_name}' already exists, skipping duplicate")
            return False
        
        try:
            self._register_command(command, self._loaded_commands, "loaded")
            return True
        except ValueError:
            return False
    
    def _register_command(self, command: Union[Type[Command], Command], 
                         target_dict: Dict[str, Type[Command]], 
                         command_type: str) -> None:
        """
        Internal method to register a command in the specified dictionary.

        Args:
            command: Command class or instance to register.
            target_dict: Dictionary to register the command in.
            command_type: Type of command for logging.

        Raises:
            ValueError: If command with the same name is already registered.
        """
        # Determine if this is a class or an instance
        if isinstance(command, type) and issubclass(command, Command):
            command_class = command
            command_instance = None
        elif isinstance(command, Command):
            command_class = command.__class__
            command_instance = command
        else:
            raise ValueError(f"Invalid command type: {type(command)}. Expected Command class or instance.")
            
        command_name = self._get_command_name(command_class)
            
        if command_name in target_dict:
            raise ValueError(f"{command_type.capitalize()} command '{command_name}' is already registered")
            
        logger.debug(f"Registering {command_type} command: {command_name}")
        target_dict[command_name] = command_class
        
        # Store instance if provided
        if command_instance:
            logger.debug(f"Storing {command_type} instance for command: {command_name}")
            self._instances[command_name] = command_instance
    
    def _get_command_name(self, command_class: Type[Command]) -> str:
        """
        Get command name from command class.

        Args:
            command_class: Command class.

        Returns:
            Command name.
        """
        if not hasattr(command_class, "name") or not command_class.name:
            # Use class name if name attribute is not set
            command_name = command_class.__name__.lower()
            if command_name.endswith("command"):
                command_name = command_name[:-7]  # Remove "command" suffix
        else:
            command_name = command_class.name
        
        return command_name
    

    

    
    def load_command_from_source(self, source: str) -> Dict[str, Any]:
        """
        Universal command loader - handles local files, URLs, and remote registry.
        
        Args:
            source: Source string - local path, URL, or command name from registry
            
        Returns:
            Dictionary with loading result information
        """
        logger.info(f"Loading command from source: {source}")
        
        # Parse source to determine type
        parsed_url = urllib.parse.urlparse(source)
        is_url = parsed_url.scheme in ('http', 'https')
        
        if is_url:
            # URL - always download and load
            return self._load_command_from_url(source)
        else:
            # Local path or command name - check remote registry first
            return self._load_command_with_registry_check(source)
    
    def _load_command_with_registry_check(self, source: str) -> Dict[str, Any]:
        """
        Load command with remote registry check.
        
        Args:
            source: Local path or command name
            
        Returns:
            Dictionary with loading result information
        """
        try:
            from mcp_proxy_adapter.commands.catalog_manager import CatalogManager
            
            # Get remote registry
            plugin_servers = config.get("commands.plugin_servers", [])
            catalog_dir = "./catalog"
            
            if plugin_servers:
                # Initialize catalog manager
                catalog_manager = CatalogManager(catalog_dir)
                
                # Check if source is a command name in registry
                if not os.path.exists(source) and not source.endswith('_command.py'):
                    # Try to find in remote registry
                    for server_url in plugin_servers:
                        try:
                            server_catalog = catalog_manager.get_catalog_from_server(server_url)
                            if source in server_catalog:
                                server_cmd = server_catalog[source]
                                # Download from registry
                                if catalog_manager._download_command(source, server_cmd):
                                    source = str(catalog_manager.commands_dir / f"{source}_command.py")
                                    break
                        except Exception as e:
                            logger.warning(f"Failed to check registry {server_url}: {e}")
            
            # Load from local file
            return self._load_command_from_file(source)
            
        except Exception as e:
            logger.error(f"Failed to load command with registry check: {e}")
            return {
                "success": False,
                "commands_loaded": 0,
                "error": str(e)
            }
    
    def _load_command_from_url(self, url: str) -> Dict[str, Any]:
        """
        Load command from HTTP/HTTPS URL.
        
        Args:
            url: URL to load command from
            
        Returns:
            Dictionary with loading result information
        """
        if not REQUESTS_AVAILABLE:
            error_msg = "requests library not available, cannot load from URL"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "commands_loaded": 0,
                "source": url
            }
        
        try:
            logger.debug(f"Downloading command from URL: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Get filename from URL or use default
            filename = os.path.basename(urllib.parse.urlparse(url).path)
            if not filename or not filename.endswith('.py'):
                filename = 'remote_command.py'
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(response.text)
                temp_file_path = temp_file.name
            
            try:
                # Load command from temporary file
                result = self._load_command_from_file(temp_file_path, is_temporary=True)
                result["source"] = url
                return result
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
                    
        except Exception as e:
            error_msg = f"Failed to load command from URL {url}: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "commands_loaded": 0,
                "source": url
            }
    
    def _load_command_from_file(self, file_path: str, is_temporary: bool = False) -> Dict[str, Any]:
        """
        Load command from local file.
        
        Args:
            file_path: Path to command file
            is_temporary: Whether this is a temporary file (for cleanup)
            
        Returns:
            Dictionary with loading result information
        """
        if not os.path.exists(file_path):
            error_msg = f"Command file does not exist: {file_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "commands_loaded": 0,
                "source": file_path
            }
        
        # For temporary files (downloaded from URL), we don't enforce the _command.py naming
        # since the original filename is preserved in the URL
        if not is_temporary and not file_path.endswith('_command.py'):
            error_msg = f"Command file must end with '_command.py': {file_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "commands_loaded": 0,
                "source": file_path
            }
        
        try:
            module_name = os.path.basename(file_path)[:-3]  # Remove .py extension
            logger.debug(f"Loading command from file: {file_path}")
            
            # Load module from file
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                commands_loaded = 0
                loaded_commands = []
                
                # Find command classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Command) and 
                        obj != Command and
                        not inspect.isabstract(obj)):
                        
                        command_name = self._get_command_name(obj)
                        if self.register_loaded(cast(Type[Command], obj)):
                            commands_loaded += 1
                            loaded_commands.append(command_name)
                            logger.debug(f"Loaded command: {command_name}")
                        else:
                            logger.debug(f"Skipped command: {command_name}")
                
                return {
                    "success": True,
                    "commands_loaded": commands_loaded,
                    "loaded_commands": loaded_commands,
                    "source": file_path
                }
            else:
                error_msg = f"Failed to create module spec for: {file_path}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "commands_loaded": 0,
                    "source": file_path
                }
                
        except Exception as e:
            error_msg = f"Error loading command from file {file_path}: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "commands_loaded": 0,
                "source": file_path
            }
    
    def unload_command(self, command_name: str) -> Dict[str, Any]:
        """
        Unload a loaded command from registry.
        
        Args:
            command_name: Name of the command to unload
            
        Returns:
            Dictionary with unloading result information
        """
        logger.info(f"Unloading command: {command_name}")
        
        # Check if command exists in loaded commands
        if command_name not in self._loaded_commands:
            error_msg = f"Command '{command_name}' is not a loaded command or does not exist"
            logger.warning(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "command_name": command_name
            }
        
        try:
            # Remove from loaded commands
            del self._loaded_commands[command_name]
            
            # Remove instance if exists
            if command_name in self._instances:
                del self._instances[command_name]
            
            logger.info(f"Successfully unloaded command: {command_name}")
            return {
                "success": True,
                "command_name": command_name,
                "message": f"Command '{command_name}' unloaded successfully"
            }
            
        except Exception as e:
            error_msg = f"Failed to unload command '{command_name}': {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "command_name": command_name
            }
    
    def command_exists(self, command_name: str) -> bool:
        """
        Check if command exists with priority order.

        Args:
            command_name: Command name to check.

        Returns:
            True if command exists, False otherwise.
        """
        return (command_name in self._custom_commands or 
                command_name in self._builtin_commands or 
                command_name in self._loaded_commands)
    
    def get_command(self, command_name: str) -> Type[Command]:
        """
        Get command class with priority order.

        Args:
            command_name: Command name.

        Returns:
            Command class.

        Raises:
            NotFoundError: If command is not found.
        """
        # Check in priority order: custom -> built-in -> loaded
        if command_name in self._custom_commands:
            return self._custom_commands[command_name]
        elif command_name in self._builtin_commands:
            return self._builtin_commands[command_name]
        elif command_name in self._loaded_commands:
            return self._loaded_commands[command_name]
        else:
            raise NotFoundError(f"Command '{command_name}' not found")
    
    def get_command_instance(self, command_name: str) -> Command:
        """
        Get command instance by name. If instance doesn't exist, creates new one.
        
        Args:
            command_name: Command name
            
        Returns:
            Command instance
            
        Raises:
            NotFoundError: If command is not found
        """
        if not self.command_exists(command_name):
            raise NotFoundError(f"Command '{command_name}' not found")
            
        # Return existing instance if available
        if command_name in self._instances:
            return self._instances[command_name]
            
        # Otherwise create new instance
        try:
            command_class = self.get_command(command_name)
            return command_class()
        except Exception as e:
            logger.error(f"Failed to create instance of '{command_name}': {e}")
            raise ValueError(f"Command '{command_name}' requires dependencies but was registered as class. Register an instance instead.") from e
    
    def has_instance(self, command_name: str) -> bool:
        """
        Check if command has a registered instance.
        
        Args:
            command_name: Command name
            
        Returns:
            True if command has instance, False otherwise
        """
        return command_name in self._instances
    
    def get_all_commands(self) -> Dict[str, Type[Command]]:
        """
        Get all registered commands with priority order.

        Returns:
            Dictionary with command names and their classes.
        """
        all_commands = {}
        
        # Add commands in priority order: custom -> built-in -> loaded
        # Custom commands override built-in and loaded
        all_commands.update(self._custom_commands)
        
        # Built-in commands (only if not overridden by custom)
        for name, command_class in self._builtin_commands.items():
            if name not in all_commands:
                all_commands[name] = command_class
        
        # Loaded commands (only if not overridden by custom or built-in)
        for name, command_class in self._loaded_commands.items():
            if name not in all_commands:
                all_commands[name] = command_class
        
        return all_commands
    
    def get_commands_by_type(self) -> Dict[str, Dict[str, Type[Command]]]:
        """
        Get commands grouped by type.

        Returns:
            Dictionary with commands grouped by type.
        """
        return {
            "custom": self._custom_commands,
            "builtin": self._builtin_commands,
            "loaded": self._loaded_commands
        }
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all registered commands.
        
        Returns:
            Dictionary with command names as keys and metadata as values.
        """
        metadata = {}
        
        # Get all commands with priority order
        all_commands = self.get_all_commands()
        
        for command_name, command_class in all_commands.items():
            try:
                # Get command metadata
                if hasattr(command_class, 'get_metadata'):
                    metadata[command_name] = command_class.get_metadata()
                else:
                    # Fallback metadata
                    metadata[command_name] = {
                        "name": command_name,
                        "class": command_class.__name__,
                        "module": command_class.__module__,
                        "description": getattr(command_class, '__doc__', 'No description available')
                    }
            except Exception as e:
                logger.warning(f"Failed to get metadata for command '{command_name}': {e}")
                metadata[command_name] = {
                    "name": command_name,
                    "error": f"Failed to get metadata: {str(e)}"
                }
        
        return metadata
    
    def clear(self) -> None:
        """
        Clear all registered commands.
        """
        logger.debug("Clearing all registered commands")
        self._builtin_commands.clear()
        self._custom_commands.clear()
        self._loaded_commands.clear()
        self._instances.clear()
    
    
    async def reload_system(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Universal method for system initialization and reload.
        This method should be used both at startup and during reload.
        
        Args:
            config_path: Path to configuration file. If None, uses default or existing path.
            
        Returns:
            Dictionary with initialization information.
        """
        logger.info(f"🔄 Starting system reload with config: {config_path or 'default'}")
        
        # Step 1: Load configuration
        try:
            if config_path:
                config.load_from_file(config_path)
                logger.info(f"✅ Configuration loaded from: {config_path}")
            else:
                config.load_config()
                logger.info("✅ Configuration loaded from default path")
            
            config_reloaded = True
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            config_reloaded = False
        
        # Step 2: Initialize logging with configuration
        try:
            from mcp_proxy_adapter.core.logging import setup_logging
            setup_logging()
            logger.info("✅ Logging initialized with configuration")
        except Exception as e:
            logger.error(f"❌ Failed to initialize logging: {e}")
        
        # Step 2.5: Reload protocol manager configuration
        try:
            from mcp_proxy_adapter.core.protocol_manager import protocol_manager
            protocol_manager.reload_config()
            logger.info("✅ Protocol manager configuration reloaded")
        except Exception as e:
            logger.error(f"❌ Failed to reload protocol manager: {e}")
        
        # Step 3: Clear all commands (always clear for consistency)
        self.clear()
        
        # Step 4: Execute before init hooks
        try:
            hooks.execute_before_init_hooks()
        except Exception as e:
            logger.error(f"❌ Failed to execute before init hooks: {e}")
        
        # Step 5: Register built-in commands
        try:
            from mcp_proxy_adapter.commands.builtin_commands import register_builtin_commands
            builtin_commands_count = register_builtin_commands()
        except Exception as e:
            logger.error(f"❌ Failed to register built-in commands: {e}")
            builtin_commands_count = 0
        
        # Step 6: Execute custom commands hooks
        try:
            custom_commands_count = hooks.execute_custom_commands_hooks(self)
        except Exception as e:
            logger.error(f"❌ Failed to execute custom commands hooks: {e}")
            custom_commands_count = 0
        
        # Step 7: Load all commands (built-in, custom, loadable)
        try:
            load_result = self._load_all_commands()
            remote_commands_count = load_result.get("remote_commands", 0)
            loaded_commands_count = load_result.get("loaded_commands", 0)
        except Exception as e:
            logger.error(f"❌ Failed to load commands: {e}")
            remote_commands_count = 0
            loaded_commands_count = 0
        
        # Step 8: Execute after init hooks
        try:
            hooks.execute_after_init_hooks()
        except Exception as e:
            logger.error(f"❌ Failed to execute after init hooks: {e}")
        
        # Step 9: Register with proxy if enabled
        proxy_registration_success = False
        try:
            from mcp_proxy_adapter.core.proxy_registration import register_with_proxy
            
            # Get server configuration
            server_config = config.get("server", {})
            server_host = server_config.get("host", "0.0.0.0")
            server_port = server_config.get("port", 8000)
            
            # Determine server URL based on SSL configuration
            ssl_config = config.get("ssl", {})
            if ssl_config.get("enabled", False):
                protocol = "https"
            else:
                protocol = "http"
            
            # Use localhost for external access if host is 0.0.0.0
            if server_host == "0.0.0.0":
                server_host = "localhost"
            
            server_url = f"{protocol}://{server_host}:{server_port}"
            
            # Attempt proxy registration
            proxy_registration_success = await register_with_proxy(server_url)
            if proxy_registration_success:
                logger.info("✅ Proxy registration completed successfully during system reload")
            else:
                logger.info("ℹ️ Proxy registration is disabled or failed during system reload")
                
        except Exception as e:
            logger.error(f"❌ Failed to register with proxy during system reload: {e}")
        
        # Get final counts
        total_commands = len(self.get_all_commands())
        
        result = {
            "config_reloaded": config_reloaded,
            "builtin_commands": builtin_commands_count,
            "custom_commands": custom_commands_count,
            "loaded_commands": loaded_commands_count,
            "remote_commands": remote_commands_count,
            "total_commands": total_commands,
            "proxy_registration_success": proxy_registration_success
        }
        
        logger.info(f"✅ System reload completed: {result}")
        return result
    
    def _load_all_commands(self) -> Dict[str, Any]:
        """
        Universal command loader - handles all command types.
        
        Returns:
            Dictionary with loading results
        """
        try:
            remote_commands = 0
            loaded_commands = 0
            
            # 1. Load commands from directory (if configured)
            commands_directory = config.get("commands.commands_directory")
            if commands_directory and os.path.exists(commands_directory):
                logger.info(f"Loading commands from directory: {commands_directory}")
                for file_path in Path(commands_directory).glob("*_command.py"):
                    try:
                        result = self.load_command_from_source(str(file_path))
                        if result.get("success"):
                            loaded_commands += result.get("commands_loaded", 0)
                    except Exception as e:
                        logger.error(f"Failed to load command from {file_path}: {e}")
            
            # 2. Load commands from plugin servers (if configured)
            plugin_servers = config.get("commands.plugin_servers", [])
            if plugin_servers:
                logger.info(f"Loading commands from {len(plugin_servers)} plugin servers")
                for server_url in plugin_servers:
                    try:
                        # Load catalog from server
                        from mcp_proxy_adapter.commands.catalog_manager import CatalogManager
                        catalog_manager = CatalogManager("./catalog")
                        server_catalog = catalog_manager.get_catalog_from_server(server_url)
                        
                        # Load each command from catalog
                        for command_name, server_cmd in server_catalog.items():
                            try:
                                result = self.load_command_from_source(command_name)
                                if result.get("success"):
                                    remote_commands += result.get("commands_loaded", 0)
                            except Exception as e:
                                logger.error(f"Failed to load command {command_name}: {e}")
                                
                    except Exception as e:
                        logger.error(f"Failed to load from server {server_url}: {e}")
            
            return {
                "remote_commands": remote_commands,
                "loaded_commands": loaded_commands
            }
            
        except Exception as e:
            logger.error(f"Failed to load all commands: {e}")
            return {
                "remote_commands": 0,
                "loaded_commands": 0,
                "error": str(e)
            }


    def get_all_commands_info(self) -> Dict[str, Any]:
        """
        Get information about all registered commands.
        
        Returns:
            Dictionary with command information
        """
        commands_info = {}
        
        # Get all commands
        all_commands = self.get_all_commands()
        
        for command_name, command_class in all_commands.items():
            try:
                # Get command metadata
                metadata = command_class.get_metadata()
                
                # Get command schema
                schema = command_class.get_schema()
                
                commands_info[command_name] = {
                    "name": command_name,
                    "metadata": metadata,
                    "schema": schema,
                    "type": self._get_command_type(command_name)
                }
                
            except Exception as e:
                logger.warning(f"Failed to get info for command {command_name}: {e}")
                commands_info[command_name] = {
                    "name": command_name,
                    "error": str(e),
                    "type": self._get_command_type(command_name)
                }
        
        return {
            "commands": commands_info,
            "total": len(commands_info)
        }
    
    def get_command_info(self, command_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific command.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Dictionary with command information or None if not found
        """
        try:
            # Check if command exists
            if not self.command_exists(command_name):
                return None
            
            # Get command class
            command_class = self.get_command(command_name)
            
            # Get command metadata
            metadata = command_class.get_metadata()
            
            # Get command schema
            schema = command_class.get_schema()
            
            return {
                "name": command_name,
                "metadata": metadata,
                "schema": schema,
                "type": self._get_command_type(command_name)
            }
            
        except Exception as e:
            logger.warning(f"Failed to get info for command {command_name}: {e}")
            return {
                "name": command_name,
                "error": str(e),
                "type": self._get_command_type(command_name)
            }
    
    def _get_command_type(self, command_name: str) -> str:
        """
        Get the type of a command (built-in, custom, or loaded).
        
        Args:
            command_name: Name of the command
            
        Returns:
            Command type string
        """
        if command_name in self._custom_commands:
            return "custom"
        elif command_name in self._builtin_commands:
            return "built-in"
        elif command_name in self._loaded_commands:
            return "loaded"
        else:
            return "unknown"


# Global command registry instance
registry = CommandRegistry()

# Remove automatic command discovery - use reload_system instead
# This prevents duplication of loading logic
