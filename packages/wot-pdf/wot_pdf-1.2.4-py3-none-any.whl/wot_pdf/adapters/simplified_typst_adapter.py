"""
Simplified Typst Engine Adapter
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import subprocess
import tempfile

class SimplifiedTypstAdapter:
    """Simplified Typst engine adapter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self._name = "typst_simplified"
        
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
            with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False) as f:
                # Convert markdown to basic typst
                typst_content = self._markdown_to_typst(content)
                f.write(typst_content)
                temp_typst = f.name
                
            # Compile with typst
            result = subprocess.run([
                'typst', 'compile', temp_typst, str(output_path)
            ], capture_output=True, text=True)
            
            # Cleanup
            os.unlink(temp_typst)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'engine': self._name,
                    'output_file': str(output_path),
                    'template': template,
                    'file_size': output_path.stat().st_size if output_path.exists() else 0
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
            
    def _markdown_to_typst(self, markdown: str) -> str:
        """Convert markdown to basic typst"""
        lines = markdown.strip().split('\n')
        typst_lines = []
        
        for line in lines:
            if line.startswith('# '):
                typst_lines.append(f"= {line[2:]}")
            elif line.startswith('## '):
                typst_lines.append(f"== {line[3:]}")
            elif line.startswith('### '):
                typst_lines.append(f"=== {line[4:]}")
            elif line.strip().startswith('- '):
                typst_lines.append(f"- {line.strip()[2:]}")
            elif line.strip():
                typst_lines.append(line)
            else:
                typst_lines.append("")
                
        return '\n'.join(typst_lines)
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities"""
        return {
            'formats': ['pdf'],
            'quality': 'high',
            'speed': 'fast',
            'features': ['typography', 'formatting']
        }
