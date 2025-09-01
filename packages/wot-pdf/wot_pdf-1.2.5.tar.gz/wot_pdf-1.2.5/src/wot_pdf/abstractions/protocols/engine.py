"""
Engine Protocol Interface
"""

from typing import Protocol, Dict, Any, List
from pathlib import Path

class EngineProtocol(Protocol):
    """Protocol for PDF engines"""
    
    def generate_pdf(self, content: str, output_path: Path, **kwargs) -> bool:
        """Generate PDF"""
        ...
        
    def validate_content(self, content: str) -> List[str]:
        """Validate content"""
        ...
