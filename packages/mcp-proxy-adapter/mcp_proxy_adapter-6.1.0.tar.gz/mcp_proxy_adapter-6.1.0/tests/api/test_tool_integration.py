"""
Tests for tool_integration module.

This module contains comprehensive tests for the ToolIntegration class
and related functions to ensure 90%+ code coverage.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from mcp_proxy_adapter.api.tool_integration import ToolIntegration, generate_tool_help
from mcp_proxy_adapter.commands.command_registry import CommandRegistry


class TestToolIntegration:
    """Test cases for ToolIntegration class."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock command registry for testing."""
        registry = Mock(spec=CommandRegistry)
        
        # Mock metadata for commands
        registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command description",
                "params": {
                    "param1": {
                        "type": "строка",
                        "description": "Test parameter",
                        "required": True
                    },
                    "param2": {
                        "type": "целое число",
                        "description": "Another parameter",
                        "required": False
                    }
                },
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"param1": "value1"}
                    }
                ]
            },
            "another_command": {
                "summary": "Another test command",
                "params": {
                    "param3": {
                        "type": "логическое значение",
                        "description": "Boolean parameter",
                        "required": True
                    }
                },
                "examples": [
                    {
                        "command": "another_command",
                        "params": {"param3": True}
                    }
                ]
            }
        }
        
        return registry

    @pytest.fixture
    def mock_api_tool_description(self):
        """Mock APIToolDescription class."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock:
            mock.generate_tool_description.return_value = {
                "description": "Test tool description",
                "supported_commands": {
                    "test_command": {
                        "params": {
                            "param1": {
                                "type": "строка",
                                "description": "Test parameter"
                            }
                        }
                    }
                }
            }
            mock.generate_tool_description_text.return_value = "# Test Tool\n\nTest description"
            yield mock

    def test_generate_tool_schema_success(self, mock_registry, mock_api_tool_description):
        """Test successful tool schema generation."""
        tool_name = "test_tool"
        description = "Custom tool description"
        
        schema = ToolIntegration.generate_tool_schema(tool_name, mock_registry, description)
        
        # Verify schema structure
        assert schema["name"] == tool_name
        assert schema["description"] == description
        assert "parameters" in schema
        assert "properties" in schema["parameters"]
        assert "command" in schema["parameters"]["properties"]
        assert "params" in schema["parameters"]["properties"]
        
        # Verify command enum
        command_enum = schema["parameters"]["properties"]["command"]["enum"]
        assert "test_command" in command_enum
        
        # Verify parameter types
        param_types = schema["parameters"]["properties"]["params"]["properties"]
        assert "param1" in param_types
        assert param_types["param1"]["type"] == "string"

    def test_generate_tool_schema_without_description(self, mock_registry, mock_api_tool_description):
        """Test tool schema generation without custom description."""
        tool_name = "test_tool"
        
        schema = ToolIntegration.generate_tool_schema(tool_name, mock_registry)
        
        assert schema["description"] == "Test tool description"

    def test_generate_tool_schema_parameter_type_conversion(self, mock_registry):
        """Test parameter type conversion from Russian to JSON Schema types."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock:
            mock.generate_tool_description.return_value = {
                "description": "Test tool",
                "supported_commands": {
                    "test_command": {
                        "params": {
                            "string_param": {"type": "строка", "description": "String"},
                            "int_param": {"type": "целое число", "description": "Integer"},
                            "float_param": {"type": "число", "description": "Float"},
                            "bool_param": {"type": "логическое значение", "description": "Boolean"},
                            "array_param": {"type": "список", "description": "Array"},
                            "object_param": {"type": "объект", "description": "Object"},
                            "unknown_param": {"type": "неизвестный", "description": "Unknown"}
                        }
                    }
                }
            }
            
            schema = ToolIntegration.generate_tool_schema("test_tool", mock_registry)
            param_types = schema["parameters"]["properties"]["params"]["properties"]
            
            assert param_types["string_param"]["type"] == "string"
            assert param_types["int_param"]["type"] == "integer"
            assert param_types["float_param"]["type"] == "number"
            assert param_types["bool_param"]["type"] == "boolean"
            assert param_types["array_param"]["type"] == "array"
            assert param_types["object_param"]["type"] == "object"
            assert param_types["unknown_param"]["type"] == "string"  # Default fallback

    def test_generate_tool_documentation_markdown(self, mock_registry, mock_api_tool_description):
        """Test markdown documentation generation."""
        tool_name = "test_tool"
        
        doc = ToolIntegration.generate_tool_documentation(tool_name, mock_registry, "markdown")
        
        assert doc == "# Test Tool\n\nTest description"
        mock_api_tool_description.generate_tool_description_text.assert_called_once_with(tool_name, mock_registry)

    def test_generate_tool_documentation_html(self, mock_registry, mock_api_tool_description):
        """Test HTML documentation generation."""
        tool_name = "test_tool"
        
        doc = ToolIntegration.generate_tool_documentation(tool_name, mock_registry, "html")
        
        assert "<html>" in doc
        assert "<body>" in doc
        assert "Test Tool" in doc

    def test_generate_tool_documentation_default_format(self, mock_registry, mock_api_tool_description):
        """Test documentation generation with default format."""
        tool_name = "test_tool"
        
        doc = ToolIntegration.generate_tool_documentation(tool_name, mock_registry, "unknown")
        
        assert doc == "# Test Tool\n\nTest description"

    def test_register_external_tools_success(self, mock_registry, mock_api_tool_description):
        """Test successful external tool registration."""
        tool_names = ["tool1", "tool2"]
        
        results = ToolIntegration.register_external_tools(mock_registry, tool_names)
        
        assert len(results) == 2
        assert results["tool1"]["status"] == "success"
        assert results["tool2"]["status"] == "success"
        assert "schema" in results["tool1"]
        assert "schema" in results["tool2"]

    def test_register_external_tools_with_error(self, mock_registry):
        """Test external tool registration with error."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock:
            mock.generate_tool_description.side_effect = Exception("Test error")
            
            tool_names = ["error_tool"]
            results = ToolIntegration.register_external_tools(mock_registry, tool_names)
            
            assert results["error_tool"]["status"] == "error"
            assert "Test error" in results["error_tool"]["error"]

    def test_register_external_tools_empty_list(self, mock_registry):
        """Test external tool registration with empty list."""
        results = ToolIntegration.register_external_tools(mock_registry, [])
        
        assert results == {}

    def test_extract_parameter_types(self):
        """Test parameter type extraction."""
        commands = {
            "cmd1": {
                "params": {
                    "param1": {"type": "строка", "description": "String param"},
                    "param2": {"type": "целое число", "description": "Integer param"}
                }
            },
            "cmd2": {
                "params": {
                    "param3": {"type": "логическое значение", "description": "Boolean param"}
                }
            }
        }
        
        parameter_types = ToolIntegration._extract_parameter_types(commands)
        
        assert parameter_types["param1"]["type"] == "string"
        assert parameter_types["param2"]["type"] == "integer"
        assert parameter_types["param3"]["type"] == "boolean"
        assert parameter_types["param1"]["description"] == "String param"

    def test_extract_parameter_types_empty_commands(self):
        """Test parameter type extraction with empty commands."""
        parameter_types = ToolIntegration._extract_parameter_types({})
        
        assert parameter_types == {}

    def test_extract_parameter_types_commands_without_params(self):
        """Test parameter type extraction for commands without parameters."""
        commands = {
            "cmd1": {"params": {}},
            "cmd2": {"params": None}
        }
        
        parameter_types = ToolIntegration._extract_parameter_types(commands)
        
        assert parameter_types == {}

    def test_extract_parameter_types_missing_type(self):
        """Test parameter type extraction with missing type information."""
        commands = {
            "cmd1": {
                "params": {
                    "param1": {"description": "Param without type"}
                }
            }
        }
        
        parameter_types = ToolIntegration._extract_parameter_types(commands)
        
        assert parameter_types["param1"]["type"] == "string"  # Default fallback


class TestGenerateToolHelp:
    """Test cases for generate_tool_help function."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock command registry for testing."""
        registry = Mock(spec=CommandRegistry)
        
        registry.get_all_metadata.return_value = {
            "help": {
                "summary": "Show help information",
                "params": {
                    "command": {
                        "type": "строка",
                        "description": "Command name",
                        "required": False
                    }
                },
                "examples": [
                    {
                        "command": "help",
                        "params": {"command": "test"}
                    }
                ]
            },
            "config": {
                "summary": "Get configuration",
                "params": {
                    "section": {
                        "type": "строка",
                        "description": "Configuration section",
                        "required": True
                    }
                },
                "examples": [
                    {
                        "command": "config",
                        "params": {"section": "database"}
                    }
                ]
            }
        }
        
        return registry

    def test_generate_tool_help_success(self, mock_registry):
        """Test successful tool help generation."""
        tool_name = "test_tool"
        
        help_text = generate_tool_help(tool_name, mock_registry)
        
        # Verify basic structure
        assert f"# Инструмент {tool_name}" in help_text
        assert "Позволяет выполнять команды через JSON-RPC протокол" in help_text
        assert "## Доступные команды:" in help_text
        
        # Verify command information
        assert "### help" in help_text
        assert "Show help information" in help_text
        assert "### config" in help_text
        assert "Get configuration" in help_text
        
        # Verify parameter information
        assert "Параметры:" in help_text
        assert "command: опциональный" in help_text
        assert "section: обязательный" in help_text
        
        # Verify JSON examples
        assert "```json" in help_text
        assert '"command": "help"' in help_text
        assert '"command": "test"' in help_text

    def test_generate_tool_help_without_params(self, mock_registry):
        """Test tool help generation for commands without parameters."""
        mock_registry.get_all_metadata.return_value = {
            "simple_command": {
                "summary": "Simple command without params",
                "params": {},
                "examples": [
                    {
                        "command": "simple_command",
                        "params": {}
                    }
                ]
            }
        }
        
        help_text = generate_tool_help("test_tool", mock_registry)
        
        assert "### simple_command" in help_text
        assert "Simple command without params" in help_text
        # Should not contain "Параметры:" section for commands without params

    def test_generate_tool_help_without_examples(self, mock_registry):
        """Test tool help generation for commands without examples."""
        mock_registry.get_all_metadata.return_value = {
            "no_example_command": {
                "summary": "Command without examples",
                "params": {
                    "param1": {
                        "type": "строка",
                        "description": "Test parameter",
                        "required": True
                    }
                },
                "examples": []
            }
        }
        
        help_text = generate_tool_help("test_tool", mock_registry)
        
        assert "### no_example_command" in help_text
        assert "Command without examples" in help_text
        # Should not contain JSON example section

    def test_generate_tool_help_empty_registry(self, mock_registry):
        """Test tool help generation with empty command registry."""
        mock_registry.get_all_metadata.return_value = {}
        
        help_text = generate_tool_help("test_tool", mock_registry)
        
        assert "## Доступные команды:" in help_text
        # Should not contain any command sections

    def test_generate_tool_help_with_none_params(self, mock_registry):
        """Test tool help generation with None params."""
        mock_registry.get_all_metadata.return_value = {
            "command": {
                "summary": "Test command",
                "params": None,
                "examples": []
            }
        }
        
        help_text = generate_tool_help("test_tool", mock_registry)
        
        assert "### command" in help_text
        # Should handle None params gracefully

    def test_generate_tool_help_with_missing_examples(self, mock_registry):
        """Test tool help generation with missing examples key."""
        mock_registry.get_all_metadata.return_value = {
            "command": {
                "summary": "Test command",
                "params": {}
            }
        }
        
        help_text = generate_tool_help("test_tool", mock_registry)
        
        assert "### command" in help_text
        # Should handle missing examples key gracefully


