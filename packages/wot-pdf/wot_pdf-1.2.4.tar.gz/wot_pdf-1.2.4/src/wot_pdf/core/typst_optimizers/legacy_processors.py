#!/usr/bin/env python3
"""
🔄 LEGACY OPTIMIZATION PROCESSORS
===============================
⚠️ Fallback processors for complex edge cases
🔧 Maintains compatibility with legacy optimization methods

These processors handle special cases that the main modular
optimizers might not handle correctly.
"""

import re
import uuid
from typing import Dict
import logging


class LegacyOptimizationProcessor:
    """
    Legacy optimization methods for complex edge cases.
    Uses original processing logic for maximum compatibility.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.protected_blocks = {}
    
    def process_content(self, content: str) -> str:
        """Main processing pipeline using legacy methods."""
        self.logger.info("🔄 Processing with legacy optimization methods")
        
        try:
            # Apply critical legacy optimizations in order
            content = self._smart_code_block_preprocessing(content)
            content = self._markdown_to_typst_converter(content)
            content = self._context_aware_character_handler(content)
            content = self._final_cleanup(content)
            
            self.logger.info("✅ Legacy optimization completed successfully")
            return content
            
        except Exception as e:
            self.logger.error(f"❌ Legacy processing failed: {e}")
            return content  # Return original on error
    
    def _smart_code_block_preprocessing(self, content: str) -> str:
        """Language-aware preprocessing with comment handling."""
        
        def process_code_block(match):
            full_block = match.group(0)
            language = match.group(1).strip() if match.group(1) else ""
            code_content = match.group(2)
            
            # Apply language-specific preprocessing
            if language.lower() == 'python':
                code_content = self._optimize_python_code(code_content)
            elif language.lower() in ['bash', 'shell', 'sh']:
                code_content = self._optimize_bash_code(code_content)
            elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                code_content = self._optimize_js_code(code_content)
            
            return f"```{language}\n{code_content}\n```"
        
        # Process all code blocks
        pattern = r'```(\w*)\n(.*?)\n```'
        content = re.sub(pattern, process_code_block, content, flags=re.DOTALL)
        
        return content
    
    def _optimize_python_code(self, code: str) -> str:
        """Optimize Python code blocks for Typst compatibility."""
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Handle inline comments that might confuse Typst
            if '#' in line and not line.strip().startswith('#'):
                # Check if # is in a string literal
                if '"' in line or "'" in line:
                    # Complex string processing - be conservative
                    optimized_lines.append(line)
                elif ' # ' in line:
                    # Inline comment - move to separate line
                    code_part = line.split(' # ')[0]
                    comment_part = '# ' + ' # '.join(line.split(' # ')[1:])
                    optimized_lines.append(code_part)
                    optimized_lines.append('    ' + comment_part)
                else:
                    optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _optimize_bash_code(self, code: str) -> str:
        """Optimize Bash code blocks for Typst compatibility."""
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Bash comments starting with # are usually fine
            # Focus on parameter expansion that might confuse Typst
            if '${' in line and '}' in line:
                # Parameter expansion - be careful with special chars
                line = line.replace('${', '$\\{').replace('}', '\\}')
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _optimize_js_code(self, code: str) -> str:
        """Optimize JavaScript code blocks for Typst compatibility."""
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Template literals and regex patterns
            if '`' in line and '${' in line:
                # Template literal - escape carefully
                line = re.sub(r'\$\{([^}]+)\}', r'$\\{\1\\}', line)
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _markdown_to_typst_converter(self, content: str) -> str:
        """Convert Markdown syntax to native Typst while preserving code blocks."""
        
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
        """Smart protection focusing on Python code embedded in documentation."""
        
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
    
    def _context_aware_character_handler(self, content: str) -> str:
        """Context-aware character handling with intelligent escaping."""
        
        lines = content.split('\n')
        processed_lines = []
        in_code_block = False
        
        for line in lines:
            # Track code block boundaries
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                processed_lines.append(line)
                continue
            
            # Skip processing inside code blocks
            if in_code_block:
                processed_lines.append(line)
                continue
            
            # Process regular content
            if '#' in line:
                # Check for legitimate Typst commands
                if re.match(r'\s*#(set|show|let|import|context|text|cite|code)\b', line):
                    # Legitimate Typst command - preserve
                    processed_lines.append(line)
                    continue
                
                # Check for Markdown/Typst headers (already converted)
                if line.strip().startswith('='):
                    # Typst header - preserve
                    processed_lines.append(line)
                    continue
                
                # Handle problematic # in content
                # Escape only standalone # that could confuse Typst
                line = re.sub(
                    r'(?<!\\)(?<!#)#(?![a-zA-Z{#=])',  # # not part of command/header
                    r'#{"#"}',  # Typst-safe escaping
                    line
                )
            
            # Handle other problematic characters
            if '%' in line and not in_code_block:
                # Escape % that might be interpreted as comments
                line = re.sub(r'(?<!\\)%(?![a-zA-Z])', r'\\%', line)
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _final_cleanup(self, content: str) -> str:
        """Final cleanup and validation."""
        
        # Remove any leftover protected block markers
        content = re.sub(r'PROTECTED_BLOCK_[a-f0-9]{32}', '', content)
        
        # Normalize line endings
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        # Remove excessive empty lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
