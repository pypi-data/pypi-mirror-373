#!/usr/bin/env python3
"""
🔄 CONTENT CONVERTERS
===================
📄 Specialized converters for complex content transformations
🔧 Handles RAW block conversion and other advanced transformations

Used for content that requires special handling during optimization.
"""

import re
import logging


class RawBlockConverter:
    """
    Converts problematic content sections to RAW Typst blocks.
    Used when content contains complex Python-like patterns that
    might confuse the Typst parser.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_to_raw_blocks(self, content: str) -> str:
        """Convert problematic content sections to RAW Typst blocks."""
        
        # Split content into sections
        lines = content.split('\n')
        result = []
        current_section = []
        in_raw_section = False
        
        for line in lines:
            # Check if line contains problematic Python-like content
            is_problematic = (
                re.search(r"'[^']+'\s*:\s*\d+[^,]*#.*", line) or  # Dict with comments
                re.search(r"^\s*#\s+\d+\.", line) or              # Numbered comments
                re.search(r"def\s+|class\s+|import\s+|from\s+", line) or  # Python keywords
                re.search(r"\s+#\s+(EUR|initialize|calculate)", line, re.IGNORECASE)  # Common patterns
            )
            
            if is_problematic and not in_raw_section:
                # Start RAW section
                if current_section:
                    result.extend(current_section)
                    current_section = []
                result.append("```")
                result.append("#raw[")
                in_raw_section = True
            
            if in_raw_section:
                # Escape problematic characters for RAW blocks
                escaped_line = line.replace('\\', '\\\\').replace('"', '\\"')
                result.append(f'"{escaped_line}\\n" +')
            else:
                current_section.append(line)
            
            # Check if we should end RAW section (after empty lines or section breaks)
            if in_raw_section and (not line.strip() or line.startswith('#')):
                # Look ahead to see if next problematic content is coming
                should_continue_raw = False
                # This is a simple heuristic - in practice might need refinement
                
                if not should_continue_raw:
                    result[-1] = result[-1].rstrip(' +')  # Remove trailing +
                    result.append("]")
                    result.append("```")
                    in_raw_section = False
        
        # Add remaining content
        if current_section:
            result.extend(current_section)
        
        if in_raw_section:
            result[-1] = result[-1].rstrip(' +')  # Remove trailing +
            result.append("]")
            result.append("```")
        
        return '\n'.join(result)


class MarkdownToTypstConverter:
    """
    Converts Markdown syntax to native Typst while preserving code blocks.
    Handles headers, formatting, and lists appropriately.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.protected_blocks = {}
    
    def convert_content(self, content: str) -> str:
        """Main conversion method."""
        
        # First, protect code blocks from conversion
        content = self._protect_code_blocks(content)
        
        lines = content.split('\n')
        converted_lines = []
        
        for line in lines:
            # Skip protected blocks
            if line.strip().startswith('PROTECTED_BLOCK_'):
                converted_lines.append(line)
                continue
            
            # Convert headers: # Title -> = Title
            # BUT ONLY if it's a real markdown header (has space after #)
            if line.strip().startswith('#') and ' ' in line.strip()[1:]:
                header_level = 0
                temp_line = line.lstrip()
                while temp_line.startswith('#'):
                    header_level += 1
                    temp_line = temp_line[1:]
                
                if header_level > 0 and temp_line.strip():
                    title = temp_line.strip()
                    # Use Typst header syntax
                    typst_header = '=' * header_level + ' ' + title
                    converted_lines.append(typst_header)
                    continue
            
            # Convert bold: **text** -> *text*
            line = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', line)
            
            # Convert italic: *text* -> _text_ (avoid conflicts with bold)
            line = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', line)
            
            # Convert lists (Typst uses - for bullets)
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                line = re.sub(r'^(\s*)[*-] ', r'\1- ', line)
            
            converted_lines.append(line)
        
        content = '\n'.join(converted_lines)
        
        # Restore protected code blocks
        content = self._restore_code_blocks(content)
        
        return content
    
    def _protect_code_blocks(self, content: str) -> str:
        """Protect code blocks from conversion."""
        import uuid
        
        lines = content.split('\n')
        result_lines = []
        in_python_block = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            protected = False
            
            # Skip empty lines
            if not line.strip():
                result_lines.append(line)
                i += 1
                continue
            
            # Detect start/end of Python code blocks
            if line.strip().startswith('```python') or line.strip() == '```python':
                in_python_block = True
                # Protect entire Python block
                block_lines = [line]
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    block_lines.append(lines[i])
                    i += 1
                if i < len(lines):  # Add closing ```
                    block_lines.append(lines[i])
                    in_python_block = False
                
                block_id = f"PROTECTED_BLOCK_{uuid.uuid4().hex}"
                self.protected_blocks[block_id] = '\n'.join(block_lines)
                result_lines.append(block_id)
                protected = True
            
            # Detect generic code blocks (```)
            elif line.strip().startswith('```') and not in_python_block:
                block_lines = [line]
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    block_lines.append(lines[i])
                    i += 1
                if i < len(lines):  # Add closing ```
                    block_lines.append(lines[i])
                
                block_id = f"PROTECTED_BLOCK_{uuid.uuid4().hex}"
                self.protected_blocks[block_id] = '\n'.join(block_lines)
                result_lines.append(block_id)
                protected = True
            
            # Handle inline code separately (but only if not already protected)
            elif not protected and '`' in line:
                def protect_inline(match):
                    block_id = f"PROTECTED_BLOCK_{uuid.uuid4().hex}"
                    self.protected_blocks[block_id] = match.group(0)
                    return block_id
                
                line = re.sub(r'`[^`\n]+`', protect_inline, line)
                result_lines.append(line)
                protected = True
            
            if not protected:
                result_lines.append(line)
            
            i += 1
        
        return '\n'.join(result_lines)
    
    def _restore_code_blocks(self, content: str) -> str:
        """Restore protected code blocks."""
        for block_id, original_content in self.protected_blocks.items():
            content = content.replace(block_id, original_content)
        
        # Clear the protected blocks for next use
        self.protected_blocks.clear()
        return content
