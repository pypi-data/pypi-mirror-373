#!/usr/bin/env python3
"""
🔧 TYPST OPTIMIZERS MODULE - INIT
==============================
⚡ Module initialization for modular Typst optimization system
🔷 Provides unified interface to all optimization components
📊 Exports main classes and convenience functions

COMPONENTS:
- CoreTypstOptimizer: Main optimization engine
- AdvancedTypstEngine: Enterprise features with caching
- TypstCharacterHandlers: Character processing and escaping
- CodeBlockProcessors: Language-specific code optimization

Extracted from typst_content_optimizer.py for better modularity.
"""

from .core_optimizer import (
    CoreTypstOptimizer,
    OptimizationResult,
    OptimizationConfig
)

from .advanced_engine import (
    AdvancedTypstEngine,
    CacheEntry,
    PerformanceProfile
)

from .character_handlers import (
    TypstCharacterHandlers,
    CharacterProcessingResult
)

from .code_block_processors import (
    CodeBlockProcessors
)

# Version information
__version__ = "1.0.0"
__author__ = "WOT-PDF Team"

# Main exports
__all__ = [
    # Core optimization
    'CoreTypstOptimizer',
    'OptimizationResult',
    'OptimizationConfig',
    
    # Advanced engine
    'AdvancedTypstEngine',
    'CacheEntry',
    'PerformanceProfile',
    
    # Character handling
    'TypstCharacterHandlers',
    'CharacterProcessingResult',
    
    # Code processing
    'CodeBlockProcessors',
    
    # Convenience functions
    'create_default_optimizer',
    'create_advanced_optimizer',
    'optimize_text_content',
    'optimize_markdown_content',
]


def create_default_optimizer(debug_mode: bool = False) -> CoreTypstOptimizer:
    """
    Create a default Typst optimizer with standard configuration.
    
    Args:
        debug_mode: Enable debug logging
        
    Returns:
        Configured CoreTypstOptimizer instance
    """
    config = OptimizationConfig(
        enable_character_processing=True,
        enable_code_block_processing=True,
        enable_structure_optimization=True,
        enable_performance_monitoring=True,
        debug_mode=debug_mode
    )
    return CoreTypstOptimizer(config)


def create_advanced_optimizer(cache_size: int = 1000, 
                             debug_mode: bool = False) -> AdvancedTypstEngine:
    """
    Create an advanced Typst optimizer with enterprise features.
    
    Args:
        cache_size: Size of optimization cache
        debug_mode: Enable debug logging
        
    Returns:
        Configured AdvancedTypstEngine instance
    """
    config = OptimizationConfig(
        enable_character_processing=True,
        enable_code_block_processing=True,
        enable_structure_optimization=True,
        enable_performance_monitoring=True,
        debug_mode=debug_mode
    )
    return AdvancedTypstEngine(config, cache_size)


def optimize_text_content(content: str, 
                         use_advanced: bool = False,
                         use_cache: bool = True) -> OptimizationResult:
    """
    Convenience function to optimize text content.
    
    Args:
        content: Text content to optimize
        use_advanced: Use advanced engine with caching
        use_cache: Enable caching (only for advanced engine)
        
    Returns:
        OptimizationResult with processed content
    """
    if use_advanced:
        optimizer = create_advanced_optimizer()
        return optimizer.optimize_content_advanced(content, use_cache)
    else:
        optimizer = create_default_optimizer()
        return optimizer.optimize_content(content)


def optimize_markdown_content(content: str,
                             preserve_formatting: bool = True,
                             use_advanced: bool = True) -> OptimizationResult:
    """
    Convenience function specifically for Markdown content optimization.
    
    Args:
        content: Markdown content to optimize
        preserve_formatting: Preserve original formatting
        use_advanced: Use advanced engine
        
    Returns:
        OptimizationResult with processed content
    """
    config = OptimizationConfig(
        enable_character_processing=True,
        enable_code_block_processing=True,
        enable_structure_optimization=True,
        enable_performance_monitoring=True,
        preserve_formatting=preserve_formatting
    )
    
    if use_advanced:
        optimizer = AdvancedTypstEngine(config)
        return optimizer.optimize_content_advanced(content)
    else:
        optimizer = CoreTypstOptimizer(config)
        return optimizer.optimize_content(content)


# Module-level convenience instances (lazy-loaded)
_default_optimizer = None
_advanced_optimizer = None


def get_default_optimizer() -> CoreTypstOptimizer:
    """Get shared default optimizer instance (singleton pattern)."""
    global _default_optimizer
    if _default_optimizer is None:
        _default_optimizer = create_default_optimizer()
    return _default_optimizer


def get_advanced_optimizer() -> AdvancedTypstEngine:
    """Get shared advanced optimizer instance (singleton pattern)."""
    global _advanced_optimizer
    if _advanced_optimizer is None:
        _advanced_optimizer = create_advanced_optimizer()
    return _advanced_optimizer


def reset_optimizers() -> None:
    """Reset shared optimizer instances."""
    global _default_optimizer, _advanced_optimizer
    _default_optimizer = None
    _advanced_optimizer = None
