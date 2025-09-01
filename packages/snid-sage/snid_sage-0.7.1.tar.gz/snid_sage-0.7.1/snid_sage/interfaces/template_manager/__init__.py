"""
SNID Template Manager Interface
==============================

A comprehensive GUI interface for managing SNID templates.
This provides functionality to:
- Browse and review available templates
- Visualize individual templates and their epoch data
- Create new templates using the preprocessing pipeline
- Manage template metadata and storage
- Compare and analyze templates

This module maintains visual consistency with the main SNID-SAGE GUI
while providing specialized template management capabilities.
"""

from .main_window import SNIDTemplateManagerGUI
from .launcher import main

__all__ = ['SNIDTemplateManagerGUI', 'main']
__version__ = '1.0.0'