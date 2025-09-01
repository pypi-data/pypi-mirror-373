"""
SNID SAGE CLI Interface
======================

Command-line interface for SNID SAGE spectrum analysis.

This module provides command-line tools for:
- Spectrum identification
- Batch processing
- Configuration management
"""

__version__ = "1.0.0"

# Import main CLI components
try:
    from .main import main
except ImportError:
    main = None

# Import command modules individually
try:
    from . import identify
except ImportError:
    identify = None

try:
    from . import batch
except ImportError:
    batch = None

try:
    from . import config
except ImportError:
    config = None

__all__ = ['main', 'identify', 'batch', 'config']