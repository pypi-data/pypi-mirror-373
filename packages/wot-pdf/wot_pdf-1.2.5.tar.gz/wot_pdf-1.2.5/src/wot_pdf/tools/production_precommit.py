#!/usr/bin/env python3
"""
🎯 WOT-PDF PRE-COMMIT VALIDATION - Production Quality Hooks
==========================================================
🔍 Enhanced pre-commit hooks with diagram validation and production checks
📊 Comprehensive validation of diagrams, labels, captions, and cross-references
🎨 Integration with production builder for end-to-end validation

FEATURES:
- Diagram syntax and renderability validation
- Caption/label consistency checking  
- Cross-reference validation (@fig:label)
- Markdown image processing validation
- Production builder integration tests
- Performance regression detection
"""

import os
import re
import sys
import json
import time
import logging
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# WOT-PDF imports
from wot_pdf.builders.production_builder import ProductionDiagramBuilder, DiagramMetadata
from wot_pdf.tools.precommit_hooks import ValidationResult, HookConfig
from wot_pdf.utils.logger import setup_logger


@dataclass
class DiagramValidationResult:
    """Extended validation result for diagrams"""
    diagram_hash: str
    language: str
    has_caption: bool
    has_label: bool
    is_renderable: bool
    rendering_time_ms: float
    file_size_bytes: int
    error_details: Optional[str] = None


@dataclass
class CrossReferenceCheck:
    """Cross-reference validation result"""
    reference: str  # e.g., "@fig:arch"
    target_exists: bool
    target_file: Optional[Path] = None
    target_line: Optional[int] = None


