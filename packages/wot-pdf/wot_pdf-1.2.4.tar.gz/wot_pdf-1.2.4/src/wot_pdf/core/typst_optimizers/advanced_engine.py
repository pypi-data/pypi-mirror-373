#!/usr/bin/env python3
"""
🔧 ADVANCED TYPST ENGINE - ENTERPRISE OPTIMIZATION
===============================================
⚡ Advanced optimization algorithms and enterprise features
🔷 High-performance processing for complex documents
📊 Advanced metrics, caching, and performance optimization

FEATURES:
- Advanced optimization algorithms
- Content caching and memoization
- Performance profiling and metrics
- Enterprise-grade error handling
- Batch processing capabilities

Extracted from typst_content_optimizer.py for better modularity.
"""

import logging
import time
import hashlib
import pickle
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Import core components
from .core_optimizer import CoreTypstOptimizer, OptimizationResult, OptimizationConfig


@dataclass
class CacheEntry:
    """Cache entry for optimization results."""
    content_hash: str
    result: OptimizationResult
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)


@dataclass
class PerformanceProfile:
    """Performance profiling data."""
    operation_name: str
    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    cache_hits: int = 0
    cache_misses: int = 0


class AdvancedTypstEngine:
    """
    Advanced Typst optimization engine with enterprise features.
    Provides caching, performance profiling, and batch processing.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None, cache_size: int = 1000):
        """
        Initialize advanced engine.
        
        Args:
            config: Optimization configuration
            cache_size: Maximum number of cached results
        """
        self.config = config or OptimizationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize core optimizer
        self.core_optimizer = CoreTypstOptimizer(self.config)
        
        # Caching system
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_size = cache_size
        self.cache_lock = threading.RLock()
        
        # Performance tracking
        self.performance_profiles: List[PerformanceProfile] = []
        self.performance_lock = threading.RLock()
        
        # Advanced statistics
        self.advanced_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_cache_saves': 0,
            'average_optimization_time': 0.0,
            'peak_memory_usage': 0.0,
            'concurrent_operations': 0,
            'max_concurrent_operations': 0,
        }
        
        self.logger.info("🚀 Advanced Typst Engine initialized with enterprise features")
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash for content caching."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _get_cached_result(self, content_hash: str) -> Optional[OptimizationResult]:
        """
        Retrieve cached optimization result.
        
        Args:
            content_hash: Hash of content to look up
            
        Returns:
            Cached result if found, None otherwise
        """
        with self.cache_lock:
            if content_hash in self.cache:
                cache_entry = self.cache[content_hash]
                cache_entry.access_count += 1
                cache_entry.last_access = time.time()
                self.advanced_stats['cache_hits'] += 1
                return cache_entry.result
            else:
                self.advanced_stats['cache_misses'] += 1
                return None
    
    def _cache_result(self, content_hash: str, result: OptimizationResult) -> None:
        """
        Cache optimization result.
        
        Args:
            content_hash: Hash of content
            result: Optimization result to cache
        """
        with self.cache_lock:
            # Check if cache is full and needs cleanup
            if len(self.cache) >= self.cache_size:
                self._cleanup_cache()
            
            # Add new cache entry
            cache_entry = CacheEntry(
                content_hash=content_hash,
                result=result,
                timestamp=time.time()
            )
            self.cache[content_hash] = cache_entry
            self.advanced_stats['total_cache_saves'] += 1
    
    def _cleanup_cache(self) -> None:
        """Clean up cache by removing least recently used entries."""
        if not self.cache:
            return
        
        # Sort by last access time (oldest first)
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_access
        )
        
        # Remove oldest 25% of entries
        entries_to_remove = len(sorted_entries) // 4
        for content_hash, _ in sorted_entries[:entries_to_remove]:
            del self.cache[content_hash]
        
        self.logger.debug(f"🗑️ Cleaned up {entries_to_remove} cache entries")
    
    def _profile_operation(self, operation_name: str, operation_func: Callable) -> Any:
        """
        Profile operation performance.
        
        Args:
            operation_name: Name of operation being profiled
            operation_func: Function to profile
            
        Returns:
            Result of operation function
        """
        start_time = time.time()
        
        try:
            # Execute operation
            result = operation_func()
            execution_time = time.time() - start_time
            
            # Create performance profile
            profile = PerformanceProfile(
                operation_name=operation_name,
                execution_time=execution_time
            )
            
            # Store profile
            with self.performance_lock:
                self.performance_profiles.append(profile)
                
                # Keep only recent profiles (last 1000)
                if len(self.performance_profiles) > 1000:
                    self.performance_profiles = self.performance_profiles[-1000:]
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Operation {operation_name} failed after {execution_time:.3f}s: {e}")
            raise
    
    def optimize_content_advanced(self, content: str, use_cache: bool = True) -> OptimizationResult:
        """
        Advanced content optimization with caching and profiling.
        
        Args:
            content: Content to optimize
            use_cache: Whether to use caching
            
        Returns:
            OptimizationResult with enhanced metadata
        """
        def optimize_operation():
            # Check cache first
            if use_cache:
                content_hash = self._calculate_content_hash(content)
                cached_result = self._get_cached_result(content_hash)
                if cached_result is not None:
                    self.logger.debug("⚡ Using cached optimization result")
                    return cached_result
            
            # Perform optimization
            result = self.core_optimizer.optimize_content(content)
            
            # Cache result if successful
            if use_cache and result.success:
                content_hash = self._calculate_content_hash(content)
                self._cache_result(content_hash, result)
            
            return result
        
        # Profile the operation
        return self._profile_operation("advanced_optimize_content", optimize_operation)
    
    def batch_optimize_advanced(self, 
                               contents: List[str], 
                               max_workers: int = 4,
                               use_cache: bool = True) -> List[OptimizationResult]:
        """
        Advanced batch optimization with concurrent processing.
        
        Args:
            contents: List of content strings to optimize
            max_workers: Maximum number of concurrent workers
            use_cache: Whether to use caching
            
        Returns:
            List of optimization results
        """
        def batch_operation():
            results = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all optimization tasks
                future_to_content = {
                    executor.submit(self.optimize_content_advanced, content, use_cache): content
                    for content in contents
                }
                
                # Update concurrent operations counter
                current_concurrent = len(future_to_content)
                self.advanced_stats['concurrent_operations'] = current_concurrent
                if current_concurrent > self.advanced_stats['max_concurrent_operations']:
                    self.advanced_stats['max_concurrent_operations'] = current_concurrent
                
                # Collect results as they complete
                for future in as_completed(future_to_content):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        content = future_to_content[future]
                        error_result = OptimizationResult(
                            original_content=content,
                            optimized_content=content,
                            processing_time=0.0,
                            stages_completed=[],
                            issues_found=[f"Concurrent processing error: {str(e)}"],
                            success=False
                        )
                        results.append(error_result)
                        self.logger.error(f"❌ Concurrent optimization failed: {e}")
                
                # Reset concurrent operations counter
                self.advanced_stats['concurrent_operations'] = 0
            
            return results
        
        return self._profile_operation("batch_optimize_advanced", batch_operation)
    
    def optimize_directory(self, 
                          directory_path: Union[str, Path],
                          file_pattern: str = "*.md",
                          max_workers: int = 4,
                          save_results: bool = False) -> Dict[str, OptimizationResult]:
        """
        Optimize all files in a directory.
        
        Args:
            directory_path: Path to directory
            file_pattern: File pattern to match
            max_workers: Maximum concurrent workers
            save_results: Whether to save optimized content back to files
            
        Returns:
            Dictionary mapping file paths to optimization results
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            self.logger.error(f"❌ Invalid directory: {directory_path}")
            return {}
        
        # Find matching files
        matching_files = list(directory_path.glob(file_pattern))
        
        if not matching_files:
            self.logger.warning(f"⚠️ No files found matching pattern '{file_pattern}' in {directory_path}")
            return {}
        
        self.logger.info(f"🚀 Starting directory optimization: {len(matching_files)} files")
        
        # Read all file contents
        file_contents = {}
        for file_path in matching_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents[str(file_path)] = f.read()
            except Exception as e:
                self.logger.error(f"❌ Failed to read {file_path}: {e}")
        
        # Optimize all contents
        contents_list = list(file_contents.values())
        results_list = self.batch_optimize_advanced(contents_list, max_workers)
        
        # Map results back to file paths
        results = {}
        for (file_path, _), result in zip(file_contents.items(), results_list):
            results[file_path] = result
            
            # Save optimized content if requested
            if save_results and result.success:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result.optimized_content)
                    self.logger.debug(f"💾 Saved optimized content to {file_path}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to save {file_path}: {e}")
        
        successful_count = sum(1 for r in results.values() if r.success)
        self.logger.info(f"✅ Directory optimization completed: {successful_count}/{len(results)} successful")
        
        return results
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics."""
        with self.performance_lock:
            if not self.performance_profiles:
                return {
                    'total_operations': 0,
                    'average_execution_time': 0.0,
                    'operation_types': {},
                    'performance_trends': []
                }
            
            # Calculate analytics
            total_operations = len(self.performance_profiles)
            total_time = sum(p.execution_time for p in self.performance_profiles)
            average_time = total_time / total_operations if total_operations > 0 else 0.0
            
            # Group by operation type
            operation_types = {}
            for profile in self.performance_profiles:
                op_name = profile.operation_name
                if op_name not in operation_types:
                    operation_types[op_name] = {
                        'count': 0,
                        'total_time': 0.0,
                        'average_time': 0.0,
                        'min_time': float('inf'),
                        'max_time': 0.0
                    }
                
                stats = operation_types[op_name]
                stats['count'] += 1
                stats['total_time'] += profile.execution_time
                stats['min_time'] = min(stats['min_time'], profile.execution_time)
                stats['max_time'] = max(stats['max_time'], profile.execution_time)
                stats['average_time'] = stats['total_time'] / stats['count']
            
            return {
                'total_operations': total_operations,
                'average_execution_time': average_time,
                'total_execution_time': total_time,
                'operation_types': operation_types,
                'cache_statistics': {
                    'cache_size': len(self.cache),
                    'cache_hits': self.advanced_stats['cache_hits'],
                    'cache_misses': self.advanced_stats['cache_misses'],
                    'hit_rate': self.advanced_stats['cache_hits'] / 
                               (self.advanced_stats['cache_hits'] + self.advanced_stats['cache_misses'])
                               if (self.advanced_stats['cache_hits'] + self.advanced_stats['cache_misses']) > 0 else 0.0
                },
                'concurrency_statistics': {
                    'max_concurrent_operations': self.advanced_stats['max_concurrent_operations']
                }
            }
    
    def clear_cache(self) -> None:
        """Clear optimization cache."""
        with self.cache_lock:
            cache_size = len(self.cache)
            self.cache.clear()
            self.logger.info(f"🗑️ Cleared optimization cache ({cache_size} entries)")
    
    def export_cache(self, file_path: Union[str, Path]) -> None:
        """
        Export cache to file for persistence.
        
        Args:
            file_path: Path to export cache to
        """
        file_path = Path(file_path)
        
        with self.cache_lock:
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(self.cache, f)
                self.logger.info(f"💾 Exported cache to {file_path} ({len(self.cache)} entries)")
            except Exception as e:
                self.logger.error(f"❌ Failed to export cache: {e}")
    
    def import_cache(self, file_path: Union[str, Path]) -> None:
        """
        Import cache from file.
        
        Args:
            file_path: Path to import cache from
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.error(f"❌ Cache file not found: {file_path}")
            return
        
        with self.cache_lock:
            try:
                with open(file_path, 'rb') as f:
                    imported_cache = pickle.load(f)
                    self.cache.update(imported_cache)
                self.logger.info(f"📥 Imported cache from {file_path} ({len(imported_cache)} entries)")
            except Exception as e:
                self.logger.error(f"❌ Failed to import cache: {e}")
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics."""
        core_stats = self.core_optimizer.get_optimization_statistics()
        performance_analytics = self.get_performance_analytics()
        
        return {
            'core_optimizer_stats': core_stats,
            'performance_analytics': performance_analytics,
            'advanced_stats': dict(self.advanced_stats),
            'cache_info': {
                'current_size': len(self.cache),
                'max_size': self.cache_size,
                'utilization': len(self.cache) / self.cache_size if self.cache_size > 0 else 0.0
            }
        }
