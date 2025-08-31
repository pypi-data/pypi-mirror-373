"""
Core functionality for MCP Proxy Adapter.
"""

from .errors import *
from .logging import *
from .settings import *

__all__ = [
    # Errors
    "NotFoundError",
    "InvalidParamsError",
    "CommandExecutionError",
    "ConfigurationError",
    
    # Logging
    "setup_logging",
    "get_logger",
    "logger",
    "RequestLogger",
    "CustomFormatter",
    "RequestContextFilter",
    
    # Settings
"Settings",
"ServerSettings",
"LoggingSettings",
"CommandsSettings",
"get_server_host",
"get_server_port",
"get_server_debug",
"get_logging_level",
"get_logging_dir",
"get_auto_discovery",
"get_discovery_path",
"get_setting",
"set_setting",
"reload_settings",
"add_custom_settings",
"get_custom_settings",
"get_custom_setting_value",
"set_custom_setting_value",
"clear_custom_settings"
]
