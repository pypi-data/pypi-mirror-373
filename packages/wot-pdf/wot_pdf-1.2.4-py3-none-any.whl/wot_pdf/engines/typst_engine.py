"""
🎯 Typst Engine - Professional Implementation v2.0
===============================================
Advanced Typst engine with professional architecture
Integrated with configuration management and performance monitoring
"""

import os
import re
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import professional configuration system  
try:
    from ..core.engine_configuration_protocol import (
        EngineConfiguration, 
        get_config_manager
    )
    PROFESSIONAL_CONFIG_AVAILABLE = True
except ImportError:
    PROFESSIONAL_CONFIG_AVAILABLE = False
    logging.warning("Professional configuration system not available")

# Import our enhanced components
try:
    from ..core.future_proofing_system import FutureProofingSystem
    FUTURE_PROOFING_AVAILABLE = True
except ImportError:
    FUTURE_PROOFING_AVAILABLE = False
    logging.warning("Future-proofing system not available")

# Import unified content optimizer
try:
    from ..core.unified_typst_content_optimizer import UnifiedTypstContentOptimizer
    UNIFIED_OPTIMIZER_AVAILABLE = True
except ImportError:
    # Fallback to old optimizer
    try:
        from ..core.typst_content_optimizer import TypstContentOptimizer
        UNIFIED_OPTIMIZER_AVAILABLE = False
    except ImportError:
        UNIFIED_OPTIMIZER_AVAILABLE = None
        logging.warning("No Typst content optimizer available")

# Import professional engine as optional upgrade
try:
    from .typst_engine_v2_professional import TypstEngineV2, CompilationResult
    PROFESSIONAL_ENGINE_AVAILABLE = True
except ImportError:
    PROFESSIONAL_ENGINE_AVAILABLE = False

# Import LaTeX math converter
try:
    from ..utils.latex_math_converter import LaTeXToTypstMathConverter
    LATEX_MATH_CONVERTER_AVAILABLE = True
except ImportError:
    LATEX_MATH_CONVERTER_AVAILABLE = False
    logging.warning("LaTeX math converter not available")

# Import Unicode escape system
try:
    from ..utils.unicode_escape_system import UnicodeEscapeSystem, ContextualEscapeProcessor
    UNICODE_ESCAPE_AVAILABLE = True
except ImportError:
    UNICODE_ESCAPE_AVAILABLE = False
    logging.warning("Unicode escape system not available")

