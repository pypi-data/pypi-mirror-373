"""
SNID Core Module - Unified FFT Storage Architecture
===================================================

This module provides the core components for SNID analysis:
- Unified FFT storage system for optimal performance
- FFT optimization for fast correlations  
- Centralized configuration management
"""

from ..template_fft_storage import TemplateFFTStorage, TemplateEntry, create_unified_storage
from .config import SNIDConfig

from .integration import (
    integrate_fft_optimization,
    enable_optimization,
    auto_integrate,
    enable_caching_for_cli,
    enable_caching_for_gui,
    get_cache_status,
    clear_global_cache,
    load_templates_unified
)

__all__ = [
    'TemplateFFTStorage',
    'TemplateEntry', 
    'create_unified_storage',
    'SNIDConfig',
    'integrate_fft_optimization',
    'enable_optimization',
    'auto_integrate',
    'enable_caching_for_cli',
    'enable_caching_for_gui',
    'get_cache_status',
    'clear_global_cache',
    'load_templates_unified'
] 