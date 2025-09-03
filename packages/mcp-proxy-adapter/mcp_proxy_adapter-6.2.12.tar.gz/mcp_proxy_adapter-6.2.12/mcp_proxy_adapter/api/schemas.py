"""
Module with API schema definitions.
"""

from typing import Any, Dict, List, Optional, Union, Literal

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Error response model.
    """
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ErrorWrapper(BaseModel):
    """
    Wrapper for error response.
    """
    error: ErrorResponse


class JsonRpcRequest(BaseModel):
    """
    JSON-RPC request model.
    """
    jsonrpc: Literal["2.0"] = Field("2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name")
    params: Optional[Union[Dict[str, Any], List[Any]]] = Field(None, description="Method parameters")
    id: Optional[Union[str, int]] = Field(None, description="Request ID")


class JsonRpcError(BaseModel):
    """
    JSON-RPC error model.
    """
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional error data")


class JsonRpcSuccessResponse(BaseModel):
    """
    JSON-RPC success response model.
    """
    jsonrpc: Literal["2.0"] = Field("2.0", description="JSON-RPC version")
    result: Dict[str, Any] = Field(..., description="Method result")
    id: Optional[Union[str, int]] = Field(None, description="Request ID")


class JsonRpcErrorResponse(BaseModel):
    """
    JSON-RPC error response model.
    """
    jsonrpc: Literal["2.0"] = Field("2.0", description="JSON-RPC version")
    error: JsonRpcError = Field(..., description="Error information")
    id: Optional[Union[str, int]] = Field(None, description="Request ID")


class CommandResponse(BaseModel):
    """
    Command response model.
    """
    success: bool = Field(..., description="Command execution success flag")
    data: Optional[Dict[str, Any]] = Field(None, description="Result data")
    message: Optional[str] = Field(None, description="Result message")
    error: Optional[ErrorResponse] = Field(None, description="Error information")


class HealthResponse(BaseModel):
    """
    Health response model.
    """
    status: str = Field(..., description="Server status")
    version: str = Field(..., description="Server version")
    uptime: float = Field(..., description="Server uptime in seconds")
    components: Dict[str, Any] = Field(..., description="Components health")


class CommandListResponse(BaseModel):
    """
    Command list response model.
    """
    commands: Dict[str, Dict[str, Any]] = Field(..., description="Available commands")


class CommandRequest(BaseModel):
    """
    Command request model for /cmd endpoint.
    """
    command: str = Field(..., description="Command name to execute")
    params: Optional[Dict[str, Any]] = Field({}, description="Command parameters")


class CommandSuccessResponse(BaseModel):
    """
    Command success response model for /cmd endpoint.
    """
    result: Dict[str, Any] = Field(..., description="Command execution result")


class CommandErrorResponse(BaseModel):
    """
    Command error response model for /cmd endpoint.
    """
    error: JsonRpcError = Field(..., description="Error information")


class APIToolDescription:
    """
    Генератор описаний для инструментов API на основе метаданных команд.
    
    Класс предоставляет функциональность для создания подробных и понятных
    описаний инструментов API, которые помогают пользователям сразу понять
    как использовать API.
    """
    
    @classmethod
    def generate_tool_description(cls, name: str, registry) -> Dict[str, Any]:
        """
        Генерирует подробное описание инструмента API на основе имени и реестра команд.
        
        Args:
            name: Имя инструмента API
            registry: Реестр команд
            
        Returns:
            Словарь с полным описанием инструмента
        """
        # Получаем все метаданные из реестра команд
        all_metadata = registry.get_all_metadata()
        
        # Базовое описание инструмента
        description = {
            "name": name,
            "description": f"Выполняет команды через JSON-RPC протокол на сервере проекта.",
            "supported_commands": {},
            "examples": []
        }
        
        # Добавляем информацию о поддерживаемых командах
        for cmd_name, metadata in all_metadata.items():
            command_info = {
                "summary": metadata["summary"],
                "description": metadata["description"],
                "params": {},
                "required_params": []
            }
            
            # Добавляем информацию о параметрах
            for param_name, param_info in metadata["params"].items():
                param_type = param_info.get("type", "any").replace("typing.", "")
                
                # Определяем тип параметра для документации
                simple_type = cls._simplify_type(param_type)
                
                command_info["params"][param_name] = {
                    "type": simple_type,
                    "description": cls._extract_param_description(metadata["description"], param_name),
                    "required": param_info.get("required", False)
                }
                
                # Если параметр обязательный, добавляем его в список обязательных
                if param_info.get("required", False):
                    command_info["required_params"].append(param_name)
            
            description["supported_commands"][cmd_name] = command_info
            
            # Добавляем примеры из метаданных команды
            for example in metadata.get("examples", []):
                description["examples"].append({
                    "command": example.get("command", cmd_name),
                    "params": example.get("params", {}),
                    "description": example.get("description", f"Пример использования команды {cmd_name}")
                })
        
        return description
    
    @classmethod
    def generate_tool_description_text(cls, name: str, registry) -> str:
        """
        Генерирует текстовое описание инструмента API для документации.
        
        Args:
            name: Имя инструмента API
            registry: Реестр команд
            
        Returns:
            Текстовое описание инструмента в формате markdown
        """
        tool_data = cls.generate_tool_description(name, registry)
        
        # Формируем заголовок и базовое описание
        text = f"# Инструмент {tool_data['name']}\n\n"
        text += f"{tool_data['description']}\n\n"
        
        # Список доступных команд
        text += "## Доступные команды\n\n"
        for cmd_name, cmd_info in tool_data["supported_commands"].items():
            text += f"### {cmd_name}\n\n"
            text += f"{cmd_info['description']}\n\n"
            
            # Информация о параметрах
            if cmd_info["params"]:
                text += "#### Параметры:\n\n"
                for param_name, param_info in cmd_info["params"].items():
                    required_mark = "**обязательный**" if param_info["required"] else "опциональный"
                    text += f"- `{param_name}` ({param_info['type']}, {required_mark}): {param_info['description']}\n"
                text += "\n"
            
            # Примеры использования
            cmd_examples = [ex for ex in tool_data["examples"] if ex["command"] == cmd_name]
            if cmd_examples:
                text += "#### Примеры:\n\n"
                for i, example in enumerate(cmd_examples):
                    text += f"**Пример {i+1}**: {example['description']}\n"
                    text += "```json\n"
                    text += "{\n"
                    text += f'    "command": "{example["command"]}",\n'
                    if example["params"]:
                        text += '    "params": {\n'
                        params_str = []
                        for p_name, p_value in example["params"].items():
                            if isinstance(p_value, str):
                                p_str = f'        "{p_name}": "{p_value}"'
                            else:
                                p_str = f'        "{p_name}": {p_value}'
                            params_str.append(p_str)
                        text += ",\n".join(params_str)
                        text += "\n    }\n"
                    else:
                        text += '    "params": {}\n'
                    text += "}\n"
                    text += "```\n\n"
        
        return text
    
    @classmethod
    def _simplify_type(cls, type_str: str) -> str:
        """
        Упрощает строковое представление типа для документации.
        
        Args:
            type_str: Строковое представление типа
            
        Returns:
            Упрощенное строковое представление типа
        """
        # Удаляем префиксы из строки типа
        type_str = type_str.replace("<class '", "").replace("'>", "")
        
        # Преобразование стандартных типов
        if "str" in type_str:
            return "строка"
        elif "int" in type_str:
            return "целое число"
        elif "float" in type_str:
            return "число"
        elif "bool" in type_str:
            return "логическое значение"
        elif "List" in type_str or "list" in type_str:
            return "список"
        elif "Dict" in type_str or "dict" in type_str:
            return "объект"
        elif "Optional" in type_str:
            # Извлекаем тип из Optional[X]
            inner_type = type_str.split("[")[1].split("]")[0]
            return cls._simplify_type(inner_type)
        else:
            return "значение"
    
    @classmethod
    def _extract_param_description(cls, doc_string: str, param_name: str) -> str:
        """
        Извлекает описание параметра из строки документации.
        
        Args:
            doc_string: Строка документации
            param_name: Имя параметра
            
        Returns:
            Описание параметра или пустая строка, если описание не найдено
        """
        # Проверяем, есть ли в документации секция Args или Parameters
        if "Args:" in doc_string:
            args_section = doc_string.split("Args:")[1].split("\n\n")[0]
        elif "Parameters:" in doc_string:
            args_section = doc_string.split("Parameters:")[1].split("\n\n")[0]
        else:
            return ""
        
        # Ищем описание параметра
        for line in args_section.split("\n"):
            line = line.strip()
            if line.startswith(param_name + ":") or line.startswith(param_name + " :"):
                return line.split(":", 1)[1].strip()
        
        return ""


# Create dictionary mapping command names to their schemas
command_schemas: Dict[str, Dict[str, Any]] = {}
