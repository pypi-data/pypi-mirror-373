"""
Module for registering built-in framework commands.

This module contains the procedure for adding predefined commands
that are part of the framework.
"""

from typing import List
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.help_command import HelpCommand
from mcp_proxy_adapter.commands.health_command import HealthCommand
from mcp_proxy_adapter.commands.config_command import ConfigCommand
from mcp_proxy_adapter.commands.reload_command import ReloadCommand
from mcp_proxy_adapter.commands.settings_command import SettingsCommand
from mcp_proxy_adapter.commands.load_command import LoadCommand
from mcp_proxy_adapter.commands.unload_command import UnloadCommand
from mcp_proxy_adapter.commands.plugins_command import PluginsCommand
from mcp_proxy_adapter.commands.transport_management_command import TransportManagementCommand
from mcp_proxy_adapter.commands.proxy_registration_command import ProxyRegistrationCommand
from mcp_proxy_adapter.commands.echo_command import EchoCommand
from mcp_proxy_adapter.commands.role_test_command import RoleTestCommand
from mcp_proxy_adapter.core.logging import logger


def register_builtin_commands() -> int:
    """
    Register all built-in framework commands.
    
    Returns:
        Number of built-in commands registered.
    """
    logger.debug("Registering built-in framework commands...")
    
    builtin_commands = [
        HelpCommand,
        HealthCommand,
        ConfigCommand,
        ReloadCommand,
        SettingsCommand,
        LoadCommand,
        UnloadCommand,
        PluginsCommand,
        TransportManagementCommand,
        ProxyRegistrationCommand,
        EchoCommand,
        RoleTestCommand
    ]
    
    registered_count = 0
    
    for command_class in builtin_commands:
        try:
            # Get command name for logging
            command_name = getattr(command_class, 'name', command_class.__name__.lower())
            if command_name.endswith('command'):
                command_name = command_name[:-7]
            
            # Check if command already exists (should not happen for built-in)
            if registry.command_exists(command_name):
                logger.warning(f"Built-in command '{command_name}' already exists, skipping")
                continue
            
            # Register the command
            registry.register_builtin(command_class)
            registered_count += 1
            logger.debug(f"Registered built-in command: {command_name}")
            
        except Exception as e:
            logger.error(f"Failed to register built-in command {command_class.__name__}: {e}")
    
    logger.info(f"Registered {registered_count} built-in framework commands")
    return registered_count


def get_builtin_commands_list() -> list:
    """
    Get list of all built-in command classes.
    
    Returns:
        List of built-in command classes.
    """
    return [
        HelpCommand,
        HealthCommand,
        ConfigCommand,
        ReloadCommand,
        SettingsCommand,
        LoadCommand,
        UnloadCommand,
        PluginsCommand,
        TransportManagementCommand,
        ProxyRegistrationCommand,
        EchoCommand,
        RoleTestCommand
    ] 