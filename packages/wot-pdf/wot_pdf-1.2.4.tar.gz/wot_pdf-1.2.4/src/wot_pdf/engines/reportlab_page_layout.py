#!/usr/bin/env python3
"""
📄 REPORTLAB PAGE LAYOUT - HEADERS, FOOTERS & TOC
===============================================
⚡ Professional page layout management for ReportLab PDFs
🔷 Header/footer generation, page numbering, and table of contents
📊 Template-specific layouts with consistent branding

Extracted from enhanced_reportlab_engine.py for better modularity.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import Paragraph, Spacer
    reportlab_available = True
except ImportError:
    reportlab_available = False


class ReportLabPageLayout:
    """
    Professional page layout management for ReportLab PDF generation.
    Handles headers, footers, page numbering, and table of contents.
    """

    def __init__(self, theme_manager=None):
        """
        Initialize page layout manager.
        
        Args:
            theme_manager: ReportLabThemeManager instance for styling
        """
        self.logger = logging.getLogger(__name__)
        self.theme_manager = theme_manager
        
    def create_professional_header_footer(self, canvas, doc, title: str, 
                                        author: str = "", 
                                        page_numbering: str = "standard") -> None:
        """
        Create professional header and footer for PDF pages.
        
        Args:
            canvas: ReportLab canvas object
            doc: Document template object
            title: Document title
            author: Document author
            page_numbering: Style of page numbering ('standard', 'chapter', 'none')
        """
        if not reportlab_available:
            return
            
        try:
            # Get page dimensions
            width, height = A4
            
            # Get theme colors if available
            if self.theme_manager:
                primary_color = self.theme_manager.get_theme_color('primary')
                accent_color = self.theme_manager.get_theme_color('accent')
                text_color = self.theme_manager.get_theme_color('text')
            else:
                primary_color = HexColor('#2B2B2B')
                accent_color = HexColor('#007ACC') 
                text_color = HexColor('#333333')

            # Header
            self._draw_header(canvas, width, height, title, primary_color, accent_color)
            
            # Footer
            self._draw_footer(canvas, doc, width, height, author, text_color, page_numbering)

        except Exception as e:
            self.logger.warning(f"Header/footer creation failed: {e}")

    def _draw_header(self, canvas, width: float, height: float, title: str, 
                    primary_color: Any, accent_color: Any) -> None:
        """Draw document header."""
        try:
            # Debug: Log title value
            self.logger.debug(f"Drawing header with title: '{title}' (type: {type(title)})")
            
            # Handle None title gracefully
            if title is None:
                title = "Untitled Document"
            
            # Header line
            canvas.setStrokeColor(accent_color)
            canvas.setLineWidth(2)
            canvas.line(0.75 * inch, height - 0.75 * inch, 
                       width - 0.75 * inch, height - 0.75 * inch)
            
            # Document title in header
            canvas.setFillColor(primary_color)
            canvas.setFont('Helvetica-Bold', 12)
            title_text = title[:60] + "..." if len(title) > 60 else title
            canvas.drawString(0.75 * inch, height - 0.6 * inch, title_text)
            
            # Generation timestamp (small, right-aligned)
            canvas.setFillColor(primary_color)
            canvas.setFont('Helvetica', 8)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            timestamp_width = canvas.stringWidth(timestamp, 'Helvetica', 8)
            canvas.drawString(width - 0.75 * inch - timestamp_width, 
                            height - 0.6 * inch, f"Generated: {timestamp}")

        except Exception as e:
            self.logger.warning(f"Header drawing failed: {e}")

    def _draw_footer(self, canvas, doc, width: float, height: float, 
                    author: str, text_color: Any, page_numbering: str) -> None:
        """Draw document footer."""
        try:
            # Footer line
            canvas.setStrokeColor(text_color)
            canvas.setLineWidth(1)
            canvas.line(0.75 * inch, 0.75 * inch, 
                       width - 0.75 * inch, 0.75 * inch)
            
            # Author name (left side)
            if author:
                canvas.setFillColor(text_color)
                canvas.setFont('Helvetica', 9)
                canvas.drawString(0.75 * inch, 0.5 * inch, f"Author: {author}")
            
            # Page numbering (right side)
            if page_numbering != "none":
                canvas.setFillColor(text_color)
                canvas.setFont('Helvetica', 9)
                
                if page_numbering == "standard":
                    page_text = f"Page {doc.page}"
                elif page_numbering == "chapter":
                    # Simple chapter-based numbering
                    chapter = ((doc.page - 1) // 10) + 1  # Assume 10 pages per chapter
                    page_in_chapter = ((doc.page - 1) % 10) + 1
                    page_text = f"Chapter {chapter} - Page {page_in_chapter}"
                else:
                    page_text = f"{doc.page}"
                
                page_width = canvas.stringWidth(page_text, 'Helvetica', 9)
                canvas.drawString(width - 0.75 * inch - page_width, 
                                0.5 * inch, page_text)

        except Exception as e:
            self.logger.warning(f"Footer drawing failed: {e}")

    def create_table_of_contents(self, headings: List[Dict[str, Any]]) -> List[Any]:
        """
        Create table of contents from headings list.
        
        Args:
            headings: List of heading dictionaries with numbering
            
        Returns:
            List of ReportLab flowables for TOC
        """
        if not headings or not reportlab_available:
            return []

        try:
            toc_elements = []
            
            # Get styles
            if self.theme_manager:
                styles = self.theme_manager.get_professional_styles()
                primary_color = self.theme_manager.get_theme_color('primary')
                secondary_color = self.theme_manager.get_theme_color('secondary')
            else:
                styles = {}
                primary_color = HexColor('#2B2B2B')
                secondary_color = HexColor('#4A4A4A')

            # TOC Title
            toc_title = Paragraph("Table of Contents", 
                                styles.get('Heading1', None))
            toc_elements.append(toc_title)
            toc_elements.append(Spacer(1, 20))

            # TOC Entries
            for heading in headings:
                level = heading['level']
                number = heading.get('number', '')
                text = heading['text']
                
                # Determine indentation based on level
                indent = (level - 1) * 20
                
                # Create TOC entry style based on level
                if level == 1:
                    font_size = 12
                    font_name = 'Helvetica-Bold'
                    color = primary_color
                    space_after = 8
                elif level == 2:
                    font_size = 11
                    font_name = 'Helvetica-Bold'
                    color = secondary_color
                    space_after = 6
                else:
                    font_size = 10
                    font_name = 'Helvetica'
                    color = secondary_color
                    space_after = 4

                # Format TOC entry
                if number:
                    toc_text = f"{number}. {text}"
                else:
                    toc_text = text

                toc_entry = Paragraph(
                    f'<font name="{font_name}" size="{font_size}" color="{color}">{toc_text}</font>',
                    styles.get('Normal', None)
                )
                
                # Add indentation for sub-levels
                if indent > 0:
                    toc_entry.leftIndent = indent
                    
                toc_elements.append(toc_entry)
                toc_elements.append(Spacer(1, space_after))

            # Add page break after TOC
            from reportlab.platypus import PageBreak
            toc_elements.append(PageBreak())
            
            return toc_elements

        except Exception as e:
            self.logger.error(f"TOC creation failed: {e}")
            return []

    def create_cover_page(self, title: str, author: str = "", 
                         description: str = "", template: str = "technical") -> List[Any]:
        """
        Create professional cover page.
        
        Args:
            title: Document title
            author: Document author
            description: Document description
            template: Template style ('technical', 'modern', 'academic')
            
        Returns:
            List of ReportLab flowables for cover page
        """
        if not reportlab_available:
            return []

        try:
            cover_elements = []
            
            # Get styles and colors
            if self.theme_manager:
                styles = self.theme_manager.get_professional_styles()
                primary_color = self.theme_manager.get_theme_color('primary')
                accent_color = self.theme_manager.get_theme_color('accent')
            else:
                styles = {}
                primary_color = HexColor('#2B2B2B')
                accent_color = HexColor('#007ACC')

            # Spacer to center content vertically
            cover_elements.append(Spacer(1, 2 * inch))

            # Main Title
            title_para = Paragraph(
                f'<font name="Helvetica-Bold" size="28" color="{primary_color}">{title}</font>',
                styles.get('Title', None)
            )
            cover_elements.append(title_para)
            cover_elements.append(Spacer(1, 0.5 * inch))

            # Description if provided
            if description:
                desc_para = Paragraph(
                    f'<font name="Helvetica" size="14" color="{primary_color}">{description}</font>',
                    styles.get('Normal', None)
                )
                desc_para.alignment = TA_CENTER
                cover_elements.append(desc_para)
                cover_elements.append(Spacer(1, 1 * inch))

            # Author
            if author:
                author_para = Paragraph(
                    f'<font name="Helvetica-Bold" size="16" color="{accent_color}">by {author}</font>',
                    styles.get('Normal', None)
                )
                author_para.alignment = TA_CENTER
                cover_elements.append(author_para)

            # Generation date
            generation_date = datetime.now().strftime("%B %Y")
            date_para = Paragraph(
                f'<font name="Helvetica" size="12" color="{primary_color}">{generation_date}</font>',
                styles.get('Normal', None)
            )
            date_para.alignment = TA_CENTER
            
            # Add spacer to push date toward bottom
            cover_elements.append(Spacer(1, 2 * inch))
            cover_elements.append(date_para)

            # Page break after cover
            from reportlab.platypus import PageBreak
            cover_elements.append(PageBreak())

            return cover_elements

        except Exception as e:
            self.logger.error(f"Cover page creation failed: {e}")
            return []

    def get_page_template_settings(self, template: str = "technical") -> Dict[str, Any]:
        """
        Get page template settings for different document types.
        
        Args:
            template: Template name ('technical', 'modern', 'academic')
            
        Returns:
            Dictionary with template settings
        """
        templates = {
            'technical': {
                'pagesize': A4,
                'leftMargin': 0.75 * inch,
                'rightMargin': 0.75 * inch,
                'topMargin': 1 * inch,
                'bottomMargin': 1 * inch,
                'showBoundary': False,
                'header_height': 0.5 * inch,
                'footer_height': 0.5 * inch
            },
            'modern': {
                'pagesize': A4,
                'leftMargin': 1 * inch,
                'rightMargin': 1 * inch,
                'topMargin': 1.2 * inch,
                'bottomMargin': 1.2 * inch,
                'showBoundary': False,
                'header_height': 0.6 * inch,
                'footer_height': 0.6 * inch
            },
            'academic': {
                'pagesize': A4,
                'leftMargin': 1.25 * inch,
                'rightMargin': 1 * inch,
                'topMargin': 1 * inch,
                'bottomMargin': 1.25 * inch,
                'showBoundary': False,
                'header_height': 0.4 * inch,
                'footer_height': 0.7 * inch
            }
        }
        
        return templates.get(template, templates['technical'])
