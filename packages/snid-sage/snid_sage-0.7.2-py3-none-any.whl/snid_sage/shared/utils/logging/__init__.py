"""
SNID SAGE Logging System
========================

Centralized logging system for SNID SAGE with verbosity control.

This module provides a clean API for configuring and using logging
throughout the SNID SAGE application.

Quick Start:
    # Simple usage (auto-configures)
    from snid_sage.shared.utils.logging import get_logger
    logger = get_logger('my_module')
    logger.info("Hello world")
    
    # Manual configuration
    from snid_sage.shared.utils.logging import configure_logging
    configure_logging(verbosity='debug', gui_mode=True)
    
    # Command-line integration
    from snid_sage.shared.utils.logging.config import add_logging_arguments, configure_from_args
    parser = argparse.ArgumentParser()
    add_logging_arguments(parser)
    args = parser.parse_args()
    configure_from_args(args)
"""

# Import main API functions
from .snid_logger import (
    get_logger,
    configure_logging,
    set_verbosity,
    get_verbosity,
    is_gui_mode,
    cleanup_logging,
    VerbosityLevel,
    SNIDLogger
)

# Import configuration functions
from .config import (
    add_logging_arguments,
    configure_from_args,
    configure_from_environment,
    configure_for_gui,
    configure_for_cli,
    print_logging_status,
    get_logger_config
)

# Version and metadata
__version__ = '1.0.0'
__author__ = 'SNID SAGE Team'

# Public API - what gets imported with "from snid_sage.shared.utils.logging import *"
__all__ = [
    # Core logging functions
    'get_logger',
    'configure_logging',
    'set_verbosity',
    'get_verbosity',
    'is_gui_mode',
    'cleanup_logging',
    
    # Configuration functions
    'add_logging_arguments',
    'configure_from_args',
    'configure_from_environment',
    'configure_for_gui',
    'configure_for_cli',
    
    # Utility functions
    'print_logging_status',
    'get_logger_config',
    
    # Classes and enums
    'VerbosityLevel',
    'SNIDLogger'
]

# Convenience aliases for common patterns
def setup_gui_logging(verbosity='normal', enable_file_logging=False):
    """
    Quick setup for GUI applications
    
    Args:
        verbosity: Verbosity level ('normal', 'verbose', 'debug', etc.)
        enable_file_logging: Whether to enable file logging
    """
    configure_for_gui(verbosity=verbosity, enable_file_logging=enable_file_logging)


def setup_cli_logging(verbosity='normal'):
    """
    Quick setup for CLI applications
    
    Args:
        verbosity: Verbosity level ('normal', 'verbose', 'debug', etc.)
    """
    configure_for_cli(verbosity=verbosity)


# Add convenience functions to __all__
__all__.extend(['setup_gui_logging', 'setup_cli_logging']) 