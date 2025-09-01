"""
Base Engine Abstract Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path

class BaseEngine(ABC):
    """Abstract base class for all PDF engines"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        
    @abstractmethod
    def generate_pdf(self, content: str, output_path: Path, **kwargs) -> bool:
        """Generate PDF from markdown content"""
        pass
        
    @abstractmethod
    def validate_content(self, content: str) -> List[str]:
        """Validate content"""
        pass
