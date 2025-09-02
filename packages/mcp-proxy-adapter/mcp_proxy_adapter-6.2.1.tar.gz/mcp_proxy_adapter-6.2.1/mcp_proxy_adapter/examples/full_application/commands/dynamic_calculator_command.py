"""
Dynamic Calculator Command
This module demonstrates a dynamically loaded command implementation for the full application example.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import BaseCommand
from mcp_proxy_adapter.commands.result import CommandResult
class CalculatorResult(CommandResult):
    """Result class for calculator command."""
    def __init__(self, operation: str, result: float, expression: str):
        self.operation = operation
        self.result = result
        self.expression = expression
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "operation": self.operation,
            "result": self.result,
            "expression": self.expression,
            "command_type": "dynamic_calculator"
        }
    def get_schema(self) -> Dict[str, Any]:
        """Get result schema."""
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "description": "Mathematical operation"},
                "result": {"type": "number", "description": "Calculation result"},
                "expression": {"type": "string", "description": "Full expression"},
                "command_type": {"type": "string", "description": "Command type"}
            },
            "required": ["operation", "result", "expression", "command_type"]
        }
class DynamicCalculatorCommand(BaseCommand):
    """Dynamic calculator command implementation."""
    def get_name(self) -> str:
        """Get command name."""
        return "dynamic_calculator"
    def get_description(self) -> str:
        """Get command description."""
        return "Dynamic calculator with basic mathematical operations"
    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Mathematical operation (add, subtract, multiply, divide)",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number",
                    "description": "Second number"
                }
            },
            "required": ["operation", "a", "b"]
        }
    async def execute(self, params: Dict[str, Any]) -> CalculatorResult:
        """Execute the calculator command."""
        operation = params.get("operation")
        a = params.get("a")
        b = params.get("b")
        if operation == "add":
            result = a + b
            expression = f"{a} + {b}"
        elif operation == "subtract":
            result = a - b
            expression = f"{a} - {b}"
        elif operation == "multiply":
            result = a * b
            expression = f"{a} * {b}"
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero is not allowed")
            result = a / b
            expression = f"{a} / {b}"
        else:
            raise ValueError(f"Unknown operation: {operation}")
        return CalculatorResult(
            operation=operation,
            result=result,
            expression=expression
        )