class TestToolIntegrationEdgeCases:
    """Test edge cases and error conditions."""

    def test_generate_tool_schema_with_none_registry(self):
        """Test tool schema generation with None registry."""
        with pytest.raises(AttributeError):
            ToolIntegration.generate_tool_schema("test_tool", None)

    def test_generate_tool_documentation_with_none_registry(self):
        """Test documentation generation with None registry."""
        with pytest.raises(AttributeError):
            ToolIntegration.generate_tool_documentation("test_tool", None)

    def test_register_external_tools_with_none_registry(self):
        """Test external tool registration with None registry."""
        # This should handle None gracefully and return error status
        results = ToolIntegration.register_external_tools(None, ["tool1"])
        assert "tool1" in results
        assert results["tool1"]["status"] == "error"
        assert "get_all_metadata" in results["tool1"]["error"]

    def test_generate_tool_help_with_none_registry(self):
        """Test tool help generation with None registry."""
        with pytest.raises(AttributeError):
            generate_tool_help("test_tool", None)

    @patch('mcp_proxy_adapter.api.tool_integration.logger')
    def test_register_external_tools_logging(self, mock_logger):
        """Test that logging is called during tool registration."""
        mock_registry = Mock(spec=CommandRegistry)
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock:
            mock.generate_tool_description.return_value = {
                "description": "Test tool",
                "supported_commands": {}
            }
            
            ToolIntegration.register_external_tools(mock_registry, ["test_tool"])
            
            # Verify info log for successful registration
            mock_logger.info.assert_called_with("Successfully registered tool: test_tool")

    @patch('mcp_proxy_adapter.api.tool_integration.logger')
    def test_register_external_tools_error_logging(self, mock_logger):
        """Test that error logging is called during failed tool registration."""
        mock_registry = Mock(spec=CommandRegistry)
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock:
            mock.generate_tool_description.side_effect = Exception("Test error")
            
            ToolIntegration.register_external_tools(mock_registry, ["error_tool"])
            
            # Verify debug log for error
            mock_logger.debug.assert_called_with("Error registering tool error_tool: Test error")


