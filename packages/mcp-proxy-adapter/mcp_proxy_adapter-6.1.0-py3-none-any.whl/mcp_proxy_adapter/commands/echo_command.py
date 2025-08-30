"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Echo command for testing purposes.
"""

import asyncio
from typing import Any, Dict, Optional

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult


class EchoCommandResult(SuccessResult):
    """Result for echo command."""
    
    def __init__(self, message: str, timestamp: Optional[str] = None):
        data = {"message": message}
        if timestamp:
            data["timestamp"] = timestamp
        super().__init__(data=data, message=message)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for result."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "timestamp": {"type": "string", "nullable": True}
                    }
                },
                "message": {"type": "string"}
            },
            "required": ["success", "data"]
        }


class EchoCommand(Command):
    """Echo command for testing purposes."""
    
    name = "echo"
    version = "1.0.0"
    descr = "Echo command for testing"
    category = "testing"
    author = "Vasiliy Zdanovskiy"
    email = "vasilyvz@gmail.com"
    result_class = EchoCommandResult
    
    async def execute(self, **kwargs) -> EchoCommandResult:
        """Execute echo command."""
        message = kwargs.get("message", "Hello, World!")
        timestamp = kwargs.get("timestamp")
        
        # Simulate some processing time
        await asyncio.sleep(0.001)
        
        return EchoCommandResult(message=message, timestamp=timestamp)
    
    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo",
                    "default": "Hello, World!"
                },
                "timestamp": {
                    "type": "string",
                    "description": "Optional timestamp",
                    "nullable": True
                }
            }
        }
