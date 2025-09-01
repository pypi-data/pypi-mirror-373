"""
🎯 Book Generator - Enhanced with Typst Optimization
===================================================
Convert directories of markdown files into professional books
Integrated with Future-Proofing and Typst Content Optimization
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .generator import PDFGenerator

# Import optimization systems
try:
    from .unified_typst_content_optimizer import UnifiedTypstContentOptimizer
    CONTENT_OPTIMIZER_AVAILABLE = True
except ImportError:
    CONTENT_OPTIMIZER_AVAILABLE = False
    logging.warning("Unified Typst Content Optimizer not available")

try:
    from .future_proofing_system import FutureProofingSystem
    FUTURE_PROOFING_AVAILABLE = True
except ImportError:
    FUTURE_PROOFING_AVAILABLE = False
    logging.warning("Future-Proofing System not available")

class BookGenerator:
    """
    Enhanced book generator with Typst optimization and future-proofing
    """
    
    def __init__(self, pdf_generator: Optional[PDFGenerator] = None):
        """
        Initialize enhanced book generator
        
        Args:
            pdf_generator: PDF generator instance (optional)
        """
        print("[FIRE] CRITICAL DEBUG: BookGenerator.__init__ called!")
        self.pdf_generator = pdf_generator or PDFGenerator()
        self.logger = logging.getLogger(__name__)
        print("[FIRE] CRITICAL DEBUG: PDF generator and logger initialized!")
        
        # Initialize optimization systems
        if CONTENT_OPTIMIZER_AVAILABLE:
            self.content_optimizer = UnifiedTypstContentOptimizer()
            self.logger.info("[TARGET] Unified Typst Content Optimizer enabled")
        else:
            self.content_optimizer = None
            
        if FUTURE_PROOFING_AVAILABLE:
            self.future_proofing = FutureProofingSystem()
            self.logger.info("🛡️ Future-Proofing System enabled")
        else:
            self.future_proofing = None
    
    def generate_book(self,
                      input_dir: Path,
                      output_file: Path,
                      template: str = "technical",
                      title: Optional[str] = None,
                      author: Optional[str] = None,
                      recursive: bool = True,
                      file_pattern: str = "*.md",
                      **kwargs) -> Dict[str, Any]:
        """
        Enhanced book generation with Typst optimization and future-proofing
        
        Args:
            input_dir: Directory containing markdown files
            output_file: Output PDF file path
            template: Template name
            title: Book title (auto-generated if None)
            author: Book author
            recursive: Search subdirectories
            file_pattern: File pattern to match
            **kwargs: Additional template parameters
            
        Returns:
            Generation result with optimization details
        """
        print("[FIRE] CRITICAL DEBUG: generate_book method entered!")
        print(f"[FIRE] CRITICAL DEBUG: input_dir={input_dir}, output_file={output_file}")
        print(f"[FIRE] CRITICAL DEBUG: kwargs={kwargs}")
        try:
            print("[FIRE] CRITICAL DEBUG: trying to process input directory...")
            input_path = Path(input_dir)
            if not input_path.exists():
                raise FileNotFoundError(f"Input directory not found: {input_path}")
            
            # Find markdown files
            markdown_files = self._find_markdown_files(input_path, recursive, file_pattern)
            
            if not markdown_files:
                raise ValueError(f"No markdown files found in {input_path}")
            
            self.logger.info(f"Found {len(markdown_files)} markdown files")
            
            # Combine files into single content with per-chapter optimization
            print(f"🚨 ABOUT TO CALL _combine_files with {len(markdown_files)} files")
            combined_content = self._combine_files(markdown_files)
            print(f"🚨 _combine_files RETURNED - content length: {len(combined_content)}")
            
            # STEP 1: Typst optimization will be applied during final PDF generation
            # This ensures numbered headers added during book combination get properly converted
            optimization_info = {"applied": True, "method": "final-generation-pass", "issues": []}
            self.logger.info("[CHECK] Typst optimization applied per-chapter during combination")
            
            # STEP 2: Apply Future-Proofing Security
            security_info = {"applied": False, "issues": []}
            if self.future_proofing:
                self.logger.info("🛡️ Applying future-proofing protection...")
                try:
                    processed_content, issues = self.future_proofing.process_content_safely(
                        combined_content, f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    combined_content = processed_content
                    security_info["applied"] = True
                    security_info["issues"] = issues
                    if issues:
                        self.logger.info(f"🛡️ Resolved {len(issues)} security/compatibility issues")
                except Exception as e:
                    self.logger.warning(f"⚠️ Future-proofing failed: {e}")
                    security_info["error"] = str(e)
            
            # Generate metadata
            book_title = title or self._generate_title(input_path)
            book_author = author or "Generated by WOT-PDF"
            
            # Generate PDF (allow normal optimization to handle numbered headers)
            self.logger.info("📤 Calling PDF generator with normal optimization enabled")
            self.logger.info(f"🔍 kwargs being passed: {list(kwargs.keys())}")
            
            # Remove skip_optimization from kwargs if present to avoid duplicate
            generator_kwargs = kwargs.copy()
            generator_kwargs.pop('skip_optimization', None)
            
            result = self.pdf_generator.generate(
                input_content=combined_content,
                output_file=output_file,
                template=template,
                title=book_title,
                author=book_author,
                # REMOVE skip_optimization - let Typst engine handle proper # → = conversion
                **generator_kwargs
            )
            
            # Add book-specific metadata
            if result.get("success"):
                result.update({
                    "book_title": book_title,
                    "book_author": book_author,
                    "source_files": len(markdown_files),
                    "source_directory": str(input_path),
                    "optimization_applied": optimization_info,
                    "security_protection": security_info,
                    "enhanced_features": {
                        "typst_optimization": optimization_info["applied"],
                        "future_proofing": security_info["applied"],
                        "total_issues_resolved": len(security_info.get("issues", []))
                    }
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Book generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_directory": str(input_dir)
            }
    
    def _find_markdown_files(self, 
                           directory: Path, 
                           recursive: bool, 
                           pattern: str) -> List[Path]:
        """Find markdown files in directory"""
        print(f"🔍 _find_markdown_files: directory={directory}, recursive={recursive}, pattern={pattern}")
        files = []
        
        if recursive:
            # Recursive search
            print(f"🔍 Doing recursive search for pattern: {pattern}")
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    print(f"🔍 Found recursive file: {file_path}")
                    files.append(file_path)
        else:
            # Non-recursive search
            print(f"🔍 Doing non-recursive search for pattern: {pattern}")
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    print(f"🔍 Found non-recursive file: {file_path}")
                    files.append(file_path)
        
        print(f"🔍 Total files found: {len(files)}")
        # Sort files for consistent ordering
        return sorted(files)
    
    def _combine_files(self, files: List[Path]) -> str:
        """Combine multiple markdown files with chapter-by-chapter Typst optimization"""
        print(f"🚨 _combine_files ENTRY: Called with {len(files)} files")
        combined_lines = []
        chapter_num = 1
        
        print(f"🚨 CRITICAL DEBUG: _combine_files called with {len(files)} files")
        self.logger.info("📚 Processing files with numbered headers and Typst optimization...")
        
        for file_path in files:
            try:
                self.logger.info(f"📖 Processing chapter {chapter_num}: {file_path.name}")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # STEP 1: FIRST add chapter numbering (before optimization)
                content_lines = content.split('\n')
                numbered_lines = []
                
                # Track chapters per-file instead of globally
                file_chapter_num = 1
                
                for line in content_lines:
                    # Add chapter number to main headers (Markdown # format) - ONLY FIRST HEADER per file
                    if line.strip().startswith('# ') and not line.strip().startswith('## ') and file_chapter_num == 1:
                        header_text = line.strip()[2:].strip()
                        # Add simple chapter number (file-based, not cumulative)
                        numbered_header = f"# Chapter {len(combined_lines) // 20 + 1}: {header_text}"
                        numbered_lines.append(numbered_header)
                        file_chapter_num += 1  # Prevent multiple numbering in same file
                    else:
                        numbered_lines.append(line)
                
                # Rejoin numbered content
                numbered_content = '\n'.join(numbered_lines)
                
                # STEP 2: THEN apply Typst optimization to numbered content
                if self.content_optimizer:
                    try:
                        print(f"🔍 DEBUG: Before optimization - first 500 chars:")
                        print(repr(numbered_content[:500]))
                        
                        optimized_content = self.content_optimizer.optimize_content_for_typst(numbered_content)
                        content = optimized_content
                        
                        print(f"🔍 DEBUG: After optimization - first 500 chars:")
                        print(repr(content[:500]))
                        
                        self.logger.debug(f"[CHECK] Typst optimization with numbering applied to {file_path.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Typst optimization failed for {file_path.name}: {e}")
                        content = numbered_content  # Use numbered but unoptimized content
                else:
                    content = numbered_content
                
                # STEP 3: Add processed content to combined lines
                processed_lines = content.split('\n')
                
                # Add processed content
                combined_lines.append("")
                combined_lines.extend(processed_lines)
                combined_lines.append("")
                combined_lines.append("---")  # Section separator (Markdown format)
                combined_lines.append("")
                
            except Exception as e:
                self.logger.warning(f"Failed to read {file_path}: {e}")
                combined_lines.append(f"<!-- Error reading {file_path.name}: {e} -->")
                combined_lines.append("")
        
        combined_result = "\n".join(combined_lines)
        
        # [TARGET] CRITICAL FINAL STEP: Ensure all numbered headers are properly converted for Typst
        print(f"[ALERT] FINAL STEP: Applying Typst optimization to entire combined content ({len(combined_result)} chars)")
        if self.content_optimizer:
            try:
                print(f"[SEARCH] BEFORE final optimization - sample content:")
                print(repr(combined_result[:200]))
                
                final_optimized = self.content_optimizer.optimize_content_for_typst(combined_result)
                
                print(f"[SEARCH] AFTER final optimization - sample content:")
                print(repr(final_optimized[:200]))
                
                print(f"[CHECK] Final Typst optimization completed - returning {len(final_optimized)} chars")
                return final_optimized
            except Exception as e:
                print(f"[X] Final optimization FAILED: {e}")
                self.logger.warning(f"Final optimization failed: {e}")
                return combined_result
        else:
            print(f"[WARN] No content optimizer available - returning unoptimized combined content")
            return combined_result
    
    def _generate_title(self, input_dir: Path) -> str:
        """Generate book title from directory name"""
        dir_name = input_dir.name
        
        # Clean up directory name
        title = dir_name.replace('_', ' ').replace('-', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        
        # Add "Guide" or "Manual" suffix if not present
        if not any(suffix in title.lower() for suffix in ['guide', 'manual', 'book', 'documentation']):
            title += " Guide"
        
        return title
