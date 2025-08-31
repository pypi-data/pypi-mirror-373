"""
Tests for API endpoints.
"""

import pytest
from typing import Dict, Any
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import asyncio

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.core.errors import NotFoundError


@pytest.fixture
def client():
    """Fixture for test client."""
    # Создаем приложение с очищенным реестром команд для тестов
    from mcp_proxy_adapter.commands.command_registry import registry
    registry.clear()  # Очищаем реестр перед тестами
    
    # Отключаем security middleware для тестов
    with patch('mcp_proxy_adapter.api.middleware.setup_middleware') as mock_setup_middleware:
        def mock_setup(app):
            # Добавляем только базовые middleware без security
            from fastapi.middleware.cors import CORSMiddleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        mock_setup_middleware.side_effect = mock_setup
        
        app = create_app()
        return TestClient(app)


@pytest.fixture
def success_result():
    """Fixture for test success result."""
    result = SuccessResult(data={"key": "value"}, message="Success")
    return result


class TestCommandsEndpoint:
    """Tests for the /api/commands endpoint."""
    
    @patch("mcp_proxy_adapter.api.app.get_commands_list")
    def test_commands_list_endpoint(self, mock_get_commands_list, client):
        """Test getting list of available commands."""
        # Create mock commands info
        mock_commands_info = {
            "command1": {
                "name": "command1",
                "description": "Test command 1",
                "params": {},
                "schema": {"type": "object"},
                "result_schema": {"type": "object"}
            },
            "command2": {
                "name": "command2",
                "description": "Test command 2",
                "params": {},
                "schema": {"type": "object"},
                "result_schema": {"type": "object"}
            }
        }
        
        # Setup mock для асинхронного метода
        mock_get_commands_list.return_value = mock_commands_info
        
        # Get commands list
        response = client.get("/api/commands")
        
        # Assertions
        assert response.status_code == 200
        assert response.json() == {"commands": mock_commands_info}
        mock_get_commands_list.assert_called_once()


class TestHealthEndpoint:
    """Tests for the /health endpoint."""
    
    @patch("mcp_proxy_adapter.api.app.get_server_health")
    def test_health_endpoint(self, mock_get_server_health, client):
        """Test getting server health information."""
        # Create mock health info
        mock_health_info = {
            "status": "ok",
            "model": "mcp-proxy-adapter",
            "version": "1.0.0"
        }
        
        # Setup mock для асинхронного метода
        mock_get_server_health.return_value = mock_health_info
        
        # Get health info
        response = client.get("/health")
        
        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "ok"
        assert "version" in response_data


class TestJsonRpcEndpoint:
    """Tests for JSON-RPC endpoint."""
    
    @pytest.mark.asyncio
    async def test_jsonrpc_endpoint_empty_batch(self, client):
        """Test JSON-RPC endpoint handles empty batch requests."""
        # Make request with empty array
        response = client.post("/api/jsonrpc", json=[])
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "error" in data
        assert data["error"]["code"] == -32600
        assert "Empty batch request" in data["error"]["message"]
    
    @pytest.mark.asyncio
    @patch("mcp_proxy_adapter.commands.command_registry.registry.get_command")
    async def test_handle_json_rpc_success(self, mock_get_command):
        """Test handle_json_rpc function with success result."""
        from mcp_proxy_adapter.commands.result import SuccessResult
        
        # Create mock command class
        mock_command = MagicMock()
        mock_command.run = AsyncMock(return_value=SuccessResult(
            data={"status": "success"},
            message="Success message"
        ))
        mock_get_command.return_value = mock_command
        
        # Create JSON-RPC request
        request_data = {
            "jsonrpc": "2.0",
            "method": "test_command",
            "params": {"param": "value"},
            "id": "1"
        }
        
        # Call handler directly
        from mcp_proxy_adapter.api.handlers import handle_json_rpc
        response = await handle_json_rpc(request_data)
        
        # Assertions
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert response["result"]["data"]["status"] == "success"
        assert response["id"] == "1"
        mock_get_command.assert_called_once_with("test_command")
        mock_command.run.assert_called_once_with(param="value")
    
    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc(self):
        """Test handle_batch_json_rpc function."""
        from mcp_proxy_adapter.api.handlers import handle_batch_json_rpc
        
        # Create mock for handle_json_rpc
        with patch("mcp_proxy_adapter.api.handlers.handle_json_rpc") as mock_handle_json_rpc:
            # Setup mock responses
            mock_handle_json_rpc.side_effect = [
                {"jsonrpc": "2.0", "result": {"status": "success1"}, "id": "1"},
                {"jsonrpc": "2.0", "result": {"status": "success2"}, "id": "2"}
            ]
            
            # Create batch request
            batch_request = [
                {"jsonrpc": "2.0", "method": "method1", "params": {}, "id": "1"},
                {"jsonrpc": "2.0", "method": "method2", "params": {}, "id": "2"}
            ]
            
            # Create mock request
            mock_request = MagicMock()
            mock_request.state.request_id = "test-request-id"
            
            # Call batch handler
            responses = await handle_batch_json_rpc(batch_request, mock_request)
            
            # Assertions
            assert len(responses) == 2
            assert responses[0]["jsonrpc"] == "2.0"
            assert responses[0]["result"]["status"] == "success1"
            assert responses[0]["id"] == "1"
            
            assert responses[1]["jsonrpc"] == "2.0"
            assert responses[1]["result"]["status"] == "success2"
            assert responses[1]["id"] == "2"
            
            # Check mock calls
            assert mock_handle_json_rpc.call_count == 2
            mock_handle_json_rpc.assert_any_call(batch_request[0], "test-request-id")
            mock_handle_json_rpc.assert_any_call(batch_request[1], "test-request-id")


