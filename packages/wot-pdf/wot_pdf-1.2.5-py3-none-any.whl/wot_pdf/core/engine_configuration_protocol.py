#!/usr/bin/env python3
"""
🎯 ENGINE CONFIGURATION PROTOCOL
================================
🏗️ Professional configuration system for WOT-PDF engines

This module provides enterprise-grade configuration management:
- Type-safe configuration protocols
- Validation and error handling  
- Performance optimization settings
- Extensible configuration architecture
"""

import logging
from typing import Dict, Any, Optional, Protocol, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class EngineType(Enum):
    """Supported engine types"""
    TYPST = "typst"
    REPORTLAB = "reportlab" 
    HYBRID = "hybrid"

class ProcessingQuality(Enum):
    """Processing quality levels"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"

class OptimizationLevel(Enum):
    """Content optimization levels"""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    enable_caching: bool = True
    cache_size: int = 1000
    enable_parallel_processing: bool = False
    max_workers: int = 4
    timeout_seconds: int = 300
    memory_limit_mb: Optional[int] = None

@dataclass  
class ContentOptimizationConfig:
    """Content optimization settings"""
    optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    preserve_formatting: bool = True
    enable_character_processing: bool = True
    enable_code_block_processing: bool = True
    enable_table_processing: bool = True
    enable_structure_optimization: bool = True

@dataclass
class TypstEngineConfig:
    """Typst-specific engine configuration"""
    template: str = "technical"
    enable_future_proofing: bool = True
    compilation_timeout: int = 300
    use_unified_optimizer: bool = True
    skip_content_optimization: bool = False
    custom_template_path: Optional[Path] = None

@dataclass
class ReportLabEngineConfig:
    """ReportLab-specific engine configuration"""
    page_format: str = "A4"
    enable_advanced_features: bool = True
    font_config: Dict[str, str] = field(default_factory=dict)
    style_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EngineConfiguration:
    """
    🎯 MASTER ENGINE CONFIGURATION
    =============================
    
    Comprehensive configuration for WOT-PDF engine system.
    Provides type-safe, validated configuration management.
    """
    
    # Core settings
    engine_type: EngineType = EngineType.TYPST
    processing_quality: ProcessingQuality = ProcessingQuality.STANDARD
    debug: bool = False
    
    # Performance settings  
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Content optimization
    content_optimization: ContentOptimizationConfig = field(default_factory=ContentOptimizationConfig)
    
    # Engine-specific settings
    typst_config: TypstEngineConfig = field(default_factory=TypstEngineConfig)
    reportlab_config: ReportLabEngineConfig = field(default_factory=ReportLabEngineConfig)
    
    # Output settings
    output_format: str = "pdf"
    output_quality: str = "high"
    
    # Metadata
    document_title: str = "Generated Document"
    document_author: str = "WOT-PDF System"
    
    # Custom options
    custom_options: Dict[str, Any] = field(default_factory=dict)

class EngineConfigurationProtocol(Protocol):
    """Protocol defining engine configuration interface"""
    
    def validate_configuration(self) -> bool:
        """Validate configuration settings"""
        ...
    
    def get_optimization_settings(self) -> Dict[str, Any]:
        """Get optimization settings for the engine"""
        ...
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance settings"""
        ...

