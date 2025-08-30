"""
Tests for the help command.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.commands.help_command import HelpCommand, HelpResult
from mcp_proxy_adapter.core.errors import NotFoundError


@pytest.fixture
def mock_registry():
    """Mock for command registry."""
    with patch("mcp_proxy_adapter.commands.help_command.registry") as mock_reg:
        yield mock_reg


@pytest.mark.asyncio
async def test_help_command_without_params(mock_registry):
    """Test help command without parameters."""
    # Setup mocks
    mock_registry.get_all_metadata.return_value = {
        "help": {
            "name": "help",
            "summary": "Get help information",
            "description": "Get help information",
            "params": {},
            "examples": []
        },
        "health": {
            "name": "health",
            "summary": "Check server health",
            "description": "Check server health",
            "params": {},
            "examples": []
        }
    }
    
    # Execute command
    command = HelpCommand()
    result = await command.execute()
    
    # Check result
    assert isinstance(result, HelpResult)
    assert result.commands_info is not None
    assert result.command_info is None
    
    # Check content
    commands_dict = result.to_dict()
    assert "commands" in commands_dict
    assert "help" in commands_dict["commands"]
    assert "health" in commands_dict["commands"]
    assert "summary" in commands_dict["commands"]["help"]
    assert "Get help information" in commands_dict["commands"]["help"]["summary"]


@pytest.mark.asyncio
async def test_help_command_with_cmdname(mock_registry):
    """Test help command with cmdname parameter."""
    # Setup mocks
    mock_registry.get_command_metadata.return_value = {
        "name": "health",
        "description": "Check server health",
        "summary": "Check server health",
        "params": {
            "check_type": {
                "type": "string",
                "description": "Type of health check",
                "required": False,
                "default": "basic"
            }
        },
        "examples": []
    }
    
    # Execute command
    command = HelpCommand()
    result = await command.execute(cmdname="health")
    
    # Check result
    assert isinstance(result, HelpResult)
    assert result.commands_info is None
    assert result.command_info is not None
    
    # Check content
    command_dict = result.to_dict()
    assert "cmdname" in command_dict
    assert command_dict["cmdname"] == "health"
    assert "info" in command_dict
    assert "description" in command_dict["info"]
    assert "Check server health" in command_dict["info"]["description"]
    assert "params" in command_dict["info"]
    assert "check_type" in command_dict["info"]["params"]


@pytest.mark.asyncio
async def test_help_command_with_invalid_cmdname(mock_registry):
    """Test help command with invalid cmdname parameter."""
    # Setup mocks
    mock_registry.get_command_metadata.side_effect = NotFoundError("Command not found")
    
    # Execute command and check result fields
    command = HelpCommand()
    result = await command.execute(cmdname="non_existent")
    result_dict = result.to_dict()
    assert "error" in result_dict
    assert "example" in result_dict
    assert "note" in result_dict
    assert result_dict["error"].startswith("Command")
    assert result_dict["example"]["command"] == "help"


def test_help_result_schema():
    """Test help command result schema."""
    schema = HelpResult.get_schema()
    
    assert schema["type"] == "object"
    assert "oneOf" in schema
    assert len(schema["oneOf"]) == 2
    
    commands_schema = schema["oneOf"][0]
    assert "properties" in commands_schema
    assert "commands" in commands_schema["properties"]
    
    command_schema = schema["oneOf"][1]
    assert "properties" in command_schema
    assert "cmdname" in command_schema["properties"]
    assert "info" in command_schema["properties"]


def test_help_command_schema():
    """Test help command schema."""
    schema = HelpCommand.get_schema()
    
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "cmdname" in schema["properties"]
    assert schema["properties"]["cmdname"]["type"] == "string" 