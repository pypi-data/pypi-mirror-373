"""MCP Proxy API Service package.

This package provides a framework for creating JSON-RPC-enabled microservices.
"""

from mcp_proxy_adapter.version import __version__
from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult, ErrorResult
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import (
    MicroserviceError, CommandError, ValidationError, 
    InvalidParamsError, NotFoundError, TimeoutError,
    InternalError
)

# Экспортируем основные классы и функции для удобного использования
__all__ = [
    "__version__",
    "create_app",
    "Command",
    "CommandResult", 
    "SuccessResult",
    "ErrorResult",
    "registry",
    "MicroserviceError",
    "CommandError",
    "ValidationError",
    "InvalidParamsError",
    "NotFoundError",
    "TimeoutError",
    "InternalError"
]
