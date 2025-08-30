"""
Tests for API handlers module.

This module contains comprehensive tests for the handlers module
to ensure 90%+ code coverage.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, List

from fastapi import Request

from mcp_proxy_adapter.api.handlers import (
    execute_command, handle_batch_json_rpc, handle_json_rpc,
    _create_error_response, get_server_health, get_commands_list
)
from mcp_proxy_adapter.core.errors import (
    NotFoundError, MethodNotFoundError, InvalidRequestError,
    InternalError, MicroserviceError, InvalidParamsError
)
from mcp_proxy_adapter.commands.command_registry import registry


class TestExecuteCommand:
    """Test cases for execute_command function."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock registry for testing."""
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_reg:
            yield mock_reg

    @pytest.fixture
    def mock_command_class(self):
        """Create a mock command class for testing."""
        class MockCommand:
            name = "test_command"
            
            @classmethod
            def get_schema(cls):
                return {"type": "object", "properties": {}}
            
            @classmethod
            async def run(cls, **kwargs):
                return MockResult()
            
            async def execute(self, **kwargs):
                return {"result": "test"}
        
        class MockResult:
            def to_dict(self):
                return {"result": "test"}
        
        return MockCommand

    @pytest.mark.asyncio
    async def test_execute_command_success(self, mock_registry, mock_command_class):
        """Test successful command execution."""
        mock_registry.get_command.return_value = mock_command_class
        
        result = await execute_command("test_command", {"param": "value"})
        
        assert result == {"result": "test"}
        mock_registry.get_command.assert_called_once_with("test_command")

    @pytest.mark.asyncio
    async def test_execute_command_with_request_id(self, mock_registry, mock_command_class):
        """Test command execution with request ID."""
        mock_registry.get_command.return_value = mock_command_class
        
        result = await execute_command("test_command", {"param": "value"}, "req_123")
        
        assert result == {"result": "test"}

    @pytest.mark.asyncio
    async def test_execute_command_not_found(self, mock_registry):
        """Test command execution when command not found."""
        mock_registry.get_command.side_effect = NotFoundError("Command not found")
        
        with pytest.raises(MethodNotFoundError):
            await execute_command("nonexistent_command", {})

    @pytest.mark.asyncio
    async def test_execute_command_microservice_error(self, mock_registry):
        """Test command execution with microservice error."""
        mock_registry.get_command.side_effect = InvalidRequestError("Invalid parameters")
        
        with pytest.raises(InvalidRequestError):
            await execute_command("test_command", {})

    @pytest.mark.asyncio
    async def test_execute_command_general_exception(self, mock_registry):
        """Test command execution with general exception."""
        mock_registry.get_command.side_effect = Exception("Unexpected error")
        
        with pytest.raises(InternalError):
            await execute_command("test_command", {})

    @pytest.mark.asyncio
    async def test_execute_command_execution_time_logging(self, mock_registry, mock_command_class):
        """Test that execution time is logged."""
        mock_registry.get_command.return_value = mock_command_class
        
        with patch('mcp_proxy_adapter.api.handlers.logger') as mock_logger:
            await execute_command("test_command", {})
            
            # Check that timing was logged
            mock_logger.info.assert_called()
            call_args = mock_logger.info.call_args[0][0]
            assert "executed in" in call_args


