"""
SNID SAGE - PySide6 Workflow Manager
====================================

Manages button states and workflow progression for the PySide6 GUI.

This system provides:
- Centralized button state management
- Workflow progression tracking
- Color-coded button states
- Cross-platform consistent styling

Developed by Fiorenzo Stoppa for SNID SAGE
"""

from typing import Dict, List, Optional, Callable
from enum import Enum
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_workflow')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_workflow')

# Import WorkflowState from controller
from snid_sage.interfaces.gui.controllers.pyside6_app_controller import WorkflowState

# Import unified theme manager
from .pyside6_theme_manager import get_pyside6_theme_manager


class ButtonDefinition:
    """Definition of a workflow button"""
    def __init__(self, name: str, color_type: str, activation_state: WorkflowState, always_enabled: bool = False):
        self.name = name
        self.color_type = color_type  # Theme manager button type (load, preprocessing, etc.)
        self.activation_state = activation_state
        self.always_enabled = always_enabled


class PySide6WorkflowManager:
    """
    Manages button states and workflow progression for PySide6 GUI
    
    This class coordinates button states according to workflow progression,
    providing visual feedback and preventing invalid operations.
    """
    
    def _get_button_definitions(self):
        """Get button definitions using theme manager colors"""
        return {
            # Always available buttons
            'load_btn': ButtonDefinition('load_btn', 'load', WorkflowState.INITIAL, always_enabled=True),
            'reset_btn': ButtonDefinition('reset_btn', 'reset', WorkflowState.INITIAL, always_enabled=True),
            'settings_btn': ButtonDefinition('settings_btn', 'settings', WorkflowState.INITIAL, always_enabled=True),
            'info_btn': ButtonDefinition('info_btn', 'info', WorkflowState.INITIAL, always_enabled=True),
            
            # Workflow progression buttons
            'preprocessing_btn': ButtonDefinition('preprocessing_btn', 'preprocessing', WorkflowState.FILE_LOADED),
            'redshift_selection_btn': ButtonDefinition('redshift_selection_btn', 'redshift', WorkflowState.FILE_LOADED),
            'analysis_btn': ButtonDefinition('analysis_btn', 'analysis', WorkflowState.PREPROCESSED),
            
            # Advanced features (enabled after analysis)
            'emission_line_btn': ButtonDefinition('emission_line_btn', 'advanced', WorkflowState.ANALYSIS_COMPLETE),
            'cluster_summary_btn': ButtonDefinition('cluster_summary_btn', 'advanced', WorkflowState.ANALYSIS_COMPLETE),
            'gmm_btn': ButtonDefinition('gmm_btn', 'advanced', WorkflowState.ANALYSIS_COMPLETE),
            'redshift_age_btn': ButtonDefinition('redshift_age_btn', 'advanced', WorkflowState.ANALYSIS_COMPLETE),
            'subtype_proportions_btn': ButtonDefinition('subtype_proportions_btn', 'advanced', WorkflowState.ANALYSIS_COMPLETE),
            
            # AI features
            'chat_btn': ButtonDefinition('chat_btn', 'ai', WorkflowState.ANALYSIS_COMPLETE),
            
            # Navigation buttons 
            'prev_btn': ButtonDefinition('prev_btn', 'advanced', WorkflowState.ANALYSIS_COMPLETE),  # template nav after analysis
            'next_btn': ButtonDefinition('next_btn', 'advanced', WorkflowState.ANALYSIS_COMPLETE),  # template nav after analysis

            
            # Mask buttons (enabled after file loaded)
            'mask_btn': ButtonDefinition('mask_btn', 'neutral', WorkflowState.FILE_LOADED),
            'clear_masks_btn': ButtonDefinition('clear_masks_btn', 'neutral', WorkflowState.FILE_LOADED),
        }
    
    def __init__(self, main_window):
        """Initialize the workflow manager"""
        self.main_window = main_window
        self.current_state = WorkflowState.INITIAL
        self.button_widgets: Dict[str, QtWidgets.QPushButton] = {}
        self.state_change_callbacks: List[Callable[[WorkflowState], None]] = []
        
        # Get theme manager for consistent styling
        self.theme_manager = get_pyside6_theme_manager()
        
        # Initialize enhanced button manager for smooth animations
        self.enhanced_button_manager = self.theme_manager.create_enhanced_button_manager()
        self.enhanced_button_manager.set_workflow_manager_reference(self)
        
        _LOGGER.info("PySide6 Workflow Manager initialized with enhanced button feedback")
    
    def register_button(self, button_name: str, button_widget: QtWidgets.QPushButton):
        """Register a button widget with the workflow system"""
        button_definitions = self._get_button_definitions()
        if button_name in button_definitions:
            self.button_widgets[button_name] = button_widget
            
            # Set initial state
            definition = button_definitions[button_name]
            if definition.always_enabled:
                self._set_button_state(button_widget, True, definition.color_type)
                _LOGGER.debug(f"Button {button_name} configured: {definition.color_type} (always enabled)")
            else:
                self._set_button_state(button_widget, False, "disabled")
                _LOGGER.debug(f"Button {button_name} configured: disabled")
            
            # Register with enhanced button manager for main workflow buttons
            if self._is_main_workflow_button(button_name):
                self.enhanced_button_manager.register_button(button_widget, definition.color_type)
                _LOGGER.debug(f"Button {button_name} registered for enhanced feedback")
            
            _LOGGER.debug(f"Button {button_name} registered with workflow system")
        else:
            _LOGGER.warning(f"Unknown button name: {button_name}")
    
    def update_workflow_state(self, new_state: WorkflowState):
        """Update workflow state and refresh all button states"""
        old_state = self.current_state
        self.current_state = new_state
        
        # Update all button states
        self._update_all_buttons()
        
        # Notify callbacks
        for callback in self.state_change_callbacks:
            try:
                callback(new_state)
            except Exception as e:
                _LOGGER.error(f"Error in state change callback: {e}")
        
        _LOGGER.info(f"Workflow state updated: {old_state.value} → {new_state.value}")
    
    def _update_all_buttons(self):
        """Update all registered buttons according to current state"""
        button_definitions = self._get_button_definitions()
        for button_name, button_widget in self.button_widgets.items():
            if button_name in button_definitions:
                definition = button_definitions[button_name]
                self._update_single_button(button_name, definition)
    
    def _update_single_button(self, button_name: str, definition: ButtonDefinition):
        """Update a single button's state based on current workflow"""
        button_widget = self.button_widgets[button_name]
        
        # Determine if button should be enabled
        should_enable = self._should_button_be_enabled(definition)
        
        # Set button state and color
        if should_enable:
            self._set_button_state(button_widget, True, definition.color_type)
            _LOGGER.debug(f"Button {button_name}: ENABLED with color type {definition.color_type}")
        else:
            self._set_button_state(button_widget, False, "disabled")
            _LOGGER.debug(f"Button {button_name}: DISABLED")
    
    def _should_button_be_enabled(self, definition: ButtonDefinition) -> bool:
        """Determine if a button should be enabled based on current state"""
        # Always enabled buttons
        if definition.always_enabled:
            return True
        
        # Check if we've reached the required state
        state_order = [
            WorkflowState.INITIAL,
            WorkflowState.FILE_LOADED,
            WorkflowState.PREPROCESSED,
            WorkflowState.REDSHIFT_SET,
            WorkflowState.ANALYSIS_COMPLETE,
            WorkflowState.AI_READY
        ]
        
        try:
            current_index = state_order.index(self.current_state)
            required_index = state_order.index(definition.activation_state)
            
            # Basic workflow state check
            state_requirement_met = current_index >= required_index
            
            # Special case for navigation buttons: also check if templates are available
            if definition.name in ['prev_btn', 'next_btn'] and state_requirement_met:
                # Check if we have analysis results with templates for navigation
                if hasattr(self.main_window, 'app_controller') and self.main_window.app_controller:
                    controller = self.main_window.app_controller
                    if (hasattr(controller, 'snid_results') and controller.snid_results and
                        hasattr(controller.snid_results, 'best_matches') and controller.snid_results.best_matches):
                        # Templates are available - enable navigation
                        return True
                    else:
                        # No templates available yet - keep disabled
                        return False
                else:
                    # No controller available - fall back to basic state check
                    return state_requirement_met
            
            # Special case for advanced features after analysis: require reliable matches
            if definition.name in [
                'emission_line_btn', 'cluster_summary_btn', 'gmm_btn',
                'redshift_age_btn', 'subtype_proportions_btn', 'chat_btn'
            ] and state_requirement_met:
                if hasattr(self.main_window, 'app_controller') and self.main_window.app_controller:
                    controller = self.main_window.app_controller
                    res = getattr(controller, 'snid_results', None)
                    if res is None:
                        return False
                    # Reliable if clustering succeeded or thresholded filtered_matches exist
                    has_cluster = bool(getattr(res, 'clustering_results', None)) and res.clustering_results.get('success', False)
                    has_thresholded = bool(getattr(res, 'filtered_matches', []))
                    return bool(has_cluster or has_thresholded)
                else:
                    return False
            
            # For all other buttons, just use the basic workflow state check
            return state_requirement_met
            
        except ValueError:
            # Handle unknown states
            _LOGGER.warning(f"Unknown state in workflow: {self.current_state} or {definition.activation_state}")
            return False
    
    def _set_button_state(self, button: QtWidgets.QPushButton, enabled: bool, color_type: str):
        """Set button enabled state and styling using theme manager"""
        try:
            button.setEnabled(enabled)
            
            # Get object name for targeted styling
            object_name = button.objectName()
            
            # Validate object name to prevent stylesheet parsing errors
            if not object_name or not object_name.strip():
                _LOGGER.warning(f"Button has no object name, using generic styling")
                object_name = "button"
                button.setObjectName(object_name)
            
            # Get color from theme manager or use disabled colors
            if enabled and color_type != "disabled":
                # Use theme manager for workflow button styling
                button_style = self.theme_manager.get_workflow_button_style(color_type)
                stylesheet = f"QPushButton#{object_name} {{ {button_style} }}"
            else:
                # Use disabled styling from theme manager - HEIGHT IS HANDLED BY CSS
                disabled_bg = self.theme_manager.get_color('bg_disabled')
                disabled_text = self.theme_manager.get_color('text_muted')
                
                stylesheet = f"""
                QPushButton#{object_name} {{
                    background: {disabled_bg} !important;
                    color: {disabled_text} !important;
                    border: 2px solid {disabled_bg} !important;
                }}"""
            
            button.setStyleSheet(stylesheet)
            
        except Exception as e:
            _LOGGER.error(f"Error setting button state: {e}")
    

    
    def add_state_change_callback(self, callback: Callable[[WorkflowState], None]):
        """Add a callback function to be called when workflow state changes"""
        self.state_change_callbacks.append(callback)
    
    def refresh_button_states(self):
        """Refresh all button states based on current conditions"""
        self._update_all_buttons()
        _LOGGER.debug("Button states refreshed manually")
    
    def get_current_state(self) -> WorkflowState:
        """Get current workflow state"""
        return self.current_state
    
    def force_state_transition(self, target_state: WorkflowState):
        """Force transition to a specific state (for testing/debugging)"""
        self.update_workflow_state(target_state)
        _LOGGER.info(f"Forced state transition to: {target_state.value}")
    
    def _is_main_workflow_button(self, button_name: str) -> bool:
        """Determine if a button should receive enhanced feedback"""
        # Main workflow buttons that should get enhanced animations
        main_workflow_buttons = {
            'load_btn',
            'preprocessing_btn', 
            'redshift_selection_btn',
            'analysis_btn',
            'emission_line_btn',
            'chat_btn',  # AI Assistant
            # Always-enabled utility buttons
            'reset_btn',
            'settings_btn',
            'info_btn',
            # Navigation buttons
            'prev_btn',
            'next_btn',
            # Analysis plot buttons
            'cluster_summary_btn',
            'gmm_btn',
            'redshift_age_btn',
            'subtype_proportions_btn',
        }
        
        return button_name in main_workflow_buttons
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'enhanced_button_manager'):
            self.enhanced_button_manager.cleanup()
        _LOGGER.info("Workflow Manager cleaned up") 