class TypstEngine:
    """
    🎯 Advanced Typst engine with professional architecture support
    =============================================================
    
    Includes future-proofing, configuration management, and performance monitoring.
    Automatically upgrades to professional engine when available.
    """
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize Typst engine with optional professional configuration"""
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(__file__).parent.parent
        
        # Try to create professional engine first
        if PROFESSIONAL_ENGINE_AVAILABLE and config is not None:
            self.logger.info("🎯 Initializing with professional engine")
            try:
                # Delegate to professional engine
                self._professional_engine = TypstEngineV2(config)
                self._use_professional = True
                self.logger.info("✅ Professional engine initialized successfully")
            except Exception as e:
                self.logger.warning(f"Professional engine initialization failed: {e}")
                self._professional_engine = None
                self._use_professional = False
        else:
            self._professional_engine = None
            self._use_professional = False
        
        if not self._use_professional:
            # Initialize legacy engine
            self._initialize_legacy_engine()
    
    def _initialize_legacy_engine(self):
        """Initialize legacy engine components"""
        # Initialize future-proofing system
        if FUTURE_PROOFING_AVAILABLE:
            self.future_proofing = FutureProofingSystem()
            self.logger.info("🛡️ Future-proofing system enabled")
        else:
            self.future_proofing = None
            self.logger.warning("⚠️ Future-proofing system disabled")
        
        # Initialize LaTeX math converter
        if LATEX_MATH_CONVERTER_AVAILABLE:
            self.latex_math_converter = LaTeXToTypstMathConverter()
            self.logger.info("🧮 LaTeX math converter enabled")
        else:
            self.latex_math_converter = None
            self.logger.warning("⚠️ LaTeX math converter not available")
        
        # Initialize Unicode escape system
        if UNICODE_ESCAPE_AVAILABLE:
            self.unicode_escape_system = UnicodeEscapeSystem()
            self.contextual_escape_processor = ContextualEscapeProcessor()
            self.logger.info("🔤 Unicode escape system enabled")
        else:
            self.unicode_escape_system = None
            self.contextual_escape_processor = None
            self.logger.warning("⚠️ Unicode escape system not available")
        
        # Initialize content optimizer
        if UNIFIED_OPTIMIZER_AVAILABLE is True:
            self.content_optimizer = UnifiedTypstContentOptimizer(debug=True)
            self.logger.info("🚀 Unified Typst content optimizer enabled")
        elif UNIFIED_OPTIMIZER_AVAILABLE is False:
            self.content_optimizer = TypstContentOptimizer()
            self.logger.info("⚙️ Legacy Typst content optimizer enabled")
        else:
            self.content_optimizer = None
            self.logger.warning("⚠️ No content optimizer available")
        
        # Check if Typst CLI is available
        self.typst_available = self._check_typst_cli()
        
        if not self.typst_available:
            self.logger.warning("System Typst CLI not found - this engine will not function")
    
    def _check_typst_cli(self) -> bool:
        """Check if Typst CLI is available in system PATH"""
        try:
            result = subprocess.run(
                ["typst", "--version"], 
                capture_output=True, 
                encoding='utf-8',
                errors='replace',
                timeout=5
            )
            if result.returncode == 0:
                self.logger.info(f"Typst CLI found: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False

    def generate(self, 
                 content: str,
                 output_file: Path,
                 template: str = "technical",
                 **kwargs) -> Dict[str, Any]:
        """
        Generate PDF using Typst with automatic professional engine delegation
        
        Args:
            content: Markdown content
            output_file: Output PDF path
            template: Template name
            **kwargs: Additional options
            
        Returns:
            Generation result dictionary
        """
        
        # Delegate to professional engine if available
        if self._use_professional and self._professional_engine:
            self.logger.info("🎯 Using professional engine for generation")
            try:
                result = self._professional_engine.generate(content, output_file, template, **kwargs)
                
                # Convert CompilationResult to legacy format if needed
                if hasattr(result, 'success'):
                    return {
                        "success": result.success,
                        "output_file": str(result.output_file) if result.output_file else None,
                        "error": result.error_message,
                        "engine": "typst_professional_v2",
                        "metrics": result.metrics.__dict__ if result.metrics else None
                    }
                else:
                    return result
                    
            except Exception as e:
                self.logger.error(f"Professional engine failed: {e}, falling back to legacy")
                # Fall through to legacy engine
        
        # Legacy engine implementation
        return self._generate_legacy(content, output_file, template, **kwargs)
    
    def _generate_legacy(self, content: str, output_file: Path, template: str, **kwargs) -> Dict[str, Any]:
        """Legacy generation implementation"""
        
        self.logger.info(f"🔧 TypstEngine.generate called with skip_optimization={kwargs.get('skip_optimization', 'NOT_SET')}")
        
        if not self.typst_available:
            return {
                "success": False,
                "error": "Typst CLI not available"
            }
        
        # Generate unique document ID for compilation management
        document_id = f"typst_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # STEP 1: Apply future-proofing protection
            if self.future_proofing:
                # Process content through security and version management
                processed_content, issues = self.future_proofing.process_content_safely(
                    content, document_id
                )
                
                if issues:
                    self.logger.info(f"🛡️ Future-proofing applied: {len(issues)} issues resolved")
                    for issue in issues[:3]:  # Log first 3 issues
                        self.logger.debug(f"   - {issue}")
                
                content = processed_content
            
            # STEP 2: Use safe compilation context
            if self.future_proofing:
                with self.future_proofing.safe_compilation_context(document_id) as slot:
                    return self._compile_with_slot(content, output_file, template, slot, **kwargs)
            else:
                # Fallback to direct compilation
                return self._compile_direct(content, output_file, template, **kwargs)
            
        except Exception as e:
            self.logger.error(f"❌ Typst generation failed for {document_id}: {e}")
            raise
    
    def _compile_with_slot(self, content: str, output_file: Path, template: str, slot, **kwargs) -> Dict[str, Any]:
        """Compile Typst with managed compilation slot"""
        self.logger.info(f"🔧 Compiling with managed slot: {slot.document_id}")
        
        # Convert markdown to Typst using temp directory from slot
        skip_optimization = kwargs.pop('skip_optimization', False)
        
        # PROBLEM 6 DEBUG - Pokazuj skip_optimization
        print(f"[FIRE] DEBUG: _compile_with_slot skip_optimization={skip_optimization}")
        
        typst_content = self._markdown_to_typst(content, template, skip_optimization=skip_optimization, **kwargs)
        
        # Create temp file in managed directory
        temp_typst_file = Path(slot.temp_dir) / "document.typ"
        temp_typst_file.write_text(typst_content, encoding='utf-8')
        
        # PROBLEM 6 DEBUG - Shrani copy za debugging
        debug_copy = Path("debug_document.typ")
        debug_copy.write_text(typst_content, encoding='utf-8')
        print(f"[FIRE] DEBUG: Generated Typst content saved to {debug_copy.absolute()}")
        
        try:
            # Compile with Typst CLI
            result = subprocess.run([
                'typst', 'compile', str(temp_typst_file), str(output_file)
            ], 
            capture_output=True, 
            encoding='utf-8',
            errors='replace',  # Handle encoding errors gracefully
            timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                file_size = output_file.stat().st_size if output_file.exists() else 0
                self.logger.info(f"✅ Typst compilation successful: {file_size} bytes")
                
                return {
                    "success": True,
                    "output_file": str(output_file),
                    "file_size_bytes": file_size,
                    "engine": "typst",
                    "compilation_slot": slot.document_id,
                    "typst_source": str(temp_typst_file)
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown compilation error"
                self.logger.error(f"[X] Typst compilation failed: {error_msg}")
                
                return {
                    "success": False,
                    "error": f"Typst compilation failed: {error_msg}",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Typst compilation timeout")
            return {
                "success": False,
                "error": "Compilation timeout (5 minutes exceeded)"
            }
        except Exception as e:
            self.logger.error(f"❌ Compilation process error: {e}")
            return {
                "success": False,
                "error": f"Process error: {e}"
            }
    
    def _compile_direct(self, content: str, output_file: Path, template: str, **kwargs) -> Dict[str, Any]:
        """Direct compilation without slot management (fallback)"""
        self.logger.warning("⚠️ Using direct compilation (no future-proofing)")
        
        # Convert markdown to Typst
        skip_optimization = kwargs.pop('skip_optimization', False)
        typst_content = self._markdown_to_typst(content, template, skip_optimization=skip_optimization, **kwargs)
        
        # Create temporary Typst file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False, encoding='utf-8') as f:
            f.write(typst_content)
            temp_typst_file = f.name
        
        try:
            # Compile with Typst CLI
            result = subprocess.run([
                'typst', 'compile', temp_typst_file, str(output_file)
            ], 
            capture_output=True, 
            timeout=60,
            encoding='utf-8',
            errors='replace',  # Handle encoding errors gracefully
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            if result.returncode == 0:
                file_size = output_file.stat().st_size if output_file.exists() else 0
                return {
                    "success": True,
                    "output_file": str(output_file),
                    "template": template,
                    "engine": "typst_direct",
                    "file_size_bytes": file_size,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = result.stderr or result.stdout or "Unknown Typst error"
                self.logger.error(f"Typst compilation failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"Typst compilation failed: {error_msg}",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
                
        finally:
            # Cleanup temporary file
            try:
                os.unlink(temp_typst_file)
            except OSError:
                pass
    
    def _markdown_to_typst(self, markdown_content: str, template: str, skip_optimization: bool = False, **kwargs) -> str:
        """
        Convert markdown content to Typst syntax
        
        This is a simplified, clean conversion focused on reliability
        """
        self.logger.info(f"🔍 _markdown_to_typst called with skip_optimization={skip_optimization}")
        
        # Get template
        typst_template = self._get_template(template)
        
        # Basic metadata
        title = kwargs.get('title', 'Document')
        author = kwargs.get('author', 'Generated by WOT-PDF')
        
        # Apply template with metadata
        header = typst_template.format(
            title=title,
            author=author,
            date=datetime.now().strftime("%B %d, %Y")
        )
        
        # Convert markdown to Typst content
        typst_content = self._convert_markdown_syntax(markdown_content, skip_optimization=skip_optimization)
        
        return header + "\n\n" + typst_content
    
    def _convert_markdown_syntax(self, content: str, skip_optimization: bool = False) -> str:
        """
        Enhanced markdown to Typst conversion with unified optimizer
        """
        
        # PROBLEM 6 DEBUG - Vedno loggiraj
        print(f"[FIRE] DEBUG: _convert_markdown_syntax called with skip_optimization={skip_optimization}")
        self.logger.info(f"[FIRE] DEBUG: _convert_markdown_syntax called with skip_optimization={skip_optimization}")
        
        # Check if optimization should be skipped (for pre-processed content)
        if skip_optimization:
            print(f"🔄 Skipping optimization - content already processed")
            self.logger.info("🔄 Skipping optimization - content already processed")
            return content
        
        # IZBOLJŠAVA 1: Convert LaTeX math expressions first
        if hasattr(self, 'latex_math_converter') and self.latex_math_converter is not None:
            try:
                print(f"🧮 Converting LaTeX math expressions to Typst")
                self.logger.info("🧮 Converting LaTeX math expressions to Typst")
                content = self.latex_math_converter.convert_latex_math(content)
                
                # Validate conversion
                if self.latex_math_converter.validate_conversion(content, content):
                    print(f"✅ LaTeX math conversion successful")
                    self.logger.info("✅ LaTeX math conversion successful")
                else:
                    print(f"⚠️ LaTeX math conversion validation failed")
                    self.logger.warning("⚠️ LaTeX math conversion validation failed")
            except Exception as e:
                print(f"❌ LaTeX math conversion failed: {e}")
                self.logger.error(f"❌ LaTeX math conversion failed: {e}")
        else:
            print(f"⚠️ LaTeX math converter not available")
            self.logger.warning("⚠️ LaTeX math converter not available")
        
        # IZBOLJŠAVA 2: Apply Unicode escape processing
        if hasattr(self, 'unicode_escape_system') and self.unicode_escape_system is not None:
            try:
                print(f"🔤 Applying Unicode escape processing")
                self.logger.info("🔤 Applying Unicode escape processing")
                
                # Use contextual processor if available, otherwise fallback
                if hasattr(self, 'contextual_escape_processor') and self.contextual_escape_processor is not None:
                    content = self.contextual_escape_processor.process_document_sections(content)
                    print(f"✅ Contextual Unicode escape processing successful")
                    self.logger.info("✅ Contextual Unicode escape processing successful")
                else:
                    content = self.unicode_escape_system.escape_content(content)
                    print(f"✅ Basic Unicode escape processing successful")
                    self.logger.info("✅ Basic Unicode escape processing successful")
                    
            except Exception as e:
                print(f"❌ Unicode escape processing failed: {e}")
                self.logger.error(f"❌ Unicode escape processing failed: {e}")
        else:
            print(f"⚠️ Unicode escape system not available")
            self.logger.warning("⚠️ Unicode escape system not available")
        
        # PROBLEM 4 REŠEN: Uporabi content optimizer samo če je na voljo in deluje
        if hasattr(self, 'content_optimizer') and self.content_optimizer is not None:
            try:
                print(f"🚀 Using unified Typst content optimizer")
                self.logger.info("🚀 Using unified Typst content optimizer")
                return self.content_optimizer.optimize_content_for_typst(content, "technical")
            except Exception as e:
                print(f"⚠️ Content optimizer failed: {e}, falling back to basic conversion")
                self.logger.warning(f"⚠️ Content optimizer failed: {e}, falling back to basic conversion")
        
        # Fallback: osnovni conversion - SEDAJ SE TA VEDNO IZVRŠUJE
        print(f"🔧 Using ENHANCED basic markdown conversion with header escaping")
        self.logger.info("🔧 Using ENHANCED basic markdown conversion with header escaping")
        return self._basic_markdown_conversion(content)
    
    def _basic_markdown_conversion(self, content: str) -> str:
        """
        Enhanced fallback markdown to Typst conversion with better header handling
        """
        lines = content.split('\n')
        typst_lines = []
        in_code_block = False
        in_table = False
        table_headers = []
        table_rows = []
        code_lang = ""
        
        for i, line in enumerate(lines):
            # Code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    code_lang = line.strip()[3:].strip()
                    if code_lang:
                        typst_lines.append(f"```{code_lang}")
                    else:
                        typst_lines.append("```")
                else:
                    # Ending code block
                    in_code_block = False
                    typst_lines.append("```")
                continue
            
            # If inside code block, preserve line exactly
            if in_code_block:
                typst_lines.append(line)
                continue
            
            # Table detection
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                self.logger.debug(f"Table line detected: {line}")
                if not in_table:
                    # Starting a table
                    in_table = True
                    table_headers = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                    self.logger.debug(f"Table headers: {table_headers}")
                    continue
                elif line.strip().replace('|', '').replace('-', '').replace(' ', '') == '':
                    # Table separator line, skip
                    self.logger.debug("Table separator line, skipping")
                    continue
                else:
                    # Table data row
                    self.logger.debug(f"BEFORE processing table row line: '{line}'")
                    table_row = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                    self.logger.debug(f"AFTER processing table row: {table_row}")
                    table_rows.append(table_row)
                    self.logger.debug(f"Table row added: {table_row}")
                    # Check if next line is still table
                    if i + 1 >= len(lines) or not (lines[i + 1].strip().startswith('|') and lines[i + 1].strip().endswith('|')):
                        # End of table, output it
                        self.logger.debug(f"End of table, creating Typst table with {len(table_headers)} headers and {len(table_rows)} rows")
                        typst_table = self._create_typst_table(table_headers, table_rows)
                        typst_lines.append(typst_table)
                        self.logger.debug(f"Generated Typst table: {typst_table}")
                        in_table = False
                        table_headers = []
                        table_rows = []
                    continue
            
            # Headers - IMPROVED DETECTION
            if line.strip().startswith('#') and not in_code_block:
                # Only convert if it's a proper markdown header (# followed by space)
                import re
                if re.match(r'^#{1,6}\s+', line.strip()):
                    level = len(line.strip()) - len(line.strip().lstrip('#'))
                    header_text = line.strip().lstrip('# ').strip()
                    if level <= 6:
                        # Clean header text but keep it readable
                        safe_header_text = self._escape_header_for_typst(header_text)
                        typst_lines.append(f"{'=' * level} {safe_header_text}")
                        continue
            
            # Horizontal rules
            if line.strip() in ['---', '***', '___']:
                typst_lines.append("#line(length: 100%)")
                continue
            
            # Lists (improved handling)
            if line.strip().startswith(('- ', '* ', '+ ')):
                indent = len(line) - len(line.lstrip())
                item_text = line.strip()[2:].strip()
                # Convert markdown formatting in list items
                item_text = self._convert_inline_formatting(item_text)
                typst_lines.append(' ' * indent + f"- {item_text}")
                continue
            
            # Numbered lists
            if line.strip() and line.strip()[0].isdigit() and '. ' in line.strip():
                indent = len(line) - len(line.lstrip())
                item_text = line.strip().split('. ', 1)[1] if '. ' in line.strip() else line.strip()
                item_text = self._convert_inline_formatting(item_text)
                typst_lines.append(' ' * indent + f"+ {item_text}")
                continue
            
            # Block quotes
            if line.strip().startswith('> '):
                quote_text = line.strip()[2:]
                quote_text = self._convert_inline_formatting(quote_text)
                typst_lines.append(f"#quote[{quote_text}]")
                continue
            
            # Regular text - IMPROVED HASH ESCAPING
            if line.strip():
                safe_line = line
                
                # SYSTEMATIC HASH ESCAPING - Check if line starts with # but wasn't converted as header
                if line.strip().startswith('#'):
                    # This means it wasn't converted as proper markdown header above
                    # So we need to escape it to prevent Typst compilation errors
                    safe_line = line.replace('#', '\\#')
                    self.logger.debug(f"Escaped hash at line start: {line.strip()[:50]}...")
                elif '#' in line:
                    # Escape hash characters in middle of text
                    safe_line = line.replace('#', '\\#')
                    self.logger.debug(f"Escaped hash in text: {line.strip()[:50]}...")
                
                converted_line = self._convert_inline_formatting(safe_line)
                typst_lines.append(converted_line)
            else:
                typst_lines.append("")
        
        return '\n'.join(typst_lines)
    
    def _clean_content_for_typst(self, content: str) -> str:
        """Revolutionary aggressive content cleaning for guaranteed Typst success"""
        try:
            # AGGRESSIVE BUILT-IN PROCESSOR - GUARANTEED ZERO ERRORS
            
            lines = content.split('\n')
            safe_lines = []
            in_code_block = False
            current_language = ""
            
            for line_num, line in enumerate(lines, 1):
                # Handle code block boundaries
                if line.strip().startswith('```'):
                    if not in_code_block:
                        # Starting code block
                        current_language = line.replace('```', '').strip()
                        in_code_block = True
                        if current_language:
                            safe_lines.append(f'```{current_language}')
                        else:
                            safe_lines.append('```')
                    else:
                        # Ending code block
                        safe_lines.append('```')
                        in_code_block = False
                        current_language = ""
                    continue
                
                # If inside code block, preserve ALL content completely
                if in_code_block:
                    # CRITICAL: Preserve Python comments and all code content!
                    safe_lines.append(line)
                    continue
                
                # AGGRESSIVE FILTERING FOR NON-CODE CONTENT
                stripped = line.strip()
                
                # Skip empty lines (they're safe)
                if not stripped:
                    safe_lines.append(line)
                    continue
                
                # Detect and preserve legitimate Typst commands
                if self._is_legitimate_typst_command(stripped):
                    safe_lines.append(line)
                    continue
                
                # Convert markdown headers to Typst syntax
                if self._is_markdown_header(stripped):
                    converted_header = self._convert_header_to_typst(stripped)
                    if converted_header:
                        safe_lines.append(converted_header)
                    continue
                
                # AGGRESSIVE FILTERING: Skip ANY line with problematic patterns
                if self._is_problematic_line(stripped):
                    self.logger.debug(f"⚠️ Skipping problematic line {line_num}: {stripped[:50]}...")
                    continue
                
                # Apply ultra-safe character processing
                safe_line = self._ultra_safe_character_processing(line)
                if safe_line:
                    safe_lines.append(safe_line)
            
            result = '\n'.join(safe_lines)
            self.logger.info(f"🚀 Aggressive processing complete: {len(lines)} → {len(safe_lines)} lines")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Aggressive processing failed: {e}")
            return self._emergency_fallback_processing(content)
    
    def _is_legitimate_typst_command(self, line: str) -> bool:
        """Check if line is a legitimate Typst command."""
        typst_commands = [
            '#set ', '#show ', '#let ', '#import ', '#context ', 
            '#text(', '#cite ', '#raw(', '#figure(', '#table(',
            '#grid(', '#align(', '#block(', '#box('
        ]
        return any(line.startswith(cmd) for cmd in typst_commands)
    
    def _is_markdown_header(self, line: str) -> bool:
        """Check if line is a markdown header."""
        import re
        return re.match(r'^#{1,6}\s+.+', line) is not None
    
    def _convert_header_to_typst(self, line: str) -> str:
        """Convert markdown header to Typst syntax."""
        if line.startswith('######'):
            return f"====== {line.replace('######', '').strip()}"
        elif line.startswith('#####'):
            return f"===== {line.replace('#####', '').strip()}"
        elif line.startswith('####'):
            return f"==== {line.replace('####', '').strip()}"
        elif line.startswith('###'):
            return f"=== {line.replace('###', '').strip()}"
        elif line.startswith('##'):
            return f"== {line.replace('##', '').strip()}"
        elif line.startswith('#'):
            return f"= {line.replace('#', '').strip()}"
        return ""
    
    def _is_problematic_line(self, line: str) -> bool:
        """Check if line contains problematic patterns."""
        # SUPER AGGRESSIVE FILTERING - Better safe than sorry!
        problematic_patterns = [
            # Python code patterns
            'def ', 'class ', 'if __name__', 'import ', 'from ',
            'for i in', 'while ', 'try:', 'except:', 'finally:',
            'range(', 'enumerate(', 'len(', 'str(', 'int(', 'float(',
            
            # Problematic symbols and syntax
            '# ', '#=', '#{', '#[', '@', '$', '<>', '[]', '{}',
            '→', '←', '├', '└', '│', '─',
            
            # File operations and paths
            '.glob(', '.read(', '.write(', 'open(', 'with open',
            'os.path', 'pathlib', '__file__',
            
            # Regular expressions and complex patterns
            're.findall', 're.sub', 're.match', 'regex', 'pattern',
            
            # Error messages and debugging
            'error:', 'Error:', 'ERROR:', 'exception:', 'Exception:',
            'duplicate argument', 'unclosed delimiter', 'expected expression',
            
            # Complex formatting
            'f"', "f'", '.format(', '%s', '%d', '%f',
            
            # Shell commands and system calls
            'subprocess', 'os.system', 'exec(', 'eval(',
            
            # Version control and file management
            'git ', '.git', 'commit', 'branch', 'merge',
            
            # Package management
            'pip install', 'poetry', 'setup.py', 'requirements.txt',
        ]
        
        # Check if line contains any problematic patterns
        line_lower = line.lower()
        for pattern in problematic_patterns:
            if pattern.lower() in line_lower:
                return True
        
        # Additional checks for standalone problematic characters
        if line.startswith('#') and not self._is_markdown_header(line):
            return True
        
        # Check for unbalanced delimiters
        if (line.count('(') != line.count(')') or 
            line.count('[') != line.count(']') or
            line.count('{') != line.count('}')):
            return True
        
        return False
    
    def _ultra_safe_character_processing(self, line: str) -> str:
        """Apply ultra-safe character processing."""
        # Only handle the most critical character replacements
        safe_line = line
        
        # Tree symbols to safe alternatives
        tree_replacements = {
            '├──': '- ',
            '└──': '- ', 
            '│': ' | ',
            '─': ' - ',
            '→': ' -> ',
            '←': ' <- ',
        }
        
        for symbol, replacement in tree_replacements.items():
            safe_line = safe_line.replace(symbol, replacement)
        
        # Only escape absolutely critical characters
        if '\\' in safe_line and not '\\\\' in safe_line:
            safe_line = safe_line.replace('\\', '\\\\')
        
        return safe_line
    
    def _emergency_fallback_processing(self, content: str) -> str:
        """Emergency fallback processing."""
        # Extract only the safest content
        lines = content.split('\n')
        emergency_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Only keep completely safe lines
            if (not stripped or 
                stripped.startswith('=') or  # Typst headers
                (len(stripped) < 50 and not any(char in stripped for char in '#@$<>[]{}'))):
                emergency_lines.append(line)
        
        return '\n'.join(emergency_lines)
    
    def _simple_clean_fallback(self, content: str) -> str:
        """Simple fallback cleaning when modules aren't available"""
        # Basic replacements
        content = content.replace('├──', '- ')
        content = content.replace('└──', '- ')
        content = content.replace('│', '|')
        content = content.replace('─', '-')
        content = content.replace(':', ' -')
        
        # Remove problematic lines
        lines = content.split('\n')
        clean_lines = []
        
        for line in lines:
            if any(problem in line for problem in [
                'def ', 'class ', 'if ', 'for ', '"class":',
                're.findall', '.glob', 'range('
            ]):
                continue
            clean_lines.append(line)
            
        return '\n'.join(clean_lines)
    
    def _clean_python_block(self, block: str) -> str:
        """Clean a Python code block for Typst"""
        lines = block.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip().startswith('```'):
                cleaned_lines.append(line)
                continue
            
            # Clean problematic Python syntax
            cleaned_line = line
            
            # Replace quotes in code with safe alternatives
            if '#' in cleaned_line and not cleaned_line.strip().startswith('#'):
                # Has hash but not a comment line - likely problematic
                cleaned_line = cleaned_line.replace("'", '"')  
                
            # Remove complex regex patterns
            if 're.findall(' in cleaned_line or 're.sub(' in cleaned_line:
                cleaned_line = "    // Complex regex pattern simplified for PDF"
                
            # Handle problematic string patterns
            cleaned_line = cleaned_line.replace("'''", '"""')
            cleaned_line = cleaned_line.replace("')", '")')
            cleaned_line = cleaned_line.replace("('", '("')
            
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_code_line(self, line: str) -> str:
        """Clean individual code line for Typst compatibility"""
        # Replace quotes that cause issues
        cleaned = line.replace("')", '")')
        cleaned = cleaned.replace("('", '("') 
        cleaned = cleaned.replace("'''", '"""')
        
        # Handle hash comments carefully
        if cleaned.strip().startswith('#') and not cleaned.strip().startswith('##'):
            # This is a comment, make it safe
            cleaned = cleaned.replace("'", '"')
            
        return cleaned
    
    def _escape_header_for_typst(self, header_text: str) -> str:
        """
        PROBLEM 1 SOLUTION: Escape header text for safe Typst compilation
        Resolves 'Issue #1:' -> 'Issue \\#1:' conversion errors
        """
        # Escape hash characters that aren't at the start of headers
        safe_text = header_text.replace("#", "\\#")
        
        # Escape other problematic Typst characters
        safe_text = safe_text.replace("@", "\\@")
        safe_text = safe_text.replace("$", "\\$") 
        safe_text = safe_text.replace("[", "\\[")
        safe_text = safe_text.replace("]", "\\]")
        
        # Clean quotes for consistency
        safe_text = safe_text.replace("'", '"')
        
        self.logger.debug(f"🔧 Header escaped: '{header_text}' -> '{safe_text}'")
        return safe_text
    
    def _is_markdown_header(self, line: str) -> bool:
        """
        Better detection of markdown headers vs regular text with # characters
        """
        stripped = line.strip()
        if not stripped.startswith('#'):
            return False
            
        # Count leading # characters
        level = 0
        for char in stripped:
            if char == '#':
                level += 1
            elif char == ' ':
                # Must have space after # characters for valid header
                return level > 0 and level <= 6
            else:
                # No space after # - not a header
                return False
        
        # Line is all # characters - not a header
        return False
    
    def _escape_hash_characters(self, line: str) -> str:
        """
        Escape # characters in regular text (not headers)
        """
        # Don't escape if this looks like a header
        if self._is_markdown_header(line):
            return line
            
        # Escape # characters that appear in regular text
        # But preserve them in contexts where they might be meaningful
        result = line
        
        # Simple approach: escape standalone # characters
        # More sophisticated logic could be added here
        result = re.sub(r'(?<!^)(?<!\s)#(?!\s*\w+:)', r'\\#', result)
        
        return result
    
    def _create_typst_table(self, headers: list, rows: list) -> str:
        """Create Typst table from markdown table data"""
        if not headers:
            return ""
        
        # Calculate column count
        col_count = len(headers)
        
        # Create table header with white text on blue background and center alignment
        header_cells = ', '.join([f'[#text(fill: white, weight: "bold")[#align(center)[{self._escape_typst_text(header)}]]]' for header in headers])
        
        # Create table rows with smart alignment
        table_rows = []
        for row in rows:
            # Pad row if necessary
            while len(row) < col_count:
                row.append("")
            # Smart alignment based on content
            aligned_cells = []
            for cell in row[:col_count]:
                cell_content = cell.strip()
                # Escape special characters in cell content
                escaped_cell = self._escape_typst_text(cell)
                # Check if cell contains primarily numbers/currency/percentages
                if any(c in cell_content for c in ['$', '%', '€', '£']) or cell_content.replace(',', '').replace('.', '').replace('-', '').replace('+', '').replace('$', '').isdigit():
                    aligned_cells.append(f'[#align(right)[{escaped_cell}]]')
                else:
                    aligned_cells.append(f'[#align(left)[{escaped_cell}]]')
            row_cells = ', '.join(aligned_cells)
            table_rows.append(row_cells)
        
        # Combine all rows
        all_rows = [header_cells] + table_rows
        table_content = ',\n  '.join(all_rows)
        
        return f"""#table(
  columns: ({', '.join(['auto'] * col_count)}),
  stroke: 1pt + rgb("#b0b0b0"),
  fill: (x, y) => if y == 0 {{ rgb("#4A90E2") }} else if calc.odd(y) {{ rgb("#f7f8fa") }} else {{ white }},
  align: horizon,
  inset: 8pt,
  {table_content}
)"""
    
    def _convert_inline_formatting(self, text: str) -> str:
        """Convert inline markdown formatting to Typst"""
        import re
        
        # Bold: **text** or __text__ -> *text*
        text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
        text = re.sub(r'__(.+?)__', r'*\1*', text)
        
        # Italic: *text* or _text_ -> _text_
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'_\1_', text)
        text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'_\1_', text)
        
        # Inline code: `code` -> `code`
        text = re.sub(r'`([^`]+?)`', r'`\1`', text)
        
        # Links: [text](url) -> #link("url")[text]
        text = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'#link("\2")[\1]', text)
        
        # Images: ![alt](url) -> #image("url")
        text = re.sub(r'!\[([^\]]*?)\]\(([^)]+?)\)', r'#image("\2")', text)
        
        # Strikethrough: ~~text~~ -> #strike[text]
        text = re.sub(r'~~(.+?)~~', r'#strike[\1]', text)
        
        return text
    
    def _escape_typst_text(self, text: str) -> str:
        """Escape special characters for Typst"""
        # CRITICAL FIX: Avoid double-escaping when Unicode escape system is active
        # Check if Unicode escape system has already processed dollar signs
        if hasattr(self, 'unicode_escape_system') and self.unicode_escape_system is not None:
            # Unicode escape system already handled dollar signs, SKIP dollar escaping
            self.logger.debug(f"🔤 Skipping dollar escape (Unicode escape system active): '{text[:50]}...'")
        else:
            # Escape dollar signs only when Unicode escape system is not available
            text = text.replace('$', r'\$')
        
        # Always escape other special characters
        text = text.replace('#', r'\#')
        text = text.replace('@', r'\@')
        return text
    
    def _get_template(self, template_name: str) -> str:
        """Get Typst template from file or inline"""
        template_dir = self.base_dir / "templates" / "typst"
        template_file = template_dir / f"{template_name}.typ"
        
        # Try to load from file first
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                self.logger.warning(f"Failed to load template file {template_file}: {e}")
        
        # Fallback to inline templates
        return self._get_inline_template(template_name)
    
    def _get_inline_template(self, template_name: str) -> str:
        """Get fallback inline Typst template"""
        templates = {
            "technical": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "New Computer Modern",
  size: 11pt,
  lang: "en"
)

