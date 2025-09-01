"""
Engine Selector Module
Selects optimal PDF engine based on content
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import logging


class EngineType(Enum):
    """PDF Engine types"""
    TYPST = "typst"
    REPORTLAB = "reportlab"
    WEASYPRINT = "weasyprint"
    AUTO = "auto"


class EngineSelector:
    """Selects optimal PDF engine based on content analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def select_engine(self, analysis: Dict[str, Any]) -> EngineType:
        """Select optimal engine based on content analysis"""
        
        # Default to AUTO for intelligent selection
        complexity = analysis.get('complexity', 'medium')
        has_math = analysis.get('has_mathematical_content', False)
        code_blocks = analysis.get('code_blocks', [])
        tables = analysis.get('tables', [])
        
        self.logger.debug(f"Engine selection criteria: complexity={complexity}, math={has_math}, "
                         f"code_blocks={len(code_blocks)}, tables={len(tables)}")
        
        # Typst is preferred for complex content
        if complexity in ['complex', 'very_complex'] or has_math:
            self.logger.info("🎯 Selected Typst engine for complex content")
            return EngineType.TYPST
        
        # Typst is also good for code-heavy content
        if len(code_blocks) > 3:
            self.logger.info("🎯 Selected Typst engine for code-heavy content")
            return EngineType.TYPST
        
        # ReportLab for simple, reliable documents
        if complexity == 'simple':
            self.logger.info("🎯 Selected ReportLab engine for simple content")
            return EngineType.REPORTLAB
        
        # Default: AUTO (try Typst, fallback to ReportLab)
        self.logger.info("🎯 Selected AUTO engine (Typst preferred, ReportLab fallback)")
        return EngineType.AUTO
    
    def get_engine_priority(self, analysis: Dict[str, Any]) -> List[EngineType]:
        """Get ordered list of engines to try"""
        primary_engine = self.select_engine(analysis)
        
        if primary_engine == EngineType.TYPST:
            return [EngineType.TYPST, EngineType.REPORTLAB]
        elif primary_engine == EngineType.REPORTLAB:
            return [EngineType.REPORTLAB, EngineType.TYPST]
        else:  # AUTO
            return [EngineType.TYPST, EngineType.REPORTLAB]
        
    def recommend_engine(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get engine recommendation with detailed reasoning"""
        primary_engine = self.select_engine(analysis)
        
        return {
            'engine': primary_engine,
            'confidence': 0.8,
            'reasoning': f"Selected {primary_engine.value} based on content analysis"
        }
