"""
SNID SAGE - Enhanced Dialog Button Manager
==========================================

Provides consistent visual feedback and styling for dialog buttons including:
- Unified color system by button meaning (Apply=green, Cancel=red, etc.)
- Consistent sizing for dialog buttons (smaller than main GUI buttons)
- Smooth hover and click animations
- Support for special button behaviors (toggle buttons, etc.)
- Professional visual feedback using theme colors

Developed by Assistant for SNID SAGE
"""

from typing import Dict, Optional, Callable, Any
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.enhanced_dialog_buttons')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.enhanced_dialog_buttons')


class EnhancedDialogButtonManager(QtCore.QObject):
    """
    Manager for enhanced dialog button visual feedback and styling
    
    This class provides:
    - Consistent visual feedback for all dialog buttons
    - Unified color system based on button function/meaning
    - Proper sizing for dialog buttons (smaller than main GUI)
    - Support for special button behaviors (toggles, state changes)
    """
    
    # Color definitions by button meaning - Updated to reuse main GUI colors
    BUTTON_COLORS = {
        # Primary actions - updated green per user preference
        'apply': '#048c36',           # Apply, Accept, Continue, Proceed
        'apply_hover': '#037a2f',
        'apply_pressed': '#026a2a',
        
        # Secondary actions - using main GUI analysis color (magenta)  
        'secondary': '#BC5090',       # OK, Confirm, Yes - matches analysis button
        'secondary_hover': '#A84981',
        'secondary_pressed': '#944272',
        
        # Destructive/Cancel actions - using main GUI reset color (cranberry)
        'cancel': '#A65965',          # Cancel, Close, No, Remove - matches reset button
        'cancel_hover': '#95515C',
        'cancel_pressed': '#844953',
        
        # Utility actions - using main GUI advanced color (purple)
        'utility': '#58508D',         # Export, Save, Copy - matches advanced button
        'utility_hover': '#4F477E',
        'utility_pressed': '#463E6F',
        
        # Info/Help actions - use same blue as main GUI top-left info button
        'info': '#3b82f6',           # Help, Info, Show
        'info_hover': '#2563eb',
        'info_pressed': '#1d4ed8',
        
        # Reset/Refresh actions - match Cancel styling per request
        'reset': '#A65965',          # Reset, Restart, Refresh, Clear
        'reset_hover': '#95515C',
        'reset_pressed': '#844953',
        
        # Navigation actions - using main GUI redshift color (coral)
        'navigation': '#FF6361',      # Previous, Next, Back - matches redshift button
        'navigation_hover': '#E85A58',
        'navigation_pressed': '#CC514F',
        
        # Neutral actions - using main GUI AI color (deep blue)
        'neutral': '#003F5C',         # Hide, Test, Browse - matches AI button
        'neutral_hover': '#003A54',
        'neutral_pressed': '#00344B',
        'neutral_pressed': '#00344B',
        
        # Accent actions - same green as apply per user preference
        'accent': '#048c36',          # Special actions
        'accent_hover': '#037a2f',
        'accent_pressed': '#026a2a',
        
        # Toggle button states - using main GUI colors
        'toggle_inactive': '#6E6E6E',  # Using load button color for inactive
        'toggle_inactive_hover': '#656565',
        'toggle_active': '#FFA600',    # Using preprocessing button color for active
        'toggle_active_hover': '#E89500',
    }
    
    # Button type mappings based on text content and common patterns
    BUTTON_TYPE_PATTERNS = {
        # Apply/Continue actions
        'apply': ['apply', 'accept', 'continue', 'proceed', 'run', 'start', 'analyze'],
        
        # Secondary actions
        'secondary': ['ok', 'confirm', 'yes', 'done'],
        
        # Cancel/Close actions
        'cancel': ['cancel', 'close', 'no', 'remove', 'delete', 'clear all', 'stop'],
        
        # Utility actions
        'utility': ['export', 'save', 'copy', 'load', 'import'],
        
        # Info/Help actions
        'info': ['help', 'info', 'show', 'instructions'],
        
        # Reset/Refresh actions
        'reset': ['reset', 'restart', 'refresh', 'clear', 'revert'],
        
        # Navigation actions
        'navigation': ['previous', 'next', 'back', 'step', '←', '→', '◀', '▶'],
        
        # Neutral actions
        'neutral': ['hide', 'test', 'browse', 'fetch'],
        
        # Accent actions (special features)
        'accent': ['accept redshift', 'continue analysis', 'run analysis'],
    }
    
    def __init__(self, theme_manager=None):
        """Initialize the enhanced dialog button manager"""
        super().__init__()
        self.theme_manager = theme_manager
        self.enhanced_buttons: Dict[str, QtWidgets.QPushButton] = {}
        self.button_configs: Dict[str, Dict[str, Any]] = {}
        
        _LOGGER.info("Enhanced Dialog Button Manager initialized")
    
    def register_button(
        self, 
        button: QtWidgets.QPushButton, 
        button_type: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ):
        """
        Register a dialog button for enhanced visual feedback
        
        Args:
            button: The QPushButton to enhance
            button_type: Type of button ('apply', 'cancel', etc.) - auto-detected if None
            custom_config: Custom configuration for special buttons (toggles, etc.)
        """
        if not button:
            _LOGGER.warning("Cannot register None button")
            return
            
        object_name = button.objectName()
        if not object_name:
            # Generate a fallback object name if none exists
            object_name = f"enhanced_dialog_btn_{id(button)}"
            button.setObjectName(object_name)
            _LOGGER.debug(f"Generated object name for dialog button: {object_name}")
        
        # Auto-detect button type if not provided
        if button_type is None:
            button_type = self._detect_button_type(button)
        
        # Store button configuration
        config = custom_config or {}
        config['type'] = button_type
        config['is_toggle'] = config.get('is_toggle', False)
        config['toggle_state'] = config.get('toggle_state', False)
        config['size_class'] = config.get('size_class', 'normal')  # normal, small, icon
        
        self.enhanced_buttons[object_name] = button
        self.button_configs[object_name] = config
        
        # Apply initial styling
        self._apply_button_styling(button, button_type, config)
        
        # Install event filter for enhanced interactions
        button.installEventFilter(self)
        
        # Set cursor to pointing hand
        button.setCursor(QtCore.Qt.PointingHandCursor)
        
        _LOGGER.debug(f"Dialog button {object_name} registered with type: {button_type}")
    
    def update_button_state(self, button: QtWidgets.QPushButton, enabled: bool = True):
        """
        Update button state (enabled/disabled) with appropriate styling
        
        Args:
            button: The button to update
            enabled: Whether the button should be enabled
        """
        # Guard against deleted objects
        try:
            button.objectName()
        except RuntimeError:
            return

        button.setEnabled(enabled)
        
        object_name = button.objectName()
        config = self.button_configs.get(object_name, {})
        button_type = config.get('type', 'neutral')
        
        # Update styling based on enabled state
        if enabled:
            self._apply_button_styling(button, button_type, config)
        else:
            # Apply disabled styling
            self._apply_disabled_styling(button, config)
    
    def _apply_disabled_styling(self, button: QtWidgets.QPushButton, config: Dict[str, Any]):
        """Apply disabled styling to a button"""
        size_class = config.get('size_class', 'normal')
        
        if size_class == 'small':
            height = "20px"
            font_size = "8pt"
            padding = "2px 6px"
        elif size_class == 'icon':
            height = "24px"
            font_size = "10pt"
            padding = "2px"
        else:
            height = "24px"
            font_size = "9pt"
            padding = "4px 8px"
        
        # Use a muted gray color for disabled buttons
        disabled_color = "#9ca3af"  # gray-400
        disabled_text_color = "#6b7280"  # gray-500
        
        disabled_style = f"""
        QPushButton {{
            background-color: {disabled_color};
            color: {disabled_text_color};
            border: 2px solid {disabled_color};
            border-radius: 4px;
            font-weight: bold;
            font-size: {font_size};
            padding: {padding};
            min-height: {height};
            font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
        }}
        QPushButton:focus {{
            outline: none;
        }}
        """
        
        try:
            # Check if the C++ object is still valid
            if hasattr(button, 'setStyleSheet') and button is not None:
                try:
                    button.objectName()  # This will raise RuntimeError if object is deleted
                    button.setStyleSheet(disabled_style)
                except RuntimeError:
                    # Object has been deleted, skip styling
                    pass
        except RuntimeError:
            # Handle deleted Qt objects silently
            pass
    
    def _detect_button_type(self, button: QtWidgets.QPushButton) -> str:
        """Auto-detect button type based on text content"""
        text = button.text().lower().strip()
        
        # Remove common emojis and symbols for detection
        clean_text = text
        for char in ['🔄', '❌', '✅', '📊', '📋', '💾', '🔍', '❓', '→', '←', '◀', '▶']:
            clean_text = clean_text.replace(char, '').strip()
        
        # Check patterns
        for button_type, patterns in self.BUTTON_TYPE_PATTERNS.items():
            for pattern in patterns:
                if pattern in clean_text:
                    return button_type
        
        # Default to neutral for unrecognized buttons
        return 'neutral'
    
    def _apply_button_styling(
        self, 
        button: QtWidgets.QPushButton, 
        button_type: str, 
        config: Dict[str, Any]
    ):
        """Apply consistent styling to a dialog button"""
        size_class = config.get('size_class', 'normal')
        is_toggle = config.get('is_toggle', False)
        toggle_state = config.get('toggle_state', False)
        
        # Determine colors based on type and state
        if is_toggle:
            # Allow per-button override colors; fall back to global palette
            if toggle_state:
                base_color = (
                    config.get('active_color')
                    or self.BUTTON_COLORS['toggle_active']
                )
            else:
                base_color = (
                    config.get('inactive_color')
                    or self.BUTTON_COLORS['toggle_inactive']
                )
            # For hover, use a gradient derived from the base color
            hover_color = base_color
        else:
            base_color = self.BUTTON_COLORS.get(button_type, self.BUTTON_COLORS['neutral'])
            hover_color = self.BUTTON_COLORS.get(f"{button_type}_hover", self.BUTTON_COLORS['neutral_hover'])
        
        # Determine sizing based on size class
        if size_class == 'small':
            height = "20px"
            font_size = "8pt"
            padding = "2px 6px"
        elif size_class == 'icon':
            height = "24px"
            font_size = "10pt"
            padding = "2px"
            button.setMaximumWidth(24)
        else:  # normal
            height = "24px"
            font_size = "9pt"
            padding = "4px 8px"
        
        # Apply base styling with safety check for deleted objects
        try:
            # Check if the C++ object is still valid
            if not hasattr(button, 'setStyleSheet') or button is None:
                return
            
            # Additional check for deleted Qt objects
            try:
                button.objectName()  # This will raise RuntimeError if object is deleted
            except RuntimeError:
                # Object has been deleted, skip styling
                return
            
            button.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                border: 2px solid {base_color};
                border-radius: 4px;
                font-weight: bold;
                font-size: {font_size};
                padding: {padding};
                min-height: {height};
                font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-color: {hover_color};
            }}
            QPushButton:focus {{
                outline: none;
            }}
            """)
        except RuntimeError as e:
            # Handle case where Qt object was deleted
            if "Internal C++ object" in str(e) and "already deleted" in str(e):
                # This is expected during dialog cleanup, silently ignore
                return
            else:
                # Re-raise unexpected errors
                raise
        
        # Store original style info for animations (with safety checks)
        try:
            button.setProperty("enhanced_base_color", base_color)
            button.setProperty("enhanced_hover_color", hover_color)
            button.setProperty("enhanced_type", button_type)
            button.setProperty("enhanced_config", config)
        except RuntimeError:
            # Object was deleted while we were working with it
            pass
    
    def update_toggle_button(self, button: QtWidgets.QPushButton, new_state: bool):
        """Update a toggle button's visual state"""
        # Guard against deleted objects
        if button is None:
            return
        try:
            button.objectName()
        except RuntimeError:
            return

        object_name = button.objectName()
        if object_name not in self.button_configs:
            _LOGGER.warning(f"Button {object_name} not registered for toggle updates")
            return
        
        config = self.button_configs[object_name]
        if not config.get('is_toggle', False):
            _LOGGER.warning(f"Button {object_name} is not configured as a toggle button")
            return
        
        # Update config
        config['toggle_state'] = new_state
        
        # Reapply styling with new state
        button_type = config['type']
        try:
            self._apply_button_styling(button, button_type, config)
        except RuntimeError:
            # Silently ignore if button is gone during update
            pass
    
    def register_toggle_button(
        self, 
        button: QtWidgets.QPushButton,
        toggle_callback: Callable[[bool], None],
        initial_state: bool = False,
        active_text: str = None,
        inactive_text: str = None,
        active_color: str = None,
        inactive_color: str = None
    ):
        """
        Register a toggle button with special behavior
        
        Args:
            button: The toggle button
            toggle_callback: Function called when toggle state changes
            initial_state: Initial toggle state
            active_text: Text when active (optional)
            inactive_text: Text when inactive (optional)
            active_color: Color when active (optional)
            inactive_color: Color when inactive (optional)
        """
        config = {
            'is_toggle': True,
            'toggle_state': initial_state,
            'toggle_callback': toggle_callback,
            'active_text': active_text,
            'inactive_text': inactive_text,
            'active_color': active_color,
            'inactive_color': inactive_color,
        }
        
        # Set initial text if provided
        if initial_state and active_text:
            button.setText(active_text)
        elif not initial_state and inactive_text:
            button.setText(inactive_text)
        
        # Register with toggle configuration
        self.register_button(button, 'neutral', config)
        
        # Connect click handler for toggle behavior
        button.clicked.connect(lambda: self._handle_toggle_click(button))
    
    def _handle_toggle_click(self, button: QtWidgets.QPushButton):
        """Handle click on toggle button"""
        object_name = button.objectName()
        config = self.button_configs.get(object_name, {})
        
        if not config.get('is_toggle', False):
            return
        
        # Toggle state
        new_state = not config['toggle_state']
        config['toggle_state'] = new_state
        
        # Update text if configured
        if new_state and config.get('active_text'):
            button.setText(config['active_text'])
        elif not new_state and config.get('inactive_text'):
            button.setText(config['inactive_text'])
        
        # Update styling
        self.update_toggle_button(button, new_state)
        
        # Call callback if provided
        callback = config.get('toggle_callback')
        if callback:
            try:
                callback(new_state)
            except Exception as e:
                _LOGGER.error(f"Error in toggle callback for {object_name}: {e}")
    
    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Handle enhanced button interactions"""
        if not isinstance(obj, QtWidgets.QPushButton):
            return super().eventFilter(obj, event)
        
        object_name = obj.objectName()
        if object_name not in self.enhanced_buttons:
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
                    self._animate_button_press(obj)
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton:
                    self._animate_button_release(obj)
        except Exception as e:
            _LOGGER.error(f"Error in event filter for {object_name}: {e}")
        
        return super().eventFilter(obj, event)
    
    def _animate_hover_enter(self, button: QtWidgets.QPushButton):
        """Animate button on hover enter"""
        # Get colors from button properties
        hover_color = button.property("enhanced_hover_color")
        if not hover_color:
            return
        
        # Apply hover style directly (no animation needed for immediate feedback)
        hover_style = self._create_hover_style(button, hover_color)
        try:
            if hasattr(button, 'setStyleSheet') and button is not None:
                try:
                    button.objectName()  # Check if object is deleted
                    button.setStyleSheet(hover_style)
                except RuntimeError:
                    pass
        except RuntimeError:
            pass
    
    def _animate_hover_leave(self, button: QtWidgets.QPushButton):
        """Animate button on hover leave"""
        # Get base color from button properties
        base_color = button.property("enhanced_base_color")
        if not base_color:
            return
        
        # Apply base style directly
        base_style = self._create_base_style(button, base_color)
        try:
            if hasattr(button, 'setStyleSheet') and button is not None:
                try:
                    button.objectName()  # Check if object is deleted
                    button.setStyleSheet(base_style)
                except RuntimeError:
                    pass
        except RuntimeError:
            pass
    
    def _animate_button_press(self, button: QtWidgets.QPushButton):
        """Animate button press with darker color effect"""
        # Get pressed color
        button_type = button.property("enhanced_type")
        config = button.property("enhanced_config") or {}
        
        if config.get('is_toggle', False):
            # Darken whichever color is currently shown (active or inactive)
            current_color = (
                config.get('active_color') if config.get('toggle_state', False)
                else config.get('inactive_color')
            ) or button.property("enhanced_base_color") or self.BUTTON_COLORS.get(button_type, '#6E6E6E')
            pressed_color = self._darken_color(current_color, 0.15)
        else:
            pressed_color = self.BUTTON_COLORS.get(
                f"{button_type}_pressed", 
                self.BUTTON_COLORS['neutral_pressed']
            )
        
        # Apply pressed style immediately
        pressed_style = self._create_pressed_style(button, pressed_color)
        try:
            if hasattr(button, 'setStyleSheet') and button is not None:
                try:
                    button.objectName()  # Check if object is deleted
                    button.setStyleSheet(pressed_style)
                except RuntimeError:
                    pass
        except RuntimeError:
            pass
    
    def _animate_button_release(self, button: QtWidgets.QPushButton):
        """Animate button release"""
        # Transition back to hover state
        hover_color = button.property("enhanced_hover_color")
        if hover_color:
            hover_style = self._create_hover_style(button, hover_color)
            try:
                if hasattr(button, 'setStyleSheet') and button is not None:
                    try:
                        button.objectName()  # Check if object is deleted
                        button.setStyleSheet(hover_style)
                    except RuntimeError:
                        pass
            except RuntimeError:
                pass
    
    def _create_base_style(self, button: QtWidgets.QPushButton, color: str) -> str:
        """Create base button style"""
        config = self.button_configs.get(button.objectName(), {})
        size_class = config.get('size_class', 'normal')
        
        if size_class == 'small':
            height = "20px"
            font_size = "8pt"
            padding = "2px 6px"
        elif size_class == 'icon':
            height = "24px"
            font_size = "10pt"
            padding = "2px"
        else:
            height = "24px"
            font_size = "9pt"
            padding = "4px 8px"
        
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: 2px solid {color};
            border-radius: 4px;
            font-weight: bold;
            font-size: {font_size};
            padding: {padding};
            min-height: {height};
            font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
        }}
        QPushButton:focus {{
            outline: none;
        }}
        """
    
    def _create_hover_style(self, button: QtWidgets.QPushButton, color: str) -> str:
        """Create hover button style using gradient like main GUI buttons"""
        config = self.button_configs.get(button.objectName(), {})
        size_class = config.get('size_class', 'normal')
        
        if size_class == 'small':
            height = "20px"
            font_size = "8pt"
            padding = "2px 6px"
        elif size_class == 'icon':
            height = "24px"
            font_size = "10pt"
            padding = "2px"
        else:
            height = "24px"
            font_size = "9pt"
            padding = "4px 8px"
        
        # Create subtle gradient effect like main GUI buttons
        hover_color_1 = self._lighten_color(color, 0.08)  # Subtle lightening
        hover_color_2 = color  # Original bottom
        
        return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {hover_color_1},
                stop:1 {hover_color_2});
            color: white;
            border: 2px solid {color};
            border-radius: 4px;
            font-weight: bold;
            font-size: {font_size};
            padding: {padding};
            min-height: {height};
            font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
        }}
        QPushButton:focus {{
            outline: none;
        }}
        """
    
    def _create_pressed_style(self, button: QtWidgets.QPushButton, color: str) -> str:
        """Create pressed button style using darker color"""
        config = self.button_configs.get(button.objectName(), {})
        size_class = config.get('size_class', 'normal')
        
        if size_class == 'small':
            height = "20px"
            font_size = "8pt"
            padding = "2px 6px"
        elif size_class == 'icon':
            height = "24px"
            font_size = "10pt"
            padding = "2px"
        else:
            height = "24px"
            font_size = "9pt"
            padding = "4px 8px"
        
        # Use darker color for pressed effect
        pressed_color = self._darken_color(color, 0.15)
        
        return f"""
        QPushButton {{
            background-color: {pressed_color};
            color: white;
            border: 2px solid {pressed_color};
            border-radius: 4px;
            font-weight: bold;
            font-size: {font_size};
            padding: {padding};
            min-height: {height};
            font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
        }}
        QPushButton:focus {{
            outline: none;
        }}
        """
    
    def cleanup(self):
        """Clean up references"""
        self.enhanced_buttons.clear()
        self.button_configs.clear()
        
        _LOGGER.info("Enhanced Dialog Button Manager cleaned up")
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by a factor (0.0 to 1.0)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darken a hex color by a factor (0.0 to 1.0)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"