#set heading(numbering: "1.1")
#set par(justify: true, leading: 0.65em)

#align(center)[
  #text(size: 20pt, weight: "bold")[{title}]
  
  #v(1em)
  
  #text(size: 12pt)[{author}]
  
  #v(0.5em)
  
  #text(size: 10pt)[{date}]
]

#v(2em)''',

            "academic": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4", 
  margin: (left: 3cm, right: 3cm, top: 2.5cm, bottom: 2.5cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Linux Libertine",
  size: 12pt,
  lang: "en"
)

#set heading(numbering: "1.")
#set par(justify: true, first-line-indent: 1.5em)

#align(center)[
  #text(size: 18pt, weight: "bold")[{title}]
  
  #v(1em)
  
  #text(size: 14pt)[{author}]
  
  #v(0.5em)
  
  #text(size: 10pt)[{date}]
]

#v(2em)''',

            "minimal": '''#set document(title: "{title}", author: "{author}")
#set page(margin: 2cm, numbering: "1")
#set text(font: "Arial", size: 11pt)
#set heading(numbering: "1.")

#align(center)[
  #text(size: 16pt, weight: "bold")[{title}]
  #v(1em)
  #text(size: 10pt)[{author} • {date}]
]

#v(1.5em)''',

            "corporate": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm),
  numbering: "1",
  number-align: center,
  header: [
    #line(length: 100%, stroke: 0.5pt + gray)
    #v(-8pt)
    #text(size: 8pt, fill: gray)[{title}]
    #h(1fr)
    #text(size: 8pt, fill: gray)[{date}]
  ]
)

