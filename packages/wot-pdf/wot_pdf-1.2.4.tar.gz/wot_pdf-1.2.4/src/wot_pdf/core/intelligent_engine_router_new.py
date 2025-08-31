#!/usr/bin/env python3
"""
🎯 INTELLIGENT ENGINE ROUTER - SMART PDF GENERATION ROUTING
===========================================================
⚡ Dynamic engine selection based on content analysis
🔷 Routes to optimal PDF generation engine (Typst vs ReportLab)
📊 Content complexity analysis and optimization

FEATURES:
- Intelligent content analysis and complexity scoring
- Dynamic engine routing (Typst primary, ReportLab fallback)
- Environment variable overrides (FORCE_TYPST, FORCE_REPORTLAB)
- Detailed recommendation reporting
- Content preprocessing and optimization

This is the brain of the WOT-PDF system - it analyzes your content
and routes it to the optimal PDF generation engine for the best results.

USAGE EXAMPLES:
    # Basic usage
    router = IntelligentEngineRouter()
    result = router.route_content(content, output_path)
    
    # With custom settings
    result = router.route_content(
        content, output_path, 
        force_engine="typst",
        get_recommendation_only=True
    )
    
    # Analyze content without generating
    analysis = router.analyze_content(content)
    print(f"Complexity: {analysis.complexity_score}")
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Import our modular components
from .content_analyzer import ContentAnalyzer, ContentAnalysisResults
from .engine_selector import EngineSelector, EngineType
from .content_preprocessor import ContentPreprocessor


class IntelligentEngineRouter:
    """
    🎯 MAIN ROUTER CLASS
    ===================
    Orchestrates content analysis, engine selection, and preprocessing
    for optimal PDF generation routing.
    
    This class coordinates all the modular components to provide
    intelligent routing decisions based on content complexity.
    """
    
    def __init__(self):
        """Initialize router with all components."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize modular components
        self.content_analyzer = ContentAnalyzer()
        self.engine_selector = EngineSelector()
        self.content_preprocessor = ContentPreprocessor()
        
        # Router settings
        self.settings = {
            'enable_preprocessing': True,
            'detailed_reporting': True,
            'cache_analysis': True
        }
        
        self.logger.info("🚀 Intelligent Engine Router initialized with modular architecture")

    def analyze_content(self, content: str, source_path: Optional[Path] = None) -> ContentAnalysisResults:
        """
        Perform comprehensive content analysis.
        
        Args:
            content: Markdown content to analyze
            source_path: Optional source file path
            
        Returns:
            ContentAnalysisResults with detailed analysis
        """
        self.logger.debug(f"📊 Analyzing content ({len(content)} characters)")
        
        try:
            analysis_results = self.content_analyzer.analyze(content)
            
            self.logger.info(f"✅ Content analysis complete - Complexity: {analysis_results.complexity_score}")
            self.logger.debug(f"📋 Analysis details: {len(analysis_results.programming_languages)} languages, "
                            f"{analysis_results.code_block_count} code blocks, "
                            f"{analysis_results.special_char_density:.1f}% special chars")
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"❌ Content analysis failed: {e}")
            # Return basic analysis results as fallback
            return ContentAnalysisResults(
                complexity_score=500,  # Medium complexity fallback
                code_block_count=0,
                programming_languages=set(),
                special_char_density=0.0,
                has_math_formulas=False,
                has_tables=False,
                analysis_details={"error": str(e)}
            )

    def recommend_engine(self, content: str, source_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get engine recommendation without generating PDF.
        
        Args:
            content: Markdown content to analyze
            source_path: Optional source file path
            
        Returns:
            Dictionary with recommendation details
        """
        self.logger.debug("🤔 Getting engine recommendation")
        
        try:
            # Analyze content
            analysis_results = self.analyze_content(content, source_path)
            
            # Get recommendation
            recommendation = self.engine_selector.recommend_engine(analysis_results)
            
            self.logger.info(f"💡 Engine recommendation: {recommendation['engine'].value} "
                           f"(confidence: {recommendation['confidence']:.2f})")
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"❌ Engine recommendation failed: {e}")
            # Return safe fallback recommendation
            return {
                'engine': EngineType.REPORTLAB,
                'confidence': 0.5,
                'complexity_score': 500,
                'summary': f"Error in analysis: {e}, defaulting to ReportLab",
                'reasoning': {'error': str(e)},
                'thresholds': {'typst_threshold': 200, 'reportlab_threshold': 800}
            }

    def preprocess_content(self, content: str, engine_type: EngineType, 
                          analysis_results: ContentAnalysisResults,
                          source_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Preprocess content for specific engine.
        
        Args:
            content: Raw content to preprocess
            engine_type: Target engine
            analysis_results: Content analysis results
            source_path: Optional source file path
            
        Returns:
            Dictionary with preprocessed content and metadata
        """
        if not self.settings['enable_preprocessing']:
            return {
                'content': content,
                'metadata': {'title': 'Document'},
                'validation': {'is_valid': True, 'warnings': [], 'errors': []},
                'preprocessing_report': {'optimizations_applied': []},
                'engine_optimizations': []
            }
        
        self.logger.debug(f"🔧 Preprocessing content for {engine_type.value}")
        
        try:
            preprocessing_results = self.content_preprocessor.preprocess_content(
                content, engine_type, analysis_results, source_path
            )
            
            optimization_count = len(preprocessing_results.get('engine_optimizations', []))
            self.logger.info(f"✅ Content preprocessing complete - {optimization_count} optimizations applied")
            
            return preprocessing_results
            
        except Exception as e:
            self.logger.error(f"❌ Content preprocessing failed: {e}")
            # Return content without preprocessing as fallback
            return {
                'content': content,
                'metadata': {'title': 'Document', 'error': str(e)},
                'validation': {'is_valid': False, 'errors': [str(e)]},
                'preprocessing_report': {'error': str(e)},
                'engine_optimizations': []
            }

    def route_content(self, content: str, output_path: Optional[Path] = None,
                     force_engine: Optional[str] = None,
                     get_recommendation_only: bool = False,
                     source_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        🎯 MAIN ROUTING METHOD
        =====================
        Complete content routing with analysis, recommendation, and preprocessing.
        
        Args:
            content: Markdown content to process
            output_path: Optional output PDF path
            force_engine: Optional engine override ('typst' or 'reportlab')
            get_recommendation_only: If True, only return recommendation
            source_path: Optional source file path
            
        Returns:
            Complete routing results with all analysis data
        """
        self.logger.info("🎯 Starting intelligent content routing")
        
        try:
            # Step 1: Analyze content
            self.logger.debug("📊 Step 1: Content analysis")
            analysis_results = self.analyze_content(content, source_path)
            
            # Step 2: Get engine recommendation
            self.logger.debug("💡 Step 2: Engine recommendation")
            recommendation = self.engine_selector.recommend_engine(analysis_results)
            
            # Step 3: Apply force override if specified
            selected_engine = recommendation['engine']
            if force_engine:
                if force_engine.lower() == 'typst':
                    selected_engine = EngineType.TYPST
                    self.logger.info("🚀 FORCE OVERRIDE: Using Typst engine")
                elif force_engine.lower() == 'reportlab':
                    selected_engine = EngineType.REPORTLAB
                    self.logger.info("🔧 FORCE OVERRIDE: Using ReportLab engine")
                else:
                    self.logger.warning(f"⚠️ Invalid force_engine '{force_engine}', using recommendation")
            
            # Step 4: Preprocess content for selected engine
            self.logger.debug("🔧 Step 3: Content preprocessing")
            preprocessing_results = self.preprocess_content(
                content, selected_engine, analysis_results, source_path
            )
            
            # Generate complete routing results
            routing_results = {
                'success': True,
                'selected_engine': selected_engine.value,
                'recommendation': recommendation,
                'analysis': {
                    'complexity_score': analysis_results.complexity_score,
                    'code_block_count': analysis_results.code_block_count,
                    'programming_languages': list(analysis_results.programming_languages),
                    'special_char_density': analysis_results.special_char_density,
                    'has_math_formulas': analysis_results.has_math_formulas,
                    'has_tables': analysis_results.has_tables,
                    'analysis_details': analysis_results.analysis_details
                },
                'preprocessing': preprocessing_results,
                'routing_metadata': {
                    'force_engine_used': force_engine is not None,
                    'original_recommendation': recommendation['engine'].value,
                    'final_engine': selected_engine.value,
                    'recommendation_only': get_recommendation_only,
                    'content_length': len(content),
                    'source_path': str(source_path) if source_path else None,
                    'output_path': str(output_path) if output_path else None
                }
            }
            
            self.logger.info(f"✅ Routing complete - Engine: {selected_engine.value}, "
                           f"Complexity: {analysis_results.complexity_score}")
            
            return routing_results
            
        except Exception as e:
            self.logger.error(f"❌ Routing failed: {e}")
            
            # Return error results
            return {
                'success': False,
                'error': str(e),
                'selected_engine': 'reportlab',  # Safe fallback
                'recommendation': {
                    'engine': EngineType.REPORTLAB,
                    'confidence': 0.5,
                    'summary': f"Error occurred, defaulting to ReportLab: {e}"
                },
                'analysis': {
                    'complexity_score': 500,
                    'error': str(e)
                },
                'preprocessing': {
                    'content': content,
                    'error': str(e)
                },
                'routing_metadata': {
                    'error': True,
                    'force_engine_used': force_engine is not None,
                    'recommendation_only': get_recommendation_only
                }
            }

    def get_routing_summary(self, routing_results: Dict[str, Any]) -> str:
        """
        Generate human-readable routing summary.
        
        Args:
            routing_results: Results from route_content()
            
        Returns:
            Formatted summary string
        """
        if not routing_results.get('success', False):
            return f"❌ **Routing Failed:** {routing_results.get('error', 'Unknown error')}"
        
        engine = routing_results['selected_engine']
        complexity = routing_results['analysis']['complexity_score']
        confidence = routing_results['recommendation']['confidence']
        
        summary = f"🎯 **Routing Summary**\n"
        summary += f"📋 **Selected Engine:** {engine.upper()}\n"
        summary += f"🔢 **Complexity Score:** {complexity}\n"
        summary += f"💯 **Confidence:** {confidence:.1%}\n"
        
        # Add key decision factors
        analysis = routing_results['analysis']
        summary += f"📊 **Content Stats:**\n"
        summary += f"  - Code blocks: {analysis['code_block_count']}\n"
        summary += f"  - Languages: {len(analysis['programming_languages'])}\n"
        summary += f"  - Special chars: {analysis['special_char_density']:.1f}%\n"
        summary += f"  - Math formulas: {'Yes' if analysis['has_math_formulas'] else 'No'}\n"
        summary += f"  - Tables: {'Yes' if analysis['has_tables'] else 'No'}\n"
        
        # Add preprocessing info
        preprocessing = routing_results['preprocessing']
        if preprocessing.get('engine_optimizations'):
            summary += f"🔧 **Optimizations Applied:** {len(preprocessing['engine_optimizations'])}\n"
        
        return summary

    def update_settings(self, **kwargs):
        """Update router settings."""
        for key, value in kwargs.items():
            if key in self.settings:
                old_value = self.settings[key]
                self.settings[key] = value
                self.logger.debug(f"⚙️ Setting updated: {key} = {value} (was {old_value})")
            else:
                self.logger.warning(f"⚠️ Unknown setting: {key}")

    def get_version_info(self) -> Dict[str, str]:
        """Get version information for all components."""
        return {
            'router_version': '1.0.0',
            'architecture': 'modular',
            'components': {
                'content_analyzer': 'ContentAnalyzer v1.0.0',
                'engine_selector': 'EngineSelector v1.0.0', 
                'content_preprocessor': 'ContentPreprocessor v1.0.0'
            },
            'supported_engines': ['typst', 'reportlab'],
            'description': 'Intelligent PDF generation engine router with modular architecture'
        }

    def get_current_settings(self) -> Dict[str, Any]:
        """Get current router settings and component configurations."""
        return {
            'router_settings': self.settings,
            'engine_selector_settings': self.engine_selector.get_current_settings(),
            'content_analyzer_active': True,
            'content_preprocessor_active': self.settings['enable_preprocessing']
        }


# Convenience functions for direct usage
def analyze_content(content: str, source_path: Optional[Path] = None) -> ContentAnalysisResults:
    """Quick content analysis without creating router instance."""
    router = IntelligentEngineRouter()
    return router.analyze_content(content, source_path)


def recommend_engine(content: str, source_path: Optional[Path] = None) -> Dict[str, Any]:
    """Quick engine recommendation without creating router instance."""
    router = IntelligentEngineRouter()
    return router.recommend_engine(content, source_path)


def route_content(content: str, output_path: Optional[Path] = None,
                 force_engine: Optional[str] = None) -> Dict[str, Any]:
    """Quick content routing without creating router instance."""
    router = IntelligentEngineRouter()
    return router.route_content(content, output_path, force_engine)
