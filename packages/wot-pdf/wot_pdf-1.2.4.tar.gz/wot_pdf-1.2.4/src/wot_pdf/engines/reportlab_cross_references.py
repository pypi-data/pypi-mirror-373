#!/usr/bin/env python3
"""
🔗 CROSS-REFERENCE SYSTEM FOR REPORTLAB
======================================
⚡ Professional cross-reference system supporting @fig:, @tbl:, @sec: references
🔷 Automatic numbering and linking system
📊 Compatible with academic and technical document standards

SUPPORTED REFERENCES:
- @fig:label - Figure references
- @tbl:label - Table references  
- @sec:label - Section references
- @eq:label - Equation references (future)
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class CrossReference:
    """Cross-reference entry"""
    ref_type: str  # 'fig', 'tbl', 'sec', 'eq'
    label: str     # User-defined label
    number: str    # Auto-generated number
    title: str     # Caption/title text
    page: int = 0  # Page number (if available)

class CrossReferenceManager:
    """
    Professional cross-reference management system
    Handles automatic numbering and reference resolution
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.references: Dict[str, CrossReference] = {}
        self.counters = {
            'fig': 0,
            'tbl': 0,
            'sec': 0,
            'eq': 0
        }
        
        # Reference patterns
        self.ref_patterns = {
            'figure_caption': re.compile(r'!\[([^\]]*)\]\([^)]*\)\s*{#fig:([^}]+)}'),
            'table_caption': re.compile(r'^{#tbl:([^}]+)}$'),  # Table label on separate line
            'section_label': re.compile(r'^(#{1,6})\s+([^{]+)\s*{#sec:([^}]+)}'),
            'reference_link': re.compile(r'@(fig|tbl|sec|eq):([a-zA-Z0-9_-]+)')
        }
        
        self.logger.info("🔗 Cross-Reference Manager initialized")
    
    def scan_content_for_references(self, content: str) -> str:
        """
        Scan content for reference definitions and create reference database
        Returns content with processed reference definitions
        """
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = line
            
            # Debug: Show what we're scanning
            if '@' in line or '{#' in line:
                self.logger.info(f"🔍 Scanning line: {line.strip()}")
            
            # Scan for figure captions with labels
            fig_match = self.ref_patterns['figure_caption'].search(line)
            if fig_match:
                caption = fig_match.group(1).strip()
                label = fig_match.group(2)
                
                self.logger.info(f"✅ Found figure: {label} - {caption}")
                
                # Generate figure number
                self.counters['fig'] += 1
                fig_number = str(self.counters['fig'])
                
                # Store reference
                self.references[f"fig:{label}"] = CrossReference(
                    ref_type='fig',
                    label=label,
                    number=fig_number,
                    title=caption
                )
                
                # Replace with numbered caption
                full_caption = f"Figure {fig_number}: {caption}" if caption else f"Figure {fig_number}"
                processed_line = re.sub(r'!\[([^\]]*)\]\(([^)]*)\)\s*{#fig:([^}]+)}',
                                      f'![{full_caption}](\\2)', line)
                
                self.logger.debug(f"📊 Registered figure reference: fig:{label} = Figure {fig_number}")
            
            # Scan for table captions with labels
            tbl_match = self.ref_patterns['table_caption'].search(line)
            if tbl_match:
                label = tbl_match.group(1)
                
                self.logger.info(f"✅ Found table: {label}")
                
                self.counters['tbl'] += 1
                tbl_number = str(self.counters['tbl'])
                
                self.references[f"tbl:{label}"] = CrossReference(
                    ref_type='tbl',
                    label=label,
                    number=tbl_number,
                    title=f"Table {tbl_number}"
                )
                
                # Instead of replacing with caption, mark for table processing
                # This will be handled by Enhanced Engine's table processor
                processed_line = f"{{TABLE_CAPTION:{label}:Table {tbl_number}}}"
                
                self.logger.debug(f"📊 Registered table reference: tbl:{label} = Table {tbl_number}")
            
            # Scan for section labels
            sec_match = self.ref_patterns['section_label'].search(line)
            if sec_match:
                level_markers = sec_match.group(1)
                title = sec_match.group(2).strip()
                label = sec_match.group(3)
                
                # Generate section number (simple sequential for now)
                self.counters['sec'] += 1
                sec_number = str(self.counters['sec'])
                
                # Store reference
                self.references[f"sec:{label}"] = CrossReference(
                    ref_type='sec',
                    label=label,
                    number=sec_number,
                    title=title
                )
                
                # Remove label from heading
                processed_line = f"{level_markers} {title}"
                
                self.logger.debug(f"📊 Registered section reference: sec:{label} = Section {sec_number}")
            
            processed_lines.append(processed_line)
        
        processed_content = '\n'.join(processed_lines)
        
        # Now resolve all cross-references
        processed_content = self.resolve_references(processed_content)
        
        self.logger.info(f"✅ Cross-reference scan completed: {len(self.references)} references found")
        return processed_content
    
    def resolve_references(self, content: str) -> str:
        """
        Resolve all @fig:, @tbl:, @sec: references to proper links
        """
        def replace_reference(match):
            ref_type = match.group(1)
            label = match.group(2)
            ref_key = f"{ref_type}:{label}"
            
            if ref_key in self.references:
                ref = self.references[ref_key]
                if ref_type == 'fig':
                    return f"Figure {ref.number}"
                elif ref_type == 'tbl':
                    return f"Table {ref.number}"
                elif ref_type == 'sec':
                    return f"Section {ref.number}"
                elif ref_type == 'eq':
                    return f"Equation {ref.number}"
            else:
                self.logger.warning(f"⚠️ Unresolved reference: {ref_key}")
                return f"[{ref_type}:{label}]"
        
        # Replace all references
        resolved_content = self.ref_patterns['reference_link'].sub(replace_reference, content)
        
        resolved_count = len(self.ref_patterns['reference_link'].findall(content))
        if resolved_count > 0:
            self.logger.info(f"🔗 Resolved {resolved_count} cross-references")
        
        return resolved_content
    
    def generate_list_of_figures(self) -> str:
        """Generate list of figures"""
        if not any(ref.ref_type == 'fig' for ref in self.references.values()):
            return ""
        
        lines = ["## List of Figures\n"]
        
        for ref_key, ref in sorted(self.references.items()):
            if ref.ref_type == 'fig':
                lines.append(f"- Figure {ref.number}: {ref.title}")
        
        return '\n'.join(lines) + '\n'
    
    def generate_list_of_tables(self) -> str:
        """Generate list of tables"""
        if not any(ref.ref_type == 'tbl' for ref in self.references.values()):
            return ""
        
        lines = ["## List of Tables\n"]
        
        for ref_key, ref in sorted(self.references.items()):
            if ref.ref_type == 'tbl':
                lines.append(f"- Table {ref.number}: {ref.title}")
        
        return '\n'.join(lines) + '\n'
    
    def get_reference_statistics(self) -> Dict[str, Any]:
        """Get cross-reference statistics"""
        stats = {
            'total_references': len(self.references),
            'by_type': {
                'figures': len([r for r in self.references.values() if r.ref_type == 'fig']),
                'tables': len([r for r in self.references.values() if r.ref_type == 'tbl']),
                'sections': len([r for r in self.references.values() if r.ref_type == 'sec']),
                'equations': len([r for r in self.references.values() if r.ref_type == 'eq'])
            },
            'references_list': list(self.references.keys())
        }
        
        return stats


