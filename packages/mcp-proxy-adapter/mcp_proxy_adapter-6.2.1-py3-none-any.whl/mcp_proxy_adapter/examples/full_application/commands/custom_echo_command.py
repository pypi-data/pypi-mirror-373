"""
Custom Echo Command
This module demonstrates a custom command implementation for the full application example.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import BaseCommand
from mcp_proxy_adapter.commands.result import CommandResult
class CustomEchoResult(CommandResult):
    """Result class for custom echo command."""
    def __init__(self, message: str, timestamp: str, echo_count: int):
        self.message = message
        self.timestamp = timestamp
        self.echo_count = echo_count
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "message": self.message,
            "timestamp": self.timestamp,
            "echo_count": self.echo_count,
            "command_type": "custom_echo"
        }
    def get_schema(self) -> Dict[str, Any]:
        """Get result schema."""
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Echoed message"},
                "timestamp": {"type": "string", "description": "Timestamp of echo"},
                "echo_count": {"type": "integer", "description": "Number of echoes"},
                "command_type": {"type": "string", "description": "Command type"}
            },
            "required": ["message", "timestamp", "echo_count", "command_type"]
        }
class CustomEchoCommand(BaseCommand):
    """Custom echo command implementation."""
    def __init__(self):
        super().__init__()
        self.echo_count = 0
    def get_name(self) -> str:
        """Get command name."""
        return "custom_echo"
    def get_description(self) -> str:
        """Get command description."""
        return "Custom echo command with enhanced features"
    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo",
                    "default": "Hello from custom echo!"
                },
                "repeat": {
                    "type": "integer",
                    "description": "Number of times to repeat",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["message"]
        }
    async def execute(self, params: Dict[str, Any]) -> CustomEchoResult:
        """Execute the custom echo command."""
        message = params.get("message", "Hello from custom echo!")
        repeat = min(max(params.get("repeat", 1), 1), 10)
        self.echo_count += 1
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        # Repeat the message
        echoed_message = " ".join([message] * repeat)
        return CustomEchoResult(
            message=echoed_message,
            timestamp=timestamp,
            echo_count=self.echo_count
        )
