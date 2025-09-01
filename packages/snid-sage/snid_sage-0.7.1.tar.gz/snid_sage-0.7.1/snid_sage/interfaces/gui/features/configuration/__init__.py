"""
SNID SAGE Configuration Features
================================

Configuration management features for the SNID SAGE GUI.

Provides:
- ConfigController: Main configuration controller for SNID analysis parameters
- GUISettingsController: GUI-specific settings management (fonts, themes, display)
"""

from .config_controller import ConfigController

__all__ = [
    'ConfigController'
] 
