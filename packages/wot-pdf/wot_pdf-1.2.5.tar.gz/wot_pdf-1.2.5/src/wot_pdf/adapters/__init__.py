"""
Simplified WOT-PDF Engine Adapters
"""

from .simplified_typst_adapter import SimplifiedTypstAdapter
from .simplified_reportlab_adapter import SimplifiedReportLabAdapter

__all__ = [
    "SimplifiedTypstAdapter",
    "SimplifiedReportLabAdapter"
]
