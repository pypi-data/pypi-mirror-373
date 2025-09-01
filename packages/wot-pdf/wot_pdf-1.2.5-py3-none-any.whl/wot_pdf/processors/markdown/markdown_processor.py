"""
Markdown Processor
Main markdown content processing and coordination
"""

import logging
from typing import Dict, Any, Optional, List

from ...abstractions.base.processor import BaseProcessor

class MarkdownProcessor(BaseProcessor):
    """Main markdown content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._logger = logging.getLogger(__name__)
        
    def process(self, content: str, **kwargs) -> str:
        """Process markdown content"""
        
        self._logger.debug("Processing markdown content...")
        
        # Process headers
        processed = self._process_headers(content)
        
        # Process links
        processed = self._process_links(processed)
        
        # Process text formatting
        processed = self._process_text_formatting(processed)
        
        # Process lists
        processed = self._process_lists(processed)
        
        self._logger.debug("Markdown processing complete")
        
        return processed
    
    def _process_headers(self, content: str) -> str:
        """Process markdown headers"""
        
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Check for ATX headers (# ## ###)
            if stripped.startswith('#'):
                # Count header level
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # Extract header text
                header_text = stripped[level:].strip()
                
                # Generate header ID if needed
                header_id = self._generate_header_id(header_text)
                
                # Format header with proper spacing
                formatted_header = f"{'#' * level} {header_text}"
                if header_id:
                    formatted_header += f" {{#{header_id}}}"
                
                processed_lines.append(formatted_header)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _generate_header_id(self, header_text: str) -> str:
        """Generate header ID for cross-references"""
        
        # Convert to lowercase and replace spaces with hyphens
        header_id = header_text.lower().replace(' ', '-')
        
        # Remove special characters
        import re
        header_id = re.sub(r'[^a-z0-9-]', '', header_id)
        
        # Remove multiple hyphens
        header_id = re.sub(r'-+', '-', header_id)
        
        # Remove leading/trailing hyphens
        header_id = header_id.strip('-')
        
        return header_id
    
    def _process_links(self, content: str) -> str:
        """Process markdown links"""
        
        import re
        
        # Pattern for markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        def format_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Validate URL if needed
            if self._validate_url(url):
                return f'[{text}]({url})'
            else:
                self._logger.warning(f"Invalid URL: {url}")
                return f'[{text}](INVALID_URL)'
        
        return re.sub(link_pattern, format_link, content)
    
    def _validate_url(self, url: str) -> bool:
        """Basic URL validation"""
        
        # Allow relative paths, absolute URLs, and anchors
        if (url.startswith('http://') or 
            url.startswith('https://') or 
            url.startswith('/') or 
            url.startswith('./') or 
            url.startswith('../') or
            url.startswith('#')):
            return True
        
        # Allow file paths
        return True
    
    def _process_text_formatting(self, content: str) -> str:
        """Process text formatting (bold, italic, etc.)"""
        
        # Bold: **text** or __text__
        # Italic: *text* or _text_
        # Code: `text`
        # Strikethrough: ~~text~~
        
        # This is handled by the engines typically
        return content
    
    def _process_lists(self, content: str) -> str:
        """Process markdown lists"""
        
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Bullet lists
            if stripped.startswith('- ') or stripped.startswith('* ') or stripped.startswith('+ '):
                # Preserve indentation for nested lists
                indent = len(line) - len(line.lstrip())
                processed_lines.append(line)
            
            # Numbered lists
            elif stripped and stripped[0].isdigit() and '. ' in stripped:
                processed_lines.append(line)
            
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def validate(self, content: str) -> bool:
        """Validate markdown syntax"""
        
        # Basic validation checks
        
        # Check for unmatched brackets
        if content.count('[') != content.count(']'):
            self._logger.warning("Unmatched square brackets")
        
        if content.count('(') != content.count(')'):
            self._logger.warning("Unmatched parentheses")
        
        # Check for proper header syntax
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                if not stripped[len(stripped.rstrip('#')):].strip():
                    self._logger.warning(f"Empty header at line {i}")
        
        return True
    
    def get_markdown_stats(self, content: str) -> Dict[str, Any]:
        """Get markdown statistics"""
        
        lines = content.split('\n')
        
        # Count headers
        headers = [line for line in lines if line.strip().startswith('#')]
        header_levels = {}
        for header in headers:
            level = len(header) - len(header.lstrip('#'))
            header_levels[level] = header_levels.get(level, 0) + 1
        
        # Count links
        import re
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        return {
            "total_lines": len(lines),
            "headers": len(headers),
            "header_levels": header_levels,
            "links": len(links),
            "paragraphs": len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        }
