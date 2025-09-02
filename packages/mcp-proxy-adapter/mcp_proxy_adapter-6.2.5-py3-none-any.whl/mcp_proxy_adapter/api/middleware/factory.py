"""
Middleware Factory for creating and managing middleware components.

This module provides a factory for creating middleware components with proper
configuration and dependency management.
"""

import logging
from typing import Dict, Any, List, Optional, Type

from fastapi import FastAPI

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.core.security_factory import SecurityFactory
from .base import BaseMiddleware
from .unified_security import UnifiedSecurityMiddleware
from .error_handling import ErrorHandlingMiddleware
from .logging import LoggingMiddleware
from .user_info_middleware import UserInfoMiddleware


class MiddlewareFactory:
    """
    Factory for creating and managing middleware components.
    
    Provides methods to create middleware components with proper configuration
    and dependency management.
    """
    
    def __init__(self, app: FastAPI, config: Dict[str, Any]):
        """
        Initialize middleware factory.
        
        Args:
            app: FastAPI application
            config: Application configuration
        """
        self.app = app
        self.config = config
        self.middleware_stack: List[BaseMiddleware] = []
        
        logger.info("Middleware factory initialized")
    
    def create_security_middleware(self) -> Optional[UnifiedSecurityMiddleware]:
        """
        Create unified security middleware.
        
        Returns:
            UnifiedSecurityMiddleware instance or None if creation failed
        """
        try:
            security_config = self.config.get("security", {})
            
            if not security_config.get("enabled", True):
                logger.info("Security middleware disabled by configuration")
                return None
            
            middleware = UnifiedSecurityMiddleware(self.app, self.config)
            self.middleware_stack.append(middleware)
            
            logger.info("Unified security middleware created successfully")
            return middleware
            
        except Exception as e:
            logger.error(f"Failed to create unified security middleware: {e}")
            return None
    
    def create_error_handling_middleware(self) -> Optional[ErrorHandlingMiddleware]:
        """
        Create error handling middleware.
        
        Returns:
            ErrorHandlingMiddleware instance or None if creation failed
        """
        try:
            # Import here to avoid circular imports
            from .error_handling import ErrorHandlingMiddleware
            
            middleware = ErrorHandlingMiddleware(self.app)
            self.middleware_stack.append(middleware)
            
            logger.info("Error handling middleware created successfully")
            return middleware
            
        except Exception as e:
            logger.error(f"Failed to create error handling middleware: {e}")
            return None
    
    def create_logging_middleware(self) -> Optional[LoggingMiddleware]:
        """
        Create logging middleware.
        
        Returns:
            LoggingMiddleware instance or None if creation failed
        """
        try:
            # Import here to avoid circular imports
            from .logging import LoggingMiddleware
            
            middleware = LoggingMiddleware(self.app, self.config)
            self.middleware_stack.append(middleware)
            
            logger.info("Logging middleware created successfully")
            return middleware
            
        except Exception as e:
            logger.error(f"Failed to create logging middleware: {e}")
            return None
    
    def create_user_info_middleware(self) -> Optional[UserInfoMiddleware]:
        """
        Create user info middleware.
        
        Returns:
            UserInfoMiddleware instance or None if creation failed
        """
        try:
            middleware = UserInfoMiddleware(self.app, self.config)
            self.middleware_stack.append(middleware)
            
            logger.info("User info middleware created successfully")
            return middleware
            
        except Exception as e:
            logger.error(f"Failed to create user info middleware: {e}")
            return None
    

    
    def create_all_middleware(self) -> List[BaseMiddleware]:
        """
        Create all required middleware components.
        
        Returns:
            List of created middleware instances
        """
        middleware_list = []
        
        # Create security middleware (unified)
        security_middleware = self.create_security_middleware()
        if security_middleware:
            middleware_list.append(security_middleware)
        
        # Create error handling middleware
        error_middleware = self.create_error_handling_middleware()
        if error_middleware:
            middleware_list.append(error_middleware)
        
        # Create logging middleware
        logging_middleware = self.create_logging_middleware()
        if logging_middleware:
            middleware_list.append(logging_middleware)
        
        # Create user info middleware
        user_info_middleware = self.create_user_info_middleware()
        if user_info_middleware:
            middleware_list.append(user_info_middleware)
        
        logger.info(f"Created {len(middleware_list)} middleware components")
        return middleware_list
    

    
    def get_middleware_by_type(self, middleware_type: Type[BaseMiddleware]) -> Optional[BaseMiddleware]:
        """
        Get middleware instance by type.
        
        Args:
            middleware_type: Type of middleware to find
            
        Returns:
            Middleware instance or None if not found
        """
        for middleware in self.middleware_stack:
            if isinstance(middleware, middleware_type):
                return middleware
        return None
    
    def get_security_middleware(self) -> Optional[UnifiedSecurityMiddleware]:
        """
        Get unified security middleware instance.
        
        Returns:
            UnifiedSecurityMiddleware instance or None if not found
        """
        return self.get_middleware_by_type(UnifiedSecurityMiddleware)
    
    def validate_middleware_config(self) -> bool:
        """
        Validate middleware configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            security_config = self.config.get("security", {})
            
            # Validate security configuration
            if not SecurityFactory.validate_config(self.config):
                logger.error("Security configuration validation failed")
                return False
            
            # Validate middleware-specific configurations
            if security_config.get("enabled", True):
                # Check required fields for security middleware
                auth_config = security_config.get("auth", {})
                if not isinstance(auth_config, dict):
                    logger.error("Auth configuration must be a dictionary")
                    return False
                
                ssl_config = security_config.get("ssl", {})
                if not isinstance(ssl_config, dict):
                    logger.error("SSL configuration must be a dictionary")
                    return False
            
            logger.info("Middleware configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Middleware configuration validation failed: {e}")
            return False
    
    def get_middleware_info(self) -> Dict[str, Any]:
        """
        Get information about created middleware.
        
        Returns:
            Dictionary with middleware information
        """
        info = {
            "total_middleware": len(self.middleware_stack),
            "middleware_types": [],
            "security_enabled": False
        }
        
        for middleware in self.middleware_stack:
            middleware_type = type(middleware).__name__
            info["middleware_types"].append(middleware_type)
            
            if isinstance(middleware, UnifiedSecurityMiddleware):
                info["security_enabled"] = True
        
        return info
