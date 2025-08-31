"""
🎯 Template Manager
==================
Manage PDF templates and their configurations
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import central template registry
from ..templates.template_registry import AVAILABLE_TEMPLATES, get_template_names, get_template_info

class TemplateManager:
    """
    Manage PDF generation templates
    """
    
    def __init__(self):
        """Initialize template manager"""
        self.logger = logging.getLogger(__name__)
        
        # Use central template registry
        self.templates = AVAILABLE_TEMPLATES
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates
        
        Returns:
            List of template information
        """
        return [
            {
                "name": name,
                **info
            }
            for name, info in self.templates.items()
        ]
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get template information
        
        Args:
            name: Template name
            
        Returns:
            Template information or None if not found
        """
        return self.templates.get(name)
    
    def validate_template(self, name: str) -> bool:
        """
        Validate if template exists
        
        Args:
            name: Template name
            
        Returns:
            True if template exists
        """
        return name in self.templates
    
    def get_template_names(self) -> List[str]:
        """Get list of template names"""
        return list(self.templates.keys())
    
    def get_default_template(self) -> str:
        """Get default template name"""
        return "technical"
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        Search templates by name, description, or features
        
        Args:
            query: Search query
            
        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        matches = []
        
        for name, info in self.templates.items():
            # Search in name
            if query_lower in name.lower():
                matches.append({"name": name, **info, "match_type": "name"})
                continue
            
            # Search in description
            if query_lower in info["description"].lower():
                matches.append({"name": name, **info, "match_type": "description"})
                continue
            
            # Search in features
            if any(query_lower in feature.lower() for feature in info["features"]):
                matches.append({"name": name, **info, "match_type": "feature"})
                continue
            
            # Search in best_for
            if query_lower in info["best_for"].lower():
                matches.append({"name": name, **info, "match_type": "use_case"})
        
        return matches
