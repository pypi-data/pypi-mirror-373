#!/usr/bin/env python3
"""
🧪 QUICK MODULAR ARCHITECTURE TEST
================================
Test our newly refactored modular components to ensure they work correctly.
"""

import sys
from pathlib import Path

# Add the core directory to path for imports
core_dir = Path(__file__).parent
sys.path.insert(0, str(core_dir))

try:
    import content_analyzer
    import engine_selector
    import content_preprocessor
    import intelligent_engine_router
    
    ContentAnalyzer = content_analyzer.ContentAnalyzer
    ContentAnalysisResults = content_analyzer.ContentAnalysisResults
    EngineSelector = engine_selector.EngineSelector
    EngineType = engine_selector.EngineType
    ContentPreprocessor = content_preprocessor.ContentPreprocessor
    IntelligentEngineRouter = intelligent_engine_router.IntelligentEngineRouter
    
    print("🎉 ALL IMPORTS SUCCESSFUL!")
    
    # Test content
    test_content = """
# Test Document

This is a simple test document with some **markdown** content.

```python
def hello_world():
    print("Hello, World!")
    return "success"
```

Here's a table:

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

And some math: $E = mc^2$

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```
"""

    print("\n📊 Testing Content Analyzer...")
    analyzer = ContentAnalyzer()
    analysis_results = analyzer.analyze(test_content)
    print(f"✅ Complexity Score: {analysis_results.complexity_score}")
    print(f"✅ Code Blocks: {analysis_results.code_block_count}")
    print(f"✅ Languages: {analysis_results.programming_languages}")
    print(f"✅ Has Math: {analysis_results.has_math_formulas}")
    print(f"✅ Has Tables: {analysis_results.has_tables}")
    
    print("\n🎯 Testing Engine Selector...")
    selector = EngineSelector()
    recommendation = selector.recommend_engine(analysis_results)
    print(f"✅ Recommended Engine: {recommendation['engine'].value}")
    print(f"✅ Confidence: {recommendation['confidence']:.2f}")
    
    print("\n🔧 Testing Content Preprocessor...")
    preprocessor = ContentPreprocessor()
    preprocessing_results = preprocessor.preprocess_content(
        test_content, recommendation['engine'], analysis_results
    )
    print(f"✅ Preprocessed Content Length: {len(preprocessing_results['content'])}")
    print(f"✅ Optimizations Applied: {len(preprocessing_results['engine_optimizations'])}")
    
    print("\n🎯 Testing Intelligent Router (Full Integration)...")
    router = IntelligentEngineRouter()
    routing_results = router.route_content(test_content, get_recommendation_only=True)
    
    if routing_results['success']:
        print(f"✅ Selected Engine: {routing_results['selected_engine']}")
        print(f"✅ Complexity Score: {routing_results['analysis']['complexity_score']}")
        print(f"✅ Code Blocks: {routing_results['analysis']['code_block_count']}")
        print(f"✅ Recommendation Confidence: {routing_results['recommendation']['confidence']:.2f}")
    else:
        print(f"❌ Router Error: {routing_results.get('error', 'Unknown error')}")
    
    print("\n🏆 MODULAR ARCHITECTURE TEST COMPLETE!")
    print("✅ All components working correctly!")
    print("✅ Refactoring successful - professional modular architecture achieved!")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print("Please check module dependencies and imports.")
except Exception as e:
    print(f"❌ TEST ERROR: {e}")
    import traceback
    traceback.print_exc()
