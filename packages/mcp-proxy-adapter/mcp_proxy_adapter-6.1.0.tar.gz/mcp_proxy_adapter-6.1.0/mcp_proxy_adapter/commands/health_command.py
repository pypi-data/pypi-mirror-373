"""
Module with health command implementation.
"""

import os
import platform
import sys
import psutil
from datetime import datetime
from typing import Dict, Any, Optional

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.proxy_registration import get_proxy_registration_status


class HealthResult(SuccessResult):
    """
    Result of the health command execution.
    """
    
    def __init__(self, status: str, version: str, uptime: float, components: Dict[str, Any]):
        """
        Initialize health command result.
        
        Args:
            status: Server status ("ok" or "error")
            version: Server version
            uptime: Server uptime in seconds
            components: Dictionary with components status
        """
        super().__init__(
            data={
                "status": status,
                "version": version,
                "uptime": uptime,
                "components": components
            }
        )
    
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
                        "status": {"type": "string"},
                        "version": {"type": "string"},
                        "uptime": {"type": "number"},
                        "components": {
                            "type": "object",
                            "properties": {
                                "system": {"type": "object"},
                                "process": {"type": "object"},
                                "commands": {"type": "object"}
                            }
                        }
                    },
                    "required": ["status", "version", "uptime", "components"]
                }
            },
            "required": ["data"]
        }


class HealthCommand(Command):
    """
    Command that returns information about server health and status.
    """
    
    name = "health"
    result_class = HealthResult
    
    async def execute(self) -> HealthResult:
        """
        Execute health command.
        
        Returns:
            HealthResult: Health command result
        """
        # Get version from package
        try:
            from mcp_proxy_adapter.version import __version__ as version
        except ImportError:
            version = "unknown"
        
        # Get process start time
        process = psutil.Process(os.getpid())
        start_time = datetime.fromtimestamp(process.create_time())
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        
        # Get system information
        memory_info = process.memory_info()
        
        return HealthResult(
            status="ok",
            version=version,
            uptime=uptime_seconds,
            components={
                "system": {
                    "python_version": sys.version,
                    "platform": platform.platform(),
                    "cpu_count": os.cpu_count()
                },
                "process": {
                    "pid": os.getpid(),
                    "memory_usage_mb": memory_info.rss / (1024 * 1024),
                    "start_time": start_time.isoformat()
                },
                "commands": {
                    "registered_count": len(registry.get_all_commands())
                },
                "proxy_registration": {
                    "enabled": get_proxy_registration_status().get("enabled", False),
                    "registered": get_proxy_registration_status().get("registered", False),
                    "server_key": get_proxy_registration_status().get("server_key"),
                    "proxy_url": get_proxy_registration_status().get("proxy_url")
                }
            }
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters validation.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "additionalProperties": False,
            "description": "Command doesn't accept any parameters"
        }
