"""
Tests for command registry.
"""

import pytest
from unittest.mock import MagicMock, patch

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.core.errors import NotFoundError


class MockResult(CommandResult):
    """Test result class for testing."""
    
    def __init__(self):
        pass
    
    def to_dict(self):
        return {}
    
    @classmethod
    def get_schema(cls):
        return {}


class TestCommand1(Command):
    """First test command."""
    
    name = "test_command1"
    result_class = MockResult
    
    async def execute(self, **kwargs):
        return MockResult()


class TestCommand2(Command):
    """Second test command."""
    
    name = "test_command2"
    result_class = MockResult
    
    async def execute(self, **kwargs):
        return MockResult()


def test_registry_initialization():
    """Test registry initialization."""
    registry = CommandRegistry()
    assert len(registry.get_all_commands()) == 0


def test_register_command():
    """Test registering command."""
    registry = CommandRegistry()
    
    # Register first command
    registry.register_custom(TestCommand1)
    assert len(registry.get_all_commands()) == 1
    assert "test_command1" in registry.get_all_commands()
    
    # Register second command
    registry.register_custom(TestCommand2)
    assert len(registry.get_all_commands()) == 2
    assert "test_command2" in registry.get_all_commands()


def test_register_duplicated_command():
    """Test registering duplicated command."""
    registry = CommandRegistry()
    
    # Register command
    registry.register_custom(TestCommand1)
    
    # Try to register again
    with pytest.raises(ValueError):
        registry.register_custom(TestCommand1)


def test_register_command_without_name():
    """Test registering command without name attribute."""
    registry = CommandRegistry()
    
    # Create command without name
    class CommandWithoutName(Command):
        result_class = MockResult
        
        async def execute(self, **kwargs):
            return MockResult()
    
    # Register command
    registry.register_custom(CommandWithoutName)
    
    # Check if registered with class name
    assert "commandwithoutname" in registry.get_all_commands()


def test_clear_registry():
    """Test clearing registry."""
    registry = CommandRegistry()
    
    # Register commands
    registry.register_custom(TestCommand1)
    registry.register_custom(TestCommand2)
    assert len(registry.get_all_commands()) == 2
    
    # Clear registry
    registry.clear()
    assert len(registry.get_all_commands()) == 0


def test_get_command():
    """Test getting command."""
    registry = CommandRegistry()
    
    # Register command
    registry.register_custom(TestCommand1)
    
    # Get command
    command = registry.get_command("test_command1")
    assert command == TestCommand1


def test_get_nonexistent_command():
    """Test getting nonexistent command."""
    registry = CommandRegistry()
    
    # Try to get nonexistent command
    with pytest.raises(NotFoundError):
        registry.get_command("nonexistent")


def test_get_all_commands():
    """Test getting all commands."""
    registry = CommandRegistry()
    
    # Register commands
    registry.register_custom(TestCommand1)
    registry.register_custom(TestCommand2)
    
    # Get all commands
    commands = registry.get_all_commands()
    assert len(commands) == 2
    assert "test_command1" in commands
    assert "test_command2" in commands
    assert commands["test_command1"] == TestCommand1
    assert commands["test_command2"] == TestCommand2


def test_get_command_info():
    """Test getting command info."""
    registry = CommandRegistry()
    
    # Register command
    registry.register_custom(TestCommand1)
    
    # Get command info
    info = registry.get_command_info("test_command1")
    
    # Check info structure
    assert info["name"] == "test_command1"
    assert "metadata" in info
    assert "schema" in info


def test_get_all_commands_info():
    """Test getting all commands info."""
    registry = CommandRegistry()
    
    # Register commands
    registry.register_custom(TestCommand1)
    registry.register_custom(TestCommand2)
    
    # Get all commands info
    info = registry.get_all_commands_info()
    
    # Check info structure
    assert "commands" in info
    assert info["total"] == 2
    assert "test_command1" in info["commands"]
    assert "test_command2" in info["commands"]
    assert info["commands"]["test_command1"]["name"] == "test_command1"
    assert info["commands"]["test_command2"]["name"] == "test_command2"


def test_register_command_instance():
    """Test registering a command instance (with dependencies)."""
    registry = CommandRegistry()

    class Service:
        def __init__(self, value):
            self.value = value

    class CommandWithDependency(Command):
        name = "command_with_dep"
        result_class = MockResult
        def __init__(self, service: Service):
            self.service = service
        async def execute(self, **kwargs):
            # Return the value from the injected service
            result = MockResult()
            result.service_value = self.service.value
            return result

    service = Service(value=42)
    command_instance = CommandWithDependency(service=service)
    registry.register_custom(command_instance)

    # Проверяем, что экземпляр зарегистрирован
    assert registry.has_instance("command_with_dep")
    # Проверяем, что get_command_instance возвращает именно этот экземпляр
    assert registry.get_command_instance("command_with_dep") is command_instance
    # Проверяем, что execute использует внедрённый сервис
    import asyncio
    result = asyncio.run(
        registry.get_command_instance("command_with_dep").execute()
    )
    assert hasattr(result, "service_value")
    assert result.service_value == 42 