#set text(font: "Arial", size: 11pt)
#set heading(numbering: "1.")
#set par(justify: true)

#align(center)[
  #text(size: 20pt, weight: "bold", fill: rgb("#1f4788"))[{title}]
  
  #v(0.5em)
  
  #text(size: 12pt, fill: gray)[{author}]
  
  #v(0.3em)
  
  #text(size: 10pt, fill: gray)[{date}]
]

#v(2em)''',

            "educational": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: 2.5cm,
  numbering: "1",
  number-align: center,
)

#set text(font: "Open Sans", size: 11pt)
#set heading(numbering: "1.")
#set par(justify: true, leading: 0.7em)

#rect(
  width: 100%,
  fill: rgb("#f0f8ff"),
  stroke: rgb("#4a90e2"),
  radius: 5pt,
  inset: 1em
)[
  #align(center)[
    #text(size: 18pt, weight: "bold", fill: rgb("#2c5aa0"))[{title}]
    
    #v(0.5em)
    
    #text(size: 12pt)[{author}]
    
    #v(0.3em)
    
    #text(size: 10pt, style: "italic")[{date}]
  ]
]

#v(2em)'''
        }
        
        return templates.get(template_name, templates["technical"])

# PROFESSIONAL FACTORY FUNCTIONS
# ================================

