#!/usr/bin/env python3
"""
🎯 ENHANCED REPORTLAB ENGINE V2.0 - MODULAR ARCHITECTURE  
========================================================
⚡ Advanced ReportLab engine with modular design and professional themes
🔷 Uses specialized modules for theme, text, content, and layout management
📊 Clean architecture with proper separation of concerns

MODULAR COMPONENTS:
- ReportLabThemeManager: Professional themes and styling
- ReportLabTextProcessor: Text cleaning and formatting
- ReportLabContentProcessor: Markdown parsing and tables
- ReportLabPageLayout: Headers, footers, and page structure
"""

import logging
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime

# Global ReportLab availability flag
REPORTLAB_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass

# Import our modular components
from .reportlab_theme_manager import ReportLabThemeManager
from .reportlab_text_processor import ReportLabTextProcessor
from .reportlab_content_processor import ReportLabContentProcessor
from .reportlab_page_layout import ReportLabPageLayout
from .reportlab_advanced_features import create_advanced_reportlab_system
from .reportlab_cross_references import create_cross_reference_system


class EnhancedReportLabEngine:
    """
    Enhanced ReportLab PDF engine with modular architecture.
    Coordinates specialized components for professional PDF generation.
    """
    
    # Template configurations mapping to themes and features
    TEMPLATE_CONFIGS = {
        'technical': {
            'theme': 'technical',
            'features': ['code_highlighting', 'api_docs', 'diagrams'],
            'font_size': 11,
            'line_spacing': 1.2,
            'page_numbering': 'standard'
        },
        'academic': {
            'theme': 'academic', 
            'features': ['citations', 'bibliography', 'equations'],
            'font_size': 12,
            'line_spacing': 1.4,
            'page_numbering': 'chapter'
        },
        'corporate': {
            'theme': 'modern',
            'features': ['executive_summary', 'charts', 'branding'], 
            'font_size': 11,
            'line_spacing': 1.3,
            'page_numbering': 'standard'
        },
        'minimal': {
            'theme': 'technical',
            'features': ['clean_typography', 'basic_formatting'],
            'font_size': 11,
            'line_spacing': 1.2,
            'page_numbering': 'standard'
        }
    }

    def __init__(self, template: str = "technical"):
        """
        Initialize enhanced ReportLab engine with modular components.
        
        Args:
            template: Template name ('technical', 'academic', 'corporate', 'minimal')
        """
        self.logger = logging.getLogger(__name__)
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required but not installed")
        
        # Get template configuration
        self.template_name = template
        self.template_config = self.TEMPLATE_CONFIGS.get(template, self.TEMPLATE_CONFIGS['technical'])
        
        # Initialize modular components
        theme_name = self.template_config['theme']
        self.theme_manager = ReportLabThemeManager(theme_name)
        self.text_processor = ReportLabTextProcessor()
        self.content_processor = ReportLabContentProcessor(self.text_processor, self.theme_manager)
        self.page_layout = ReportLabPageLayout(self.theme_manager)
        
        # Initialize advanced features system
        self.advanced_features = create_advanced_reportlab_system()
        
        # Initialize cross-reference system
        self.cross_ref_system = create_cross_reference_system()
        
        # Setup components
        self.theme_manager.setup_custom_fonts()
        
        self.logger.info(f"✅ Enhanced ReportLab Engine initialized with template: {template}")
        self.logger.info("🚀 Advanced features enabled: optimizer, security, batch processing, monitoring")
        self.logger.info("🔗 Cross-reference system enabled: figures, tables, sections")

    def generate(self,
                content: str,
                output_path: str,
                title: str = "Document",
                author: str = "",
                template: Optional[str] = None,
                add_toc: bool = True,
                add_cover: bool = True,
                chapter_numbering: bool = False,
                enable_advanced_features: bool = True) -> Dict[str, Any]:
        """
        Generate PDF with professional formatting using modular components.
        
        Args:
            content: Markdown content to convert
            output_path: Path where PDF should be saved
            title: Document title
            author: Document author
            template: Override template (optional)
            add_toc: Whether to add table of contents
            add_cover: Whether to add cover page
            chapter_numbering: Whether to add chapter numbering to headings
            enable_advanced_features: Enable advanced processing and optimization
            
        Returns:
            Dictionary with generation results and statistics
        """
        try:
            start_time = datetime.now()
            
            # ADVANCED FEATURE 1: Security Validation
            if enable_advanced_features:
                security_result = self.advanced_features['security_validator'].validate_content(content)
                if not security_result.is_safe:
                    return {
                        'success': False,
                        'error': f'Content security validation failed. Risk score: {security_result.risk_score}',
                        'security_warnings': security_result.warnings,
                        'blocked_elements': security_result.blocked_elements
                    }
                elif security_result.warnings:
                    self.logger.warning(f"🛡️ Content security warnings: {len(security_result.warnings)} issues found")
            
            # ADVANCED FEATURE 2: Content Optimization + Cross-Reference Processing
            optimization_time = 0.0
            if enable_advanced_features:
                opt_start = time.time()
                
                # Step 1: Process cross-references and figure captions
                self.logger.info("🔗 Processing cross-references and figure captions...")
                self.logger.info(f"📊 Content length before cross-ref processing: {len(content)}")
                
                cross_ref_manager = self.cross_ref_system['cross_ref_manager']
                figure_processor = self.cross_ref_system['figure_processor']
                
                # Process cross-references first
                content = cross_ref_manager.scan_content_for_references(content)
                self.logger.info(f"📊 Content length after cross-ref processing: {len(content)}")
                
                # Then process figure captions
                content = figure_processor.process_figure_captions(content)
                self.logger.info(f"📊 Content length after figure processing: {len(content)}")
                
                # Get cross-reference statistics
                ref_stats = cross_ref_manager.get_reference_statistics()
                self.logger.info(f"📊 Cross-references processed: {ref_stats['total_references']} total")
                if ref_stats['by_type']['figures'] > 0:
                    self.logger.info(f"   - Figures: {ref_stats['by_type']['figures']}")
                if ref_stats['by_type']['tables'] > 0:
                    self.logger.info(f"   - Tables: {ref_stats['by_type']['tables']}")
                if ref_stats['by_type']['sections'] > 0:
                    self.logger.info(f"   - Sections: {ref_stats['by_type']['sections']}")
                
                # Step 2: Content optimization
                self.logger.info(f"📊 Content length before optimization: {len(content)}")
                optimization_result = self.advanced_features['optimizer'].optimize_content(content)
                optimization_time = time.time() - opt_start
                
                if optimization_result.success:
                    content = optimization_result.optimized_content
                    self.logger.info(f"📊 Content length after optimization: {len(content)}")
                    total_improvements = len(optimization_result.optimizations_applied)
                    self.logger.info(f"✅ Content optimized with {total_improvements} improvements + cross-references")
                else:
                    self.logger.warning("⚠️ Content optimization failed, using original content")
            else:
                # Even without advanced features, process cross-references (they're essential)
                self.logger.info("🔗 Processing cross-references (essential functionality)...")
                cross_ref_manager = self.cross_ref_system['cross_ref_manager']
                figure_processor = self.cross_ref_system['figure_processor']
                
                content = cross_ref_manager.scan_content_for_references(content)
                content = figure_processor.process_figure_captions(content)
            
            # Use override template if provided
            if template and template != self.template_name:
                self._reconfigure_template(template)
            
            # Get page template settings
            page_settings = self.page_layout.get_page_template_settings(self.template_name)
            
            # Create document with professional settings
            doc = SimpleDocTemplate(
                output_path,
                pagesize=page_settings['pagesize'],
                leftMargin=page_settings['leftMargin'],
                rightMargin=page_settings['rightMargin'],
                topMargin=page_settings['topMargin'],
                bottomMargin=page_settings['bottomMargin']
            )
            
            # Prepare content elements
            story = []
            
            # Add cover page if requested
            if add_cover:
                cover_elements = self.page_layout.create_cover_page(
                    title, author, template=self.template_name
                )
                story.extend(cover_elements)
            
            # Process content and extract headings for TOC using processed content
            # Use the cross-reference processed content
            headings = self.content_processor.collect_headings(content)
            
            # Add chapter numbering if requested
            if chapter_numbering and headings:
                headings = self.content_processor.add_heading_numbers(headings)
                # Apply numbering to processed content (after cross-reference processing)
                numbered_content = self.content_processor.apply_heading_numbers(content, headings)
            else:
                numbered_content = content  # Use processed content with cross-references
            
            # Add table of contents if requested
            if add_toc and headings:
                toc_elements = self.page_layout.create_table_of_contents(headings)
                story.extend(toc_elements)
            
            # Process main content with our NEW line-by-line processor (NO preprocessing!)
            self.logger.info(f"🔄 Processing markdown content ({len(numbered_content)} chars)")
            content_elements = self._process_markdown_content(numbered_content)
            self.logger.info(f"📊 Generated {len(content_elements)} content elements")
            story.extend(content_elements)
            
            # Build PDF with header/footer callback
            def header_footer_callback(canvas, doc):
                self.logger.debug(f"Header callback called with title: '{title}'")
                self.page_layout.create_professional_header_footer(
                    canvas, doc, title, author, 
                    self.template_config.get('page_numbering', 'standard')
                )
            
            self.logger.debug(f"Starting PDF build with {len(story)} story elements")
            try:
                doc.build(story, onFirstPage=header_footer_callback, 
                         onLaterPages=header_footer_callback)
                self.logger.debug(f"PDF build completed successfully")
            except Exception as build_error:
                self.logger.error(f"PDF build failed: {build_error}")
                raise
            
            # Calculate generation stats
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # Get actual file size
            try:
                file_size = Path(output_path).stat().st_size
            except Exception:
                file_size = 0  # Fallback if file size can't be determined
            
            # ADVANCED FEATURE 3: Performance Monitoring
            if enable_advanced_features:
                self.advanced_features['performance_monitor'].record_generation(
                    generation_time, len(content), optimization_time
                )
            
            result = {
                'success': True,
                'output_path': output_path,
                'template': self.template_name,
                'generation_time': generation_time,
                'optimization_time': optimization_time,
                'file_size_bytes': file_size,  # Add missing file size
                'pages_estimated': len(story) // 10,  # Rough estimate
                'headings_processed': len(headings),
                'features_used': self.template_config['features'],
                'theme': self.template_config['theme'],
                'advanced_features_enabled': enable_advanced_features
            }
            
            # Add advanced features stats if enabled
            if enable_advanced_features:
                result['optimization_stats'] = self.advanced_features['optimizer'].get_optimization_stats()
                result['performance_report'] = self.advanced_features['performance_monitor'].get_performance_report()
            
            self.logger.info(f"✅ PDF generated successfully: {output_path}")
            self.logger.info(f"⏱️ Generation time: {generation_time:.2f}s")
            if enable_advanced_features:
                self.logger.info(f"🚀 Optimization time: {optimization_time:.3f}s")
            
            return result
            
        except Exception as e:
            # Record error in performance monitor
            if enable_advanced_features:
                self.advanced_features['performance_monitor'].record_error(type(e).__name__, str(e))
            
            self.logger.error(f"❌ PDF generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'template': self.template_name
            }

    def _reconfigure_template(self, new_template: str) -> None:
        """Reconfigure engine for different template."""
        if new_template in self.TEMPLATE_CONFIGS:
            self.template_name = new_template
            self.template_config = self.TEMPLATE_CONFIGS[new_template]
            
            # Update theme if it changed
            new_theme = self.template_config['theme']
            if new_theme != self.theme_manager.theme_name:
                self.theme_manager.switch_theme(new_theme)
                
            self.logger.info(f"🔄 Reconfigured to template: {new_template}")

    def _process_markdown_content(self, content: str) -> List[Any]:
        """
        Process Markdown content into ReportLab flowables with proper line-by-line parsing.
        COMPLETELY REWRITTEN for proper markdown processing.
        
        Args:
            content: Raw Markdown content
            
        Returns:
            List of ReportLab flowable elements
        """
        if not content.strip():
            return []

        import re
        from reportlab.platypus import Paragraph, Spacer

        try:
            story = []
            lines = content.split('\n')
            i = 0
            
            # Get professional styles
            styles = self.theme_manager.get_professional_styles()
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines but add spacing
                if not line:
                    story.append(Spacer(1, 6))
                    i += 1
                    continue
                
                # Process headings (# ## ###)
                heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
                if heading_match:
                    level = len(heading_match.group(1))
                    text = heading_match.group(2).strip()
                    
                    # Apply simple text cleaning (no HTML escaping for headings)
                    clean_text = self._simple_text_clean(text)
                    
                    # Select appropriate style
                    if level == 1:
                        style = styles.get('Heading1', styles.get('Normal'))
                    elif level == 2:
                        style = styles.get('Heading2', styles.get('Normal'))
                    elif level == 3:
                        style = styles.get('Heading3', styles.get('Normal'))
                    else:
                        style = styles.get('Heading3', styles.get('Normal'))
                    
                    story.append(Paragraph(clean_text, style))
                    story.append(Spacer(1, 12))
                    i += 1
                    continue
                
                # Process code blocks (```)
                if line.startswith('```'):
                    code_elements, new_i = self._process_simple_code_block(lines, i, styles)
                    story.extend(code_elements)
                    i = new_i
                    continue
                
                # Process lists (- or *)
                if line.startswith('- ') or line.startswith('* '):
                    list_elements, new_i = self._process_simple_list(lines, i, styles)
                    story.extend(list_elements)
                    i = new_i
                    continue
                
                # Process numbered lists (1. 2. 3.)
                if re.match(r'^\d+\.\s', line):
                    list_elements, new_i = self._process_numbered_list(lines, i, styles)
                    story.extend(list_elements)
                    i = new_i
                    continue
                
                # Process tables (|) - but first check for table captions
                if '|' in line and line.count('|') >= 2:
                    # Look ahead for table caption marker
                    table_caption = None
                    caption_index = -1
                    
                    # Look for table caption after the table
                    for look_ahead in range(i, min(i + 10, len(lines))):
                        if '{TABLE_CAPTION:' in lines[look_ahead]:
                            # Extract caption info
                            import re
                            caption_match = re.search(r'{TABLE_CAPTION:([^:]+):([^}]+)}', lines[look_ahead])
                            if caption_match:
                                table_caption = caption_match.group(2)  # "Table 1"
                                caption_index = look_ahead
                                break
                    
                    table_element, new_i = self._process_simple_table(lines, i, styles)
                    if table_element:
                        # Add table with caption if found
                        if table_caption:
                            caption_para = Paragraph(f"<b>{table_caption}</b>", styles.get('Normal'))
                            story.append(caption_para)
                            story.append(Spacer(1, 6))
                            
                            # Remove the caption marker line
                            if caption_index >= 0 and caption_index < len(lines):
                                lines[caption_index] = ""  # Clear the marker line
                        
                        story.append(table_element)
                        story.append(Spacer(1, 12))
                    
                    i = new_i
                    continue
                
                # Skip empty lines and table caption markers
                if not line.strip() or '{TABLE_CAPTION:' in line:
                    i += 1
                    continue
                
                # Process horizontal rules (---)
                if line.startswith('---') or line.startswith('***'):
                    from reportlab.platypus import HRFlowable
                    story.append(Spacer(1, 12))
                    story.append(HRFlowable(width="100%", thickness=1, color='black'))
                    story.append(Spacer(1, 12))
                    i += 1
                    continue
                
                # Process regular paragraphs with simple inline formatting
                para_text = self._apply_simple_inline_formatting(line)
                paragraph = Paragraph(para_text, styles.get('Normal'))
                story.append(paragraph)
                story.append(Spacer(1, 8))
                i += 1
                
            return story
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {e}")
            # Return fallback paragraph with error info
            styles = self.theme_manager.get_professional_styles() if self.theme_manager else {}
            fallback_style = styles.get('Normal')
            if fallback_style:
                return [Paragraph("Content processing error occurred. Please check the markdown syntax.", fallback_style)]
            else:
                return []

    def _simple_text_clean(self, text: str) -> str:
        """Simple text cleaning without HTML escaping for basic content."""
        if not text:
            return ""
        # Only escape the most dangerous characters, preserve basic formatting
        text = text.replace('&', '&amp;')  # Must be first
        return text.strip()

    def _apply_simple_inline_formatting(self, text: str) -> str:
        """Apply basic inline formatting without complex font specifications."""
        if not text:
            return ""
            
        try:
            # Simple bold formatting
            text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
            
            # Simple italic formatting  
            text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
            
            # Simple code formatting - no font specification to avoid mapping issues
            text = re.sub(r'`([^`]+)`', r'<font color="#B03A2E">\1</font>', text)
            
            # Clean up any ampersands (but preserve HTML entities)
            text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', text)
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Simple inline formatting failed: {e}")
            return self._simple_text_clean(text)

    def _process_simple_code_block(self, lines: List[str], start_index: int, 
                                  styles: Dict[str, Any]) -> Tuple[List[Any], int]:
        """Process code blocks with simple formatting."""
        elements = []
        i = start_index + 1  # Skip opening ```
        code_lines = []
        
        # Collect code lines
        while i < len(lines) and not lines[i].strip().startswith('```'):
            code_lines.append(lines[i])
            i += 1
        
        if i < len(lines):
            i += 1  # Skip closing ```
        
        if code_lines:
            elements.append(Spacer(1, 6))
            code_text = '\n'.join(code_lines)
            # Simple code formatting without font family specifications
            code_text = self._simple_text_clean(code_text)
            code_para = Paragraph(f'<font color="#B03A2E">{code_text}</font>', 
                                styles.get('Code', styles.get('Normal')))
            elements.append(code_para)
            elements.append(Spacer(1, 6))
        
        return elements, i

    def _process_simple_list(self, lines: List[str], start_index: int, 
                           styles: Dict[str, Any]) -> Tuple[List[Any], int]:
        """Process bulleted lists."""
        elements = []
        i = start_index
        
        while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
            item_text = lines[i].strip()[2:].strip()  # Remove '- ' or '* '
            item_text = self._apply_simple_inline_formatting(item_text)
            
            # Use bullet character instead of complex formatting
            bullet_text = f'• {item_text}'
            elements.append(Paragraph(bullet_text, styles.get('Normal')))
            i += 1
        
        if elements:
            elements.append(Spacer(1, 8))
        
        return elements, i

    def _process_numbered_list(self, lines: List[str], start_index: int, 
                             styles: Dict[str, Any]) -> Tuple[List[Any], int]:
        """Process numbered lists."""
        elements = []
        i = start_index
        
        while i < len(lines):
            line = lines[i].strip()
            match = re.match(r'^(\d+)\.\s+(.+)', line)
            if not match:
                break
            
            number = match.group(1)
            item_text = match.group(2)
            item_text = self._apply_simple_inline_formatting(item_text)
            
            numbered_text = f'{number}. {item_text}'
            elements.append(Paragraph(numbered_text, styles.get('Normal')))
            i += 1
        
        if elements:
            elements.append(Spacer(1, 8))
        
        return elements, i

    def _process_simple_table(self, lines: List[str], start_index: int, 
                            styles: Dict[str, Any]) -> Tuple[Optional[Any], int]:
        """Process markdown tables with simple formatting."""
        table_data = []
        i = start_index
        
        # Process table rows
        while i < len(lines) and '|' in lines[i]:
            line = lines[i].strip()
            
            # Skip separator rows (---- or |---|---|)
            if re.match(r'^[\s\-:|]+$', line):
                self.logger.debug(f"🚫 Skipping separator line: {line}")
                i += 1
                continue
                
            self.logger.debug(f"📊 Processing table row: {line}")
            
            # Split by | and clean cells
            cells = [cell.strip() for cell in line.split('|')]
            # Remove empty first/last cells if they exist
            if cells and cells[0] == '':
                cells = cells[1:]
            if cells and cells[-1] == '':
                cells = cells[:-1]
            
            if cells:
                # Apply simple formatting to each cell
                formatted_cells = [self._apply_simple_inline_formatting(cell) for cell in cells]
                table_data.append(formatted_cells)
                self.logger.debug(f"✅ Added table row: {formatted_cells}")
            
            i += 1
        
        if len(table_data) >= 1:  # At least one row
            try:
                from reportlab.platypus import Table, TableStyle
                from reportlab.lib.colors import HexColor
                
                table = Table(table_data)
                # Simple table style without complex formatting
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),  # Header row
                    ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#333333')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                return table, i
                
            except Exception as e:
                self.logger.warning(f"Simple table creation failed: {e}")
                return None, i
        
        return None, i

    def _create_heading_paragraph(self, line: str, styles: Dict[str, Any]) -> Optional[Any]:
        """Create paragraph for heading line."""
        try:
            # Extract heading level and text
            match = re.match(r'^(#{1,6})\s+(.+)', line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                
                # Clean text
                clean_text = self.text_processor.gentle_clean_text(text)
                
                # Select appropriate style
                if level == 1:
                    style = styles.get('Heading1')
                elif level == 2:
                    style = styles.get('Heading2')  
                elif level == 3:
                    style = styles.get('Heading3')
                else:
                    style = styles.get('Heading3')  # Use Heading3 for deeper levels
                
                if style:
                    return Paragraph(clean_text, style)
                    
            return None
            
        except Exception as e:
            self.logger.warning(f"Heading creation failed: {e}")
            return None

    def _process_code_block(self, lines: List[str], start_index: int, 
                          styles: Dict[str, Any]) -> Tuple[List[Any], int]:
        """Process code block starting at given index."""
        try:
            elements = []
            i = start_index + 1  # Skip opening ```
            code_lines = []
            
            # Collect code lines until closing ```
            while i < len(lines):
                if lines[i].strip().startswith('```'):
                    break
                code_lines.append(lines[i])
                i += 1
            
            # Create code block
            if code_lines:
                code_content = '\n'.join(code_lines)
                clean_code = self.text_processor.clean_code_for_xml(code_content)
                
                # Use code style if available
                code_style = styles.get('Code')
                if code_style:
                    code_para = Paragraph(f'<pre>{clean_code}</pre>', code_style)
                    elements.append(KeepTogether([code_para]))
                    elements.append(Spacer(1, 12))
            
            return elements, i + 1  # Skip closing ```
            
        except Exception as e:
            self.logger.warning(f"Code block processing failed: {e}")
            return [], start_index + 1

    def get_available_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.TEMPLATE_CONFIGS.keys())
        
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get information about specific template."""
        return self.TEMPLATE_CONFIGS.get(template_name)
        
    def batch_generate(self,
                      content_list: List[Dict[str, Any]], 
                      max_workers: int = 4,
                      enable_advanced_features: bool = True) -> List[Dict[str, Any]]:
        """
        ADVANCED FEATURE 4: Batch PDF Generation
        Generate multiple PDFs in parallel using advanced batch processing
        
        Args:
            content_list: List of generation requests, each containing:
                         {'content': str, 'output_path': str, 'title': str, 'author': str, ...}
            max_workers: Maximum parallel workers
            enable_advanced_features: Enable advanced processing
            
        Returns:
            List of generation results for each request
        """
        if not enable_advanced_features:
            # Fallback to sequential processing
            results = []
            for i, request in enumerate(content_list):
                self.logger.info(f"Processing document {i+1}/{len(content_list)} sequentially")
                result = self.generate(**request, enable_advanced_features=False)
                results.append({
                    'index': i,
                    'success': result.get('success', False),
                    'result': result,
                    'original_request': request,
                    'error': result.get('error') if not result.get('success', False) else None
                })
            return results
        
        # Use advanced batch processor
        self.logger.info(f"🚀 Starting batch generation with {max_workers} workers for {len(content_list)} documents")
        
        def process_single_request(request: Dict[str, Any]) -> Dict[str, Any]:
            """Process single generation request"""
            return self.generate(**request, enable_advanced_features=True)
        
        # Extract content for batch processing validation
        contents = [req.get('content', '') for req in content_list]
        
        # Process batch with advanced batch processor
        batch_results = self.advanced_features['batch_processor'].process_batch(
            contents, 
            lambda content, **kwargs: process_single_request(content_list[contents.index(content)]),
            max_workers=max_workers
        )
        
        # Get batch processing stats
        batch_stats = self.advanced_features['batch_processor'].get_batch_stats()
        
        self.logger.info(f"✅ Batch generation completed")
        self.logger.info(f"📊 Batch stats: {batch_stats['success_rate']:.1f}% success rate, avg time: {batch_stats['average_batch_time']:.2f}s")
        
        return batch_results

    def get_advanced_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of advanced ReportLab system
        Returns detailed information about all advanced components
        """
        if not hasattr(self, 'advanced_features'):
            return {
                'advanced_features_enabled': False,
                'message': 'Advanced features not initialized'
            }
        
        return {
            'advanced_features_enabled': True,
            'template': self.template_name,
            'theme': self.theme_manager.theme_name,
            'available_templates': self.get_available_templates(),
            'available_themes': self.theme_manager.get_available_themes(),
            
            # Advanced component status
            'optimizer_stats': self.advanced_features['optimizer'].get_optimization_stats(),
            'batch_processor_stats': self.advanced_features['batch_processor'].get_batch_stats(),
            'performance_report': self.advanced_features['performance_monitor'].get_performance_report(),
            
            # Component information
            'components': {
                'theme_manager': type(self.theme_manager).__name__,
                'text_processor': type(self.text_processor).__name__,
                'content_processor': type(self.content_processor).__name__,
                'page_layout': type(self.page_layout).__name__,
                'content_optimizer': type(self.advanced_features['optimizer']).__name__,
                'security_validator': type(self.advanced_features['security_validator']).__name__,
                'batch_processor': type(self.advanced_features['batch_processor']).__name__,
                'performance_monitor': type(self.advanced_features['performance_monitor']).__name__
            }
        }
