"""
Code Processor
Code block processing and syntax highlighting
"""

import re
import logging
from typing import Dict, Any, Optional, List

from ...abstractions.base.processor import BaseProcessor

class CodeProcessor(BaseProcessor):
    """Code block content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._logger = logging.getLogger(__name__)
        self.code_block_count = 0
        
        # Supported languages
        self.supported_languages = {
            'python', 'javascript', 'java', 'c', 'cpp', 'csharp', 
            'go', 'rust', 'php', 'ruby', 'swift', 'kotlin',
            'html', 'css', 'scss', 'sass', 'json', 'xml', 'yaml',
            'bash', 'shell', 'powershell', 'dockerfile',
            'sql', 'markdown', 'latex', 'typst'
        }
        
    def process(self, content: str, **kwargs) -> str:
        """Process code blocks in content"""
        
        self._logger.debug("Processing code blocks...")
        
        # Reset counter
        self.code_block_count = 0
        
        # Process fenced code blocks
        processed = self._process_fenced_code_blocks(content)
        
        # Process inline code
        processed = self._process_inline_code(processed)
        
        self._logger.info(f"Processed {self.code_block_count} code blocks")
        
        return processed
    
    def _process_fenced_code_blocks(self, content: str) -> str:
        """Process fenced code blocks (```)"""
        
        # Pattern for fenced code blocks: ```language\ncode\n```
        pattern = r'```([a-zA-Z0-9_+-]*)?\n?(.*?)\n?```'
        
        def replace_code_block(match):
            language = match.group(1) or 'text'
            code = match.group(2)
            
            self.code_block_count += 1
            
            # Validate and normalize language
            normalized_language = self._normalize_language(language)
            
            # Clean and format code
            formatted_code = self._format_code(code)
            
            return f'```{normalized_language}\n{formatted_code}\n```'
        
        return re.sub(pattern, replace_code_block, content, flags=re.DOTALL)
    
    def _process_inline_code(self, content: str) -> str:
        """Process inline code (`code`)"""
        
        # Pattern for inline code: `code`
        pattern = r'`([^`]+)`'
        
        def replace_inline_code(match):
            code = match.group(1)
            
            # Clean inline code
            cleaned_code = code.strip()
            
            return f'`{cleaned_code}`'
        
        return re.sub(pattern, replace_inline_code, content)
    
    def _normalize_language(self, language: str) -> str:
        """Normalize language identifier"""
        
        if not language:
            return 'text'
        
        # Convert common aliases
        language_aliases = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'sh': 'bash',
            'ps1': 'powershell',
            'cs': 'csharp',
            'cpp': 'cpp',
            'c++': 'cpp',
            'yml': 'yaml'
        }
        
        normalized = language.lower()
        normalized = language_aliases.get(normalized, normalized)
        
        # Check if supported
        if normalized in self.supported_languages:
            return normalized
        else:
            self._logger.debug(f"Unsupported language: {language}, using 'text'")
            return 'text'
    
    def _format_code(self, code: str) -> str:
        """Format code content"""
        
        # Remove excessive whitespace while preserving structure
        lines = code.split('\n')
        
        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        return '\n'.join(lines)
    
    def validate(self, content: str) -> bool:
        """Validate code block syntax"""
        
        # Check for unmatched code block delimiters
        if content.count('```') % 2 != 0:
            self._logger.error("Unmatched code block delimiters")
            return False
        
        # Check for unmatched inline code
        if content.count('`') % 2 != 0:
            self._logger.warning("Unmatched inline code delimiters")
            # This is not necessarily an error, continue processing
        
        return True
    
    def get_code_stats(self, content: str) -> Dict[str, Any]:
        """Get code block statistics"""
        
        # Count fenced code blocks
        fenced_pattern = r'```([a-zA-Z0-9_+-]*)?\n?(.*?)\n?```'
        fenced_blocks = re.findall(fenced_pattern, content, re.DOTALL)
        
        # Count inline code
        inline_pattern = r'`([^`]+)`'
        inline_code = re.findall(inline_pattern, content)
        
        # Language statistics
        languages = [block[0] or 'text' for block in fenced_blocks]
        language_counts = {}
        for lang in languages:
            normalized = self._normalize_language(lang)
            language_counts[normalized] = language_counts.get(normalized, 0) + 1
        
        return {
            "fenced_blocks": len(fenced_blocks),
            "inline_code": len(inline_code),
            "languages_used": language_counts,
            "total_code_elements": len(fenced_blocks) + len(inline_code)
        }
