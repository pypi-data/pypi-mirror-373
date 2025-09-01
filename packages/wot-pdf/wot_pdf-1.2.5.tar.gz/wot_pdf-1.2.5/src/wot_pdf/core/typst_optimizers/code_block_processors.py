#!/usr/bin/env python3
"""
🔧 CODE BLOCK PROCESSORS - LANGUAGE-SPECIFIC OPTIMIZATION
=========================================================
⚡ Specialized processors for different programming languages
🔷 Optimizes code blocks for Typst compilation compatibility
📊 Language-aware syntax handling and character escaping

FEATURES:
- Python code optimization with keyword handling
- Bash/Shell script processing
- JavaScript/TypeScript optimization
- Generic code block preprocessing
- Character escaping for Typst compatibility

Extracted from typst_content_optimizer.py for better modularity.
"""

import re
import logging
from typing import Dict, List, Optional


class CodeBlockProcessors:
    """
    Language-specific code block processors for Typst optimization.
    Handles syntax-aware preprocessing for different programming languages.
    """
    
    def __init__(self):
        """Initialize code block processors."""
        self.logger = logging.getLogger(__name__)
        
        # Language-specific patterns and handlers
        self.language_handlers = {
            'python': self.optimize_python_code,
            'py': self.optimize_python_code,
            'bash': self.optimize_bash_code,
            'sh': self.optimize_bash_code,
            'shell': self.optimize_bash_code,
            'javascript': self.optimize_js_code,
            'js': self.optimize_js_code,
            'typescript': self.optimize_js_code,
            'ts': self.optimize_js_code
        }
        
    def process_code_block(self, language: str, code: str) -> str:
        """
        Process code block based on language type.
        
        Args:
            language: Programming language identifier
            code: Raw code content
            
        Returns:
            Processed code optimized for Typst
        """
        if not language or not code.strip():
            return code
            
        # Get appropriate handler for language
        handler = self.language_handlers.get(language.lower(), self.optimize_generic_code)
        
        try:
            processed_code = handler(code)
            self.logger.debug(f"🔧 Processed {language} code block ({len(code.split())} lines)")
            return processed_code
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to process {language} code: {e}")
            return self.optimize_generic_code(code)  # Fallback to generic
    
    def optimize_python_code(self, code: str) -> str:
        """
        Optimize Python code for Typst compilation.
        
        Args:
            code: Python source code
            
        Returns:
            Typst-compatible Python code
        """
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = line
            
            # Handle problematic Python constructs
            patterns_to_escape = [
                # String formatting that conflicts with Typst
                (r'f"([^"]*\{[^}]*\}[^"]*)"', r'f"\1"'),  # f-strings with braces
                (r"f'([^']*\{[^}]*\}[^']*)'", r"f'\1'"),  # f-strings with braces
                
                # Dictionary/set literals that might conflict
                (r'\{([^}]*)\}', lambda m: '{' + m.group(1) + '}' if ':' in m.group(1) else m.group(0)),
                
                # Comments with special characters
                (r'#\s*(.*)$', r'# \1'),
                
                # Docstrings with problematic characters
                (r'"""([^"]*)"""', r'"""\1"""'),
                (r"'''([^']*)'''", r"'''\1'''"),
            ]
            
            for pattern, replacement in patterns_to_escape:
                if callable(replacement):
                    processed_line = re.sub(pattern, replacement, processed_line)
                else:
                    processed_line = re.sub(pattern, replacement, processed_line)
            
            # Handle indentation preservation
            leading_spaces = len(processed_line) - len(processed_line.lstrip())
            if leading_spaces > 0:
                processed_line = ' ' * leading_spaces + processed_line.lstrip()
            
            processed_lines.append(processed_line)
        
        return '\n'.join(processed_lines)
    
    def optimize_bash_code(self, code: str) -> str:
        """
        Optimize Bash/Shell code for Typst compilation.
        
        Args:
            code: Bash/Shell source code
            
        Returns:
            Typst-compatible bash code
        """
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = line
            
            # Handle bash-specific constructs
            replacements = [
                # Variable substitution that might conflict
                (r'\$\{([^}]+)\}', r'${\1}'),  # Preserve variable syntax
                
                # Command substitution
                (r'\$\(([^)]+)\)', r'$(\1)'),  # Preserve command substitution
                
                # Handle pipes and redirections
                (r'\|', r'|'),  # Preserve pipes
                (r'>>', r'>>'),  # Preserve append redirect
                (r'>', r'>'),   # Preserve redirect
                
                # Comments
                (r'#\s*(.*)$', r'# \1'),
                
                # String quoting - preserve as-is for bash
                (r'"([^"]*)"', r'"\1"'),
                (r"'([^']*)'", r"'\1'"),
            ]
            
            for pattern, replacement in replacements:
                processed_line = re.sub(pattern, replacement, processed_line)
            
            processed_lines.append(processed_line)
        
        return '\n'.join(processed_lines)
    
    def optimize_js_code(self, code: str) -> str:
        """
        Optimize JavaScript/TypeScript code for Typst compilation.
        
        Args:
            code: JavaScript/TypeScript source code
            
        Returns:
            Typst-compatible JavaScript code
        """
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = line
            
            # Handle JavaScript-specific constructs
            replacements = [
                # Template literals that might conflict with Typst
                (r'`([^`]*\$\{[^}]*\}[^`]*)`', r'`\1`'),  # Template literals
                
                # Object literals
                (r'\{([^}]*)\}', lambda m: '{' + m.group(1) + '}' if ':' in m.group(1) else m.group(0)),
                
                # Arrow functions
                (r'=>\s*\{', r'=> {'),  # Arrow function formatting
                
                # Regex literals
                (r'/([^/]+)/([gimuy]*)', r'/\1/\2'),  # Preserve regex flags
                
                # Comments
                (r'//\s*(.*)$', r'// \1'),  # Single line comments
                (r'/\*([^*]*)\*/', r'/*\1*/'),  # Multi-line comments
                
                # String literals
                (r'"([^"]*)"', r'"\1"'),  # Double quotes
                (r"'([^']*)'", r"'\1'"),  # Single quotes
            ]
            
            for pattern, replacement in replacements:
                if callable(replacement):
                    processed_line = re.sub(pattern, replacement, processed_line)
                else:
                    processed_line = re.sub(pattern, replacement, processed_line)
            
            processed_lines.append(processed_line)
        
        return '\n'.join(processed_lines)
    
    def optimize_generic_code(self, code: str) -> str:
        """
        Generic code optimization for unknown languages.
        
        Args:
            code: Source code in any language
            
        Returns:
            Typst-compatible code with basic optimizations
        """
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = line
            
            # Basic character escaping that applies to all languages
            basic_replacements = [
                # Preserve basic structure but escape problematic chars
                (r'\\', r'\\\\'),  # Escape backslashes
                
                # Handle common comment patterns
                (r'#\s*(.*)$', r'# \1'),      # Hash comments
                (r'//\s*(.*)$', r'// \1'),    # Double slash comments
                (r'/\*([^*]*)\*/', r'/*\1*/'), # Block comments
                
                # Basic string handling
                (r'"([^"]*)"', r'"\1"'),      # Double quotes
                (r"'([^']*)'", r"'\1'"),      # Single quotes
            ]
            
            for pattern, replacement in basic_replacements:
                processed_line = re.sub(pattern, replacement, processed_line)
            
            processed_lines.append(processed_line)
        
        return '\n'.join(processed_lines)
    
    def smart_code_block_preprocessing(self, content: str) -> str:
        """
        Process all code blocks in content with language-aware optimization.
        
        Args:
            content: Full markdown content with code blocks
            
        Returns:
            Content with optimized code blocks
        """
        def process_code_block_match(match):
            language = match.group(1) or 'text'
            code = match.group(2)
            
            # Process the code block with appropriate handler
            processed_code = self.process_code_block(language, code)
            
            # Return formatted code block
            return f'```{language}\n{processed_code}\n```'
        
        # Process all code blocks in the content
        pattern = r'```(\w*)\n(.*?)\n```'
        processed_content = re.sub(pattern, process_code_block_match, content, flags=re.DOTALL)
        
        return processed_content
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return list(self.language_handlers.keys())
    
    def add_language_handler(self, language: str, handler_func) -> None:
        """
        Add custom language handler.
        
        Args:
            language: Language identifier
            handler_func: Function that processes code for this language
        """
        self.language_handlers[language.lower()] = handler_func
        self.logger.info(f"🔧 Added handler for {language}")
    
    def get_processing_stats(self) -> Dict[str, int]:
        """Get statistics about code block processing."""
        return {
            'supported_languages': len(self.language_handlers),
            'handlers_available': len(self.language_handlers)
        }
