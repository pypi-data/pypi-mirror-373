"""
SNID SAGE - Shared Exceptions Package
=====================================

This package contains all custom exception classes used throughout SNID SAGE
for better error handling and debugging.
"""

# Import all core exceptions
from .core_exceptions import *

# Version information
__version__ = '1.0.0'
__author__ = 'SNID SAGE Team'

# Make all exceptions easily accessible
__all__ = [
    # Base exception
    'SNIDError',
    
    # Spectrum-related exceptions
    'SpectrumLoadError',
    'SpectrumProcessingError',
    
    # Analysis exceptions
    'AnalysisError',
    'TemplateError',
    'RedshiftError',
    
    # Configuration exceptions
    'ConfigurationError',
    'ValidationError',
    
    # Processing exceptions
    'MaskingError',
    'PlottingError',
    
    # External service exceptions
    'LLMError',
    'ImportError'
] 