class TestToolIntegrationIntegration:
    """Integration tests for ToolIntegration class."""

    @pytest.fixture
    def real_registry(self):
        """Create a real command registry for integration testing."""
        from mcp_proxy_adapter.commands.command_registry import CommandRegistry
        from mcp_proxy_adapter.commands.base import Command
        
        registry = CommandRegistry()
        
        # Create a proper mock that inherits from Command
        class MockCommand(Command):
            name = "integration_test"
            
            @classmethod
            def get_metadata(cls):
                return {
                    "summary": "Integration test command",
                    "description": "Integration test command description",
                    "params": {
                        "test_param": {
                            "type": "строка",
                            "description": "Test parameter",
                            "required": True
                        }
                    },
                    "examples": [
                        {
                            "command": "integration_test",
                            "params": {"test_param": "value"}
                        }
                    ]
                }
            
            async def execute(self, **kwargs):
                return {"result": "test"}
        
        registry.register_custom(MockCommand())
        
        return registry

    def test_integration_generate_tool_schema(self, real_registry):
        """Integration test for tool schema generation with real registry."""
        schema = ToolIntegration.generate_tool_schema("integration_tool", real_registry)
        
        assert schema["name"] == "integration_tool"
        assert "parameters" in schema
        assert "properties" in schema["parameters"]

    def test_integration_generate_tool_documentation(self, real_registry):
        """Integration test for tool documentation generation with real registry."""
        doc = ToolIntegration.generate_tool_documentation("integration_tool", real_registry)
        
        assert "integration_tool" in doc.lower()

    def test_integration_generate_tool_help(self, real_registry):
        """Integration test for tool help generation with real registry."""
        help_text = generate_tool_help("integration_tool", real_registry)
        
        assert "Инструмент integration_tool" in help_text
        assert "integration_test" in help_text 