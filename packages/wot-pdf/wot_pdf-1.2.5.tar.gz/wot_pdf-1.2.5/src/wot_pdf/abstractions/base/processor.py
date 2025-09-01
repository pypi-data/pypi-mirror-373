"""
Base Processor Abstract Class
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseProcessor(ABC):
    """Abstract base class for content processors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        
    @abstractmethod
    def process(self, content: str, **kwargs) -> str:
        """Process content"""
        pass
        
    @abstractmethod
    def validate(self, content: str) -> bool:
        """Validate content"""
        pass
