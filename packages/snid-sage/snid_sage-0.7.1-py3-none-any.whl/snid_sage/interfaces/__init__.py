"""
SNID SAGE Interfaces Package
============================

This package contains all user interfaces for SNID SAGE:
- GUI: Modern graphical user interface
- CLI: Command-line interface  
- LLM: Large Language Model integration interface
- API: REST API interface (future)
"""

__version__ = "1.0.0"
__author__ = "Fiorenzo Stoppa"

# Import main interface modules
try:
    from . import gui
except ImportError:
    gui = None

try:
    from . import cli
except ImportError:
    cli = None

try:
    from . import llm
except ImportError:
    llm = None

__all__ = ['gui', 'cli', 'llm'] 