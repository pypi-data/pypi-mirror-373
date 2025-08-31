"""
Generator Service
Main PDF generation orchestration service
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from ...abstractions.base.service import BaseService

class GeneratorService(BaseService):
    """Main PDF generation orchestration service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.engines: Dict[str, Any] = {}
        self.default_engine = self.config.get('default_engine', 'reportlab')
        self.fallback_engine = self.config.get('fallback_engine', 'typst')
        self._logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize the service"""
        try:
            self._logger.info("Initializing GeneratorService...")
            
            from .container import container
            
            # Load available engines
            engine_types = ['reportlab_engine', 'typst_engine', 'hybrid_engine']
            
            for engine_name in engine_types:
                if container.has(engine_name):
                    engine = container.get(engine_name)
                    engine_key = engine_name.replace('_engine', '')
                    self.engines[engine_key] = engine
                    self._logger.info(f"Registered {engine_key} engine")
            
            self.is_initialized = True
            self._logger.info("GeneratorService initialized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize GeneratorService: {e}")
            return False
    
    def generate_pdf(self, 
                    content: str, 
                    output_path: Path, 
                    engine: Optional[str] = None,
                    **kwargs) -> bool:
        """Generate PDF using specified engine"""
        
        if not self.is_initialized:
            self._logger.error("GeneratorService not initialized")
            return False
        
        # Select engine
        selected_engine = engine or self.default_engine
        
        if selected_engine not in self.engines:
            self._logger.warning(f"Engine {selected_engine} not available, using fallback")
            selected_engine = self.fallback_engine
        
        if selected_engine not in self.engines:
            self._logger.error("No engines available")
            return False
        
        # Generate PDF
        try:
            engine_instance = self.engines[selected_engine]
            self._logger.info(f"Generating PDF using {selected_engine} engine")
            
            success = engine_instance.generate_pdf(content, output_path, **kwargs)
            
            if success:
                self._logger.info(f"PDF generated successfully: {output_path}")
            else:
                self._logger.error(f"PDF generation failed with {selected_engine}")
                
                # Try fallback
                if selected_engine != self.fallback_engine and self.fallback_engine in self.engines:
                    self._logger.info(f"Trying fallback engine: {self.fallback_engine}")
                    fallback = self.engines[self.fallback_engine]
                    success = fallback.generate_pdf(content, output_path, **kwargs)
            
            return success
            
        except Exception as e:
            self._logger.error(f"Error during PDF generation: {e}")
            return False
    
    def get_available_engines(self) -> List[str]:
        """Get available engines"""
        return list(self.engines.keys())
    
    def shutdown(self) -> None:
        """Shutdown the service"""
        self._logger.info("Shutting down GeneratorService...")
        self.engines.clear()
        self.is_initialized = False
