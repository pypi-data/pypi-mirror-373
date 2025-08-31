#!/usr/bin/env python3
"""
🎯 WOT-PDF FILE WATCHER - Live Rebuild System
============================================
⚡ Intelligent file watching with debouncing and selective rebuilds
🔷 Integrates with WOT-PDF Enhanced Diagram Builder
📊 Real-time PDF generation with performance monitoring

FEATURES:
- Smart file watching with debouncing
- Selective rebuilds (only changed files)
- Integration with wot-pdf dual-engine system
- Performance metrics and statistics
- Auto-opening of generated PDFs
- Error recovery and retry logic
"""

import os
import sys
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, Set, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️  watchdog not installed. Install with: pip install watchdog")

from wot_pdf.diagrams.enhanced_builder import EnhancedDiagramBuilder
from wot_pdf.core.pdf_generator import PDFGenerator


@dataclass
class BuildTask:
    """Represents a build task for a file"""
    file_path: Path
    task_type: str  # 'diagram', 'pdf', 'full'
    scheduled_time: datetime
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WatcherStats:
    """Statistics for file watcher performance"""
    files_watched: int = 0
    builds_triggered: int = 0
    successful_builds: int = 0
    failed_builds: int = 0
    cache_hits: int = 0
    total_build_time: float = 0.0
    last_build_time: Optional[datetime] = None
    
    # Tracking sets
    watched_extensions: Set[str] = field(default_factory=set)
    processed_files: Set[Path] = field(default_factory=set)


