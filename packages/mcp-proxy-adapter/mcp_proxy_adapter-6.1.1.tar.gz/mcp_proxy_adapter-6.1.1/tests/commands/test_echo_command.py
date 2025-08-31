"""
Tests for the echo command.
"""

import pytest
import asyncio
from typing import Dict, Any
import json

from tests.stubs.echo_command import EchoCommand
from tests.stubs.echo_command import EchoResult


@pytest.mark.unit
def test_echo_command_execution():
    """
    Test execution of echo command.
    """
    # Create test parameters
    test_params = {
        "string_param": "test_value",
        "int_param": 42,
        "bool_param": True,
        "complex_param": {"nested": "value", "array": [1, 2, 3]}
    }
    
    # Create and execute command
    command = EchoCommand()
    result = asyncio.run(command.execute(**test_params))
    
    # Check result type
    assert isinstance(result, EchoResult)
    
    # Check result content
    assert result.params == test_params
    assert result.params["string_param"] == "test_value"
    assert result.params["int_param"] == 42
    assert result.params["bool_param"] is True
    assert result.params["complex_param"]["nested"] == "value"
    assert result.params["complex_param"]["array"] == [1, 2, 3]


@pytest.mark.unit
def test_echo_result_serialization():
    """
    Test serialization of echo result.
    """
    # Create test parameters
    test_params = {
        "string_param": "test_value",
        "int_param": 42,
        "bool_param": True,
        "complex_param": {"nested": "value", "array": [1, 2, 3]}
    }
    
    # Create result
    result = EchoResult(params=test_params)
    
    # Test to_dict method
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert "params" in result_dict
    assert result_dict["params"] == test_params
    
    # Test that result can be properly serialized to JSON
    json_str = json.dumps(result_dict)
    parsed_json = json.loads(json_str)
    assert parsed_json == result_dict


@pytest.mark.unit
def test_echo_command_schema():
    """
    Test command schema generation.
    """
    # Get schema
    schema = EchoCommand.get_schema()
    
    # Check schema structure
    assert isinstance(schema, dict)
    assert "type" in schema and schema["type"] == "object"
    assert "additionalProperties" in schema and schema["additionalProperties"] is True
    assert "description" in schema


@pytest.mark.unit
def test_echo_result_schema():
    """
    Test result schema generation.
    """
    # Get schema
    schema = EchoResult.get_schema()
    
    # Check schema structure
    assert isinstance(schema, dict)
    assert "type" in schema and schema["type"] == "object"
    assert "properties" in schema
    assert "params" in schema["properties"]
    assert "required" in schema and "params" in schema["required"]
    assert schema["properties"]["params"]["type"] == "object"
    assert schema["properties"]["params"]["additionalProperties"] is True


@pytest.mark.unit
def test_echo_result_from_dict():
    """
    Test creating result from dictionary.
    """
    # Create test data
    test_data = {
        "params": {
            "key1": "value1",
            "key2": 42
        }
    }
    
    # Create result from dict
    result = EchoResult.from_dict(test_data)
    
    # Check result
    assert isinstance(result, EchoResult)
    assert result.params == test_data["params"]
    
    # Test with empty params
    empty_result = EchoResult.from_dict({})
    assert isinstance(empty_result, EchoResult)
    assert empty_result.params == {} 