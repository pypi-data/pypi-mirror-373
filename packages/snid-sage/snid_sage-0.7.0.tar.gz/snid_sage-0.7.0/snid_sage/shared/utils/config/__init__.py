"""
SNID Configuration
==================

Configuration management utilities for SNID SAGE.

Provides:
- ConfigurationManager: Core configuration business logic
- ValidationResult: Configuration validation results
- ConfigValidationRule: Validation rule definitions
- config_manager: Global configuration manager instance
"""

from .configuration_manager import (
    ConfigurationManager,
    ValidationResult,
    ConfigValidationRule,
    config_manager
)

__all__ = [
    'ConfigurationManager',
    'ValidationResult', 
    'ConfigValidationRule',
    'config_manager'
] 