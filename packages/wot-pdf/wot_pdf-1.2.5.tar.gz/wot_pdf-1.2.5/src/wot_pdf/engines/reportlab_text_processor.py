#!/usr/bin/env python3
"""
🔤 REPORTLAB TEXT PROCESSOR - CONTENT CLEANING
==============================================
⚡ Advanced text processing for ReportLab PDF generation
🔷 Unicode handling, emoji processing, and content sanitization  
📊 XML-safe text preparation with inline formatting support

Extracted from enhanced_reportlab_engine.py for better modularity.
"""

import unicodedata
import re
import logging
from typing import Dict, Any, Optional, List, Tuple


class ReportLabTextProcessor:
    """
    Advanced text processing for ReportLab PDF generation.
    Handles Unicode, emoji, XML safety, and inline formatting.
    """
    
    # Emoji replacement mappings
    EMOJI_REPLACEMENTS = {
        '🚀': '[ROCKET]',
        '✅': '[CHECK]', 
        '❌': '[CROSS]',
        '⚡': '[LIGHTNING]',
        '🔷': '[DIAMOND]',
        '📊': '[CHART]',
        '🎯': '[TARGET]',
        '🔧': '[WRENCH]',
        '🛠': '[TOOLS]',
        '📝': '[MEMO]',
        '💡': '[BULB]',
        '🔍': '[MAGNIFIER]',
        '⚠️': '[WARNING]',
        '🎨': '[PALETTE]',
        '🔄': '[REFRESH]',
        '📈': '[TRENDING_UP]',
        '🎪': '[CIRCUS]',
        '🏆': '[TROPHY]',
        '🌟': '[STAR]',
        '🔥': '[FIRE]',
        '💪': '[MUSCLE]',
        '🧠': '[BRAIN]',
        '💰': '[MONEY]',
        '🎉': '[PARTY]',
        '🚨': '[SIREN]',
        '🎭': '[THEATER]',
        '🔒': '[LOCK]',
        '🗝️': '[KEY]',
        '📚': '[BOOKS]',
        '🌈': '[RAINBOW]',
        '⭐': '[STAR2]',
        '💎': '[GEM]',
        '🎪': '[CIRCUS]'
    }

    def __init__(self):
        """Initialize text processor."""
        self.logger = logging.getLogger(__name__)

    def validate_xml_tags(self, text: str) -> bool:
        """
        Validate that XML tags in text are properly formed.
        Returns True if valid, False if invalid.
        """
        try:
            # Basic XML validation - check for matching tags
            open_tags = re.findall(r'<(\w+)[^>]*>', text)
            close_tags = re.findall(r'</(\w+)>', text)
            
            # Check self-closing tags
            self_closing = re.findall(r'<(\w+)[^>]*/>|<(br|img|hr)\s*>', text)
            self_closing_names = [tag for tag_tuple in self_closing for tag in tag_tuple if tag]
            
            # Remove self-closing tags from open tags count
            for tag in self_closing_names:
                if tag in open_tags:
                    open_tags.remove(tag)
            
            # Simple check - same number of opening and closing tags
            return len(open_tags) == len(close_tags)
            
        except Exception as e:
            self.logger.warning(f"XML validation failed: {e}")
            return False

    def clean_code_for_xml(self, code: str) -> str:
        """
        Clean code content to be XML-safe while preserving readability.
        Handles special characters and operators safely.
        """
        if not code.strip():
            return code
            
        try:
            # Handle Python string operators that cause XML issues
            code = self._fix_python_string_operators(code)
            
            # Basic XML escaping
            replacements = {
                '&': '&amp;',
                '<': '&lt;', 
                '>': '&gt;',
                '"': '&quot;',
                "'": '&apos;'
            }
            
            for char, replacement in replacements.items():
                code = code.replace(char, replacement)
                
            return code
            
        except Exception as e:
            self.logger.warning(f"Code cleaning failed: {e}")
            return code

    def make_safe_text(self, text: str) -> str:
        """
        Make text completely safe for XML/ReportLab processing.
        More aggressive cleaning than gentle_safe_text.
        """
        if not text:
            return ""
            
        try:
            # Remove problematic characters
            text = re.sub(r'[^\w\s\-.,!?():;/\\@#$%^&*+=\[\]{}|~`"\']', ' ', text)
            
            # Handle XML entities
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;') 
            text = text.replace('"', '&quot;')
            
            # Clean up multiple spaces
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Text safety processing failed: {e}")
            return str(text) if text else ""

    def gentle_clean_text(self, text: str) -> str:
        """
        Gently clean text while preserving HTML formatting tags.
        Only escapes dangerous characters outside of HTML tags.
        """
        if not text:
            return ""
            
        try:
            # First escape ampersands that aren't part of HTML entities
            import re
            # Preserve existing HTML entities, but escape standalone &
            text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', text)
            
            # Don't escape < and > that are part of HTML tags
            # This preserves <b>, <i>, <font>, etc. while escaping standalone < >
            # We'll only escape < > that aren't part of valid HTML tag structure
            
            # For now, let's be conservative and NOT escape < > at all
            # since ReportLab should handle HTML tags correctly
            
            # Preserve quotes but make them XML-safe if needed
            if '"' in text and ('<font' in text or 'color=' in text):
                # Only escape quotes that are inside HTML attributes
                text = re.sub(r'"([^"]*)"', r'&quot;\1&quot;', text)
                
            return text.strip()
            
        except Exception as e:
            self.logger.warning(f"Gentle text processing failed: {e}")
            # Fallback: return original text
            return text

    def process_inline_formatting(self, text: str) -> str:
        """
        Process inline Markdown formatting for ReportLab.
        Converts **bold**, *italic*, `code` to XML tags.
        """
        if not text:
            return ""

        def replace_inline_code(match):
            code_content = match.group(1)
            # Clean the code content  
            cleaned_code = self.clean_code_for_xml(code_content)
            # Use standard ReportLab monospace font - Times-Roman as fallback
            return f'<font name="Times-Roman" color="#B03A2E">{cleaned_code}</font>'

        try:
            # Handle inline code first (to avoid conflicts)
            text = re.sub(r'`([^`]+)`', replace_inline_code, text)
            
            # Bold text
            text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
            
            # Italic text  
            text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
            
            # Handle remaining backticks as code
            text = text.replace('`', '"')
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Inline formatting processing failed: {e}")
            return text

    def clean_unicode_content(self, content: str) -> str:
        """
        Clean Unicode content for ReportLab compatibility.
        Handles special characters and normalization.
        """
        if not content:
            return ""
            
        try:
            # Normalize Unicode (NFC form)
            content = unicodedata.normalize('NFC', content)
            
            # Remove or replace problematic Unicode characters
            # Keep most common extended ASCII and Unicode
            cleaned = ""
            for char in content:
                # Get Unicode category
                category = unicodedata.category(char)
                
                # Keep letters, numbers, punctuation, symbols, separators
                if category.startswith(('L', 'N', 'P', 'S', 'Z')):
                    # But exclude some problematic control characters
                    if ord(char) < 32 and char not in '\n\r\t':
                        cleaned += ' '  # Replace control chars with space
                    else:
                        cleaned += char
                else:
                    cleaned += ' '  # Replace other categories with space
                    
            # Clean up multiple spaces
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            return cleaned
            
        except Exception as e:
            self.logger.warning(f"Unicode cleaning failed: {e}")
            return content

    def handle_emoji_content(self, content: str) -> str:
        """
        Handle emoji characters in content by replacing with text equivalents.
        Returns content with emoji replaced by descriptive text.
        """
        if not content:
            return ""
            
        try:
            # Replace known emoji with text equivalents
            processed_content = content
            for emoji, replacement in self.EMOJI_REPLACEMENTS.items():
                processed_content = processed_content.replace(emoji, replacement)
            
            # Handle any remaining emoji-like characters
            # This is a broad approach - replace high Unicode ranges often used for emoji
            def replace_high_unicode(match):
                char = match.group(0)
                # Try to get a name for the character
                try:
                    name = unicodedata.name(char, '').replace('_', ' ')
                    return f'[{name}]' if name else '[EMOJI]'
                except ValueError:
                    return '[EMOJI]'
            
            # Replace characters in common emoji ranges
            emoji_ranges = [
                (0x1F600, 0x1F64F),  # Emoticons
                (0x1F300, 0x1F5FF),  # Miscellaneous Symbols
                (0x1F680, 0x1F6FF),  # Transport and Map
                (0x1F700, 0x1F77F),  # Alchemical Symbols
                (0x1F900, 0x1F9FF),  # Supplemental Symbols
                (0x2600, 0x26FF),    # Miscellaneous Symbols
                (0x2700, 0x27BF),    # Dingbats
            ]
            
            for start, end in emoji_ranges:
                pattern = ''.join(chr(i) for i in range(start, min(end + 1, 0x110000)) 
                                if i <= 0x10FFFF)
                if pattern:
                    processed_content = re.sub(f'[{re.escape(pattern)}]', 
                                             replace_high_unicode, processed_content)
            
            return processed_content
            
        except Exception as e:
            self.logger.warning(f"Emoji processing failed: {e}")
            return content

    def _fix_python_string_operators(self, code_text: str) -> str:
        """
        Fix Python string operators that cause XML parsing issues.
        Specifically handles f-strings and string operations.
        """
        try:
            # Handle f-string expressions that might contain < > operators
            # This is a simplified approach - more complex f-strings might need better parsing
            code_text = re.sub(r'f"([^"]*)"', r'f&quot;\1&quot;', code_text)
            code_text = re.sub(r"f'([^']*)'", r"f&apos;\1&apos;", code_text)
            
            return code_text
            
        except Exception as e:
            self.logger.warning(f"Python string operator fixing failed: {e}")
            return code_text

    def process_full_content(self, content: str, 
                           handle_emoji: bool = True,
                           clean_unicode: bool = True, 
                           process_formatting: bool = True) -> str:
        """
        Process content through complete cleaning pipeline.
        
        Args:
            content: Raw content to process
            handle_emoji: Whether to replace emoji with text
            clean_unicode: Whether to normalize and clean Unicode
            process_formatting: Whether to process inline formatting
            
        Returns:
            Fully processed content safe for ReportLab
        """
        if not content:
            return ""
            
        try:
            processed = content
            
            # Step 1: Handle emoji if requested
            if handle_emoji:
                processed = self.handle_emoji_content(processed)
                
            # Step 2: Clean Unicode if requested  
            if clean_unicode:
                processed = self.clean_unicode_content(processed)
                
            # Step 3: Process inline formatting if requested
            if process_formatting:
                processed = self.process_inline_formatting(processed)
                
            # Step 4: Final safety pass
            processed = self.gentle_clean_text(processed)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Full content processing failed: {e}")
            # Fallback to basic safety
            return self.make_safe_text(content)
