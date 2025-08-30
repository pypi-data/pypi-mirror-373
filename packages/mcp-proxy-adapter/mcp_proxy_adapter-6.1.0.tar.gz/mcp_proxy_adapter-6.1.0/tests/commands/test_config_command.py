"""
Unit tests for config command.
"""

import json
import os
import tempfile
from typing import Generator

import pytest

from mcp_proxy_adapter.commands.config_command import ConfigCommand, ConfigResult
from config import Config


@pytest.fixture
def temp_config_file() -> Generator[str, None, None]:
    """
    Creates temporary configuration file for tests.
    
    Returns:
        Path to temporary configuration file.
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=".json")
    
    # Write test configuration
    test_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8000
        },
        "logging": {
            "level": "DEBUG",
            "file": "test.log"
        },
        "test_section": {
            "test_key": "test_value",
            "nested": {
                "key1": "value1",
                "key2": 42
            }
        }
    }
    
    with os.fdopen(fd, "w") as f:
        json.dump(test_config, f)
    
    yield path
    
    # Remove temporary file after tests
    os.unlink(path)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_command_get_all(temp_config_file: str):
    """
    Test getting all configuration values.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    # Create config instance with test file
    config_instance = Config(temp_config_file)
    
    # Create command with this config
    command = ConfigCommand()
    
    # Override the config instance used in the command
    from mcp_proxy_adapter.commands import config_command
    original_config = config_command.config_instance
    config_command.config_instance = config_instance
    
    try:
        # Execute command with get operation and no path
        result = await command.execute(operation="get")
        
        # Check result
        assert isinstance(result, ConfigResult)
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert "data" in result_dict
        assert "config" in result_dict["data"]
        assert "operation" in result_dict["data"]
        assert result_dict["data"]["operation"] == "get"
        
        # Check all config values are present
        config_data = result_dict["data"]["config"]
        assert "server" in config_data
        assert "logging" in config_data
        assert "test_section" in config_data
        
        assert config_data["server"]["host"] == "127.0.0.1"
        assert config_data["logging"]["level"] == "DEBUG"
        assert config_data["test_section"]["test_key"] == "test_value"
    finally:
        # Restore original config instance
        config_command.config_instance = original_config


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_command_get_specific(temp_config_file: str):
    """
    Test getting specific configuration value.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    # Create config instance with test file
    config_instance = Config(temp_config_file)
    
    # Create command with this config
    command = ConfigCommand()
    
    # Override the config instance used in the command
    from mcp_proxy_adapter.commands import config_command
    original_config = config_command.config_instance
    config_command.config_instance = config_instance
    
    try:
        # Execute command with get operation and specific path
        result = await command.execute(operation="get", path="server.host")
        
        # Check result
        assert isinstance(result, ConfigResult)
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert "data" in result_dict
        assert "config" in result_dict["data"]
        assert "operation" in result_dict["data"]
        assert result_dict["data"]["operation"] == "get"
        
        # Check specific config value
        config_data = result_dict["data"]["config"]
        assert "server.host" in config_data
        assert config_data["server.host"] == "127.0.0.1"
    finally:
        # Restore original config instance
        config_command.config_instance = original_config


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_command_set_value(temp_config_file: str):
    """
    Test setting configuration value.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    # Create config instance with test file
    config_instance = Config(temp_config_file)
    
    # Create command with this config
    command = ConfigCommand()
    
    # Override the config instance used in the command
    from mcp_proxy_adapter.commands import config_command
    original_config = config_command.config_instance
    config_command.config_instance = config_instance
    
    try:
        # Execute command with set operation
        result = await command.execute(
            operation="set", 
            path="server.host", 
            value="localhost"
        )
        
        # Check result
        assert isinstance(result, ConfigResult)
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert "data" in result_dict
        assert "config" in result_dict["data"]
        assert "operation" in result_dict["data"]
        assert result_dict["data"]["operation"] == "set"
        
        # Check updated config value
        config_data = result_dict["data"]["config"]
        assert "server.host" in config_data
        assert config_data["server.host"] == "localhost"
        
        # Check that value was updated in config instance
        assert config_instance.get("server.host") == "localhost"
    finally:
        # Restore original config instance
        config_command.config_instance = original_config


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_command_validate_schema():
    """
    Test validation schema for config command.
    """
    command = ConfigCommand()
    schema = command.get_schema()
    
    # Check schema structure
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "operation" in schema["properties"]
    assert "path" in schema["properties"]
    assert "value" in schema["properties"]
    
    # Check operation property
    operation_prop = schema["properties"]["operation"]
    assert operation_prop["type"] == "string"
    assert "enum" in operation_prop
    assert "get" in operation_prop["enum"]
    assert "set" in operation_prop["enum"]
    assert operation_prop["default"] == "get" 