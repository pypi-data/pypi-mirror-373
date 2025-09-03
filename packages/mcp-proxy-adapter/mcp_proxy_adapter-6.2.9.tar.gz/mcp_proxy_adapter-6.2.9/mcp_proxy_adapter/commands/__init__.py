"""
Commands module initialization file.
"""

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.command_registry import registry, CommandRegistry
from mcp_proxy_adapter.commands.dependency_container import container, DependencyContainer
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult, ErrorResult
from mcp_proxy_adapter.commands.auth_validation_command import AuthValidationCommand
from mcp_proxy_adapter.commands.ssl_setup_command import SSLSetupCommand
from mcp_proxy_adapter.commands.certificate_management_command import CertificateManagementCommand
from mcp_proxy_adapter.commands.key_management_command import KeyManagementCommand
from mcp_proxy_adapter.commands.cert_monitor_command import CertMonitorCommand
from mcp_proxy_adapter.commands.transport_management_command import TransportManagementCommand
from mcp_proxy_adapter.commands.role_test_command import RoleTestCommand
from mcp_proxy_adapter.commands.echo_command import EchoCommand
from mcp_proxy_adapter.commands.proxy_registration_command import ProxyRegistrationCommand

__all__ = [
    "Command",
    "CommandResult",
    "SuccessResult", 
    "ErrorResult",
    "registry",
    "CommandRegistry",
    "container",
    "DependencyContainer",
    "AuthValidationCommand",
    "SSLSetupCommand",
    "CertificateManagementCommand",
    "KeyManagementCommand",
    "CertMonitorCommand",
    "TransportManagementCommand",
    "RoleTestCommand",
    "EchoCommand",
    "ProxyRegistrationCommand"
]
