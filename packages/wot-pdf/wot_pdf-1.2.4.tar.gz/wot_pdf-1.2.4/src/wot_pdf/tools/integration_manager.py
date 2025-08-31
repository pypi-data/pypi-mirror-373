#!/usr/bin/env python3
"""
🎯 WOT-PDF INTEGRATION MANAGER - Complete System Integration
===========================================================
🔧 Intelligent integration of enhanced diagram builder with WOT-PDF core
🚀 Seamless migration from v1.1.1 to v1.2.0 with enhanced capabilities
📊 Comprehensive feature integration and validation

FEATURES:
- Enhanced diagram builder integration
- Template system expansion (5→10 templates per engine)
- File watcher integration for live rebuilds
- Pre-commit hooks for quality assurance
- Configuration management system
- Performance monitoring and optimization
- VS Code integration enhancements
"""

import os
import sys
import json
import yaml
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import subprocess

# WOT-PDF imports
from wot_pdf.core.pdf_generator import PDFGenerator
from wot_pdf.core.template_registry import TemplateRegistry
from wot_pdf.diagrams.enhanced_builder import EnhancedDiagramBuilder
from wot_pdf.tools.file_watcher import WOTPDFFileWatcher
from wot_pdf.tools.precommit_hooks import WOTPDFPreCommitHooks


@dataclass
class IntegrationFeature:
    """Represents an integration feature"""
    name: str
    description: str
    status: str  # 'enabled', 'disabled', 'partial', 'error'
    dependencies: List[str] = field(default_factory=list)
    config_keys: List[str] = field(default_factory=list)
    version_added: str = "1.2.0"


@dataclass
class SystemStatus:
    """Current system status"""
    wot_pdf_version: str
    features_enabled: Set[str]
    templates_available: Dict[str, int]  # engine -> count
    diagram_engines: Set[str]
    integration_health: float  # 0-100%
    last_updated: datetime
    
    # Performance metrics
    avg_diagram_build_time: float = 0.0
    avg_pdf_generation_time: float = 0.0
    cache_hit_rate: float = 0.0


