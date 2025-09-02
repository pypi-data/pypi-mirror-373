"""
Middleware package for API.
This package contains middleware components for request processing.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.config import config
from .base import BaseMiddleware
from .factory import MiddlewareFactory
from .protocol_middleware import setup_protocol_middleware

def setup_middleware(app: FastAPI, app_config: Optional[Dict[str, Any]] = None) -> None:
    """
    Sets up middleware for application using the new middleware factory.

    Args:
        app: FastAPI application instance.
        app_config: Application configuration dictionary (optional)
    """
    # Use provided configuration or fallback to global config
    current_config = app_config if app_config is not None else config.get_all()
    
    # Create middleware factory
    factory = MiddlewareFactory(app, current_config)
    
    # Validate middleware configuration
    if not factory.validate_middleware_config():
        logger.error("Middleware configuration validation failed")
        raise SystemExit(1)
    
    logger.info("Using unified security middleware")
    middleware_list = factory.create_all_middleware()
    
    # Add middleware to application
    for middleware in middleware_list:
        # For ASGI middleware, we need to wrap the application
        if hasattr(middleware, 'dispatch'):
            # This is a proper ASGI middleware
            app.middleware("http")(middleware.dispatch)
        else:
            logger.warning(f"Middleware {middleware.__class__.__name__} doesn't have dispatch method")
    
    # Add protocol middleware with current configuration
    setup_protocol_middleware(app, current_config)
    
    # Log middleware information
    middleware_info = factory.get_middleware_info()
    logger.info(f"Middleware setup completed:")
    logger.info(f"  - Total middleware: {middleware_info['total_middleware']}")
    logger.info(f"  - Types: {', '.join(middleware_info['middleware_types'])}")
    logger.info(f"  - Security enabled: {middleware_info['security_enabled']}")
 