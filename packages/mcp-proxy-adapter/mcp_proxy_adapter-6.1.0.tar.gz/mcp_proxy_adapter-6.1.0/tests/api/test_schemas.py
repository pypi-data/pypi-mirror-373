"""
Tests for schemas module.

This module contains comprehensive tests for API schema definitions
to ensure 90%+ code coverage.
"""

import pytest
import json
from typing import Dict, Any

from mcp_proxy_adapter.api.schemas import (
    ErrorResponse, ErrorWrapper, JsonRpcRequest, JsonRpcError,
    JsonRpcSuccessResponse, JsonRpcErrorResponse, CommandResponse,
    HealthResponse, CommandListResponse, CommandRequest,
    CommandSuccessResponse, CommandErrorResponse, APIToolDescription
)


class TestErrorResponse:
    """Test cases for ErrorResponse model."""

    def test_error_response_creation(self):
        """Test ErrorResponse creation with all fields."""
        error = ErrorResponse(
            code=404,
            message="Not found",
            details={"resource": "user", "id": 123}
        )
        
        assert error.code == 404
        assert error.message == "Not found"
        assert error.details == {"resource": "user", "id": 123}

    def test_error_response_creation_without_details(self):
        """Test ErrorResponse creation without optional details."""
        error = ErrorResponse(code=500, message="Internal server error")
        
        assert error.code == 500
        assert error.message == "Internal server error"
        assert error.details is None

    def test_error_response_to_dict(self):
        """Test ErrorResponse serialization to dict."""
        error = ErrorResponse(
            code=400,
            message="Bad request",
            details={"field": "email"}
        )
        
        error_dict = error.model_dump()
        assert error_dict["code"] == 400
        assert error_dict["message"] == "Bad request"
        assert error_dict["details"] == {"field": "email"}


class TestErrorWrapper:
    """Test cases for ErrorWrapper model."""

    def test_error_wrapper_creation(self):
        """Test ErrorWrapper creation."""
        error_response = ErrorResponse(code=404, message="Not found")
        wrapper = ErrorWrapper(error=error_response)
        
        assert wrapper.error == error_response
        assert wrapper.error.code == 404

    def test_error_wrapper_to_dict(self):
        """Test ErrorWrapper serialization to dict."""
        error_response = ErrorResponse(code=500, message="Server error")
        wrapper = ErrorWrapper(error=error_response)
        
        wrapper_dict = wrapper.model_dump()
        assert "error" in wrapper_dict
        assert wrapper_dict["error"]["code"] == 500


class TestJsonRpcRequest:
    """Test cases for JsonRpcRequest model."""

    def test_json_rpc_request_creation(self):
        """Test JsonRpcRequest creation with all fields."""
        request = JsonRpcRequest(
            method="test_method",
            params={"param1": "value1", "param2": 42},
            id="request_123"
        )
        
        assert request.jsonrpc == "2.0"
        assert request.method == "test_method"
        assert request.params == {"param1": "value1", "param2": 42}
        assert request.id == "request_123"

    def test_json_rpc_request_creation_without_params(self):
        """Test JsonRpcRequest creation without params."""
        request = JsonRpcRequest(method="simple_method", id=1)
        
        assert request.method == "simple_method"
        assert request.params is None
        assert request.id == 1

    def test_json_rpc_request_creation_with_list_params(self):
        """Test JsonRpcRequest creation with list params."""
        request = JsonRpcRequest(
            method="list_method",
            params=["item1", "item2", "item3"],
            id="list_request"
        )
        
        assert request.params == ["item1", "item2", "item3"]

    def test_json_rpc_request_to_dict(self):
        """Test JsonRpcRequest serialization to dict."""
        request = JsonRpcRequest(
            method="test_method",
            params={"test": "value"},
            id="test_id"
        )
        
        request_dict = request.model_dump()
        assert request_dict["jsonrpc"] == "2.0"
        assert request_dict["method"] == "test_method"
        assert request_dict["params"] == {"test": "value"}
        assert request_dict["id"] == "test_id"


