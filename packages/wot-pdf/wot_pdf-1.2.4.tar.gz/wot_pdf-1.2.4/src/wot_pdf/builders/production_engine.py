#!/usr/bin/env python3
"""
🚀 PRODUCTION ENGINE - MAIN PDF GENERATION COORDINATOR
=====================================================
⚡ Production-ready engine coordinating all WOT-PDF components
🔷 Integrates diagram processing, Markdown conversion, and PDF compilation
📊 Comprehensive error handling with detailed statistics

FEATURES:
- Coordinates DiagramProcessor and MarkdownProcessor
- Handles Typst compilation with professional headers
- Provides detailed build statistics and error reporting
- Supports customizable templates and themes

Extracted from production_builder.py for better modularity.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# WOT-PDF integration
from wot_pdf.core.base_engine import BaseEngine
from wot_pdf.utils.logger import setup_logger


class ProductionEngine(BaseEngine):
    """
    Production-ready PDF generation engine with modular architecture.
    Coordinates diagram processing, Markdown conversion, and Typst compilation.
    """

    def __init__(self):
        """Initialize production engine with modular components."""
        super().__init__()
        self.logger = setup_logger(__name__)
        
        # Initialize modular components (lazy loading)
        self._diagram_processor = None
        self._markdown_processor = None
        self._content_optimizer = None
        
        self.logger.info("🚀 Production Engine initialized")

    @property
    def diagram_processor(self):
        """Lazy loading of diagram processor."""
        if self._diagram_processor is None:
            from .diagram_processor import DiagramProcessor
            self._diagram_processor = DiagramProcessor()
        return self._diagram_processor

    @property
    def markdown_processor(self):
        """Lazy loading of markdown processor."""
        if self._markdown_processor is None:
            from .markdown_processor import MarkdownProcessor
            from wot_pdf.core.unified_typst_content_optimizer import UnifiedTypstContentOptimizer
            
            # Initialize optimizer
            if self._content_optimizer is None:
                self._content_optimizer = UnifiedTypstContentOptimizer()
            
            self._markdown_processor = MarkdownProcessor(
                diagram_processor=self.diagram_processor,
                content_optimizer=self._content_optimizer
            )
        return self._markdown_processor

    def generate_pdf(self, input_file: str, output_file: str, **kwargs) -> Dict[str, Any]:
        """
        Generate PDF from Markdown input with full processing pipeline.
        
        Args:
            input_file: Path to input Markdown file
            output_file: Path to output PDF file
            **kwargs: Additional options (template, theme, etc.)
            
        Returns:
            Dictionary with generation results and statistics
        """
        start_time = time.time()
        
        try:
            # Convert paths
            input_path = Path(input_file)
            output_path = Path(output_file)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            # Read input content
            content = input_path.read_text(encoding='utf-8')
            self.logger.info(f"📖 Read input file: {input_path} ({len(content)} chars)")
            
            # Create intermediate Typst file
            typst_path = output_path.with_suffix('.typ')
            
            # Convert Markdown to Typst
            conversion_stats = self._convert_markdown_to_typst(content, typst_path, **kwargs)
            
            # Compile Typst to PDF
            compilation_result = self._compile_typst(typst_path, output_path)
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Combine statistics
            result = {
                'success': True,
                'input_file': str(input_path),
                'output_file': str(output_path),
                'typst_file': str(typst_path),
                'total_time': total_time,
                'conversion': conversion_stats,
                'compilation': compilation_result,
                'engine': 'ProductionEngine',
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ PDF generated successfully: {output_path}")
            self.logger.info(f"⏱️ Total time: {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            error_time = time.time() - start_time
            self.logger.error(f"❌ PDF generation failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'input_file': input_file,
                'output_file': output_file,
                'error_time': error_time,
                'engine': 'ProductionEngine',
                'timestamp': datetime.now().isoformat()
            }

    def _convert_markdown_to_typst(self, content: str, typst_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Convert Markdown content to Typst with full processing pipeline.
        
        Args:
            content: Markdown content
            typst_path: Output Typst file path
            **kwargs: Conversion options
            
        Returns:
            Conversion statistics and results
        """
        try:
            # Reset processor statistics
            self.markdown_processor.reset_stats()
            
            # Convert Markdown to Typst
            typst_content = self.markdown_processor.convert_markdown_to_typst(content)
            
            # Generate Typst header with metadata
            header = self._generate_typst_header(**kwargs)
            
            # Combine header and content
            full_typst = header + "\n\n" + typst_content
            
            # Write to file
            typst_path.write_text(full_typst, encoding='utf-8')
            
            # Get processing statistics
            conversion_stats = self.markdown_processor.get_stats()
            diagram_stats = self.diagram_processor.get_stats()
            
            result = {
                'success': True,
                'typst_file': str(typst_path),
                'typst_length': len(full_typst),
                'markdown': {
                    'images_processed': conversion_stats.images_processed,
                    'tables_processed': conversion_stats.tables_processed,
                    'diagrams_found': conversion_stats.diagrams_found,
                    'figures_extracted': conversion_stats.figures_extracted
                },
                'diagrams': {
                    'processed': diagram_stats.diagrams_processed,
                    'cached': diagram_stats.diagrams_cached,
                    'rendered': diagram_stats.diagrams_rendered,
                    'cache_hit_rate': diagram_stats.cache_hit_rate
                }
            }
            
            self.logger.info(f"📝 Markdown conversion completed: {len(full_typst)} chars")
            self.logger.info(f"📊 Processed: {conversion_stats.images_processed} images, "
                           f"{conversion_stats.tables_processed} tables, "
                           f"{conversion_stats.diagrams_found} diagrams")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Markdown conversion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _compile_typst(self, typst_path: Path, pdf_path: Path) -> Dict[str, Any]:
        """
        Compile Typst file to PDF using Typst CLI.
        
        Args:
            typst_path: Input Typst file path
            pdf_path: Output PDF file path
            
        Returns:
            Compilation results and statistics
        """
        try:
            # Check if Typst CLI is available
            try:
                subprocess.run(['typst', '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError("Typst CLI not found. Please install Typst.")
            
            # Prepare compilation command
            cmd = [
                'typst', 'compile',
                str(typst_path),
                str(pdf_path)
            ]
            
            # Execute compilation
            self.logger.info(f"🔧 Compiling with Typst: {' '.join(cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            
            compilation_time = time.time() - start_time
            
            if result.returncode == 0:
                # Check if PDF was created
                if pdf_path.exists():
                    pdf_size = pdf_path.stat().st_size
                    
                    self.logger.info(f"✅ Typst compilation successful: {pdf_path}")
                    self.logger.info(f"📄 PDF size: {pdf_size:,} bytes")
                    self.logger.info(f"⏱️ Compilation time: {compilation_time:.2f}s")
                    
                    return {
                        'success': True,
                        'pdf_path': str(pdf_path),
                        'pdf_size': pdf_size,
                        'compilation_time': compilation_time,
                        'typst_version': self._get_typst_version(),
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                else:
                    raise RuntimeError("PDF file was not created despite successful compilation")
            else:
                error_msg = f"Typst compilation failed (exit code {result.returncode})"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                
                self.logger.error(f"❌ {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'compilation_time': compilation_time
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Typst compilation timed out")
            return {
                'success': False,
                'error': 'Compilation timed out',
                'timeout': True
            }
        except Exception as e:
            self.logger.error(f"❌ Typst compilation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_typst_header(self, **kwargs) -> str:
        """
        Generate Typst document header with metadata and styling.
        
        Args:
            **kwargs: Header options (title, author, template, etc.)
            
        Returns:
            Typst header string
        """
        template = kwargs.get('template', 'technical')
        title = kwargs.get('title', 'Document')
        author = kwargs.get('author', '')
        date = kwargs.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Professional Typst header
        header = f'''// WOT-PDF Production Template: {template}
// Generated: {datetime.now().isoformat()}

#set document(
  title: "{title}",
  author: "{author}",
  date: datetime.today()
)

#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 2cm),
  header: [
    #set text(size: 10pt, fill: gray)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*],
      [Generated: {date}]
    )
    #line(length: 100%, stroke: 0.5pt + gray)
  ],
  footer: [
    #set text(size: 9pt, fill: gray)
    #line(length: 100%, stroke: 0.5pt + gray)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [Author: {author}],
      [Page #counter(page).display()]
    )
  ]
)

#set text(
  font: "Linux Libertine",
  size: 11pt,
  lang: "en"
)

#set heading(
  numbering: "1.1."
)

#set figure(
  supplement: [Figure]
)

#set table(
  stroke: 0.5pt,
  fill: (x, y) => if y == 0 {{ gray.lighten(80%) }}
)

#show link: underline

// Document content starts here'''
        
        return header

    def _get_typst_version(self) -> Optional[str]:
        """Get Typst CLI version."""
        try:
            result = subprocess.run(['typst', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get comprehensive engine information and capabilities.
        
        Returns:
            Dictionary with engine information
        """
        return {
            'name': 'ProductionEngine',
            'version': '2.0.0',
            'description': 'Production-ready PDF generation with modular architecture',
            'components': {
                'diagram_processor': 'DiagramProcessor',
                'markdown_processor': 'MarkdownProcessor',
                'content_optimizer': 'UnifiedTypstContentOptimizer'
            },
            'capabilities': {
                'diagrams': list(self.diagram_processor.get_available_engines()),
                'formats': ['markdown', 'typst'],
                'output': ['pdf'],
                'features': [
                    'diagram_rendering',
                    'table_processing',
                    'image_processing',
                    'content_optimization',
                    'professional_formatting',
                    'caching',
                    'statistics'
                ]
            },
            'dependencies': {
                'required': ['typst'],
                'optional': ['mmdc', 'dot', 'd2', 'plantuml']
            },
            'typst_version': self._get_typst_version()
        }
