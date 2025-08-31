"""
Module for dependency injection container implementation.

This module provides a container for registering and resolving dependencies
for command instances in the microservice.
"""

from typing import Any, Dict, Optional, Type, TypeVar, cast

T = TypeVar('T')


class DependencyContainer:
    """
    Container for managing dependencies.
    
    This class provides functionality to register, resolve, and manage
    dependencies that can be injected into command instances.
    """
    
    def __init__(self):
        """Initialize dependency container."""
        self._dependencies: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, name: str, instance: Any) -> None:
        """
        Register a dependency instance with a given name.
        
        Args:
            name: The name to register the dependency under
            instance: The dependency instance
        """
        self._dependencies[name] = instance
    
    def register_factory(self, name: str, factory: callable) -> None:
        """
        Register a factory function that will be called to create the dependency.
        
        Args:
            name: The name to register the factory under
            factory: A callable that creates the dependency
        """
        self._factories[name] = factory
    
    def register_singleton(self, name: str, factory: callable) -> None:
        """
        Register a singleton factory that will create the instance only once.
        
        Args:
            name: The name to register the singleton under
            factory: A callable that creates the singleton instance
        """
        self._factories[name] = factory
        # Mark as singleton but don't create until requested
        self._singletons[name] = None
    
    def get(self, name: str) -> Any:
        """
        Get a dependency by name.
        
        Args:
            name: The name of the dependency to get
            
        Returns:
            The dependency instance
            
        Raises:
            KeyError: If the dependency is not registered
        """
        # Check for direct instance
        if name in self._dependencies:
            return self._dependencies[name]
            
        # Check for singleton
        if name in self._singletons:
            # Create singleton if doesn't exist
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]
            
        # Check for factory
        if name in self._factories:
            return self._factories[name]()
            
        raise KeyError(f"Dependency '{name}' not registered")
        
    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._dependencies.clear()
        self._factories.clear()
        self._singletons.clear()
        
    def has(self, name: str) -> bool:
        """
        Check if a dependency is registered.
        
        Args:
            name: The name of the dependency
            
        Returns:
            True if the dependency is registered, False otherwise
        """
        return (name in self._dependencies or 
                name in self._factories)


# Global dependency container instance
container = DependencyContainer() 