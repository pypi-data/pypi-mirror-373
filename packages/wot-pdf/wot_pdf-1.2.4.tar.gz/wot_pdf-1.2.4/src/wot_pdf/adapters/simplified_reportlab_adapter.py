"""
Simplified ReportLab Engine Adapter
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class SimplifiedReportLabAdapter:
    """Simplified ReportLab engine adapter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self._name = "reportlab_simplified"
        
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize ReportLab adapter"""
        try:
            if REPORTLAB_AVAILABLE:
                self._is_initialized = True
                self.logger.info("✅ ReportLab available")
                return True
            else:
                self.logger.error("❌ ReportLab not available")
                return False
        except Exception as e:
            self.logger.error(f"❌ ReportLab initialization failed: {e}")
            return False
            
    @property
    def is_available(self) -> bool:
        """Check if ReportLab is available"""
        return REPORTLAB_AVAILABLE and self._is_initialized
        
    def generate_pdf(self, content: str, output_path: Path, template: str = "technical", **kwargs) -> Dict[str, Any]:
        """Generate PDF with ReportLab"""
        if not self._is_initialized:
            raise RuntimeError("ReportLab adapter not initialized")
            
        try:
            # Create PDF document
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Simple markdown to PDF conversion
            lines = content.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    if line.startswith('#'):
                        # Header
                        level = len(line) - len(line.lstrip('#'))
                        text = line.lstrip('# ')
                        if level == 1:
                            story.append(Paragraph(text, styles['Title']))
                        else:
                            story.append(Paragraph(text, styles['Heading1']))
                        story.append(Spacer(1, 12))
                    else:
                        # Regular paragraph
                        story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 6))
                        
            # Build PDF
            doc.build(story)
            
            return {
                'success': True,
                'engine': self._name,
                'output_file': str(output_path),
                'template': template,
                'file_size': output_path.stat().st_size if output_path.exists() else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ ReportLab generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'engine': self._name
            }
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities"""
        return {
            'formats': ['pdf'],
            'quality': 'medium',
            'speed': 'medium',
            'features': ['basic_formatting', 'reliable']
        }
