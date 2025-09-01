"""
SNID SAGE - Dialog Button Enhancer Utility
==========================================

Utility functions to easily enhance dialog buttons throughout the GUI.
Provides convenient methods to apply enhanced styling to all buttons in a dialog.

Developed by Assistant for SNID SAGE
"""

from typing import List, Dict, Any, Optional
import PySide6.QtWidgets as QtWidgets
from .enhanced_dialog_button_manager import EnhancedDialogButtonManager

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.dialog_button_enhancer')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.dialog_button_enhancer')


def enhance_dialog_buttons(dialog: QtWidgets.QDialog, 
                         theme_manager=None,
                         custom_button_configs: Optional[Dict[str, Dict[str, Any]]] = None) -> EnhancedDialogButtonManager:
    """
    Enhance all buttons in a dialog with consistent styling and animations
    
    Args:
        dialog: The dialog to enhance
        theme_manager: Optional theme manager
        custom_button_configs: Custom configurations for specific buttons
    
    Returns:
        The button manager instance for further customization
    """
    button_manager = EnhancedDialogButtonManager(theme_manager)
    custom_configs = custom_button_configs or {}
    
    # Find all buttons in the dialog
    buttons = dialog.findChildren(QtWidgets.QPushButton)
    
    for button in buttons:
        object_name = button.objectName()
        custom_config = custom_configs.get(object_name, {})
        
        # Extract button type from custom config if provided
        button_type = custom_config.get('type', None)
        
        # Apply automatic enhancements
        button_manager.register_button(button, button_type=button_type, custom_config=custom_config)
    
    _LOGGER.info(f"Enhanced {len(buttons)} buttons in dialog: {dialog.windowTitle()}")
    return button_manager


def create_button_with_enhancement(parent: QtWidgets.QWidget,
                                 text: str,
                                 button_type: str = None,
                                 size_class: str = 'normal',
                                 object_name: str = None) -> QtWidgets.QPushButton:
    """
    Create a new button with automatic enhancement
    
    Args:
        parent: Parent widget
        text: Button text
        button_type: Type of button ('apply', 'cancel', etc.)
        size_class: Size class ('normal', 'small', 'icon')
        object_name: Optional object name
    
    Returns:
        Enhanced QPushButton
    """
    button = QtWidgets.QPushButton(text, parent)
    
    if object_name:
        button.setObjectName(object_name)
    
    # This will be enhanced when the dialog is processed
    # Store the configuration for later enhancement
    button.setProperty("enhancement_type", button_type)
    button.setProperty("enhancement_size", size_class)
    
    return button


def setup_sensitivity_toggle_button(button_manager: EnhancedDialogButtonManager,
                                   button: QtWidgets.QPushButton,
                                   callback_function,
                                   initial_state: bool = False,
                                   active_color: str = None,
                                   inactive_color: str = None) -> None:
    """
    Setup a sensitivity toggle button (like Precision/Normal)
    
    Args:
        button_manager: The dialog button manager
        button: The button to configure as a toggle
        callback_function: Function to call when toggled
        initial_state: Initial state (False = Normal, True = Precision)
    """
    active_text = "Sensitivity: Precision"
    inactive_text = "Sensitivity: Normal"
    
    # Colors (allow overrides); default to preprocessing orange and load gray
    if active_color is None:
        active_color = "#FFA600"
    if inactive_color is None:
        inactive_color = "#6E6E6E"
    
    button_manager.register_toggle_button(
        button=button,
        toggle_callback=callback_function,
        initial_state=initial_state,
        active_text=active_text,
        inactive_text=inactive_text,
        active_color=active_color,
        inactive_color=inactive_color
    )


