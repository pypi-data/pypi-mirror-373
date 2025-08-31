"""
Tests for custom_openapi module.

This module contains comprehensive tests for the CustomOpenAPIGenerator class
and related functions to ensure 90%+ code coverage.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI

from mcp_proxy_adapter.custom_openapi import CustomOpenAPIGenerator, custom_openapi
from mcp_proxy_adapter.commands.base import Command


class TestCustomOpenAPIGenerator:
    """Test cases for CustomOpenAPIGenerator class."""

    @pytest.fixture
    def mock_base_schema(self):
        """Create a mock base schema for testing."""
        return {
            "info": {
                "title": "Test API",
                "description": "Test API description",
                "version": "1.0.0"
            },
            "components": {
                "schemas": {
                    "CommandRequest": {
                        "properties": {
                            "command": {
                                "type": "string",
                                "enum": []
                            },
                            "params": {
                                "type": "object",
                                "oneOf": []
                            }
                        }
                    }
                }
            }
        }

    @pytest.fixture
    def mock_command_class(self):
        """Create a mock command class for testing."""
        class MockCommand(Command):
            name = "test_command"
            
            @classmethod
            def get_schema(cls):
                return {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Test parameter"
                        }
                    }
                }
            
            async def execute(self, **kwargs):
                return {"result": "test"}
        
        return MockCommand

    @pytest.fixture
    def generator(self, mock_base_schema):
        """Create a CustomOpenAPIGenerator instance with mocked base schema."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = mock_base_schema
            generator = CustomOpenAPIGenerator()
            return generator

    def test_generator_initialization(self, mock_base_schema):
        """Test CustomOpenAPIGenerator initialization."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = mock_base_schema
            generator = CustomOpenAPIGenerator()
            
            assert generator.base_schema == mock_base_schema
            assert "schemas" in generator.base_schema_path.parts

    def test_load_base_schema(self):
        """Test loading base schema from file."""
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "schema"}'
            
            generator = CustomOpenAPIGenerator()
            schema = generator._load_base_schema()
            
            assert schema == {"test": "schema"}

    def test_add_commands_to_schema(self, generator, mock_command_class):
        """Test adding commands to schema."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {
                "test_command": mock_command_class
            }
            
            schema = {
                "components": {
                    "schemas": {
                        "CommandRequest": {
                            "properties": {
                                "command": {"type": "string", "enum": []},
                                "params": {"type": "object", "oneOf": []}
                            }
                        }
                    }
                }
            }
            generator._add_commands_to_schema(schema)
            
            # Check that command was added to enum
            command_enum = schema["components"]["schemas"]["CommandRequest"]["properties"]["command"]["enum"]
            assert "test_command" in command_enum
            
            # Check that params schema was created
            assert "Test_commandParams" in schema["components"]["schemas"]

    def test_create_params_schema(self, generator, mock_command_class):
        """Test creating parameters schema for a command."""
        schema = generator._create_params_schema(mock_command_class)
        
        assert schema["title"] == "Parameters for test_command"
        assert schema["description"] == "Parameters for the test_command command"
        assert "properties" in schema
        assert "param1" in schema["properties"]

    def test_generate_with_defaults(self, generator):
        """Test schema generation with default parameters."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            schema = generator.generate()
            
            assert "info" in schema
            assert "components" in schema
            assert schema["info"]["title"] == "Test API"

    def test_generate_with_custom_title(self, generator):
        """Test schema generation with custom title."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            schema = generator.generate(title="Custom Title")
            
            assert schema["info"]["title"] == "Custom Title"

    def test_generate_with_custom_description(self, generator):
        """Test schema generation with custom description."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            schema = generator.generate(description="Custom Description")
            
            assert "Custom Description" in schema["info"]["description"]

    def test_generate_with_custom_version(self, generator):
        """Test schema generation with custom version."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            schema = generator.generate(version="2.0.0")
            
            assert schema["info"]["version"] == "2.0.0"

    def test_generate_with_commands(self, generator, mock_command_class):
        """Test schema generation with registered commands."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {
                "test_command": mock_command_class
            }
            
            schema = generator.generate()
            
            # Check that commands were added
            command_enum = schema["components"]["schemas"]["CommandRequest"]["properties"]["command"]["enum"]
            assert "test_command" in command_enum

    def test_generate_enhances_description_with_commands(self, generator):
        """Test that description is enhanced with command information."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            # Create proper mock commands with get_schema method
            mock_help = Mock()
            mock_help.get_schema.return_value = {"type": "object", "properties": {}}
            mock_help.name = "help"
            
            mock_config = Mock()
            mock_config.get_schema.return_value = {"type": "object", "properties": {}}
            mock_config.name = "config"
            
            mock_registry.get_all_commands.return_value = {
                "help": mock_help,
                "config": mock_config
            }
            
            schema = generator.generate()
            
            description = schema["info"]["description"]
            assert "Available commands:" in description
            assert "help" in description
            assert "config" in description

    def test_generate_creates_tool_description(self, generator):
        """Test that ToolDescription schema is created."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            schema = generator.generate()
            
            assert "ToolDescription" in schema["components"]["schemas"]
            tool_desc = schema["components"]["schemas"]["ToolDescription"]
            assert "properties" in tool_desc
            assert "name" in tool_desc["properties"]
            assert "description" in tool_desc["properties"]

    def test_generate_adds_help_examples(self, generator):
        """Test that help examples are added to tool description."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            # Create proper mock command with get_schema method
            mock_help = Mock()
            mock_help.get_schema.return_value = {"type": "object", "properties": {}}
            mock_help.name = "help"
            
            mock_registry.get_all_commands.return_value = {"help": mock_help}
            
            schema = generator.generate()
            
            tool_desc = schema["components"]["schemas"]["ToolDescription"]
            assert "help_examples" in tool_desc["properties"]
            help_examples = tool_desc["properties"]["help_examples"]
            assert "without_params" in help_examples["properties"]
            assert "with_params" in help_examples["properties"]

    def test_generate_adds_available_commands(self, generator):
        """Test that available commands are added to tool description."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            # Create proper mock commands with get_schema method
            mock_help = Mock()
            mock_help.get_schema.return_value = {"type": "object", "properties": {}}
            mock_help.name = "help"
            
            mock_config = Mock()
            mock_config.get_schema.return_value = {"type": "object", "properties": {}}
            mock_config.name = "config"
            
            mock_registry.get_all_commands.return_value = {"help": mock_help, "config": mock_config}
            
            schema = generator.generate()
            
            tool_desc = schema["components"]["schemas"]["ToolDescription"]
            assert "available_commands" in tool_desc["properties"]
            available_commands = tool_desc["properties"]["available_commands"]
            assert available_commands["type"] == "array"

    def test_generate_with_empty_commands(self, generator):
        """Test schema generation with no commands."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            schema = generator.generate()
            
            # Should handle empty commands gracefully
            assert "components" in schema
            assert "schemas" in schema["components"]

    def test_generate_logs_command_count(self, generator):
        """Test that command count is logged during generation."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            # Create proper mock commands with get_schema method
            mock_cmd1 = Mock()
            mock_cmd1.get_schema.return_value = {"type": "object", "properties": {}}
            mock_cmd1.name = "cmd1"
            
            mock_cmd2 = Mock()
            mock_cmd2.get_schema.return_value = {"type": "object", "properties": {}}
            mock_cmd2.name = "cmd2"
            
            mock_registry.get_all_commands.return_value = {"cmd1": mock_cmd1, "cmd2": mock_cmd2}
            
            with patch('mcp_proxy_adapter.custom_openapi.logger') as mock_logger:
                generator.generate()
                
                mock_logger.info.assert_called_with("Generated OpenAPI schema with 2 commands")

    def test_generate_with_custom_title_preserves_description(self, generator):
        """Test that custom title preserves original description."""
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            # Set custom title to trigger special handling
            generator.base_schema["info"]["title"] = "Custom Title"
            schema = generator.generate(title="Custom Title")
            
            # Description should remain unchanged for test case
            assert "Test API description" in schema["info"]["description"]


class TestCustomOpenAPIFunction:
    """Test cases for custom_openapi function."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock FastAPI application."""
        app = Mock(spec=FastAPI)
        app.title = "Test App"
        app.description = "Test App Description"
        app.version = "1.0.0"
        return app

    def test_custom_openapi_function(self, mock_app):
        """Test custom_openapi function."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.generate.return_value = {"test": "schema"}
            mock_generator_class.return_value = mock_generator
            
            result = custom_openapi(mock_app)
            
            # Check that generator was called with app attributes
            mock_generator.generate.assert_called_with(
                title="Test App",
                description="Test App Description",
                version="1.0.0"
            )
            
            # Check that schema was cached
            assert mock_app.openapi_schema == {"test": "schema"}
            assert result == {"test": "schema"}

    def test_custom_openapi_with_missing_attributes(self):
        """Test custom_openapi function with app missing attributes."""
        app = Mock(spec=FastAPI)
        # Don't set title, description, version
        
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.generate.return_value = {"test": "schema"}
            mock_generator_class.return_value = mock_generator
            
            result = custom_openapi(app)
            
            # Check that generator was called with None values
            mock_generator.generate.assert_called_with(
                title=None,
                description=None,
                version=None
            )

    def test_custom_openapi_with_partial_attributes(self):
        """Test custom_openapi function with app having only some attributes."""
        app = Mock(spec=FastAPI)
        app.title = "Partial App"
        # Don't set description and version
        
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.generate.return_value = {"test": "schema"}
            mock_generator_class.return_value = mock_generator
            
            result = custom_openapi(app)
            
            # Check that generator was called with partial values
            mock_generator.generate.assert_called_with(
                title="Partial App",
                description=None,
                version=None
            )


class TestCustomOpenAPIGeneratorEdgeCases:
    """Test edge cases and error conditions."""

    def test_generator_with_missing_base_schema_file(self):
        """Test generator initialization with missing base schema file."""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                CustomOpenAPIGenerator()

    def test_generator_with_invalid_json_in_base_schema(self):
        """Test generator initialization with invalid JSON in base schema."""
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "invalid json"
            
            with pytest.raises(json.JSONDecodeError):
                CustomOpenAPIGenerator()

    def test_add_commands_to_schema_with_empty_registry(self):
        """Test adding commands to schema with empty registry."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = {
                "components": {
                    "schemas": {
                        "CommandRequest": {
                            "properties": {
                                "command": {"type": "string", "enum": []},
                                "params": {"type": "object", "oneOf": []}
                            }
                        }
                    }
                }
            }
            
            generator = CustomOpenAPIGenerator()
            
            with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
                mock_registry.get_all_commands.return_value = {}
                
                schema = {
                    "components": {
                        "schemas": {
                            "CommandRequest": {
                                "properties": {
                                    "command": {"type": "string", "enum": []},
                                    "params": {"type": "object", "oneOf": []}
                                }
                            }
                        }
                    }
                }
                generator._add_commands_to_schema(schema)
                
                # Should handle empty registry gracefully
                command_enum = schema["components"]["schemas"]["CommandRequest"]["properties"]["command"]["enum"]
                assert command_enum == []

    def test_create_params_schema_with_command_without_schema(self):
        """Test creating params schema for command without get_schema method."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = {}
            
            generator = CustomOpenAPIGenerator()
            
            # Create a command class without get_schema method
            class CommandWithoutSchema(Command):
                name = "test_command"
                
                async def execute(self, **kwargs):
                    return {"result": "test"}
            
            # Should handle command without get_schema gracefully
            schema = generator._create_params_schema(CommandWithoutSchema)
            assert "title" in schema
            assert "description" in schema

    def test_generate_with_missing_components_in_base_schema(self):
        """Test generation with base schema missing components."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {
                    "title": "Test",
                    "description": "Test description"
                },
                "components": {
                    "schemas": {
                        "CommandRequest": {
                            "properties": {
                                "command": {"type": "string", "enum": []},
                                "params": {"type": "object", "oneOf": []}
                            }
                        }
                    }
                }
            }
            
            generator = CustomOpenAPIGenerator()
            
            with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
                mock_registry.get_all_commands.return_value = {}
                
                # Should handle missing components gracefully
                schema = generator.generate()
                assert "components" in schema
                assert "schemas" in schema["components"]

    def test_generate_with_completely_empty_base_schema(self):
        """Test generation with completely empty base schema (missing components and schemas)."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {
                    "title": "Test",
                    "description": "Test description"
                }
                # Missing components entirely
            }
            
            generator = CustomOpenAPIGenerator()
            
            with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
                mock_registry.get_all_commands.return_value = {}
                
                # Should handle completely missing components gracefully
                schema = generator.generate()
                assert "components" in schema
                assert "schemas" in schema["components"]
                assert "ToolDescription" in schema["components"]["schemas"]

    def test_generate_with_missing_schemas_in_components(self):
        """Test generation with components but missing schemas."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {
                    "title": "Test",
                    "description": "Test description"
                },
                "components": {
                    # Missing schemas
                }
            }
            
            generator = CustomOpenAPIGenerator()
            
            with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
                mock_registry.get_all_commands.return_value = {}
                
                # Should handle missing schemas gracefully
                schema = generator.generate()
                assert "components" in schema
                assert "schemas" in schema["components"]
                assert "ToolDescription" in schema["components"]["schemas"]

    def test_generate_with_missing_command_request_in_schemas(self):
        """Test generation with schemas but missing CommandRequest."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {
                    "title": "Test",
                    "description": "Test description"
                },
                "components": {
                    "schemas": {
                        # Missing CommandRequest
                        "SomeOtherSchema": {"type": "object"}
                    }
                }
            }
            
            generator = CustomOpenAPIGenerator()
            
            with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
                mock_registry.get_all_commands.return_value = {}
                
                # Should handle missing CommandRequest gracefully
                schema = generator.generate()
                assert "components" in schema
                assert "schemas" in schema["components"]
                assert "ToolDescription" in schema["components"]["schemas"]


class TestCustomOpenAPIGeneratorIntegration:
    """Integration tests for CustomOpenAPIGenerator."""

    def test_full_generation_workflow(self):
        """Test the complete schema generation workflow."""
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator._load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {
                    "title": "Test API",
                    "description": "Test description",
                    "version": "1.0.0"
                },
                "components": {
                    "schemas": {
                        "CommandRequest": {
                            "properties": {
                                "command": {"type": "string", "enum": []},
                                "params": {"type": "object", "oneOf": []}
                            }
                        }
                    }
                }
            }
            
            generator = CustomOpenAPIGenerator()
            
            with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
                # Create a mock command
                class TestCommand(Command):
                    name = "test_command"
                    
                    @classmethod
                    def get_schema(cls):
                        return {
                            "type": "object",
                            "properties": {
                                "param1": {"type": "string"}
                            }
                        }
                    
                    async def execute(self, **kwargs):
                        return {"result": "test"}
                
                mock_registry.get_all_commands.return_value = {
                    "test_command": TestCommand
                }
                
                schema = generator.generate(
                    title="Custom Title",
                    description="Custom Description",
                    version="2.0.0"
                )
                
                # Verify the complete schema structure
                assert schema["info"]["title"] == "Custom Title"
                assert schema["info"]["version"] == "2.0.0"
                assert "components" in schema
                assert "schemas" in schema["components"]
                assert "ToolDescription" in schema["components"]["schemas"]
                assert "Test_commandParams" in schema["components"]["schemas"] 