"""
Content Service  
Content processing and validation service
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

from ...abstractions.base.service import BaseService

class ContentService(BaseService):
    """Content processing and validation service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.processors: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize the service"""
        try:
            self._logger.info("Initializing ContentService...")
            
            from ..core.container import container
            
            # Load processors
            processor_types = [
                'markdown_processor',
                'table_processor', 
                'image_processor',
                'code_processor'
            ]
            
            for processor_type in processor_types:
                if container.has(processor_type):
                    processor = container.get(processor_type)
                    self.processors[processor_type] = processor
                    self._logger.info(f"Registered {processor_type}")
            
            self.is_initialized = True
            self._logger.info("ContentService initialized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize ContentService: {e}")
            return False
    
    def process_content(self, content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Process content through pipeline"""
        
        if not self.is_initialized:
            return content
        
        processed = content
        pipeline = options.get('pipeline', ['markdown_processor']) if options else ['markdown_processor']
        
        for processor_name in pipeline:
            if processor_name in self.processors:
                try:
                    processor = self.processors[processor_name]
                    if hasattr(processor, 'process'):
                        processed = processor.process(processed)
                        self._logger.debug(f"Processed with {processor_name}")
                except Exception as e:
                    self._logger.error(f"Error in {processor_name}: {e}")
        
        return processed
    
    def validate_content(self, content: str) -> Tuple[bool, List[str]]:
        """Validate content"""
        
        errors = []
        warnings = []
        
        if not content.strip():
            errors.append("Content is empty")
            return False, errors
        
        # Basic validations
        if len(content) > 1000000:  # 1MB
            warnings.append("Content is very large")
        
        if content.count("```") % 2 != 0:
            errors.append("Unmatched code block delimiters")
        
        is_valid = len(errors) == 0
        messages = errors + warnings
        
        return is_valid, messages
    
    def get_content_stats(self, content: str) -> Dict[str, Any]:
        """Get content statistics"""
        
        lines = content.split('\n')
        
        return {
            "characters": len(content),
            "lines": len(lines),
            "words": len(content.split()),
            "paragraphs": len([line for line in lines if line.strip()]),
            "code_blocks": content.count("```") // 2,
            "tables": content.count("|"),
            "headers": len([line for line in lines if line.strip().startswith("#")]),
            "images": content.count("!["),
            "links": content.count("](")
        }
    
    def shutdown(self) -> None:
        """Shutdown the service"""
        self._logger.info("Shutting down ContentService...")
        self.processors.clear()
        self.is_initialized = False
