#!/usr/bin/env python3
"""
🎯 TYPST ENGINE v2.0 - PROFESSIONAL ARCHITECTURE
================================================
🏗️ Enterprise-grade Typst engine with advanced configuration management

ARCHITECTURE ENHANCEMENTS:
- Dependency injection for configuration management
- Professional error handling and recovery
- Performance monitoring and metrics
- Modular content processing pipeline  
- Extensible template management system
"""

import os
import subprocess
import tempfile
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Protocol
from datetime import datetime
from dataclasses import dataclass

# Import professional configuration system
try:
    from ..core.engine_configuration_protocol import (
        EngineConfiguration, 
        ConfigurationManager, 
        EngineType,
        get_config_manager
    )
    CONFIGURATION_SYSTEM_AVAILABLE = True
except ImportError:
    CONFIGURATION_SYSTEM_AVAILABLE = False

# Import existing systems
try:
    from ..core.future_proofing_system import FutureProofingSystem
    FUTURE_PROOFING_AVAILABLE = True
except ImportError:
    FUTURE_PROOFING_AVAILABLE = False

# Import content optimizers (with fallback chain)
try:
    from ..core.unified_typst_content_optimizer import UnifiedTypstContentOptimizer
    UNIFIED_OPTIMIZER_AVAILABLE = True
except ImportError:
    try:
        from ..core.typst_content_optimizer import TypstContentOptimizer
        UNIFIED_OPTIMIZER_AVAILABLE = False
    except ImportError:
        UNIFIED_OPTIMIZER_AVAILABLE = None

@dataclass
class CompilationMetrics:
    """Compilation performance metrics"""
    content_length: int
    processing_time_ms: float
    compilation_time_ms: float
    total_time_ms: float
    optimizer_used: str
    template_used: str
    cache_hit: bool = False
    warnings: list[str] = None
    file_size_bytes: int = 0
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

@dataclass
class CompilationResult:
    """Comprehensive compilation result"""
    success: bool
    output_file: Optional[Path] = None
    error_message: Optional[str] = None
    metrics: Optional[CompilationMetrics] = None
    typst_source_file: Optional[Path] = None
    stderr_output: Optional[str] = None
    stdout_output: Optional[str] = None

class ContentProcessorProtocol(Protocol):
    """Protocol for content processors"""
    def process_content(self, content: str, template_type: str = "technical") -> str:
        """Process content for Typst compilation"""
        ...

