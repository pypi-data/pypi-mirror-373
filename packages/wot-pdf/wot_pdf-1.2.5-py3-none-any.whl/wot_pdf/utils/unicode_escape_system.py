"""
Unicode Escape System for Typst Engine
Handles problematic characters that cause Typst compilation issues
"""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class UnicodeEscapeSystem:
    """
    Advanced Unicode character escape system for Typst compatibility
    Handles problematic characters that cause compilation errors
    """
    
    def __init__(self):
        self.setup_escape_mappings()
    
    def setup_escape_mappings(self):
        """Setup comprehensive character escape mappings"""
        
        # Characters that cause problems in Typst
        self.problematic_chars = {
            # Dollar signs (math mode triggers)
            '$': 'dollar',
            
            # Curly braces (grouping issues)
            '{': 'lbrace',
            '}': 'rbrace',
            
            # Backslashes (escape sequence issues)
            '\\': 'backslash',
            
            # Hash symbols (can conflict with Typst syntax)
            '#': 'hash',
            
            # Underscores in certain contexts (subscript issues)
            # Note: Only escape when not in code blocks
            
            # Caret symbols (superscript issues)
            '^': 'caret',
            
            # Pipe symbols (table formatting)
            '|': 'pipe',
            
            # Ampersand (potential issues)
            '&': 'ampersand',
            
            # Less than / Greater than (potential tag issues)
            '<': 'lt',
            '>': 'gt',
        }
        
        # Safe replacements for problematic characters
        self.safe_replacements = {
            '$': '\\$',          # Escape dollar sign
            '{': '\\{',          # Escape left brace
            '}': '\\}',          # Escape right brace  
            '#': '\\#',          # Escape hash
            '^': '\\^',          # Escape caret
            # Note: DON'T escape backslash here to avoid double escaping
            # '\\': '\\\\',        # Escape backslash - REMOVED to prevent double escaping
            '&': '\\&',          # Escape ampersand
            '<': '\\<',          # Escape less than
            '>': '\\>',          # Escape greater than
            '|': '\\|',          # Escape pipe
        }
        
        # Context-aware escape patterns
        self.context_patterns = [
            # Don't escape within code blocks
            (r'```[\s\S]*?```', 'code_block'),
            (r'`[^`]*?`', 'inline_code'),
            
            # Don't escape within math blocks  
            (r'\$\$[\s\S]*?\$\$', 'display_math'),
            # SELECTIVE inline math: protect expressions with equals signs (equations)
            (r'(?<!\$)\$(?!\$)[^$]*=[^$]*?\$(?!\$)', 'inline_math_with_equals'),
            # CRITICAL: Protect Typst math functions (mat, vec, etc.) from LaTeX conversion
            (r'(?<!\$)\$(?!\$)[^$]*(?:mat|vec|cases|frac|sqrt|sum|int|lim)\([^$]*?\$(?!\$)', 'typst_math_functions'),
            
            # Don't escape within URLs
            (r'https?://[^\s\)]+', 'url'),
            
            # Table context (preserve entire table row structure)
            # Match complete table rows: | content | content | content |
            (r'\|.*?\|.*?\|', 'table_row'),  # Multi-column tables
            (r'\|[^|\n]*\|(?:\s*\|[^|\n]*\|)*', 'table_full_row'),  # Complete table rows
        ]
    
    def escape_content(self, content: str) -> str:
        """
        Escape problematic Unicode characters for Typst compatibility
        
        Args:
            content: Raw content with potential problematic characters
            
        Returns:
            Content with escaped characters
        """
        try:
            # IMPROVED: Better double-escape protection
            # Only skip if content has MORE escaped dollars than raw dollars
            escaped_dollars = content.count('\\$')
            raw_dollars = content.count('$') - escaped_dollars  # Subtract escaped from total
            
            if escaped_dollars > 0 and raw_dollars == 0:
                logger.debug(f"🔄 Content appears fully escaped ({escaped_dollars} \\$ vs {raw_dollars} raw $), skipping re-escaping")
                return content
            # Store protected sections to avoid escaping them
            protected_sections = {}
            processed_content = content
            
            # Extract and protect code blocks, math, etc.
            for pattern, section_type in self.context_patterns:
                matches = list(re.finditer(pattern, processed_content, re.DOTALL))
                for i, match in enumerate(matches):
                    placeholder = f"__PROTECTED_{section_type.upper()}_{i}__"
                    protected_sections[placeholder] = match.group(0)
                    processed_content = processed_content.replace(match.group(0), placeholder, 1)
            
            # CRITICAL: Use smart dollar escape instead of direct replacement
            if '$' in processed_content:
                processed_content = self.smart_dollar_escape(processed_content)
            
            # Escape other problematic characters (excluding dollar signs)
            for char, replacement in self.safe_replacements.items():
                if char != '$':  # Skip dollar - already handled by smart_dollar_escape
                    processed_content = processed_content.replace(char, replacement)
            
            # Restore protected sections
            for placeholder, original_content in protected_sections.items():
                processed_content = processed_content.replace(placeholder, original_content)
            
            logger.info(f"✅ Unicode escape completed successfully")
            return processed_content
            
        except Exception as e:
            logger.error(f"❌ Unicode escape failed: {str(e)}")
            return content  # Return original if escaping fails
    
    def smart_dollar_escape(self, content: str) -> str:
        """
        Intelligently escape dollar signs while preserving math expressions
        """
        result = content
        
        # Pattern to match dollar signs NOT in math contexts
        # This is a simplified approach - more sophisticated parsing may be needed
        
        # First, protect existing math expressions
        math_blocks = []
        
        # Extract display math ($$...$$)
        display_math_pattern = r'\$\$(?:(?!\$\$)[\s\S])*\$\$'
        for match in re.finditer(display_math_pattern, result):
            placeholder = f"__MATH_BLOCK_{len(math_blocks)}__"
            math_blocks.append((placeholder, match.group(0)))
            result = result.replace(match.group(0), placeholder, 1)
        
        # Extract inline math ($...$) - but be more careful about business content
        # SUPER RESTRICTIVE: Only protect expressions with equals signs (actual math)
        inline_math_pattern = r'(?<!\$)\$(?!\$)[^$]*=[^$]*?\$(?!\$)'
        for match in re.finditer(inline_math_pattern, result):
            placeholder = f"__MATH_INLINE_{len(math_blocks)}__"
            math_blocks.append((placeholder, match.group(0)))
            result = result.replace(match.group(0), placeholder, 1)
        
        # CRITICAL FIX: Handle problematic dash-year combinations
        # Fix patterns like "$- 3-year" which cause Typst to interpret "year" as variable  
        # Pattern: number-year -> number-"year"
        result = re.sub(r'(\d+-)(year|month|day|week)', r'\1"\2"', result)
        
        # Now escape remaining dollar signs
        result = result.replace('$', '\\$')
        
        # Restore math expressions
        for placeholder, math_expr in math_blocks:
            result = result.replace(placeholder, math_expr)
        
        return result
    
    def fix_currency_symbols(self, content: str) -> str:
        """
        Specifically handle currency symbols that cause issues
        """
        # Currency symbols that need special handling
        currency_fixes = {
            # Standalone dollar signs (not math)
            r'\b\$(\d+(?:\.\d{2})?)\b': r'\\$\1',  # $100, $50.99
            r'\$\s*([A-Z]{3})\b': r'\\$ \1',        # $ USD, $ EUR
        }
        
        result = content
        for pattern, replacement in currency_fixes.items():
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def validate_escaping(self, original: str, escaped: str) -> bool:
        """
        Validate that escaping was done correctly
        
        Args:
            original: Original content
            escaped: Escaped content
            
        Returns:
            True if escaping appears valid
        """
        try:
            # Basic validation checks
            
            # Check that we haven't broken code blocks
            original_code_blocks = len(re.findall(r'```[\s\S]*?```', original))
            escaped_code_blocks = len(re.findall(r'```[\s\S]*?```', escaped))
            if original_code_blocks != escaped_code_blocks:
                logger.warning(f"⚠️ Code block count mismatch: {original_code_blocks} -> {escaped_code_blocks}")
                return False
            
            # Check that we haven't broken math expressions
            original_math = len(re.findall(r'\$\$[\s\S]*?\$\$', original))
            escaped_math = len(re.findall(r'\$\$[\s\S]*?\$\$', escaped))
            if original_math != escaped_math:
                logger.warning(f"⚠️ Math block count mismatch: {original_math} -> {escaped_math}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}")
            return False
    
    def get_escape_statistics(self, original: str, escaped: str) -> Dict[str, int]:
        """Get statistics about the escaping operation"""
        stats = {
            'original_length': len(original),
            'escaped_length': len(escaped),
            'characters_escaped': 0,
            'protected_sections': 0
        }
        
        # Count escaped characters
        for char in self.safe_replacements.keys():
            original_count = original.count(char)
            escaped_count = escaped.count(f'\\{char}')
            stats['characters_escaped'] += escaped_count
        
        # Count protected sections
        for pattern, _ in self.context_patterns:
            stats['protected_sections'] += len(re.findall(pattern, original))
        
        return stats

