#!/usr/bin/env python3
"""
🎨 DIAGRAM PROCESSOR - MERMAID & GRAPHVIZ RENDERING
=================================================
⚡ Production-ready diagram builder with CLI detection and caching
🔷 Cross-platform tool support (Windows/Linux/macOS)
📊 Hash-based SVG caching with metadata extraction

FEATURES:
- Auto-detection of CLI tools (mmdc, dot, d2, plantuml)
- Caption and label extraction from diagram comments
- Hash-based caching for performance optimization
- Smart CLI path resolution for Windows

Extracted from production_builder.py for better modularity.
"""

import os
import sys
import subprocess
import hashlib
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class DiagramMetadata:
    """Metadata extracted from diagram comments"""
    caption: Optional[str] = None
    label: Optional[str] = None
    hash: Optional[str] = None
    language: Optional[str] = None


@dataclass
class RenderStats:
    """Statistics for diagram rendering process"""
    diagrams_processed: int = 0
    diagrams_cached: int = 0
    diagrams_rendered: int = 0
    cache_hit_rate: float = 0.0


# Supported diagram engines with CLI commands
SUPPORTED_ENGINES = {
    'mermaid': ('mmdc', ['-i', '{input}', '-o', '{output}', '-e', 'png', '--theme', 'default', 
                        '--backgroundColor', 'transparent', '--scale', '3', '--width', '1200']),
    'dot': ('dot', ['-Tsvg', '{input}', '-o', '{output}']),
    'graphviz': ('dot', ['-Tsvg', '{input}', '-o', '{output}']),
    'd2': ('d2', ['{input}', '{output}', '--theme', '0']),
    'plantuml': ('plantuml', ['-tsvg', '{input}']),
}

# Caption extraction patterns for different languages
CAPTION_PATTERNS = {
    'mermaid': r'^\s*%%\s*caption:\s*(.+)$',
    'plantuml': r'^\s*\'\s*caption:\s*(.+)$|^\s*%%\s*caption:\s*(.+)$',
    'd2': r'^\s*#\s*caption:\s*(.+)$',
    'dot': r'^\s*//\s*caption:\s*(.+)$|^\s*/\*\s*caption:\s*(.+)\s*\*/',
    'graphviz': r'^\s*//\s*caption:\s*(.+)$|^\s*/\*\s*caption:\s*(.+)\s*\*/',
}

# Label extraction patterns for different languages  
LABEL_PATTERNS = {
    'mermaid': r'^\s*%%\s*label:\s*(fig:[\w\-_]+)$',
    'plantuml': r'^\s*\'\s*label:\s*(fig:[\w\-_]+)$|^\s*%%\s*label:\s*(fig:[\w\-_]+)$',
    'd2': r'^\s*#\s*label:\s*(fig:[\w\-_]+)$',
    'dot': r'^\s*//\s*label:\s*(fig:[\w\-_]+)$|^\s*/\*\s*label:\s*(fig:[\w\-_]+)\s*\*/',
    'graphviz': r'^\s*//\s*label:\s*(fig:[\w\-_]+)$|^\s*/\*\s*label:\s*(fig:[\w\-_]+)\s*\*/',
}


