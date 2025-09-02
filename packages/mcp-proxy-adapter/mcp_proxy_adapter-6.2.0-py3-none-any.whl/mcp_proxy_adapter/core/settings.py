"""
Settings management for the MCP Proxy Adapter framework.
Provides utilities for reading and managing framework settings from configuration.
"""

from typing import Any, Dict, Optional, Union
from mcp_proxy_adapter.config import config


class Settings:
    """
    Settings management class for the framework.
    Provides easy access to configuration values with type conversion and validation.
    """
    
    # Store custom settings as a class variable
    _custom_settings: Dict[str, Any] = {}
    
    @classmethod
    def add_custom_settings(cls, settings: Dict[str, Any]) -> None:
        """
        Add custom settings to the settings manager.
        
        Args:
            settings: Dictionary with custom settings
        """
        cls._custom_settings.update(settings)
    
    @classmethod
    def get_custom_settings(cls) -> Dict[str, Any]:
        """
        Get all custom settings.
        
        Returns:
            Dictionary with all custom settings
        """
        return cls._custom_settings.copy()
    
    @classmethod
    def get_custom_setting_value(cls, key: str, default: Any = None) -> Any:
        """
        Get custom setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        return cls._custom_settings.get(key, default)
    
    @classmethod
    def set_custom_setting_value(cls, key: str, value: Any) -> None:
        """
        Set custom setting value.
        
        Args:
            key: Setting key
            value: Value to set
        """
        cls._custom_settings[key] = value
    
    @classmethod
    def clear_custom_settings(cls) -> None:
        """
        Clear all custom settings.
        """
        cls._custom_settings.clear()
    
    @staticmethod
    def get_server_settings() -> Dict[str, Any]:
        """
        Get server configuration settings.
        
        Returns:
            Dictionary with server settings
        """
        return {
            "host": config.get("server.host", "0.0.0.0"),
            "port": config.get("server.port", 8000),
            "debug": config.get("server.debug", False),
            "log_level": config.get("server.log_level", "INFO")
        }
    
    @staticmethod
    def get_logging_settings() -> Dict[str, Any]:
        """
        Get logging configuration settings.
        
        Returns:
            Dictionary with logging settings
        """
        return {
            "level": config.get("logging.level", "INFO"),
            "file": config.get("logging.file"),
            "log_dir": config.get("logging.log_dir", "./logs"),
            "log_file": config.get("logging.log_file", "mcp_proxy_adapter.log"),
            "error_log_file": config.get("logging.error_log_file", "mcp_proxy_adapter_error.log"),
            "access_log_file": config.get("logging.access_log_file", "mcp_proxy_adapter_access.log"),
            "max_file_size": config.get("logging.max_file_size", "10MB"),
            "backup_count": config.get("logging.backup_count", 5),
            "format": config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            "date_format": config.get("logging.date_format", "%Y-%m-%d %H:%M:%S"),
            "console_output": config.get("logging.console_output", True),
            "file_output": config.get("logging.file_output", True)
        }
    
    @staticmethod
    def get_commands_settings() -> Dict[str, Any]:
        """
        Get commands configuration settings.
        
        Returns:
            Dictionary with commands settings
        """
        return {
            "auto_discovery": config.get("commands.auto_discovery", True),
            "discovery_path": config.get("commands.discovery_path", "mcp_proxy_adapter.commands"),
            "auto_commands_path": config.get("commands.auto_commands_path"),
            "custom_commands_path": config.get("commands.custom_commands_path")
        }
    
    @staticmethod
    def get_custom_setting(key: str, default: Any = None) -> Any:
        """
        Get custom setting from configuration.
        
        Args:
            key: Configuration key in dot notation (e.g., "custom.feature_enabled")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return config.get(key, default)
    
    @staticmethod
    def get_all_settings() -> Dict[str, Any]:
        """
        Get all configuration settings including custom settings.
        
        Returns:
            Dictionary with all configuration settings
        """
        all_settings = config.get_all()
        all_settings['custom_settings'] = Settings._custom_settings
        return all_settings
    
    @staticmethod
    def set_custom_setting(key: str, value: Any) -> None:
        """
        Set custom setting in configuration.
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        config.set(key, value)
    
    @staticmethod
    def reload_config() -> None:
        """
        Reload configuration from file and environment variables.
        """
        config.load_config()


class ServerSettings:
    """
    Server-specific settings helper.
    """
    
    @staticmethod
    def get_host() -> str:
        """Get server host."""
        return config.get("server.host", "0.0.0.0")
    
    @staticmethod
    def get_port() -> int:
        """Get server port."""
        return config.get("server.port", 8000)
    
    @staticmethod
    def get_debug() -> bool:
        """Get debug mode."""
        return config.get("server.debug", False)
    
    @staticmethod
    def get_log_level() -> str:
        """Get log level."""
        return config.get("server.log_level", "INFO")


class LoggingSettings:
    """
    Logging-specific settings helper.
    """
    
    @staticmethod
    def get_level() -> str:
        """Get logging level."""
        return config.get("logging.level", "INFO")
    
    @staticmethod
    def get_log_dir() -> str:
        """Get log directory."""
        return config.get("logging.log_dir", "./logs")
    
    @staticmethod
    def get_log_file() -> Optional[str]:
        """Get main log file name."""
        return config.get("logging.log_file", "mcp_proxy_adapter.log")
    
    @staticmethod
    def get_error_log_file() -> Optional[str]:
        """Get error log file name."""
        return config.get("logging.error_log_file", "mcp_proxy_adapter_error.log")
    
    @staticmethod
    def get_access_log_file() -> Optional[str]:
        """Get access log file name."""
        return config.get("logging.access_log_file", "mcp_proxy_adapter_access.log")
    
    @staticmethod
    def get_max_file_size() -> str:
        """Get max file size."""
        return config.get("logging.max_file_size", "10MB")
    
    @staticmethod
    def get_backup_count() -> int:
        """Get backup count."""
        return config.get("logging.backup_count", 5)
    
    @staticmethod
    def get_format() -> str:
        """Get log format."""
        return config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @staticmethod
    def get_date_format() -> str:
        """Get date format."""
        return config.get("logging.date_format", "%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_console_output() -> bool:
        """Get console output setting."""
        return config.get("logging.console_output", True)
    
    @staticmethod
    def get_file_output() -> bool:
        """Get file output setting."""
        return config.get("logging.file_output", True)


class CommandsSettings:
    """
    Commands-specific settings helper.
    """
    
    @staticmethod
    def get_auto_discovery() -> bool:
        """Get auto discovery setting."""
        return config.get("commands.auto_discovery", True)
    
    @staticmethod
    def get_discovery_path() -> str:
        """Get discovery path."""
        return config.get("commands.discovery_path", "mcp_proxy_adapter.commands")
    
    @staticmethod
    def get_custom_commands_path() -> Optional[str]:
        """Get custom commands path."""
        return config.get("commands.custom_commands_path")


# Convenience functions for easy access
def get_server_host() -> str:
    """Get server host."""
    return ServerSettings.get_host()


def get_server_port() -> int:
    """Get server port."""
    return ServerSettings.get_port()


def get_server_debug() -> bool:
    """Get server debug mode."""
    return ServerSettings.get_debug()


def get_logging_level() -> str:
    """Get logging level."""
    return LoggingSettings.get_level()


def get_logging_dir() -> str:
    """Get logging directory."""
    return LoggingSettings.get_log_dir()


def get_auto_discovery() -> bool:
    """Get auto discovery setting."""
    return CommandsSettings.get_auto_discovery()


def get_discovery_path() -> str:
    """Get discovery path."""
    return CommandsSettings.get_discovery_path()


def get_setting(key: str, default: Any = None) -> Any:
    """Get any setting by key."""
    return Settings.get_custom_setting(key, default)


def set_setting(key: str, value: Any) -> None:
    """Set any setting by key."""
    Settings.set_custom_setting(key, value)


def reload_settings() -> None:
    """Reload all settings from configuration."""
    Settings.reload_config()


def add_custom_settings(settings: Dict[str, Any]) -> None:
    """
    Add custom settings to the settings manager.
    
    Args:
        settings: Dictionary with custom settings
    """
    Settings.add_custom_settings(settings)


def get_custom_settings() -> Dict[str, Any]:
    """
    Get all custom settings.
    
    Returns:
        Dictionary with all custom settings
    """
    return Settings.get_custom_settings()


def get_custom_setting_value(key: str, default: Any = None) -> Any:
    """
    Get custom setting value.
    
    Args:
        key: Setting key
        default: Default value if key not found
        
    Returns:
        Setting value
    """
    return Settings.get_custom_setting_value(key, default)


def set_custom_setting_value(key: str, value: Any) -> None:
    """
    Set custom setting value.
    
    Args:
        key: Setting key
        value: Value to set
    """
    Settings.set_custom_setting_value(key, value)


def clear_custom_settings() -> None:
    """
    Clear all custom settings.
    """
    Settings.clear_custom_settings() 