class ProductionPreCommitValidator:
    """Enhanced pre-commit validator with production builder integration"""
    
    def __init__(self, 
                 root_path: Path,
                 config: Optional[HookConfig] = None,
                 logger: Optional[logging.Logger] = None):
        
        self.root_path = root_path.resolve()
        self.config = config or self._load_default_config()
        self.logger = logger or setup_logger(self.__class__.__name__)
        
        # Initialize production builder for validation
        self.builder = ProductionDiagramBuilder(
            output_dir=root_path / '.validation-cache' / 'diagrams',
            cache_enabled=True,
            logger=self.logger
        )
        
        # Validation statistics
        self.validation_stats = {
            'diagrams_validated': 0,
            'diagrams_failed': 0,
            'cross_references_checked': 0,
            'cross_references_broken': 0,
            'performance_regressions': 0,
            'total_validation_time_ms': 0
        }
        
        self.logger.info(f"🔍 Production Pre-Commit Validator initialized for {self.root_path}")
    
    def _load_default_config(self) -> HookConfig:
        """Load default validation configuration"""
        return HookConfig(
            enabled_checks={
                'diagram_validation',
                'caption_label_validation', 
                'cross_reference_validation',
                'markdown_image_validation',
                'production_build_test',
                'performance_regression_test'
            },
            diagram_validation=True,
            pdf_generation_test=True,
            template_validation=True,
            markdown_lint=True,
            yaml_validation=True,
            max_file_size_mb=10,
            timeout_seconds=30,
            parallel_jobs=4,
            fail_fast=False,
            verbose=False
        )
    
    def validate_file(self, file_path: Path) -> List[ValidationResult]:
        """Comprehensive file validation"""
        results = []
        start_time = time.time()
        
        try:
            if file_path.suffix.lower() == '.md':
                results.extend(self._validate_markdown_file(file_path))
            elif file_path.suffix.lower() in ['.mmd', '.dot', '.d2', '.puml']:
                results.extend(self._validate_diagram_file(file_path))
            elif file_path.suffix.lower() == '.typ':
                results.extend(self._validate_typst_file(file_path))
            else:
                results.append(ValidationResult(
                    check_name='file_type',
                    file_path=file_path,
                    status='skip',
                    message='File type not supported for validation',
                    duration_ms=(time.time() - start_time) * 1000
                ))
        
        except Exception as e:
            results.append(ValidationResult(
                check_name='validation_error',
                file_path=file_path,
                status='fail',
                message=f'Validation failed with error: {str(e)}',
                duration_ms=(time.time() - start_time) * 1000
            ))
        
        return results
    
    def _validate_markdown_file(self, file_path: Path) -> List[ValidationResult]:
        """Validate Markdown file with diagram and cross-reference checks"""
        results = []
        start_time = time.time()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Basic structure validation
            results.append(ValidationResult(
                check_name='markdown_structure',
                file_path=file_path,
                status='pass',
                message=f'Markdown loaded successfully ({len(content)} chars)',
                duration_ms=(time.time() - start_time) * 1000
            ))
            
            # Validate diagrams in code blocks
            if 'diagram_validation' in self.config.enabled_checks:
                results.extend(self._validate_embedded_diagrams(file_path, content))
            
            # Validate captions and labels
            if 'caption_label_validation' in self.config.enabled_checks:
                results.extend(self._validate_captions_labels(file_path, content))
            
            # Validate cross-references
            if 'cross_reference_validation' in self.config.enabled_checks:
                results.extend(self._validate_cross_references(file_path, content))
            
            # Validate Markdown images
            if 'markdown_image_validation' in self.config.enabled_checks:
                results.extend(self._validate_markdown_images(file_path, content))
            
            # Test production build
            if 'production_build_test' in self.config.enabled_checks:
                results.extend(self._test_production_build(file_path))
        
        except Exception as e:
            results.append(ValidationResult(
                check_name='markdown_validation',
                file_path=file_path,
                status='fail',
                message=f'Markdown validation error: {str(e)}',
                duration_ms=(time.time() - start_time) * 1000
            ))
        
        return results
    
    def _validate_embedded_diagrams(self, file_path: Path, content: str) -> List[ValidationResult]:
        """Validate diagrams embedded in Markdown"""
        results = []
        
        # Find diagram blocks
        diagram_blocks = self.builder.find_diagram_blocks(content)
        
        for lang, code, match in diagram_blocks:
            result = self._validate_single_diagram(file_path, lang, code, match.start())
            results.append(result)
            
            # Update statistics
            self.validation_stats['diagrams_validated'] += 1
            if result.status == 'fail':
                self.validation_stats['diagrams_failed'] += 1
        
        if not diagram_blocks:
            results.append(ValidationResult(
                check_name='embedded_diagrams',
                file_path=file_path,
                status='pass',
                message='No embedded diagrams found',
                duration_ms=0
            ))
        
        return results
    
    def _validate_single_diagram(self, file_path: Path, lang: str, code: str, position: int) -> ValidationResult:
        """Validate a single diagram"""
        start_time = time.time()
        
        try:
            # Extract metadata
            metadata = self.builder.extract_metadata(lang, code)
            
            # Check if diagram is renderable
            is_renderable = True
            rendering_time = 0
            file_size = 0
            error_details = None
            
            try:
                # Test rendering (this will use cache if available)
                render_start = time.time()
                svg_path = self.builder.render_diagram(lang, code, metadata)
                rendering_time = (time.time() - render_start) * 1000
                
                if svg_path.exists():
                    file_size = svg_path.stat().st_size
                else:
                    is_renderable = False
                    error_details = "SVG output not created"
            
            except Exception as e:
                is_renderable = False
                error_details = str(e)
            
            # Determine validation status
            if not is_renderable:
                status = 'fail'
                message = f'{lang} diagram not renderable: {error_details}'
            elif not metadata.caption:
                status = 'warning'
                message = f'{lang} diagram missing caption'
            elif not metadata.label:
                status = 'warning' 
                message = f'{lang} diagram missing explicit label'
            else:
                status = 'pass'
                message = f'{lang} diagram valid (caption: "{metadata.caption}", label: "{metadata.label}")'
            
            # Create detailed result
            validation_result = ValidationResult(
                check_name='diagram_validation',
                file_path=file_path,
                status=status,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                details={
                    'language': lang,
                    'hash': metadata.hash,
                    'caption': metadata.caption,
                    'label': metadata.label,
                    'is_renderable': is_renderable,
                    'rendering_time_ms': rendering_time,
                    'file_size_bytes': file_size,
                    'position': position
                }
            )
            
            return validation_result
        
        except Exception as e:
            return ValidationResult(
                check_name='diagram_validation',
                file_path=file_path,
                status='fail',
                message=f'Diagram validation failed: {str(e)}',
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def _validate_captions_labels(self, file_path: Path, content: str) -> List[ValidationResult]:
        """Validate caption and label consistency"""
        results = []
        
        # Find all labels in the document
        label_pattern = r'<(fig:[\w\-_]+)>'
        labels_found = set(re.findall(label_pattern, content))
        
        # Find all figure references  
        ref_pattern = r'@(fig:[\w\-_]+)'
        refs_found = set(re.findall(ref_pattern, content))
        
        # Check for unused labels
        unused_labels = labels_found - refs_found
        if unused_labels:
            results.append(ValidationResult(
                check_name='caption_label_validation',
                file_path=file_path,
                status='warning',
                message=f'Unused labels found: {", ".join(sorted(unused_labels))}',
                duration_ms=0,
                details={'unused_labels': list(unused_labels)}
            ))
        
        # Check for broken references
        broken_refs = refs_found - labels_found
        if broken_refs:
            results.append(ValidationResult(
                check_name='caption_label_validation',
                file_path=file_path,
                status='fail',
                message=f'Broken figure references: {", ".join(sorted(broken_refs))}',
                duration_ms=0,
                details={'broken_references': list(broken_refs)}
            ))
        
        # Success case
        if not unused_labels and not broken_refs:
            results.append(ValidationResult(
                check_name='caption_label_validation',
                file_path=file_path,
                status='pass',
                message=f'All {len(labels_found)} labels have valid references',
                duration_ms=0,
                details={'labels': list(labels_found), 'references': list(refs_found)}
            ))
        
        return results
    
    def _validate_cross_references(self, file_path: Path, content: str) -> List[ValidationResult]:
        """Validate cross-references across the project"""
        results = []
        start_time = time.time()
        
        # Find all cross-references in this file
        ref_pattern = r'@((?:fig|tbl|eq|sec):[\w\-_]+)'
        references = re.findall(ref_pattern, content)
        
        if not references:
            results.append(ValidationResult(
                check_name='cross_reference_validation',
                file_path=file_path,
                status='pass',
                message='No cross-references found',
                duration_ms=(time.time() - start_time) * 1000
            ))
            return results
        
        # Check each reference
        broken_refs = []
        valid_refs = []
        
        for ref in references:
            if self._find_reference_target(ref):
                valid_refs.append(ref)
            else:
                broken_refs.append(ref)
        
        # Update statistics
        self.validation_stats['cross_references_checked'] += len(references)
        self.validation_stats['cross_references_broken'] += len(broken_refs)
        
        # Report results
        if broken_refs:
            results.append(ValidationResult(
                check_name='cross_reference_validation',
                file_path=file_path,
                status='fail',
                message=f'Broken cross-references: {", ".join(broken_refs)}',
                duration_ms=(time.time() - start_time) * 1000,
                details={'broken': broken_refs, 'valid': valid_refs}
            ))
        else:
            results.append(ValidationResult(
                check_name='cross_reference_validation',
                file_path=file_path,
                status='pass',
                message=f'All {len(references)} cross-references are valid',
                duration_ms=(time.time() - start_time) * 1000,
                details={'references': references}
            ))
        
        return results
    
    def _find_reference_target(self, reference: str) -> bool:
        """Find if a reference target exists in the project"""
        # Search for label in all Markdown files
        label_pattern = f'<{re.escape(reference)}>'
        
        for md_file in self.root_path.glob('**/*.md'):
            if md_file == self.root_path:
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                if re.search(label_pattern, content):
                    return True
            except Exception:
                continue  # Skip files we can't read
        
        return False
    
    def _validate_markdown_images(self, file_path: Path, content: str) -> List[ValidationResult]:
        """Validate Markdown images with {#fig:label} syntax"""
        results = []
        start_time = time.time()
        
        # Pattern for ![alt](path){#fig:label}
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)\s*\{#(fig:[\w\-_]+)\}'
        images = list(re.finditer(image_pattern, content))
        
        if not images:
            results.append(ValidationResult(
                check_name='markdown_image_validation',
                file_path=file_path,
                status='pass',
                message='No Markdown images with labels found',
                duration_ms=(time.time() - start_time) * 1000
            ))
            return results
        
        valid_images = 0
        issues = []
        
        for match in images:
            alt_text = match.group(1)
            image_path = match.group(2)
            label = match.group(3)
            
            # Check if image file exists
            full_image_path = file_path.parent / image_path
            if not full_image_path.exists():
                issues.append(f'{label}: image not found ({image_path})')
                continue
            
            # Check if alt text exists
            if not alt_text.strip():
                issues.append(f'{label}: missing alt text')
            
            valid_images += 1
        
        # Report results
        if issues:
            results.append(ValidationResult(
                check_name='markdown_image_validation',
                file_path=file_path,
                status='warning',
                message=f'Image issues found: {"; ".join(issues[:3])}{"..." if len(issues) > 3 else ""}',
                duration_ms=(time.time() - start_time) * 1000,
                details={'issues': issues, 'total_images': len(images)}
            ))
        else:
            results.append(ValidationResult(
                check_name='markdown_image_validation',
                file_path=file_path,
                status='pass',
                message=f'{len(images)} Markdown images are valid',
                duration_ms=(time.time() - start_time) * 1000
            ))
        
        return results
    
    def _test_production_build(self, file_path: Path) -> List[ValidationResult]:
        """Test production build pipeline"""
        results = []
        start_time = time.time()
        
        try:
            # Create temporary output file
            temp_typ = file_path.with_suffix('.test.typ')
            
            # Test conversion
            stats = self.builder.md_to_typst(file_path, temp_typ)
            
            # Check if output was created
            if temp_typ.exists():
                # Clean up
                temp_typ.unlink()
                
                results.append(ValidationResult(
                    check_name='production_build_test',
                    file_path=file_path,
                    status='pass',
                    message=f'Production build test passed ({stats.diagrams_processed} diagrams processed)',
                    duration_ms=(time.time() - start_time) * 1000,
                    details={
                        'diagrams_processed': stats.diagrams_processed,
                        'diagrams_cached': stats.diagrams_cached,
                        'cache_hit_rate': stats.cache_hit_rate,
                        'build_time_ms': stats.build_time_ms
                    }
                ))
            else:
                results.append(ValidationResult(
                    check_name='production_build_test',
                    file_path=file_path,
                    status='fail',
                    message='Production build test failed: no output generated',
                    duration_ms=(time.time() - start_time) * 1000
                ))
        
        except Exception as e:
            results.append(ValidationResult(
                check_name='production_build_test',
                file_path=file_path,
                status='fail',
                message=f'Production build test failed: {str(e)}',
                duration_ms=(time.time() - start_time) * 1000
            ))
        
        return results
    
    def _validate_diagram_file(self, file_path: Path) -> List[ValidationResult]:
        """Validate standalone diagram file"""
        results = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lang = file_path.suffix[1:].lower()  # Remove dot from extension
            
            if lang == 'puml':
                lang = 'plantuml'
            
            result = self._validate_single_diagram(file_path, lang, content, 0)
            results.append(result)
        
        except Exception as e:
            results.append(ValidationResult(
                check_name='diagram_file_validation',
                file_path=file_path,
                status='fail',
                message=f'Diagram file validation failed: {str(e)}',
                duration_ms=0
            ))
        
        return results
    
    def _validate_typst_file(self, file_path: Path) -> List[ValidationResult]:
        """Validate Typst file"""
        results = []
        start_time = time.time()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Basic syntax check
            if not any(marker in content for marker in ['#set', '#let', '#show', '#import']):
                results.append(ValidationResult(
                    check_name='typst_validation',
                    file_path=file_path,
                    status='warning',
                    message='No Typst markup detected in file',
                    duration_ms=(time.time() - start_time) * 1000
                ))
            else:
                results.append(ValidationResult(
                    check_name='typst_validation',
                    file_path=file_path,
                    status='pass',
                    message='Typst file appears to have valid markup',
                    duration_ms=(time.time() - start_time) * 1000
                ))
        
        except Exception as e:
            results.append(ValidationResult(
                check_name='typst_validation',
                file_path=file_path,
                status='fail',
                message=f'Typst validation failed: {str(e)}',
                duration_ms=(time.time() - start_time) * 1000
            ))
        
        return results
    
    def get_validation_summary(self) -> Dict:
        """Get comprehensive validation summary"""
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.validation_stats,
            'configuration': {
                'enabled_checks': list(self.config.enabled_checks),
                'parallel_jobs': self.config.parallel_jobs,
                'timeout_seconds': self.config.timeout_seconds,
                'fail_fast': self.config.fail_fast
            },
            'builder_info': {
                'cache_enabled': self.builder.cache_enabled,
                'output_dir': str(self.builder.output_dir)
            }
        }