class TypstEngineV2:
    """
    🎯 TYPST ENGINE V2.0 - PROFESSIONAL ARCHITECTURE
    ================================================
    
    Enterprise-grade Typst PDF generation engine featuring:
    - Configuration-driven architecture
    - Professional error handling
    - Performance monitoring
    - Modular content processing
    - Extensible template system
    """
    
    def __init__(self, config: Optional[EngineConfiguration] = None):
        """
        Initialize Typst Engine with professional configuration
        
        Args:
            config: Optional EngineConfiguration. If None, uses default quality config
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize configuration management
        self.config_manager = get_config_manager() if CONFIGURATION_SYSTEM_AVAILABLE else None
        self.config = config or self._get_default_config()
        
        # Initialize base systems
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = self.base_dir / "templates"
        
        # Initialize performance tracking
        self.compilation_stats = {
            "total_compilations": 0,
            "successful_compilations": 0,
            "failed_compilations": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "cache_hits": 0
        }
        
        # Initialize systems based on configuration
        self._initialize_future_proofing()
        self._initialize_content_processor()
        
        # System capability checks
        self.typst_available = self._check_typst_cli()
        
        self.logger.info(f"🎯 Typst Engine v2.0 initialized with {self.config.engine_type.value} configuration")
    
    def _get_default_config(self) -> EngineConfiguration:
        """Get default configuration"""
        if CONFIGURATION_SYSTEM_AVAILABLE:
            return self.config_manager.load_configuration("quality")
        else:
            # Fallback configuration
            return self._create_fallback_config()
    
    def _create_fallback_config(self) -> EngineConfiguration:
        """Create fallback configuration when config system unavailable"""
        # Create a simple config-like object
        class FallbackConfig:
            def __init__(self):
                self.engine_type = "typst"
                self.debug = False
                self.performance = type('obj', (object,), {
                    'enable_caching': True,
                    'timeout_seconds': 300
                })()
                self.typst_config = type('obj', (object,), {
                    'template': 'technical',
                    'enable_future_proofing': True,
                    'use_unified_optimizer': True,
                    'skip_content_optimization': False
                })()
        
        return FallbackConfig()
    
    def _initialize_future_proofing(self):
        """Initialize future-proofing system"""
        if FUTURE_PROOFING_AVAILABLE and getattr(self.config.typst_config, 'enable_future_proofing', True):
            try:
                self.future_proofing = FutureProofingSystem()
                self.logger.info("🛡️ Future-proofing system enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize future-proofing: {e}")
                self.future_proofing = None
        else:
            self.future_proofing = None
            self.logger.info("🔧 Future-proofing system disabled by configuration")
    
    def _initialize_content_processor(self):
        """Initialize content processor based on configuration"""
        use_unified = getattr(self.config.typst_config, 'use_unified_optimizer', True)
        
        if use_unified and UNIFIED_OPTIMIZER_AVAILABLE is True:
            self.content_processor = UnifiedTypstContentOptimizer(debug=self.config.debug)
            self.processor_type = "unified"
            self.logger.info("🚀 Unified content optimizer enabled")
        elif UNIFIED_OPTIMIZER_AVAILABLE is False:
            self.content_processor = TypstContentOptimizer()
            self.processor_type = "legacy"
            self.logger.info("⚙️ Legacy content optimizer enabled")
        else:
            self.content_processor = None
            self.processor_type = "none"
            self.logger.warning("⚠️ No content optimizer available")
    
    def _check_typst_cli(self) -> bool:
        """Enhanced Typst CLI availability check"""
        try:
            result = subprocess.run(
                ["typst", "--version"], 
                capture_output=True, 
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.strip()
                self.logger.info(f"✅ Typst CLI available: {version_info}")
                return True
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Typst CLI check timeout")
        except FileNotFoundError:
            self.logger.error("❌ Typst CLI not found in PATH")
        except Exception as e:
            self.logger.error(f"❌ Typst CLI check failed: {e}")
        
        return False
    
    def generate(self, 
                 content: str,
                 output_file: Path,
                 template: Optional[str] = None,
                 **kwargs) -> CompilationResult:
        """
        🎯 PROFESSIONAL PDF GENERATION
        ==============================
        
        Generate PDF with comprehensive error handling and metrics
        
        Args:
            content: Markdown content to convert
            output_file: Path for output PDF
            template: Template name (uses config default if None)
            **kwargs: Additional options
            
        Returns:
            CompilationResult with detailed metrics and status
        """
        start_time = time.time()
        
        # Initialize metrics
        metrics = CompilationMetrics(
            content_length=len(content),
            processing_time_ms=0.0,
            compilation_time_ms=0.0,
            total_time_ms=0.0,
            optimizer_used=self.processor_type,
            template_used=template or getattr(self.config.typst_config, 'template', 'technical')
        )
        
        try:
            # Pre-flight checks
            preflight_result = self._preflight_checks(content, output_file)
            if not preflight_result[0]:
                return CompilationResult(
                    success=False,
                    error_message=preflight_result[1],
                    metrics=metrics
                )
            
            # Content processing
            processing_start = time.time()
            typst_content = self._process_content_professional(content, template or metrics.template_used, **kwargs)
            metrics.processing_time_ms = (time.time() - processing_start) * 1000
            
            # Compilation
            compilation_start = time.time()
            compilation_result = self._compile_with_professional_handling(typst_content, output_file, metrics)
            metrics.compilation_time_ms = (time.time() - compilation_start) * 1000
            
            # Finalize metrics
            metrics.total_time_ms = (time.time() - start_time) * 1000
            compilation_result.metrics = metrics
            
            # Update statistics
            self._update_compilation_stats(compilation_result)
            
            return compilation_result
            
        except Exception as e:
            self.logger.error(f"❌ Compilation failed with exception: {e}")
            metrics.total_time_ms = (time.time() - start_time) * 1000
            
            result = CompilationResult(
                success=False,
                error_message=f"Compilation exception: {str(e)}",
                metrics=metrics
            )
            
            self._update_compilation_stats(result)
            return result
    
    def _preflight_checks(self, content: str, output_file: Path) -> tuple[bool, Optional[str]]:
        """Comprehensive pre-flight validation"""
        
        # Check Typst CLI availability
        if not self.typst_available:
            return False, "Typst CLI not available"
        
        # Validate content
        if not content.strip():
            return False, "Content cannot be empty"
        
        # Validate output path
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Cannot create output directory: {e}"
        
        # Check content length
        if len(content) > 10_000_000:  # 10MB limit
            return False, "Content exceeds maximum size limit (10MB)"
        
        return True, None
    
    def _process_content_professional(self, content: str, template: str, **kwargs) -> str:
        """Professional content processing with error handling"""
        
        # Check if optimization should be skipped
        if getattr(self.config.typst_config, 'skip_content_optimization', False):
            self.logger.info("🔄 Content optimization skipped by configuration")
            typst_content = content
        elif self.content_processor:
            # Use available content processor
            if hasattr(self.content_processor, 'optimize_content_for_typst'):
                # Unified optimizer
                typst_content = self.content_processor.optimize_content_for_typst(content, template)
            elif hasattr(self.content_processor, 'optimize_content'):
                # Legacy optimizer
                typst_content = self.content_processor.optimize_content(content)
            else:
                # Fallback
                typst_content = content
                self.logger.warning("⚠️ Content processor has no optimization method")
        else:
            # No processor available - use basic conversion
            typst_content = self._basic_markdown_conversion(content)
        
        # Apply template
        full_content = self._apply_template_professional(typst_content, template, **kwargs)
        
        return full_content
    
    def _apply_template_professional(self, content: str, template: str, **kwargs) -> str:
        """Professional template application with validation"""
        
        try:
            # Get template content
            typst_template = self._get_template_professional(template)
            
            # Prepare metadata
            metadata = {
                'title': kwargs.get('title', 'Document'),
                'author': kwargs.get('author', 'Generated by WOT-PDF'),
                'date': datetime.now().strftime("%B %d, %Y")
            }
            
            # Apply template
            header = typst_template.format(**metadata)
            full_content = header + "\n\n" + content
            
            self.logger.debug(f"✅ Applied template '{template}' successfully")
            return full_content
            
        except Exception as e:
            self.logger.warning(f"⚠️ Template application failed: {e}. Using minimal template.")
            return self._get_minimal_template().format(
                title=kwargs.get('title', 'Document'),
                author=kwargs.get('author', 'Generated by WOT-PDF'),
                date=datetime.now().strftime("%B %d, %Y")
            ) + "\n\n" + content
    
    def _compile_with_professional_handling(self, typst_content: str, output_file: Path, metrics: CompilationMetrics) -> CompilationResult:
        """Professional compilation with comprehensive error handling"""
        
        # Create temporary file for Typst source
        with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', encoding='utf-8', delete=False) as temp_file:
            temp_file.write(typst_content)
            temp_typst_file = Path(temp_file.name)
        
        try:
            # Execute Typst compilation
            timeout = getattr(self.config.performance, 'timeout_seconds', 300)
            
            result = subprocess.run([
                'typst', 'compile', str(temp_typst_file), str(output_file)
            ], 
            capture_output=True, 
            encoding='utf-8',
            errors='replace',
            timeout=timeout
            )
            
            # Analyze compilation result
            if result.returncode == 0:
                # Success
                file_size = output_file.stat().st_size if output_file.exists() else 0
                metrics.file_size_bytes = file_size
                
                self.logger.info(f"✅ Compilation successful: {file_size} bytes")
                
                return CompilationResult(
                    success=True,
                    output_file=output_file,
                    typst_source_file=temp_typst_file,
                    stdout_output=result.stdout
                )
            else:
                # Compilation error
                error_msg = result.stderr.strip() if result.stderr else "Unknown compilation error"
                
                self.logger.error(f"❌ Compilation failed: {error_msg}")
                
                return CompilationResult(
                    success=False,
                    error_message=f"Typst compilation failed: {error_msg}",
                    typst_source_file=temp_typst_file,
                    stderr_output=result.stderr,
                    stdout_output=result.stdout
                )
                
        except subprocess.TimeoutExpired:
            error_msg = f"Compilation timeout ({timeout} seconds)"
            self.logger.error(f"❌ {error_msg}")
            
            return CompilationResult(
                success=False,
                error_message=error_msg,
                typst_source_file=temp_typst_file
            )
        except Exception as e:
            error_msg = f"Compilation process error: {e}"
            self.logger.error(f"❌ {error_msg}")
            
            return CompilationResult(
                success=False,
                error_message=error_msg,
                typst_source_file=temp_typst_file
            )
        finally:
            # Cleanup temporary file unless debug mode
            if not self.config.debug:
                try:
                    temp_typst_file.unlink(missing_ok=True)
                except Exception:
                    pass
    
    def _update_compilation_stats(self, result: CompilationResult):
        """Update compilation statistics"""
        self.compilation_stats["total_compilations"] += 1
        
        if result.success:
            self.compilation_stats["successful_compilations"] += 1
        else:
            self.compilation_stats["failed_compilations"] += 1
        
        if result.metrics:
            self.compilation_stats["total_processing_time"] += result.metrics.total_time_ms
            
            # Update average
            self.compilation_stats["average_processing_time"] = (
                self.compilation_stats["total_processing_time"] / 
                self.compilation_stats["total_compilations"]
            )
            
            if result.metrics.cache_hit:
                self.compilation_stats["cache_hits"] += 1
    
    def _get_template_professional(self, template: str) -> str:
        """Professional template loading with fallbacks"""
        
        # Check for custom template path first
        custom_path = getattr(self.config.typst_config, 'custom_template_path', None)
        if custom_path and custom_path.exists():
            try:
                return custom_path.read_text(encoding='utf-8')
            except Exception as e:
                self.logger.warning(f"Failed to load custom template: {e}")
        
        # Standard template locations
        template_locations = [
            self.templates_dir / f"{template}.typ",
            self.base_dir.parent / "templates" / f"{template}.typ"
        ]
        
        for template_file in template_locations:
            if template_file.exists():
                try:
                    return template_file.read_text(encoding='utf-8')
                except Exception as e:
                    self.logger.warning(f"Failed to load template {template_file}: {e}")
        
        # Fallback to inline templates
        return self._get_inline_template(template)
    
    def _get_inline_template(self, template_name: str) -> str:
        """Enhanced inline templates"""
        templates = {
            "minimal": '''#set document(title: "{title}", author: "{author}")
#set page(paper: "a4", margin: 2.5cm, numbering: "1")
#set text(font: "Arial", size: 11pt)

#align(center)[#text(size: 16pt, weight: "bold")[{title}]]
#align(center)[#text(size: 10pt)[{author} | {date}]]
#v(1em)''',

            "technical": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  numbering: "1",
  number-align: center,
)

#set text(font: "New Computer Modern", size: 11pt, lang: "en")
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

#set text(font: "Times New Roman", size: 12pt)
#set heading(numbering: "1.")
#set par(justify: true, first-line-indent: 1.25cm, leading: 0.8em)

#align(center)[
  #text(size: 18pt, weight: "bold")[{title}]
  #v(1em)
  #text(size: 14pt)[{author}]
  #v(0.5em)
  #text(size: 11pt)[{date}]
]
#v(2em)'''
        }
        
        return templates.get(template_name, templates["technical"])
    
    def _get_minimal_template(self) -> str:
        """Get minimal safe template for error recovery"""
        return '''#set document(title: "{title}", author: "{author}")
#set page(paper: "a4", margin: 2cm)
#set text(size: 11pt)
#align(center)[{title}]
#align(center)[{author} | {date}]
#v(1em)'''
    
    def _basic_markdown_conversion(self, content: str) -> str:
        """Basic markdown to Typst conversion as final fallback"""
        import re
        
        # Headers
        content = re.sub(r'^# (.+)$', r'= \1', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'== \1', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'=== \1', content, flags=re.MULTILINE)
        
        # Bold and italic
        content = re.sub(r'\*\*(.+?)\*\*', r'*\1*', content)
        content = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', content)
        
        # Code blocks  
        content = re.sub(r'```(\w+)?\n(.*?)```', r'```\1\n\2```', content, flags=re.DOTALL)
        
        return content
    
    def get_compilation_stats(self) -> Dict[str, Any]:
        """Get compilation statistics"""
        return self.compilation_stats.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "engine_version": "2.0",
            "typst_available": self.typst_available,
            "future_proofing_enabled": self.future_proofing is not None,
            "content_processor": self.processor_type,
            "configuration_system": CONFIGURATION_SYSTEM_AVAILABLE,
            "compilation_stats": self.get_compilation_stats()
        }

# Convenience functions for backward compatibility
class TypstEngine(TypstEngineV2):
    """Backward compatibility alias"""
    pass

def create_typst_engine(config_name: str = "quality") -> TypstEngineV2:
    """Create Typst engine with named configuration"""
    if CONFIGURATION_SYSTEM_AVAILABLE:
        config_manager = get_config_manager()
        config = config_manager.load_configuration(config_name)
        return TypstEngineV2(config)
    else:
        return TypstEngineV2()

def create_enterprise_typst_engine() -> TypstEngineV2:
    """Create enterprise-grade Typst engine"""
    return create_typst_engine("enterprise")
