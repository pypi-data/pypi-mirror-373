#!/usr/bin/env python3
"""
🎨 REPORTLAB THEME MANAGER - PROFESSIONAL THEMES
================================================
⚡ Professional styling and color schemes for ReportLab engine
🔷 Theme management with Typst-quality visual design
📊 Custom font support and professional layouts

Extracted from enhanced_reportlab_engine.py for better modularity.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.colors import HexColor, black, blue, red, green, gray, white
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfbase import pdfutils
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    reportlab_available = True
except ImportError:
    # Define fallback objects when ReportLab is not available
    HexColor = lambda x: x  # Simple fallback
    black = '#000000'
    TA_LEFT = TA_CENTER = TA_RIGHT = TA_JUSTIFY = 0
    ParagraphStyle = object
    reportlab_available = False

# Export for compatibility
REPORTLAB_AVAILABLE = reportlab_available


class ReportLabThemeManager:
    """
    Professional theme management for ReportLab PDF generation
    Handles fonts, colors, and styling configurations.
    """
    
    # CUSTOM FONT SUPPORT
    CUSTOM_FONTS = {
        'source_code_pro': {
            'family': 'SourceCodePro',
            'files': {
                'regular': 'fonts/SourceCodePro-Regular.ttf',
                'bold': 'fonts/SourceCodePro-Bold.ttf',
                'italic': 'fonts/SourceCodePro-Italic.ttf'
            }
        },
        'fira_code': {
            'family': 'FiraCode',
            'files': {
                'regular': 'fonts/FiraCode-Regular.ttf',
                'bold': 'fonts/FiraCode-Bold.ttf'
            }
        }
    }

    # PROFESSIONAL COLOR THEMES
    PROFESSIONAL_THEMES = {
        'technical': {
            'primary': HexColor('#2B2B2B'),      # Dark gray
            'secondary': HexColor('#4A4A4A'),    # Medium gray
            'accent': HexColor('#007ACC'),       # VS Code blue
            'success': HexColor('#4CAF50'),      # Green
            'warning': HexColor('#FF9800'),      # Orange
            'error': HexColor('#F44336'),        # Red
            'background': HexColor('#F8F8F8'),   # Light gray
            'text': HexColor('#333333'),         # Dark text
            'code': HexColor('#1E1E1E'),         # Code background
            'border': HexColor('#E0E0E0')        # Light borders
        },
        'modern': {
            'primary': HexColor('#1A1A1A'),      # Almost black
            'secondary': HexColor('#3A3A3A'),    # Charcoal
            'accent': HexColor('#0066CC'),       # Modern blue
            'success': HexColor('#00C851'),      # Bright green
            'warning': HexColor('#FF6D00'),      # Deep orange
            'error': HexColor('#CC0000'),        # Deep red
            'background': HexColor('#FAFAFA'),   # Almost white
            'text': HexColor('#212121'),         # Near black
            'code': HexColor('#263238'),         # Material dark
            'border': HexColor('#E0E0E0')        # Standard border
        },
        'academic': {
            'primary': HexColor('#1B365D'),      # Academic blue
            'secondary': HexColor('#5D6D7E'),    # Gray blue
            'accent': HexColor('#B03A2E'),       # Academic red
            'success': HexColor('#239B56'),      # Forest green
            'warning': HexColor('#D68910'),      # Amber
            'error': HexColor('#CB4335'),        # Cardinal red
            'background': HexColor('#FBFCFC'),   # Off white
            'text': HexColor('#17202A'),         # Dark navy
            'code': HexColor('#F8F9F9'),         # Very light gray
            'border': HexColor('#D5DBDB')        # Light gray border
        }
    }

    def __init__(self, theme_name: str = "technical"):
        """Initialize theme manager with specified theme."""
        self.logger = logging.getLogger(__name__)
        self.theme_name = theme_name
        self.current_theme = self.PROFESSIONAL_THEMES.get(theme_name, self.PROFESSIONAL_THEMES['technical'])
        self.styles = None
        self.fonts_setup = False
        
    def setup_custom_fonts(self) -> bool:
        """
        Setup custom fonts for professional typography.
        Returns True if successful, False if fonts not available.
        """
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available - cannot setup custom fonts")
            return False
            
        if self.fonts_setup:
            return True
            
        try:
            # Try to register custom fonts
            for font_name, font_config in self.CUSTOM_FONTS.items():
                family = font_config['family']
                files = font_config['files']
                
                # Check if font files exist (simplified check)
                font_path = Path(__file__).parent.parent / files['regular']
                if font_path.exists():
                    try:
                        # Register regular font
                        pdfmetrics.registerFont(TTFont(family, str(font_path)))
                        
                        # Register bold variant if available
                        if 'bold' in files:
                            bold_path = Path(__file__).parent.parent / files['bold']
                            if bold_path.exists():
                                pdfmetrics.registerFont(TTFont(f"{family}-Bold", str(bold_path)))
                                
                        # Register italic variant if available  
                        if 'italic' in files:
                            italic_path = Path(__file__).parent.parent / files['italic']
                            if italic_path.exists():
                                pdfmetrics.registerFont(TTFont(f"{family}-Italic", str(italic_path)))
                                
                        self.logger.info(f"✅ Registered custom font: {family}")
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ Could not register font {family}: {e}")
                        
            self.fonts_setup = True
            return True
            
        except Exception as e:
            self.logger.warning(f"❌ Custom font setup failed: {e}")
            return False

    def get_professional_styles(self) -> Dict[str, ParagraphStyle]:
        """
        Create professional paragraph styles using current theme.
        Returns dictionary of styled paragraph styles.
        """
        if self.styles is not None:
            return self.styles
            
        if not REPORTLAB_AVAILABLE:
            return {}
            
        # Get base styles and customize
        base_styles = getSampleStyleSheet()
        theme = self.current_theme
        
        # Main content font - use reliable fonts to avoid mapping issues
        main_font = 'Times-Roman'  # Reliable standard font
        code_font = 'Courier'      # Reliable monospace font
        
        self.styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=24,
                textColor=theme['primary'],
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            
            'Heading1': ParagraphStyle(
                'CustomHeading1', 
                parent=base_styles['Heading1'],
                fontSize=20,
                textColor=theme['primary'],
                spaceAfter=20,
                spaceBefore=30,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderColor=theme['accent'],
                borderPadding=5
            ),
            
            'Heading2': ParagraphStyle(
                'CustomHeading2',
                parent=base_styles['Heading2'], 
                fontSize=16,
                textColor=theme['secondary'],
                spaceAfter=15,
                spaceBefore=20,
                fontName='Helvetica-Bold'
            ),
            
            'Heading3': ParagraphStyle(
                'CustomHeading3',
                parent=base_styles['Heading3'],
                fontSize=14,
                textColor=theme['secondary'],
                spaceAfter=12,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            ),
            
            'Normal': ParagraphStyle(
                'CustomNormal',
                parent=base_styles['Normal'],
                fontSize=11,
                textColor=theme['text'],
                spaceAfter=12,
                fontName=main_font,
                alignment=TA_JUSTIFY
            ),
            
            'Code': ParagraphStyle(
                'CustomCode',
                parent=base_styles['Code'],
                fontSize=9,
                textColor=theme['text'],
                fontName=code_font,
                backgroundColor=theme['background'],
                borderWidth=1,
                borderColor=theme['border'],
                borderPadding=8,
                spaceAfter=12,
                spaceBefore=6
            ),
            
            'Quote': ParagraphStyle(
                'CustomQuote',
                parent=base_styles['Normal'],
                fontSize=11,
                textColor=theme['secondary'],
                fontName=main_font,
                leftIndent=20,
                rightIndent=20,
                borderWidth=0,
                borderColor=theme['accent'],
                borderPadding=10,
                spaceAfter=12,
                spaceBefore=6
            ),
            
            'Caption': ParagraphStyle(
                'CustomCaption',
                parent=base_styles['Normal'],
                fontSize=9,
                textColor=theme['secondary'],
                fontName=main_font,
                alignment=TA_CENTER,
                spaceAfter=6
            )
        }
        
        return self.styles

    def get_theme_color(self, color_name: str) -> Any:
        """Get color from current theme by name."""
        return self.current_theme.get(color_name, black)
        
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.PROFESSIONAL_THEMES.keys())
        
    def switch_theme(self, theme_name: str) -> bool:
        """Switch to different theme. Returns True if successful."""
        if theme_name in self.PROFESSIONAL_THEMES:
            self.theme_name = theme_name
            self.current_theme = self.PROFESSIONAL_THEMES[theme_name]
            # Clear cached styles to force regeneration
            self.styles = None
            self.logger.info(f"✅ Switched to theme: {theme_name}")
            return True
        else:
            self.logger.warning(f"❌ Unknown theme: {theme_name}")
            return False
