#!/usr/bin/env python3
"""
🚀 REPORTLAB ADVANCED FEATURES ENGINE
===================================
⚡ Advanced capabilities matching Typst engine features
🔷 Intelligent content processing, optimization, and batch operations
📊 Enterprise-grade features with performance monitoring

ADVANCED COMPONENTS:
- ReportLabContentOptimizer: Intelligent markdown optimization
- ReportLabSecurityValidator: Content security validation
- ReportLabBatchProcessor: Multi-threaded batch operations
- ReportLabPerformanceMonitor: Real-time metrics and profiling
"""

import time
import hashlib
import threading
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging

@dataclass
class OptimizationResult:
    """Results from content optimization"""
    original_content: str
    optimized_content: str
    processing_time: float
    optimizations_applied: List[str]
    warnings: List[str]
    success: bool
    file_size_estimate: int

@dataclass
class SecurityValidationResult:
    """Results from security validation"""
    is_safe: bool
    warnings: List[str]
    blocked_elements: List[str]
    risk_score: float

class ReportLabContentOptimizer:
    """
    ADVANCED FEATURE 1: Intelligent content optimization
    Matches Typst's V4 Unified Content Optimizer capabilities
    """
    
    def __init__(self, cache_size: int = 1000):
        self.logger = logging.getLogger(f"{__name__}.ContentOptimizer")
        self.cache = {}
        self.cache_size = cache_size
        self.cache_lock = threading.RLock()
        self.optimization_stats = {
            'total_optimizations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        
        self.logger.info("🚀 ReportLab Content Optimizer initialized")
    
    def optimize_content(self, content: str, use_cache: bool = True) -> OptimizationResult:
        """
        Optimize content for ReportLab rendering with intelligent processing
        """
        start_time = time.time()
        
        self.logger.info(f"🔧 Starting content optimization ({len(content)} chars)")
        
        # Check cache first
        content_hash = None
        if use_cache:
            content_hash = self._calculate_hash(content)
            cached_result = self._get_cached_result(content_hash)
            if cached_result:
                self.optimization_stats['cache_hits'] += 1
                self.logger.debug("⚡ Using cached optimization result")
                return cached_result
        
        self.optimization_stats['cache_misses'] += 1
        
        # Perform optimization
        optimizations_applied = []
        warnings = []
        optimized_content = content
        
        self.logger.info(f"📝 Initial content length: {len(optimized_content)}")
        
        # 1. Intelligent paragraph optimization
        if self._needs_paragraph_optimization(content):
            optimized_content = self._optimize_paragraphs(optimized_content)
            optimizations_applied.append("paragraph_optimization")
            self.logger.info(f"📝 After paragraph optimization: {len(optimized_content)}")
        
        # 2. Advanced table processing
        if self._contains_complex_tables(content):
            optimized_content, table_warnings = self._optimize_tables(optimized_content)
            optimizations_applied.append("table_optimization")
            warnings.extend(table_warnings)
            self.logger.info(f"📝 After table optimization: {len(optimized_content)}")
        
        # 3. Code block enhancement
        if self._contains_code_blocks(content):
            optimized_content = self._optimize_code_blocks(optimized_content)
            optimizations_applied.append("code_optimization")
            self.logger.info(f"📝 After code optimization: {len(optimized_content)}")
        
        # 4. List structure improvement
        if self._contains_lists(content):
            optimized_content = self._optimize_lists(optimized_content)
            optimizations_applied.append("list_optimization")
            self.logger.info(f"📝 After list optimization: {len(optimized_content)}")
        
        # 5. Header hierarchy validation
        optimized_content, header_warnings = self._optimize_headers(optimized_content)
        if header_warnings:
            optimizations_applied.append("header_optimization")
            warnings.extend(header_warnings)
        self.logger.info(f"📝 After header optimization: {len(optimized_content)}")
        
        # 6. Performance-critical formatting
        optimized_content = self._optimize_formatting(optimized_content)
        optimizations_applied.append("formatting_optimization")
        self.logger.info(f"📝 After formatting optimization: {len(optimized_content)}")
        
        self.logger.info(f"🎯 Final optimized content length: {len(optimized_content)}")
        
        processing_time = time.time() - start_time
        
        # Update stats
        self.optimization_stats['total_optimizations'] += 1
        self.optimization_stats['total_processing_time'] += processing_time
        self.optimization_stats['average_processing_time'] = (
            self.optimization_stats['total_processing_time'] / 
            self.optimization_stats['total_optimizations']
        )
        
        result = OptimizationResult(
            original_content=content,
            optimized_content=optimized_content,
            processing_time=processing_time,
            optimizations_applied=optimizations_applied,
            warnings=warnings,
            success=True,
            file_size_estimate=len(optimized_content)
        )
        
        # Cache result
        if use_cache and content_hash:
            self._cache_result(content_hash, result)
        
        self.logger.info(f"✅ Content optimization completed in {processing_time:.3f}s with {len(optimizations_applied)} optimizations")
        return result
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate content hash for caching"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _get_cached_result(self, content_hash: str) -> Optional[OptimizationResult]:
        """Get cached optimization result"""
        with self.cache_lock:
            return self.cache.get(content_hash)
    
    def _cache_result(self, content_hash: str, result: OptimizationResult) -> None:
        """Cache optimization result"""
        with self.cache_lock:
            if len(self.cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[content_hash] = result
    
    def _needs_paragraph_optimization(self, content: str) -> bool:
        """Check if content needs paragraph optimization"""
        return len(content.split('\n\n')) > 5 or len(content.split('\n')) > 20
    
    def _optimize_paragraphs(self, content: str) -> str:
        """Optimize paragraph structure for better ReportLab rendering"""
        lines = content.split('\n')
        optimized_lines = []
        
        in_code_block = False
        current_paragraph = []
        
        for line in lines:
            stripped = line.strip()
            
            # Track code blocks
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                if current_paragraph:
                    optimized_lines.extend(current_paragraph)
                    current_paragraph = []
                optimized_lines.append(line)
                continue
            
            if in_code_block:
                optimized_lines.append(line)
                continue
            
            # Handle empty lines and paragraph breaks
            if not stripped:
                if current_paragraph:
                    # Join current paragraph with proper spacing
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 200:  # Split long paragraphs
                        sentences = paragraph_text.split('. ')
                        if len(sentences) > 2:
                            mid_point = len(sentences) // 2
                            part1 = '. '.join(sentences[:mid_point]) + '.'
                            part2 = '. '.join(sentences[mid_point:])
                            optimized_lines.extend([part1, '', part2])
                        else:
                            optimized_lines.append(paragraph_text)
                    else:
                        optimized_lines.append(paragraph_text)
                    current_paragraph = []
                optimized_lines.append('')
            else:
                # Check if this starts a new structure (headers, lists, etc.)
                if (stripped.startswith('#') or stripped.startswith('-') or 
                    stripped.startswith('*') or stripped.startswith('1.')):
                    if current_paragraph:
                        paragraph_text = ' '.join(current_paragraph)
                        optimized_lines.append(paragraph_text)
                        current_paragraph = []
                    optimized_lines.append(line)
                else:
                    current_paragraph.append(stripped)
        
        # Handle remaining paragraph
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            optimized_lines.append(paragraph_text)
        
        return '\n'.join(optimized_lines)
    
    def _contains_complex_tables(self, content: str) -> bool:
        """Check for complex table structures"""
        lines = content.split('\n')
        table_lines = [line for line in lines if '|' in line and line.count('|') >= 2]
        return len(table_lines) > 3  # Complex if more than header + separator + 1 row
    
    def _optimize_tables(self, content: str) -> Tuple[str, List[str]]:
        """Optimize table structures for ReportLab"""
        warnings = []
        lines = content.split('\n')
        optimized_lines = []
        
        in_table = False
        table_rows = []
        max_columns = 0
        
        for line in lines:
            if '|' in line and line.count('|') >= 2:
                if not in_table:
                    in_table = True
                    table_rows = []
                
                # Clean and normalize table row
                cells = [cell.strip() for cell in line.split('|')]
                if cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                
                if cells:
                    max_columns = max(max_columns, len(cells))
                    table_rows.append(cells)
            else:
                if in_table:
                    # Process completed table
                    if table_rows:
                        optimized_table, table_warnings = self._process_table_rows(table_rows, max_columns)
                        optimized_lines.extend(optimized_table)
                        warnings.extend(table_warnings)
                    
                    in_table = False
                    table_rows = []
                    max_columns = 0
                
                optimized_lines.append(line)
        
        # Handle table at end of content
        if in_table and table_rows:
            optimized_table, table_warnings = self._process_table_rows(table_rows, max_columns)
            optimized_lines.extend(optimized_table)
            warnings.extend(table_warnings)
        
        return '\n'.join(optimized_lines), warnings
    
    def _process_table_rows(self, rows: List[List[str]], max_columns: int) -> Tuple[List[str], List[str]]:
        """Process table rows with normalization and validation"""
        warnings = []
        processed_rows = []
        
        for i, row in enumerate(rows):
            # Skip separator rows (---|---|---)
            if all(re.match(r'^[\s\-:|]*$', cell) for cell in row):
                continue
            
            # Normalize column count
            while len(row) < max_columns:
                row.append('')
                if i == 0:  # Header row
                    warnings.append(f"Table header missing column {len(row)}")
            
            # Limit column width for ReportLab
            processed_cells = []
            for cell in row[:max_columns]:  # Limit to max_columns
                if len(cell) > 50:  # Long cell content
                    cell = cell[:47] + '...'
                    warnings.append("Long table cell content truncated")
                processed_cells.append(cell)
            
            # Reconstruct table row
            processed_row = '| ' + ' | '.join(processed_cells) + ' |'
            processed_rows.append(processed_row)
        
        # Don't add separators - ReportLab handles table styling itself
        # The separator lines will be handled by TableStyle in ReportLab
        return processed_rows, warnings
    
    def _contains_code_blocks(self, content: str) -> bool:
        """Check for code blocks"""
        return '```' in content or content.count('`') > 4
    
    def _optimize_code_blocks(self, content: str) -> str:
        """Optimize code blocks for ReportLab rendering"""
        lines = content.split('\n')
        optimized_lines = []
        
        in_code_block = False
        code_lines = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # Process completed code block
                    if code_lines:
                        # Limit line length for ReportLab
                        processed_code = []
                        for code_line in code_lines:
                            if len(code_line) > 80:  # Wrap long lines
                                while len(code_line) > 80:
                                    processed_code.append(code_line[:80])
                                    code_line = '  ' + code_line[80:]  # Indent continuation
                                if code_line.strip():
                                    processed_code.append(code_line)
                            else:
                                processed_code.append(code_line)
                        
                        optimized_lines.append('```')
                        optimized_lines.extend(processed_code)
                        optimized_lines.append('```')
                    
                    in_code_block = False
                    code_lines = []
                else:
                    in_code_block = True
                    optimized_lines.append(line)
            elif in_code_block:
                code_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _contains_lists(self, content: str) -> bool:
        """Check for list structures"""
        lines = content.split('\n')
        list_lines = [line for line in lines if (
            line.strip().startswith('- ') or 
            line.strip().startswith('* ') or
            bool(re.match(r'^\s*\d+\.\s', line.strip()))
        )]
        return len(list_lines) > 2
    
    def _optimize_lists(self, content: str) -> str:
        """Optimize list structures"""
        lines = content.split('\n')
        optimized_lines = []
        
        in_list = False
        list_items = []
        
        for line in lines:
            stripped = line.strip()
            
            if (stripped.startswith('- ') or stripped.startswith('* ') or
                bool(re.match(r'^\d+\.\s', stripped))):
                
                if not in_list:
                    in_list = True
                    list_items = []
                
                # Clean list item
                if stripped.startswith('- ') or stripped.startswith('* '):
                    item_text = stripped[2:].strip()
                else:  # Numbered list
                    match = re.match(r'^\d+\.\s(.+)', stripped)
                    item_text = match.group(1) if match else stripped
                
                # Limit item length
                if len(item_text) > 100:
                    item_text = item_text[:97] + '...'
                
                list_items.append((stripped[:2], item_text))
                
            else:
                if in_list and list_items:
                    # Process completed list
                    for prefix, item_text in list_items:
                        optimized_lines.append(f"{prefix} {item_text}")
                    
                    in_list = False
                    list_items = []
                
                optimized_lines.append(line)
        
        # Handle list at end
        if in_list and list_items:
            for prefix, item_text in list_items:
                optimized_lines.append(f"{prefix} {item_text}")
        
        return '\n'.join(optimized_lines)
    
    def _optimize_headers(self, content: str) -> Tuple[str, List[str]]:
        """Optimize header hierarchy"""
        warnings = []
        lines = content.split('\n')
        optimized_lines = []
        
        header_levels = []
        
        for line in lines:
            if line.strip().startswith('#'):
                match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
                if match:
                    level = len(match.group(1))
                    text = match.group(2).strip()
                    header_levels.append(level)
                    
                    # Validate header hierarchy
                    if len(header_levels) > 1:
                        prev_level = header_levels[-2]
                        if level > prev_level + 1:
                            warnings.append(f"Header level jump from {prev_level} to {level}: '{text[:30]}'")
                    
                    # Limit header text length
                    if len(text) > 60:
                        text = text[:57] + '...'
                        warnings.append("Long header text truncated")
                    
                    optimized_lines.append(f"{'#' * level} {text}")
                else:
                    optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines), warnings
    
    def _optimize_formatting(self, content: str) -> str:
        """Optimize inline formatting for ReportLab"""
        # Clean up excessive formatting
        content = re.sub(r'\*{3,}', '**', content)  # Limit bold formatting
        content = re.sub(r'_{3,}', '_', content)    # Limit italic formatting
        
        # Optimize link formatting  
        content = re.sub(r'\[([^\]]{50,})\]', lambda m: f'[{m.group(1)[:47]}...]', content)
        
        # Clean up excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        return content
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            **self.optimization_stats,
            'cache_size': len(self.cache),
            'cache_hit_rate': (
                self.optimization_stats['cache_hits'] / 
                max(self.optimization_stats['cache_hits'] + self.optimization_stats['cache_misses'], 1)
            ) * 100
        }


