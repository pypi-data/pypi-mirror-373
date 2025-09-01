#!/usr/bin/env python3
"""
🏗️ UNIFIED CONTENT PROCESSOR FACTORY
====================================
🎯 Professional factory pattern for content processing

Enterprise-grade factory implementation that provides:
- Dependency injection for optimizer selection  
- Configuration-driven processor creation
- Performance monitoring and metrics
- Extensible architecture for future processors
"""

import logging
from typing import Dict, Type, Optional, Protocol, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

# Import existing optimizers
try:
    from .typst_optimizers.advanced_engine import AdvancedTypstEngine
    from .typst_optimizers.core_optimizer import CoreTypstOptimizer
    from .typst_optimizers import OptimizationConfig, OptimizationResult
    TYPST_OPTIMIZERS_AVAILABLE = True
except ImportError:
    try:
        from ..core.typst_optimizers.advanced_engine import AdvancedTypstEngine
        from ..core.typst_optimizers.core_optimizer import CoreTypstOptimizer
        from ..core.typst_optimizers import OptimizationConfig, OptimizationResult
        TYPST_OPTIMIZERS_AVAILABLE = True
    except ImportError:
        TYPST_OPTIMIZERS_AVAILABLE = False

try:
    from ..engines.reportlab_advanced_features import ReportLabContentOptimizer
    REPORTLAB_OPTIMIZER_AVAILABLE = True
except ImportError:
    REPORTLAB_OPTIMIZER_AVAILABLE = False

class ProcessorType(Enum):
    """Supported processor types"""
    TYPST_BASIC = "typst_basic"
    TYPST_ADVANCED = "typst_advanced" 
    REPORTLAB_BASIC = "reportlab_basic"
    REPORTLAB_ADVANCED = "reportlab_advanced"
    UNIFIED_HYBRID = "unified_hybrid"

class ProcessingMode(Enum):
    """Content processing modes"""
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"
    ENTERPRISE = "enterprise"

@dataclass
class ProcessorConfig:
    """Configuration for content processors"""
    processor_type: ProcessorType
    processing_mode: ProcessingMode
    enable_caching: bool = True
    enable_monitoring: bool = True
    cache_size: int = 1000
    debug: bool = False
    custom_options: Dict[str, Any] = None

class ContentProcessor(Protocol):
    """Protocol defining content processor interface"""
    
    def process_content(self, content: str, **kwargs) -> OptimizationResult:
        """Process content and return optimization result"""
        ...
    
    def get_processor_info(self) -> Dict[str, str]:
        """Get processor information"""
        ...

class BaseContentProcessor(ABC):
    """Abstract base class for content processors"""
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def process_content(self, content: str, **kwargs) -> OptimizationResult:
        """Process content - must be implemented by subclasses"""
        pass
    
    @abstractmethod  
    def get_processor_info(self) -> Dict[str, str]:
        """Get processor information - must be implemented by subclasses"""
        pass

class TypstBasicProcessor(BaseContentProcessor):
    """Basic Typst content processor"""
    
    def __init__(self, config: ProcessorConfig):
        super().__init__(config)
        if TYPST_OPTIMIZERS_AVAILABLE:
            opt_config = OptimizationConfig(
                enable_character_processing=True,
                enable_code_block_processing=True,
                enable_structure_optimization=True,
                preserve_formatting=True
            )
            self.optimizer = CoreTypstOptimizer(opt_config)
        else:
            self.optimizer = None
            self.logger.warning("Typst optimizers not available - using fallback")
    
    def process_content(self, content: str, **kwargs) -> OptimizationResult:
        """Process content with basic Typst optimizer"""
        if self.optimizer:
            return self.optimizer.optimize_content(content)
        else:
            # Fallback result
            return OptimizationResult(
                original_content=content,
                optimized_content=content,
                processing_time=0.0,
                success=False,
                warnings=["Typst optimizers not available"],
                optimizations_applied=[],
                file_size_estimate=len(content)
            )
    
    def get_processor_info(self) -> Dict[str, str]:
        """Get processor information"""
        return {
            "name": "Typst Basic Processor",
            "type": "typst_basic",
            "capabilities": "Basic Typst optimization",
            "performance": "Fast",
            "available": str(TYPST_OPTIMIZERS_AVAILABLE)
        }

