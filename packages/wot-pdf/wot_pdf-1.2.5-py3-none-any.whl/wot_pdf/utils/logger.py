"""
🎯 WOT-PDF Logger Setup
======================
Simple logger configuration for WOT-PDF components
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str, 
                level: int = logging.INFO,
                format_string: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting
    
    Args:
        name: Logger name (usually __name__ or class name)
        level: Logging level (default INFO)
        format_string: Custom format string
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    if not format_string:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get or create a logger with standard configuration"""
    return setup_logger(name, level)
