#!/usr/bin/env python3
"""
🔄 TABLE CONVERTERS
==================
📊 Markdown table to Typst table conversion
🎯 Robust table processing with error handling

Converts Markdown tables to native Typst table syntax.
"""

import re
import logging
from typing import List, Tuple
from .syntax_generators import TypstSyntaxGenerator


class TableConverter:
    """Robust table conversion with proper error handling."""
    
    def __init__(self, syntax_gen: TypstSyntaxGenerator = None):
        self.syntax = syntax_gen if syntax_gen else TypstSyntaxGenerator()
        self.logger = logging.getLogger(__name__)
    
    def detect_tables(self, content: str) -> List[Tuple[int, int, str]]:
        """Detect markdown tables in content."""
        tables = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for table row pattern
            if self._is_table_row(line):
                table_start = i
                table_lines = [line]
                i += 1
                
                # Look for separator row
                if i < len(lines) and self._is_separator_row(lines[i].strip()):
                    table_lines.append(lines[i].strip())
                    i += 1
                
                # Collect data rows
                while i < len(lines) and self._is_table_row(lines[i].strip()):
                    table_lines.append(lines[i].strip())
                    i += 1
                
                # Validate (at least header + 1 data row)
                data_rows = [row for row in table_lines if not self._is_separator_row(row)]
                if len(data_rows) >= 2:
                    table_content = '\n'.join(table_lines)
                    tables.append((table_start, i - 1, table_content))
            else:
                i += 1
        
        return tables
    
    def _is_table_row(self, line: str) -> bool:
        """Check if line is a table row."""
        return (line.startswith('|') and 
                line.endswith('|') and 
                line.count('|') >= 3)
    
    def _is_separator_row(self, line: str) -> bool:
        """Check if line is separator row."""
        return bool(re.match(r'^\|[\s\-\|:]+\|$', line))
    
    def _parse_table_row(self, row: str) -> List[str]:
        """Parse table row into cells."""
        # Remove outer pipes
        if row.startswith('|'):
            row = row[1:]
        if row.endswith('|'):
            row = row[:-1]
        
        # Simple split by pipe
        cells = [cell.strip() for cell in row.split('|')]
        return cells
    
    def _process_cell_content(self, cell: str) -> str:
        """Process individual cell content."""
        if not cell.strip():
            return "[]"
        
        content = cell.strip()
        
        # Process markdown elements
        # Bold: **text** → *text*
        content = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', content)
        
        # Italic: *text* → _text_
        content = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', content)
        
        # Inline code: `code` → `code`
        content = re.sub(r'`([^`]+)`', 
                        lambda m: self.syntax.generate_inline_code(m.group(1)), 
                        content)
        
        # Links: [text](url) → link("url")[text]
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', 
                        lambda m: self.syntax.generate_link(m.group(2), m.group(1)), 
                        content)
        
        # Escape text content
        content = self.syntax.escape_text_content(content)
        
        return f'[{content}]'
    
    def convert_table(self, table_markdown: str) -> str:
        """Convert markdown table to Typst."""
        try:
            lines = [line.strip() for line in table_markdown.split('\n') if line.strip()]
            
            # Separate header and data
            header_row = None
            data_rows = []
            
            for line in lines:
                if self._is_separator_row(line):
                    continue
                elif header_row is None:
                    header_row = line
                else:
                    data_rows.append(line)
            
            if not header_row or not data_rows:
                return table_markdown  # Return original
            
            # Process header
            header_cells = self._parse_table_row(header_row)
            num_columns = len(header_cells)
            processed_header = [self._process_cell_content(cell) for cell in header_cells]
            
            # Process data rows
            processed_data = []
            for row in data_rows:
                cells = self._parse_table_row(row)
                # Normalize column count
                while len(cells) < num_columns:
                    cells.append("")
                cells = cells[:num_columns]
                
                processed_cells = [self._process_cell_content(cell) for cell in cells]
                processed_data.append(processed_cells)
            
            # Generate Typst table
            result_lines = [
                "#table(",
                f"  columns: {num_columns},",
                "  stroke: 0.5pt,",
                "  inset: 5pt,",
            ]
            
            # Add header
            header_line = "  " + ", ".join(processed_header) + ","
            result_lines.append(header_line)
            
            # Add data rows
            for row in processed_data:
                row_line = "  " + ", ".join(row) + ","
                result_lines.append(row_line)
            
            result_lines.append(")")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            self.logger.error(f"Table conversion failed: {e}")
            return table_markdown  # Return original on error


class AdvancedTableProcessor:
    """Advanced table processing with additional features."""
    
    def __init__(self):
        self.converter = TableConverter()
        self.logger = logging.getLogger(__name__)
    
    def process_all_tables(self, content: str) -> str:
        """Process all tables in content."""
        try:
            tables = self.converter.detect_tables(content)
            
            # Process tables in reverse order to maintain line positions
            for start_line, end_line, table_content in reversed(tables):
                typst_table = self.converter.convert_table(table_content)
                
                # Replace table content
                lines = content.split('\n')
                lines[start_line:end_line + 1] = [typst_table]
                content = '\n'.join(lines)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Advanced table processing failed: {e}")
            return content  # Return original on error
    
    def optimize_table_formatting(self, table_content: str) -> str:
        """Optimize table formatting for better readability."""
        try:
            lines = table_content.split('\n')
            optimized_lines = []
            
            for line in lines:
                if line.strip().startswith('#table('):
                    # Ensure proper indentation
                    optimized_lines.append('#table(')
                elif line.strip() == ')':
                    # Ensure proper closing
                    optimized_lines.append(')')
                elif 'columns:' in line or 'stroke:' in line or 'inset:' in line:
                    # Format table properties
                    optimized_lines.append(f'  {line.strip()}')
                elif line.strip():
                    # Format table data with proper indentation
                    optimized_lines.append(f'  {line.strip()}')
                else:
                    optimized_lines.append(line)
            
            return '\n'.join(optimized_lines)
            
        except Exception as e:
            self.logger.error(f"Table formatting optimization failed: {e}")
            return table_content  # Return original on error
