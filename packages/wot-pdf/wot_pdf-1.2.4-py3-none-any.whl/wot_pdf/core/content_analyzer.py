"""
WOT-PDF Content Analyzer
Analyzes and processes Markdown content for optimization
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
import logging
import re


@dataclass
class ContentAnalysisResults:
    """Results of content analysis"""
    complexity_score: float
    code_block_count: int
    programming_languages: Set[str]
    special_char_density: float
    estimated_pages: int = 0
    has_mathematical_content: bool = False


class ContentAnalyzer:
    """Analyzes Markdown content for PDF generation optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, content: str) -> ContentAnalysisResults:
        """Analyze content and return ContentAnalysisResults"""
        analysis = self.analyze_content(content)
        
        # Extract programming languages from code blocks
        languages = set()
        for block in analysis['code_blocks']:
            if block.get('language'):
                languages.add(block['language'])
        
        # Calculate special character density
        special_chars = len(re.findall(r'[^\w\s]', content))
        special_char_density = (special_chars / len(content)) * 100 if len(content) > 0 else 0
        
        return ContentAnalysisResults(
            complexity_score=analysis['complexity'],
            code_block_count=len(analysis['code_blocks']),
            programming_languages=languages,
            special_char_density=special_char_density,
            estimated_pages=analysis['estimated_pages'],
            has_mathematical_content=analysis['has_mathematical_content']
        )
        
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze Markdown content and return structure information"""
        analysis = {
            'total_length': len(content),
            'line_count': len(content.split('\n')),
            'headers': self._extract_headers(content),
            'code_blocks': self._extract_code_blocks(content),
            'tables': self._extract_tables(content),
            'links': self._extract_links(content),
            'images': self._extract_images(content),
            'complexity': self._calculate_complexity(content),
            'estimated_pages': self._estimate_pages(content),
            'has_mathematical_content': self._has_math_content(content),
            'formatting_elements': self._count_formatting(content)
        }
        
        self.logger.debug(f"Content analysis completed: {analysis['complexity']} complexity, {analysis['estimated_pages']} pages")
        return analysis
    
    def _extract_headers(self, content: str) -> List[Dict[str, Any]]:
        """Extract header information"""
        headers = []
        header_pattern = r'^(#{1,6})\s+(.+)$'
        
        for i, line in enumerate(content.split('\n'), 1):
            match = re.match(header_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2)
                headers.append({
                    'level': level,
                    'text': text,
                    'line': i
                })
        
        return headers
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Extract code blocks"""
        code_blocks = []
        
        # Fenced code blocks
        fenced_pattern = r'```(\w+)?\n(.*?)\n```'
        for match in re.finditer(fenced_pattern, content, re.MULTILINE | re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2)
            code_blocks.append({
                'type': 'fenced',
                'language': language,
                'content': code,
                'lines': len(code.split('\n'))
            })
        
        # Inline code
        inline_pattern = r'`([^`]+)`'
        inline_count = len(re.findall(inline_pattern, content))
        if inline_count > 0:
            code_blocks.append({
                'type': 'inline',
                'count': inline_count
            })
        
        return code_blocks
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract table information"""
        tables = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|[\s\-:|]+\|\s*$', lines[i + 1]):
                # Found a table
                rows = 1
                cols = len([cell for cell in line.split('|') if cell.strip()])
                
                # Count additional rows
                for j in range(i + 2, len(lines)):
                    if '|' in lines[j]:
                        rows += 1
                    else:
                        break
                
                tables.append({
                    'rows': rows,
                    'columns': cols,
                    'line_start': i + 1
                })
        
        return tables
    
    def _extract_links(self, content: str) -> List[Dict[str, Any]]:
        """Extract links"""
        links = []
        
        # Markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            links.append({
                'text': match.group(1),
                'url': match.group(2),
                'type': 'markdown'
            })
        
        # Direct URLs
        url_pattern = r'https?://[^\s)]+'
        for match in re.finditer(url_pattern, content):
            links.append({
                'url': match.group(0),
                'type': 'direct'
            })
        
        return links
    
    def _extract_images(self, content: str) -> List[Dict[str, Any]]:
        """Extract images"""
        images = []
        
        # Markdown images ![alt](src)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(image_pattern, content):
            images.append({
                'alt': match.group(1),
                'src': match.group(2),
                'type': 'markdown'
            })
        
        return images
    
    def _calculate_complexity(self, content: str) -> str:
        """Calculate content complexity"""
        score = 0
        
        # Basic length score
        score += min(len(content) // 1000, 10)
        
        # Headers add complexity
        headers = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        score += min(headers, 5)
        
        # Code blocks add complexity
        code_blocks = len(re.findall(r'```', content)) // 2
        score += code_blocks * 2
        
        # Tables add complexity
        tables = len(re.findall(r'\|.*\|', content))
        if tables > 0:
            score += min(tables // 3, 5)
        
        # Mathematical content adds complexity
        if self._has_math_content(content):
            score += 3
        
        # Complex formatting
        formatting_score = (
            len(re.findall(r'\*\*.*?\*\*', content)) +  # Bold
            len(re.findall(r'\*.*?\*', content)) +      # Italic
            len(re.findall(r'`.*?`', content))          # Code
        )
        score += min(formatting_score // 10, 3)
        
        if score <= 3:
            return "simple"
        elif score <= 7:
            return "medium"
        elif score <= 12:
            return "complex"
        else:
            return "very_complex"
    
    def _estimate_pages(self, content: str) -> int:
        """Estimate number of pages"""
        # Rough estimation: 500 words per page
        words = len(content.split())
        
        # Adjust for code blocks (take more space)
        code_blocks = len(re.findall(r'```.*?```', content, re.DOTALL))
        code_penalty = code_blocks * 0.5
        
        # Adjust for tables (take more space)
        tables = len(re.findall(r'\|.*\|', content))
        table_penalty = (tables // 3) * 0.3 if tables > 0 else 0
        
        estimated_pages = max(1, int((words / 500) + code_penalty + table_penalty))
        return min(estimated_pages, 50)  # Cap at 50 pages
    
    def _has_math_content(self, content: str) -> bool:
        """Check if content has mathematical expressions"""
        math_patterns = [
            r'\$.*?\$',  # Inline math
            r'\$\$.*?\$\$',  # Display math
            r'\\begin\{equation\}',  # LaTeX equations
            r'\\frac\{',  # Fractions
            r'\\sum',  # Summations
            r'\\int',  # Integrals
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, content, re.DOTALL):
                return True
        
        return False
    
    def _count_formatting(self, content: str) -> Dict[str, int]:
        """Count formatting elements"""
        return {
            'bold': len(re.findall(r'\*\*.*?\*\*', content)),
            'italic': len(re.findall(r'(?<!\*)\*(?!\*).*?\*(?!\*)', content)),
            'code_inline': len(re.findall(r'`[^`]+`', content)),
            'strikethrough': len(re.findall(r'~~.*?~~', content)),
            'lists': len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)),
            'numbered_lists': len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE)),
            'blockquotes': len(re.findall(r'^>\s+', content, re.MULTILINE))
        }


class ContentOptimizer:
    """Optimizes content for specific PDF engines"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzer = ContentAnalyzer()
    
    def optimize_for_typst(self, content: str) -> str:
        """Optimize content for Typst engine"""
        self.logger.debug("Optimizing content for Typst engine")
        
        # Analyze content first
        analysis = self.analyzer.analyze_content(content)
        
        # Apply Typst-specific optimizations
        optimized = content
        
        # Fix common Typst issues
        if analysis['has_mathematical_content']:
            # Ensure math expressions are properly formatted for Typst
            optimized = self._optimize_math_for_typst(optimized)
        
        if analysis['code_blocks']:
            # Optimize code blocks for Typst
            optimized = self._optimize_code_for_typst(optimized)
        
        if analysis['tables']:
            # Optimize tables for Typst
            optimized = self._optimize_tables_for_typst(optimized)
        
        return optimized
    
    def optimize_for_reportlab(self, content: str) -> str:
        """Optimize content for ReportLab engine"""
        self.logger.debug("Optimizing content for ReportLab engine")
        
        # ReportLab is more tolerant, minimal optimization needed
        return content
    
    def _optimize_math_for_typst(self, content: str) -> str:
        """Optimize mathematical content for Typst"""
        # Convert LaTeX-style math to Typst format
        # This is a simplified conversion
        optimized = content
        
        # Convert inline math
        optimized = re.sub(r'\$([^$]+)\$', r'$ \1 $', optimized)
        
        return optimized
    
    def _optimize_code_for_typst(self, content: str) -> str:
        """Optimize code blocks for Typst"""
        # Ensure code blocks have proper language tags
        return content
    
    def _optimize_tables_for_typst(self, content: str) -> str:
        """Optimize tables for Typst"""
        # Ensure tables are properly formatted
        return content


# Global instances for easy access
content_analyzer = ContentAnalyzer()
content_optimizer = ContentOptimizer()