def create_fast_typst_engine() -> TypstEngine:
    """
    🚀 Create Typst engine optimized for speed
    ===========================================
    Uses fast configuration with minimal processing
    """
    if PROFESSIONAL_CONFIG_AVAILABLE:
        from ..core.engine_configuration_protocol import ConfigurationFactory
        config = ConfigurationFactory.create_fast_config()
        return TypstEngine(config)
    else:
        return TypstEngine()

def create_quality_typst_engine() -> TypstEngine:
    """
    ✨ Create Typst engine optimized for quality
    ===========================================  
    Uses quality configuration with full optimization
    """
    if PROFESSIONAL_CONFIG_AVAILABLE:
        from ..core.engine_configuration_protocol import ConfigurationFactory
        config = ConfigurationFactory.create_quality_config()
        return TypstEngine(config)
    else:
        return TypstEngine()

def create_enterprise_typst_engine() -> TypstEngine:
    """
    🏢 Create enterprise-grade Typst engine
    ======================================
    Uses enterprise configuration with all professional features
    """
    if PROFESSIONAL_CONFIG_AVAILABLE:
        from ..core.engine_configuration_protocol import ConfigurationFactory
        config = ConfigurationFactory.create_enterprise_config()
        return TypstEngine(config)
    else:
        return TypstEngine()

