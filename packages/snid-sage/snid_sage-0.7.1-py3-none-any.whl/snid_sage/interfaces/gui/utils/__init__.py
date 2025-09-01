"""
SNID SAGE GUI Utils Package
===========================

Utilities and helper functions for the SNID SAGE GUI.
Part of the SNID SAGE GUI restructuring.

Import specific modules as needed rather than using this package directly.
"""

# Cross-platform utilities (framework-agnostic)
from .import_manager import check_optional_features

# Legacy Tk utilities are not included in this package

# PySide6-specific utilities
try:
    from .unified_pyside6_layout_manager import UnifiedPySide6LayoutManager, LayoutSettings
    from .pyside6_helpers import PySide6Helpers
    from .enhanced_dialog_button_manager import EnhancedDialogButtonManager
    from .dialog_button_enhancer import enhance_dialog_buttons, enhance_dialog_with_preset, setup_sensitivity_toggle_button, create_button_with_enhancement
    PYSIDE6_UTILS_AVAILABLE = True
except ImportError:
    PYSIDE6_UTILS_AVAILABLE = False

# Conditional exports based on what's available
__all__ = ['check_optional_features']

if PYSIDE6_UTILS_AVAILABLE:
    __all__.extend([
        'UnifiedPySide6LayoutManager',
        'LayoutSettings',
        'PySide6Helpers',
        'EnhancedDialogButtonManager',
        'enhance_dialog_buttons',
        'enhance_dialog_with_preset',
        'setup_sensitivity_toggle_button',
        'create_button_with_enhancement'
    ]) 
