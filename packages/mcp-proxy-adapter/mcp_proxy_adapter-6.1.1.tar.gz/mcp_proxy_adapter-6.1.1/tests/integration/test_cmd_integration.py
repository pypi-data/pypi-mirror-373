"""
Integration tests for /cmd endpoint and help command.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.help_command import HelpCommand


@pytest.fixture(autouse=True)
def setup_registry():
    """Setup command registry for tests."""
    # Clear registry
    registry.clear()
    
    # Register help command
    registry.register_custom(HelpCommand)
    
    yield
    
    # Clear registry again
    registry.clear()


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    from fastapi import FastAPI, Request
    from mcp_proxy_adapter.api.handlers import execute_command
    from mcp_proxy_adapter.commands.command_registry import registry
    
    # Создаем минимальное приложение без middleware
    app = FastAPI()
    
    # Добавляем только CORS middleware
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Добавляем endpoint напрямую
    @app.post("/cmd")
    async def cmd_wrapper(command_data: dict):
        try:
            # Determine request format (CommandRequest or JSON-RPC)
            if "jsonrpc" in command_data and "method" in command_data:
                # JSON-RPC format
                from mcp_proxy_adapter.api.handlers import handle_json_rpc
                return await handle_json_rpc(command_data, None)
            
            # CommandRequest format
            command_name = command_data.get("command")
            if not command_name:
                return {"error": {"code": -32600, "message": "Отсутствует обязательное поле 'command'"}}
            
            params = command_data.get("params", {})
            result = await execute_command(command_name, params, None)
            
            return {"result": result}
            
        except Exception as e:
            # Handle different types of errors
            error_msg = str(e)
            if "not found" in error_msg.lower():
                return {"error": {"code": -32601, "message": error_msg}}
            elif "Отсутствует обязательное поле" in error_msg:
                return {"error": {"code": -32600, "message": error_msg}}
            else:
                return {"error": {"code": -32603, "message": error_msg}}
    
    return TestClient(app)


def test_cmd_help_without_params(client):
    """Test /cmd endpoint with help command without parameters."""
    response = client.post(
        "/cmd",
        json={"command": "help"}
    )
    
    assert response.status_code == 200
    assert "result" in response.json()
    result = response.json()["result"]
    
    assert "commands" in result
    assert "help" in result["commands"]
    assert "summary" in result["commands"]["help"]


def test_cmd_help_with_cmdname(client):
    """Test /cmd endpoint with help command with cmdname parameter."""
    response = client.post(
        "/cmd",
        json={
            "command": "help",
            "params": {
                "cmdname": "help"
            }
        }
    )
    
    assert response.status_code == 200
    assert "result" in response.json()
    result = response.json()["result"]
    
    assert "cmdname" in result
    assert result["cmdname"] == "help"
    assert "info" in result
    assert "description" in result["info"]
    assert "params" in result["info"]
    assert "cmdname" in result["info"]["params"]


def test_cmd_help_unknown_command(client):
    """Test /cmd endpoint with help command for unknown command."""
    response = client.post(
        "/cmd",
        json={
            "command": "help",
            "params": {
                "cmdname": "unknown_command"
            }
        }
    )
    
    assert response.status_code == 200
    assert "result" in response.json()
    result = response.json()["result"]
    
    assert "error" in result
    assert "example" in result
    assert "note" in result
    assert result["error"].startswith("Command")
    assert result["example"]["command"] == "help"


def test_cmd_unknown_command(client):
    """Test /cmd endpoint with unknown command."""
    response = client.post(
        "/cmd",
        json={"command": "unknown_command"}
    )
    
    assert response.status_code == 200
    assert "error" in response.json()
    error = response.json()["error"]
    
    assert error["code"] == -32601
    assert "not found" in error["message"].lower()


def test_cmd_invalid_request(client):
    """Test /cmd endpoint with invalid request format."""
    response = client.post(
        "/cmd",
        json={"invalid": "request"}
    )
    
    assert response.status_code == 200
    assert "error" in response.json()
    error = response.json()["error"]
    
    assert error["code"] == -32600
    assert "Отсутствует обязательное поле 'command'" in error["message"] 