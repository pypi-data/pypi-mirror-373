"""
Service Registry
Central service management and initialization
"""

import logging
from typing import Dict, Any, Optional, List

from .container import container
from ..generators.generator_service import GeneratorService
from ..content.content_service import ContentService

class ServiceRegistry:
    """Central service registry and manager"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._initialized = False
        
    def initialize_all(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize all core services"""
        
        try:
            self._logger.info("Initializing WOT-PDF service registry...")
            
            # Register services
            container.register_singleton('generator_service', 
                                       lambda: GeneratorService(config))
            container.register_singleton('content_service', 
                                       lambda: ContentService(config))
            
            # Initialize services
            services = ['content_service', 'generator_service']
            
            for service_name in services:
                service = container.get(service_name)
                if hasattr(service, 'initialize'):
                    success = service.initialize()
                    if not success:
                        self._logger.error(f"Failed to initialize {service_name}")
                        return False
                    self._logger.info(f"Initialized {service_name}")
            
            self._initialized = True
            self._logger.info("All services initialized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Service initialization failed: {e}")
            return False
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get service by name"""
        if not self._initialized:
            return None
        
        try:
            return container.get(service_name)
        except ValueError:
            return None
    
    def shutdown_all(self) -> None:
        """Shutdown all services"""
        
        self._logger.info("Shutting down all services...")
        
        services = ['generator_service', 'content_service']
        
        for service_name in services:
            if container.has(service_name):
                try:
                    service = container.get(service_name)
                    if hasattr(service, 'shutdown'):
                        service.shutdown()
                        self._logger.info(f"Shutdown {service_name}")
                except Exception as e:
                    self._logger.error(f"Error shutting down {service_name}: {e}")
        
        container.clear()
        self._initialized = False
        self._logger.info("Service shutdown complete")
    
    def health_check(self) -> Dict[str, bool]:
        """Perform health check on all services"""
        
        health = {}
        
        if not self._initialized:
            return {"registry": False}
        
        services = ['generator_service', 'content_service']
        
        for service_name in services:
            try:
                service = container.get(service_name)
                if hasattr(service, 'is_ready'):
                    health[service_name] = service.is_ready()
                else:
                    health[service_name] = True  # Assume healthy if no method
            except:
                health[service_name] = False
        
        health["registry"] = all(health.values())
        
        return health

# Global registry
registry = ServiceRegistry()