class DiagramProcessor:
    """
    Production-ready diagram processing with CLI tool detection and caching.
    Handles Mermaid, Graphviz, D2, and PlantUML diagrams.
    """

    def __init__(self, output_dir: Path = Path('diagrams'), cache_dir: Path = Path('.cache')):
        """
        Initialize diagram processor.
        
        Args:
            output_dir: Directory for rendered diagram outputs
            cache_dir: Directory for caching CLI availability and diagrams
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # CLI availability cache
        self.cli_cache = self._load_cli_cache()
        self.available_tools = set()
        
        # Statistics
        self.stats = RenderStats()
        
        # Ensure CLI tools are available
        self._check_cli_tools()

    def _load_cli_cache(self) -> Dict[str, bool]:
        """Load CLI availability cache from disk."""
        cache_file = self.cache_dir / 'cli_availability.json'
        if cache_file.exists():
            try:
                import json
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load CLI cache: {e}")
        return {}

    def _save_cli_cache(self):
        """Save CLI availability cache to disk."""
        try:
            import json
            cache_file = self.cache_dir / 'cli_availability.json'
            with open(cache_file, 'w') as f:
                json.dump(self.cli_cache, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save CLI cache: {e}")

    def _resolve_command_path(self, command: str) -> str:
        """Resolve command to full path on Windows."""
        if sys.platform.startswith('win') and command == 'mmdc':
            # Try npm global path first
            npm_path = os.path.expanduser(r'~\AppData\Roaming\npm\mmdc.cmd')
            if os.path.exists(npm_path):
                return npm_path
        return command  # fallback to original command

    def _is_command_available(self, command: str) -> bool:
        """Check if CLI command is available."""
        # Check cache first
        if command in self.cli_cache:
            return self.cli_cache[command]
        
        try:
            resolved_command = self._resolve_command_path(command)
            result = subprocess.run(
                [resolved_command, '--version'],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith('win') else 0
            )
            available = result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, OSError):
            try:
                # Try alternative version check
                result = subprocess.run(
                    [resolved_command, '-h'],
                    capture_output=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith('win') else 0
                )
                available = result.returncode == 0
            except:
                available = False
        
        # Cache result
        self.cli_cache[command] = available
        self._save_cli_cache()
        
        return available

    def _check_cli_tools(self):
        """Check availability of all supported CLI tools."""
        self.available_tools.clear()
        
        for engine, (command, _) in SUPPORTED_ENGINES.items():
            if self._is_command_available(command):
                self.available_tools.add(engine)
                self.logger.info(f"✅ {engine.upper()} CLI available: {command}")
            else:
                self.logger.warning(f"❌ {engine.upper()} CLI not found: {command}")

        if not self.available_tools:
            self.logger.error("❌ No diagram rendering tools available!")
        else:
            self.logger.info(f"📊 Available diagram tools: {', '.join(self.available_tools)}")

    def extract_metadata(self, language: str, code: str) -> DiagramMetadata:
        """
        Extract metadata (caption, label) from diagram code.
        
        Args:
            language: Diagram language (mermaid, dot, etc.)
            code: Diagram source code
            
        Returns:
            DiagramMetadata with extracted information
        """
        metadata = DiagramMetadata(language=language)
        lines = code.split('\n')
        
        # Extract caption
        caption_pattern = CAPTION_PATTERNS.get(language)
        if caption_pattern:
            import re
            for line in lines:
                match = re.search(caption_pattern, line)
                if match:
                    # Handle multiple capture groups
                    caption = None
                    for group in match.groups():
                        if group:
                            caption = group.strip()
                            break
                    if caption:
                        metadata.caption = caption
                        break

        # Extract label  
        label_pattern = LABEL_PATTERNS.get(language)
        if label_pattern:
            for line in lines:
                match = re.search(label_pattern, line)
                if match:
                    # Handle multiple capture groups
                    label = None
                    for group in match.groups():
                        if group and group.startswith('fig:'):
                            label = group.strip()
                            break
                    if label:
                        metadata.label = label
                        break

        # Generate content hash for caching
        metadata.hash = hashlib.md5(code.encode('utf-8')).hexdigest()[:12]
        
        return metadata

    def is_engine_available(self, language: str) -> bool:
        """Check if rendering engine for language is available."""
        return language in self.available_tools

    def render_diagram(self, language: str, code: str, metadata: DiagramMetadata) -> Optional[Path]:
        """
        Render diagram to image file with caching.
        
        Args:
            language: Diagram language
            code: Diagram source code
            metadata: Extracted metadata with hash
            
        Returns:
            Path to rendered image file, or None if rendering failed
        """
        if language not in SUPPORTED_ENGINES:
            self.logger.warning(f"Unsupported diagram language: {language}")
            return None
            
        if language not in self.available_tools:
            self.logger.warning(f"CLI tool for {language} not available")
            return None

        try:
            # Generate output filename
            base_name = f"{language}_{metadata.hash}"
            if metadata.label:
                label_clean = metadata.label.replace('fig:', '').replace(':', '_')
                base_name = f"{language}_{label_clean}_{metadata.hash}"
                
            output_file = self.output_dir / f"{base_name}.png"
            
            # Check if cached version exists
            if output_file.exists():
                self.stats.diagrams_cached += 1
                self.logger.debug(f"📦 Using cached diagram: {output_file}")
                return output_file
            
            # Create temporary source file
            temp_source = self.cache_dir / f"{base_name}.{self._get_file_extension(language)}"
            temp_source.write_text(code, encoding='utf-8')
            
            # Get rendering command
            command, args_template = SUPPORTED_ENGINES[language]
            resolved_command = self._resolve_command_path(command)
            
            # Prepare command arguments
            args = []
            for arg in args_template:
                if '{input}' in arg:
                    args.append(arg.replace('{input}', str(temp_source)))
                elif '{output}' in arg:
                    args.append(arg.replace('{output}', str(output_file)))
                else:
                    args.append(arg)
            
            # Execute rendering command
            full_command = [resolved_command] + args
            self.logger.debug(f"🔧 Rendering with: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith('win') else 0
            )
            
            if result.returncode == 0 and output_file.exists():
                self.stats.diagrams_rendered += 1
                self.logger.info(f"✅ Rendered {language} diagram: {output_file}")
                
                # Clean up temp file
                temp_source.unlink(missing_ok=True)
                
                return output_file
            else:
                self.logger.error(f"❌ Failed to render {language} diagram")
                if result.stderr:
                    self.logger.error(f"Error: {result.stderr.decode('utf-8')}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ Diagram rendering timed out: {language}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Diagram rendering failed: {e}")
            return None
        finally:
            self.stats.diagrams_processed += 1

    def _get_file_extension(self, language: str) -> str:
        """Get appropriate file extension for diagram language."""
        extensions = {
            'mermaid': 'mmd',
            'dot': 'dot',
            'graphviz': 'dot', 
            'd2': 'd2',
            'plantuml': 'puml'
        }
        return extensions.get(language, 'txt')

    def download_image(self, url: str) -> Optional[str]:
        """
        Download image from URL and cache it locally.
        
        Args:
            url: Image URL to download
            
        Returns:
            Local file path or None if download failed
        """
        try:
            # Generate filename from URL
            parsed = urllib.parse.urlparse(url)
            filename = Path(parsed.path).name
            if not filename or '.' not in filename:
                filename = f"image_{hashlib.md5(url.encode()).hexdigest()[:8]}.png"
            
            local_path = self.output_dir / filename
            
            # Check if already cached
            if local_path.exists():
                self.logger.debug(f"📦 Using cached image: {filename}")
                return str(local_path)
            
            # Download image
            self.logger.info(f"⬇️ Downloading image: {url}")
            urllib.request.urlretrieve(url, local_path)
            
            if local_path.exists():
                self.logger.info(f"✅ Downloaded image: {filename}")
                return str(local_path)
            else:
                self.logger.error(f"❌ Failed to download image: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Image download failed: {e}")
            return None

    def get_stats(self) -> RenderStats:
        """Get current rendering statistics."""
        if self.stats.diagrams_processed > 0:
            self.stats.cache_hit_rate = self.stats.diagrams_cached / self.stats.diagrams_processed
        return self.stats

    def clear_cache(self):
        """Clear diagram cache."""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(exist_ok=True, parents=True)
            self.logger.info("🗑️ Diagram cache cleared")
        except Exception as e:
            self.logger.error(f"❌ Failed to clear cache: {e}")

    def get_available_engines(self) -> Set[str]:
        """Get set of available diagram engines."""
        return self.available_tools.copy()
