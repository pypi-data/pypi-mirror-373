#!/usr/bin/env python3
"""
🎯 WOT-PDF PRODUCTION BUILDER - Modular Production Pipeline
==========================================================
🚀 Orchestrates end-to-end Markdown→Typst→PDF pipeline
📊 Coordinates diagram processing and content conversion  
🎨 Clean modular architecture with specialized components

FEATURES:
- Modular architecture with clear separation of concerns
- Integration with DiagramProcessor for diagram handling
- Integration with MarkdownProcessor for content conversion
- Production-ready pipeline coordination
- Comprehensive error handling and logging
- Build statistics and performance monitoring

ARCHITECTURE:
- ProductionBuilder: Main orchestrator class
- DiagramProcessor: Handles diagram rendering and caching
- MarkdownProcessor: Handles markdown to Typst conversion
- Clean interfaces between components
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# WOT-PDF integration
from wot_pdf.core.base_engine import BaseEngine
from wot_pdf.utils.logger import setup_logger

# Import our modular components
from .diagram_processor import DiagramProcessor, DiagramMetadata
from .markdown_processor import MarkdownProcessor


@dataclass
class ProductionBuildResult:
    """Result of production build process"""
    success: bool
    output_file: Optional[str] = None
    typst_file: Optional[str] = None
    diagrams_processed: int = 0
    diagrams_cached: int = 0
    build_time_seconds: float = 0.0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class ProductionBuilder(BaseEngine):
    """
    🎯 PRODUCTION BUILDER - Main Pipeline Orchestrator
    =================================================
    Coordinates the complete Markdown→Typst→PDF production pipeline
    using modular components for diagram processing and markdown conversion.
    """
    
    def __init__(self, output_dir: str = "output", cache_dir: str = ".cache", 
                 debug: bool = False):
        """
        Initialize production builder with modular components.
        
        Args:
            output_dir: Directory for output files
            cache_dir: Directory for caching (diagrams, etc.)
            debug: Enable debug logging
        """
        super().__init__()
        
        # Setup directories
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = setup_logger(__name__, debug=debug)
        self.debug = debug
        
        # Initialize modular components
        self.diagram_processor = DiagramProcessor(
            cache_dir=str(self.cache_dir / "diagrams"),
            debug=debug
        )
        
        self.markdown_processor = MarkdownProcessor(
            debug=debug
        )
        
        self.logger.info("🎯 Production Builder initialized with modular architecture")
        
    def generate(self, input_content: str, output_file: str, 
                template: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate PDF from markdown content using modular pipeline.
        
        Args:
            input_content: Markdown content to convert
            output_file: Output PDF file path
            template: Typst template to use
            **kwargs: Additional options
            
        Returns:
            Dictionary with generation results
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🚀 Starting production build: {output_file}")
            
            # Step 1: Process diagrams
            self.logger.debug("📊 Step 1: Processing diagrams...")
            diagram_results = self.diagram_processor.process_content_diagrams(input_content)
            
            if not diagram_results['success']:
                return {
                    'success': False,
                    'error': f"Diagram processing failed: {diagram_results.get('error', 'Unknown error')}",
                    'stage': 'diagram_processing'
                }
            
            # Step 2: Convert markdown to Typst
            self.logger.debug("📝 Step 2: Converting Markdown to Typst...")
            content_with_diagrams = diagram_results['processed_content']
            
            typst_results = self.markdown_processor.convert_to_typst(
                content_with_diagrams,
                template=template,
                **kwargs
            )
            
            if not typst_results['success']:
                return {
                    'success': False,
                    'error': f"Markdown conversion failed: {typst_results.get('error', 'Unknown error')}",
                    'stage': 'markdown_conversion'
                }
            
            # Step 3: Save Typst file
            typst_content = typst_results['typst_content']
            typst_file = self._generate_typst_filename(output_file)
            
            with open(typst_file, 'w', encoding='utf-8') as f:
                f.write(typst_content)
            
            self.logger.debug(f"💾 Typst file saved: {typst_file}")
            
            # Step 4: Compile to PDF (if requested)
            pdf_file = None
            if output_file.endswith('.pdf'):
                pdf_results = self._compile_typst_to_pdf(typst_file, output_file)
                
                if pdf_results['success']:
                    pdf_file = output_file
                    self.logger.info(f"✅ PDF generated: {pdf_file}")
                else:
                    return {
                        'success': False,
                        'error': f"PDF compilation failed: {pdf_results.get('error', 'Unknown error')}",
                        'stage': 'pdf_compilation',
                        'typst_file': str(typst_file)
                    }
            
            # Calculate build time
            build_time = (datetime.now() - start_time).total_seconds()
            
            # Create final result
            result = ProductionBuildResult(
                success=True,
                output_file=pdf_file,
                typst_file=str(typst_file),
                diagrams_processed=diagram_results.get('diagrams_processed', 0),
                diagrams_cached=diagram_results.get('diagrams_cached', 0),
                build_time_seconds=build_time
            )
            
            self.logger.info(f"🎉 Production build complete in {build_time:.2f}s")
            self.logger.info(f"   📊 Diagrams: {result.diagrams_processed} processed, {result.diagrams_cached} cached")
            
            # Return comprehensive results
            return {
                'success': True,
                'output_file': result.output_file,
                'typst_file': result.typst_file,
                'build_stats': {
                    'diagrams_processed': result.diagrams_processed,
                    'diagrams_cached': result.diagrams_cached,
                    'build_time_seconds': result.build_time_seconds
                },
                'diagram_results': diagram_results,
                'markdown_results': typst_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Production build failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'stage': 'unknown',
                'build_time_seconds': (datetime.now() - start_time).total_seconds()
            }
    
    def _generate_typst_filename(self, output_file: str) -> str:
        """Generate Typst filename from output filename."""
        output_path = Path(output_file)
        if output_path.suffix == '.pdf':
            typst_file = output_path.with_suffix('.typ')
        else:
            typst_file = output_path.with_suffix('.typ')
        
        return str(typst_file)
    
    def _compile_typst_to_pdf(self, typst_file: str, output_file: str) -> Dict[str, Any]:
        """
        Compile Typst file to PDF.
        
        Args:
            typst_file: Path to Typst source file
            output_file: Path to output PDF file
            
        Returns:
            Compilation results
        """
        try:
            import subprocess
            
            # Try to compile with typst
            cmd = ['typst', 'compile', typst_file, output_file]
            
            self.logger.debug(f"🔧 Compiling: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                return {
                    'success': False,
                    'error': f"Typst compilation failed (exit code {result.returncode})",
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': "Typst compilation timed out"
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': "Typst compiler not found. Please install typst CLI."
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Compilation error: {e}"
            }
    
    def get_build_statistics(self) -> Dict[str, Any]:
        """Get comprehensive build statistics from all components."""
        return {
            'diagram_processor_stats': self.diagram_processor.get_statistics(),
            'markdown_processor_stats': self.markdown_processor.get_statistics(),
            'cache_info': {
                'cache_dir': str(self.cache_dir),
                'cache_size_mb': self._get_cache_size_mb()
            }
        }
    
    def _get_cache_size_mb(self) -> float:
        """Calculate total cache size in MB."""
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            
            return total_size / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    def clear_cache(self) -> bool:
        """Clear all caches."""
        try:
            self.diagram_processor.clear_cache()
            self.logger.info("🧹 Production builder cache cleared")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to clear cache: {e}")
            return False
    
    def validate_setup(self) -> Dict[str, Any]:
        """Validate the production environment setup."""
        validation_results = {
            'diagram_tools': self.diagram_processor.validate_cli_tools(),
            'markdown_processor': self.markdown_processor.validate_setup(),
            'directories': {
                'output_dir_exists': self.output_dir.exists(),
                'output_dir_writable': os.access(self.output_dir, os.W_OK),
                'cache_dir_exists': self.cache_dir.exists(),
                'cache_dir_writable': os.access(self.cache_dir, os.W_OK)
            }
        }
        
        # Overall validation status
        validation_results['overall_status'] = all([
            validation_results['diagram_tools'].get('valid', False),
            validation_results['markdown_processor'].get('valid', False),
            validation_results['directories']['output_dir_writable'],
            validation_results['directories']['cache_dir_writable']
        ])
        
        return validation_results
    
    def print_setup_status(self):
        """Print comprehensive setup status to console."""
        print("🎯 PRODUCTION BUILDER SETUP STATUS")
        print("=" * 50)
        
        validation = self.validate_setup()
        
        # Diagram tools status
        diagram_status = validation['diagram_tools']
        print(f"\n📊 Diagram Tools:")
        for tool, available in diagram_status.get('tools', {}).items():
            status = "✅" if available else "❌"
            print(f"   {status} {tool}")
        
        # Markdown processor status
        markdown_status = validation['markdown_processor']
        print(f"\n📝 Markdown Processor: {'✅' if markdown_status.get('valid') else '❌'}")
        
        # Directory status
        dirs = validation['directories']
        print(f"\n📁 Directories:")
        print(f"   ✅ Output: {self.output_dir} ({'writable' if dirs['output_dir_writable'] else 'not writable'})")
        print(f"   ✅ Cache: {self.cache_dir} ({'writable' if dirs['cache_dir_writable'] else 'not writable'})")
        
        # Overall status
        overall = validation['overall_status']
        print(f"\n🏆 Overall Status: {'✅ READY' if overall else '❌ ISSUES DETECTED'}")
        
        if not overall:
            print("\n⚠️  Please resolve the issues above before using production builder.")


# Convenience function for quick builds
def build_pdf(input_content: str, output_file: str, **kwargs) -> Dict[str, Any]:
    """
    Quick build function for PDF generation.
    
    Args:
        input_content: Markdown content
        output_file: Output PDF file path
        **kwargs: Additional build options
        
    Returns:
        Build results
    """
    builder = ProductionBuilder()
    return builder.generate(input_content, output_file, **kwargs)
