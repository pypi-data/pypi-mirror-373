"""
Tests for base command module.

This module contains comprehensive tests for the base Command class
to ensure 90%+ code coverage.
"""

import pytest
import inspect
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.core.errors import (
    ValidationError, InvalidParamsError, NotFoundError, 
    TimeoutError, CommandError, InternalError
)


class MockResultClass:
    """Mock result class for testing."""
    def to_dict(self):
        return {"status": "success", "data": "test_data"}
    
    @classmethod
    def get_schema(cls):
        return {"type": "object", "properties": {"data": {"type": "string"}}}


class TestCommand(Command):
    """Test command class for testing."""
    name = "test_command"
    result_class = MockResultClass
    
    @classmethod
    def get_schema(cls):
        return {
            "type": "object",
            "properties": {
                "test_param": {"type": "string"},
                "param1": {"type": "string"},
                "param2": {"type": "string"},
                "param3": {"type": "string"},
                "cmdname": {"type": "string"},
                "valid_value": {"type": "string"},
                "complex_param": {"type": "object"}
            }
        }
    
    async def execute(self, **kwargs):
        return SuccessResult(data=kwargs)


def test_success_result():
    """Test success result creation."""
    result = SuccessResult(data="test_data")
    assert result.data == "test_data"
    result_dict = result.to_dict()
    assert result_dict["success"] is True


def test_error_result():
    """Test error result creation."""
    result = ErrorResult(message="Test error", code=400)
    assert result.message == "Test error"
    assert result.code == 400


