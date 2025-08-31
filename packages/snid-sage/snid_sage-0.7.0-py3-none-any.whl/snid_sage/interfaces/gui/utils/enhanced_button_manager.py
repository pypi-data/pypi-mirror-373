"""
SNID SAGE - Enhanced Button Manager
====================================

Provides smooth visual feedback for main workflow buttons including:
- Hover animations with color transitions
- Click animations with subtle scale effects
- Professional visual feedback using existing theme colors
- No conflicts with existing workflow and theme systems

Developed by Assistant for SNID SAGE
"""

from typing import Dict, Optional
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.enhanced_buttons')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.enhanced_buttons')


class EnhancedButtonManager(QtCore.QObject):
    """
    Manager for enhanced button visual feedback
    
    This class adds smooth hover and click animations to workflow buttons
    while preserving all existing functionality and styling systems.
    Uses predefined colors for optimal performance.
    """
    
    # Predefined color states for all button types (faster than runtime calculations)
    BUTTON_COLOR_STATES = {
        'load': {
            'base': '#6E6E6E',
            'hover': '#656565', 
            'pressed': '#585858'
        },
        'redshift': {
            'base': '#FFA600',
            'hover': '#E89500',
            'pressed': '#CC8400'
        },
        'preprocessing': {
            'base': '#FF6361',
            'hover': '#E85A58',
            'pressed': '#CC514F'
        },
        'analysis': {
            'base': '#BC5090',
            'hover': '#A84981',
            'pressed': '#944272'
        },
        'advanced': {
            'base': '#58508D',
            'hover': '#4F477E',
            'pressed': '#463E6F'
        },
        'ai': {
            'base': '#003F5C',
            'hover': '#003A54',
            'pressed': '#00344B'
        },
        'settings': {
            'base': '#7A8585',
            'hover': '#6E7777',
            'pressed': '#626969'
        },
        'reset': {
            'base': '#A65965',
            'hover': '#95515C',
            'pressed': '#844953'
        },
        'info': {
            'base': '#3b82f6',
            'hover': '#2563eb',
            'pressed': '#1d4ed8'
        },
        'neutral': {
            'base': '#9ca3af',
            'hover': '#6b7280',
            'pressed': '#4b5563'
        }
    }
    
    def __init__(self, theme_manager):
        """Initialize the enhanced button manager"""
        super().__init__()
        self.theme_manager = theme_manager
        self.enhanced_buttons: Dict[str, QtWidgets.QPushButton] = {}
        self.animations: Dict[str, QtCore.QPropertyAnimation] = {}
        
        _LOGGER.info("Enhanced Button Manager initialized")
    
    def register_button(self, button: QtWidgets.QPushButton, color_type: str):
        """Register a button for enhanced feedback"""
        if not button:
            _LOGGER.warning("Cannot register None button")
            return
            
        object_name = button.objectName()
        if not object_name:
            # Generate a fallback object name if none exists
            object_name = f"enhanced_btn_{id(button)}"
            button.setObjectName(object_name)
            _LOGGER.debug(f"Generated object name for button: {object_name}")
        
        # Store button and its color type
        self.enhanced_buttons[object_name] = button
        button.setProperty("enhanced_color_type", color_type)
        button.setProperty("is_enhanced", True)
        
        # Install event filter for enhanced interactions
        button.installEventFilter(self)
        
        # Set cursor to pointing hand
        button.setCursor(QtCore.Qt.PointingHandCursor)
        
        _LOGGER.debug(f"Button {object_name} registered for enhanced feedback with color type: {color_type}")
    
    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Handle enhanced button interactions"""
        if not isinstance(obj, QtWidgets.QPushButton):
            return super().eventFilter(obj, event)
        
        if not obj.property("is_enhanced"):
            return super().eventFilter(obj, event)
        
        # Only process events for enabled buttons
        if not obj.isEnabled():
            return super().eventFilter(obj, event)
        
        try:
            if event.type() == QtCore.QEvent.Enter:
                self._animate_hover_enter(obj)
            elif event.type() == QtCore.QEvent.Leave:
                self._animate_hover_leave(obj)
            elif event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.LeftButton:
                    _LOGGER.debug(f"Button press animation triggered: {obj.objectName()} (left click)")
                    self._animate_button_press(obj)
                elif event.button() == QtCore.Qt.RightButton:
                    # Only show enhanced feedback for right-clicks on buttons that have right-click functionality
                    if self._button_has_right_click_functionality(obj):
                        _LOGGER.debug(f"Button press animation triggered: {obj.objectName()} (right click)")
                        self._animate_button_press(obj)
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton:
                    _LOGGER.debug(f"Button release animation triggered: {obj.objectName()} (left click)")
                    self._animate_button_release(obj)
                elif event.button() == QtCore.Qt.RightButton:
                    # Only show enhanced feedback for right-clicks on buttons that have right-click functionality
                    if self._button_has_right_click_functionality(obj):
                        _LOGGER.debug(f"Button release animation triggered: {obj.objectName()} (right click)")
                        self._animate_button_release(obj)
        except Exception as e:
            _LOGGER.error(f"Error in enhanced button event handling: {e}")
        
        return super().eventFilter(obj, event)
    
    def _button_has_right_click_functionality(self, button: QtWidgets.QPushButton) -> bool:
        """Check if a button has right-click functionality that should show enhanced feedback"""
        object_name = button.objectName()
        
        # Only Preprocessing and Analysis buttons have right-click functionality
        right_click_buttons = {
            'unified_preprocessing_btn',      # Preprocessing button
            'unified_analysis_btn',           # Analysis button
            'preprocessing_btn',              # Alternative name
            'analysis_btn',                   # Alternative name
        }
        
        return object_name in right_click_buttons
    
    def _is_small_button(self, object_name: str) -> bool:
        """Determine if a button should use small dimensions (24px height)"""
        small_buttons = {
            'unified_prev_btn',
            'unified_next_btn',
            'unified_cluster_summary_btn',
            'unified_gmm_btn',
            'unified_redshift_age_btn',
            'unified_subtype_proportions_btn',
            'unified_reset_btn',
            'unified_settings_btn',
            'unified_info_btn',
        }
        return object_name in small_buttons
    
    def _animate_hover_enter(self, button: QtWidgets.QPushButton):
        """Animate button on hover enter"""
        color_type = button.property("enhanced_color_type")
        if not color_type:
            return
        
        # Check if this is the cluster summary button and it's currently blinking
        # If so, don't apply hover effects to avoid size conflicts
        object_name = button.objectName()
        if object_name == "unified_cluster_summary_btn":
            if hasattr(self, '_workflow_manager_ref') and self._workflow_manager_ref:
                main_window = self._workflow_manager_ref.main_window
                if hasattr(main_window, 'cluster_summary_blinking') and main_window.cluster_summary_blinking:
                    return  # Skip hover effects while blinking
        
        base_color = self._get_color_for_type(color_type)
        if not base_color:
            return
        
        # Get predefined hover color for optimal performance (no runtime calculations)
        color_states = self.BUTTON_COLOR_STATES.get(color_type, self.BUTTON_COLOR_STATES['neutral'])
        hover_color_1 = color_states['hover']  # Predefined hover color
        hover_color_2 = base_color  # Original bottom for gradient
        
        object_name = button.objectName()
        
        # Determine button size based on object name
        if self._is_small_button(object_name):
            # Small buttons (navigation, analysis, utility) - use smaller dimensions
            if "unified_prev_btn" in object_name or "unified_next_btn" in object_name:
                font_size = "14pt"  # Navigation arrows
            elif "unified_reset_btn" in object_name or "unified_settings_btn" in object_name:
                font_size = "9pt"   # Utility buttons
            elif "unified_info_btn" in object_name:
                font_size = "14px"  # Info button (uses px like in its inline style)
            elif "unified_gmm_btn" in object_name or "unified_redshift_age_btn" in object_name or "unified_subtype_proportions_btn" in object_name:
                font_size = "14pt"  # Larger emoji buttons
            else:
                font_size = "12pt"  # Default small buttons (cluster summary)
            padding = "2px 4px"
            min_height = "24px"
        else:
            # Main workflow buttons - use standard dimensions
            font_size = "11pt"
            padding = "6px 12px"
            min_height = "32px"
        
        enhanced_style = f"""
        QPushButton#{object_name} {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {hover_color_1},
                stop:1 {hover_color_2});
            color: white;
            border: 2px solid {base_color};
            border-radius: 4px;
            font-weight: bold;
            font-size: {font_size};
            padding: {padding};
            min-height: {min_height};
        }}
        """
        
        button.setStyleSheet(enhanced_style)
    
    def _animate_hover_leave(self, button: QtWidgets.QPushButton):
        """Animate button on hover leave - restore workflow manager styling"""
        # Let the workflow manager handle the styling restoration
        # This ensures consistency with the existing system
        object_name = button.objectName()
        color_type = button.property("enhanced_color_type")
        
        # Check if this is the cluster summary button and it's currently blinking
        # If so, don't apply hover leave effects to avoid size conflicts
        if object_name == "unified_cluster_summary_btn":
            if hasattr(self, '_workflow_manager_ref') and self._workflow_manager_ref:
                main_window = self._workflow_manager_ref.main_window
                if hasattr(main_window, 'cluster_summary_blinking') and main_window.cluster_summary_blinking:
                    return  # Skip hover leave effects while blinking
        
        if color_type and hasattr(self, '_workflow_manager_ref'):
            # Use workflow manager's styling with appropriate dimensions
            base_color = self._get_color_for_type(color_type)
            if not base_color:
                return
                
            # Determine button size based on object name
            if self._is_small_button(object_name):
                # Small buttons (navigation, analysis, utility) - use smaller dimensions
                if "unified_prev_btn" in object_name or "unified_next_btn" in object_name:
                    font_size = "14pt"  # Navigation arrows
                elif "unified_reset_btn" in object_name or "unified_settings_btn" in object_name:
                    font_size = "9pt"   # Utility buttons
                elif "unified_gmm_btn" in object_name or "unified_redshift_age_btn" in object_name or "unified_subtype_proportions_btn" in object_name:
                    font_size = "14pt"  # Larger emoji buttons
                else:
                    font_size = "12pt"  # Default small buttons (cluster summary)
                padding = "2px 4px"
                min_height = "24px"
            else:
                # Main workflow buttons - use standard dimensions
                font_size = "11pt"
                padding = "6px 12px"
                min_height = "32px"
            
            basic_style = f"""
            QPushButton#{object_name} {{
                background: {base_color} !important;
                color: white !important;
                border: 2px solid {base_color} !important;
                border-radius: 4px;
                font-weight: bold;
                font-size: {font_size};
                padding: {padding};
                min-height: {min_height};
            }}
            """
            button.setStyleSheet(basic_style)
        else:
            # Fallback to basic styling with correct dimensions
            base_color = self._get_color_for_type(color_type)
            if not base_color:
                return
            
            # Determine button size
            if self._is_small_button(object_name):
                if "unified_prev_btn" in object_name or "unified_next_btn" in object_name:
                    font_size = "14pt"  # Navigation arrows
                elif "unified_reset_btn" in object_name or "unified_settings_btn" in object_name:
                    font_size = "9pt"   # Utility buttons
                elif "unified_gmm_btn" in object_name or "unified_redshift_age_btn" in object_name or "unified_subtype_proportions_btn" in object_name:
                    font_size = "14pt"  # Larger emoji buttons
                else:
                    font_size = "12pt"  # Default small buttons (cluster summary)
                padding = "2px 4px"
                min_height = "24px"
            else:
                font_size = "11pt"
                padding = "6px 12px"
                min_height = "32px"
            
            basic_style = f"""
            QPushButton#{object_name} {{
                background: {base_color};
                color: white;
                border: 2px solid {base_color};
                border-radius: 4px;
                font-weight: bold;
                font-size: {font_size};
                padding: {padding};
                min-height: {min_height};
            }}
            """
            button.setStyleSheet(basic_style)
    
    def _animate_button_press(self, button: QtWidgets.QPushButton):
        """Animate button press with subtle scale effect"""
        color_type = button.property("enhanced_color_type")
        if not color_type:
            return
        
        base_color = self._get_color_for_type(color_type)
        if not base_color:
            return
        
        # Create subtle scale animation
        object_name = button.objectName()
        animation_key = f"{object_name}_press"
        
        # Clean up any existing animation
        if animation_key in self.animations:
            self.animations[animation_key].stop()
            del self.animations[animation_key]
        
        # No geometry animation to keep button shape consistent
        # We'll rely on color changes only for visual feedback
        
        # Enhanced pressed styling - keep same shape but change colors only
        # Use predefined pressed colors for optimal performance and consistency
        color_states = self.BUTTON_COLOR_STATES.get(color_type, self.BUTTON_COLOR_STATES['neutral'])
        pressed_color_1 = color_states['pressed']  # Predefined pressed color
        pressed_color_2 = color_states['hover']    # Slightly lighter gradient bottom
        
        # Determine button size based on object name
        if self._is_small_button(object_name):
            # Small buttons (navigation, analysis, utility) - use smaller dimensions
            if "unified_prev_btn" in object_name or "unified_next_btn" in object_name:
                font_size = "14pt"  # Navigation arrows
            elif "unified_reset_btn" in object_name or "unified_settings_btn" in object_name:
                font_size = "9pt"   # Utility buttons
            elif "unified_info_btn" in object_name:
                font_size = "14px"  # Info button (uses px like in its inline style)
            elif "unified_gmm_btn" in object_name or "unified_redshift_age_btn" in object_name or "unified_subtype_proportions_btn" in object_name:
                font_size = "14pt"  # Larger emoji buttons
            else:
                font_size = "12pt"  # Default small buttons (cluster summary)
            padding = "2px 4px"
            min_height = "24px"
        else:
            # Main workflow buttons - use standard dimensions
            font_size = "11pt"
            padding = "6px 12px"
            min_height = "32px"
        
        pressed_style = f"""
        QPushButton#{object_name} {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {pressed_color_1},
                stop:1 {pressed_color_2});
            color: white;
            border: 2px solid {base_color};
            border-radius: 4px;
            font-weight: bold;
            font-size: {font_size};
            padding: {padding};
            min-height: {min_height};
        }}
        """
        
        button.setStyleSheet(pressed_style)
    
    def _animate_button_release(self, button: QtWidgets.QPushButton):
        """Animate button release"""
        object_name = button.objectName()
        animation_key = f"{object_name}_release"
        press_animation_key = f"{object_name}_press"
        
        # Clean up press animation
        if press_animation_key in self.animations:
            self.animations[press_animation_key].stop()
            del self.animations[press_animation_key]
        
        # No geometry restoration needed since we don't change geometry anymore
        
        # Return to hover state
        self._animate_hover_enter(button)
    
    def _get_color_for_type(self, color_type: str) -> Optional[str]:
        """Get base color for button type using predefined colors"""
        color_states = self.BUTTON_COLOR_STATES.get(color_type, self.BUTTON_COLOR_STATES['neutral'])
        return color_states['base']
    
    # Color calculation methods removed - now using predefined colors for better performance
    
    def set_workflow_manager_reference(self, workflow_manager):
        """Set reference to workflow manager for proper style restoration"""
        self._workflow_manager_ref = workflow_manager
    
    def cleanup(self):
        """Clean up animations and event filters"""
        for animation in self.animations.values():
            animation.stop()
        self.animations.clear()
        
        for button in self.enhanced_buttons.values():
            button.removeEventFilter(self)
        
        self.enhanced_buttons.clear()
        _LOGGER.info("Enhanced Button Manager cleaned up")