"""
Flexible Number Input Widget for SNID SAGE GUI

This module provides a flexible alternative to QSpinBox/QDoubleSpinBox that allows
users to input numbers freely without restrictive formatting, decimal limitations,
or forced step increments.
"""

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
from typing import Optional, Union, Callable
import re


class FlexibleNumberInput(QtWidgets.QLineEdit):
    """
    A flexible number input widget that allows free-form numeric input
    without the restrictions of QSpinBox/QDoubleSpinBox.
    
    Features:
    - No forced decimal places
    - No step increments
    - Optional range validation
    - Scientific notation support
    - Customizable suffix
    - Real-time validation feedback
    """
    
    # Signal emitted when the value changes (similar to QSpinBox.valueChanged)
    valueChanged = QtCore.Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuration
        self._min_value: Optional[float] = None
        self._max_value: Optional[float] = None
        self._suffix: str = ""
        self._allow_empty: bool = True
        self._default_value: float = 0.0
        self._validator_callback: Optional[Callable[[float], bool]] = None
        self._max_decimals: int = 8
        # Mapping for special sentinel values -> display text (e.g., -9999 -> "No minimum")
        self._special_value_to_display: dict[float, str] = {}
        self._special_display_to_value: dict[str, float] = {}
        
        # State
        self._last_valid_value: Optional[float] = None
        self._is_valid: bool = True
        
        # Setup
        self._setup_widget()
        self._connect_signals()
    
    def _setup_widget(self):
        """Setup the widget appearance and behavior"""
        # Set placeholder text
        self.setPlaceholderText("Enter number...")
        
        # Set initial styling for valid state
        self._update_style(True)
        
        # Allow context menu for copy/paste
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
    
    def _connect_signals(self):
        """Connect internal signals"""
        self.textChanged.connect(self._on_text_changed)
        self.editingFinished.connect(self._on_editing_finished)
    
    def _update_style(self, is_valid: bool):
        """Update widget styling based on validation state"""
        if is_valid:
            self.setStyleSheet("")  # Use default styling
        else:
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #ef4444;
                    background-color: #fef2f2;
                }
            """)
    
    def _on_text_changed(self, text: str):
        """Handle text changes with real-time validation"""
        # Handle special display text (do not attempt numeric validation)
        if text in self._special_display_to_value:
            self._is_valid = True
            special_value = self._special_display_to_value[text]
            if self._last_valid_value != special_value:
                self._last_valid_value = special_value
                self.valueChanged.emit(special_value)
            self._update_style(True)
            return

        # Remove suffix for validation
        clean_text = text
        if self._suffix and text.endswith(self._suffix):
            clean_text = text[:-len(self._suffix)].strip()
        
        # Allow empty if configured
        if not clean_text and self._allow_empty:
            self._is_valid = True
            self._update_style(True)
            return
        
        # Validate numeric input
        is_valid, value = self._validate_number(clean_text)
        self._is_valid = is_valid
        self._update_style(is_valid)
        
        # Emit value changed signal if valid (rounded to configured decimals)
        if is_valid and value is not None:
            rounded_value = round(value, self._max_decimals)
            if self._last_valid_value != rounded_value:
                self._last_valid_value = rounded_value
                self.valueChanged.emit(rounded_value)
    
    def _on_editing_finished(self):
        """Handle when user finishes editing (focus lost or Enter pressed)"""
        if not self._is_valid and self._last_valid_value is not None:
            # Restore last valid value if current input is invalid
            self.setValue(self._last_valid_value)
        elif not self.text() and not self._allow_empty:
            # Set default value if empty and not allowed
            self.setValue(self._default_value)
        else:
            # Normalize display to configured decimal precision
            current_value = self.value()
            if current_value is not None:
                self.setValue(current_value)
    
    def _validate_number(self, text: str) -> tuple[bool, Optional[float]]:
        """
        Validate if text represents a valid number
        
        Returns:
            tuple: (is_valid, parsed_value)
        """
        if not text:
            return self._allow_empty, None
        
        try:
            # Handle scientific notation and regular numbers
            value = float(text)
            
            # Check range constraints
            if self._min_value is not None and value < self._min_value:
                return False, None
            
            if self._max_value is not None and value > self._max_value:
                return False, None
            
            # Check custom validator
            if self._validator_callback and not self._validator_callback(value):
                return False, None
            
            return True, value
            
        except ValueError:
            # Check if it's a partial valid input (like "1.", "1e", etc.)
            if self._is_partial_valid_number(text):
                return True, None  # Valid input but incomplete
            return False, None
    
    def _is_partial_valid_number(self, text: str) -> bool:
        """Check if text could be part of a valid number being typed"""
        # Patterns for partial numbers
        partial_patterns = [
            r'^[+-]?$',                    # Just sign
            r'^[+-]?\d+\.$',               # Number with trailing decimal
            r'^[+-]?\d*\.\d*$',            # Decimal number (possibly incomplete)
            r'^[+-]?\d+[eE]$',             # Number with E but no exponent
            r'^[+-]?\d+[eE][+-]?$',        # Number with E and sign but no exponent
            r'^[+-]?\d+[eE][+-]?\d*$',     # Scientific notation (possibly incomplete)
            r'^[+-]?\d*\.\d*[eE]$',        # Decimal with E but no exponent
            r'^[+-]?\d*\.\d*[eE][+-]?$',   # Decimal with E and sign but no exponent
            r'^[+-]?\d*\.\d*[eE][+-]?\d*$' # Decimal scientific notation (possibly incomplete)
        ]
        
        return any(re.match(pattern, text) for pattern in partial_patterns)
    
    # Public API methods
    
    def setRange(self, min_value: Optional[float], max_value: Optional[float]):
        """Set the valid range for input values"""
        self._min_value = min_value
        self._max_value = max_value
        
        # Update tooltip
        tooltip_parts = []
        if min_value is not None:
            tooltip_parts.append(f"Min: {min_value}")
        if max_value is not None:
            tooltip_parts.append(f"Max: {max_value}")
        
        if tooltip_parts:
            self.setToolTip(" | ".join(tooltip_parts))
    
    def setSuffix(self, suffix: str):
        """Set a suffix to display after the number"""
        self._suffix = suffix
        
        # Update current display if there's a value
        current_value = self.value()
        if current_value is not None:
            self._set_display_text(current_value)
    
    def setAllowEmpty(self, allow: bool):
        """Set whether empty input is allowed"""
        self._allow_empty = allow
        if not allow and not self.text():
            self.setValue(self._default_value)
    
    def setDefaultValue(self, value: float):
        """Set the default value used when input is empty"""
        self._default_value = value
    
    def setValidator(self, callback: Callable[[float], bool]):
        """Set a custom validation callback"""
        self._validator_callback = callback
    
    def setValue(self, value: Union[float, int, None]):
        """Set the current value"""
        if value is None:
            self.clear()
            self._last_valid_value = None
        else:
            float_value = round(float(value), self._max_decimals)
            self._last_valid_value = float_value
            # If value has a special display mapping, show that instead of numeric
            if float_value in self._special_value_to_display:
                display_text = self._special_value_to_display[float_value]
                self.blockSignals(True)
                self.setText(display_text)
                self.blockSignals(False)
            else:
                self._set_display_text(float_value)
            self._is_valid = True
            self._update_style(True)
    
    def value(self) -> Optional[float]:
        """Get the current numeric value"""
        text = self.text()
        # If current text matches a special display, return its mapped value
        if text in self._special_display_to_value:
            return self._special_display_to_value[text]
        
        # Remove suffix
        if self._suffix and text.endswith(self._suffix):
            text = text[:-len(self._suffix)].strip()
        
        if not text:
            return None if self._allow_empty else self._default_value
        
        try:
            return round(float(text), self._max_decimals)
        except ValueError:
            return self._last_valid_value
    
    def _set_display_text(self, value: float):
        """Set the display text for a given value"""
        # Handle special display mapping
        if value in self._special_value_to_display:
            text = self._special_value_to_display[value]
            self.blockSignals(True)
            self.setText(text)
            self.blockSignals(False)
            return
        # Format the number with max decimals, trimming trailing zeros
        text = self._format_number(value)
        
        # Add suffix if configured
        if self._suffix:
            text += self._suffix
        
        # Block signals to avoid recursive calls
        self.blockSignals(True)
        self.setText(text)
        self.blockSignals(False)

    def _format_number(self, value: float) -> str:
        """Format a float respecting max decimals and trimming trailing zeros."""
        # Use fixed-point formatting up to _max_decimals, then trim
        formatted = f"{round(float(value), self._max_decimals):.{self._max_decimals}f}"
        # Trim trailing zeros and possibly the dot
        if "." in formatted:
            formatted = formatted.rstrip("0").rstrip(".")
        return formatted
    
    def isValid(self) -> bool:
        """Check if current input is valid"""
        return self._is_valid
    
    def clear(self):
        """Clear the input"""
        super().clear()
        self._last_valid_value = None
        self._is_valid = True
        self._update_style(True)
    
    # Compatibility methods for QSpinBox/QDoubleSpinBox API
    def setSingleStep(self, step: float):
        """Compatibility method - does nothing since we don't use steps"""
        pass
    
    def singleStep(self) -> float:
        """Compatibility method - returns 1.0 as default"""
        return 1.0
    
    def setDecimals(self, decimals: int):
        """Set maximum number of decimals to display/emit."""
        try:
            decimals_int = int(decimals)
            if decimals_int < 0:
                decimals_int = 0
            self._max_decimals = decimals_int
            # Refresh display if there is a current value
            current_value = self.value()
            if current_value is not None:
                self.setValue(current_value)
        except Exception:
            # Ignore invalid inputs for safety
            pass
    
    def decimals(self) -> int:
        """Get current maximum number of decimals."""
        return self._max_decimals
    
    def setSpecialValueText(self, text: str):
        """Compatibility method - sets placeholder text"""
        self.setPlaceholderText(text)
    
    def specialValueText(self) -> str:
        """Compatibility method - returns placeholder text"""
        return self.placeholderText()

    # New API for special sentinel value display
    def setSpecialValueDisplay(self, value: float, display_text: str):
        """Map a sentinel numeric value to a special, human-friendly display text.

        When the control holds this value, the text will be set to the provided
        display_text (without suffix). When reading the value, if the current
        text equals display_text, the mapped numeric value will be returned.
        """
        try:
            numeric_value = round(float(value), self._max_decimals)
        except Exception:
            return
        self._special_value_to_display[numeric_value] = display_text
        self._special_display_to_value[display_text] = numeric_value
        # Refresh current display if this value is currently active
        current_value = self.value()
        if current_value is not None and round(float(current_value), self._max_decimals) == numeric_value:
            self.setValue(numeric_value)