# Common button configuration presets
DIALOG_BUTTON_PRESETS = {
    'configuration_dialog': {
        'apply_btn': {'type': 'apply', 'size_class': 'normal'},
        'primary_btn': {'type': 'apply', 'size_class': 'normal'},
        'secondary_btn': {'type': 'secondary', 'size_class': 'normal'},
        'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
        'reset_btn': {'type': 'reset', 'size_class': 'normal'},
    },
    
    'analysis_progress_dialog': {
        'games_btn': {'type': 'info', 'size_class': 'normal'},
        'hide_btn': {'type': 'neutral', 'size_class': 'normal'},
        'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
    },
    
    'manual_redshift_dialog': {
        'precision_button': {
            'type': 'neutral', 
            'size_class': 'normal',
            'is_toggle': True,
            'toggle_state': False
        },
        'accept_btn': {'type': 'accent', 'size_class': 'normal'},
        'auto_btn': {'type': 'navigation', 'size_class': 'normal'},
        'help_btn': {'type': 'info', 'size_class': 'normal'},
    },
    
    'gmm_clustering_dialog': {
        'close_btn': {'type': 'apply', 'size_class': 'normal'},
        'primary_btn': {'type': 'apply', 'size_class': 'normal'},
        'export_data_btn': {'type': 'utility', 'size_class': 'normal'},
        'export_plot_btn': {'type': 'utility', 'size_class': 'normal'},
        'refresh_btn': {'type': 'reset', 'size_class': 'normal'},
        'highlight_btn': {'type': 'info', 'size_class': 'normal'},
    },
    
    'emission_dialog': {
        'sn_button': {'type': 'secondary', 'size_class': 'normal'},
        'galaxy_button': {'type': 'secondary', 'size_class': 'normal'},
        'apply_btn': {'type': 'apply', 'size_class': 'normal'},
        'clear_btn': {'type': 'reset', 'size_class': 'normal'},
        'remove_btn': {'type': 'cancel', 'size_class': 'normal'},
        'step2_btn': {'type': 'apply', 'size_class': 'normal'},
        'step2_prev_btn': {'type': 'navigation', 'size_class': 'small'},
        'step2_next_btn': {'type': 'navigation', 'size_class': 'small'},
        'analyze_btn': {'type': 'apply', 'size_class': 'normal'},
    },
    
    'mask_manager_dialog': {
        'apply_btn': {'type': 'apply', 'size_class': 'normal'},
        'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
        'save_btn': {'type': 'utility', 'size_class': 'normal'},
        'load_btn': {'type': 'utility', 'size_class': 'normal'},
        'add_mask_btn': {'type': 'secondary', 'size_class': 'normal'},
        'remove_btn': {'type': 'cancel', 'size_class': 'normal'},
        'clear_all_btn': {'type': 'reset', 'size_class': 'normal'},
    },
    
    'settings_dialog': {
        'apply_btn': {'type': 'apply', 'size_class': 'normal'},
        'ok_btn': {'type': 'apply', 'size_class': 'normal'},
        'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
        'test_connection_btn': {'type': 'neutral', 'size_class': 'normal'},
        'fetch_models_btn': {'type': 'neutral', 'size_class': 'normal'},
        'fetch_free_btn': {'type': 'neutral', 'size_class': 'normal'},
        'test_model_btn': {'type': 'neutral', 'size_class': 'normal'},
        'show_key_btn': {'type': 'info', 'size_class': 'small'},
        'reset_button': {'type': 'reset', 'size_class': 'normal'},
    },
    
    'results_dialog': {
        'close_btn': {'type': 'apply', 'size_class': 'normal'},
        'copy_summary_btn': {'type': 'utility', 'size_class': 'normal'},
        'save_results_btn': {'type': 'utility', 'size_class': 'normal'},
    },
    
    'redshift_mode_dialog': {
        'primary_btn': {'type': 'accent', 'size_class': 'normal'},  # Continue Analysis button
        'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
    },
    
    'preprocessing_dialog': {
        'apply_btn': {'type': 'apply', 'size_class': 'normal'},
        'restart_btn': {'type': 'reset', 'size_class': 'normal'},
        'masking_toggle_btn': {
            'type': 'neutral', 
            'size_class': 'normal',
            'is_toggle': True,
            'toggle_state': False
        },
    },

    'enhanced_ai_assistant_dialog': {
        # Summary tab
        'generate_summary_btn': {'type': 'apply', 'size_class': 'normal'},
        'export_summary_btn': {'type': 'utility', 'size_class': 'normal'},
        'copy_summary_btn': {'type': 'utility', 'size_class': 'normal'},
        # Chat tab
        'send_btn': {'type': 'apply', 'size_class': 'normal'},
        'clear_chat_btn': {'type': 'reset', 'size_class': 'normal'},
        # Settings tab
        'show_key_btn': {'type': 'info', 'size_class': 'small'},
        'test_connection_btn': {'type': 'neutral', 'size_class': 'normal'},
        'fetch_models_btn': {'type': 'neutral', 'size_class': 'normal'},
        'fetch_free_btn': {'type': 'neutral', 'size_class': 'normal'},
        'test_model_btn': {'type': 'neutral', 'size_class': 'normal'},
        # Footer
        'help_btn': {'type': 'info', 'size_class': 'normal'},
        'close_btn': {'type': 'cancel', 'size_class': 'normal'},
    },

    # Additional dialogs
    'redshift_age_dialog': {
        'export_plot_btn': {'type': 'utility', 'size_class': 'normal'},
        'export_data_btn': {'type': 'utility', 'size_class': 'normal'},
        'close_btn': {'type': 'apply', 'size_class': 'normal'},
    },

    'preprocessing_selection_dialog': {
        'apply_btn': {'type': 'apply', 'size_class': 'normal'},
        'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
    },

    'games_dialog': {
        'play_button': {'type': 'apply', 'size_class': 'normal'},
        'cancel_button': {'type': 'cancel', 'size_class': 'normal'},
    },

    'progress_dialog': {
        'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
    },

    'subtype_proportions_dialog': {
        'export_plot_btn': {'type': 'utility', 'size_class': 'normal'},
        'export_data_btn': {'type': 'utility', 'size_class': 'normal'},
        'close_btn': {'type': 'apply', 'size_class': 'normal'},
    },

    'cluster_selection_dialog': {
        'confirm_btn': {'type': 'apply', 'size_class': 'normal'},
    },
}


def enhance_dialog_with_preset(dialog: QtWidgets.QDialog, 
                              preset_name: str,
                              theme_manager=None) -> EnhancedDialogButtonManager:
    """
    Enhance a dialog using a predefined button configuration preset
    
    Args:
        dialog: The dialog to enhance
        preset_name: Name of the preset configuration
        theme_manager: Optional theme manager
    
    Returns:
        The button manager instance
    """
    if preset_name not in DIALOG_BUTTON_PRESETS:
        _LOGGER.warning(f"Unknown preset: {preset_name}. Using default enhancement.")
        return enhance_dialog_buttons(dialog, theme_manager)
    
    preset_config = DIALOG_BUTTON_PRESETS[preset_name]
    return enhance_dialog_buttons(dialog, theme_manager, preset_config)