class TypstAdvancedProcessor(BaseContentProcessor):
    """Advanced Typst content processor with caching"""
    
    def __init__(self, config: ProcessorConfig):
        super().__init__(config)
        if TYPST_OPTIMIZERS_AVAILABLE:
            opt_config = OptimizationConfig(
                enable_character_processing=True,
                enable_code_block_processing=True,
                enable_structure_optimization=True,
                enable_performance_monitoring=True,
                preserve_formatting=True
            )
            self.optimizer = AdvancedTypstEngine(opt_config, cache_size=config.cache_size)
        else:
            self.optimizer = None
            self.logger.warning("Advanced Typst engine not available")
    
    def process_content(self, content: str, **kwargs) -> OptimizationResult:
        """Process content with advanced Typst optimizer"""
        if self.optimizer:
            use_cache = self.config.enable_caching
            return self.optimizer.optimize_content_advanced(content, use_cache=use_cache)
        else:
            # Fallback to basic processing
            return self._fallback_processing(content)
    
    def _fallback_processing(self, content: str) -> OptimizationResult:
        """Fallback processing when advanced engine unavailable"""
        self.logger.info("Using fallback processing")
        return OptimizationResult(
            original_content=content,
            optimized_content=content,
            processing_time=0.0,
            success=False,
            warnings=["Advanced Typst engine not available - using fallback"],
            optimizations_applied=[],
            file_size_estimate=len(content)
        )
    
    def get_processor_info(self) -> Dict[str, str]:
        """Get processor information"""
        return {
            "name": "Typst Advanced Processor", 
            "type": "typst_advanced",
            "capabilities": "Advanced Typst optimization with caching",
            "performance": "High Quality",
            "available": str(TYPST_OPTIMIZERS_AVAILABLE)
        }

class ReportLabProcessor(BaseContentProcessor):
    """ReportLab content processor"""
    
    def __init__(self, config: ProcessorConfig):
        super().__init__(config)
        if REPORTLAB_OPTIMIZER_AVAILABLE:
            self.optimizer = ReportLabContentOptimizer(cache_size=config.cache_size)
        else:
            self.optimizer = None
            self.logger.warning("ReportLab optimizer not available")
    
    def process_content(self, content: str, **kwargs) -> OptimizationResult:
        """Process content with ReportLab optimizer"""
        if self.optimizer:
            use_cache = self.config.enable_caching
            return self.optimizer.optimize_content(content, use_cache=use_cache)
        else:
            return self._fallback_processing(content)
    
    def _fallback_processing(self, content: str) -> OptimizationResult:
        """Fallback processing"""
        return OptimizationResult(
            original_content=content,
            optimized_content=content,
            processing_time=0.0,
            success=False,
            warnings=["ReportLab optimizer not available"],
            optimizations_applied=[],
            file_size_estimate=len(content)
        )
    
    def get_processor_info(self) -> Dict[str, str]:
        """Get processor information"""
        return {
            "name": "ReportLab Processor",
            "type": "reportlab_advanced", 
            "capabilities": "ReportLab content optimization",
            "performance": "Optimized",
            "available": str(REPORTLAB_OPTIMIZER_AVAILABLE)
        }

class HybridProcessor(BaseContentProcessor):
    """Hybrid processor that uses multiple engines"""
    
    def __init__(self, config: ProcessorConfig):
        super().__init__(config)
        self.typst_processor = TypstAdvancedProcessor(config)
        self.reportlab_processor = ReportLabProcessor(config)
    
    def process_content(self, content: str, **kwargs) -> OptimizationResult:
        """Process content using intelligent engine selection"""
        
        # Determine best processor based on content characteristics
        processor = self._select_optimal_processor(content)
        
        result = processor.process_content(content, **kwargs)
        
        # Add hybrid processing metadata
        if hasattr(result, 'optimizations_applied'):
            result.optimizations_applied.append(f"hybrid_selection_{processor.__class__.__name__}")
        
        return result
    
    def _select_optimal_processor(self, content: str) -> BaseContentProcessor:
        """Select optimal processor based on content analysis"""
        
        # Simple heuristics for processor selection
        if any(marker in content for marker in ['#set', '#let', '#import']):
            # Content already contains Typst syntax
            return self.typst_processor
        
        # Check content complexity
        lines = content.split('\n')
        has_tables = any('|' in line for line in lines)
        has_code = any('```' in line for line in lines)
        
        if has_tables or has_code:
            # Complex content - use advanced Typst
            return self.typst_processor
        else:
            # Simple content - can use either, prefer Typst for consistency
            return self.typst_processor
    
    def get_processor_info(self) -> Dict[str, str]:
        """Get processor information"""
        return {
            "name": "Hybrid Processor",
            "type": "unified_hybrid",
            "capabilities": "Intelligent multi-engine content processing",
            "performance": "Adaptive",
            "available": "True"
        }

