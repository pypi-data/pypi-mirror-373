"""
Модуль с реализацией инструментов API для внешних систем.

Этот модуль содержит классы инструментов API, которые могут быть
интегрированы с внешними системами для выполнения команд микросервиса.
"""

from typing import Any, Dict, Optional, Union, List
import json
import logging

from mcp_proxy_adapter.api.tool_integration import ToolIntegration
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import NotFoundError, InvalidParamsError

logger = logging.getLogger(__name__)


class TSTCommandExecutor:
    """
    Инструмент для выполнения команд через JSON-RPC протокол на сервере проекта.
    
    Этот класс предоставляет функциональность для выполнения команд микросервиса
    через внешний интерфейс TST (Tool-System-Transport).
    """
    
    name = "tst_execute_command"
    description = "Выполняет команду через JSON-RPC протокол."
    
    @classmethod
    async def execute(cls, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполняет команду с указанными параметрами.
        
        Args:
            command: Имя команды для выполнения
            params: Параметры команды (опционально)
            
        Returns:
            Результат выполнения команды
            
        Raises:
            NotFoundError: Если команда не найдена
            InvalidParamsError: Если переданы некорректные параметры
        """
        if not params:
            params = {}
            
        logger.info(f"Executing command via TST: {command}, params: {params}")
        
        try:
            # Проверяем существование команды
            if not registry.command_exists_with_priority(command):
                raise NotFoundError(f"Команда '{command}' не найдена")
            
            # Получаем класс команды
            command_class = registry.get_command_with_priority(command)
            
            # Выполняем команду
            result = await command_class.execute(**params)
            
            # Возвращаем результат
            return result.to_dict()
        except NotFoundError as e:
            logger.error(f"Command not found: {command}")
            raise
        except Exception as e:
            logger.exception(f"Error executing command {command}: {e}")
            raise
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Возвращает схему инструмента в формате OpenAPI.
        
        Returns:
            Словарь со схемой инструмента
        """
        return ToolIntegration.generate_tool_schema(cls.name, registry, cls.description)
    
    @classmethod
    def get_description(cls, format: str = "json") -> Union[Dict[str, Any], str]:
        """
        Возвращает полное описание инструмента в указанном формате.
        
        Args:
            format: Формат описания (json, markdown, html)
            
        Returns:
            Описание инструмента в указанном формате
        """
        if format.lower() == "json":
            # Получаем базовое описание инструмента
            base_description = ToolIntegration.generate_tool_schema(cls.name, registry, cls.description)
            
            # Добавляем дополнительную информацию
            base_description["examples"] = cls._generate_examples()
            base_description["error_codes"] = cls._generate_error_codes()
            
            return base_description
        elif format.lower() in ["markdown", "text", "html"]:
            return ToolIntegration.generate_tool_documentation(cls.name, registry, format)
        else:
            # По умолчанию возвращаем JSON формат
            return ToolIntegration.generate_tool_schema(cls.name, registry, cls.description)
    
    @classmethod
    def _generate_examples(cls) -> List[Dict[str, Any]]:
        """
        Генерирует примеры использования инструмента.
        
        Returns:
            Список примеров использования
        """
        examples = []
        
        # Получаем метаданные всех команд
        all_metadata = registry.get_all_metadata()
        
        # Добавляем по одному примеру для каждой команды
        for cmd_name, metadata in all_metadata.items():
            if metadata.get("examples"):
                # Берем первый пример из метаданных
                example = metadata["examples"][0]
                
                # Формируем пример использования инструмента
                examples.append({
                    "command": cls.name,
                    "params": {
                        "command": example.get("command", cmd_name),
                        "params": example.get("params", {})
                    },
                    "description": f"Выполнение команды {cmd_name}"
                })
        
        return examples
    
    @classmethod
    def _generate_error_codes(cls) -> Dict[str, str]:
        """
        Генерирует словарь возможных кодов ошибок.
        
        Returns:
            Словарь с кодами ошибок и их описаниями
        """
        return {
            "-32600": "Некорректный запрос",
            "-32601": "Команда не найдена",
            "-32602": "Некорректные параметры",
            "-32603": "Внутренняя ошибка",
            "-32000": "Ошибка выполнения команды"
        }


# Экспортируем доступные инструменты API
available_tools = {
    TSTCommandExecutor.name: TSTCommandExecutor
}


def get_tool_description(tool_name: str, format: str = "json") -> Union[Dict[str, Any], str]:
    """
    Получает описание инструмента API по имени.
    
    Args:
        tool_name: Имя инструмента API
        format: Формат описания (json, markdown, html)
        
    Returns:
        Описание инструмента в указанном формате
        
    Raises:
        NotFoundError: Если инструмент не найден
    """
    if tool_name in available_tools:
        return available_tools[tool_name].get_description(format)
    else:
        raise NotFoundError(f"Инструмент '{tool_name}' не найден")


async def execute_tool(tool_name: str, **params) -> Dict[str, Any]:
    """
    Выполняет инструмент API с указанными параметрами.
    
    Args:
        tool_name: Имя инструмента API
        **params: Параметры инструмента
        
    Returns:
        Результат выполнения инструмента
        
    Raises:
        NotFoundError: Если инструмент не найден
    """
    if tool_name in available_tools:
        return await available_tools[tool_name].execute(**params)
    else:
        raise NotFoundError(f"Инструмент '{tool_name}' не найден") 