# Advanced contextual escape system
class ContextualEscapeProcessor:
    """
    Advanced processor that understands document context for better escaping
    """
    
    def __init__(self):
        self.escape_system = UnicodeEscapeSystem()
    
    def process_document_sections(self, content: str) -> str:
        """
        Process document with awareness of different sections (headers, code, text, etc.)
        """
        lines = content.split('\n')
        processed_lines = []
        current_context = 'text'
        
        for line in lines:
            line_context = self._detect_line_context(line, current_context)
            processed_line = self._process_line_by_context(line, line_context)
            processed_lines.append(processed_line)
            
            # Update context for next line
            current_context = self._update_context(current_context, line_context, line)
        
        return '\n'.join(processed_lines)
    
    def _detect_line_context(self, line: str, current_context: str) -> str:
        """Detect the context of current line"""
        line_stripped = line.strip()
        
        # Code block detection
        if line_stripped.startswith('```'):
            return 'code_block_delimiter'
        if current_context == 'code_block':
            return 'code_block'
        
        # Header detection
        if line_stripped.startswith('#'):
            return 'header'
        
        # List detection
        if re.match(r'^\s*[-*+]\s', line):
            return 'unordered_list'
        if re.match(r'^\s*\d+\.\s', line):
            return 'ordered_list'
        
        # Table detection
        if '|' in line_stripped and line_stripped.startswith('|'):
            return 'table'
        
        # Quote detection
        if line_stripped.startswith('>'):
            return 'quote'
        
        return 'text'
    
    def _process_line_by_context(self, line: str, context: str) -> str:
        """Process line based on its context"""
        if context in ['code_block', 'code_block_delimiter']:
            # Don't escape anything in code blocks
            return line
        elif context == 'header':
            # Special handling for headers
            return self._escape_header_line(line)
        elif context == 'table':
            # Preserve table structure while escaping content
            return self._escape_table_line(line)
        elif self._is_math_content(line):
            # CRITICAL: Don't escape LaTeX math expressions
            return line
        else:
            # Standard text escaping
            return self.escape_system.escape_content(line)
    
    def _is_math_content(self, line: str) -> bool:
        """Check if line contains LaTeX math expressions that should not be escaped"""
        # Check for display math $$...$$
        if '$$' in line:
            return True
        
        # Check for LaTeX commands (common ones that should not be escaped)
        latex_patterns = [
            r'\\begin\{',    # Matrix/environment starts
            r'\\end\{',      # Matrix/environment ends
            r'\\int[_^{]',   # Integrals
            r'\\sum[_^{]',   # Summations
            r'\\prod[_^{]',  # Products
            r'\\frac\{',     # Fractions
            r'\\sqrt\{',     # Square roots
            r'\\[a-zA-Z]+',  # General LaTeX commands (alpha, beta, etc.)
        ]
        
        for pattern in latex_patterns:
            if re.search(pattern, line):
                return True
                
        return False
    
    def _escape_header_line(self, line: str) -> str:
        """Special escaping for header lines"""
        # Split into markdown header symbols and text
        match = re.match(r'^(#{1,6}\s*)(.*)', line)
        if match:
            header_symbols = match.group(1)
            header_text = match.group(2)
            # Escape the text part but preserve header markdown
            escaped_text = self.escape_system.escape_content(header_text)
            return header_symbols + escaped_text
        return line
    
    def _escape_table_line(self, line: str) -> str:
        """Special escaping for table lines while preserving structure"""
        if '|' not in line:
            return line
        
        # Process table content: escape each cell individually while preserving table structure
        parts = line.split('|')
        escaped_parts = []
        
        for i, part in enumerate(parts):
            if i == 0 and part.strip() == '':
                # First empty part (line starts with |)
                escaped_parts.append(part)
            elif i == len(parts) - 1 and part.strip() == '':
                # Last empty part (line ends with |)
                escaped_parts.append(part)
            else:
                # CRITICAL FIX: Special handling for bold text in table cells
                # **TOTAL** becomes empty ** blocks, so we need special handling
                escaped_part = part
                
                # First escape dollars in this cell, but handle bold specially
                if '**' in escaped_part and '$' in escaped_part:
                    # Handle pattern like **360000$** properly
                    # Replace **<content-with-dollar>** pattern
                    escaped_part = re.sub(r'\*\*([^*]*\$[^*]*)\*\*', lambda m: f'**{m.group(1).replace("$", "\\$")}**', escaped_part)
                else:
                    # Regular escaping for non-bold cells
                    escaped_part = self.escape_system.escape_content(escaped_part)
                    
                escaped_parts.append(escaped_part)
        
        return '|'.join(escaped_parts)
    
    def _update_context(self, current_context: str, line_context: str, line: str) -> str:
        """Update context based on current line"""
        if line_context == 'code_block_delimiter':
            if current_context == 'code_block':
                return 'text'  # End of code block
            else:
                return 'code_block'  # Start of code block
        elif current_context == 'code_block':
            return 'code_block'  # Continue in code block
        else:
            return 'text'  # Default to text context

# Example usage
if __name__ == "__main__":
    escape_system = UnicodeEscapeSystem()
    contextual_processor = ContextualEscapeProcessor()
    
    # Test cases
    test_content = """
# Test Document with $ Symbols

This costs $50 and €30.

```python
price = $100  # This should not be escaped
```

| Product | Price | Currency |
|---------|-------|----------|
| Item 1  | $50   | USD      |
| Item 2  | €30   | EUR      |

Math: $E = mc^2$ and $$\int_{0}^{\infty} x dx$$
"""
    
    print("=== Original ===")
    print(test_content)
    
    print("\n=== Basic Escaping ===")
    escaped_basic = escape_system.escape_content(test_content)
    print(escaped_basic)
    
    print("\n=== Contextual Escaping ===")
    escaped_contextual = contextual_processor.process_document_sections(test_content)
    print(escaped_contextual)
    
    print("\n=== Statistics ===")
    stats = escape_system.get_escape_statistics(test_content, escaped_basic)
    print(f"Stats: {stats}")
    
    validation = escape_system.validate_escaping(test_content, escaped_basic)
    print(f"Valid: {validation}")