class TestJsonRpcError:
    """Test cases for JsonRpcError model."""

    def test_json_rpc_error_creation(self):
        """Test JsonRpcError creation with all fields."""
        error = JsonRpcError(
            code=-32601,
            message="Method not found",
            data={"available_methods": ["help", "config"]}
        )
        
        assert error.code == -32601
        assert error.message == "Method not found"
        assert error.data == {"available_methods": ["help", "config"]}

    def test_json_rpc_error_creation_without_data(self):
        """Test JsonRpcError creation without optional data."""
        error = JsonRpcError(code=-32700, message="Parse error")
        
        assert error.code == -32700
        assert error.message == "Parse error"
        assert error.data is None

    def test_json_rpc_error_to_dict(self):
        """Test JsonRpcError serialization to dict."""
        error = JsonRpcError(
            code=-32602,
            message="Invalid params",
            data={"expected": "string", "received": "number"}
        )
        
        error_dict = error.model_dump()
        assert error_dict["code"] == -32602
        assert error_dict["message"] == "Invalid params"
        assert error_dict["data"] == {"expected": "string", "received": "number"}


class TestJsonRpcSuccessResponse:
    """Test cases for JsonRpcSuccessResponse model."""

    def test_json_rpc_success_response_creation(self):
        """Test JsonRpcSuccessResponse creation."""
        response = JsonRpcSuccessResponse(
            result={"status": "success", "data": "test_data"},
            id="response_123"
        )
        
        assert response.jsonrpc == "2.0"
        assert response.result == {"status": "success", "data": "test_data"}
        assert response.id == "response_123"

    def test_json_rpc_success_response_to_dict(self):
        """Test JsonRpcSuccessResponse serialization to dict."""
        response = JsonRpcSuccessResponse(
            result={"message": "OK"},
            id=1
        )
        
        response_dict = response.model_dump()
        assert response_dict["jsonrpc"] == "2.0"
        assert response_dict["result"] == {"message": "OK"}
        assert response_dict["id"] == 1


class TestJsonRpcErrorResponse:
    """Test cases for JsonRpcErrorResponse model."""

    def test_json_rpc_error_response_creation(self):
        """Test JsonRpcErrorResponse creation."""
        error = JsonRpcError(code=-32601, message="Method not found")
        response = JsonRpcErrorResponse(error=error, id="error_response")
        
        assert response.jsonrpc == "2.0"
        assert response.error == error
        assert response.id == "error_response"

    def test_json_rpc_error_response_to_dict(self):
        """Test JsonRpcErrorResponse serialization to dict."""
        error = JsonRpcError(code=-32700, message="Parse error")
        response = JsonRpcErrorResponse(error=error, id=1)
        
        response_dict = response.model_dump()
        assert response_dict["jsonrpc"] == "2.0"
        assert response_dict["error"]["code"] == -32700
        assert response_dict["error"]["message"] == "Parse error"
        assert response_dict["id"] == 1


class TestCommandResponse:
    """Test cases for CommandResponse model."""

    def test_command_response_success(self):
        """Test CommandResponse creation for success case."""
        response = CommandResponse(
            success=True,
            data={"result": "command executed"},
            message="Command completed successfully"
        )
        
        assert response.success is True
        assert response.data == {"result": "command executed"}
        assert response.message == "Command completed successfully"
        assert response.error is None

    def test_command_response_error(self):
        """Test CommandResponse creation for error case."""
        error = ErrorResponse(code=400, message="Bad request")
        response = CommandResponse(
            success=False,
            error=error,
            message="Command failed"
        )
        
        assert response.success is False
        assert response.data is None
        assert response.message == "Command failed"
        assert response.error == error

    def test_command_response_to_dict(self):
        """Test CommandResponse serialization to dict."""
        response = CommandResponse(
            success=True,
            data={"status": "ok"},
            message="Success"
        )
        
        response_dict = response.model_dump()
        assert response_dict["success"] is True
        assert response_dict["data"] == {"status": "ok"}
        assert response_dict["message"] == "Success"
        assert response_dict["error"] is None


