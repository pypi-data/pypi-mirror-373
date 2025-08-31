"""
Base Service Abstract Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseService(ABC):
    """Abstract base class for services"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.is_initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the service"""
        pass
        
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the service"""
        pass
        
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.is_initialized
