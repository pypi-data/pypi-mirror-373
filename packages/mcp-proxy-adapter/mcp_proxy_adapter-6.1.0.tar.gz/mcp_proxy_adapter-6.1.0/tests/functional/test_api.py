"""
Functional tests for the API.
"""

import pytest
from typing import Dict, Any

from fastapi.testclient import TestClient

from mcp_proxy_adapter.commands.command_registry import registry
from tests.common.mock_classes import MockEchoCommand as EchoCommand


@pytest.fixture
def register_echo_command(clean_registry):
    """
    Fixture to register the Echo command for testing.
    
    Args:
        clean_registry: Fixture to clean registry before and after test.
    """
    registry.register_custom(EchoCommand)
    yield
    registry.clear()


@pytest.mark.functional
def test_execute_command(test_client: TestClient, json_rpc_request: Dict[str, Any], register_echo_command):
    """
    Test execution of command via API.
    
    Args:
        test_client: FastAPI test client.
        json_rpc_request: Base JSON-RPC request.
        register_echo_command: Fixture to register test command.
    """
    # Create JSON-RPC request
    request_data = json_rpc_request.copy()
    request_data["method"] = "echo"
    request_data["params"] = {"test_key": "test_value"}
    
    # Send request
    response = test_client.post("/api/jsonrpc", json=request_data)
    
    # Check response
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    # Check response structure
    data = response.json()
    assert "jsonrpc" in data and data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "id" in data and data["id"] == request_data["id"]
    
    # Check result content
    assert "params" in data["result"]
    assert data["result"]["params"] == {"test_key": "test_value"}


@pytest.mark.functional
def test_execute_nonexistent_command(test_client: TestClient, json_rpc_request: Dict[str, Any]):
    """
    Test execution of nonexistent command.
    
    Args:
        test_client: FastAPI test client.
        json_rpc_request: Base JSON-RPC request.
    """
    # Create JSON-RPC request with nonexistent command
    request_data = json_rpc_request.copy()
    request_data["method"] = "nonexistent_command"
    
    # Send request
    response = test_client.post("/api/jsonrpc", json=request_data)
    
    # Check response
    assert response.status_code == 400 or response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "jsonrpc" in data and data["jsonrpc"] == "2.0"
    assert "error" in data
    assert "id" in data and data["id"] == request_data["id"]
    
    # Check error content
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == -32601  # Method not found
    assert "not found" in data["error"]["message"].lower()


@pytest.mark.functional
def test_invalid_json_rpc_request(test_client: TestClient):
    """
    Test invalid JSON-RPC request.
    
    Args:
        test_client: FastAPI test client.
    """
    # Create invalid JSON-RPC request
    request_data = {
        "method": "echo",
        "params": {}
        # Missing jsonrpc and id fields
    }
    
    # Send request
    response = test_client.post("/api/jsonrpc", json=request_data)
    
    # Check response
    assert response.status_code == 400 or response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "jsonrpc" in data and data["jsonrpc"] == "2.0"
    assert "error" in data
    
    # Check error content
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == -32600  # Invalid Request


@pytest.mark.functional
def test_get_commands(test_client: TestClient, register_echo_command):
    """
    Test getting list of commands.
    
    Args:
        test_client: FastAPI test client.
        register_echo_command: Fixture to register test command.
    """
    # Send request
    response = test_client.get("/api/commands")
    
    # Check response
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "commands" in data
    assert isinstance(data["commands"], dict)
    
    # Check that echo command is in the list
    assert "echo" in data["commands"]
    assert "description" in data["commands"]["echo"]
    assert "schema" in data["commands"]["echo"]


@pytest.mark.functional
def test_health_check(test_client: TestClient):
    """
    Test health check endpoint.
    
    Args:
        test_client: FastAPI test client.
    """
    # Send request
    response = test_client.get("/health")
    
    # Check response
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


@pytest.mark.functional
def test_openapi_schema(test_client: TestClient):
    """
    Test OpenAPI schema endpoint.
    
    Args:
        test_client: FastAPI test client.
    """
    # Send request
    response = test_client.get("/openapi.json")
    
    # Check response
    assert response.status_code == 200
    
    # Check response content
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    
    # Check that API endpoints are in schema
    assert "/cmd" in data["paths"]
    assert "/api/commands" in data["paths"]
    assert "/health" in data["paths"]


@pytest.mark.functional
def test_batch_requests(test_client: TestClient, json_rpc_request: Dict[str, Any], register_echo_command):
    """
    Test batch requests processing.
    
    Args:
        test_client: FastAPI test client.
        json_rpc_request: Base JSON-RPC request.
        register_echo_command: Fixture to register test command.
    """
    # Create batch request
    request1 = json_rpc_request.copy()
    request1["method"] = "echo"
    request1["params"] = {"request_id": "1"}
    request1["id"] = "1"
    
    request2 = json_rpc_request.copy()
    request2["method"] = "echo"
    request2["params"] = {"request_id": "2"}
    request2["id"] = "2"
    
    batch_request = [request1, request2]
    
    # Send request
    response = test_client.post("/api/jsonrpc", json=batch_request)
    
    # Check response
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Check individual responses
    assert data[0]["result"]["params"] == {"request_id": "1"}
    assert data[0]["id"] == "1"
    
    assert data[1]["result"]["params"] == {"request_id": "2"}
    assert data[1]["id"] == "2"


def test_custom_openapi_schema_fields():
    """
    Test that custom title, description, and version are set in the OpenAPI schema.
    """
    from fastapi import FastAPI
    from mcp_proxy_adapter.custom_openapi import custom_openapi

    app = FastAPI(
        title="Custom Title",
        description="Custom Description",
        version="9.9.9"
    )
    schema = custom_openapi(app)
    assert schema["info"]["title"] == "Custom Title"
    assert schema["info"]["description"] == "Custom Description"
    assert schema["info"]["version"] == "9.9.9" 