def create_typst_engine_with_config(config_name: str) -> TypstEngine:
    """
    ⚙️ Create Typst engine with named configuration
    ===============================================
    
    Args:
        config_name: Configuration name ('fast', 'quality', 'enterprise')
        
    Returns:
        Configured TypstEngine instance
    """
    if PROFESSIONAL_CONFIG_AVAILABLE:
        config_manager = get_config_manager()
        config = config_manager.load_configuration(config_name)
        return TypstEngine(config)
    else:
        return TypstEngine()

def get_typst_engine_info() -> Dict[str, Any]:
    """
    📊 Get comprehensive Typst engine information
    ============================================
    
    Returns system capabilities and configuration status
    """
    return {
        "professional_config_available": PROFESSIONAL_CONFIG_AVAILABLE,
        "professional_engine_available": PROFESSIONAL_ENGINE_AVAILABLE,
        "future_proofing_available": FUTURE_PROOFING_AVAILABLE,
        "unified_optimizer_available": UNIFIED_OPTIMIZER_AVAILABLE,
        "recommended_configuration": "enterprise" if PROFESSIONAL_CONFIG_AVAILABLE else "legacy",
        "factory_functions": [
            "create_fast_typst_engine",
            "create_quality_typst_engine", 
            "create_enterprise_typst_engine",
            "create_typst_engine_with_config"
        ]
    }

# Legacy compatibility
def create_default_typst_engine() -> TypstEngine:
    """Legacy function for backward compatibility"""
    return TypstEngine()

# Export for convenience
__all__ = [
    'TypstEngine',
    'create_fast_typst_engine',
    'create_quality_typst_engine',
    'create_enterprise_typst_engine',
    'create_typst_engine_with_config',
    'get_typst_engine_info',
    'create_default_typst_engine'
]
