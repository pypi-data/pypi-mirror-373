"""
Table Processor
Specialized table processing and enhancement
"""

import re
import logging
from typing import Dict, Any, Optional, List

from ...abstractions.base.processor import BaseProcessor

class TableProcessor(BaseProcessor):
    """Specialized table content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._logger = logging.getLogger(__name__)
        self.table_count = 0
        
    def process(self, content: str, **kwargs) -> str:
        """Process tables in content"""
        
        self._logger.debug("Processing tables...")
        
        # Reset counter
        self.table_count = 0
        
        # Process markdown tables
        processed = self._process_markdown_tables(content)
        
        # Add table captions if needed
        processed = self._add_table_captions(processed)
        
        self._logger.info(f"Processed {self.table_count} tables")
        
        return processed
    
    def _process_markdown_tables(self, content: str) -> str:
        """Process markdown tables"""
        
        lines = content.split('\n')
        processed_lines = []
        in_table = False
        table_lines = []
        
        for line in lines:
            # Detect table start
            if '|' in line and not in_table:
                in_table = True
                table_lines = [line]
            elif '|' in line and in_table:
                table_lines.append(line)
            elif in_table and '|' not in line:
                # End of table
                processed_table = self._enhance_table(table_lines)
                processed_lines.extend(processed_table)
                processed_lines.append(line)
                in_table = False
                table_lines = []
                self.table_count += 1
            else:
                processed_lines.append(line)
        
        # Handle table at end of content
        if in_table and table_lines:
            processed_table = self._enhance_table(table_lines)
            processed_lines.extend(processed_table)
            self.table_count += 1
        
        return '\n'.join(processed_lines)
    
    def _enhance_table(self, table_lines: List[str]) -> List[str]:
        """Enhance individual table"""
        
        enhanced = []
        
        for line in table_lines:
            # Clean up table formatting
            clean_line = line.strip()
            
            # Skip separator lines like |---|---|
            if self._is_separator_line(clean_line):
                continue
            
            # Process table cells
            if '|' in clean_line:
                enhanced_line = self._process_table_cells(clean_line)
                enhanced.append(enhanced_line)
        
        return enhanced
    
    def _is_separator_line(self, line: str) -> bool:
        """Check if line is a table separator"""
        
        # Pattern for separator lines: |---|---|
        separator_pattern = r'^\|\s*[-:]+\s*(\|\s*[-:]+\s*)*\|?\s*$'
        return bool(re.match(separator_pattern, line))
    
    def _process_table_cells(self, line: str) -> str:
        """Process individual table cells"""
        
        # Split by | but preserve cell content
        cells = line.split('|')
        processed_cells = []
        
        for cell in cells:
            processed_cell = cell.strip()
            
            # Apply cell formatting if needed
            processed_cell = self._format_cell_content(processed_cell)
            
            processed_cells.append(processed_cell)
        
        return '|'.join(processed_cells)
    
    def _format_cell_content(self, cell: str) -> str:
        """Format individual cell content"""
        
        # Preserve existing markdown formatting
        # Bold: **text**
        # Italic: *text*
        # Code: `code`
        
        return cell
    
    def _add_table_captions(self, content: str) -> str:
        """Add table captions where needed"""
        
        lines = content.split('\n')
        processed_lines = []
        table_num = 1
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a table start
            if '|' in line and not self._is_separator_line(line):
                # Look for existing caption above or below
                has_caption_above = (i > 0 and 
                                   'Table' in lines[i-1] and 
                                   ':' in lines[i-1])
                
                # Add caption if none exists
                if not has_caption_above:
                    caption = f"{{TABLE_CAPTION:table{table_num}:Table {table_num}}}"
                    processed_lines.append(caption)
                    table_num += 1
                
                # Add the table line
                processed_lines.append(line)
                
                # Skip to end of table
                j = i + 1
                while j < len(lines) and '|' in lines[j]:
                    if not self._is_separator_line(lines[j]):
                        processed_lines.append(lines[j])
                    j += 1
                
                i = j - 1
            else:
                processed_lines.append(line)
            
            i += 1
        
        return '\n'.join(processed_lines)
    
    def validate(self, content: str) -> bool:
        """Validate table content"""
        
        lines = content.split('\n')
        
        for line in lines:
            if '|' in line:
                # Check for proper table structure
                if line.count('|') < 2:
                    self._logger.warning(f"Malformed table line: {line}")
                    return False
        
        return True
    
    def get_table_stats(self, content: str) -> Dict[str, Any]:
        """Get table statistics"""
        
        lines = content.split('\n')
        table_lines = [line for line in lines if '|' in line and not self._is_separator_line(line)]
        
        return {
            "table_count": content.count('\n|'),
            "table_lines": len(table_lines),
            "separator_lines": len([line for line in lines if self._is_separator_line(line)])
        }
