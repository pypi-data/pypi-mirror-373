#!/usr/bin/env python3
"""
📊 REPORTLAB CONTENT PROCESSOR - MARKDOWN PARSING
================================================
⚡ Advanced Markdown processing for ReportLab PDF generation
🔷 Table processing, heading management, and content structure
📝 Handles complex Markdown structures with professional formatting

Extracted from enhanced_reportlab_engine.py for better modularity.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple

try:
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    reportlab_available = True
except ImportError:
    reportlab_available = False


class ReportLabContentProcessor:
    """
    Advanced content processing for ReportLab PDF generation.
    Handles Markdown tables, headings, and content structuring.
    """

    def __init__(self, text_processor=None, theme_manager=None):
        """
        Initialize content processor.
        
        Args:
            text_processor: ReportLabTextProcessor instance for text cleaning
            theme_manager: ReportLabThemeManager instance for styling
        """
        self.logger = logging.getLogger(__name__)
        self.text_processor = text_processor
        self.theme_manager = theme_manager

    def process_markdown_table(self, lines: List[str], start_index: int) -> Tuple[Optional[List[List[str]]], int]:
        """
        Process Markdown table from lines starting at given index.
        
        Args:
            lines: List of content lines
            start_index: Index where table starts
            
        Returns:
            Tuple of (table_data, next_index) where table_data is None if no valid table
        """
        if not lines or start_index >= len(lines):
            return None, start_index

        try:
            table_data = []
            current_index = start_index
            
            # Process table rows
            while current_index < len(lines):
                line = lines[current_index].strip()
                
                # Empty line ends table
                if not line:
                    break
                    
                # Check if line looks like a table row
                if '|' in line:
                    # Split by | and clean up cells
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    
                    # Skip separator row (contains only -, :, |, and spaces)
                    if not re.match(r'^[\s\-:|]+$', line):
                        if cells:  # Only add non-empty rows
                            table_data.append(cells)
                else:
                    # Non-table line - stop processing
                    break
                    
                current_index += 1

            # Return table data if we have at least 2 rows
            if len(table_data) >= 2:
                return table_data, current_index
            else:
                return None, start_index
                
        except Exception as e:
            self.logger.warning(f"Table processing failed: {e}")
            return None, start_index

    def create_professional_table(self, table_data: List[List[str]]) -> Optional[Any]:
        """
        Create professionally styled ReportLab table.
        
        Args:
            table_data: List of rows, each row is list of cell contents
            
        Returns:
            ReportLab Table object or None if creation failed
        """
        if not table_data or not reportlab_available:
            return None

        try:
            # Process table data - clean text if text processor available
            processed_data = []
            for row in table_data:
                processed_row = []
                for cell in row:
                    if self.text_processor:
                        processed_cell = self.text_processor.gentle_clean_text(str(cell))
                    else:
                        processed_cell = str(cell)
                    processed_row.append(processed_cell)
                processed_data.append(processed_row)

            # Create table with processed data
            table = Table(processed_data)
            
            # Get theme colors if available
            if self.theme_manager:
                primary_color = self.theme_manager.get_theme_color('primary')
                accent_color = self.theme_manager.get_theme_color('accent')
                background_color = self.theme_manager.get_theme_color('background')
                border_color = self.theme_manager.get_theme_color('border')
            else:
                primary_color = HexColor('#2B2B2B') if reportlab_available else '#2B2B2B'
                accent_color = HexColor('#007ACC') if reportlab_available else '#007ACC'
                background_color = HexColor('#F8F8F8') if reportlab_available else '#F8F8F8'
                border_color = HexColor('#E0E0E0') if reportlab_available else '#E0E0E0'

            # Apply professional styling
            style = TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), accent_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -1), 1, border_color),
                ('LINEBELOW', (0, 0), (-1, 0), 2, primary_color),
                
                # Cell padding
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                
                # Alternating row colors
                ('BACKGROUND', (0, 1), (-1, -1), white),
            ])
            
            # Add alternating row colors for better readability
            for i in range(2, len(processed_data), 2):
                style.add('BACKGROUND', (0, i), (-1, i), background_color)

            table.setStyle(style)
            
            # Set column widths to be more balanced
            if len(processed_data[0]) > 1:
                col_widths = [2 * inch] * len(processed_data[0])
                table._argW = col_widths

            return table

        except Exception as e:
            self.logger.error(f"Professional table creation failed: {e}")
            return None

    def collect_headings(self, content: str) -> List[Dict[str, Any]]:
        """
        Collect all headings from Markdown content for table of contents.
        
        Args:
            content: Markdown content to analyze
            
        Returns:
            List of heading dictionaries with level, text, and line info
        """
        headings = []
        
        try:
            lines = content.split('\n')
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                # ATX-style headings (## Heading)
                match = re.match(r'^(#{1,6})\s+(.+)', line)
                if match:
                    level = len(match.group(1))
                    text = match.group(2).strip()
                    
                    # Clean heading text if text processor available
                    if self.text_processor:
                        clean_text = self.text_processor.gentle_clean_text(text)
                    else:
                        clean_text = text
                        
                    headings.append({
                        'level': level,
                        'text': clean_text,
                        'original_text': text,
                        'line_number': line_num,
                        'anchor': self._create_anchor(clean_text)
                    })

            return headings

        except Exception as e:
            self.logger.warning(f"Heading collection failed: {e}")
            return []

    def add_heading_numbers(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add hierarchical numbering to headings.
        
        Args:
            headings: List of heading dictionaries
            
        Returns:
            Updated headings with numbering information
        """
        if not headings:
            return headings

        try:
            # Track counters for each heading level
            counters = [0] * 6  # Support up to 6 levels
            
            for heading in headings:
                level = heading['level'] - 1  # Convert to 0-based index
                
                # Increment counter for current level
                counters[level] += 1
                
                # Reset deeper level counters
                for i in range(level + 1, 6):
                    counters[i] = 0
                
                # Build number string (e.g., "2.1.3")
                number_parts = []
                for i in range(level + 1):
                    if counters[i] > 0:
                        number_parts.append(str(counters[i]))
                
                heading['number'] = '.'.join(number_parts)
                heading['full_title'] = f"{heading['number']}. {heading['text']}"

            return headings

        except Exception as e:
            self.logger.warning(f"Heading numbering failed: {e}")
            return headings

    def apply_heading_numbers(self, content: str, headings: List[Dict[str, Any]]) -> str:
        """
        Apply heading numbers to content.
        
        Args:
            content: Original Markdown content
            headings: List of headings with numbering
            
        Returns:
            Content with numbered headings
        """
        if not headings:
            return content

        try:
            lines = content.split('\n')
            
            # Apply numbering to each heading
            for heading in headings:
                line_num = heading['line_number']
                if line_num < len(lines):
                    original_line = lines[line_num]
                    
                    # Extract heading markers (### )
                    match = re.match(r'^(#{1,6})\s+(.+)', original_line)
                    if match:
                        markers = match.group(1)
                        # Replace with numbered version
                        lines[line_num] = f"{markers} {heading['full_title']}"

            return '\n'.join(lines)

        except Exception as e:
            self.logger.warning(f"Heading numbering application failed: {e}")
            return content

    def _create_anchor(self, text: str) -> str:
        """
        Create URL-safe anchor from heading text.
        
        Args:
            text: Heading text
            
        Returns:
            Anchor string suitable for internal links
        """
        try:
            # Convert to lowercase and replace spaces with hyphens
            anchor = text.lower().replace(' ', '-')
            
            # Remove special characters, keep only alphanumeric and hyphens
            anchor = re.sub(r'[^a-z0-9\-]', '', anchor)
            
            # Remove multiple consecutive hyphens
            anchor = re.sub(r'-+', '-', anchor)
            
            # Remove leading/trailing hyphens
            anchor = anchor.strip('-')
            
            return anchor
            
        except Exception as e:
            self.logger.warning(f"Anchor creation failed: {e}")
            return "heading"

    def extract_code_blocks(self, content: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Extract code blocks from content for special processing.
        
        Args:
            content: Markdown content
            
        Returns:
            Tuple of (content_without_code_blocks, list_of_code_blocks)
        """
        code_blocks = []
        placeholders = []
        
        try:
            # Find fenced code blocks
            pattern = r'```(\w*)\n(.*?)```'
            matches = list(re.finditer(pattern, content, re.DOTALL))
            
            for i, match in enumerate(matches):
                language = match.group(1) or 'text'
                code_content = match.group(2)
                
                # Create placeholder
                placeholder = f"__CODE_BLOCK_{i}__"
                placeholders.append(placeholder)
                
                # Store code block info
                code_blocks.append({
                    'language': language,
                    'content': code_content,
                    'placeholder': placeholder
                })
            
            # Replace code blocks with placeholders
            processed_content = content
            for match, placeholder in zip(reversed(matches), reversed(placeholders)):
                processed_content = (processed_content[:match.start()] + 
                                   placeholder + 
                                   processed_content[match.end():])
            
            return processed_content, code_blocks

        except Exception as e:
            self.logger.warning(f"Code block extraction failed: {e}")
            return content, []

    def restore_code_blocks(self, content: str, code_blocks: List[Dict[str, str]]) -> str:
        """
        Restore code blocks to processed content.
        
        Args:
            content: Content with placeholders
            code_blocks: List of code blocks to restore
            
        Returns:
            Content with code blocks restored
        """
        try:
            restored_content = content
            
            for code_block in code_blocks:
                placeholder = code_block['placeholder']
                language = code_block['language']
                code_content = code_block['content']
                
                # Format code block for ReportLab
                formatted_block = f"```{language}\n{code_content}```"
                
                # Replace placeholder
                restored_content = restored_content.replace(placeholder, formatted_block)
                
            return restored_content

        except Exception as e:
            self.logger.warning(f"Code block restoration failed: {e}")
            return content
