"""
Модуль для интеграции метаданных команд с внешними API инструментами.

Этот модуль обеспечивает преобразование метаданных команд микросервиса 
в форматы, понятные для внешних систем, таких как OpenAPI, JSON-RPC,
и других API интерфейсов.
"""

from typing import Any, Dict, List, Optional, Union
import json
import logging

from mcp_proxy_adapter.api.schemas import APIToolDescription
from mcp_proxy_adapter.commands.command_registry import CommandRegistry

logger = logging.getLogger(__name__)


class ToolIntegration:
    """
    Класс для интеграции метаданных команд с внешними инструментами API.
    
    Обеспечивает генерацию описаний инструментов API для различных систем
    на основе метаданных команд микросервиса.
    """
    
    @classmethod
    def generate_tool_schema(cls, tool_name: str, registry: CommandRegistry, 
                             description: Optional[str] = None) -> Dict[str, Any]:
        """
        Генерирует схему инструмента API для использования в OpenAPI и других системах.
        
        Args:
            tool_name: Имя инструмента API
            registry: Реестр команд
            description: Дополнительное описание инструмента (опционально)
            
        Returns:
            Словарь с описанием инструмента в формате OpenAPI
        """
        # Получаем базовое описание инструмента
        base_description = APIToolDescription.generate_tool_description(tool_name, registry)
        
        # Получаем типы параметров
        parameter_types = cls._extract_parameter_types(base_description["supported_commands"])
        
        # Формируем схему инструмента
        schema = {
            "name": tool_name,
            "description": description or base_description["description"],
            "parameters": {
                "properties": {
                    "command": {
                        "description": "Команда для выполнения",
                        "type": "string",
                        "enum": list(base_description["supported_commands"].keys())
                    },
                    "params": {
                        "description": "Параметры команды",
                        "type": "object",
                        "additionalProperties": True,
                        "properties": parameter_types
                    }
                },
                "required": ["command"],
                "type": "object"
            }
        }
        
        return schema
    
    @classmethod
    def generate_tool_documentation(cls, tool_name: str, registry: CommandRegistry, 
                                   format: str = "markdown") -> str:
        """
        Генерирует документацию по инструменту API в заданном формате.
        
        Args:
            tool_name: Имя инструмента API
            registry: Реестр команд
            format: Формат документации (markdown, html)
            
        Returns:
            Строка с документацией в заданном формате
        """
        if format.lower() == "markdown":
            return APIToolDescription.generate_tool_description_text(tool_name, registry)
        elif format.lower() == "html":
            # Преобразуем markdown в HTML (в реальном проекте здесь будет 
            # использоваться библиотека для конвертации markdown в HTML)
            markdown = APIToolDescription.generate_tool_description_text(tool_name, registry)
            # Простая конвертация для примера
            body = markdown.replace('#', '<h1>').replace('\n\n', '</p><p>')
            html = f"<html><body>{body}</body></html>"
            return html
        else:
            # По умолчанию возвращаем markdown
            return APIToolDescription.generate_tool_description_text(tool_name, registry)
    
    @classmethod
    def register_external_tools(cls, registry: CommandRegistry, tool_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Регистрирует инструменты API во внешних системах.
        
        Args:
            registry: Реестр команд
            tool_names: Список имен инструментов API для регистрации
            
        Returns:
            Словарь с результатами регистрации инструментов
        """
        results = {}
        
        for tool_name in tool_names:
            try:
                # Генерируем схему инструмента
                schema = cls.generate_tool_schema(tool_name, registry)
                
                # Здесь будет код для регистрации инструмента во внешней системе
                # Например, отправка схемы в API регистрации инструментов
                
                results[tool_name] = {
                    "status": "success",
                    "schema": schema
                }
                
                logger.info(f"Successfully registered tool: {tool_name}")
            except Exception as e:
                logger.debug(f"Error registering tool {tool_name}: {e}")
                results[tool_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    @classmethod
    def _extract_parameter_types(cls, commands: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Извлекает типы параметров из описания команд для формирования схемы.
        
        Args:
            commands: Словарь с описанием команд
            
        Returns:
            Словарь с типами параметров для схемы OpenAPI
        """
        parameter_types = {}
        
        # Формируем словарь типов для всех параметров всех команд
        for cmd_name, cmd_info in commands.items():
            params = cmd_info.get("params", {})
            if params is None:
                continue
            for param_name, param_info in params.items():
                param_type = param_info.get("type", "значение")
                
                # Преобразуем русские типы в типы JSON Schema
                if param_type == "строка":
                    json_type = "string"
                elif param_type == "целое число":
                    json_type = "integer"
                elif param_type == "число":
                    json_type = "number"
                elif param_type == "логическое значение":
                    json_type = "boolean"
                elif param_type == "список":
                    json_type = "array"
                elif param_type == "объект":
                    json_type = "object"
                else:
                    json_type = "string"
                
                # Добавляем тип в общий словарь
                parameter_types[param_name] = {
                    "type": json_type,
                    "description": param_info.get("description", "")
                }
        
        return parameter_types


def generate_tool_help(tool_name: str, registry: CommandRegistry) -> str:
    """
    Генерирует справочную информацию по инструменту API.
    
    Args:
        tool_name: Имя инструмента API
        registry: Реестр команд
        
    Returns:
        Строка с описанием инструмента и доступных команд
    """
    # Получаем метаданные всех команд
    all_metadata = registry.get_all_metadata()
    
    # Формируем текст справки
    help_text = f"# Инструмент {tool_name}\n\n"
    help_text += "Позволяет выполнять команды через JSON-RPC протокол.\n\n"
    help_text += "## Доступные команды:\n\n"
    
    # Добавляем информацию о каждой команде
    for cmd_name, metadata in all_metadata.items():
        help_text += f"### {cmd_name}\n"
        help_text += f"{metadata['summary']}\n\n"
        
        # Добавляем информацию о параметрах команды
        if metadata["params"]:
            help_text += "Параметры:\n"
            for param_name, param_info in metadata["params"].items():
                required = "обязательный" if param_info.get("required", False) else "опциональный"
                help_text += f"- {param_name}: {required}\n"
            help_text += "\n"
        
        # Добавляем пример использования команды
        if metadata.get("examples"):
            example = metadata["examples"][0]
            help_text += "Пример:\n"
            help_text += "```json\n"
            help_text += json.dumps(
                {"command": example.get("command", cmd_name), "params": example.get("params", {})},
                indent=2,
                ensure_ascii=False
            )
            help_text += "\n```\n\n"
    
    return help_text 