"""
Dependency Injection Container
Manages service dependencies and lifecycle
"""

from typing import Dict, Any, Callable, TypeVar, Type, Optional
from threading import Lock
import logging

T = TypeVar('T')

class DIContainer:
    """Professional dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._transients: Dict[str, Callable[[], Any]] = {}
        self._lock = Lock()
        self._logger = logging.getLogger(__name__)
        
    def register_singleton(self, name: str, factory: Callable[[], T]) -> None:
        """Register a singleton service"""
        with self._lock:
            self._factories[name] = factory
            if name in self._transients:
                del self._transients[name]
            self._logger.debug(f"Registered singleton: {name}")
    
    def register_transient(self, name: str, factory: Callable[[], T]) -> None:
        """Register a transient service (new instance each time)"""
        with self._lock:
            self._transients[name] = factory
            if name in self._factories:
                del self._factories[name]
            if name in self._singletons:
                del self._singletons[name]
            self._logger.debug(f"Registered transient: {name}")
    
    def register_instance(self, name: str, instance: T) -> None:
        """Register a service instance directly"""
        with self._lock:
            self._singletons[name] = instance
            self._logger.debug(f"Registered instance: {name}")
    
    def get(self, name: str) -> Any:
        """Get service instance"""
        with self._lock:
            # Check singleton first
            if name in self._singletons:
                return self._singletons[name]
            
            # Check transient
            if name in self._transients:
                return self._transients[name]()
            
            # Check factory (singleton)
            if name in self._factories:
                instance = self._factories[name]()
                self._singletons[name] = instance
                return instance
            
            raise ValueError(f"Service not registered: {name}")
    
    def has(self, name: str) -> bool:
        """Check if service exists"""
        return (name in self._factories or 
                name in self._singletons or 
                name in self._transients)
    
    def clear(self) -> None:
        """Clear all services"""
        with self._lock:
            self._factories.clear()
            self._singletons.clear()
            self._transients.clear()

# Global container
container = DIContainer()
