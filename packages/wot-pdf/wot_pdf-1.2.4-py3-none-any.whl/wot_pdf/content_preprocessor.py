"""
Content Preprocessor Module
Preprocesses content for PDF generation
"""

from typing import Dict, Any, Optional
import logging
import re


class ContentPreprocessor:
    """Preprocesses content for optimal PDF generation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def preprocess(self, content: str, engine_type: Optional[str] = None) -> str:
        """Preprocess content for specified engine"""
        
        self.logger.debug(f"Preprocessing content for engine: {engine_type}")
        
        # Basic preprocessing
        processed = content
        
        # Fix common Markdown issues
        processed = self._fix_line_endings(processed)
        processed = self._normalize_headers(processed)
        processed = self._fix_code_blocks(processed)
        
        # Engine-specific preprocessing
        if engine_type == "typst":
            processed = self._preprocess_for_typst(processed)
        elif engine_type == "reportlab":
            processed = self._preprocess_for_reportlab(processed)
        
        return processed
    
    def _fix_line_endings(self, content: str) -> str:
        """Normalize line endings"""
        return content.replace('\r\n', '\n').replace('\r', '\n')
    
    def _normalize_headers(self, content: str) -> str:
        """Normalize header formatting"""
        # Ensure headers have proper spacing
        content = re.sub(r'^(#+)\s*(.+?)$', r'\1 \2', content, flags=re.MULTILINE)
        return content
    
    def _fix_code_blocks(self, content: str) -> str:
        """Fix code block formatting"""
        # Ensure code blocks have proper language tags
        content = re.sub(r'^```\s*$', '```text', content, flags=re.MULTILINE)
        return content
    
    def _preprocess_for_typst(self, content: str) -> str:
        """Preprocess content specifically for Typst"""
        # No special preprocessing needed for Typst
        # The enhanced adapter handles Markdown->Typst conversion
        return content
    
    def _preprocess_for_reportlab(self, content: str) -> str:
        """Preprocess content specifically for ReportLab"""
        # ReportLab handles standard Markdown well
        return content
    
    def preprocess_content(self, content: str, engine_type: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess content with detailed results"""
        processed_content = self.preprocess(content, engine_type)
        
        return {
            'content': processed_content,
            'engine_optimizations': [],
            'preprocessing_count': 1
        }
