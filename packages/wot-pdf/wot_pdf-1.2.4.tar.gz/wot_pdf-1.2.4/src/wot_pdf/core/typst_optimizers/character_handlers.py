#!/usr/bin/env python3
"""
🔧 CHARACTER HANDLERS - TYPST COMPATIBILITY LAYER
===============================================
⚡ Advanced character processing for Typst compilation
🔷 Handles special characters, Unicode, emojis, and encoding issues
📊 Ensures content compatibility with Typst rendering engine

FEATURES:
- Special character escaping for Typst syntax
- Unicode normalization and validation
- Emoji handling and replacement
- Mathematical symbol processing
- Advanced character encoding management

Extracted from typst_content_optimizer.py for better modularity.
"""

import re
import logging
import unicodedata
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class CharacterProcessingResult:
    """Result of character processing operation."""
    content: str
    replacements_made: int
    issues_found: List[str]
    processing_time: float


class TypstCharacterHandlers:
    """
    Advanced character processing for Typst compatibility.
    Handles special characters, Unicode, and encoding issues.
    """
    
    def __init__(self):
        """Initialize character handlers."""
        self.logger = logging.getLogger(__name__)
        
        # Typst-specific character mappings
        self.typst_escape_chars = {
            '\\': '\\\\',  # Backslash must be escaped
            '#': '\\#',    # Hash for Typst commands
            '$': '\\$',    # Dollar for math mode
            '@': '\\@',    # At for references
            '<': '\\<',    # Less than for markup
            '>': '\\>',    # Greater than for markup
            '[': '\\[',    # Left bracket for arrays
            ']': '\\]',    # Right bracket for arrays
            '{': '\\{',    # Left brace for blocks
            '}': '\\}',    # Right brace for blocks
        }
        
        # Safe characters that don't need escaping in most contexts
        self.safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \n\t.,!?;:-_()"\'')
        
        # Unicode categories to handle specially
        self.problematic_unicode_categories = [
            'Cc',  # Control characters
            'Cf',  # Format characters
            'Co',  # Private use
            'Cs',  # Surrogates
        ]
        
        # Emoji replacement patterns
        self.emoji_patterns = {
            '📊': '[CHART]',
            '📈': '[TREND-UP]',
            '📉': '[TREND-DOWN]',
            '✅': '[CHECK]',
            '❌': '[X]',
            '⚠️': '[WARNING]',
            '🔧': '[TOOL]',
            '🔷': '[DIAMOND]',
            '⚡': '[LIGHTNING]',
            '🎯': '[TARGET]',
            '📝': '[MEMO]',
            '💡': '[IDEA]',
        }
        
    def process_special_characters(self, content: str) -> str:
        """
        Process and escape special characters for Typst compatibility.
        
        Args:
            content: Raw text content
            
        Returns:
            Content with escaped special characters
        """
        processed = content
        
        # Apply character escaping
        for char, escaped in self.typst_escape_chars.items():
            processed = processed.replace(char, escaped)
        
        return processed
    
    def normalize_unicode(self, content: str) -> str:
        """
        Normalize Unicode characters for consistent processing.
        
        Args:
            content: Content with Unicode characters
            
        Returns:
            Normalized Unicode content
        """
        try:
            # Normalize to NFC (Canonical Decomposition followed by Canonical Composition)
            normalized = unicodedata.normalize('NFC', content)
            
            # Remove or replace problematic Unicode categories
            filtered_chars = []
            for char in normalized:
                category = unicodedata.category(char)
                if category in self.problematic_unicode_categories:
                    # Replace problematic characters with safe equivalents
                    if char.isspace():
                        filtered_chars.append(' ')  # Replace with regular space
                    else:
                        filtered_chars.append('?')  # Replace with question mark
                else:
                    filtered_chars.append(char)
            
            result = ''.join(filtered_chars)
            self.logger.debug(f"🔧 Normalized Unicode content ({len(content)} → {len(result)} chars)")
            return result
            
        except Exception as e:
            self.logger.warning(f"⚠️ Unicode normalization failed: {e}")
            return content  # Return original if normalization fails
    
    def handle_emoji_characters(self, content: str) -> str:
        """
        Handle emoji characters for Typst compatibility.
        
        Args:
            content: Content with emoji characters
            
        Returns:
            Content with processed emojis
        """
        processed = content
        replacements_made = 0
        
        # Apply emoji replacements
        for emoji, replacement in self.emoji_patterns.items():
            if emoji in processed:
                processed = processed.replace(emoji, replacement)
                replacements_made += 1
        
        # Handle remaining emojis with generic pattern
        emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|'  # Emoticons
            r'[\U0001F300-\U0001F5FF]|'  # Symbols & pictographs
            r'[\U0001F680-\U0001F6FF]|'  # Transport & map symbols
            r'[\U0001F1E0-\U0001F1FF]|'  # Regional indicators
            r'[\U00002702-\U000027B0]|'  # Dingbats
            r'[\U000024C2-\U0001F251]'   # Enclosed characters
        )
        
        def emoji_replacer(match):
            return f'[EMOJI:{ord(match.group(0)):04X}]'
        
        processed = emoji_pattern.sub(emoji_replacer, processed)
        
        if replacements_made > 0:
            self.logger.debug(f"🔧 Processed {replacements_made} emoji characters")
        
        return processed
    
    def process_mathematical_symbols(self, content: str) -> str:
        """
        Process mathematical symbols for Typst compatibility.
        
        Args:
            content: Content with mathematical symbols
            
        Returns:
            Content with processed mathematical symbols
        """
        # Mathematical symbol mappings for Typst
        math_replacements = {
            '±': '\\pm',
            '×': '\\times',
            '÷': '\\div',
            '∞': '\\infty',
            '∑': '\\sum',
            '∏': '\\prod',
            '∫': '\\int',
            '√': '\\sqrt',
            '∆': '\\Delta',
            '∇': '\\nabla',
            '∂': '\\partial',
            'α': '\\alpha',
            'β': '\\beta',
            'γ': '\\gamma',
            'δ': '\\delta',
            'ε': '\\epsilon',
            'θ': '\\theta',
            'λ': '\\lambda',
            'μ': '\\mu',
            'π': '\\pi',
            'σ': '\\sigma',
            'τ': '\\tau',
            'φ': '\\phi',
            'ψ': '\\psi',
            'ω': '\\omega',
        }
        
        processed = content
        for symbol, replacement in math_replacements.items():
            processed = processed.replace(symbol, replacement)
        
        return processed
    
    def handle_encoding_issues(self, content: str) -> str:
        """
        Handle common encoding issues in text content.
        
        Args:
            content: Content with potential encoding issues
            
        Returns:
            Content with resolved encoding issues
        """
        # Common encoding issue patterns and fixes
        encoding_fixes = [
            # Windows-1252 to UTF-8 common issues
            ('â€™', "'"),  # Right single quotation mark
            ('â€œ', '"'),  # Left double quotation mark
            ('â€', '"'),   # Right double quotation mark
            ('â€"', '—'),  # Em dash
            ('â€"', '–'),  # En dash
            ('Â ', ' '),   # Non-breaking space issues
            ('Ã©', 'é'),  # e with acute
            ('Ã¡', 'á'),  # a with acute
            ('Ã­', 'í'),  # i with acute
            ('Ã³', 'ó'),  # o with acute
            ('Ãº', 'ú'),  # u with acute
            ('Ã±', 'ñ'),  # n with tilde
        ]
        
        processed = content
        fixes_applied = 0
        
        for broken, fixed in encoding_fixes:
            if broken in processed:
                processed = processed.replace(broken, fixed)
                fixes_applied += 1
        
        if fixes_applied > 0:
            self.logger.debug(f"🔧 Applied {fixes_applied} encoding fixes")
        
        return processed
    
    def validate_character_safety(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate that content contains only Typst-safe characters.
        
        Args:
            content: Content to validate
            
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        issues = []
        
        # Check for problematic characters
        problematic_chars = []
        for char in content:
            if char not in self.safe_chars and ord(char) > 127:
                # High Unicode character - might be problematic
                category = unicodedata.category(char)
                if category in self.problematic_unicode_categories:
                    problematic_chars.append(f"'{char}' (U+{ord(char):04X}, {category})")
        
        if problematic_chars:
            issues.append(f"Problematic characters found: {', '.join(set(problematic_chars[:5]))}")
        
        # Check for unescaped Typst special characters
        unescaped = []
        for char in self.typst_escape_chars:
            if char in content and f"\\{char}" not in content:
                unescaped.append(char)
        
        if unescaped:
            issues.append(f"Unescaped Typst special characters: {', '.join(unescaped)}")
        
        return len(issues) == 0, issues
    
    def comprehensive_character_processing(self, content: str) -> CharacterProcessingResult:
        """
        Apply comprehensive character processing for Typst compatibility.
        
        Args:
            content: Raw content to process
            
        Returns:
            CharacterProcessingResult with processed content and metadata
        """
        import time
        start_time = time.time()
        
        original_length = len(content)
        processed_content = content
        total_replacements = 0
        issues_found = []
        
        # Step 1: Handle encoding issues
        processed_content = self.handle_encoding_issues(processed_content)
        
        # Step 2: Normalize Unicode
        processed_content = self.normalize_unicode(processed_content)
        
        # Step 3: Process mathematical symbols
        processed_content = self.process_mathematical_symbols(processed_content)
        
        # Step 4: Handle emojis
        processed_content = self.handle_emoji_characters(processed_content)
        
        # Step 5: Escape special characters
        processed_content = self.process_special_characters(processed_content)
        
        # Step 6: Validate safety
        is_safe, validation_issues = self.validate_character_safety(processed_content)
        if not is_safe:
            issues_found.extend(validation_issues)
        
        # Calculate processing metrics
        replacements_made = abs(len(processed_content) - original_length)
        processing_time = time.time() - start_time
        
        result = CharacterProcessingResult(
            content=processed_content,
            replacements_made=replacements_made,
            issues_found=issues_found,
            processing_time=processing_time
        )
        
        self.logger.info(f"🔧 Character processing complete: {original_length}→{len(processed_content)} chars in {processing_time:.3f}s")
        
        return result
    
    def get_character_statistics(self, content: str) -> Dict[str, Union[int, float, List[str]]]:
        """
        Get detailed statistics about character composition.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with character statistics
        """
        stats = {
            'total_characters': len(content),
            'ascii_characters': sum(1 for c in content if ord(c) < 128),
            'unicode_characters': sum(1 for c in content if ord(c) >= 128),
            'special_characters': sum(1 for c in content if c in self.typst_escape_chars),
            'emoji_characters': 0,
            'problematic_characters': [],
            'unicode_categories': {},
        }
        
        # Count emojis and analyze Unicode categories
        for char in content:
            # Check if emoji
            if any(emoji in char for emoji in self.emoji_patterns):
                stats['emoji_characters'] += 1
            
            # Analyze Unicode category
            category = unicodedata.category(char)
            stats['unicode_categories'][category] = stats['unicode_categories'].get(category, 0) + 1
            
            # Check for problematic characters
            if category in self.problematic_unicode_categories:
                stats['problematic_characters'].append(f"'{char}' (U+{ord(char):04X})")
        
        # Calculate ratios
        total = stats['total_characters']
        if total > 0:
            stats['ascii_ratio'] = stats['ascii_characters'] / total
            stats['unicode_ratio'] = stats['unicode_characters'] / total
        else:
            stats['ascii_ratio'] = 0.0
            stats['unicode_ratio'] = 0.0
        
        return stats