class TestHealthResponse:
    """Test cases for HealthResponse model."""

    def test_health_response_creation(self):
        """Test HealthResponse creation."""
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime=3600.5,
            components={"database": "ok", "cache": "ok"}
        )
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.uptime == 3600.5
        assert response.components == {"database": "ok", "cache": "ok"}

    def test_health_response_to_dict(self):
        """Test HealthResponse serialization to dict."""
        response = HealthResponse(
            status="degraded",
            version="2.1.0",
            uptime=7200.0,
            components={"database": "ok", "cache": "error"}
        )
        
        response_dict = response.model_dump()
        assert response_dict["status"] == "degraded"
        assert response_dict["version"] == "2.1.0"
        assert response_dict["uptime"] == 7200.0
        assert response_dict["components"] == {"database": "ok", "cache": "error"}


class TestCommandListResponse:
    """Test cases for CommandListResponse model."""

    def test_command_list_response_creation(self):
        """Test CommandListResponse creation."""
        commands = {
            "help": {"summary": "Show help", "params": {}},
            "config": {"summary": "Get config", "params": {"section": "string"}}
        }
        response = CommandListResponse(commands=commands)
        
        assert response.commands == commands
        assert len(response.commands) == 2

    def test_command_list_response_to_dict(self):
        """Test CommandListResponse serialization to dict."""
        commands = {"test": {"summary": "Test command"}}
        response = CommandListResponse(commands=commands)
        
        response_dict = response.model_dump()
        assert response_dict["commands"] == commands


class TestCommandRequest:
    """Test cases for CommandRequest model."""

    def test_command_request_creation(self):
        """Test CommandRequest creation with params."""
        request = CommandRequest(
            command="test_command",
            params={"param1": "value1", "param2": 42}
        )
        
        assert request.command == "test_command"
        assert request.params == {"param1": "value1", "param2": 42}

    def test_command_request_creation_without_params(self):
        """Test CommandRequest creation without params."""
        request = CommandRequest(command="simple_command")
        
        assert request.command == "simple_command"
        assert request.params == {}

    def test_command_request_to_dict(self):
        """Test CommandRequest serialization to dict."""
        request = CommandRequest(
            command="test_command",
            params={"test": "value"}
        )
        
        request_dict = request.model_dump()
        assert request_dict["command"] == "test_command"
        assert request_dict["params"] == {"test": "value"}


class TestCommandSuccessResponse:
    """Test cases for CommandSuccessResponse model."""

    def test_command_success_response_creation(self):
        """Test CommandSuccessResponse creation."""
        response = CommandSuccessResponse(
            result={"status": "success", "data": "test_data"}
        )
        
        assert response.result == {"status": "success", "data": "test_data"}

    def test_command_success_response_with_id(self):
        """Test CommandSuccessResponse creation with id."""
        response = CommandSuccessResponse(
            result={"message": "OK"}
        )
        
        assert response.result == {"message": "OK"}

    def test_command_success_response_to_dict(self):
        """Test CommandSuccessResponse serialization to dict."""
        response = CommandSuccessResponse(
            result={"data": "test"}
        )
        
        response_dict = response.model_dump()
        assert response_dict["result"] == {"data": "test"}


class TestCommandErrorResponse:
    """Test cases for CommandErrorResponse model."""

    def test_command_error_response_creation(self):
        """Test CommandErrorResponse creation."""
        error = JsonRpcError(code=-32601, message="Method not found")
        response = CommandErrorResponse(error=error)
        
        assert response.error == error

    def test_command_error_response_with_id(self):
        """Test CommandErrorResponse creation with id."""
        error = JsonRpcError(code=-32700, message="Parse error")
        response = CommandErrorResponse(error=error)
        
        assert response.error == error

    def test_command_error_response_to_dict(self):
        """Test CommandErrorResponse serialization to dict."""
        error = JsonRpcError(code=-32602, message="Invalid params")
        response = CommandErrorResponse(error=error)
        
        response_dict = response.model_dump()
        assert response_dict["error"]["code"] == -32602
        assert response_dict["error"]["message"] == "Invalid params"


