#!/usr/bin/env python3
"""
Модуль core - основна бізнес-логіка PhotoControl
"""

from .image_processor import ImageProcessor, AnalysisPoint, GridSettings
from .constants import *

__version__ = "2.0.0"
__all__ = [
    'ImageProcessor',
    'AnalysisPoint', 
    'GridSettings',
    # Константи
    'ALBUM', 'UI', 'IMAGE', 'RADAR', 'GRID', 
    'STYLES', 'FILES', 'TEMPLATE_DEFAULTS', 
    'WORD_STYLES', 'VALIDATION'
]