"""
Module with help command implementation.
"""

from typing import Dict, Any, Optional
import logging
import traceback

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import NotFoundError

# Добавляем логирование
logger = logging.getLogger("mcp_proxy_adapter.commands.help_command")


class HelpResult(CommandResult):
    """
    Result of the help command execution.
    """

    def __init__(self, commands_info: Optional[Dict[str, Any]] = None, command_info: Optional[Dict[str, Any]] = None):
        """
        Initialize help command result.

        Args:
            commands_info: Information about all commands (for request without parameters)
            command_info: Information about a specific command (for request with cmdname parameter)
        """
        logger.debug(f"HelpResult.__init__: commands_info={commands_info is not None}, command_info={command_info is not None}")
        self.commands_info = commands_info
        self.command_info = command_info

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.

        Returns:
            Dict[str, Any]: Result as dictionary
        """
        try:
            logger.debug(f"HelpResult.to_dict: command_info={self.command_info is not None}, commands_info={self.commands_info is not None}")

            # Защита от None для self.command_info
            if self.command_info is not None:
                logger.debug(f"HelpResult.to_dict: returning command_info for {self.command_info.get('name', 'unknown')}")
                # Делаем безопасное получение всех полей с дефолтными значениями
                metadata = self.command_info.get("metadata", {})
                schema = self.command_info.get("schema", {})
                return {
                    "cmdname": self.command_info.get("name", "unknown"),
                    "info": {
                        "description": metadata.get("description", ""),
                        "summary": metadata.get("summary", ""),
                        "params": schema.get("properties", {}),
                        "examples": metadata.get("examples", [])
                    }
                }

            # Защита от None для self.commands_info
            if self.commands_info is None:
                logger.warning("HelpResult.to_dict: commands_info is None, создаем пустой результат")
                # Возвращаем пустой список команд вместо ошибки
                return {
                    "tool_info": {
                        "name": "MCP-Proxy API Service",
                        "description": "JSON-RPC API for microservice command execution",
                        "version": "1.0.0"
                    },
                    "help_usage": {
                        "description": "Get information about commands",
                        "examples": [
                            {"command": "help", "description": "List of all available commands"},
                            {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed information about a specific command"}
                        ]
                    },
                    "commands": {},
                    "total": 0,
                    "note": "To get detailed information about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}"
                }

            # For list of all commands, return as is (already formatted)
            logger.debug(f"HelpResult.to_dict: processing commands_info with {len(self.commands_info.get('commands', {}))} commands")
            result = self.commands_info.copy()

            # Add total count and note about usage
            commands = result.get("commands", {})
            result["total"] = len(commands)
            result["note"] = "To get detailed information about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}"

            logger.debug(f"HelpResult.to_dict: returning result with {result['total']} commands")
            return result
        except Exception as e:
            logger.error(f"Ошибка в HelpResult.to_dict: {e}")
            logger.debug(f"Трассировка: {traceback.format_exc()}")
            # В случае неожиданной ошибки возвращаем базовый ответ вместо ошибки
            return {
                "tool_info": {
                    "name": "MCP-Proxy API Service",
                    "description": "JSON-RPC API for microservice command execution",
                    "version": "1.0.0"
                },
                "commands": {},
                "total": 0,
                "error": str(e)
            }

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result validation.

        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "oneOf": [
                {
                    "properties": {
                        "commands": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "tool_info": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "version": {"type": "string"}
                            }
                        },
                        "help_usage": {
                            "type": "object"
                        },
                        "total": {"type": "integer"},
                        "note": {"type": "string"}
                    },
                    "required": ["commands"]
                },
                {
                    "properties": {
                        "cmdname": {"type": "string"},
                        "info": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "summary": {"type": "string"},
                                "params": {"type": "object"},
                                "examples": {"type": "array"}
                            }
                        }
                    },
                    "required": ["cmdname", "info"]
                }
            ]
        }


class HelpCommand(Command):
    """
    Command for getting help information about available commands.
    """

    name = "help"
    result_class = HelpResult

    async def execute(self, cmdname: Optional[str] = None, **kwargs) -> HelpResult:
        """
        Execute help command.

        Args:
            cmdname: Name of the command to get information about (optional)
            **kwargs: Any additional parameters (will be ignored)

        Returns:
            HelpResult: Help command result

        Raises:
            NotFoundError: If specified command not found
        """
        logger.debug(f"HelpCommand.execute начало: cmdname={cmdname}, kwargs={kwargs}")

        try:
            # Handle case when cmdname is provided
            if cmdname is not None and cmdname != "":
                logger.debug(f"Обработка запроса для конкретной команды: {cmdname}")
                try:
                    # Get command info from registry
                    command_info = registry.get_command_info(cmdname)
                    if command_info is None:
                        raise NotFoundError(f"Command '{cmdname}' not found")
                    logger.debug(f"Получены метаданные для команды {cmdname}")
                    return HelpResult(command_info=command_info)
                except NotFoundError:
                    logger.warning(f"Команда '{cmdname}' не найдена")
                    # Получаем список всех команд
                    all_commands = list(registry.get_all_commands().keys())
                    if all_commands:
                        example_cmd = all_commands[0]
                        example = {
                            "command": "help",
                            "params": {"cmdname": example_cmd}
                        }
                        note = f"Use help with an existing command name to get detailed info. For example: help with cmdname '{example_cmd}'. To list all commands: call help without parameters."
                    else:
                        example = {"command": "help"}
                        note = "No commands registered. To list all commands: call help without parameters."
                    return HelpResult(commands_info={
                        "commands": {},
                        "error": f"Command '{cmdname}' not found",
                        "example": example,
                        "note": note
                    })

            # Otherwise, return information about all available commands
            logger.debug("Обработка запроса для всех команд")

            # Get info for all commands
            all_commands_info = registry.get_all_commands_info()
            logger.debug(f"Получены метаданные для {len(all_commands_info.get('commands', {}))} команд")

            # Prepare response format with tool metadata
            result = {
                "tool_info": {
                    "name": "MCP-Proxy API Service",
                    "description": "JSON-RPC API for microservice command execution",
                    "version": "1.0.0"
                },
                "help_usage": {
                    "description": "Get information about commands",
                    "examples": [
                        {"command": "help", "description": "List of all available commands"},
                        {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed information about a specific command"}
                    ]
                },
                "commands": {}
            }

            # Add brief information about commands
            commands_data = all_commands_info.get("commands", {})
            for name, command_info in commands_data.items():
                try:
                    logger.debug(f"Обработка метаданных команды {name}")
                    # Безопасное получение параметров с проверкой на наличие ключей
                    metadata = command_info.get("metadata", {})
                    schema = command_info.get("schema", {})
                    result["commands"][name] = {
                        "summary": metadata.get("summary", ""),
                        "params_count": len(schema.get("properties", {}))
                    }
                except Exception as e:
                    logger.error(f"Ошибка при обработке метаданных команды {name}: {e}")
                    logger.debug(f"Метаданные команды {name}: {command_info}")
                    # Пропускаем проблемную команду
                    continue

            logger.debug(f"HelpCommand.execute завершение: возвращаем результат с {len(result['commands'])} командами")
            return HelpResult(commands_info=result)
        except Exception as e:
            logger.error(f"Неожиданная ошибка в HelpCommand.execute: {e}")
            logger.debug(f"Трассировка: {traceback.format_exc()}")
            # В случае неожиданной ошибки возвращаем пустой результат вместо ошибки
            return HelpResult(commands_info={
                "tool_info": {
                    "name": "MCP-Proxy API Service",
                    "description": "JSON-RPC API for microservice command execution",
                    "version": "1.0.0"
                },
                "commands": {},
                "error": str(e)
            })

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters validation.

        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "cmdname": {
                    "type": "string",
                    "description": "Name of command to get information about"
                }
            },
            "additionalProperties": False
        } 