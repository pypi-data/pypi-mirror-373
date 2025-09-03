"""
Base command classes for MCP Microservice.
"""

import inspect
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar

from docstring_parser import parse

from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult, ErrorResult
from mcp_proxy_adapter.core.errors import (
    CommandError, InternalError, InvalidParamsError, NotFoundError, ValidationError
)
from mcp_proxy_adapter.core.logging import logger


T = TypeVar("T", bound=CommandResult)


class Command(ABC):
    """
    Base abstract class for all commands.
    """
    
    # Command name for registration
    name: ClassVar[str]
    # Command version (default: 0.1)
    version: ClassVar[str] = "0.1"
    # Plugin filename
    plugin: ClassVar[str] = ""
    # Command description
    descr: ClassVar[str] = ""
    # Command category
    category: ClassVar[str] = ""
    # Command author
    author: ClassVar[str] = ""
    # Author email
    email: ClassVar[str] = ""
    # Source URL
    source_url: ClassVar[str] = ""
    # Result class
    result_class: ClassVar[Type[CommandResult]]
    
    @abstractmethod
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute command with the specified parameters.
        
        Args:
            **kwargs: Command parameters including optional 'context' parameter.
            
        Returns:
            Command result.
        """
        pass
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            JSON schema.
        """
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
        
    @classmethod
    def get_result_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command result.
        
        Returns:
            JSON schema.
        """
        if hasattr(cls, "result_class") and cls.result_class:
            return cls.result_class.get_schema()
        return {}
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate command parameters.
        
        Args:
            params: Parameters to validate.
            
        Returns:
            Validated parameters.
            
        Raises:
            ValidationError: If parameters are invalid.
        """
        # Ensure params is a dictionary, even if None was passed
        if params is None:
            params = {}
            
        # Create a copy to avoid modifying the input dictionary during iteration
        validated_params = params.copy()
        
        # Handle None values and empty strings in parameters
        for key, value in list(validated_params.items()):
            # Process None values or empty strings - this helps with JavaScript null/undefined conversions
            if value is None or (isinstance(value, str) and value.lower() in ["null", "none", ""]):
                # For commands that specifically handle None values, keep the parameter
                # (like help), keep the parameter but ensure it's a proper Python None
                if key in ["cmdname"]:  # список параметров, для которых None является допустимым значением
                    validated_params[key] = None
                else:
                    # For most parameters, remove None values to avoid issues
                    del validated_params[key]
        
        # Get command schema to validate parameters
        schema = self.get_schema()
        if schema and "properties" in schema:
            allowed_properties = schema["properties"].keys()
            
            # Filter out parameters that are not in the schema
            invalid_params = []
            for param_name in list(validated_params.keys()):
                if param_name not in allowed_properties:
                    invalid_params.append(param_name)
                    del validated_params[param_name]
            
            # Log warning about invalid parameters
            if invalid_params:
                logger.warning(f"Command {self.__class__.__name__} received invalid parameters: {invalid_params}. "
                             f"Allowed parameters: {list(allowed_properties)}")
        
        # Validate required parameters based on command schema
        if schema and "required" in schema:
            required_params = schema["required"]
            missing_params = []
            
            for param in required_params:
                if param not in validated_params:
                    missing_params.append(param)
            
            if missing_params:
                raise ValidationError(
                    f"Missing required parameters: {', '.join(missing_params)}",
                    data={"missing_parameters": missing_params}
                )
                
        return validated_params
    
    @classmethod
    async def run(cls, **kwargs) -> CommandResult:
        """
        Runs the command with the specified arguments.

        Args:
            **kwargs: Command arguments including optional 'context' parameter.

        Returns:
            Command result.
        """
        # Extract context from kwargs
        context = kwargs.pop('context', {}) if 'context' in kwargs else {}
        
        try:
            logger.debug(f"Running command {cls.__name__} with params: {kwargs}")
            
            # Import registry here to avoid circular imports
            from mcp_proxy_adapter.commands.command_registry import registry
            
            # Get command name
            if not hasattr(cls, "name") or not cls.name:
                command_name = cls.__name__.lower()
                if command_name.endswith("command"):
                    command_name = command_name[:-7]
            else:
                command_name = cls.name
            
            # Ensure kwargs is never None
            if kwargs is None:
                kwargs = {}
                
            # Get command with priority (custom commands first, then built-in)
            command_class = registry.get_command(command_name)
            if command_class is None:
                raise NotFoundError(f"Command '{command_name}' not found")
            
            # Create new instance and validate parameters
            command = command_class()
            validated_params = command.validate_params(kwargs)
            
            # Execute command with validated parameters and context
            result = await command.execute(**validated_params, context=context)
            
            logger.debug(f"Command {cls.__name__} executed successfully")
            return result
        except ValidationError as e:
            # Ошибка валидации параметров
            logger.error(f"Validation error in command {cls.__name__}: {e}")
            return ErrorResult(
                message=str(e), 
                code=e.code, 
                details=e.data
            )
        except InvalidParamsError as e:
            # Ошибка в параметрах команды
            logger.error(f"Invalid parameters error in command {cls.__name__}: {e}")
            return ErrorResult(
                message=str(e), 
                code=e.code, 
                details=e.data
            )
        except NotFoundError as e:
            # Ресурс не найден
            logger.error(f"Resource not found error in command {cls.__name__}: {e}")
            return ErrorResult(
                message=str(e), 
                code=e.code, 
                details=e.data
            )
        except TimeoutError as e:
            # Превышено время ожидания
            logger.error(f"Timeout error in command {cls.__name__}: {e}")
            return ErrorResult(
                message=str(e), 
                code=e.code, 
                details=e.data
            )
        except CommandError as e:
            # Ошибка выполнения команды
            logger.error(f"Command error in {cls.__name__}: {e}")
            return ErrorResult(
                message=str(e), 
                code=e.code, 
                details=e.data
            )
        except Exception as e:
            # Непредвиденная ошибка
            logger.exception(f"Unexpected error executing command {cls.__name__}: {e}")
            internal_error = InternalError(f"Command execution error: {str(e)}")
            return ErrorResult(
                message=internal_error.message,
                code=internal_error.code,
                details={"original_error": str(e)}
            )
    
    @classmethod
    def get_param_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        Gets information about execute method parameters.

        Returns:
            Dictionary with parameters information.
        """
        signature = inspect.signature(cls.execute)
        params = {}
        
        for name, param in signature.parameters.items():
            if name == "self":
                continue
                
            param_info = {
                "name": name,
                "required": param.default == inspect.Parameter.empty
            }
            
            if param.annotation != inspect.Parameter.empty:
                param_info["type"] = str(param.annotation)
            
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
                
            params[name] = param_info
            
        return params
    
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Returns complete metadata about the command.
        
        Provides a single access point to all command metadata.
        
        Returns:
            Dict with command metadata
        """
        # Get and format docstring
        doc = cls.__doc__ or ""
        description = inspect.cleandoc(doc) if doc else ""
        
        # Extract first line for summary
        summary = description.split("\n")[0] if description else ""
        
        # Get parameters information
        param_info = cls.get_param_info()
        
        # Generate examples based on parameters
        examples = cls._generate_examples(param_info)
        
        return {
            "name": cls.name,
            "version": cls.version,
            "plugin": cls.plugin,
            "descr": cls.descr,
            "category": cls.category,
            "author": cls.author,
            "email": cls.email,
            "source_url": cls.source_url,
            "summary": summary,
            "description": description,
            "params": param_info,
            "examples": examples,
            "schema": cls.get_schema(),
            "result_schema": cls.get_result_schema(),
            "result_class": cls.result_class.__name__ if hasattr(cls, "result_class") else None,
        }
    
    @classmethod
    def _generate_examples(cls, params: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generates usage examples of the command based on its parameters.
        
        Args:
            params: Information about command parameters
            
        Returns:
            List of examples
        """
        examples = []
        
        # Simple example without parameters, if all parameters are optional
        if not any(param.get("required", False) for param in params.values()):
            examples.append({
                "command": cls.name,
                "description": f"Call {cls.name} command without parameters"
            })
        
        # Example with all required parameters
        required_params = {k: v for k, v in params.items() if v.get("required", False)}
        if required_params:
            sample_params = {}
            for param_name, param_info in required_params.items():
                # Try to generate sample value based on type
                param_type = param_info.get("type", "")
                
                if "str" in param_type:
                    sample_params[param_name] = f"sample_{param_name}"
                elif "int" in param_type:
                    sample_params[param_name] = 1
                elif "float" in param_type:
                    sample_params[param_name] = 1.0
                elif "bool" in param_type:
                    sample_params[param_name] = True
                elif "list" in param_type or "List" in param_type:
                    sample_params[param_name] = []
                elif "dict" in param_type or "Dict" in param_type:
                    sample_params[param_name] = {}
                else:
                    sample_params[param_name] = "..."
            
            examples.append({
                "command": cls.name,
                "params": sample_params,
                "description": f"Call {cls.name} command with required parameters"
            })
        
        # Example with all parameters (including optional ones)
        if len(params) > len(required_params):
            all_params = {}
            for param_name, param_info in params.items():
                # For required parameters, use the same values as above
                if param_info.get("required", False):
                    # Try to generate sample value based on type
                    param_type = param_info.get("type", "")
                    
                    if "str" in param_type:
                        all_params[param_name] = f"sample_{param_name}"
                    elif "int" in param_type:
                        all_params[param_name] = 1
                    elif "float" in param_type:
                        all_params[param_name] = 1.0
                    elif "bool" in param_type:
                        all_params[param_name] = True
                    elif "list" in param_type or "List" in param_type:
                        all_params[param_name] = []
                    elif "dict" in param_type or "Dict" in param_type:
                        all_params[param_name] = {}
                    else:
                        all_params[param_name] = "..."
                # For optional parameters, use their default values or a sample value
                else:
                    if "default" in param_info:
                        all_params[param_name] = param_info["default"]
                    else:
                        param_type = param_info.get("type", "")
                        
                        if "str" in param_type:
                            all_params[param_name] = f"optional_{param_name}"
                        elif "int" in param_type:
                            all_params[param_name] = 0
                        elif "float" in param_type:
                            all_params[param_name] = 0.0
                        elif "bool" in param_type:
                            all_params[param_name] = False
                        elif "list" in param_type or "List" in param_type:
                            all_params[param_name] = []
                        elif "dict" in param_type or "Dict" in param_type:
                            all_params[param_name] = {}
                        else:
                            all_params[param_name] = None
            
            examples.append({
                "command": cls.name,
                "params": all_params,
                "description": f"Call {cls.name} command with all parameters"
            })
        
        return examples