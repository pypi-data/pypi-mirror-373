"""
OpenAPI schema generator for MCP Microservice
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import inspect
import json
from pathlib import Path

from .commands.command_registry import CommandRegistry
from .commands.base import Command
from .core.errors import ValidationError as SchemaValidationError


@dataclass
class TypeInfo:
    """Information about a type for OpenAPI schema"""
    openapi_type: str
    format: Optional[str] = None
    items: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None


class OpenApiGenerator:
    """Generates OpenAPI schema for MCP Microservice"""
    
    PYTHON_TO_OPENAPI_TYPES = {
        str: TypeInfo("string"),
        int: TypeInfo("integer", "int64"),
        float: TypeInfo("number", "float"),
        bool: TypeInfo("boolean"),
        list: TypeInfo("array"),
        dict: TypeInfo("object"),
        None: TypeInfo("null"),
    }

    def __init__(self, registry: CommandRegistry):
        """
        Initialize generator
        
        Args:
            registry: Command registry instance
        """
        self.registry = registry
        self._base_schema = self._load_base_schema()

    def _load_base_schema(self) -> Dict[str, Any]:
        """Load base schema from file"""
        schema_path = Path(__file__).parent / "schemas" / "base_schema.json"
        with open(schema_path) as f:
            return json.load(f)

    def _get_type_info(self, python_type: Any) -> TypeInfo:
        """
        Get OpenAPI type info for Python type
        
        Args:
            python_type: Python type annotation
        
        Returns:
            TypeInfo object with OpenAPI type information
        """
        # Handle Optional types
        origin = getattr(python_type, "__origin__", None)
        if origin is Optional:
            return self._get_type_info(python_type.__args__[0])

        # Handle List and Dict
        if origin is list:
            item_type = self._get_type_info(python_type.__args__[0])
            return TypeInfo("array", items={"type": item_type.openapi_type})
        
        if origin is dict:
            return TypeInfo("object", additionalProperties=True)

        # Handle basic types
        if python_type in self.PYTHON_TO_OPENAPI_TYPES:
            return self.PYTHON_TO_OPENAPI_TYPES[python_type]

        # Handle custom classes
        if inspect.isclass(python_type):
            properties = {}
            required = []
            
            for name, field in inspect.get_annotations(python_type).items():
                field_info = self._get_type_info(field)
                properties[name] = {
                    "type": field_info.openapi_type
                }
                if field_info.format:
                    properties[name]["format"] = field_info.format
                required.append(name)
            
            return TypeInfo(
                "object",
                properties=properties,
                required=required
            )

        raise ValueError(f"Unsupported type: {python_type}")

    def _add_command_params(self, schema: Dict[str, Any], command: Command):
        """
        Add command parameters to schema
        
        Args:
            schema: OpenAPI schema
            command: Command instance
        """
        params = {}
        required = []
        
        # Get parameters from function signature
        sig = inspect.signature(command.func)
        for name, param in sig.parameters.items():
            param_schema = {}
            
            # Get type info
            type_info = self._get_type_info(param.annotation)
            param_schema["type"] = type_info.openapi_type
            
            if type_info.format:
                param_schema["format"] = type_info.format
            
            if type_info.items:
                param_schema["items"] = type_info.items
            
            # Get description from docstring
            if command.doc and command.doc.params:
                for doc_param in command.doc.params:
                    if doc_param.arg_name == name:
                        param_schema["description"] = doc_param.description
                        break
            
            # Handle default value
            if param.default is not param.empty:
                param_schema["default"] = param.default
            else:
                required.append(name)
            
            params[name] = param_schema
        
        # Add to schema
        method_schema = {
            "type": "object",
            "properties": params
        }
        if required:
            method_schema["required"] = required
            
        schema["components"]["schemas"][f"Params{command.name}"] = method_schema

    def _add_commands_to_schema(self, schema: Dict[str, Any]):
        """
        Add all commands to schema
        
        Args:
            schema: OpenAPI schema
        """
        for command in self.registry.get_commands():
            self._add_command_params(schema, command)
    
    def _add_cmd_endpoint(self, schema: Dict[str, Any]) -> None:
        """
        Add /cmd endpoint to OpenAPI schema.
        
        Args:
            schema: OpenAPI schema to update
        """
        schema["paths"]["/cmd"] = {
            "post": {
                "summary": "Execute command",
                "description": "Universal endpoint for executing any command",
                "operationId": "execute_command",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CommandRequest"}
                        }
                    },
                    "required": True
                },
                "responses": {
                    "200": {
                        "description": "Command execution result",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "oneOf": [
                                        {"$ref": "#/components/schemas/CommandSuccessResponse"},
                                        {"$ref": "#/components/schemas/CommandErrorResponse"}
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _add_cmd_models(self, schema: Dict[str, Any]) -> None:
        """
        Add models for /cmd endpoint to OpenAPI schema.
        
        Args:
            schema: OpenAPI schema to update
        """
        # Add command request model
        schema["components"]["schemas"]["CommandRequest"] = {
            "type": "object",
            "required": ["command"],
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command name to execute"
                },
                "params": {
                    "type": "object",
                    "description": "Command parameters (specific to command)",
                    "additionalProperties": True
                }
            }
        }
        
        # Add command success response model
        schema["components"]["schemas"]["CommandSuccessResponse"] = {
            "type": "object",
            "required": ["result"],
            "properties": {
                "result": {
                    "type": "object",
                    "description": "Command execution result",
                    "additionalProperties": True
                }
            }
        }
        
        # Add command error response model
        schema["components"]["schemas"]["CommandErrorResponse"] = {
            "type": "object",
            "required": ["error"],
            "properties": {
                "error": {
                    "type": "object",
                    "required": ["code", "message"],
                    "properties": {
                        "code": {
                            "type": "integer",
                            "description": "Error code"
                        },
                        "message": {
                            "type": "string",
                            "description": "Error message"
                        },
                        "data": {
                            "type": "object",
                            "description": "Additional error data",
                            "additionalProperties": True
                        }
                    }
                }
            }
        }
    
    def _add_cmd_examples(self, schema: Dict[str, Any]) -> None:
        """
        Add examples for /cmd endpoint to OpenAPI schema.
        
        Args:
            schema: OpenAPI schema to update
        """
        # Create examples section if it doesn't exist
        if "examples" not in schema["components"]:
            schema["components"]["examples"] = {}
        
        # Add help command example request
        schema["components"]["examples"]["help_request"] = {
            "summary": "Get list of commands",
            "value": {
                "command": "help"
            }
        }
        
        # Add help command example response
        schema["components"]["examples"]["help_response"] = {
            "summary": "Response with list of commands",
            "value": {
                "result": {
                    "commands": {
                        "help": {
                            "description": "Get help information about available commands"
                        },
                        "health": {
                            "description": "Check server health"
                        }
                    }
                }
            }
        }
        
        # Add specific command help example request
        schema["components"]["examples"]["help_specific_request"] = {
            "summary": "Get information about specific command",
            "value": {
                "command": "help",
                "params": {
                    "cmdname": "health"
                }
            }
        }
        
        # Add error example
        schema["components"]["examples"]["command_error"] = {
            "summary": "Command not found error",
            "value": {
                "error": {
                    "code": -32601,
                    "message": "Command 'unknown_command' not found"
                }
            }
        }
        
        # Link examples to endpoint
        schema["paths"]["/cmd"]["post"]["requestBody"]["content"]["application/json"]["examples"] = {
            "help": {"$ref": "#/components/examples/help_request"},
            "help_specific": {"$ref": "#/components/examples/help_specific_request"}
        }
        
        schema["paths"]["/cmd"]["post"]["responses"]["200"]["content"]["application/json"]["examples"] = {
            "help": {"$ref": "#/components/examples/help_response"},
            "error": {"$ref": "#/components/examples/command_error"}
        }
    
    def _validate_required_paths(self, schema: Dict[str, Any]) -> None:
        """
        Validate that required paths exist in schema.
        
        Args:
            schema: OpenAPI schema to validate
        
        Raises:
            SchemaValidationError: If required paths are missing
        """
        required_paths = ['/cmd', '/api/commands']
        
        for path in required_paths:
            if path not in schema['paths']:
                raise SchemaValidationError(f"Missing required path: {path}")

    def generate(self) -> Dict[str, Any]:
        """
        Generate complete OpenAPI schema
        
        Returns:
            OpenAPI schema as dictionary
        """
        schema = self._base_schema.copy()
        
        # Add commands to schema
        self._add_commands_to_schema(schema)
        
        # Add /cmd endpoint regardless of commands
        self._add_cmd_endpoint(schema)
        self._add_cmd_models(schema)
        self._add_cmd_examples(schema)
        
        # Validate required paths
        self._validate_required_paths(schema)
        
        self.validate_schema(schema)
        return schema

    def validate_schema(self, schema: Dict[str, Any]):
        """
        Validate generated schema
        
        Args:
            schema: OpenAPI schema to validate
            
        Raises:
            SchemaValidationError: If schema is invalid
        """
        try:
            # Check that required components exist
            required_components = ['CommandRequest', 'CommandSuccessResponse', 'CommandErrorResponse']
            for component in required_components:
                if component not in schema['components']['schemas']:
                    raise SchemaValidationError(f"Missing required component: {component}")
            
            # Validate that all paths return 200 status
            for path in schema['paths'].values():
                for method in path.values():
                    if '200' not in method['responses']:
                        raise SchemaValidationError("All endpoints must return 200 status code")
                    
                    response = method['responses']['200']
                    if 'application/json' not in response['content']:
                        raise SchemaValidationError("All responses must be application/json")
        except Exception as e:
            raise SchemaValidationError(f"Schema validation failed: {str(e)}")
        
        # Here we would normally use a library like openapi-spec-validator
        # to validate the schema against the OpenAPI 3.0 specification 