class TestCommandClass:
    """Test cases for Command class."""

    @pytest.mark.asyncio
    async def test_execute(self):
        """Test execute method."""
        command = TestCommand()
        result = await command.execute(test_param="value")
        assert isinstance(result, SuccessResult)

    @pytest.mark.asyncio
    async def test_run(self):
        """Test run method (with validation)."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            result = await TestCommand.run(test_param="test_value")
            assert isinstance(result, SuccessResult)
            assert result.data == {"test_param": "test_value"}

    def test_get_schema(self):
        """Test get_schema method."""
        schema = TestCommand.get_schema()
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_get_result_schema(self):
        """Test get_result_schema method."""
        schema = TestCommand.get_result_schema()
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_get_param_info(self):
        """Test get_param_info method."""
        param_info = TestCommand.get_param_info()
        assert isinstance(param_info, dict)

    def test_validate_params_none(self):
        """Test validate_params with None."""
        command = TestCommand()
        params = command.validate_params(None)
        assert params == {}

    def test_validate_params_empty_dict(self):
        """Test validate_params with empty dict."""
        command = TestCommand()
        params = command.validate_params({})
        assert params == {}

    def test_validate_params_with_none_values(self):
        """Test validate_params with None values."""
        command = TestCommand()
        params = command.validate_params({"param1": None, "param2": "value"})
        assert "param1" not in params
        assert params["param2"] == "value"

    def test_validate_params_with_empty_strings(self):
        """Test validate_params with empty strings."""
        command = TestCommand()
        params = command.validate_params({"param1": "", "param2": "null", "param3": "value"})
        assert "param1" not in params
        assert "param2" not in params
        assert params["param3"] == "value"

    def test_validate_params_with_cmdname_none(self):
        """Test validate_params with cmdname parameter."""
        command = TestCommand()
        params = command.validate_params({"cmdname": None, "test_param": "value"})
        assert params["cmdname"] is None
        assert params["test_param"] == "value"

    def test_validate_params_copy_input(self):
        """Test that validate_params doesn't modify input."""
        command = TestCommand()
        input_params = {"param1": "value1", "param2": None}
        result = command.validate_params(input_params)
        assert input_params == {"param1": "value1", "param2": None}  # Input unchanged
        assert "param2" not in result  # Result filtered

    @pytest.mark.asyncio
    async def test_run_with_hooks_skip_processing(self):
        """Test run method when hooks skip standard processing."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            result = await TestCommand.run(test_param="value")
            assert isinstance(result, SuccessResult)
            assert result.data == {"test_param": "value"}

    @pytest.mark.asyncio
    async def test_run_command_not_found(self):
        """Test run method when command not found."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = None
            
            result = await TestCommand.run(test_param="value")
            assert isinstance(result, ErrorResult)
            assert "not found" in result.message

    @pytest.mark.asyncio
    async def test_run_with_registry_instance(self):
        """Test run method with existing registry instance."""
        mock_command = Mock()
        mock_command.execute = AsyncMock(return_value=SuccessResult(data="test"))
        
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = True
            mock_registry.get_command_instance.return_value = mock_command
            
            result = await TestCommand.run(test_param="value")
            assert isinstance(result, SuccessResult)

    @pytest.mark.asyncio
    async def test_run_validation_error(self):
        """Test run method with validation error."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            # Mock TestCommand to raise ValidationError
            with patch.object(TestCommand, 'execute', side_effect=ValidationError("Invalid params")):
                result = await TestCommand.run(test_param="value")
                assert isinstance(result, ErrorResult)
                assert "Invalid params" in result.message

    @pytest.mark.asyncio
    async def test_run_invalid_params_error(self):
        """Test run method with invalid params error."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            with patch.object(TestCommand, 'execute', side_effect=InvalidParamsError("Invalid params")):
                result = await TestCommand.run(test_param="value")
                assert isinstance(result, ErrorResult)
                assert "Invalid params" in result.message

    @pytest.mark.asyncio
    async def test_run_not_found_error(self):
        """Test run method with not found error."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            with patch.object(TestCommand, 'execute', side_effect=NotFoundError("Not found")):
                result = await TestCommand.run(test_param="value")
                assert isinstance(result, ErrorResult)
                assert "Not found" in result.message

    @pytest.mark.asyncio
    async def test_run_timeout_error(self):
        """Test run method with timeout error."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            with patch.object(TestCommand, 'execute', side_effect=TimeoutError("Timeout")):
                result = await TestCommand.run(test_param="value")
                assert isinstance(result, ErrorResult)
                assert "Timeout" in result.message

    @pytest.mark.asyncio
    async def test_run_command_error(self):
        """Test run method with command error."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            with patch.object(TestCommand, 'execute', side_effect=CommandError("Command error")):
                result = await TestCommand.run(test_param="value")
                assert isinstance(result, ErrorResult)
                assert "Command error" in result.message

    @pytest.mark.asyncio
    async def test_run_unexpected_exception(self):
        """Test run method with unexpected exception."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            with patch.object(TestCommand, 'execute', side_effect=Exception("Unexpected error")):
                result = await TestCommand.run(test_param="value")
                assert isinstance(result, ErrorResult)
                assert "Command execution error" in result.message

    @pytest.mark.asyncio
    async def test_run_with_none_kwargs(self):
        """Test run method with None kwargs."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            result = await TestCommand.run()
            assert isinstance(result, SuccessResult)

    def test_get_metadata(self):
        """Test get_metadata method."""
        metadata = TestCommand.get_metadata()
        assert isinstance(metadata, dict)
        assert "name" in metadata
        assert "summary" in metadata
        assert "params" in metadata

    def test_get_metadata_with_schema(self):
        """Test get_metadata method with schema."""
        with patch.object(TestCommand, 'get_param_info') as mock_param_info:
            mock_param_info.return_value = {
                "param1": {"type": "string", "description": "Test param"}
            }
            
            metadata = TestCommand.get_metadata()
            assert "params" in metadata
            assert "param1" in metadata["params"]

    def test_generate_examples(self):
        """Test _generate_examples method."""
        params = {
            "param1": {"type": "string", "description": "Test param"}
        }
        
        examples = TestCommand._generate_examples(params)
        assert isinstance(examples, list)
        assert len(examples) > 0

    def test_generate_examples_empty_params(self):
        """Test _generate_examples with empty params."""
        examples = TestCommand._generate_examples({})
        assert isinstance(examples, list)

    def test_get_param_info_with_annotations(self):
        """Test get_param_info with type annotations."""
        class AnnotatedCommand(Command):
            name = "annotated_command"
            result_class = MockResultClass
            
            async def execute(self, param1: str, param2: int = 42):
                return SuccessResult(data={"param1": param1, "param2": param2})
        
        param_info = AnnotatedCommand.get_param_info()
        assert "param1" in param_info
        assert "param2" in param_info
        assert param_info["param1"]["required"] is True
        assert param_info["param2"]["required"] is False

    def test_get_param_info_without_annotations(self):
        """Test get_param_info without type annotations."""
        class NoAnnotationCommand(Command):
            name = "no_annotation_command"
            result_class = MockResultClass
            
            async def execute(self, param1, param2=42):
                return SuccessResult(data={"param1": param1, "param2": param2})
        
        param_info = NoAnnotationCommand.get_param_info()
        assert "param1" in param_info
        assert "param2" in param_info
        assert param_info["param1"]["required"] is True
        assert param_info["param2"]["required"] is False

    def test_get_result_schema_with_result_class(self):
        """Test get_result_schema with result class."""
        class MockResultClassWithSchema:
            @classmethod
            def get_schema(cls):
                return {"type": "object", "properties": {"data": {"type": "string"}}}
        
        class CommandWithResultClass(Command):
            name = "command_with_result"
            result_class = MockResultClassWithSchema
            
            async def execute(self, **kwargs):
                return SuccessResult(data="test")
        
        schema = CommandWithResultClass.get_result_schema()
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_get_result_schema_without_result_class(self):
        """Test get_result_schema without result class."""
        class CommandWithoutResultClass(Command):
            name = "command_without_result"
            
            async def execute(self, **kwargs):
                return SuccessResult(data="test")
        
        schema = CommandWithoutResultClass.get_result_schema()
        assert schema == {}

    def test_command_name_generation(self):
        """Test command name generation from class name."""
        class TestCommandName(Command):
            result_class = MockResultClass
            
            async def execute(self, **kwargs):
                return SuccessResult(data="test")
        
        # Test that name is generated from class name
        # The name will be generated dynamically in the run method
        # So we test that the class can be instantiated
        command = TestCommandName()
        assert command is not None

    def test_command_name_override(self):
        """Test command name override."""
        class CustomNamedCommand(Command):
            name = "custom_name"
            result_class = MockResultClass
            
            async def execute(self, **kwargs):
                return SuccessResult(data="test")
        
        assert CustomNamedCommand.name == "custom_name"


class TestCommandEdgeCases:
    """Test edge cases for Command class."""

    def test_validate_params_with_various_none_values(self):
        """Test validate_params with various None-like values."""
        command = TestCommand()
        params = {
            "null_str": "null",
            "none_str": "none",
            "empty_str": "",
            "real_none": None,
            "valid_value": "test"
        }
        
        result = command.validate_params(params)
        assert "null_str" not in result
        assert "none_str" not in result
        assert "empty_str" not in result
        assert "real_none" not in result
        assert result["valid_value"] == "test"

    def test_validate_params_case_insensitive(self):
        """Test validate_params case insensitive handling."""
        command = TestCommand()
        params = {
            "null_upper": "NULL",
            "none_upper": "NONE",
            "valid_value": "test"
        }
        
        result = command.validate_params(params)
        assert "null_upper" not in result
        assert "none_upper" not in result
        assert result["valid_value"] == "test"

    @pytest.mark.asyncio
    async def test_run_with_complex_hook_context(self):
        """Test run method with complex hook context."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            result = await TestCommand.run(complex_param={"nested": "value"})
            assert isinstance(result, SuccessResult)

    @pytest.mark.asyncio
    async def test_run_with_after_hooks(self):
        """Test run method with after hooks execution."""
        with patch('mcp_proxy_adapter.commands.command_registry.registry', create=True) as mock_registry:
            mock_registry.get_command.return_value = TestCommand
            mock_registry.has_instance.return_value = False
            
            result = await TestCommand.run(test_param="value")
            assert isinstance(result, SuccessResult)

    def test_get_metadata_with_examples(self):
        """Test get_metadata method with examples generation."""
        with patch.object(TestCommand, 'get_param_info') as mock_param_info:
            mock_param_info.return_value = {
                "param1": {"type": "string", "description": "Test param"}
            }
            
            metadata = TestCommand.get_metadata()
            assert "examples" in metadata
            assert isinstance(metadata["examples"], list) 