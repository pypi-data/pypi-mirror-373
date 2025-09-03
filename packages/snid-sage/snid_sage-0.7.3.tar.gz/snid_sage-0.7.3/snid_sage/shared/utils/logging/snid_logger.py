"""
SNID SAGE Centralized Logging System
====================================

Provides centralized logging configuration with verbosity control
for all SNID SAGE components.

Features:
- Global verbosity level control
- Console and file logging support  
- Module-specific logger creation
- Performance-aware logging (lazy evaluation)
- GUI-safe logging (no console spam in GUI mode)

Usage:
    from snid_sage.shared.utils.logging import get_logger, configure_logging
    
    # Configure logging (typically done once at startup)
    configure_logging(verbosity='normal', gui_mode=True)
    
    # Get a logger for your module
    logger = get_logger('my_module')
    
    # Use it like standard Python logging
    logger.info("Operation completed")
    logger.debug("Debug information")
"""

import logging
import sys
import os
import time
from enum import Enum
from typing import Optional, Dict, Any, Union
from pathlib import Path


class VerbosityLevel(Enum):
    """Verbosity levels for SNID SAGE logging"""
    SILENT = 0      # Only critical errors
    QUIET = 1       # Errors and warnings only  
    NORMAL = 2      # Standard operation info
    VERBOSE = 3     # Detailed operation info
    DEBUG = 4       # Full debugging information

    @classmethod
    def from_string(cls, level_str: str) -> 'VerbosityLevel':
        """Convert string to VerbosityLevel"""
        level_map = {
            'silent': cls.SILENT,
            'quiet': cls.QUIET, 
            'normal': cls.NORMAL,
            'verbose': cls.VERBOSE,
            'debug': cls.DEBUG
        }
        return level_map.get(level_str.lower(), cls.NORMAL)

    def to_logging_level(self) -> int:
        """Convert to standard Python logging level"""
        level_map = {
            VerbosityLevel.SILENT: logging.CRITICAL,
            VerbosityLevel.QUIET: logging.WARNING,
            VerbosityLevel.NORMAL: logging.INFO,
            VerbosityLevel.VERBOSE: logging.INFO,
            VerbosityLevel.DEBUG: logging.DEBUG
        }
        return level_map[self]


