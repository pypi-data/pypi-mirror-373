"""
Tests for JSON-RPC batch requests handling.
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch, MagicMock

from mcp_proxy_adapter.api.handlers import handle_json_rpc, handle_batch_json_rpc
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.core.errors import NotFoundError, MicroserviceError


@pytest.fixture
def success_result():
    """Fixture for test success result."""
    result = SuccessResult(data={"key": "value"}, message="Success")
    return result


class TestBatchJsonRpc:
    """Tests for JSON-RPC batch requests handling."""
    
    @pytest.mark.asyncio
    @patch("mcp_proxy_adapter.api.handlers.handle_json_rpc")
    async def test_batch_request_processing(self, mock_handle_json_rpc):
        """Test handling of batch requests."""
        # Setup handle_json_rpc mock to return different responses
        mock_handle_json_rpc.side_effect = [
            # First request - success
            {
                "jsonrpc": "2.0",
                "result": {"key1": "value1"},
                "id": "1"
            },
            # Second request - error
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                },
                "id": "2"
            },
            # Third request - success
            {
                "jsonrpc": "2.0",
                "result": {"key3": "value3"},
                "id": "3"
            }
        ]
        
        # Create batch request
        batch_request = [
            {"jsonrpc": "2.0", "method": "method1", "params": {"p1": "v1"}, "id": "1"},
            {"jsonrpc": "2.0", "method": "non_existent", "id": "2"},
            {"jsonrpc": "2.0", "method": "method3", "params": {"p3": "v3"}, "id": "3"}
        ]
        
        # Process batch request
        responses = await handle_batch_json_rpc(batch_request)
        
        # Assertions
        assert len(responses) == 3
        assert mock_handle_json_rpc.call_count == 3
        
        # Check first response
        assert responses[0]["jsonrpc"] == "2.0"
        assert responses[0]["result"] == {"key1": "value1"}
        assert responses[0]["id"] == "1"
        
        # Check second response (error)
        assert responses[1]["jsonrpc"] == "2.0"
        assert responses[1]["error"]["code"] == -32601
        assert responses[1]["id"] == "2"
        
        # Check third response
        assert responses[2]["jsonrpc"] == "2.0"
        assert responses[2]["result"] == {"key3": "value3"}
        assert responses[2]["id"] == "3"
    
    @pytest.mark.asyncio
    @patch("mcp_proxy_adapter.api.handlers.handle_json_rpc")
    async def test_empty_batch_request(self, mock_handle_json_rpc):
        """Test handling of empty batch request."""
        # Create empty batch request
        batch_request = []
        
        # Process batch request
        responses = await handle_batch_json_rpc(batch_request)
        
        # Assertions
        assert len(responses) == 0
        assert mock_handle_json_rpc.call_count == 0
    
    @pytest.mark.asyncio
    @patch("mcp_proxy_adapter.api.handlers.execute_command")
    async def test_end_to_end_batch_processing(self, mock_execute_command, success_result):
        """Test end-to-end processing of batch requests."""
        # Setup execute_command mock
        mock_execute_command.return_value = success_result.to_dict()
        
        # Create batch request
        batch_request = [
            {"jsonrpc": "2.0", "method": "method1", "params": {"p1": "v1"}, "id": "1"},
            {"jsonrpc": "2.0", "method": "method2", "params": {"p2": "v2"}, "id": "2"}
        ]
        
        # Process batch request
        responses = await handle_batch_json_rpc(batch_request)
        
        # Assertions
        assert len(responses) == 2
        for response in responses:
            assert response["jsonrpc"] == "2.0"
            assert "result" in response
            assert "error" not in response 