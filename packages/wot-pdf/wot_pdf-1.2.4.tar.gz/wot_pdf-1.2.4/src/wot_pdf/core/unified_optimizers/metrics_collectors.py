#!/usr/bin/env python3
"""
🔄 METRICS COLLECTORS
====================
📊 Conversion metrics and statistics collection
📈 Legacy compatibility with ConversionStats

Provides data structures for tracking optimization performance.
"""

from typing import List
from dataclasses import dataclass, field


@dataclass
class ConversionStats:
    """Legacy compatibility - maps to new ConversionMetrics."""
    headers_converted: int = 0
    code_blocks_protected: int = 0
    inline_code_converted: int = 0
    lists_converted: int = 0
    formatting_converted: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class ConversionMetrics:
    """Detailed metrics for conversion process."""
    headers_processed: int = 0
    tables_converted: int = 0
    links_converted: int = 0
    code_blocks_converted: int = 0
    inline_code_processed: int = 0
    build_time_ms: float = 0.0
    success: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class MetricsCollector:
    """Collects and manages conversion metrics."""
    
    def __init__(self):
        self.metrics = ConversionMetrics()
        self.legacy_stats = ConversionStats()
        self.start_time = 0.0
    
    def start_timing(self):
        """Start timing the conversion process."""
        import time
        self.start_time = time.time()
    
    def stop_timing(self):
        """Stop timing and record the duration."""
        if self.start_time > 0:
            import time
            duration = (time.time() - self.start_time) * 1000  # Convert to milliseconds
            self.metrics.build_time_ms = duration
            self.start_time = 0.0
    
    def record_header_processed(self):
        """Record a header being processed."""
        self.metrics.headers_processed += 1
        self.legacy_stats.headers_converted += 1
    
    def record_table_converted(self):
        """Record a table being converted."""
        self.metrics.tables_converted += 1
    
    def record_link_converted(self):
        """Record a link being converted."""
        self.metrics.links_converted += 1
    
    def record_code_block_converted(self):
        """Record a code block being converted."""
        self.metrics.code_blocks_converted += 1
        self.legacy_stats.code_blocks_protected += 1
    
    def record_inline_code_processed(self):
        """Record inline code being processed."""
        self.metrics.inline_code_processed += 1
        self.legacy_stats.inline_code_converted += 1
    
    def record_warning(self, message: str):
        """Record a warning message."""
        self.metrics.warnings.append(message)
        self.legacy_stats.warnings.append(message)
    
    def record_error(self, message: str):
        """Record an error message."""
        self.metrics.errors.append(message)
        self.legacy_stats.errors.append(message)
        self.metrics.success = False
    
    def mark_success(self):
        """Mark the conversion as successful."""
        self.metrics.success = True
    
    def get_metrics(self) -> ConversionMetrics:
        """Get the current metrics."""
        return self.metrics
    
    def get_legacy_stats(self) -> ConversionStats:
        """Get the legacy stats for backward compatibility."""
        return self.legacy_stats
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = ConversionMetrics()
        self.legacy_stats = ConversionStats()
        self.start_time = 0.0
