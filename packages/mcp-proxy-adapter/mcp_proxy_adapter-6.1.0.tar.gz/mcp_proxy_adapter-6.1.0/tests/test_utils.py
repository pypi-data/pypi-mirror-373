"""
Test utilities for mcp_microservice.
"""

from typing import Any, Dict
from mcp_proxy_adapter.commands.result import CommandResult


class MockResult(CommandResult):
    """
    Mock result class for testing.
    
    Attributes:
        message: Test message.
        timestamp: Test timestamp.
    """
    
    def __init__(self, message: str = "Test message", timestamp: float = 12345.0):
        self.message = message
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts result to dictionary for serialization.

        Returns:
            Dictionary with result data.
        """
        return {
            "message": self.message,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Returns JSON schema for result validation.

        Returns:
            Dictionary with JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Test message"},
                "timestamp": {"type": "number", "description": "Test timestamp"}
            },
            "required": ["message", "timestamp"]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockResult":
        """
        Creates result instance from dictionary.

        Args:
            data: Dictionary with result data.

        Returns:
            MockResult instance.
        """
        return cls(
            message=data.get("message", ""),
            timestamp=data.get("timestamp", 0.0)
        ) 