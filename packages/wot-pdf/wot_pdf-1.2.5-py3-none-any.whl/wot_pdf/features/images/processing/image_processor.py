"""
Image Processor
Image processing and optimization
"""

import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from ...abstractions.base.processor import BaseProcessor

class ImageProcessor(BaseProcessor):
    """Image content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._logger = logging.getLogger(__name__)
        self.image_count = 0
        
    def process(self, content: str, **kwargs) -> str:
        """Process images in content"""
        
        self._logger.debug("Processing images...")
        
        # Reset counter
        self.image_count = 0
        
        # Process markdown images
        processed = self._process_markdown_images(content)
        
        # Add figure captions
        processed = self._add_figure_captions(processed)
        
        self._logger.info(f"Processed {self.image_count} images")
        
        return processed
    
    def _process_markdown_images(self, content: str) -> str:
        """Process markdown image syntax"""
        
        # Pattern: ![alt text](image_url "optional title")
        image_pattern = r'!\[([^\]]*)\]\(([^\)]+)(?:\s+"([^"]*)")?\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            image_url = match.group(2)
            title = match.group(3) or ""
            
            self.image_count += 1
            
            # Validate image URL/path
            if self._validate_image_path(image_url):
                # Return enhanced image markdown
                if title:
                    return f'![{alt_text}]({image_url} "{title}")'
                else:
                    return f'![{alt_text}]({image_url})'
            else:
                self._logger.warning(f"Invalid image path: {image_url}")
                return f'![{alt_text}](INVALID_IMAGE_PATH)'
        
        return re.sub(image_pattern, replace_image, content)
    
    def _validate_image_path(self, path: str) -> bool:
        """Validate image path or URL"""
        
        # Check if it's a URL
        if path.startswith('http://') or path.startswith('https://'):
            return True
        
        # Check if it's a valid file path
        image_path = Path(path)
        if image_path.exists() and image_path.is_file():
            return True
        
        # Check common image extensions
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp', '.webp'}
        if image_path.suffix.lower() in valid_extensions:
            return True
        
        return False
    
    def _add_figure_captions(self, content: str) -> str:
        """Add figure captions to images"""
        
        lines = content.split('\n')
        processed_lines = []
        figure_num = 1
        
        for i, line in enumerate(lines):
            # Check for image
            if line.strip().startswith('!['):
                # Check if caption already exists
                has_caption_below = (i + 1 < len(lines) and 
                                   'Figure' in lines[i + 1])
                
                processed_lines.append(line)
                
                # Add caption if none exists
                if not has_caption_below:
                    # Extract alt text for caption
                    alt_match = re.search(r'!\[([^\]]*)\]', line)
                    alt_text = alt_match.group(1) if alt_match else f"Figure {figure_num}"
                    
                    caption = f"{{FIGURE_CAPTION:fig{figure_num}:Figure {figure_num}: {alt_text}}}"
                    processed_lines.append(caption)
                    figure_num += 1
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def validate(self, content: str) -> bool:
        """Validate image content"""
        
        # Check for valid image syntax
        image_pattern = r'!\[([^\]]*)\]\(([^\)]+)(?:\s+"([^"]*)")?\)'
        images = re.findall(image_pattern, content)
        
        for alt_text, image_url, title in images:
            if not self._validate_image_path(image_url):
                self._logger.warning(f"Invalid image: {image_url}")
                return False
        
        return True
    
    def get_image_stats(self, content: str) -> Dict[str, Any]:
        """Get image statistics"""
        
        image_pattern = r'!\[([^\]]*)\]\(([^\)]+)(?:\s+"([^"]*)")?\)'
        images = re.findall(image_pattern, content)
        
        return {
            "image_count": len(images),
            "images_with_titles": len([img for img in images if img[2]]),
            "unique_paths": len(set(img[1] for img in images))
        }
