"""
Common mock classes for testing.

This module contains shared mock classes used across different test modules
to avoid duplication and ensure consistency.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult


class MockResult(CommandResult):
    """Mock result class for testing."""
    
    def __init__(self, data: Dict[str, Any] = None, message: str = "Mock result"):
        self.data = data or {"status": "success"}
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": True,
            "data": self.data,
            "message": self.message
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get result schema."""
        return {
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "message": {"type": "string"}
            }
        }


class MockCommand(Command):
    """Mock command class for testing."""
    
    name = "mock_command"
    result_class = MockResult
    
    def __init__(self, return_data: Dict[str, Any] = None):
        self.return_data = return_data or {"result": "mock"}
    
    async def execute(self, **kwargs) -> MockResult:
        """Execute mock command."""
        return MockResult(data=self.return_data, message="Mock command executed")
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "integer"}
            }
        }


class MockEchoResult(CommandResult):
    """Mock echo result class for testing."""
    
    def __init__(self, message: str = "Hello", params: Dict[str, Any] = None):
        self.message = message
        self.params = params or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": True,
            "data": {
                "message": self.message,
                "params": self.params
            }
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get result schema."""
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "params": {"type": "object"}
            }
        }


class MockEchoCommand(Command):
    """Mock echo command class for testing."""
    
    name = "echo"
    result_class = MockEchoResult
    
    async def execute(self, message: str = "Hello", **kwargs) -> MockEchoResult:
        """Execute mock echo command."""
        return MockEchoResult(message=message, params=kwargs)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string", "default": "Hello"}
            }
        }


class MockErrorResult(CommandResult):
    """Mock error result class for testing."""
    
    def __init__(self, message: str = "Mock error", code: int = 400):
        self.message = message
        self.code = code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message
            }
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get result schema."""
        return {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer"},
                        "message": {"type": "string"}
                    }
                }
            }
        }


class MockErrorCommand(Command):
    """Mock error command class for testing."""
    
    name = "error_command"
    result_class = MockErrorResult
    
    async def execute(self, **kwargs) -> MockErrorResult:
        """Execute mock error command."""
        return MockErrorResult(message="Mock error occurred", code=500)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {}
        }


class MockAsyncCommand(Command):
    """Mock async command class for testing."""
    
    name = "async_command"
    result_class = MockResult
    
    async def execute(self, delay: float = 0.1, **kwargs) -> MockResult:
        """Execute mock async command with delay."""
        import asyncio
        await asyncio.sleep(delay)
        return MockResult(data={"async": True, "delay": delay})
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "delay": {"type": "number", "default": 0.1}
            }
        }