class ReportLabSecurityValidator:
    """
    ADVANCED FEATURE 2: Content security validation
    Matches Typst's content security system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SecurityValidator")
        self.blocked_patterns = [
            r'<script[^>]*>.*?</script>',  # Scripts
            r'javascript:',                # JavaScript URLs
            r'data:image/[^;]*;base64,',  # Base64 images (too large)
            r'file:///.*',                # File system access
            r'\\x[0-9a-fA-F]{2}',        # Hex escapes
        ]
        
        self.warning_patterns = [
            r'<.*?>',                     # HTML tags
            r'&[a-zA-Z0-9]+;',           # HTML entities
            r'%[0-9a-fA-F]{2}',          # URL encoding
            r'\n{5,}',                   # Excessive newlines
        ]
        
        self.logger.info("🛡️ ReportLab Security Validator initialized")
    
    def validate_content(self, content: str) -> SecurityValidationResult:
        """Validate content for security issues"""
        is_safe = True
        warnings = []
        blocked_elements = []
        risk_score = 0.0
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                is_safe = False
                risk_score += 10.0
                blocked_elements.append(f"Blocked pattern: {pattern} ({len(matches)} matches)")
        
        # Check for warning patterns
        for pattern in self.warning_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                risk_score += 2.0
                warnings.append(f"Warning pattern: {pattern} ({len(matches)} matches)")
        
        # Content size checks
        if len(content) > 1_000_000:  # 1MB
            risk_score += 5.0
            warnings.append("Large content size detected")
        
        # Suspicious character patterns
        non_printable = len([c for c in content if ord(c) < 32 and c not in '\n\r\t'])
        if non_printable > 10:
            risk_score += 3.0
            warnings.append(f"Non-printable characters detected: {non_printable}")
        
        # Calculate final risk score
        risk_score = min(risk_score, 100.0)  # Cap at 100
        
        if risk_score > 20:
            is_safe = False
        
        self.logger.info(f"🛡️ Security validation completed - Safe: {is_safe}, Risk: {risk_score:.1f}")
        
        return SecurityValidationResult(
            is_safe=is_safe,
            warnings=warnings,
            blocked_elements=blocked_elements,
            risk_score=risk_score
        )


class ReportLabBatchProcessor:
    """
    ADVANCED FEATURE 3: Multi-threaded batch processing
    Matches Typst's batch processing capabilities
    """
    
    def __init__(self, max_workers: int = 4):
        self.logger = logging.getLogger(f"{__name__}.BatchProcessor")
        self.max_workers = max_workers
        self.processing_stats = {
            'total_batches': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_processing_time': 0.0,
            'average_batch_time': 0.0
        }
        
        self.logger.info(f"🚀 ReportLab Batch Processor initialized with {max_workers} workers")
    
    def process_batch(self, 
                     contents: List[str], 
                     processor_func: callable,
                     **kwargs) -> List[Dict[str, Any]]:
        """
        Process multiple content items in parallel
        """
        start_time = time.time()
        results = []
        
        self.processing_stats['total_batches'] += 1
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_content = {
                executor.submit(processor_func, content, **kwargs): (i, content)
                for i, content in enumerate(contents)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_content):
                content_index, original_content = future_to_content[future]
                
                try:
                    result = future.result()
                    results.append({
                        'index': content_index,
                        'success': True,
                        'result': result,
                        'original_length': len(original_content),
                        'error': None
                    })
                    self.processing_stats['successful_operations'] += 1
                    
                except Exception as e:
                    results.append({
                        'index': content_index,
                        'success': False,
                        'result': None,
                        'original_length': len(original_content),
                        'error': str(e)
                    })
                    self.processing_stats['failed_operations'] += 1
                    self.logger.error(f"❌ Batch processing failed for item {content_index}: {e}")
        
        # Sort results by original index
        results.sort(key=lambda x: x['index'])
        
        processing_time = time.time() - start_time
        self.processing_stats['total_processing_time'] += processing_time
        self.processing_stats['average_batch_time'] = (
            self.processing_stats['total_processing_time'] / 
            self.processing_stats['total_batches']
        )
        
        success_rate = (
            self.processing_stats['successful_operations'] / 
            max(self.processing_stats['successful_operations'] + self.processing_stats['failed_operations'], 1)
        ) * 100
        
        self.logger.info(f"✅ Batch processing completed in {processing_time:.2f}s")
        self.logger.info(f"📊 Success rate: {success_rate:.1f}% ({len([r for r in results if r['success']])}/{len(results)})")
        
        return results
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        return {
            **self.processing_stats,
            'max_workers': self.max_workers,
            'success_rate': (
                self.processing_stats['successful_operations'] / 
                max(self.processing_stats['successful_operations'] + self.processing_stats['failed_operations'], 1)
            ) * 100
        }


class ReportLabPerformanceMonitor:
    """
    ADVANCED FEATURE 4: Performance monitoring and metrics
    Real-time performance tracking and optimization suggestions
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PerformanceMonitor")
        self.metrics = {
            'generation_times': [],
            'content_sizes': [],
            'optimization_times': [],
            'memory_usage': [],
            'error_count': 0,
            'total_operations': 0
        }
        self.start_time = time.time()
        
        self.logger.info("📊 ReportLab Performance Monitor initialized")
    
    def record_generation(self, processing_time: float, content_size: int, optimization_time: float = 0.0):
        """Record generation metrics"""
        self.metrics['generation_times'].append(processing_time)
        self.metrics['content_sizes'].append(content_size)
        self.metrics['optimization_times'].append(optimization_time)
        self.metrics['total_operations'] += 1
        
        # Keep only recent metrics (sliding window)
        max_entries = 1000
        for key in ['generation_times', 'content_sizes', 'optimization_times']:
            if len(self.metrics[key]) > max_entries:
                self.metrics[key] = self.metrics[key][-max_entries:]
    
    def record_error(self, error_type: str, error_message: str):
        """Record error occurrence"""
        self.metrics['error_count'] += 1
        self.logger.warning(f"⚠️ Error recorded: {error_type} - {error_message}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics['generation_times']:
            return {
                'status': 'no_data',
                'message': 'No performance data available'
            }
        
        gen_times = self.metrics['generation_times']
        content_sizes = self.metrics['content_sizes']
        opt_times = self.metrics['optimization_times']
        
        report = {
            'uptime_seconds': time.time() - self.start_time,
            'total_operations': self.metrics['total_operations'],
            'error_count': self.metrics['error_count'],
            'error_rate': (self.metrics['error_count'] / max(self.metrics['total_operations'], 1)) * 100,
            
            'generation_times': {
                'average': sum(gen_times) / len(gen_times),
                'min': min(gen_times),
                'max': max(gen_times),
                'median': sorted(gen_times)[len(gen_times) // 2],
                'p95': sorted(gen_times)[int(len(gen_times) * 0.95)] if len(gen_times) > 20 else max(gen_times)
            },
            
            'content_sizes': {
                'average': sum(content_sizes) / len(content_sizes),
                'min': min(content_sizes),
                'max': max(content_sizes),
                'total_processed': sum(content_sizes)
            },
            
            'optimization_times': {
                'average': sum(opt_times) / len(opt_times) if opt_times else 0.0,
                'total': sum(opt_times)
            },
            
            'throughput': {
                'operations_per_second': self.metrics['total_operations'] / (time.time() - self.start_time),
                'bytes_per_second': sum(content_sizes) / (time.time() - self.start_time)
            }
        }
        
        # Generate optimization suggestions
        report['suggestions'] = self._generate_optimization_suggestions(report)
        
        return report
    
    def _generate_optimization_suggestions(self, report: Dict[str, Any]) -> List[str]:
        """Generate performance optimization suggestions"""
        suggestions = []
        
        avg_gen_time = report['generation_times']['average']
        if avg_gen_time > 1.0:
            suggestions.append("Consider enabling content caching for faster generation")
        
        if avg_gen_time > 2.0:
            suggestions.append("High generation times detected - consider batch processing")
        
        error_rate = report['error_rate']
        if error_rate > 5.0:
            suggestions.append("High error rate detected - enable content validation")
        
        avg_content_size = report['content_sizes']['average']
        if avg_content_size > 100000:  # 100KB
            suggestions.append("Large content sizes - consider content optimization")
        
        if report['optimization_times']['average'] > avg_gen_time * 0.5:
            suggestions.append("Optimization overhead high - tune optimization settings")
        
        throughput = report['throughput']['operations_per_second']
        if throughput < 1.0:
            suggestions.append("Low throughput - consider parallel processing")
        
        return suggestions


def create_advanced_reportlab_system() -> Dict[str, Any]:
    """
    Factory function to create complete advanced ReportLab system
    Returns all advanced components ready for use
    """
    return {
        'optimizer': ReportLabContentOptimizer(cache_size=1000),
        'security_validator': ReportLabSecurityValidator(),
        'batch_processor': ReportLabBatchProcessor(max_workers=4),
        'performance_monitor': ReportLabPerformanceMonitor()
    }