class TestAPIToolDescription:
    """Test cases for APIToolDescription class."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock command registry for testing."""
        from unittest.mock import Mock
        
        registry = Mock()
        registry.get_all_metadata.return_value = {
            "help": {
                "summary": "Show help information",
                "description": "Display help for commands",
                "params": {
                    "command": {
                        "type": "строка",
                        "description": "Command name",
                        "required": False
                    }
                },
                "examples": [
                    {
                        "command": "help",
                        "params": {"command": "config"}
                    }
                ]
            },
            "config": {
                "summary": "Get configuration",
                "description": "Retrieve configuration settings",
                "params": {
                    "section": {
                        "type": "строка",
                        "description": "Configuration section",
                        "required": True
                    }
                },
                "examples": [
                    {
                        "command": "config",
                        "params": {"section": "database"}
                    }
                ]
            }
        }
        
        return registry

    def test_generate_tool_description(self, mock_registry):
        """Test tool description generation."""
        tool_name = "test_tool"
        
        description = APIToolDescription.generate_tool_description(tool_name, mock_registry)
        
        assert description["name"] == tool_name
        assert "description" in description
        assert "supported_commands" in description
        assert "examples" in description
        assert "help" in description["supported_commands"]
        assert "config" in description["supported_commands"]

    def test_generate_tool_description_text(self, mock_registry):
        """Test tool description text generation."""
        tool_name = "test_tool"
        
        text = APIToolDescription.generate_tool_description_text(tool_name, mock_registry)
        
        assert isinstance(text, str)
        assert tool_name in text
        assert "help" in text
        assert "config" in text

    def test_simplify_type_conversion(self):
        """Test type simplification for various input types."""
        # Test string types
        assert APIToolDescription._simplify_type("str") == "строка"
        assert APIToolDescription._simplify_type("int") == "целое число"
        assert APIToolDescription._simplify_type("float") == "число"
        assert APIToolDescription._simplify_type("bool") == "логическое значение"
        assert APIToolDescription._simplify_type("List") == "список"
        assert APIToolDescription._simplify_type("Dict") == "объект"
        
        # Test unknown type
        assert APIToolDescription._simplify_type("неизвестный") == "значение"

    def test_extract_param_description(self):
        """Test parameter description extraction."""
        doc_string = """
        Test command.
        
        Args:
            param1: First parameter description
            param2: Second parameter description
        """
        
        description = APIToolDescription._extract_param_description(doc_string, "param1")
        assert "First parameter description" in description
        
        description = APIToolDescription._extract_param_description(doc_string, "param2")
        assert "Second parameter description" in description
        
        # Test non-existent parameter
        description = APIToolDescription._extract_param_description(doc_string, "nonexistent")
        assert description == ""

    def test_extract_param_description_no_args_section(self):
        """Test parameter description extraction without Args section."""
        doc_string = "Simple command without Args section."
        
        description = APIToolDescription._extract_param_description(doc_string, "param")
        assert description == ""

    def test_extract_param_description_empty_docstring(self):
        """Test parameter description extraction with empty docstring."""
        description = APIToolDescription._extract_param_description("", "param")
        assert description == ""

    def test_generate_tool_description_empty_registry(self, mock_registry):
        """Test tool description generation with empty registry."""
        mock_registry.get_all_metadata.return_value = {}
        
        description = APIToolDescription.generate_tool_description("empty_tool", mock_registry)
        
        assert description["name"] == "empty_tool"
        assert description["supported_commands"] == {}
        assert description["examples"] == []

    def test_generate_tool_description_with_missing_fields(self, mock_registry):
        """Test tool description generation with missing metadata fields."""
        mock_registry.get_all_metadata.return_value = {
            "incomplete": {
                "summary": "Incomplete command",
                "description": "Incomplete command description",
                "params": {}
                # Missing examples
            }
        }
        
        description = APIToolDescription.generate_tool_description("incomplete_tool", mock_registry)
        
        assert "incomplete" in description["supported_commands"]
        # Should handle missing fields gracefully
        assert description["supported_commands"]["incomplete"]["summary"] == "Incomplete command" 