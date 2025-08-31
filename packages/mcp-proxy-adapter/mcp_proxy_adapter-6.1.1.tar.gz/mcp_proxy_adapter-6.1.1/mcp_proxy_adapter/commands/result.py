"""
Module with base classes for command results.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

T = TypeVar("T", bound="CommandResult")


class CommandResult(ABC):
    """
    Base abstract class for command execution results.
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts result to dictionary for serialization.

        Returns:
            Dictionary with result data.
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Returns JSON schema for result validation.

        Returns:
            Dictionary with JSON schema.
        """
        pass
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Converts result to JSON string.

        Args:
            indent: Indentation for JSON formatting.

        Returns:
            JSON string with result.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Creates result instance from dictionary.
        This method must be overridden in subclasses.

        Args:
            data: Dictionary with result data.

        Returns:
            Result instance.
        """
        raise NotImplementedError("Method from_dict must be implemented in subclasses")


class SuccessResult(CommandResult):
    """
    Base class for successful command results.
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None, message: Optional[str] = None):
        """
        Initialize successful result.

        Args:
            data: Result data.
            message: Result message.
        """
        self.data = data or {}
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts result to dictionary for serialization.

        Returns:
            Dictionary with result data.
        """
        result = {"success": True}
        if self.data:
            result["data"] = self.data
        if self.message:
            result["message"] = self.message
        return result
    
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
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "message": {"type": "string"}
            },
            "required": ["success"]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuccessResult":
        """
        Creates successful result instance from dictionary.

        Args:
            data: Dictionary with result data.

        Returns:
            Successful result instance.
        """
        return cls(
            data=data.get("data"),
            message=data.get("message")
        )


class ErrorResult(CommandResult):
    """
    Base class for command results with error.
    
    This class follows the JSON-RPC 2.0 error object format:
    https://www.jsonrpc.org/specification#error_object
    """
    
    def __init__(
        self,
        message: str,
        code: int = -32000,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize error result.

        Args:
            message: Error message.
            code: Error code (following JSON-RPC 2.0 spec).
            details: Additional error details.
        """
        self.message = message
        self.error = message  # For backward compatibility with tests
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts result to dictionary for serialization.

        Returns:
            Dictionary with result data in JSON-RPC 2.0 error format.
        """
        result = {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message
            }
        }
        if self.details:
            result["error"]["data"] = self.details
        return result
    
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
                "success": {"type": "boolean"},
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer"},
                        "message": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["code", "message"]
                }
            },
            "required": ["success", "error"]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorResult":
        """
        Creates error result instance from dictionary.

        Args:
            data: Dictionary with result data.

        Returns:
            Error result instance.
        """
        error = data.get("error", {})
        return cls(
            message=error.get("message", "Unknown error"),
            code=error.get("code", -32000),
            details=error.get("data")
        )