class TestHandleBatchJsonRpc:
    """Test cases for handle_batch_json_rpc function."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = Mock(spec=Request)
        request.state.request_id = "batch_123"
        return request

    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc_success(self, mock_request):
        """Test successful batch JSON-RPC handling."""
        batch_requests = [
            {"jsonrpc": "2.0", "method": "help", "id": 1},
            {"jsonrpc": "2.0", "method": "config", "id": 2}
        ]
        
        with patch('mcp_proxy_adapter.api.handlers.handle_json_rpc') as mock_handle:
            mock_handle.side_effect = [
                {"jsonrpc": "2.0", "result": "help_result", "id": 1},
                {"jsonrpc": "2.0", "result": "config_result", "id": 2}
            ]
            
            responses = await handle_batch_json_rpc(batch_requests, mock_request)
            
            assert len(responses) == 2
            assert responses[0]["id"] == 1
            assert responses[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc_without_request(self):
        """Test batch JSON-RPC handling without request object."""
        batch_requests = [
            {"jsonrpc": "2.0", "method": "help", "id": 1}
        ]
        
        with patch('mcp_proxy_adapter.api.handlers.handle_json_rpc') as mock_handle:
            mock_handle.return_value = {"jsonrpc": "2.0", "result": "help_result", "id": 1}
            
            responses = await handle_batch_json_rpc(batch_requests)
            
            assert len(responses) == 1

    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc_empty_batch(self):
        """Test batch JSON-RPC handling with empty batch."""
        responses = await handle_batch_json_rpc([])
        
        assert responses == []


class TestHandleJsonRpc:
    """Test cases for handle_json_rpc function."""

    @pytest.mark.asyncio
    async def test_handle_json_rpc_success(self):
        """Test successful JSON-RPC handling."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.return_value = {"result": "help_result"}
            
            response = await handle_json_rpc(request_data)
            
            assert response["jsonrpc"] == "2.0"
            assert response["result"] == {"result": "help_result"}
            assert response["id"] == 1

    @pytest.mark.asyncio
    async def test_handle_json_rpc_with_request_id(self):
        """Test JSON-RPC handling with request ID."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.return_value = {"result": "help_result"}
            
            response = await handle_json_rpc(request_data, "req_123")
            
            assert response["jsonrpc"] == "2.0"
            assert response["result"] == {"result": "help_result"}

    @pytest.mark.asyncio
    async def test_handle_json_rpc_invalid_version(self):
        """Test JSON-RPC handling with invalid version."""
        request_data = {
            "jsonrpc": "1.0",  # Invalid version
            "method": "help",
            "id": 1
        }
        
        response = await handle_json_rpc(request_data)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid Request

    @pytest.mark.asyncio
    async def test_handle_json_rpc_missing_method(self):
        """Test JSON-RPC handling with missing method."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1
            # Missing method
        }
        
        response = await handle_json_rpc(request_data)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid Request

    @pytest.mark.asyncio
    async def test_handle_json_rpc_microservice_error(self):
        """Test JSON-RPC handling with microservice error."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.side_effect = InvalidRequestError("Invalid parameters")
            
            response = await handle_json_rpc(request_data)
            
            assert response["jsonrpc"] == "2.0"
            assert "error" in response
            assert response["error"]["code"] == -32600  # Invalid Request

    @pytest.mark.asyncio
    async def test_handle_json_rpc_unhandled_exception(self):
        """Test JSON-RPC handling with unhandled exception."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.side_effect = Exception("Unexpected error")
            
            response = await handle_json_rpc(request_data)
            
            assert response["jsonrpc"] == "2.0"
            assert "error" in response
            assert response["error"]["code"] == -32603  # Internal error

    @pytest.mark.asyncio
    async def test_handle_json_rpc_without_params(self):
        """Test JSON-RPC handling without parameters."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
            # No params
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.return_value = {"result": "help_result"}
            
            response = await handle_json_rpc(request_data)
            
            assert response["jsonrpc"] == "2.0"
            assert response["result"] == {"result": "help_result"}


class TestCreateErrorResponse:
    """Test cases for _create_error_response function."""

    def test_create_error_response(self):
        """Test creating error response."""
        error = InvalidRequestError("Test error")
        request_id = 123
        
        response = _create_error_response(error, request_id)
        
        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == -32600
        assert response["id"] == 123

    def test_create_error_response_with_none_id(self):
        """Test creating error response with None ID."""
        error = InvalidRequestError("Test error")
        
        response = _create_error_response(error, None)
        
        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == -32600
        assert response["id"] is None


class TestGetServerHealth:
    """Test cases for get_server_health function."""

    @pytest.mark.asyncio
    async def test_get_server_health(self):
        """Test getting server health information."""
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {"help": Mock(), "config": Mock()}
            
            health = await get_server_health()
            
            assert health["status"] == "ok"
            assert health["version"] == "1.0.0"
            assert "uptime" in health
            assert "components" in health
            assert health["components"]["commands"]["registered_count"] == 2

    @pytest.mark.asyncio
    async def test_get_server_health_with_empty_registry(self):
        """Test getting server health with empty registry."""
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            health = await get_server_health()
            
            assert health["status"] == "ok"
            assert health["components"]["commands"]["registered_count"] == 0

    @pytest.mark.asyncio
    async def test_get_server_health_system_info(self):
        """Test that system information is included."""
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            health = await get_server_health()
            
            assert "system" in health["components"]
            assert "process" in health["components"]
            assert "python_version" in health["components"]["system"]
            assert "platform" in health["components"]["system"]
            assert "cpu_count" in health["components"]["system"]


class TestGetCommandsList:
    """Test cases for get_commands_list function."""

    @pytest.mark.asyncio
    async def test_get_commands_list(self):
        """Test getting commands list."""
        mock_command1 = Mock()
        mock_command1.get_schema.return_value = {
            "description": "Test command 1",
            "properties": {}
        }
        
        mock_command2 = Mock()
        mock_command2.get_schema.return_value = {
            "description": "Test command 2",
            "properties": {}
        }
        
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {
                "help": mock_command1,
                "config": mock_command2
            }
            
            commands = await get_commands_list()
            
            assert len(commands) == 2
            assert "help" in commands
            assert "config" in commands
            assert commands["help"]["name"] == "help"
            assert commands["help"]["description"] == "Test command 1"

    @pytest.mark.asyncio
    async def test_get_commands_list_empty_registry(self):
        """Test getting commands list with empty registry."""
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            commands = await get_commands_list()
            
            assert commands == {}

    @pytest.mark.asyncio
    async def test_get_commands_list_command_without_description(self):
        """Test getting commands list with command without description."""
        mock_command = Mock()
        mock_command.get_schema.return_value = {
            "properties": {}
            # No description
        }
        
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {"test": mock_command}
            
            commands = await get_commands_list()
            
            assert "test" in commands
            assert commands["test"]["description"] == ""


class TestHandlersIntegration:
    """Integration tests for handlers."""

    @pytest.mark.asyncio
    async def test_full_json_rpc_workflow(self):
        """Test complete JSON-RPC workflow."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.return_value = {"result": "help_result"}
            
            response = await handle_json_rpc(request_data)
            
            assert response["jsonrpc"] == "2.0"
            assert response["result"] == {"result": "help_result"}
            assert response["id"] == 1

    @pytest.mark.asyncio
    async def test_batch_json_rpc_workflow(self):
        """Test complete batch JSON-RPC workflow."""
        batch_requests = [
            {"jsonrpc": "2.0", "method": "help", "id": 1},
            {"jsonrpc": "2.0", "method": "config", "id": 2}
        ]
        
        with patch('mcp_proxy_adapter.api.handlers.handle_json_rpc') as mock_handle:
            mock_handle.side_effect = [
                {"jsonrpc": "2.0", "result": "help_result", "id": 1},
                {"jsonrpc": "2.0", "result": "config_result", "id": 2}
            ]
            
            responses = await handle_batch_json_rpc(batch_requests)
            
            assert len(responses) == 2
            assert responses[0]["id"] == 1
            assert responses[1]["id"] == 2


