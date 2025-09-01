#!/usr/bin/env python3
"""
🔧 TYPST SYNTAX GENERATOR
========================
⚡ Clean Typst syntax generation without escaping conflicts
🎯 Native syntax generation for optimal Typst compatibility

Provides utilities for generating clean Typst syntax elements.
"""

import re
from typing import Optional


class TypstSyntaxGenerator:
    """Clean Typst syntax generation without escaping conflicts."""

    @staticmethod
    def escape_text_content(text: str) -> str:
        """Minimal escaping for text content."""
        # Only escape if absolutely necessary
        if '#' in text and not text.strip().startswith('#'):
            # Only escape standalone # that aren't part of Typst commands
            text = re.sub(r'(?<!\\)#(?![a-zA-Z\[\{])', r'\\#', text)
        return text

    @staticmethod
    def generate_header(text: str, level: int) -> str:
        """Generate Typst header syntax."""
        prefix = '=' * level
        return f"{prefix} {text.strip()}"

    @staticmethod
    def generate_link(url: str, text: str) -> str:
        """Generate Typst link syntax."""
        if text and text.strip():
            return f'link("{url}")[{text}]'
        else:
            return f'link("{url}")'

    @staticmethod
    def generate_raw_block(content: str, lang: Optional[str] = None) -> str:
        """Generate raw code block for Typst."""
        if lang:
            return f"```{lang}\n{content}\n```"
        else:
            # Use raw directive for unspecified language
            return f"#raw[\n{content}\n]"

    @staticmethod
    def generate_inline_code(content: str) -> str:
        """Generate inline code for Typst."""
        # Use backticks for simple inline code
        return f"`{content}`"

    @staticmethod
    def generate_citation(citation_key: str) -> str:
        """Generate Typst citation syntax."""
        clean_key = citation_key.replace('[', '').replace(']', '')
        return f"@{clean_key}"

    @staticmethod
    def escape_citation_brackets(content: str) -> str:
        """Escape citation brackets that aren't actual citations."""
        # Pattern to find [text] that isn't preceded by text that looks like a citation
        pattern = r'(?<![@\w])\[([^\]]+)\](?!\()'
        return re.sub(pattern, r'\\[\1\\]', content)

    @staticmethod
    def generate_emphasis(text: str, style: str = 'italic') -> str:
        """Generate emphasis markup."""
        if style == 'bold':
            return f"*{text}*"
        elif style == 'italic':
            return f"_{text}_"
        else:
            return text

    @staticmethod
    def generate_list_item(text: str, ordered: bool = False, level: int = 0) -> str:
        """Generate list item syntax."""
        indent = "  " * level
        if ordered:
            return f"{indent}+ {text}"
        else:
            return f"{indent}- {text}"

    @staticmethod
    def generate_table_separator() -> str:
        """Generate table separator for Typst."""
        return "table.hline()"

    @staticmethod
    def escape_special_chars(text: str) -> str:
        """Escape special characters for Typst."""
        # Minimal escaping - only what's absolutely necessary
        replacements = {
            '\\': '\\\\',  # Backslashes need escaping
            '"': '\\"',    # Quotes in strings need escaping
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