class SmartFileWatcher(FileSystemEventHandler):
    """Enhanced file system event handler with intelligent debouncing"""
    
    def __init__(self, 
                 root_path: Path,
                 builder: EnhancedDiagramBuilder,
                 pdf_generator: PDFGenerator,
                 config: Dict,
                 logger: logging.Logger):
        super().__init__()
        
        self.root_path = root_path.resolve()
        self.builder = builder
        self.pdf_generator = pdf_generator
        self.config = config
        self.logger = logger
        
        # Build queue and timing
        self.build_queue: Dict[Path, BuildTask] = {}
        self.last_build_times: Dict[Path, datetime] = {}
        self.debounce_delay = config.get('debounce_delay', 2.0)  # seconds
        
        # Statistics
        self.stats = WatcherStats()
        
        # Executor for async builds
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Watched extensions
        self.watched_extensions = set(config.get('watch_extensions', ['.md', '.mmd', '.dot', '.d2', '.puml']))
        self.ignore_patterns = config.get('ignore_patterns', ['node_modules', '.git', 'dist', 'build', '__pycache__'])
        
        self.logger.info(f"🔍 Watching {self.root_path} for {len(self.watched_extensions)} file types")
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed"""
        # Check extension
        if file_path.suffix.lower() not in self.watched_extensions:
            return False
        
        # Check ignore patterns
        path_str = str(file_path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return False
        
        # Check if file is under root path
        try:
            file_path.resolve().relative_to(self.root_path)
            return True
        except ValueError:
            return False
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        if not self.should_process_file(file_path):
            return
        
        self.schedule_build(file_path, 'auto_rebuild')
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        if not self.should_process_file(file_path):
            return
        
        self.logger.info(f"📝 New file detected: {file_path.name}")
        self.schedule_build(file_path, 'new_file')
    
    def schedule_build(self, file_path: Path, reason: str):
        """Schedule a build task with debouncing"""
        now = datetime.now()
        
        # Check debouncing
        if file_path in self.last_build_times:
            time_since_last = now - self.last_build_times[file_path]
            if time_since_last.total_seconds() < self.debounce_delay:
                self.logger.debug(f"⏳ Debouncing {file_path.name} ({time_since_last.total_seconds():.1f}s)")
                
                # Update existing task
                if file_path in self.build_queue:
                    self.build_queue[file_path].scheduled_time = now + timedelta(seconds=self.debounce_delay)
                return
        
        # Create new build task
        task = BuildTask(
            file_path=file_path,
            task_type=self.determine_build_type(file_path),
            scheduled_time=now + timedelta(seconds=self.debounce_delay),
            priority=self.determine_priority(file_path, reason)
        )
        
        self.build_queue[file_path] = task
        self.logger.info(f"📋 Scheduled {task.task_type} build for {file_path.name} (reason: {reason})")
    
    def determine_build_type(self, file_path: Path) -> str:
        """Determine what type of build is needed"""
        if file_path.suffix.lower() == '.md':
            return 'full_rebuild'
        elif file_path.suffix.lower() in ['.mmd', '.dot', '.d2', '.puml']:
            return 'diagram_only'
        else:
            return 'unknown'
    
    def determine_priority(self, file_path: Path, reason: str) -> int:
        """Determine build priority (lower = higher priority)"""
        if reason == 'manual':
            return 0
        elif file_path.suffix.lower() == '.md':
            return 1
        else:
            return 2
    
    async def process_build_queue(self):
        """Process pending build tasks"""
        if not self.build_queue:
            return
        
        now = datetime.now()
        ready_tasks = []
        
        # Find tasks ready for execution
        for file_path, task in list(self.build_queue.items()):
            if now >= task.scheduled_time:
                ready_tasks.append(task)
                del self.build_queue[file_path]
        
        if not ready_tasks:
            return
        
        # Sort by priority
        ready_tasks.sort(key=lambda t: (t.priority, t.scheduled_time))
        
        # Execute tasks
        for task in ready_tasks:
            try:
                await self.execute_build_task(task)
            except Exception as e:
                self.logger.error(f"Build task failed: {e}")
                
                # Retry logic
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.scheduled_time = now + timedelta(seconds=5 * task.retry_count)
                    self.build_queue[task.file_path] = task
                    self.logger.info(f"🔄 Retrying build for {task.file_path.name} (attempt {task.retry_count + 1})")
    
    async def execute_build_task(self, task: BuildTask):
        """Execute a single build task"""
        start_time = time.time()
        file_path = task.file_path
        
        self.logger.info(f"🔨 Building {file_path.name} ({task.task_type})")
        self.stats.builds_triggered += 1
        
        try:
            if task.task_type == 'full_rebuild':
                await self.build_full_document(file_path)
            elif task.task_type == 'diagram_only':
                await self.build_diagram_only(file_path)
            else:
                self.logger.warning(f"Unknown build type: {task.task_type}")
                return
            
            # Update statistics
            build_time = time.time() - start_time
            self.stats.successful_builds += 1
            self.stats.total_build_time += build_time
            self.stats.last_build_time = datetime.now()
            self.last_build_times[file_path] = datetime.now()
            self.stats.processed_files.add(file_path)
            
            self.logger.info(f"✅ Built {file_path.name} in {build_time:.2f}s")
            
            # Auto-open PDF if configured
            if self.config.get('auto_open_pdf', False):
                pdf_path = file_path.with_suffix('.pdf')
                if pdf_path.exists():
                    await self.open_pdf(pdf_path)
        
        except Exception as e:
            self.stats.failed_builds += 1
            self.logger.error(f"❌ Build failed for {file_path.name}: {e}")
            raise
    
    async def build_full_document(self, md_path: Path):
        """Build complete document from Markdown"""
        loop = asyncio.get_event_loop()
        
        # Convert MD to Typst with diagrams
        typ_path = md_path.with_suffix('.typ')
        
        def convert_diagrams():
            return self.builder.md_to_typst(md_path, typ_path)
        
        diagram_stats = await loop.run_in_executor(self.executor, convert_diagrams)
        self.stats.cache_hits += diagram_stats.get('diagrams_cached', 0)
        
        # Generate PDF using wot-pdf
        pdf_path = md_path.with_suffix('.pdf')
        
        def generate_pdf():
            result = self.pdf_generator.generate_from_typst(
                input_file=str(typ_path),
                output_file=str(pdf_path)
            )
            return result
        
        await loop.run_in_executor(self.executor, generate_pdf)
        
        self.logger.info(f"📄 Generated {pdf_path.name}")
    
    async def build_diagram_only(self, diagram_path: Path):
        """Rebuild only diagram-related files"""
        # Find all MD files that might reference this diagram
        md_files = list(self.root_path.glob('**/*.md'))
        
        # Check which MD files contain references to this diagram
        diagram_name = diagram_path.stem
        affected_files = []
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                if diagram_name in content or str(diagram_path.name) in content:
                    affected_files.append(md_file)
            except Exception:
                continue  # Skip files we can't read
        
        if affected_files:
            self.logger.info(f"📊 Diagram change affects {len(affected_files)} documents")
            for md_file in affected_files:
                await self.build_full_document(md_file)
        else:
            self.logger.info(f"📊 Diagram {diagram_path.name} not referenced in any documents")
    
    async def open_pdf(self, pdf_path: Path):
        """Open generated PDF in default viewer"""
        try:
            if sys.platform.startswith('win'):
                os.startfile(str(pdf_path))
            elif sys.platform.startswith('darwin'):
                os.system(f'open "{pdf_path}"')
            else:
                os.system(f'xdg-open "{pdf_path}"')
        except Exception as e:
            self.logger.warning(f"Could not open PDF: {e}")
    
    def get_stats(self) -> Dict:
        """Get current watcher statistics"""
        return {
            'files_watched': len(self.stats.processed_files),
            'builds_triggered': self.stats.builds_triggered,
            'successful_builds': self.stats.successful_builds,
            'failed_builds': self.stats.failed_builds,
            'cache_hits': self.stats.cache_hits,
            'success_rate': (self.stats.successful_builds / max(1, self.stats.builds_triggered)) * 100,
            'avg_build_time': self.stats.total_build_time / max(1, self.stats.successful_builds),
            'last_build': self.stats.last_build_time.isoformat() if self.stats.last_build_time else None,
            'queue_length': len(self.build_queue)
        }


class WOTPDFFileWatcher:
    """Main file watcher orchestrator"""
    
    def __init__(self, root_path: Path, config: Optional[Dict] = None):
        self.root_path = root_path.resolve()
        self.config = config or self._load_default_config()
        self.logger = self._setup_logger()
        
        # Initialize components
        self.builder = EnhancedDiagramBuilder(logger=self.logger)
        self.pdf_generator = PDFGenerator()
        
        # File watcher setup
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError("watchdog package is required for file watching")
        
        self.observer = Observer()
        self.event_handler = SmartFileWatcher(
            root_path=self.root_path,
            builder=self.builder,
            pdf_generator=self.pdf_generator,
            config=self.config,
            logger=self.logger
        )
        
        # Running state
        self.is_running = False
        self.stats_interval = self.config.get('stats_interval', 30)  # seconds
    
    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            'debounce_delay': 2.0,
            'auto_open_pdf': True,
            'watch_extensions': ['.md', '.mmd', '.dot', '.d2', '.puml'],
            'ignore_patterns': ['node_modules', '.git', 'dist', 'build', '__pycache__'],
            'stats_interval': 30,
            'log_level': 'INFO'
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for file watcher"""
        logger = logging.getLogger('wot_pdf.watcher')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            level = getattr(logging, self.config.get('log_level', 'INFO').upper())
            logger.setLevel(level)
        
        return logger
    
    async def start_watching(self):
        """Start file watching with async processing"""
        if self.is_running:
            self.logger.warning("Watcher is already running")
            return
        
        self.logger.info(f"🚀 Starting WOT-PDF file watcher for {self.root_path}")
        self.logger.info(f"📁 Watching extensions: {', '.join(self.config['watch_extensions'])}")
        
        # Start file system observer
        self.observer.schedule(
            self.event_handler, 
            str(self.root_path), 
            recursive=True
        )
        self.observer.start()
        self.is_running = True
        
        try:
            # Main event loop
            while self.is_running:
                # Process build queue
                await self.event_handler.process_build_queue()
                
                # Print stats periodically
                await self._maybe_print_stats()
                
                # Short sleep to prevent busy waiting
                await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Stopping watcher...")
        
        finally:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            
            # Print final stats
            await self._print_final_stats()
    
    async def _maybe_print_stats(self):
        """Print statistics if interval has passed"""
        if not hasattr(self, '_last_stats_time'):
            self._last_stats_time = time.time()
            return
        
        if time.time() - self._last_stats_time >= self.stats_interval:
            stats = self.event_handler.get_stats()
            
            self.logger.info(f"📊 Stats: {stats['builds_triggered']} builds, "
                           f"{stats['successful_builds']} successful, "
                           f"{stats['success_rate']:.1f}% success rate, "
                           f"{stats['avg_build_time']:.2f}s avg build time")
            
            if stats['queue_length'] > 0:
                self.logger.info(f"⏳ Queue: {stats['queue_length']} pending tasks")
            
            self._last_stats_time = time.time()
    
    async def _print_final_stats(self):
        """Print final statistics before shutdown"""
        stats = self.event_handler.get_stats()
        
        self.logger.info("📊 Final Statistics:")
        self.logger.info(f"  • Files processed: {stats['files_watched']}")
        self.logger.info(f"  • Builds triggered: {stats['builds_triggered']}")
        self.logger.info(f"  • Successful builds: {stats['successful_builds']}")
        self.logger.info(f"  • Failed builds: {stats['failed_builds']}")
        self.logger.info(f"  • Cache hits: {stats['cache_hits']}")
        self.logger.info(f"  • Success rate: {stats['success_rate']:.1f}%")
        self.logger.info(f"  • Average build time: {stats['avg_build_time']:.2f}s")


# CLI Interface
async def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WOT-PDF File Watcher - Live Rebuild System')
    parser.add_argument('path', nargs='?', default='.', help='Path to watch (default: current directory)')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    parser.add_argument('--no-auto-open', action='store_true', help='Disable auto-opening PDFs')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and Path(args.config).exists():
        import yaml
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f) or {}
    
    # Apply CLI overrides
    if args.verbose:
        config['log_level'] = 'DEBUG'
    if args.no_auto_open:
        config['auto_open_pdf'] = False
    
    # Create and start watcher
    watcher = WOTPDFFileWatcher(Path(args.path), config)
    await watcher.start_watching()


if __name__ == '__main__':
    if not WATCHDOG_AVAILABLE:
        print("❌ watchdog package is required. Install with:")
        print("   pip install watchdog")
        sys.exit(1)
    
    asyncio.run(main())