class ConfigurationValidator:
    """
    🔍 CONFIGURATION VALIDATOR  
    ===========================
    
    Professional validation system for engine configurations.
    Ensures configuration integrity and provides helpful error messages.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_configuration(self, config: EngineConfiguration) -> tuple[bool, list[str]]:
        """
        Validate complete engine configuration
        
        Args:
            config: EngineConfiguration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate core settings
        errors.extend(self._validate_core_settings(config))
        
        # Validate performance settings
        errors.extend(self._validate_performance_settings(config.performance))
        
        # Validate content optimization settings
        errors.extend(self._validate_content_settings(config.content_optimization))
        
        # Validate engine-specific settings
        if config.engine_type == EngineType.TYPST:
            errors.extend(self._validate_typst_settings(config.typst_config))
        elif config.engine_type == EngineType.REPORTLAB:
            errors.extend(self._validate_reportlab_settings(config.reportlab_config))
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("✅ Configuration validation passed")
        else:
            self.logger.warning(f"⚠️ Configuration validation failed with {len(errors)} errors")
            for error in errors:
                self.logger.warning(f"  - {error}")
        
        return is_valid, errors
    
    def _validate_core_settings(self, config: EngineConfiguration) -> list[str]:
        """Validate core configuration settings"""
        errors = []
        
        # Validate engine type
        if not isinstance(config.engine_type, EngineType):
            errors.append("Invalid engine_type - must be EngineType enum")
        
        # Validate processing quality
        if not isinstance(config.processing_quality, ProcessingQuality):
            errors.append("Invalid processing_quality - must be ProcessingQuality enum")
        
        # Validate output format
        valid_formats = ["pdf", "png", "svg"]
        if config.output_format not in valid_formats:
            errors.append(f"Invalid output_format '{config.output_format}' - must be one of {valid_formats}")
        
        return errors
    
    def _validate_performance_settings(self, performance: PerformanceConfig) -> list[str]:
        """Validate performance configuration"""
        errors = []
        
        # Validate cache size
        if performance.cache_size < 0:
            errors.append("cache_size must be non-negative")
        elif performance.cache_size > 10000:
            errors.append("cache_size exceeds recommended maximum of 10000")
        
        # Validate worker count
        if performance.max_workers < 1:
            errors.append("max_workers must be at least 1")
        elif performance.max_workers > 16:
            errors.append("max_workers exceeds recommended maximum of 16")
        
        # Validate timeout
        if performance.timeout_seconds < 10:
            errors.append("timeout_seconds must be at least 10 seconds")
        elif performance.timeout_seconds > 3600:
            errors.append("timeout_seconds exceeds maximum of 1 hour")
        
        # Validate memory limit
        if performance.memory_limit_mb is not None:
            if performance.memory_limit_mb < 100:
                errors.append("memory_limit_mb must be at least 100MB")
            elif performance.memory_limit_mb > 16384:
                errors.append("memory_limit_mb exceeds recommended maximum of 16GB")
        
        return errors
    
    def _validate_content_settings(self, content: ContentOptimizationConfig) -> list[str]:
        """Validate content optimization settings"""
        errors = []
        
        # Validate optimization level
        if not isinstance(content.optimization_level, OptimizationLevel):
            errors.append("Invalid optimization_level - must be OptimizationLevel enum")
        
        return errors
    
    def _validate_typst_settings(self, typst: TypstEngineConfig) -> list[str]:
        """Validate Typst-specific settings"""
        errors = []
        
        # Validate template
        valid_templates = ["technical", "academic", "business", "educational", "minimal"]
        if typst.template not in valid_templates:
            errors.append(f"Invalid template '{typst.template}' - must be one of {valid_templates}")
        
        # Validate timeout
        if typst.compilation_timeout < 30:
            errors.append("compilation_timeout must be at least 30 seconds")
        elif typst.compilation_timeout > 1800:
            errors.append("compilation_timeout exceeds maximum of 30 minutes")
        
        # Validate custom template path
        if typst.custom_template_path is not None:
            if not typst.custom_template_path.exists():
                errors.append(f"Custom template path does not exist: {typst.custom_template_path}")
        
        return errors
    
    def _validate_reportlab_settings(self, reportlab: ReportLabEngineConfig) -> list[str]:
        """Validate ReportLab-specific settings"""
        errors = []
        
        # Validate page format
        valid_formats = ["A4", "A3", "A5", "Letter", "Legal"]
        if reportlab.page_format not in valid_formats:
            errors.append(f"Invalid page_format '{reportlab.page_format}' - must be one of {valid_formats}")
        
        return errors

class ConfigurationFactory:
    """
    🏭 CONFIGURATION FACTORY
    ========================
    
    Factory for creating pre-configured engine configurations
    based on common use cases and best practices.
    """
    
    @staticmethod
    def create_fast_config() -> EngineConfiguration:
        """Create configuration optimized for speed"""
        return EngineConfiguration(
            engine_type=EngineType.TYPST,
            processing_quality=ProcessingQuality.DRAFT,
            performance=PerformanceConfig(
                enable_caching=True,
                cache_size=500,
                timeout_seconds=120
            ),
            content_optimization=ContentOptimizationConfig(
                optimization_level=OptimizationLevel.BASIC,
                enable_code_block_processing=False,
                enable_table_processing=False
            ),
            typst_config=TypstEngineConfig(
                template="minimal",
                enable_future_proofing=False,
                use_unified_optimizer=False
            )
        )
    
    @staticmethod
    def create_quality_config() -> EngineConfiguration:
        """Create configuration optimized for quality"""
        return EngineConfiguration(
            engine_type=EngineType.TYPST,
            processing_quality=ProcessingQuality.HIGH,
            performance=PerformanceConfig(
                enable_caching=True,
                cache_size=2000,
                timeout_seconds=600
            ),
            content_optimization=ContentOptimizationConfig(
                optimization_level=OptimizationLevel.ADVANCED,
                preserve_formatting=True,
                enable_character_processing=True,
                enable_code_block_processing=True,
                enable_table_processing=True,
                enable_structure_optimization=True
            ),
            typst_config=TypstEngineConfig(
                template="technical",
                enable_future_proofing=True,
                use_unified_optimizer=True
            )
        )
    
    @staticmethod
    def create_enterprise_config() -> EngineConfiguration:
        """Create configuration with enterprise features"""
        return EngineConfiguration(
            engine_type=EngineType.HYBRID,
            processing_quality=ProcessingQuality.PREMIUM,
            debug=True,
            performance=PerformanceConfig(
                enable_caching=True,
                cache_size=5000,
                enable_parallel_processing=True,
                max_workers=8,
                timeout_seconds=900
            ),
            content_optimization=ContentOptimizationConfig(
                optimization_level=OptimizationLevel.ENTERPRISE,
                preserve_formatting=True,
                enable_character_processing=True,
                enable_code_block_processing=True,
                enable_table_processing=True,
                enable_structure_optimization=True
            ),
            typst_config=TypstEngineConfig(
                template="academic",
                enable_future_proofing=True,
                use_unified_optimizer=True
            ),
            reportlab_config=ReportLabEngineConfig(
                enable_advanced_features=True
            )
        )
    
    @staticmethod
    def create_custom_config(**kwargs) -> EngineConfiguration:
        """Create configuration with custom options"""
        # Start with quality config as base
        config = ConfigurationFactory.create_quality_config()
        
        # Apply custom options
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                config.custom_options[key] = value
        
        return config

