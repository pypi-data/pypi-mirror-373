"""
Advanced LaTeX to Typst Math Converter
Converts LaTeX mathematical expressions to Typst syntax with comprehensive support
"""

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LaTeXToTypstMathConverter:
    """Advanced converter for LaTeX mathematical expressions to Typst syntax"""
    
    def __init__(self):
        self.setup_conversion_mappings()
    
    def setup_conversion_mappings(self):
        """Setup comprehensive LaTeX to Typst conversion mappings"""
        
        # Basic symbol mappings
        self.symbol_mappings = {
            # Greek letters
            r'\\alpha': 'α',
            r'\\beta': 'β', 
            r'\\gamma': 'γ',
            r'\\delta': 'δ',
            r'\\epsilon': 'ε',
            r'\\zeta': 'ζ',
            r'\\eta': 'η',
            r'\\theta': 'θ',
            r'\\iota': 'ι',
            r'\\kappa': 'κ',
            r'\\lambda': 'λ',
            r'\\mu': 'μ',
            r'\\nu': 'ν',
            r'\\xi': 'ξ',
            r'\\pi': 'π',
            r'\\rho': 'ρ',
            r'\\sigma': 'σ',
            r'\\tau': 'τ',
            r'\\upsilon': 'υ',
            r'\\phi': 'φ',
            r'\\chi': 'χ',
            r'\\psi': 'ψ',
            r'\\omega': 'ω',
            
            # Capital Greek letters
            r'\\Gamma': 'Γ',
            r'\\Delta': 'Δ',
            r'\\Theta': 'Θ',
            r'\\Lambda': 'Λ',
            r'\\Xi': 'Ξ',
            r'\\Pi': 'Π',
            r'\\Sigma': 'Σ',
            r'\\Upsilon': 'Υ',
            r'\\Phi': 'Φ',
            r'\\Psi': 'Ψ',
            r'\\Omega': 'Ω',
            
            # Mathematical operators
            r'\\infty': '∞',
            r'\\partial': '∂',
            r'\\nabla': '∇',
            r'\\hbar': 'ℏ',
            r'\\pm': '±',
            r'\\mp': '∓',
            r'\\times': '×',
            r'\\div': '÷',
            r'\\neq': '≠',
            r'\\leq': '≤',
            r'\\geq': '≥',
            r'\\ll': '≪',
            r'\\gg': '≫',
            r'\\approx': '≈',
            r'\\equiv': '≡',
            r'\\sim': '∼',
            r'\\propto': '∝',
            r'\\in': '∈',
            r'\\notin': '∉',
            r'\\subset': '⊂',
            r'\\supset': '⊃',
            r'\\subseteq': '⊆',
            r'\\supseteq': '⊇',
            r'\\cup': '∪',
            r'\\cap': '∩',
            r'\\vee': '∨',
            r'\\wedge': '∧',
            r'\\neg': '¬',
            r'\\exists': '∃',
            r'\\forall': '∀',
            r'\\emptyset': '∅',
            
            # Arrows
            r'\\rightarrow': '→',
            r'\\leftarrow': '←',
            r'\\leftrightarrow': '↔',
            r'\\Rightarrow': '⇒',
            r'\\Leftarrow': '⇐',
            r'\\Leftrightarrow': '⇔',
            
            # Special functions
            r'\\sin': 'sin',
            r'\\cos': 'cos',
            r'\\tan': 'tan',
            r'\\ln': 'ln',
            r'\\log': 'log',
            r'\\exp': 'exp',
            r'\\lim': 'lim',
            r'\\max': 'max',
            r'\\min': 'min',
            r'\\sup': 'sup',
            r'\\inf': 'inf',
        }
        
        # Complex function mappings that need special handling
        self.function_patterns = [
            # Integrals
            (r'\\int_{([^}]+)}^{([^}]+)}', r'∫_($1)^($2)'),
            (r'\\int_{([^}]+)}', r'∫_($1)'),
            (r'\\int\^{([^}]+)}', r'∫^($1)'),
            (r'\\int', '∫'),
            
            # Sums and products
            (r'\\sum_{([^}]+)}^{([^}]+)}', r'∑_($1)^($2)'),
            (r'\\sum_{([^}]+)}', r'∑_($1)'),
            (r'\\sum\^{([^}]+)}', r'∑^($1)'),
            (r'\\sum', '∑'),
            
            (r'\\prod_{([^}]+)}^{([^}]+)}', r'∏_($1)^($2)'),
            (r'\\prod_{([^}]+)}', r'∏_($1)'),
            (r'\\prod\^{([^}]+)}', r'∏^($1)'),
            (r'\\prod', '∏'),
            
            # Fractions
            (r'\\frac{([^}]+)}{([^}]+)}', r'($1)/($2)'),
            
            # Square roots
            (r'\\sqrt{([^}]+)}', r'sqrt($1)'),
            (r'\\sqrt\[([^\]]+)\]{([^}]+)}', r'root($1, $2)'),
            
            # Limits
            (r'\\lim_{([^}]+)}', r'lim_($1)'),
            
            # Subscripts and superscripts (improved handling)
            (r'([a-zA-Z0-9])_{([^}]+)}', r'$1_($2)'),
            (r'([a-zA-Z0-9])\^{([^}]+)}', r'$1^($2)'),
            
            # Matrix environments (basic support)
            (r'\\begin{bmatrix}(.*?)\\end{bmatrix}', self._convert_matrix),
            (r'\\begin{pmatrix}(.*?)\\end{pmatrix}', self._convert_matrix),
            (r'\\begin{matrix}(.*?)\\end{matrix}', self._convert_matrix),
        ]
    
    def _convert_matrix(self, match) -> str:
        """Convert LaTeX matrix to Typst syntax"""
        matrix_content = match.group(1).strip()
        
        # Split by rows (\\)
        rows = re.split(r'\\\\', matrix_content)
        converted_rows = []
        
        for row in rows:
            row = row.strip()
            if row:
                # Split by columns (&)
                cols = [col.strip() for col in row.split('&')]
                converted_row = ', '.join(cols)
                converted_rows.append(f"({converted_row})")
        
        return f"mat({'; '.join(converted_rows)})"
    
    def convert_latex_math(self, latex_content: str) -> str:
        """
        Convert LaTeX mathematical expressions to Typst syntax
        
        Args:
            latex_content: String containing LaTeX math expressions
            
        Returns:
            String with LaTeX math converted to Typst syntax
        """
        try:
            result = latex_content
            
            # Handle display math blocks ($$...$$ to $ ... $)
            result = re.sub(r'\$\$(.*?)\$\$', lambda m: f'$ {self._convert_math_expression(m.group(1))} $', result, flags=re.DOTALL)
            
            # Handle inline math blocks ($...$ - keep as is but convert content)
            result = re.sub(r'(?<!\$)\$([^$]+)\$(?!\$)', lambda m: f'${self._convert_math_expression(m.group(1))}$', result)
            
            logger.info("✅ LaTeX math conversion completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ LaTeX math conversion failed: {str(e)}")
            return latex_content  # Return original if conversion fails
    
    def _convert_math_expression(self, expression: str) -> str:
        """Convert a single mathematical expression from LaTeX to Typst"""
        result = expression.strip()
        
        # CRITICAL FIX: Handle matrix environments first before other conversions
        # Manually handle pmatrix (most common case)
        if '\\begin{pmatrix}' in result and '\\end{pmatrix}' in result:
            # Extract matrix content between begin and end
            matrix_match = re.search(r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}', result, re.DOTALL)
            if matrix_match:
                matrix_content = matrix_match.group(1).strip()
                
                # Convert LaTeX matrix to Typst matrix
                # Convert \\\\ to ; for row separators and & to , for column separators
                matrix_content = re.sub(r'\\\\', ';', matrix_content)
                matrix_content = re.sub(r'&', ',', matrix_content)
                matrix_content = matrix_content.replace(' ', ' ')  # Clean whitespace
                
                # Replace the entire matrix block with Typst syntax
                result = re.sub(r'\\begin\{pmatrix\}.*?\\end\{pmatrix\}', f'mat(delim: "(", {matrix_content})', result, flags=re.DOTALL)
                logger.info(f"✅ Converted pmatrix to: mat(delim: \"(\", {matrix_content})")
        
        # Apply symbol mappings
        for latex_symbol, typst_symbol in self.symbol_mappings.items():
            result = re.sub(latex_symbol, typst_symbol, result)
        
        # Apply function pattern mappings (integrals, sums, etc.)
        for pattern, replacement in self.function_patterns:
            if callable(replacement):
                # For complex conversions like matrices
                result = re.sub(pattern, replacement, result, flags=re.DOTALL)
            else:
                result = re.sub(pattern, replacement, result)
        
        # Handle remaining curly braces (convert {content} to (content) for grouping)
        result = self._handle_remaining_braces(result)
        
        # FINAL CLEANUP: Remove any remaining LaTeX artifacts
        result = re.sub(r'\\begin\{[^}]+\}', '', result)
        result = re.sub(r'\\end\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _handle_remaining_braces(self, expression: str) -> str:
        """Convert remaining LaTeX braces to Typst grouping"""
        # This is a simplified approach - for complex expressions, more sophisticated parsing is needed
        
        # Convert simple grouped expressions
        result = re.sub(r'\{([^{}]+)\}', r'(\1)', expression)
        
        # Handle nested braces (basic approach)
        depth = 0
        for _ in range(3):  # Handle up to 3 levels of nesting
            result = re.sub(r'\{([^{}]+)\}', r'(\1)', result)
        
        return result
    
    def validate_conversion(self, original: str, converted: str) -> bool:
        """
        Validate that the conversion was successful
        
        Args:
            original: Original LaTeX expression
            converted: Converted Typst expression
            
        Returns:
            True if conversion appears valid, False otherwise
        """
        try:
            # Basic validation checks
            
            # Check if we still have unconverted LaTeX commands
            remaining_latex = re.findall(r'\\[a-zA-Z]+', converted)
            if remaining_latex:
                logger.warning(f"⚠️ Unconverted LaTeX commands found: {remaining_latex}")
                return False
            
            # Check for unmatched braces
            open_braces = converted.count('{')
            close_braces = converted.count('}')
            if open_braces != close_braces:
                logger.warning(f"⚠️ Unmatched braces: {open_braces} open, {close_braces} close")
                return False
            
            # Check for unmatched parentheses
            open_parens = converted.count('(')
            close_parens = converted.count(')')
            if open_parens != close_parens:
                logger.warning(f"⚠️ Unmatched parentheses: {open_parens} open, {close_parens} close")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}")
            return False
    
    def get_conversion_stats(self, original: str, converted: str) -> Dict[str, int]:
        """Get statistics about the conversion"""
        return {
            'original_length': len(original),
            'converted_length': len(converted),
            'latex_commands_found': len(re.findall(r'\\[a-zA-Z]+', original)),
            'math_blocks_converted': len(re.findall(r'\$\$.*?\$\$', original, re.DOTALL)) + len(re.findall(r'(?<!\$)\$[^$]+\$(?!\$)', original)),
            'symbols_converted': len([sym for sym in self.symbol_mappings.keys() if sym in original])
        }

# Example usage and testing
if __name__ == "__main__":
    converter = LaTeXToTypstMathConverter()
    
    # Test cases
    test_expressions = [
        r"$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$",
        r"$$G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}$$",
        r"$$Z = \sum_{n=0}^{\infty} e^{-\beta\hbar\omega(n+\frac{1}{2})}$$",
        r"The energy is $E = mc^2$ where $c$ is the speed of light.",
        r"$$\mathcal{L} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi$$"
    ]
    
    for i, expr in enumerate(test_expressions, 1):
        print(f"\n=== Test {i} ===")
        print(f"Original: {expr}")
        converted = converter.convert_latex_math(expr)
        print(f"Converted: {converted}")
        valid = converter.validate_conversion(expr, converted)
        print(f"Valid: {valid}")
        stats = converter.get_conversion_stats(expr, converted)
        print(f"Stats: {stats}")
