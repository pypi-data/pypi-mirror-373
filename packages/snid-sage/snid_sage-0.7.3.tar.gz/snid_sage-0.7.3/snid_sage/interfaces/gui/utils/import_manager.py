"""
SNID SAGE - Import Manager
==========================

Handles optional dependency checking for the SNID SAGE GUI.
Now simplified since fast_launcher pre-loads all heavy components.

Part of the SNID SAGE GUI restructuring - Utils Module
"""

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.import_manager')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.import_manager')


def check_optional_features():
    """Check availability of optional features that might not be installed"""
    optional_features = {}
    
    try:
        from snid_sage.shared.utils.line_detection.spectrum_utils import plot_spectrum, apply_savgol_filter
        optional_features['spectrum_utils'] = True
    except ImportError:
        optional_features['spectrum_utils'] = False
    
    try:
        from snid_sage.interfaces.llm.openrouter.openrouter_llm import get_openrouter_config
        optional_features['openrouter'] = True
        optional_features['openrouter_config'] = get_openrouter_config()
    except ImportError:
        optional_features['openrouter'] = False
        optional_features['openrouter_config'] = {}
    
    try:
        from snid_sage.interfaces.llm.local.gpu_llama import LLAMA_AVAILABLE
        optional_features['llama'] = LLAMA_AVAILABLE
    except ImportError:
        optional_features['llama'] = False
    
    return optional_features 
