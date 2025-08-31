"""
Tests for the /cmd endpoint.
"""

import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi.testclient import TestClient

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import MicroserviceError





@pytest.fixture
def mock_registry():
    """Mock for command registry."""
    with patch("mcp_proxy_adapter.api.app.registry") as mock_reg:
        yield mock_reg


@pytest.fixture
def mock_execute_command():
    """Mock for execute_command function."""
    with patch("mcp_proxy_adapter.api.app.execute_command") as mock_exec:
        yield mock_exec


def test_cmd_endpoint_basic(client, mock_registry, mock_execute_command):
    """Test basic execution of /cmd endpoint."""
    # Setup mocks
    mock_registry.command_exists.return_value = True
    mock_execute_command.return_value = {"key": "value"}
    
    # Patch the registry in the handlers module
    with patch("mcp_proxy_adapter.api.handlers.registry", mock_registry):
        with patch("mcp_proxy_adapter.api.handlers.execute_command", mock_execute_command):
            # Send request
            response = client.post(
                "/cmd",
                json={"command": "test_command", "params": {"param1": "value1"}}
            )
            
            # Check result
            assert response.status_code == 200
            assert response.json() == {"result": {"key": "value"}}
            
            # Verify mock calls with ANY for request_id since it can be dynamic
            mock_registry.command_exists.assert_called_once_with("test_command")
            mock_execute_command.assert_called_once_with(
                "test_command", {"param1": "value1"}, ANY
            )


def test_cmd_endpoint_missing_command(client):
    """Test /cmd endpoint with missing 'command' field."""
    response = client.post("/cmd", json={})
    
    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"]["code"] == -32600
    assert "Отсутствует обязательное поле 'command'" in response.json()["error"]["message"]


def test_cmd_endpoint_command_not_found(client, mock_registry):
    """Test /cmd endpoint with non-existent command."""
    # Setup mocks
    mock_registry.command_exists.return_value = False
    
    # Send request
    response = client.post("/cmd", json={"command": "non_existent"})
    
    # Check result
    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"]["code"] == -32601
    assert "не найдена" in response.json()["error"]["message"]


def test_cmd_endpoint_error_handling(client, mock_registry, mock_execute_command):
    """Test error handling in /cmd endpoint."""
    # Setup mocks
    mock_registry.command_exists.return_value = True
    
    error = MicroserviceError("Test error", code=-32000)
    error.to_dict = MagicMock(return_value={"code": -32000, "message": "Test error"})
    mock_execute_command.side_effect = error
    
    # Patch the registry in the handlers module
    with patch("mcp_proxy_adapter.api.handlers.registry", mock_registry):
        with patch("mcp_proxy_adapter.api.handlers.execute_command", mock_execute_command):
            # Send request
            response = client.post("/cmd", json={"command": "test_command"})
            
            # Check result
            assert response.status_code == 200
            assert "error" in response.json()
            assert response.json()["error"]["code"] == -32000
            assert response.json()["error"]["message"] == "Test error"


def test_cmd_endpoint_internal_error(client, mock_registry, mock_execute_command):
    """Test internal error handling in /cmd endpoint."""
    # Setup mocks
    mock_registry.command_exists.return_value = True
    mock_execute_command.side_effect = Exception("Unexpected error")
    
    # Patch the registry and execute_command in both handlers and app modules
    with patch("mcp_proxy_adapter.api.handlers.registry", mock_registry):
        with patch("mcp_proxy_adapter.api.handlers.execute_command", mock_execute_command):
            with patch("mcp_proxy_adapter.api.app.registry", mock_registry):
                with patch("mcp_proxy_adapter.api.app.execute_command", mock_execute_command):
                    # Send request
                    response = client.post("/cmd", json={"command": "test_command"})
                    
                    # Check result
                    assert response.status_code == 200
                    assert "error" in response.json()
                    assert response.json()["error"]["code"] == -32603
                    assert "Internal error" in response.json()["error"]["message"]
                    assert "Unexpected error" in response.json()["error"]["data"]["details"] 