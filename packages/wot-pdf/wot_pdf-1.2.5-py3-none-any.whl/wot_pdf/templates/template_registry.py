"""
🎯 Template Registry
===================
Central registry for all available templates
"""

from typing import Dict, List

# Available templates registry
AVAILABLE_TEMPLATES = {
    "academic": {
        "name": "Academic Paper",
        "description": "Scientific and research document template with citations",
        "features": ["citations", "bibliography", "equations", "figures", "abstract"],
        "category": "academic",
        "complexity": "advanced"
    },
    "technical": {
        "name": "Technical Documentation", 
        "description": "Technical manuals and API documentation",
        "features": ["code_blocks", "diagrams", "api_docs", "tables", "syntax_highlighting"],
        "category": "documentation",
        "complexity": "standard"
    },
    "corporate": {
        "name": "Corporate Report",
        "description": "Executive reports and business documents", 
        "features": ["executive_summary", "charts", "financial_tables", "branding"],
        "category": "business",
        "complexity": "standard"
    },
    "educational": {
        "name": "Educational Guide",
        "description": "Learning materials and educational content",
        "features": ["exercises", "examples", "highlights", "summaries", "callouts"],
        "category": "education",
        "complexity": "standard"
    },
    "minimal": {
        "name": "Minimal Document",
        "description": "Clean, simple document layout",
        "features": ["basic_formatting", "clean_typography"],
        "category": "simple",
        "complexity": "basic"
    },
    # NOVIH 5 TEMPLATE-OV
    "creative": {
        "name": "Creative Design",
        "description": "Modern, artistic design for creative documents",
        "features": ["colorful_accents", "artistic_headers", "creative_layouts", "visual_elements"],
        "category": "design",
        "complexity": "advanced"
    },
    "magazine": {
        "name": "Magazine Style",
        "description": "Publication-style layout with columns and images",
        "features": ["multi_column", "image_layouts", "pull_quotes", "magazine_headers"],
        "category": "publication",
        "complexity": "advanced"
    },
    "scientific": {
        "name": "Scientific Research",
        "description": "Advanced scientific documentation with formulas",
        "features": ["complex_equations", "scientific_notation", "research_citations", "lab_reports"],
        "category": "research",
        "complexity": "expert"
    },
    "presentation": {
        "name": "Presentation Slides",
        "description": "Slide-like layout for presentations in PDF format",
        "features": ["slide_layout", "large_text", "bullet_points", "presentation_graphics"],
        "category": "presentation",
        "complexity": "standard"
    },
    "handbook": {
        "name": "Technical Handbook",
        "description": "Comprehensive technical manuals and guides",
        "features": ["detailed_toc", "cross_references", "appendices", "index", "procedures"],
        "category": "manual",
        "complexity": "expert"
    }
}

def get_template_names() -> List[str]:
    """Get list of all template names"""
    return list(AVAILABLE_TEMPLATES.keys())

def get_template_info(name: str) -> Dict:
    """Get template information"""
    return AVAILABLE_TEMPLATES.get(name, {})

def get_templates_by_category(category: str) -> Dict[str, Dict]:
    """Get templates filtered by category"""
    return {
        name: info 
        for name, info in AVAILABLE_TEMPLATES.items()
        if info.get("category") == category
    }
