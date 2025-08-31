"""
🎯 WOT-PDF Base Engine
=====================
Abstract base class for WOT-PDF engines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
import logging


class BaseEngine(ABC):
    """Abstract base class for PDF generation engines"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = logging.getLogger(self.__class__.__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
    
    @abstractmethod
    def generate_pdf(self, input_file: str, output_file: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Generate PDF from input file
        
        Args:
            input_file: Path to input file
            output_file: Path to output PDF file
            **kwargs: Additional generation options
            
        Returns:
            Dict containing:
            - success: bool
            - output_file: str (path to generated PDF)
            - message: str (status message)
            - stats: dict (optional statistics)
        """
        pass
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information and capabilities"""
        return {
            'name': self.__class__.__name__,
            'version': '1.0.0',
            'supported_inputs': [],
            'supported_outputs': ['.pdf'],
            'features': []
        }
    
    def validate_input(self, input_file: str) -> bool:
        """Validate input file"""
        input_path = Path(input_file)
        return input_path.exists() and input_path.is_file()
    
    def prepare_output_dir(self, output_file: str) -> bool:
        """Ensure output directory exists"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create output directory: {e}")
            return False