class TestHandlersEdgeCases:
    """Test edge cases for handlers."""

    @pytest.mark.asyncio
    async def test_execute_command_with_complex_params(self):
        """Test command execution with complex parameters."""
        class MockCommandClass:
            @classmethod
            async def run(cls, **kwargs):
                return MockResult()
        
        class MockResult:
            def to_dict(self):
                return {"result": "complex"}
        
        with patch('mcp_proxy_adapter.api.handlers.registry') as mock_registry:
            mock_registry.get_command.return_value = MockCommandClass
            
            complex_params = {
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "boolean": True
            }
            
            result = await execute_command("test_command", complex_params)
            
            assert result == {"result": "complex"}

    @pytest.mark.asyncio
    async def test_json_rpc_with_null_params(self):
        """Test JSON-RPC handling with null parameters."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "params": None,
            "id": 1
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.return_value = {"result": "help_result"}
            
            response = await handle_json_rpc(request_data)
            
            assert response["jsonrpc"] == "2.0"
            assert response["result"] == {"result": "help_result"}

    @pytest.mark.asyncio
    async def test_json_rpc_without_id(self):
        """Test JSON-RPC handling without ID."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help"
            # No id
        }
        
        with patch('mcp_proxy_adapter.api.handlers.execute_command') as mock_execute:
            mock_execute.return_value = {"result": "help_result"}
            
            response = await handle_json_rpc(request_data)
            
            assert response["jsonrpc"] == "2.0"
            assert response["result"] == {"result": "help_result"}
            assert response["id"] is None 