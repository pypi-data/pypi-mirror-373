"""
SSL Setup Command

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Command for SSL/TLS configuration and certificate management.
"""

import logging
import ssl
from typing import Dict, Any, Optional

# Import mcp_security_framework
try:
    from mcp_security_framework.core.ssl_manager import SSLManager
    from mcp_security_framework.schemas.config import SSLConfig
    from mcp_security_framework.utils.cert_utils import validate_certificate_chain
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False

from .base import Command
from .result import SuccessResult, ErrorResult
from ..config import Config

logger = logging.getLogger(__name__)


class SSLSetupCommand(Command):
    """
    SSL Setup Command
    
    Handles SSL/TLS configuration and certificate management.
    """
    
    # Command metadata
    name = "ssl_setup"
    version = "1.0.0"
    descr = "Configure SSL/TLS settings and manage certificates"
    category = "security"
    author = "MCP Proxy Adapter Team"
    email = "team@mcp-proxy-adapter.com"
    source_url = "https://github.com/mcp-proxy-adapter"
    result_class = SuccessResult
    
    def __init__(self):
        """Initialize SSL Setup Command."""
        super().__init__()
    
    async def execute(self, **kwargs) -> SuccessResult | ErrorResult:
        """
        Execute SSL setup command.
        
        Args:
            params: Command parameters including:
                - action: Operation to perform (get, set, update, reset, test)
                - config_data: Configuration data for set/update actions
                - cert_file: Certificate file path for testing
                - key_file: Private key file path for testing
                
        Returns:
            SuccessResult or ErrorResult
        """
        try:
            action = kwargs.get("action", "get")
            
            if action == "get":
                return await self._get_ssl_config()
            elif action == "set":
                return await self._set_ssl_config(kwargs.get("config_data", {}))
            elif action == "update":
                return await self._update_ssl_config(kwargs.get("config_data", {}))
            elif action == "reset":
                return await self._reset_ssl_config()
            elif action == "test":
                return await self._test_ssl_config(
                    kwargs.get("cert_file"),
                    kwargs.get("key_file")
                )
            else:
                return ErrorResult(
                    message=f"Unknown action: {action}. Supported actions: get, set, update, reset, test"
                )
                
        except Exception as e:
            logger.error(f"SSL setup command failed: {e}")
            return ErrorResult(
                message=f"SSL setup command failed: {str(e)}"
            )
    
    async def _get_ssl_config(self) -> SuccessResult | ErrorResult:
        """Get current SSL configuration."""
        try:
            config = Config()
            ssl_config = config.get("ssl", {})
            
            # Add framework information
            ssl_config["framework_available"] = SECURITY_FRAMEWORK_AVAILABLE
            
            return SuccessResult(
                data={"ssl_config": ssl_config}
            )
            
        except Exception as e:
            logger.error(f"Failed to get SSL config: {e}")
            return ErrorResult(
                message=f"Failed to get SSL config: {str(e)}"
            )
            
    async def _set_ssl_config(self, config_data: Dict[str, Any]) -> SuccessResult | ErrorResult:
        """Set SSL configuration."""
        try:
            if not isinstance(config_data, dict):
                return ErrorResult(
                    message="Configuration data must be a dictionary"
                )
            
            # Validate configuration if mcp_security_framework is available
            if SECURITY_FRAMEWORK_AVAILABLE:
                try:
                    ssl_config = SSLConfig(**config_data)
                    config_data = ssl_config.dict()
                except Exception as e:
                    return ErrorResult(
                        message=f"Invalid SSL configuration: {str(e)}"
                    )
            
            # Update configuration
            config = Config()
            config.update_config({"ssl": config_data})
            
            return SuccessResult(
                data={"message": "SSL configuration updated", "ssl_config": config_data}
            )
            
        except Exception as e:
            logger.error(f"Failed to set SSL config: {e}")
            return ErrorResult(
                message=f"Failed to set SSL config: {str(e)}"
            )
    
    async def _update_ssl_config(self, config_data: Dict[str, Any]) -> SuccessResult | ErrorResult:
        """Update SSL configuration."""
        try:
            if not isinstance(config_data, dict):
                return ErrorResult(
                    message="Configuration data must be a dictionary"
                )
            
            config = Config()
            current_config = config.get("ssl", {})
            
            # Update with new data
            current_config.update(config_data)
            
            # Validate configuration if mcp_security_framework is available
            if SECURITY_FRAMEWORK_AVAILABLE:
                try:
                    ssl_config = SSLConfig(**current_config)
                    current_config = ssl_config.dict()
                except Exception as e:
                    return ErrorResult(
                        message=f"Invalid SSL configuration: {str(e)}"
                    )
            
            # Update configuration
            config.update_config({"ssl": current_config})
            
            return SuccessResult(
                data={"message": "SSL configuration updated", "ssl_config": current_config}
            )
            
        except Exception as e:
            logger.error(f"Failed to update SSL config: {e}")
            return ErrorResult(
                message=f"Failed to update SSL config: {str(e)}"
            )
    
    async def _reset_ssl_config(self) -> SuccessResult | ErrorResult:
        """Reset SSL configuration to defaults."""
        try:
            default_config = {
                "enabled": False,
                "cert_file": None,
                "key_file": None,
                "ca_file": None,
                "verify_mode": "CERT_REQUIRED",
                "cipher_suites": [],
                "framework_available": SECURITY_FRAMEWORK_AVAILABLE
            }
            
            config = Config()
            config.update_config({"ssl": default_config})
            
            return SuccessResult(
                data={"message": "SSL configuration reset to defaults", "ssl_config": default_config}
            )
            
        except Exception as e:
            logger.error(f"Failed to reset SSL config: {e}")
            return ErrorResult(
                message=f"Failed to reset SSL config: {str(e)}"
            )
    
    async def _test_ssl_config(self, cert_file: Optional[str], key_file: Optional[str]) -> SuccessResult | ErrorResult:
        """
        Test SSL configuration.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            
        Returns:
            SuccessResult or ErrorResult with test results
        """
        try:
            if not cert_file or not key_file:
                return ErrorResult(
                    message="Both cert_file and key_file are required for testing"
                )
            
            if SECURITY_FRAMEWORK_AVAILABLE:
                return await self._test_ssl_config_with_framework(cert_file, key_file)
            else:
                return await self._test_ssl_config_fallback(cert_file, key_file)
                
        except Exception as e:
            logger.error(f"Failed to test SSL config: {e}")
            return ErrorResult(
                message=f"Failed to test SSL config: {str(e)}"
            )
    
    async def _test_ssl_config_with_framework(self, cert_file: str, key_file: str) -> SuccessResult | ErrorResult:
        """Test SSL configuration using mcp_security_framework."""
        try:
            # Create SSL manager
            ssl_config = SSLConfig(
                cert_file=cert_file,
                key_file=key_file,
                enabled=True
            )
            
            ssl_manager = SSLManager(ssl_config)
            
            # Test SSL context creation
            context = ssl_manager.create_server_ssl_context()
            
            details = {
                "framework": "mcp_security_framework",
                "certificate_loaded": True,
                "private_key_loaded": True,
                "context_created": True,
                "cert_file": cert_file,
                "key_file": key_file
            }
            
            return SuccessResult(
                data={
                    "success": True,
                    "details": details
                }
            )
                
        except Exception as e:
            return ErrorResult(
                message=f"SSL test failed: {str(e)}",
                data={
                    "success": False,
                    "error": str(e),
                    "details": {
                        "framework": "mcp_security_framework",
                        "certificate_loaded": False,
                        "private_key_loaded": False,
                        "context_created": False
                    }
                }
            )
    
    async def _test_ssl_config_fallback(self, cert_file: str, key_file: str) -> SuccessResult | ErrorResult:
        """Test SSL configuration using fallback method."""
        try:
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Load certificate and key
            context.load_cert_chain(cert_file, key_file)
            
            # Test basic SSL functionality
            details = {
                "framework": "fallback (ssl module)",
                "ssl_version": ssl.OPENSSL_VERSION,
                "certificate_loaded": True,
                "private_key_loaded": True,
                "context_created": True,
                "cert_file": cert_file,
                "key_file": key_file
            }
            
            return SuccessResult(
                data={
                "success": True,
                "details": details
            }
            )
            
        except Exception as e:
            return ErrorResult(
                message=f"SSL test failed: {str(e)}",
                data={
                "success": False,
                "error": str(e),
                "details": {
                        "framework": "fallback (ssl module)",
                    "ssl_version": ssl.OPENSSL_VERSION,
                    "certificate_loaded": False,
                    "private_key_loaded": False,
                    "context_created": False
                }
                }
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "framework_available": SECURITY_FRAMEWORK_AVAILABLE
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get", "set", "update", "reset", "test"],
                    "description": "Action to perform"
                },
                "config_data": {
                    "type": "object",
                    "description": "SSL configuration data",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "cert_file": {"type": "string"},
                        "key_file": {"type": "string"},
                        "ca_file": {"type": "string"},
                        "verify_mode": {"type": "string"},
                        "cipher_suites": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "cert_file": {
                    "type": "string",
                    "description": "Certificate file path for testing"
                },
                "key_file": {
                    "type": "string",
                    "description": "Private key file path for testing"
                }
            },
            "required": ["action"]
            } 