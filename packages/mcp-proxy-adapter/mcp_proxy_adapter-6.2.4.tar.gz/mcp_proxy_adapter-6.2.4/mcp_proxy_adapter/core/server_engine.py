"""
Server Engine Abstraction

This module provides an abstraction layer for the hypercorn ASGI server engine,
providing full mTLS support and SSL capabilities.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ServerEngine(ABC):
    """
    Abstract base class for server engines.
    
    This class defines the interface that all server engines must implement,
    allowing the framework to work with different ASGI servers transparently.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the server engine."""
        pass
    
    @abstractmethod
    def get_supported_features(self) -> Dict[str, bool]:
        """
        Get supported features of this server engine.
        
        Returns:
            Dictionary mapping feature names to boolean support status
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get configuration schema for this server engine.
        
        Returns:
            Dictionary describing the configuration options
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for this server engine.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def run_server(self, app: Any, config: Dict[str, Any]) -> None:
        """
        Run the server with the given configuration.
        
        Args:
            app: ASGI application
            config: Server configuration
        """
        pass


class HypercornEngine(ServerEngine):
    """
    Hypercorn server engine implementation.
    
    Provides full mTLS support and better SSL capabilities.
    """
    
    def get_name(self) -> str:
        return "hypercorn"
    
    def get_supported_features(self) -> Dict[str, bool]:
        return {
            "ssl_tls": True,
            "mtls_client_certs": True,   # Full support
            "ssl_scope_info": True,      # SSL info in request scope
            "client_cert_verification": True,
            "websockets": True,
            "http2": True,
            "reload": True
        }
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "host": {"type": "string", "default": "127.0.0.1"},
            "port": {"type": "integer", "default": 8000},
            "log_level": {"type": "string", "default": "INFO"},
            "certfile": {"type": "string", "optional": True},
            "keyfile": {"type": "string", "optional": True},
            "ca_certs": {"type": "string", "optional": True},
            "verify_mode": {"type": "string", "optional": True},
            "reload": {"type": "boolean", "default": False},
            "workers": {"type": "integer", "optional": True}
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate hypercorn configuration."""
        required_fields = ["host", "port"]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate SSL files exist if specified
        ssl_files = ["certfile", "keyfile", "ca_certs"]
        for ssl_file in ssl_files:
            if ssl_file in config and config[ssl_file]:
                if not Path(config[ssl_file]).exists():
                    logger.error(f"SSL file not found: {config[ssl_file]}")
                    return False
        
        return True
    
    def run_server(self, app: Any, config: Dict[str, Any]) -> None:
        """Run hypercorn server."""
        try:
            import hypercorn.asyncio
            import asyncio
            
            # Prepare hypercorn config
            hypercorn_config = {
                "bind": f"{config.get('host', '127.0.0.1')}:{config.get('port', 8000)}",
                "log_level": config.get("log_level", "INFO"),
                "reload": config.get("reload", False)
            }
            
            # Add SSL configuration if provided
            logger.info(f"🔍 DEBUG: Input config keys: {list(config.keys())}")
            logger.info(f"🔍 DEBUG: Input config certfile: {config.get('certfile', 'NOT_FOUND')}")
            logger.info(f"🔍 DEBUG: Input config keyfile: {config.get('keyfile', 'NOT_FOUND')}")
            logger.info(f"🔍 DEBUG: Input config ca_certs: {config.get('ca_certs', 'NOT_FOUND')}")
            logger.info(f"🔍 DEBUG: Input config verify_mode: {config.get('verify_mode', 'NOT_FOUND')}")
            
            if "certfile" in config and config["certfile"]:
                hypercorn_config["certfile"] = config["certfile"]
            if "keyfile" in config and config["keyfile"]:
                hypercorn_config["keyfile"] = config["keyfile"]
            if "ca_certs" in config and config["ca_certs"]:
                hypercorn_config["ca_certs"] = config["ca_certs"]
            if "verify_mode" in config and config["verify_mode"]:
                # Convert verify_mode string to SSL constant
                verify_mode_str = config["verify_mode"]
                if verify_mode_str == "CERT_NONE":
                    import ssl
                    hypercorn_config["verify_mode"] = ssl.CERT_NONE
                elif verify_mode_str == "CERT_REQUIRED":
                    import ssl
                    hypercorn_config["verify_mode"] = ssl.CERT_REQUIRED
                elif verify_mode_str == "CERT_OPTIONAL":
                    import ssl
                    hypercorn_config["verify_mode"] = ssl.CERT_OPTIONAL
                else:
                    hypercorn_config["verify_mode"] = verify_mode_str
            
            # Add workers if specified
            if "workers" in config and config["workers"]:
                hypercorn_config["workers"] = config["workers"]
            
            logger.info(f"Starting hypercorn server with config: {hypercorn_config}")
            logger.info(f"SSL config from input: {config.get('ssl', 'NOT_FOUND')}")
            logger.info(f"Security SSL config: {config.get('security', {}).get('ssl', 'NOT_FOUND')}")
            logger.info(f"🔍 DEBUG: Hypercorn verify_mode: {hypercorn_config.get('verify_mode', 'NOT_SET')}")
            logger.info(f"🔍 DEBUG: Hypercorn ca_certs: {hypercorn_config.get('ca_certs', 'NOT_SET')}")
            
            # Create config object
            config_obj = hypercorn.Config()
            for key, value in hypercorn_config.items():
                setattr(config_obj, key, value)
            
            # Run server
            asyncio.run(hypercorn.asyncio.serve(app, config_obj))
            
        except ImportError:
            logger.error("hypercorn not installed. Install with: pip install hypercorn")
            raise
        except Exception as e:
            logger.error(f"Failed to start hypercorn server: {e}")
            raise


class ServerEngineFactory:
    """
    Factory for creating server engines.
    
    This class manages the creation and configuration of different server engines.
    """
    
    _engines: Dict[str, ServerEngine] = {}
    
    @classmethod
    def register_engine(cls, engine: ServerEngine) -> None:
        """
        Register a server engine.
        
        Args:
            engine: Server engine instance to register
        """
        cls._engines[engine.get_name()] = engine
        logger.info(f"Registered server engine: {engine.get_name()}")
    
    @classmethod
    def get_engine(cls, name: str) -> Optional[ServerEngine]:
        """
        Get a server engine by name.
        
        Args:
            name: Name of the server engine
            
        Returns:
            Server engine instance or None if not found
        """
        return cls._engines.get(name)
    
    @classmethod
    def get_available_engines(cls) -> Dict[str, ServerEngine]:
        """
        Get all available server engines.
        
        Returns:
            Dictionary mapping engine names to engine instances
        """
        return cls._engines.copy()
    
    @classmethod
    def get_engine_with_feature(cls, feature: str) -> Optional[ServerEngine]:
        """
        Get the first available engine that supports a specific feature.
        
        Args:
            feature: Name of the feature to check
            
        Returns:
            Server engine that supports the feature or None
        """
        for engine in cls._engines.values():
            if engine.get_supported_features().get(feature, False):
                return engine
        return None
    
    @classmethod
    def initialize_default_engines(cls) -> None:
        """Initialize default server engines."""
        # Register hypercorn engine (only supported engine)
        try:
            import hypercorn
            cls.register_engine(HypercornEngine())
            logger.info("Hypercorn engine registered (full mTLS support available)")
        except ImportError:
            logger.error("Hypercorn not available - this is required for the framework")
            raise


# Initialize default engines
ServerEngineFactory.initialize_default_engines()