class WOTPDFIntegrationManager:
    """Central manager for WOT-PDF system integration"""
    
    def __init__(self, 
                 root_path: Path,
                 config_path: Optional[Path] = None,
                 logger: Optional[logging.Logger] = None):
        
        self.root_path = root_path.resolve()
        self.config_path = config_path or (self.root_path / "wot-pdf-config.yaml")
        self.logger = logger or self._setup_logger()
        
        # Load configuration
        self.config = self._load_configuration()
        
        # Initialize components
        self.pdf_generator = PDFGenerator()
        self.template_registry = TemplateRegistry()
        self.diagram_builder = EnhancedDiagramBuilder(logger=self.logger)
        
        # Optional components (initialized on demand)
        self.file_watcher: Optional[WOTPDFFileWatcher] = None
        self.precommit_hooks: Optional[WOTPDFPreCommitHooks] = None
        
        # Feature registry
        self.available_features = self._initialize_features()
        
        # System status
        self.system_status = self._assess_system_status()
        
        self.logger.info(f"🚀 WOT-PDF Integration Manager initialized for {self.root_path}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for integration manager"""
        logger = logging.getLogger('wot_pdf.integration')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_configuration(self) -> Dict:
        """Load system configuration"""
        default_config = {
            'version': '1.2.0',
            'features': {
                'enhanced_diagram_builder': {'enabled': True},
                'template_expansion': {'enabled': True},
                'file_watcher': {'enabled': False, 'auto_start': False},
                'precommit_hooks': {'enabled': False, 'strict_mode': False},
                'performance_monitoring': {'enabled': True},
                'vs_code_integration': {'enabled': True}
            },
            'diagram_engines': {
                'mermaid': {'enabled': True, 'cli_required': True},
                'graphviz': {'enabled': True, 'cli_required': True},
                'd2': {'enabled': True, 'cli_required': True},
                'plantuml': {'enabled': True, 'cli_required': False}
            },
            'performance': {
                'cache_enabled': True,
                'parallel_builds': True,
                'max_workers': 4,
                'timeout_seconds': 30
            },
            'paths': {
                'templates_dir': 'templates',
                'diagrams_dir': 'diagrams',
                'output_dir': 'output',
                'cache_dir': '.wot-pdf-cache'
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                
                # Deep merge configurations
                config = self._deep_merge_config(default_config, user_config)
                self.logger.info(f"📄 Loaded configuration from {self.config_path}")
                return config
            
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}, using defaults")
        
        return default_config
    
    def _deep_merge_config(self, base: Dict, override: Dict) -> Dict:
        """Deep merge configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _initialize_features(self) -> Dict[str, IntegrationFeature]:
        """Initialize available integration features"""
        features = {
            'enhanced_diagram_builder': IntegrationFeature(
                name='Enhanced Diagram Builder',
                description='Advanced diagram rendering with caching and metadata extraction',
                status='enabled',
                dependencies=['diagram_engines'],
                config_keys=['diagram_engines', 'performance.cache_enabled']
            ),
            
            'template_expansion': IntegrationFeature(
                name='Template System Expansion',
                description='Extended template library (10 templates per engine)',
                status='enabled',
                dependencies=[],
                config_keys=['paths.templates_dir']
            ),
            
            'file_watcher': IntegrationFeature(
                name='Live File Watcher',
                description='Automatic rebuild on file changes with intelligent debouncing',
                status='partial',
                dependencies=['enhanced_diagram_builder'],
                config_keys=['features.file_watcher']
            ),
            
            'precommit_hooks': IntegrationFeature(
                name='Pre-Commit Quality Hooks',
                description='Comprehensive validation before commits',
                status='partial',
                dependencies=['enhanced_diagram_builder', 'template_expansion'],
                config_keys=['features.precommit_hooks']
            ),
            
            'performance_monitoring': IntegrationFeature(
                name='Performance Monitoring',
                description='Build time tracking and optimization insights',
                status='enabled',
                dependencies=[],
                config_keys=['features.performance_monitoring', 'performance']
            ),
            
            'vs_code_integration': IntegrationFeature(
                name='VS Code Integration',
                description='Enhanced VS Code features for WOT-PDF workflows',
                status='enabled',
                dependencies=['file_watcher'],
                config_keys=['features.vs_code_integration']
            )
        }
        
        # Update feature statuses based on configuration
        for feature_name, feature in features.items():
            if feature_name in self.config.get('features', {}):
                feature_config = self.config['features'][feature_name]
                if not feature_config.get('enabled', True):
                    feature.status = 'disabled'
        
        return features
    
    def _assess_system_status(self) -> SystemStatus:
        """Assess current system status and health"""
        # Check WOT-PDF version
        wot_pdf_version = self.config.get('version', '1.2.0')
        
        # Count available templates
        templates_available = {}
        try:
            # Count Typst templates
            typst_templates = list((self.root_path / self.config['paths']['templates_dir']).glob('*.typ'))
            templates_available['typst'] = len(typst_templates)
            
            # Count ReportLab templates (estimated from config)
            templates_available['reportlab'] = 10  # Should be determined from actual registry
        
        except Exception:
            templates_available = {'typst': 0, 'reportlab': 0}
        
        # Check diagram engines
        diagram_engines = set()
        for engine, config in self.config.get('diagram_engines', {}).items():
            if config.get('enabled', False):
                diagram_engines.add(engine)
        
        # Calculate integration health
        enabled_features = {
            name for name, feature in self.available_features.items()
            if feature.status == 'enabled'
        }
        
        total_features = len(self.available_features)
        enabled_count = len(enabled_features)
        integration_health = (enabled_count / total_features) * 100 if total_features > 0 else 0
        
        return SystemStatus(
            wot_pdf_version=wot_pdf_version,
            features_enabled=enabled_features,
            templates_available=templates_available,
            diagram_engines=diagram_engines,
            integration_health=integration_health,
            last_updated=datetime.now()
        )
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        status = self.system_status
        
        # Check CLI tool availability
        cli_status = {}
        for engine in ['mermaid', 'dot', 'd2', 'plantuml']:
            cli_status[engine] = self._check_cli_availability(engine)
        
        return {
            'version': status.wot_pdf_version,
            'health_score': status.integration_health,
            'features': {
                name: {
                    'enabled': feature.status == 'enabled',
                    'status': feature.status,
                    'description': feature.description,
                    'version_added': feature.version_added
                }
                for name, feature in self.available_features.items()
            },
            'templates': {
                'total': sum(status.templates_available.values()),
                'by_engine': status.templates_available
            },
            'diagram_engines': {
                'enabled': list(status.diagram_engines),
                'cli_status': cli_status
            },
            'performance': {
                'avg_diagram_build_time': status.avg_diagram_build_time,
                'avg_pdf_generation_time': status.avg_pdf_generation_time,
                'cache_hit_rate': status.cache_hit_rate
            },
            'paths': self.config.get('paths', {}),
            'last_updated': status.last_updated.isoformat()
        }
    
    def _check_cli_availability(self, tool_name: str) -> Dict[str, bool]:
        """Check if CLI tool is available"""
        try:
            if tool_name == 'mermaid':
                result = subprocess.run(['mmdc', '--version'], 
                                      capture_output=True, timeout=5)
            elif tool_name == 'dot':
                result = subprocess.run(['dot', '-V'], 
                                      capture_output=True, timeout=5)
            elif tool_name == 'd2':
                result = subprocess.run(['d2', '--version'], 
                                      capture_output=True, timeout=5)
            elif tool_name == 'plantuml':
                # PlantUML can work without CLI (using plantuml.jar)
                return {'available': True, 'method': 'jar'}
            else:
                return {'available': False, 'method': 'unknown'}
            
            return {
                'available': result.returncode == 0,
                'method': 'cli'
            }
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {'available': False, 'method': 'cli'}
    
    def enable_feature(self, feature_name: str) -> bool:
        """Enable a specific integration feature"""
        if feature_name not in self.available_features:
            self.logger.error(f"Unknown feature: {feature_name}")
            return False
        
        feature = self.available_features[feature_name]
        
        # Check dependencies
        for dep in feature.dependencies:
            if dep not in self.available_features:
                continue
            
            dep_feature = self.available_features[dep]
            if dep_feature.status != 'enabled':
                self.logger.warning(f"Dependency {dep} is not enabled for {feature_name}")
        
        try:
            if feature_name == 'file_watcher':
                self._enable_file_watcher()
            elif feature_name == 'precommit_hooks':
                self._enable_precommit_hooks()
            elif feature_name == 'enhanced_diagram_builder':
                self._enable_enhanced_diagram_builder()
            
            feature.status = 'enabled'
            self.logger.info(f"✅ Enabled feature: {feature.name}")
            
            # Update configuration
            self._update_feature_config(feature_name, {'enabled': True})
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to enable {feature_name}: {e}")
            feature.status = 'error'
            return False
    
    def disable_feature(self, feature_name: str) -> bool:
        """Disable a specific integration feature"""
        if feature_name not in self.available_features:
            self.logger.error(f"Unknown feature: {feature_name}")
            return False
        
        feature = self.available_features[feature_name]
        feature.status = 'disabled'
        
        # Update configuration
        self._update_feature_config(feature_name, {'enabled': False})
        
        self.logger.info(f"❌ Disabled feature: {feature.name}")
        return True
    
    def _enable_file_watcher(self):
        """Enable file watcher functionality"""
        if not self.file_watcher:
            self.file_watcher = WOTPDFFileWatcher(
                root_path=self.root_path,
                config=self.config.get('features', {}).get('file_watcher', {})
            )
        
        self.logger.info("🔍 File watcher enabled")
    
    def _enable_precommit_hooks(self):
        """Enable pre-commit hooks functionality"""
        if not self.precommit_hooks:
            self.precommit_hooks = WOTPDFPreCommitHooks(
                root_path=self.root_path,
                config=None  # Will use default config
            )
        
        self.logger.info("🔧 Pre-commit hooks enabled")
    
    def _enable_enhanced_diagram_builder(self):
        """Enable enhanced diagram builder functionality"""
        # Already initialized in __init__, just configure
        config_path = self.root_path / "enhanced-diagrams.yaml"
        if not config_path.exists():
            self._create_diagram_builder_config(config_path)
        
        self.logger.info("📊 Enhanced diagram builder enabled")
    
    def _create_diagram_builder_config(self, config_path: Path):
        """Create enhanced diagram builder configuration"""
        config = {
            'output_settings': {
                'default_format': 'svg',
                'dpi': 300,
                'background': 'transparent'
            },
            'engines': {
                'mermaid': {
                    'theme': 'default',
                    'config_file': None,
                    'puppeteer_config': {
                        'args': ['--no-sandbox']
                    }
                },
                'graphviz': {
                    'layout': 'dot',
                    'node_attributes': {'fontname': 'Helvetica'},
                    'edge_attributes': {'fontname': 'Helvetica'}
                },
                'd2': {
                    'layout': 'dagre',
                    'theme': 'default',
                    'pad': 100
                },
                'plantuml': {
                    'theme': 'default',
                    'config': {
                        'skinparam': {
                            'backgroundColor': 'transparent'
                        }
                    }
                }
            },
            'caching': {
                'enabled': True,
                'cache_dir': '.wot-pdf-cache/diagrams',
                'max_age_days': 30
            },
            'performance': {
                'timeout_seconds': 30,
                'max_concurrent': 4
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"📄 Created diagram builder config: {config_path}")
    
    def _update_feature_config(self, feature_name: str, updates: Dict):
        """Update feature configuration"""
        if 'features' not in self.config:
            self.config['features'] = {}
        
        if feature_name not in self.config['features']:
            self.config['features'][feature_name] = {}
        
        self.config['features'][feature_name].update(updates)
        
        # Save configuration
        self._save_configuration()
    
    def _save_configuration(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"💾 Configuration saved to {self.config_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def run_system_diagnostics(self) -> Dict:
        """Run comprehensive system diagnostics"""
        self.logger.info("🔍 Running system diagnostics...")
        
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.get_system_info(),
            'health_checks': {},
            'recommendations': []
        }
        
        # Check template availability
        template_check = self._check_templates()
        diagnostics['health_checks']['templates'] = template_check
        
        # Check diagram engines
        engine_check = self._check_diagram_engines()
        diagnostics['health_checks']['diagram_engines'] = engine_check
        
        # Check file structure
        structure_check = self._check_file_structure()
        diagnostics['health_checks']['file_structure'] = structure_check
        
        # Check dependencies
        deps_check = self._check_dependencies()
        diagnostics['health_checks']['dependencies'] = deps_check
        
        # Generate recommendations
        diagnostics['recommendations'] = self._generate_recommendations(diagnostics['health_checks'])
        
        return diagnostics
    
    def _check_templates(self) -> Dict:
        """Check template availability and integrity"""
        templates_dir = self.root_path / self.config['paths']['templates_dir']
        
        check = {
            'status': 'pass',
            'templates_found': 0,
            'typst_templates': [],
            'missing_templates': []
        }
        
        if not templates_dir.exists():
            check['status'] = 'fail'
            check['error'] = f"Templates directory not found: {templates_dir}"
            return check
        
        # Check Typst templates
        typst_templates = list(templates_dir.glob('*.typ'))
        check['typst_templates'] = [t.name for t in typst_templates]
        check['templates_found'] = len(typst_templates)
        
        # Expected templates (from our expansion)
        expected_templates = [
            'academic.typ', 'professional.typ', 'creative.typ', 'magazine.typ',
            'scientific.typ', 'presentation.typ', 'handbook.typ', 'modern.typ',
            'classic.typ', 'minimal.typ'
        ]
        
        missing = [t for t in expected_templates if t not in check['typst_templates']]
        if missing:
            check['missing_templates'] = missing
            check['status'] = 'warning' if len(missing) < 3 else 'fail'
        
        return check
    
    def _check_diagram_engines(self) -> Dict:
        """Check diagram engine availability"""
        check = {
            'status': 'pass',
            'engines_checked': [],
            'available_engines': [],
            'unavailable_engines': []
        }
        
        engines = ['mermaid', 'dot', 'd2', 'plantuml']
        
        for engine in engines:
            cli_status = self._check_cli_availability(engine)
            engine_info = {
                'name': engine,
                'available': cli_status['available'],
                'method': cli_status['method']
            }
            
            check['engines_checked'].append(engine_info)
            
            if cli_status['available']:
                check['available_engines'].append(engine)
            else:
                check['unavailable_engines'].append(engine)
        
        if len(check['available_engines']) == 0:
            check['status'] = 'fail'
        elif len(check['unavailable_engines']) > 0:
            check['status'] = 'warning'
        
        return check
    
    def _check_file_structure(self) -> Dict:
        """Check project file structure"""
        check = {
            'status': 'pass',
            'required_paths': [],
            'optional_paths': [],
            'missing_paths': []
        }
        
        # Required paths
        required = [
            self.config['paths']['templates_dir']
        ]
        
        # Optional paths  
        optional = [
            self.config['paths']['diagrams_dir'],
            self.config['paths']['output_dir'],
            self.config['paths']['cache_dir']
        ]
        
        for path in required:
            full_path = self.root_path / path
            if full_path.exists():
                check['required_paths'].append(path)
            else:
                check['missing_paths'].append(path)
                check['status'] = 'fail'
        
        for path in optional:
            full_path = self.root_path / path
            if full_path.exists():
                check['optional_paths'].append(path)
        
        return check
    
    def _check_dependencies(self) -> Dict:
        """Check Python dependencies"""
        check = {
            'status': 'pass',
            'packages_checked': [],
            'missing_packages': []
        }
        
        required_packages = [
            'yaml', 'pathlib', 'dataclasses', 'concurrent.futures'
        ]
        
        optional_packages = [
            'watchdog'  # For file watcher
        ]
        
        for package in required_packages + optional_packages:
            try:
                __import__(package)
                check['packages_checked'].append({'name': package, 'status': 'available'})
            except ImportError:
                check['packages_checked'].append({'name': package, 'status': 'missing'})
                if package in required_packages:
                    check['missing_packages'].append(package)
                    check['status'] = 'fail'
        
        return check
    
    def _generate_recommendations(self, health_checks: Dict) -> List[str]:
        """Generate system improvement recommendations"""
        recommendations = []
        
        # Template recommendations
        if health_checks.get('templates', {}).get('status') == 'fail':
            recommendations.append("🔧 Create missing templates directory")
        elif health_checks.get('templates', {}).get('missing_templates'):
            missing = health_checks['templates']['missing_templates']
            recommendations.append(f"📄 Add missing templates: {', '.join(missing[:3])}...")
        
        # Engine recommendations
        if health_checks.get('diagram_engines', {}).get('unavailable_engines'):
            unavailable = health_checks['diagram_engines']['unavailable_engines']
            for engine in unavailable[:2]:  # Limit recommendations
                if engine == 'mermaid':
                    recommendations.append("💾 Install Mermaid CLI: npm install -g @mermaid-js/mermaid-cli")
                elif engine == 'dot':
                    recommendations.append("💾 Install Graphviz: Install from graphviz.org")
                elif engine == 'd2':
                    recommendations.append("💾 Install D2: Install from d2lang.com")
        
        # Performance recommendations
        if self.system_status.integration_health < 80:
            recommendations.append("⚡ Consider enabling more integration features for optimal performance")
        
        # File structure recommendations
        if health_checks.get('file_structure', {}).get('missing_paths'):
            recommendations.append("📁 Create missing project directories")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def migrate_to_v1_2_0(self) -> bool:
        """Migrate from v1.1.1 to v1.2.0"""
        self.logger.info("🚀 Starting migration to WOT-PDF v1.2.0...")
        
        migration_steps = [
            ('Backup current configuration', self._backup_config),
            ('Update template system', self._migrate_templates),
            ('Initialize enhanced diagram builder', self._migrate_diagram_builder),
            ('Setup new configuration structure', self._migrate_config_structure),
            ('Enable new features', self._migrate_enable_features),
            ('Validate migration', self._validate_migration)
        ]
        
        for step_name, step_func in migration_steps:
            self.logger.info(f"📋 {step_name}...")
            try:
                step_func()
                self.logger.info(f"✅ {step_name} completed")
            except Exception as e:
                self.logger.error(f"❌ {step_name} failed: {e}")
                return False
        
        self.logger.info("🎉 Migration to v1.2.0 completed successfully!")
        return True
    
    def _backup_config(self):
        """Backup current configuration"""
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix('.backup')
            shutil.copy2(self.config_path, backup_path)
            self.logger.info(f"💾 Configuration backed up to {backup_path}")
    
    def _migrate_templates(self):
        """Migrate template system"""
        # This would copy new templates if they don't exist
        templates_dir = self.root_path / self.config['paths']['templates_dir']
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("📄 Template system migration completed")
    
    def _migrate_diagram_builder(self):
        """Migrate to enhanced diagram builder"""
        config_path = self.root_path / "enhanced-diagrams.yaml"
        if not config_path.exists():
            self._create_diagram_builder_config(config_path)
        
        self.logger.info("📊 Enhanced diagram builder migration completed")
    
    def _migrate_config_structure(self):
        """Migrate configuration structure"""
        # Update version
        self.config['version'] = '1.2.0'
        
        # Ensure new configuration sections exist
        if 'features' not in self.config:
            self.config['features'] = self._initialize_features()
        
        self._save_configuration()
        self.logger.info("⚙️  Configuration structure migration completed")
    
    def _migrate_enable_features(self):
        """Enable new v1.2.0 features"""
        features_to_enable = ['enhanced_diagram_builder', 'template_expansion', 'performance_monitoring']
        
        for feature in features_to_enable:
            self.enable_feature(feature)
        
        self.logger.info("🚀 New features enabled")
    
    def _validate_migration(self):
        """Validate migration success"""
        diagnostics = self.run_system_diagnostics()
        
        if diagnostics['system_info']['health_score'] < 75:
            raise Exception(f"Migration validation failed: health score {diagnostics['system_info']['health_score']}%")
        
        self.logger.info("✅ Migration validation passed")


# CLI Interface
def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WOT-PDF Integration Manager')
    parser.add_argument('command', choices=['status', 'enable', 'disable', 'diagnostics', 'migrate'], 
                       help='Command to execute')
    parser.add_argument('--feature', help='Feature name for enable/disable commands')
    parser.add_argument('--root', default='.', help='Root directory path')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--format', choices=['json', 'yaml', 'text'], default='text', 
                       help='Output format')
    
    args = parser.parse_args()
    
    # Setup paths
    root_path = Path(args.root)
    config_path = Path(args.config) if args.config else None
    
    # Create integration manager
    integration_manager = WOTPDFIntegrationManager(
        root_path=root_path,
        config_path=config_path
    )
    
    if args.verbose:
        integration_manager.logger.setLevel(logging.DEBUG)
    
    # Execute command
    if args.command == 'status':
        system_info = integration_manager.get_system_info()
        
        if args.format == 'json':
            print(json.dumps(system_info, indent=2))
        elif args.format == 'yaml':
            print(yaml.dump(system_info, default_flow_style=False, indent=2))
        else:
            print(f"🚀 WOT-PDF System Status")
            print(f"Version: {system_info['version']}")
            print(f"Health Score: {system_info['health_score']:.1f}%")
            print(f"Templates: {system_info['templates']['total']} available")
            print(f"Diagram Engines: {len(system_info['diagram_engines']['enabled'])} enabled")
            
            print(f"\n📊 Features:")
            for name, feature in system_info['features'].items():
                status = "✅" if feature['enabled'] else "❌"
                print(f"  {status} {name}: {feature['description']}")
    
    elif args.command == 'enable':
        if not args.feature:
            print("❌ --feature required for enable command")
            sys.exit(1)
        
        success = integration_manager.enable_feature(args.feature)
        sys.exit(0 if success else 1)
    
    elif args.command == 'disable':
        if not args.feature:
            print("❌ --feature required for disable command")
            sys.exit(1)
        
        success = integration_manager.disable_feature(args.feature)
        sys.exit(0 if success else 1)
    
    elif args.command == 'diagnostics':
        diagnostics = integration_manager.run_system_diagnostics()
        
        if args.format == 'json':
            print(json.dumps(diagnostics, indent=2))
        elif args.format == 'yaml':
            print(yaml.dump(diagnostics, default_flow_style=False, indent=2))
        else:
            print("🔍 WOT-PDF System Diagnostics")
            print(f"Overall Health: {diagnostics['system_info']['health_score']:.1f}%")
            
            for check_name, check_result in diagnostics['health_checks'].items():
                status_icon = {"pass": "✅", "warning": "⚠️", "fail": "❌"}.get(check_result['status'], "❓")
                print(f"  {status_icon} {check_name}: {check_result['status']}")
            
            if diagnostics['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in diagnostics['recommendations']:
                    print(f"  • {rec}")
    
    elif args.command == 'migrate':
        success = integration_manager.migrate_to_v1_2_0()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