class UnifiedContentProcessorFactory:
    """
    🏭 UNIFIED CONTENT PROCESSOR FACTORY
    ===================================
    
    Professional factory for creating content processors with:
    - Configuration-driven processor selection
    - Dependency injection support  
    - Performance monitoring integration
    - Extensible architecture
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._processor_registry: Dict[ProcessorType, Type[BaseContentProcessor]] = {
            ProcessorType.TYPST_BASIC: TypstBasicProcessor,
            ProcessorType.TYPST_ADVANCED: TypstAdvancedProcessor,
            ProcessorType.REPORTLAB_BASIC: ReportLabProcessor,
            ProcessorType.REPORTLAB_ADVANCED: ReportLabProcessor, 
            ProcessorType.UNIFIED_HYBRID: HybridProcessor
        }
        
        # Performance tracking
        self.creation_stats = {
            "processors_created": 0,
            "processor_types": {},
            "total_creation_time": 0.0
        }
    
    def create_processor(self, config: ProcessorConfig) -> BaseContentProcessor:
        """
        Create content processor based on configuration
        
        Args:
            config: ProcessorConfig with processor specifications
            
        Returns:
            Configured content processor instance
            
        Raises:
            ValueError: If processor type not supported
        """
        import time
        start_time = time.time()
        
        try:
            processor_class = self._processor_registry.get(config.processor_type)
            
            if not processor_class:
                available_types = list(self._processor_registry.keys())
                raise ValueError(f"Unsupported processor type: {config.processor_type}. "
                               f"Available types: {available_types}")
            
            # Create processor instance
            processor = processor_class(config)
            
            # Update statistics
            creation_time = time.time() - start_time
            self._update_creation_stats(config.processor_type, creation_time)
            
            self.logger.info(f"✅ Created {config.processor_type.value} processor in {creation_time:.3f}s")
            
            return processor
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create processor {config.processor_type}: {e}")
            raise
    
    def create_processor_by_mode(self, mode: ProcessingMode, **kwargs) -> BaseContentProcessor:
        """
        Create processor based on processing mode
        
        Args:
            mode: ProcessingMode (FAST, BALANCED, QUALITY, ENTERPRISE)
            **kwargs: Additional configuration options
            
        Returns:
            Configured processor optimized for the specified mode
        """
        
        if mode == ProcessingMode.FAST:
            config = ProcessorConfig(
                processor_type=ProcessorType.TYPST_BASIC,
                processing_mode=mode,
                enable_caching=True,
                enable_monitoring=False,
                **kwargs
            )
        elif mode == ProcessingMode.BALANCED:
            config = ProcessorConfig(
                processor_type=ProcessorType.TYPST_ADVANCED,
                processing_mode=mode,
                enable_caching=True,
                enable_monitoring=True,
                **kwargs
            )
        elif mode == ProcessingMode.QUALITY:
            config = ProcessorConfig(
                processor_type=ProcessorType.UNIFIED_HYBRID,
                processing_mode=mode,
                enable_caching=True,
                enable_monitoring=True,
                cache_size=2000,
                **kwargs
            )
        elif mode == ProcessingMode.ENTERPRISE:
            config = ProcessorConfig(
                processor_type=ProcessorType.UNIFIED_HYBRID,
                processing_mode=mode,
                enable_caching=True,
                enable_monitoring=True,
                cache_size=5000,
                debug=True,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported processing mode: {mode}")
        
        return self.create_processor(config)
    
    def register_processor(self, processor_type: ProcessorType, processor_class: Type[BaseContentProcessor]):
        """Register custom processor type"""
        self._processor_registry[processor_type] = processor_class
        self.logger.info(f"✅ Registered custom processor: {processor_type}")
    
    def get_available_processors(self) -> Dict[str, Dict[str, str]]:
        """Get information about all available processors"""
        processors_info = {}
        
        for proc_type, proc_class in self._processor_registry.items():
            # Create dummy config to get processor info
            dummy_config = ProcessorConfig(
                processor_type=proc_type,
                processing_mode=ProcessingMode.BALANCED
            )
            
            try:
                processor = proc_class(dummy_config)
                processors_info[proc_type.value] = processor.get_processor_info()
            except Exception as e:
                self.logger.warning(f"Could not get info for {proc_type}: {e}")
                processors_info[proc_type.value] = {
                    "name": proc_type.value,
                    "available": "false",
                    "error": str(e)
                }
        
        return processors_info
    
    def get_creation_stats(self) -> Dict[str, Any]:
        """Get factory performance statistics"""
        return self.creation_stats.copy()
    
    def _update_creation_stats(self, processor_type: ProcessorType, creation_time: float):
        """Update creation statistics"""
        self.creation_stats["processors_created"] += 1
        self.creation_stats["total_creation_time"] += creation_time
        
        type_name = processor_type.value
        if type_name not in self.creation_stats["processor_types"]:
            self.creation_stats["processor_types"][type_name] = 0
        self.creation_stats["processor_types"][type_name] += 1


# Convenience functions
def create_fast_processor(**kwargs) -> BaseContentProcessor:
    """Create processor optimized for speed"""
    factory = UnifiedContentProcessorFactory()
    return factory.create_processor_by_mode(ProcessingMode.FAST, **kwargs)

def create_quality_processor(**kwargs) -> BaseContentProcessor:
    """Create processor optimized for quality"""
    factory = UnifiedContentProcessorFactory()
    return factory.create_processor_by_mode(ProcessingMode.QUALITY, **kwargs)

def create_enterprise_processor(**kwargs) -> BaseContentProcessor:
    """Create processor with enterprise features"""
    factory = UnifiedContentProcessorFactory()
    return factory.create_processor_by_mode(ProcessingMode.ENTERPRISE, **kwargs)

# Global factory instance (singleton pattern)
_global_factory = None

def get_global_factory() -> UnifiedContentProcessorFactory:
    """Get global factory instance"""
    global _global_factory
    if _global_factory is None:
        _global_factory = UnifiedContentProcessorFactory()
    return _global_factory
