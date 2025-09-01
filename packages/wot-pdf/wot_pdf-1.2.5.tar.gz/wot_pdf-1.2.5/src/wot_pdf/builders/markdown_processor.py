#!/usr/bin/env python3
"""
📝 MARKDOWN PROCESSOR - MD→TYPST CONVERSION
==========================================
⚡ Advanced Markdown to Typst conversion with image and table processing
🔷 Handles diagrams, tables, images, and metadata extraction
📊 Professional formatting with List of Figures/Tables support

FEATURES:
- Diagram block detection and processing
- Markdown table conversion to Typst
- Image processing with caption/label support
- List of Figures/Tables generation
- Smart content optimization

Extracted from production_builder.py for better modularity.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass


@dataclass
class ConversionStats:
    """Statistics for Markdown conversion process"""
    images_processed: int = 0
    tables_processed: int = 0
    diagrams_found: int = 0
    figures_extracted: int = 0
    processing_time_ms: float = 0.0


class MarkdownProcessor:
    """
    Advanced Markdown to Typst conversion with professional formatting.
    Handles diagrams, tables, images, and metadata extraction.
    """

    def __init__(self, diagram_processor=None, content_optimizer=None):
        """
        Initialize Markdown processor.
        
        Args:
            diagram_processor: DiagramProcessor instance for diagram rendering
            content_optimizer: UnifiedTypstContentOptimizer for content processing
        """
        self.logger = logging.getLogger(__name__)
        self.diagram_processor = diagram_processor
        self.content_optimizer = content_optimizer
        
        # Statistics
        self.stats = ConversionStats()
        
        # Collected metadata for document generation
        self.figures = []
        self.tables = []

    def find_diagram_blocks(self, md_text: str) -> List[Tuple[str, str, re.Match]]:
        """
        Find all diagram code blocks in Markdown text.
        
        Args:
            md_text: Markdown text to search
            
        Returns:
            List of tuples (language, code, match_object)
        """
        diagram_blocks = []
        
        # Pattern for fenced code blocks with language
        pattern = r'```(\w+)\n(.*?)```'
        
        for match in re.finditer(pattern, md_text, re.DOTALL):
            language = match.group(1).lower()
            code = match.group(2)
            
            # Check if it's a supported diagram language
            if self.diagram_processor and self.diagram_processor.is_engine_available(language):
                diagram_blocks.append((language, code, match))
                self.stats.diagrams_found += 1
                
        return diagram_blocks

    def process_markdown_images(self, text: str) -> str:
        """
        Process Markdown images and convert to Typst format.
        
        Args:
            text: Markdown text containing images
            
        Returns:
            Text with images converted to Typst format
        """
        def replace_image(match):
            alt_text = match.group(1) or ""
            url = match.group(2)
            
            # Check for label in alt text {#fig:label}
            label_match = re.search(r'\{#(fig:[\w\-_]+)\}', alt_text)
            label = ""
            if label_match:
                label = f'<{label_match.group(1)}>'
                alt_text = re.sub(r'\s*\{#fig:[\w\-_]+\}', '', alt_text)
                self.stats.figures_extracted += 1
            
            # Download image if it's a URL
            if url.startswith(('http://', 'https://')):
                if self.diagram_processor:
                    local_path = self.diagram_processor.download_image(url)
                    if local_path:
                        url = local_path
            
            self.stats.images_processed += 1
            
            # Convert to Typst figure format
            if alt_text:
                return f'#figure(image("{url}"), caption: [{alt_text}]) {label}'
            else:
                return f'#figure(image("{url}")) {label}'

        # Pattern for Markdown images: ![alt](url)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        result = re.sub(image_pattern, replace_image, text)
        
        return result

    def process_markdown_tables(self, text: str) -> str:
        """
        Convert Markdown tables to Typst table format.
        
        Args:
            text: Markdown text containing tables
            
        Returns:
            Text with tables converted to Typst format
        """
        def process_table_block(match):
            table_text = match.group(0)
            lines = table_text.strip().split('\n')
            
            if len(lines) < 2:
                return table_text  # Not a valid table
            
            # Parse header row
            header_row = lines[0]
            header_cells = [cell.strip() for cell in header_row.split('|') if cell.strip()]
            
            if not header_cells:
                return table_text
                
            # Skip separator row (if exists)
            data_start = 1
            if len(lines) > 1 and re.match(r'^[\s\|:\-]+$', lines[1]):
                data_start = 2
            
            # Parse data rows
            data_rows = []
            for i in range(data_start, len(lines)):
                line = lines[i].strip()
                if line:
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if cells:
                        data_rows.append(cells)
            
            if not data_rows:
                return table_text
            
            # Generate Typst table
            typst_table = self._generate_typst_table(header_cells, data_rows)
            self.stats.tables_processed += 1
            
            return typst_table

        # Pattern for Markdown tables (multiline)
        table_pattern = r'^[\s]*\|.*\|[\s]*$(?:\n[\s]*\|.*\|[\s]*$)+'
        result = re.sub(table_pattern, process_table_block, text, flags=re.MULTILINE)
        
        return result

    def _generate_typst_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """
        Generate Typst table syntax from header and data rows.
        
        Args:
            headers: Table header cells
            rows: Table data rows
            
        Returns:
            Typst table syntax
        """
        # Calculate column count
        max_cols = max(len(headers), max(len(row) for row in rows) if rows else 0)
        
        # Pad headers and rows to same length
        while len(headers) < max_cols:
            headers.append("")
            
        for row in rows:
            while len(row) < max_cols:
                row.append("")
        
        # Generate Typst table
        typst_lines = []
        typst_lines.append(f"#table(")
        typst_lines.append(f"  columns: {max_cols},")
        typst_lines.append(f"  stroke: 0.5pt,")
        typst_lines.append(f"  fill: (x, y) => if y == 0 {{ gray.lighten(80%) }},")
        
        # Add header row
        header_line = "  " + ", ".join(f'[*{cell}*]' for cell in headers) + ","
        typst_lines.append(header_line)
        
        # Add data rows
        for row in rows:
            row_line = "  " + ", ".join(f'[{cell}]' for cell in row) + ","
            typst_lines.append(row_line)
        
        typst_lines.append(")")
        
        return "\n".join(typst_lines)

    def convert_markdown_to_typst(self, text: str) -> str:
        """
        Convert Markdown text to Typst format with full processing pipeline.
        
        Args:
            text: Input Markdown text
            
        Returns:
            Converted Typst text
        """
        try:
            processed_text = text
            
            # Step 1: Process diagrams if processor available
            if self.diagram_processor:
                processed_text = self._process_diagram_blocks(processed_text)
            
            # Step 2: Process images
            processed_text = self.process_markdown_images(processed_text)
            
            # Step 3: Process tables
            processed_text = self.process_markdown_tables(processed_text)
            
            # Step 4: Apply content optimizer if available
            if self.content_optimizer:
                processed_text = self.content_optimizer.optimize_content(processed_text)
            
            # Step 5: Convert basic Markdown syntax to Typst
            processed_text = self._convert_basic_markdown(processed_text)
            
            return processed_text
            
        except Exception as e:
            self.logger.error(f"❌ Markdown conversion failed: {e}")
            return text

    def _process_diagram_blocks(self, text: str) -> str:
        """Process diagram blocks and replace with Typst figures."""
        diagram_blocks = self.find_diagram_blocks(text)
        
        for language, code, match in reversed(diagram_blocks):  # Reverse to maintain indices
            try:
                # Extract metadata from diagram
                metadata = self.diagram_processor.extract_metadata(language, code)
                
                # Render diagram
                rendered_path = self.diagram_processor.render_diagram(language, code, metadata)
                
                if rendered_path:
                    # Create Typst figure
                    figure_code = f'#figure(image("{rendered_path}"),'
                    
                    if metadata.caption:
                        figure_code += f' caption: [{metadata.caption}]'
                        
                    figure_code += ')'
                    
                    if metadata.label:
                        figure_code += f' <{metadata.label}>'
                    
                    # Replace original diagram block
                    text = text[:match.start()] + figure_code + text[match.end():]
                    
                else:
                    self.logger.warning(f"⚠️ Failed to render {language} diagram, keeping original")
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing {language} diagram: {e}")
                
        return text

    def _convert_basic_markdown(self, text: str) -> str:
        """Convert basic Markdown syntax to Typst."""
        # Headers
        text = re.sub(r'^# (.+)$', r'= \1', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'== \1', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'=== \1', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.+)$', r'==== \1', text, flags=re.MULTILINE)
        text = re.sub(r'^##### (.+)$', r'===== \1', text, flags=re.MULTILINE)
        text = re.sub(r'^###### (.+)$', r'====== \1', text, flags=re.MULTILINE)
        
        # Bold and italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', text)
        text = re.sub(r'\*([^*]+)\*', r'_\1_', text)
        
        # Code blocks (preserve fenced blocks that weren't diagrams)
        text = re.sub(r'```(\w+)?\n(.*?)```', r'```\1\n\2```', text, flags=re.DOTALL)
        
        # Inline code
        text = re.sub(r'`([^`]+)`', r'`\1`', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'#link("\2")[\1]', text)
        
        # Lists
        text = re.sub(r'^- (.+)$', r'- \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\* (.+)$', r'- \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\. (.+)$', r'+ \1', text, flags=re.MULTILINE)
        
        return text

    def generate_list_of_figures(self) -> str:
        """Generate List of Figures section in Typst format."""
        if not self.figures:
            return ""
            
        lof = ["= List of Figures", ""]
        for i, figure in enumerate(self.figures, 1):
            lof.append(f"{i}. {figure['caption']} ... @{figure['label']}")
        
        return "\n".join(lof) + "\n\n"

    def generate_list_of_tables(self) -> str:
        """Generate List of Tables section in Typst format.""" 
        if not self.tables:
            return ""
            
        lot = ["= List of Tables", ""]
        for i, table in enumerate(self.tables, 1):
            lot.append(f"{i}. {table['caption']} ... @{table['label']}")
        
        return "\n".join(lot) + "\n\n"

    def get_stats(self) -> ConversionStats:
        """Get current conversion statistics."""
        return self.stats

    def reset_stats(self):
        """Reset conversion statistics."""
        self.stats = ConversionStats()
        self.figures.clear()
        self.tables.clear()
