"""
Enhanced Typst Engine Adapter
Proper Markdown to Typst conversion
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import subprocess
import tempfile
import os

class EnhancedTypstAdapter:
    """Enhanced Typst engine adapter with proper Markdown conversion"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self._name = "typst_enhanced"
        
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize Typst adapter"""
        try:
            # Check if typst is available
            result = subprocess.run(['typst', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self._is_initialized = True
                self.logger.info(f"✅ Typst available: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
            
        self.logger.warning("⚠️ Typst CLI not found")
        return False
        
    @property
    def is_available(self) -> bool:
        """Check if Typst is available"""
        return self._is_initialized
        
    def generate_pdf(self, content: str, output_path: Path, template: str = "technical", **kwargs) -> Dict[str, Any]:
        """Generate PDF with Typst"""
        if not self._is_initialized:
            raise RuntimeError("Typst adapter not initialized")
            
        try:
            # Create temporary typst file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False, encoding='utf-8') as f:
                # Convert markdown to proper typst
                typst_content = self._markdown_to_typst(content, template)
                f.write(typst_content)
                temp_typst = f.name
                
            self.logger.info(f"📝 Typst file created: {temp_typst}")
            
            # Compile with typst
            result = subprocess.run([
                'typst', 'compile', temp_typst, str(output_path)
            ], capture_output=True, text=True)
            
            # Cleanup
            os.unlink(temp_typst)
            
            if result.returncode == 0:
                file_size = output_path.stat().st_size if output_path.exists() else 0
                return {
                    'success': True,
                    'engine': self._name,
                    'output_file': str(output_path),
                    'template': template,
                    'file_size': file_size,
                    'typst_output': result.stdout
                }
            else:
                raise RuntimeError(f"Typst compilation failed: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"❌ Typst generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'engine': self._name
            }
            
    def _markdown_to_typst(self, markdown: str, template: str = "technical") -> str:
        """Convert markdown to proper typst with template"""
        # Start with template header
        typst_content = self._get_template_header(template)
        
        lines = markdown.strip().split('\n')
        typst_lines = []
        in_code_block = False
        code_lang = ""
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Start code block
                    code_lang = line.strip()[3:].strip()
                    if code_lang:
                        typst_lines.append(f"```{code_lang}")
                    else:
                        typst_lines.append("```")
                    in_code_block = True
                else:
                    # End code block
                    typst_lines.append("```")
                    in_code_block = False
                    code_lang = ""
                continue
                
            # Inside code block - keep as is
            if in_code_block:
                typst_lines.append(line)
                continue
                
            # Convert headers
            if line.startswith('# '):
                typst_lines.append(f"= {line[2:].strip()}")
            elif line.startswith('## '):
                typst_lines.append(f"== {line[3:].strip()}")
            elif line.startswith('### '):
                typst_lines.append(f"=== {line[4:].strip()}")
            elif line.startswith('#### '):
                typst_lines.append(f"==== {line[5:].strip()}")
            # Convert lists
            elif line.strip().startswith('- '):
                content = line.strip()[2:].strip()
                # Convert markdown formatting in list items
                content = self._convert_inline_formatting(content)
                typst_lines.append(f"- {content}")
            # Convert numbered lists
            elif line.strip() and len(line.strip()) > 2 and line.strip()[0].isdigit() and '. ' in line:
                parts = line.strip().split('. ', 1)
                if len(parts) == 2:
                    content = self._convert_inline_formatting(parts[1])
                    typst_lines.append(f"+ {content}")
                else:
                    typst_lines.append(line)
            # Regular paragraphs
            elif line.strip():
                converted_line = self._convert_inline_formatting(line)
                typst_lines.append(converted_line)
            else:
                typst_lines.append("")
                
        return typst_content + '\n'.join(typst_lines)
        
    def _convert_inline_formatting(self, text: str) -> str:
        """Convert inline markdown formatting to typst"""
        # Convert bold **text** to *text*
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
        
        # Convert italic *text* to _text_
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'_\1_', text)
        
        # Convert inline code `code` - keep as is
        # text = re.sub(r'`([^`]+?)`', r'`\1`', text)
        
        return text
        
    def _get_template_header(self, template: str) -> str:
        """Get template-specific header"""
        headers = {
            "technical": '''#set document(title: "Technical Document", author: "WOT-PDF")
#set page(numbering: "1")
#set heading(numbering: "1.1.1")
#set text(font: "New Computer Modern", size: 11pt)
#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1em)
  #it
  #v(0.5em)
]

''',
            "academic": '''#set document(title: "Academic Paper", author: "WOT-PDF")
#set page(numbering: "1", margin: 2.5cm)
#set heading(numbering: "1.1")
#set text(font: "Linux Libertine", size: 12pt)
#set par(justify: true, leading: 0.6em)

''',
            "minimal": '''#set document(title: "Document", author: "WOT-PDF")
#set page(numbering: "1")
#set text(size: 11pt)

''',
            "corporate": '''#set document(title: "Corporate Document", author: "WOT-PDF")
#set page(numbering: "1", header: [Corporate Document])
#set heading(numbering: "1.1")
#set text(font: "Inter", size: 11pt)

'''
        }
        
        return headers.get(template, headers["technical"])
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities"""
        return {
            'formats': ['pdf'],
            'quality': 'high',
            'speed': 'fast',
            'features': ['typography', 'math', 'professional_formatting', 'code_highlighting'],
            'templates': ['technical', 'academic', 'minimal', 'corporate']
        }