class ConfigurationManager:
    """
    🎛️ CONFIGURATION MANAGER
    ========================
    
    Centralized management system for engine configurations.
    Handles loading, validation, and caching of configurations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ConfigurationValidator()
        self._config_cache: Dict[str, EngineConfiguration] = {}
    
    def load_configuration(self, config_name: str) -> EngineConfiguration:
        """Load configuration by name"""
        
        # Check cache first
        if config_name in self._config_cache:
            self.logger.debug(f"⚡ Using cached configuration: {config_name}")
            return self._config_cache[config_name]
        
        # Create configuration
        if config_name == "fast":
            config = ConfigurationFactory.create_fast_config()
        elif config_name == "quality":
            config = ConfigurationFactory.create_quality_config()
        elif config_name == "enterprise":
            config = ConfigurationFactory.create_enterprise_config()
        else:
            self.logger.warning(f"Unknown configuration name '{config_name}', using quality config")
            config = ConfigurationFactory.create_quality_config()
        
        # Validate configuration
        is_valid, errors = self.validator.validate_configuration(config)
        if not is_valid:
            self.logger.error(f"❌ Configuration '{config_name}' validation failed")
            for error in errors:
                self.logger.error(f"  - {error}")
            # Return basic safe configuration
            config = ConfigurationFactory.create_fast_config()
        
        # Cache and return
        self._config_cache[config_name] = config
        self.logger.info(f"✅ Loaded configuration: {config_name}")
        
        return config
    
    def validate_and_cache_config(self, config: EngineConfiguration, cache_key: str) -> bool:
        """Validate and cache custom configuration"""
        is_valid, errors = self.validator.validate_configuration(config)
        
        if is_valid:
            self._config_cache[cache_key] = config
            self.logger.info(f"✅ Cached validated configuration: {cache_key}")
        else:
            self.logger.error(f"❌ Configuration validation failed for: {cache_key}")
            for error in errors:
                self.logger.error(f"  - {error}")
        
        return is_valid
    
    def get_optimization_settings(self, config: EngineConfiguration) -> Dict[str, Any]:
        """Extract optimization settings from configuration"""
        return {
            "optimization_level": config.content_optimization.optimization_level.value,
            "preserve_formatting": config.content_optimization.preserve_formatting,
            "enable_character_processing": config.content_optimization.enable_character_processing,
            "enable_code_block_processing": config.content_optimization.enable_code_block_processing,
            "enable_table_processing": config.content_optimization.enable_table_processing,
            "enable_structure_optimization": config.content_optimization.enable_structure_optimization,
            "debug": config.debug
        }
    
    def get_performance_settings(self, config: EngineConfiguration) -> Dict[str, Any]:
        """Extract performance settings from configuration"""
        return {
            "enable_caching": config.performance.enable_caching,
            "cache_size": config.performance.cache_size,
            "enable_parallel_processing": config.performance.enable_parallel_processing,
            "max_workers": config.performance.max_workers,
            "timeout_seconds": config.performance.timeout_seconds,
            "memory_limit_mb": config.performance.memory_limit_mb
        }
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._config_cache.clear()
        self.logger.info("🔄 Configuration cache cleared")

# Global configuration manager instance
_global_config_manager = None

def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager()
    return _global_config_manager

# Convenience functions
def create_fast_config() -> EngineConfiguration:
    """Create fast configuration"""
    return ConfigurationFactory.create_fast_config()

def create_quality_config() -> EngineConfiguration:
    """Create quality configuration"""
    return ConfigurationFactory.create_quality_config()

def create_enterprise_config() -> EngineConfiguration:
    """Create enterprise configuration"""
    return ConfigurationFactory.create_enterprise_config()

def validate_config(config: EngineConfiguration) -> tuple[bool, list[str]]:
    """Validate configuration"""
    validator = ConfigurationValidator()
    return validator.validate_configuration(config)