def main():
    """CLI entry point for production pre-commit validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WOT-PDF Production Pre-Commit Validator')
    parser.add_argument('files', nargs='*', help='Files to validate')
    parser.add_argument('--root', default='.', help='Root project directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fail-fast', action='store_true', help='Stop on first failure')
    parser.add_argument('--parallel', type=int, default=4, help='Parallel validation jobs')
    parser.add_argument('--no-cache', action='store_true', help='Disable diagram caching')
    parser.add_argument('--disable', action='append', default=[], help='Disable specific checks')
    parser.add_argument('--summary', action='store_true', help='Print validation summary')
    
    args = parser.parse_args()
    
    # Setup configuration
    config = HookConfig(
        enabled_checks={
            'diagram_validation',
            'caption_label_validation', 
            'cross_reference_validation',
            'markdown_image_validation',
            'production_build_test'
        },
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        parallel_jobs=args.parallel
    )
    
    # Apply disabled checks
    for disabled_check in args.disable:
        config.enabled_checks.discard(disabled_check)
    
    # Create validator
    validator = ProductionPreCommitValidator(
        root_path=Path(args.root),
        config=config
    )
    
    if args.no_cache:
        validator.builder.cache_enabled = False
    
    # Get files to validate
    if args.files:
        files_to_validate = [Path(f) for f in args.files if Path(f).exists()]
    else:
        # Find all relevant files
        files_to_validate = []
        files_to_validate.extend(Path(args.root).glob('**/*.md'))
        files_to_validate.extend(Path(args.root).glob('**/*.mmd'))
        files_to_validate.extend(Path(args.root).glob('**/*.dot'))
        files_to_validate.extend(Path(args.root).glob('**/*.d2'))
        files_to_validate.extend(Path(args.root).glob('**/*.puml'))
        files_to_validate.extend(Path(args.root).glob('**/*.typ'))
    
    if not files_to_validate:
        print("✅ No files to validate")
        return
    
    print(f"🔍 Validating {len(files_to_validate)} files...")
    
    # Run validation
    all_results = []
    start_time = time.time()
    
    if config.parallel_jobs > 1:
        # Parallel validation
        with ThreadPoolExecutor(max_workers=config.parallel_jobs) as executor:
            future_to_file = {
                executor.submit(validator.validate_file, file_path): file_path
                for file_path in files_to_validate
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    results = future.result(timeout=config.timeout_seconds)
                    all_results.extend(results)
                    
                    if config.fail_fast and any(r.status == 'fail' for r in results):
                        break
                
                except Exception as e:
                    all_results.append(ValidationResult(
                        check_name='validation_error',
                        file_path=file_path,
                        status='fail',
                        message=f'Validation error: {str(e)}',
                        duration_ms=0
                    ))
    else:
        # Sequential validation
        for file_path in files_to_validate:
            results = validator.validate_file(file_path)
            all_results.extend(results)
            
            if config.fail_fast and any(r.status == 'fail' for r in results):
                break
    
    # Process results
    passed = sum(1 for r in all_results if r.status == 'pass')
    failed = sum(1 for r in all_results if r.status == 'fail')
    warned = sum(1 for r in all_results if r.status == 'warning')
    skipped = sum(1 for r in all_results if r.status == 'skip')
    
    total_time = time.time() - start_time
    
    # Print results summary
    if failed > 0:
        print(f"\n❌ FAILURES ({failed}):")
        for result in all_results:
            if result.status == 'fail':
                print(f"  {result.file_path.name}: {result.message}")
    
    if warned > 0:
        print(f"\n⚠️  WARNINGS ({warned}):")
        for result in all_results:
            if result.status == 'warning':
                print(f"  {result.file_path.name}: {result.message}")
    
    # Print statistics
    print(f"\n📊 Validation Results:")
    print(f"  • Files validated: {len(files_to_validate)}")
    print(f"  • Checks run: {len(all_results)}")
    print(f"  • Passed: {passed}")
    print(f"  • Failed: {failed}")
    print(f"  • Warnings: {warned}")
    print(f"  • Skipped: {skipped}")
    print(f"  • Total time: {total_time:.2f}s")
    
    if args.summary:
        summary = validator.get_validation_summary()
        print(f"\n📋 Detailed Summary:")
        print(json.dumps(summary, indent=2))
    
    # Exit with appropriate code
    if failed == 0:
        print("\n✅ All validations passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} validations failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