class SNIDLogger:
    """Centralized logger for SNID SAGE with verbosity control"""
    
    _instance = None
    _configured = False
    _loggers: Dict[str, logging.Logger] = {}
    _verbosity_level = VerbosityLevel.NORMAL
    _gui_mode = False
    _log_file = None
    _console_handler = None
    _file_handler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def configure(cls, 
                  verbosity: Union[VerbosityLevel, str] = VerbosityLevel.NORMAL,
                  gui_mode: bool = False, 
                  log_file: Optional[str] = None,
                  log_dir: Optional[str] = None) -> None:
        """
        Configure global logging settings
        
        Args:
            verbosity: Verbosity level (enum or string)
            gui_mode: If True, reduce console output for GUI applications
            log_file: Optional log file path
            log_dir: Optional log directory (auto-generates filename)
        """
        instance = cls()
        
        # Convert string to enum if needed
        if isinstance(verbosity, str):
            verbosity = VerbosityLevel.from_string(verbosity)
        
        instance._verbosity_level = verbosity
        instance._gui_mode = gui_mode
        
        # Setup log file if requested
        if log_dir and not log_file:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"snid_sage_{timestamp}.log"
        
        instance._log_file = log_file
        
        
        # This prevents double logging from Python's basicConfig or other sources
        python_root_logger = logging.getLogger()
        python_root_logger.handlers.clear()  # Remove all existing root handlers
        python_root_logger.setLevel(logging.CRITICAL)  # Disable root logger
        
        # Configure SNID's root logger
        root_logger = logging.getLogger('snid_sage')
        
        
        # This ensures that loggers don't emit messages above the desired level
        if gui_mode:
            # In GUI mode, be more restrictive
            if verbosity == VerbosityLevel.DEBUG:
                root_level = logging.DEBUG
            elif verbosity == VerbosityLevel.VERBOSE:
                root_level = logging.INFO  
            elif verbosity == VerbosityLevel.SILENT:
                root_level = logging.CRITICAL  # Only critical errors
            else:  # NORMAL or QUIET
                root_level = logging.WARNING  # Only warnings and errors
        else:
            # In CLI mode, use standard mapping
            root_level = verbosity.to_logging_level()
        
        root_logger.setLevel(root_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Setup console handler
        instance._setup_console_handler(verbosity, gui_mode)
        
        # Setup file handler if requested
        if log_file:
            instance._setup_file_handler(log_file)
        
        # Mark as configured
        instance._configured = True
        
        # Log the configuration (this will only appear if the level allows it)
        logger = instance.get_logger('logging.config')
        logger.debug(f"Logging configured: verbosity={verbosity.name}, gui_mode={gui_mode}, root_level={logging.getLevelName(root_level)}")
        if log_file:
            logger.debug(f"Log file: {log_file}")
    
    @classmethod
    def _setup_console_handler(cls, verbosity: VerbosityLevel, gui_mode: bool) -> None:
        """Setup console logging handler"""
        instance = cls()
        
        # Determine console output level
        if gui_mode:
            # In GUI mode, be much more conservative with console output
            if verbosity == VerbosityLevel.DEBUG:
                console_level = logging.DEBUG
            elif verbosity == VerbosityLevel.VERBOSE:
                console_level = logging.INFO
            else:  # NORMAL, QUIET, or SILENT - all map to WARNING or higher in GUI mode
                if verbosity == VerbosityLevel.SILENT:
                    console_level = logging.CRITICAL
                else:
                    console_level = logging.WARNING  # GUI should be quiet by default
        else:
            # In CLI mode, use standard levels
            console_level = verbosity.to_logging_level()
        
        # Create console handler
        instance._console_handler = logging.StreamHandler(sys.stderr)
        instance._console_handler.setLevel(console_level)
        
        # Create formatter
        if verbosity == VerbosityLevel.DEBUG:
            # Detailed format for debugging
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            )
        elif gui_mode and verbosity != VerbosityLevel.DEBUG:
            # Minimal format for GUI mode
            formatter = logging.Formatter('%(levelname)s: %(message)s')
        else:
            # Standard format
            formatter = logging.Formatter(
                '[%(levelname)8s] %(name)s: %(message)s'
            )
        
        instance._console_handler.setFormatter(formatter)
        
        # Add to root logger
        root_logger = logging.getLogger('snid_sage')
        root_logger.addHandler(instance._console_handler)
        
        
        root_logger.propagate = False
    
    @classmethod
    def _setup_file_handler(cls, log_file: Union[str, Path]) -> None:
        """Setup file logging handler"""
        instance = cls()
        
        try:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler (always debug level for files)
            instance._file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
            instance._file_handler.setLevel(logging.DEBUG)
            
            # Detailed format for file logging
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            instance._file_handler.setFormatter(formatter)
            
            # Add to root logger
            root_logger = logging.getLogger('snid_sage')
            root_logger.addHandler(instance._file_handler)
            
        except Exception as e:
            # Fallback if file logging fails
            console_logger = logging.getLogger('snid_sage.logging')
            console_logger.warning(f"Could not setup file logging to {log_file}: {e}")
    
    @classmethod  
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a configured logger for a module
        
        Args:
            name: Logger name (typically module name)
            
        Returns:
            Configured logger instance
        """
        instance = cls()
        
        # Auto-configure with defaults if not configured
        if not instance._configured:
            instance.configure()
        
        # Create hierarchical logger name
        if not name.startswith('snid_sage'):
            full_name = f'snid_sage.{name}'
        else:
            full_name = name
        
        # Return cached logger or create new one
        if full_name not in instance._loggers:
            logger = logging.getLogger(full_name)
            instance._loggers[full_name] = logger
        
        return instance._loggers[full_name]
    
    @classmethod
    def set_verbosity(cls, level: Union[VerbosityLevel, str]) -> None:
        """
        Change verbosity level at runtime
        
        Args:
            level: New verbosity level
        """
        instance = cls()
        
        if isinstance(level, str):
            level = VerbosityLevel.from_string(level)
        
        instance._verbosity_level = level
        
        
        root_logger = logging.getLogger('snid_sage')
        
        # Set root logger level using same logic as configure()
        if instance._gui_mode:
            # In GUI mode, be more restrictive
            if level == VerbosityLevel.DEBUG:
                root_level = logging.DEBUG
            elif level == VerbosityLevel.VERBOSE:
                root_level = logging.INFO
            elif level == VerbosityLevel.SILENT:
                root_level = logging.CRITICAL  # Only critical errors
            else:  # NORMAL or QUIET
                root_level = logging.WARNING  # Only warnings and errors
        else:
            # In CLI mode, use standard mapping
            root_level = level.to_logging_level()
        
        root_logger.setLevel(root_level)
        
        # Update console handler level if it exists
        if instance._console_handler:
            if instance._gui_mode:
                # Apply GUI mode logic - same as in _setup_console_handler
                if level == VerbosityLevel.DEBUG:
                    new_level = logging.DEBUG
                elif level == VerbosityLevel.VERBOSE:
                    new_level = logging.INFO
                else:  # NORMAL, QUIET, or SILENT - all map to WARNING or higher in GUI mode
                    if level == VerbosityLevel.SILENT:
                        new_level = logging.CRITICAL
                    else:
                        new_level = logging.WARNING  # GUI should be quiet by default
            else:
                new_level = level.to_logging_level()
            
            instance._console_handler.setLevel(new_level)
        
        # Log the change (this will only appear if the level allows it)
        logger = instance.get_logger('logging.config')
        logger.debug(f"Verbosity changed to {level.name}, root_level={logging.getLevelName(root_level)}")
    
    @classmethod
    def get_verbosity(cls) -> VerbosityLevel:
        """Get current verbosity level"""
        instance = cls()
        return instance._verbosity_level
    
    @classmethod
    def is_gui_mode(cls) -> bool:
        """Check if running in GUI mode"""
        instance = cls()
        return instance._gui_mode
    
    @classmethod
    def cleanup(cls) -> None:
        """Cleanup logging handlers"""
        instance = cls()
        
        if instance._file_handler:
            root_logger = logging.getLogger('snid_sage')
            root_logger.removeHandler(instance._file_handler)
            instance._file_handler.close()
            instance._file_handler = None
        
        instance._configured = False
        instance._loggers.clear()


# Convenience functions for easy import
def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name"""
    return SNIDLogger.get_logger(name)


def configure_logging(verbosity: Union[VerbosityLevel, str] = 'normal',
                     gui_mode: bool = False,
                     log_file: Optional[str] = None,
                     log_dir: Optional[str] = None) -> None:
    """Configure the SNID SAGE logging system"""
    SNIDLogger.configure(verbosity=verbosity, gui_mode=gui_mode, 
                        log_file=log_file, log_dir=log_dir)


def set_verbosity(level: Union[VerbosityLevel, str]) -> None:
    """Set the logging verbosity level"""
    SNIDLogger.set_verbosity(level)


def get_verbosity() -> VerbosityLevel:
    """Get the current verbosity level"""
    return SNIDLogger.get_verbosity()


def is_gui_mode() -> bool:
    """Check if logging is configured for GUI mode"""
    return SNIDLogger.is_gui_mode()


def cleanup_logging() -> None:
    """Cleanup logging system"""
    SNIDLogger.cleanup() 