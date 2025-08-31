"""
SSL Setup Command

This module provides commands for SSL configuration and management including
setup, status checking, testing, and configuration management.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
import os
import ssl
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base import Command
from .result import CommandResult, SuccessResult, ErrorResult
from ..core.certificate_utils import CertificateUtils
from ..core.auth_validator import AuthValidator

logger = logging.getLogger(__name__)


class SSLSetupResult:
    """
    Result class for SSL setup operations.
    
    Contains SSL configuration status and details.
    """
    
    def __init__(self, ssl_enabled: bool, cert_path: Optional[str] = None,
                 key_path: Optional[str] = None, config: Optional[Dict] = None,
                 status: str = "unknown", error: Optional[str] = None):
        """
        Initialize SSL setup result.
        
        Args:
            ssl_enabled: Whether SSL is enabled
            cert_path: Path to certificate file
            key_path: Path to private key file
            config: SSL configuration
            status: SSL status (enabled, disabled, error)
            error: Error message if any
        """
        self.ssl_enabled = ssl_enabled
        self.cert_path = cert_path
        self.key_path = key_path
        self.config = config or {}
        self.status = status
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "ssl_enabled": self.ssl_enabled,
            "cert_path": self.cert_path,
            "key_path": self.key_path,
            "config": self.config,
            "status": self.status,
            "error": self.error
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for this result.
        
        Returns:
            JSON schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "ssl_enabled": {"type": "boolean", "description": "Whether SSL is enabled"},
                "cert_path": {"type": "string", "description": "Path to certificate file"},
                "key_path": {"type": "string", "description": "Path to private key file"},
                "config": {"type": "object", "description": "SSL configuration"},
                "status": {"type": "string", "enum": ["enabled", "disabled", "error"], 
                          "description": "SSL status"},
                "error": {"type": "string", "description": "Error message if any"}
            },
            "required": ["ssl_enabled", "status"]
        }


class SSLSetupCommand(Command):
    """
    Command for SSL setup and configuration.
    
    Provides methods for SSL setup, status checking, testing, and configuration.
    """
    
    # Command metadata
    name = "ssl_setup"
    version = "1.0.0"
    descr = "SSL setup and configuration management"
    category = "security"
    author = "MCP Proxy Adapter Team"
    email = "team@mcp-proxy-adapter.com"
    source_url = "https://github.com/mcp-proxy-adapter"
    result_class = SSLSetupResult
    
    def __init__(self):
        """Initialize SSL setup command."""
        super().__init__()
        self.certificate_utils = CertificateUtils()
        self.auth_validator = AuthValidator()
    
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute SSL setup command.
        
        Args:
            **kwargs: Command parameters including:
                - action: Action to perform (ssl_setup, ssl_status, ssl_test, ssl_config)
                - ssl_config: SSL configuration for ssl_setup action
                - cert_file: Certificate file path for ssl_test action
                - key_file: Key file path for ssl_test action
                - action: Action for ssl_config (get, set, update, reset)
                - config_data: Configuration data for ssl_config action
                
        Returns:
            CommandResult with SSL operation status
        """
        action = kwargs.get("action", "ssl_status")
        
        if action == "ssl_setup":
            ssl_config = kwargs.get("ssl_config", {})
            return await self.ssl_setup(ssl_config)
        elif action == "ssl_status":
            return await self.ssl_status()
        elif action == "ssl_test":
            cert_file = kwargs.get("cert_file")
            key_file = kwargs.get("key_file")
            return await self.ssl_test(cert_file, key_file)
        elif action == "ssl_config":
            config_action = kwargs.get("config_action", "get")
            config_data = kwargs.get("config_data", {})
            return await self.ssl_config(config_action, config_data)
        else:
            return ErrorResult(
                message=f"Unknown action: {action}. Supported actions: ssl_setup, ssl_status, ssl_test, ssl_config"
            )
    
    async def ssl_setup(self, ssl_config: Dict[str, Any]) -> CommandResult:
        """
        Setup SSL configuration.
        
        Args:
            ssl_config: SSL configuration dictionary containing:
                - enabled: Whether to enable SSL
                - cert_file: Path to certificate file
                - key_file: Path to private key file
                - ca_file: Path to CA certificate file (optional)
                - verify_mode: SSL verification mode (optional)
                - cipher_suites: List of allowed cipher suites (optional)
                
        Returns:
            CommandResult with SSL setup status
        """
        try:
            logger.info("Setting up SSL configuration")
            
            # Validate SSL configuration
            if not isinstance(ssl_config, dict):
                return ErrorResult(
                    message="SSL configuration must be a dictionary"
                )
            
            enabled = ssl_config.get("enabled", False)
            if not enabled:
                result = SSLSetupResult(
                    ssl_enabled=False,
                    status="disabled",
                    config=ssl_config
                )
                return SuccessResult(data=result.to_dict())
            
            # Validate required files
            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            
            if not cert_file or not key_file:
                return ErrorResult(
                    message="Certificate and key files are required when SSL is enabled"
                )
            
            # Check if files exist
            if not os.path.exists(cert_file):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_file}"
                )
            
            if not os.path.exists(key_file):
                return ErrorResult(
                    message=f"Private key file not found: {key_file}"
                )
            
            # Validate certificate and key
            cert_validation = self.auth_validator.validate_certificate(cert_file)
            if not cert_validation.is_valid:
                return ErrorResult(
                    message=f"Certificate validation failed: {cert_validation.error_message}"
                )
            
            # Test SSL configuration
            test_result = await self._test_ssl_config(cert_file, key_file)
            if not test_result["success"]:
                return ErrorResult(
                    message=f"SSL configuration test failed: {test_result['error']}"
                )
            
            result = SSLSetupResult(
                ssl_enabled=True,
                cert_path=cert_file,
                key_path=key_file,
                config=ssl_config,
                status="enabled"
            )
            
            logger.info("SSL configuration setup completed successfully")
            return SuccessResult(data=result.to_dict())
            
        except Exception as e:
            logger.error(f"SSL setup failed: {e}")
            return ErrorResult(
                message=f"SSL setup failed: {str(e)}"
            )
    
    async def ssl_status(self) -> CommandResult:
        """
        Get current SSL status.
        
        Returns:
            CommandResult with SSL status information
        """
        try:
            logger.info("Checking SSL status")
            
            # Check if SSL is configured in the application
            from ...config import Config
            config = Config()
            
            ssl_config = config.get("ssl", {})
            enabled = ssl_config.get("enabled", False)
            
            if not enabled:
                result = SSLSetupResult(
                    ssl_enabled=False,
                    status="disabled",
                    config=ssl_config
                )
                return SuccessResult(data=result.to_dict())
            
            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            
            # Check file existence
            cert_exists = os.path.exists(cert_file) if cert_file else False
            key_exists = os.path.exists(key_file) if key_file else False
            
            if not cert_exists or not key_exists:
                result = SSLSetupResult(
                    ssl_enabled=False,
                    status="error",
                    cert_path=cert_file,
                    key_path=key_file,
                    config=ssl_config,
                    error="Certificate or key file not found"
                )
                return SuccessResult(data=result.to_dict())
            
            # Validate certificate
            cert_validation = self.auth_validator.validate_certificate(cert_file)
            if not cert_validation.is_valid:
                result = SSLSetupResult(
                    ssl_enabled=False,
                    status="error",
                    cert_path=cert_file,
                    key_path=key_file,
                    config=ssl_config,
                    error=f"Certificate validation failed: {cert_validation.error_message}"
                )
                return SuccessResult(data=result.to_dict())
            
            result = SSLSetupResult(
                ssl_enabled=True,
                cert_path=cert_file,
                key_path=key_file,
                config=ssl_config,
                status="enabled"
            )
            
            logger.info("SSL status check completed")
            return SuccessResult(data=result.to_dict())
            
        except Exception as e:
            logger.error(f"SSL status check failed: {e}")
            return ErrorResult(
                message=f"SSL status check failed: {str(e)}"
            )
    
    async def ssl_test(self, cert_file: str, key_file: str) -> CommandResult:
        """
        Test SSL configuration with certificate and key files.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            
        Returns:
            CommandResult with test results
        """
        try:
            logger.info(f"Testing SSL configuration with cert: {cert_file}, key: {key_file}")
            
            # Validate parameters
            if not cert_file or not key_file:
                return ErrorResult(
                    message="Certificate and key file paths are required"
                )
            
            # Check file existence
            if not os.path.exists(cert_file):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_file}"
                )
            
            if not os.path.exists(key_file):
                return ErrorResult(
                    message=f"Private key file not found: {key_file}"
                )
            
            # Test SSL configuration
            test_result = await self._test_ssl_config(cert_file, key_file)
            
            if test_result["success"]:
                logger.info("SSL configuration test passed")
                return SuccessResult(
                    data={
                        "test_passed": True,
                        "cert_file": cert_file,
                        "key_file": key_file,
                        "details": test_result["details"]
                    }
                )
            else:
                logger.error(f"SSL configuration test failed: {test_result['error']}")
                return ErrorResult(
                    message=test_result["error"]
                )
                
        except Exception as e:
            logger.error(f"SSL test failed: {e}")
            return ErrorResult(
                message=f"SSL test failed: {str(e)}"
            )
    
    async def ssl_config(self, action: str, config_data: Dict[str, Any]) -> CommandResult:
        """
        Manage SSL configuration.
        
        Args:
            action: Action to perform (get, set, update, reset)
            config_data: Configuration data for the action
            
        Returns:
            CommandResult with configuration operation result
        """
        try:
            logger.info(f"Performing SSL config action: {action}")
            
            from ...config import Config
            config = Config()
            
            if action == "get":
                ssl_config = config.get("ssl", {})
                return SuccessResult(
                    data={"ssl_config": ssl_config}
                )
            
            elif action == "set":
                # Validate configuration
                if not isinstance(config_data, dict):
                    return ErrorResult(
                        message="Configuration data must be a dictionary"
                    )
                
                # Update configuration
                config.update_config({"ssl": config_data})
                return SuccessResult(
                    data={"message": "SSL configuration updated", "ssl_config": config_data}
                )
            
            elif action == "update":
                # Get current configuration
                current_config = config.get("ssl", {})
                
                # Update with new data
                current_config.update(config_data)
                
                # Update configuration
                config.update_config({"ssl": current_config})
                return SuccessResult(
                    data={"message": "SSL configuration updated", "ssl_config": current_config}
                )
            
            elif action == "reset":
                # Reset to default configuration
                default_config = {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_file": None,
                    "verify_mode": "CERT_REQUIRED",
                    "cipher_suites": []
                }
                
                config.update_config({"ssl": default_config})
                return SuccessResult(
                    data={"message": "SSL configuration reset to defaults", "ssl_config": default_config}
                )
            
            else:
                return ErrorResult(
                    message=f"Unknown action: {action}. Supported actions: get, set, update, reset"
                )
                
        except Exception as e:
            logger.error(f"SSL config action failed: {e}")
            return ErrorResult(
                message=f"SSL config action failed: {str(e)}"
            )
    
    async def _test_ssl_config(self, cert_file: str, key_file: str) -> Dict[str, Any]:
        """
        Test SSL configuration internally.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            
        Returns:
            Dictionary with test results
        """
        try:
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Load certificate and key
            context.load_cert_chain(cert_file, key_file)
            
            # Test basic SSL functionality
            details = {
                "ssl_version": ssl.OPENSSL_VERSION,
                "certificate_loaded": True,
                "private_key_loaded": True,
                "context_created": True
            }
            
            return {
                "success": True,
                "details": details
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "ssl_version": ssl.OPENSSL_VERSION,
                    "certificate_loaded": False,
                    "private_key_loaded": False,
                    "context_created": False
                }
            } 