"""
Server Configuration Adapter

This module provides adapters for converting configuration between different
server engines and handling SSL configuration mapping.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .server_engine import ServerEngineFactory, ServerEngine

logger = logging.getLogger(__name__)


class ServerConfigAdapter:
    """
    Adapter for converting server configurations between different engines.
    
    This class handles the mapping of configuration parameters between
    different server engines and provides unified configuration management.
    """
    
    @staticmethod
    def convert_ssl_config_for_engine(
        ssl_config: Dict[str, Any], 
        target_engine: str
    ) -> Dict[str, Any]:
        """
        Convert SSL configuration for a specific server engine.
        
        Args:
            ssl_config: Source SSL configuration
            target_engine: Target engine name (uvicorn, hypercorn, etc.)
            
        Returns:
            Converted SSL configuration for the target engine
        """
        engine = ServerEngineFactory.get_engine(target_engine)
        if not engine:
            logger.error(f"Unknown server engine: {target_engine}")
            return {}
        
        if target_engine == "uvicorn":
            return ServerConfigAdapter._convert_to_uvicorn_ssl(ssl_config)
        elif target_engine == "hypercorn":
            return ServerConfigAdapter._convert_to_hypercorn_ssl(ssl_config)
        else:
            logger.warning(f"No SSL conversion available for engine: {target_engine}")
            return {}
    
    @staticmethod
    def _convert_to_uvicorn_ssl(ssl_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SSL configuration to uvicorn format."""
        uvicorn_ssl = {}
        
        # Map SSL parameters
        if ssl_config.get("cert_file"):
            uvicorn_ssl["ssl_certfile"] = ssl_config["cert_file"]
        if ssl_config.get("key_file"):
            uvicorn_ssl["ssl_keyfile"] = ssl_config["key_file"]
        if ssl_config.get("ca_cert"):
            uvicorn_ssl["ssl_ca_certs"] = ssl_config["ca_cert"]
        
        # Map verification mode
        if ssl_config.get("verify_client", False):
            import ssl
            uvicorn_ssl["ssl_cert_reqs"] = ssl.CERT_REQUIRED
        
        logger.debug(f"Converted SSL config to uvicorn: {uvicorn_ssl}")
        return uvicorn_ssl
    
    @staticmethod
    def _convert_to_hypercorn_ssl(ssl_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SSL configuration to hypercorn format."""
        hypercorn_ssl = {}
        
        # Map SSL parameters
        if ssl_config.get("cert_file"):
            hypercorn_ssl["certfile"] = ssl_config["cert_file"]
        if ssl_config.get("key_file"):
            hypercorn_ssl["keyfile"] = ssl_config["key_file"]
        if ssl_config.get("ca_cert"):
            hypercorn_ssl["ca_certs"] = ssl_config["ca_cert"]
        
        # Map verification mode
        if ssl_config.get("verify_client", False):
            hypercorn_ssl["verify_mode"] = "CERT_REQUIRED"
        
        logger.debug(f"Converted SSL config to hypercorn: {hypercorn_ssl}")
        return hypercorn_ssl
    
    @staticmethod
    def get_optimal_engine_for_config(config: Dict[str, Any]) -> Optional[str]:
        """
        Determine the optimal server engine for a given configuration.
        
        Args:
            config: Server configuration
            
        Returns:
            Name of the optimal engine or None if no suitable engine found
        """
        # Check if mTLS is required
        ssl_config = config.get("ssl", {})
        if not ssl_config:
            # Try to get SSL config from security section
            ssl_config = config.get("security", {}).get("ssl", {})
        
        # Prefer hypercorn for all SSL/TLS scenarios due to better mTLS support
        if ssl_config.get("enabled", False):
            engine = ServerEngineFactory.get_engine("hypercorn")
            if engine:
                logger.info("Selected hypercorn for SSL/TLS support (better mTLS capabilities)")
                return engine.get_name()
            else:
                logger.warning("SSL enabled but hypercorn not available")
        
        # For mTLS client verification, hypercorn is required
        if ssl_config.get("verify_client", False) or ssl_config.get("client_cert_required", False):
            engine = ServerEngineFactory.get_engine_with_feature("mtls_client_certs")
            if engine:
                logger.info(f"Selected {engine.get_name()} for mTLS support")
                return engine.get_name()
            else:
                logger.warning("mTLS required but no suitable engine available")
                return None
        
        # Default to hypercorn for better async support, fallback to uvicorn
        engine = ServerEngineFactory.get_engine("hypercorn")
        if engine:
            logger.info("Selected hypercorn as default engine (better async support)")
            return engine.get_name()
        
        engine = ServerEngineFactory.get_engine("uvicorn")
        if engine:
            logger.info("Selected uvicorn as fallback engine")
            return "uvicorn"
        
        return None
    
    @staticmethod
    def validate_engine_compatibility(
        config: Dict[str, Any], 
        engine_name: str
    ) -> bool:
        """
        Validate if a configuration is compatible with a specific engine.
        
        Args:
            config: Server configuration
            engine_name: Name of the server engine
            
        Returns:
            True if compatible, False otherwise
        """
        engine = ServerEngineFactory.get_engine(engine_name)
        if not engine:
            logger.error(f"Unknown engine: {engine_name}")
            return False
        
        # Check SSL requirements
        ssl_config = config.get("ssl", {})
        if not ssl_config:
            # Try to get SSL config from security section
            ssl_config = config.get("security", {}).get("ssl", {})
        
        if ssl_config.get("verify_client", False):
            if not engine.get_supported_features().get("mtls_client_certs", False):
                logger.error(f"Engine {engine_name} doesn't support mTLS client certificates")
                return False
        
        # Validate engine-specific configuration
        return engine.validate_config(config)
    
    @staticmethod
    def get_engine_capabilities(engine_name: str) -> Dict[str, Any]:
        """
        Get capabilities of a specific server engine.
        
        Args:
            engine_name: Name of the server engine
            
        Returns:
            Dictionary of engine capabilities
        """
        engine = ServerEngineFactory.get_engine(engine_name)
        if not engine:
            return {}
        
        return {
            "name": engine.get_name(),
            "features": engine.get_supported_features(),
            "config_schema": engine.get_config_schema()
        }


class UnifiedServerRunner:
    """
    Unified server runner that abstracts the choice of server engine.
    
    This class provides a unified interface for running servers regardless
    of the underlying engine, automatically selecting the best engine
    for the given configuration.
    """
    
    def __init__(self, default_engine: str = "uvicorn"):
        """
        Initialize the unified server runner.
        
        Args:
            default_engine: Default engine to use if no specific requirements
        """
        self.default_engine = default_engine
        self.available_engines = ServerEngineFactory.get_available_engines()
        
        logger.info(f"Available engines: {list(self.available_engines.keys())}")
        logger.info(f"Default engine: {default_engine}")
    
    def run_server(
        self, 
        app: Any, 
        config: Dict[str, Any], 
        engine_name: Optional[str] = None
    ) -> None:
        """
        Run server with the specified or optimal engine.
        
        Args:
            app: ASGI application
            config: Server configuration
            engine_name: Specific engine to use (optional)
        """
        # Determine which engine to use
        if engine_name:
            selected_engine = engine_name
            logger.info(f"Using specified engine: {selected_engine}")
        else:
            selected_engine = ServerConfigAdapter.get_optimal_engine_for_config(config)
            if not selected_engine:
                selected_engine = self.default_engine
                logger.info(f"Using default engine: {selected_engine}")
        
        # Validate compatibility
        if not ServerConfigAdapter.validate_engine_compatibility(config, selected_engine):
            raise ValueError(f"Configuration not compatible with engine: {selected_engine}")
        
        # Get engine instance
        engine = ServerEngineFactory.get_engine(selected_engine)
        if not engine:
            raise ValueError(f"Engine not available: {selected_engine}")
        
        # Convert configuration if needed
        converted_config = self._prepare_config_for_engine(config, selected_engine)
        
        # Run server
        logger.info(f"Starting server with {selected_engine} engine")
        engine.run_server(app, converted_config)
    
    def _prepare_config_for_engine(
        self, 
        config: Dict[str, Any], 
        engine_name: str
    ) -> Dict[str, Any]:
        logger.info(f"🔍 Debug: _prepare_config_for_engine called with config keys: {list(config.keys())}")
        logger.info(f"🔍 Debug: SSL config in input: {config.get('ssl', 'NOT_FOUND')}")
        """
        Prepare configuration for a specific engine.
        
        Args:
            config: Original configuration
            engine_name: Target engine name
            
        Returns:
            Engine-specific configuration
        """
        # Start with basic config
        engine_config = {
            "host": config.get("host", "127.0.0.1"),
            "port": config.get("port", 8000),
            "log_level": config.get("log_level", "info"),
            "reload": config.get("reload", False)
        }
        
        # Add SSL configuration if present
        # First check for direct SSL parameters (from app_factory.py)
        if "certfile" in config or "keyfile" in config or "ca_certs" in config or "verify_mode" in config:
            logger.info(f"🔍 DEBUG: Direct SSL parameters found in config")
            if "certfile" in config:
                engine_config["certfile"] = config["certfile"]
            if "keyfile" in config:
                engine_config["keyfile"] = config["keyfile"]
            if "ca_certs" in config:
                engine_config["ca_certs"] = config["ca_certs"]
            if "verify_mode" in config:
                engine_config["verify_mode"] = config["verify_mode"]
        else:
            # Try to get SSL config from ssl section
            ssl_config = config.get("ssl", {})
            if not ssl_config:
                # Try to get SSL config from security section
                ssl_config = config.get("security", {}).get("ssl", {})
            
            if ssl_config:
                converted_ssl = ServerConfigAdapter.convert_ssl_config_for_engine(
                    ssl_config, engine_name
                )
                engine_config.update(converted_ssl)
        
        # Add engine-specific configuration
        if "workers" in config:
            engine_config["workers"] = config["workers"]
        
        return engine_config
    
    def get_engine_info(self, engine_name: str) -> Dict[str, Any]:
        """
        Get information about a specific engine.
        
        Args:
            engine_name: Name of the engine
            
        Returns:
            Engine information dictionary
        """
        return ServerConfigAdapter.get_engine_capabilities(engine_name)
    
    def list_available_engines(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available engines with their capabilities.
        
        Returns:
            Dictionary mapping engine names to their capabilities
        """
        engines_info = {}
        for name, engine in self.available_engines.items():
            engines_info[name] = {
                "features": engine.get_supported_features(),
                "config_schema": engine.get_config_schema()
            }
        return engines_info