class TestCommandEndpoint:
    """Tests for the /api/command/{command_name} endpoint."""
    
    @patch("mcp_proxy_adapter.api.app.execute_command")
    def test_command_endpoint_success(self, mock_execute_command, client, success_result):
        """Test direct command execution with success."""
        # Create mock params and result
        mock_params = {"param": "value"}
        mock_result = success_result.to_dict()
        
        # Setup mock
        mock_execute_command.return_value = mock_result
        
        # Execute command
        response = client.post("/api/command/test_command", json=mock_params)
        
        # Assertions
        assert response.status_code == 200
        assert response.json() == mock_result
        mock_execute_command.assert_called_once()
    
    @patch("mcp_proxy_adapter.api.app.execute_command")
    def test_command_endpoint_error(self, mock_execute_command, client):
        """Test direct command execution with error."""
        # Create mock error
        from mcp_proxy_adapter.core.errors import MicroserviceError
        mock_error = MicroserviceError("Test error", code=400)
        mock_error_dict = {"error": {"code": 400, "message": "Test error"}}
        mock_error.to_dict = MagicMock(return_value=mock_error_dict)
        
        # Setup mock
        mock_execute_command.side_effect = mock_error
        
        # Execute command
        response = client.post("/api/command/test_command", json={})
        
        # Assertions
        assert response.status_code == 400
        assert response.json() == mock_error_dict
        mock_execute_command.assert_called_once()


class TestCommandInfoEndpoint:
    """Tests for command info endpoint."""
    
    @patch("mcp_proxy_adapter.commands.command_registry.registry.get_command_info")
    def test_command_info_endpoint_success(self, mock_get_command_info, client):
        """Test command info endpoint returns command information."""
        # Setup mock
        mock_get_command_info.return_value = {
            "name": "test_command",
            "description": "Test command description",
            "params": {"param1": {"type": "string"}},
            "schema": {"properties": {"param1": {"type": "string"}}},
            "result_schema": {"properties": {"key": {"type": "string"}}}
        }
        
        # Make request
        response = client.get("/api/commands/test_command")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_command"
        assert data["description"] == "Test command description"
        assert "params" in data
        assert "schema" in data
        assert "result_schema" in data
    
    @patch("mcp_proxy_adapter.commands.command_registry.registry.get_command_info")
    def test_command_info_endpoint_not_found(self, mock_get_command_info, client):
        """Test command info endpoint returns 404 for non-existent command."""
        # Setup mock to raise NotFoundError
        mock_get_command_info.side_effect = NotFoundError("Command not found")
        
        # Make request
        response = client.get("/api/commands/non_existent")
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == 404
        assert "Command 'non_existent' not found" in data["error"]["message"] 