class FigureCaptionProcessor:
    """
    HIGH PRIORITY 2: Figure captions and numbering
    Professional figure caption processing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.figure_counter = 0
        
        # Enhanced figure patterns
        self.patterns = {
            'labeled_figure': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)\s*{#fig:([^}]+)}'),
            'simple_figure': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)(?!\s*{#)'),
            'bare_image': re.compile(r'!\[\]\(([^)]+)\)')
        }
        
        self.logger.info("🖼️ Figure Caption Processor initialized")
    
    def process_figure_captions(self, content: str) -> str:
        """
        Process all figure captions and add professional numbering
        Works with both labeled and unlabeled figures
        """
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = line
            
            # Handle labeled figures (already processed by CrossReferenceManager)
            if self.patterns['labeled_figure'].search(line):
                processed_lines.append(processed_line)
                continue
            
            # Handle simple figures with alt text
            simple_match = self.patterns['simple_figure'].search(line)
            if simple_match:
                alt_text = simple_match.group(1).strip()
                image_path = simple_match.group(2)
                
                self.figure_counter += 1
                
                if alt_text:
                    caption = f"Figure {self.figure_counter}: {alt_text}"
                else:
                    caption = f"Figure {self.figure_counter}"
                
                processed_line = f"![{caption}]({image_path})"
                
                self.logger.debug(f"📊 Processed simple figure: Figure {self.figure_counter}")
            
            # Handle bare images without alt text
            bare_match = self.patterns['bare_image'].search(line)
            if bare_match and not simple_match:  # Avoid double processing
                image_path = bare_match.group(1)
                
                self.figure_counter += 1
                caption = f"Figure {self.figure_counter}"
                
                processed_line = f"![{caption}]({image_path})"
                
                self.logger.debug(f"📊 Processed bare image: Figure {self.figure_counter}")
            
            processed_lines.append(processed_line)
        
        if self.figure_counter > 0:
            self.logger.info(f"✅ Processed {self.figure_counter} figures with captions")
        
        return '\n'.join(processed_lines)


def create_cross_reference_system():
    """
    Factory function to create complete cross-reference system
    """
    return {
        'cross_ref_manager': CrossReferenceManager(),
        'figure_processor': FigureCaptionProcessor()
    }
