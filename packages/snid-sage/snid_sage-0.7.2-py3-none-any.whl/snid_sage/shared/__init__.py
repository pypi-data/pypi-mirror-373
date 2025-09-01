"""
SNID SAGE Shared Package
========================

Shared utilities, constants, exceptions, and types used across all SNID SAGE components.

This package contains:
- utils: Common utility functions and classes
- constants: Physical constants, GUI constants, processing parameters
- exceptions: Custom exception classes
- types: Data structure definitions and type hints
"""

__version__ = "1.0.0"
__author__ = "Fiorenzo Stoppa"

# Import main shared modules
try:
    from . import utils
except ImportError:
    utils = None

try:
    from . import constants
except ImportError:
    constants = None

try:
    from . import exceptions
except ImportError:
    exceptions = None

try:
    from . import types
except ImportError:
    types = None

__all__ = ['utils', 'constants', 'exceptions', 'types'] 