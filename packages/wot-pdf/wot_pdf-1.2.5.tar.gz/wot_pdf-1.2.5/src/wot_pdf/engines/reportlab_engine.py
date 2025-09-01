"""
🎯 ReportLab Engine - Reliable Fallback
======================================
100% reliable PDF generation using ReportLab
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import re

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.platypus import Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import black, blue, red, green, gray
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ReportLabEngine:
    """
    ReportLab PDF engine - 100% reliable fallback
    Converts markdown to professional PDF using ReportLab
    """
    
    def __init__(self):
        """Initialize ReportLab engine"""
        self.logger = logging.getLogger(__name__)
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required but not installed")
        
        # Setup fresh styles to avoid conflicts
        self.styles = getSampleStyleSheet()
        # Note: Template-specific styles are applied in generate()
    
    def _setup_custom_styles(self, template: str = "technical"):
        """Setup custom paragraph styles based on template"""
        
        # Clear existing custom styles to avoid conflicts
        custom_styles = ['CustomTitle', 'CustomSubtitle', 'WOTCode']
        for i in range(1, 7):
            custom_styles.append(f'CustomHeading{i}')
        
        for style_name in custom_styles:
            if style_name in self.styles:
                del self.styles.byName[style_name]
        
        # Template-specific colors and fonts
        if template == "corporate":
            title_color = colors.HexColor('#1f4e79')  # Corporate blue
            text_color = colors.HexColor('#2c2c2c')   # Dark gray
            code_bg = colors.HexColor('#f8f9fa')      # Light gray
        elif template == "academic":
            title_color = colors.black
            text_color = colors.black
            code_bg = colors.HexColor('#f5f5f5')
        elif template == "educational":
            title_color = colors.HexColor('#2e7d32')  # Green
            text_color = colors.HexColor('#333333')
            code_bg = colors.HexColor('#e8f5e8')      # Light green
        else:  # technical (default)
            title_color = colors.HexColor('#0066cc')  # Tech blue
            text_color = colors.black
            code_bg = colors.HexColor('#f5f5f5')
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=title_color
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=gray
        ))
        
        # Heading styles with template colors
        for i in range(1, 7):
            size = max(16 - i, 10)
            self.styles.add(ParagraphStyle(
                name=f'CustomHeading{i}',
                parent=self.styles['Heading1'],
                fontSize=size,
                spaceBefore=12,
                spaceAfter=8,
                textColor=title_color if i <= 2 else text_color
            ))
        
        # Code style with template-specific background
        self.styles.add(ParagraphStyle(
            name='WOTCode',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            backColor=code_bg,
            borderColor='#cccccc',
            borderWidth=1,
            borderPadding=5
        ))
    
    def generate(self, 
                 content: str,
                 output_file: Path,
                 template: str = "technical",
                 **kwargs) -> Dict[str, Any]:
        """
        Generate PDF using ReportLab
        
        Args:
            content: Markdown content
            output_file: Output PDF path
            template: Template name (influences styling)
            **kwargs: Template parameters
            
        Returns:
            Generation result
        """
        try:
            # Setup template-specific styles
            self._setup_custom_styles(template)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=A4,
                leftMargin=2*cm,
                rightMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Parse content and create story
            story = []
            
            # Add title page
            title = kwargs.get('title', 'Document')
            author = kwargs.get('author', 'Generated by WOT-PDF')
            date = kwargs.get('date', datetime.now().strftime("%B %d, %Y"))
            
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"By {author}", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(date, self.styles['CustomSubtitle']))
            story.append(Spacer(1, 30))
            
            # Parse markdown content
            elements = self._parse_markdown(content)
            story.extend(elements)
            
            # Build PDF
            doc.build(story)
            
            # Get file size
            file_size = output_file.stat().st_size if output_file.exists() else 0
            
            return {
                "success": True,
                "output_file": str(output_file),
                "template": template,
                "engine": "reportlab",
                "file_size_bytes": file_size,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"ReportLab generation error: {e}")
            raise
    
    def _parse_markdown(self, content: str) -> list:
        """
        Parse markdown content into ReportLab elements
        
        Returns:
            List of ReportLab flowables
        """
        elements = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Empty lines
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Headers
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('# ').strip()
                style_name = f'CustomHeading{min(level, 6)}'
                elements.append(Paragraph(header_text, self.styles[style_name]))
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Code blocks
            if line.startswith('```'):
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    # Escape HTML characters for ReportLab
                    code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    elements.append(Paragraph(f"<pre>{code_text}</pre>", self.styles['WOTCode']))
                    elements.append(Spacer(1, 12))
                i += 1
                continue
            
            # Lists
            if line.startswith('- ') or line.startswith('* '):
                list_items = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    item_text = lines[i].strip()[2:].strip()
                    # Basic markdown formatting
                    item_text = self._format_inline_markdown(item_text)
                    list_items.append(f"• {item_text}")
                    i += 1
                
                for item in list_items:
                    elements.append(Paragraph(item, self.styles['Normal']))
                elements.append(Spacer(1, 6))
                continue
            
            # Regular paragraphs
            paragraph_lines = [line]
            i += 1
            
            # Collect continuation lines
            while i < len(lines) and lines[i].strip() and not self._is_special_line(lines[i]):
                paragraph_lines.append(lines[i].strip())
                i += 1
            
            # Join and format paragraph
            paragraph_text = ' '.join(paragraph_lines)
            paragraph_text = self._format_inline_markdown(paragraph_text)
            
            elements.append(Paragraph(paragraph_text, self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _is_special_line(self, line: str) -> bool:
        """Check if line is a special markdown element"""
        stripped = line.strip()
        return (stripped.startswith('#') or 
                stripped.startswith('```') or
                stripped.startswith('- ') or
                stripped.startswith('* ') or
                stripped.startswith('1. '))
    
    def _format_inline_markdown(self, text: str) -> str:
        """
        Apply basic inline markdown formatting for ReportLab
        
        Args:
            text: Text with markdown formatting
            
        Returns:
            Text with ReportLab markup
        """
        # Bold: **text** -> <b>text</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # Italic: *text* -> <i>text</i> (simpler regex)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
        
        # Code: `text` -> <font name="Courier">text</font>
        text = re.sub(r'`([^`]+?)`', r'<font name="Courier">\1</font>', text)
        
        # Escape HTML characters
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Restore our markup
        text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
        text = text.replace('&lt;font name="Courier"&gt;', '<font name="Courier">').replace('&lt;/font&gt;', '</font>')
        
        return text