class FlexibleNumberInputWithButtons(QtWidgets.QWidget):
    """
    A flexible number input with optional increment/decrement buttons
    Similar to QSpinBox but without restrictive formatting
    """
    
    valueChanged = QtCore.Signal(float)
    
    def __init__(self, parent=None, show_buttons: bool = True):
        super().__init__(parent)
        
        self._show_buttons = show_buttons
        self._step_value = 1.0
        
        self._setup_layout()
        self._connect_signals()
    
    def _setup_layout(self):
        """Setup the widget layout"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main number input
        self.number_input = FlexibleNumberInput()
        layout.addWidget(self.number_input)
        
        if self._show_buttons:
            # Button container
            button_container = QtWidgets.QWidget()
            button_layout = QtWidgets.QVBoxLayout(button_container)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(0)
            
            # Up button
            self.up_button = QtWidgets.QPushButton("▲")
            self.up_button.setMaximumSize(20, 15)
            self.up_button.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ccc;
                    background: #f0f0f0;
                    font-size: 8px;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                }
                QPushButton:pressed {
                    background: #d0d0d0;
                }
            """)
            
            # Down button
            self.down_button = QtWidgets.QPushButton("▼")
            self.down_button.setMaximumSize(20, 15)
            self.down_button.setStyleSheet(self.up_button.styleSheet())
            
            button_layout.addWidget(self.up_button)
            button_layout.addWidget(self.down_button)
            
            layout.addWidget(button_container)
    
    def _connect_signals(self):
        """Connect signals"""
        self.number_input.valueChanged.connect(self.valueChanged.emit)
        
        if self._show_buttons:
            self.up_button.clicked.connect(self._increment)
            self.down_button.clicked.connect(self._decrement)
    
    def _increment(self):
        """Increment the value"""
        current = self.value() or 0
        self.setValue(current + self._step_value)
    
    def _decrement(self):
        """Decrement the value"""
        current = self.value() or 0
        self.setValue(current - self._step_value)
    
    def setSingleStep(self, step: float):
        """Set the step value for increment/decrement buttons"""
        self._step_value = step
    
    # Delegate methods to the number input
    def setRange(self, min_value: Optional[float], max_value: Optional[float]):
        self.number_input.setRange(min_value, max_value)
    
    def setSuffix(self, suffix: str):
        self.number_input.setSuffix(suffix)
    
    def setAllowEmpty(self, allow: bool):
        self.number_input.setAllowEmpty(allow)
    
    def setDefaultValue(self, value: float):
        self.number_input.setDefaultValue(value)
    
    def setValidator(self, callback: Callable[[float], bool]):
        self.number_input.setValidator(callback)
    
    def setValue(self, value: Union[float, int, None]):
        self.number_input.setValue(value)
    
    def value(self) -> Optional[float]:
        return self.number_input.value()
    
    def isValid(self) -> bool:
        return self.number_input.isValid()
    
    def clear(self):
        self.number_input.clear()
    
    def setToolTip(self, tooltip: str):
        self.number_input.setToolTip(tooltip)
    
    # Compatibility methods for QSpinBox/QDoubleSpinBox API
    def setSingleStep(self, step: float):
        """Set the step value for increment/decrement buttons"""
        self._step_value = step
        self.number_input.setSingleStep(step)  # Pass through to underlying widget
    
    def singleStep(self) -> float:
        """Get the step value"""
        return self._step_value
    
    def setDecimals(self, decimals: int):
        """Compatibility method - pass through to number input"""
        self.number_input.setDecimals(decimals)
    
    def decimals(self) -> int:
        """Compatibility method - pass through to number input"""
        return self.number_input.decimals()
    
    def setSpecialValueText(self, text: str):
        """Compatibility method - pass through to number input"""
        self.number_input.setSpecialValueText(text)
    
    def specialValueText(self) -> str:
        """Compatibility method - pass through to number input"""
        return self.number_input.specialValueText()

    def setSpecialValueDisplay(self, value: float, display_text: str):
        """Pass-through mapping for special sentinel display."""
        # Ensure underlying number input supports the method
        if hasattr(self.number_input, 'setSpecialValueDisplay'):
            self.number_input.setSpecialValueDisplay(value, display_text)


# Convenience functions for easy replacement
def create_flexible_double_input(min_val=None, max_val=None, suffix="", default=0.0, show_buttons=False):
    """Create a flexible double input to replace QDoubleSpinBox"""
    widget = FlexibleNumberInputWithButtons(show_buttons=show_buttons) if show_buttons else FlexibleNumberInput()
    
    if min_val is not None or max_val is not None:
        widget.setRange(min_val, max_val)
    
    if suffix:
        widget.setSuffix(suffix)
    
    widget.setDefaultValue(default)
    widget.setAllowEmpty(False)
    
    return widget


def create_flexible_int_input(min_val=None, max_val=None, suffix="", default=0, show_buttons=False):
    """Create a flexible integer input to replace QSpinBox"""
    widget = FlexibleNumberInputWithButtons(show_buttons=show_buttons) if show_buttons else FlexibleNumberInput()
    
    if min_val is not None or max_val is not None:
        widget.setRange(min_val, max_val)
    
    if suffix:
        widget.setSuffix(suffix)
    
    widget.setDefaultValue(float(default))
    widget.setAllowEmpty(False)
    
    # Add integer validation
    def integer_validator(value):
        return value == int(value)
    
    widget.setValidator(integer_validator)
    
    return widget