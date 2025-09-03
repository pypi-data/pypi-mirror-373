"""
Redshift Mode Selection Dialog - PySide6 Version

This dialog appears after a user accepts a redshift in the manual redshift dialog,
giving them options for how to use that redshift in the SNID analysis.
"""

import sys
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
from typing import Optional, Dict, Any

# Import flexible number input widget
from snid_sage.interfaces.gui.components.widgets.flexible_number_input import FlexibleNumberInput

# Import enhanced button support
try:
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
    ENHANCED_BUTTONS_AVAILABLE = True
except ImportError:
    ENHANCED_BUTTONS_AVAILABLE = False

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_redshift_mode')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_redshift_mode')


class PySide6RedshiftModeDialog(QtWidgets.QDialog):
    """Dialog for selecting redshift analysis mode - PySide6 version"""
    
    def __init__(self, parent, redshift_value: float):
        super().__init__(parent)
        self.redshift_value = redshift_value
        self.result = None
        
        # Unified color scheme matching other dialogs
        self.colors = {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#f1f5f9',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'border': '#e2e8f0',
            'accent_primary': '#3b82f6',
            'btn_success': '#22c55e',
            'btn_secondary': '#64748b'
        }
        
        self._setup_dialog()
        self._create_interface()
        
        # Setup enhanced buttons
        self._setup_enhanced_buttons()
        
        # Center the dialog properly on parent
        if parent:
            self._center_on_parent()
    
    def _center_on_parent(self):
        """Center the dialog on the parent window"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            dialog_size = self.size()
            
            # Calculate center position relative to parent
            x = parent_geometry.x() + (parent_geometry.width() - dialog_size.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_size.height()) // 2
            
            # Get screen geometry to ensure dialog stays visible
            screen = QtWidgets.QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                
                # Ensure dialog stays within screen bounds with margins
                margin = 50
                x = max(margin, min(x, screen_geometry.width() - dialog_size.width() - margin))
                y = max(margin, min(y, screen_geometry.height() - dialog_size.height() - margin))
                
                # Additional check to prevent dialog from being too high
                if y < margin:
                    y = margin
                
                self.move(x, y)
                _LOGGER.debug(f"Positioned dialog at ({x}, {y}) within screen bounds")
            else:
                # Fallback if no screen info available
                self.move(x, y)
        else:
            # Center on screen if no parent
            screen = QtWidgets.QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                dialog_size = self.size()
                
                x = (screen_geometry.width() - dialog_size.width()) // 2
                y = (screen_geometry.height() - dialog_size.height()) // 2
                
                self.move(x, y)
    
    def showEvent(self, event):
        """Override showEvent to ensure proper positioning"""
        super().showEvent(event)
        # Re-center when actually shown to account for final size
        QtCore.QTimer.singleShot(0, self._center_on_parent)
    
    def _setup_dialog(self):
        """Setup dialog window properties"""
        self.setWindowTitle("Redshift Analysis Mode")
        self.setFixedSize(500, 450)  # Smaller, simpler size
        self.setModal(True)
        
        # Apply theme manager styles and minimal custom styling for QLineEdit
        from snid_sage.interfaces.gui.utils.pyside6_theme_manager import apply_theme_to_widget
        apply_theme_to_widget(self)
        
        # Add minimal custom styling for QLineEdit focus states
        self.setStyleSheet(self.styleSheet() + f"""
            QLineEdit:focus {{
                border-color: {self.colors['accent_primary']};
                background: white;
            }}
            
            QLabel {{
                background: transparent;
            }}
            
            QFrame {{
                background: transparent;
            }}
        """)
    
    def _create_interface(self):
        """Create the dialog interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        self._create_header(layout)
        
        # Mode options
        self._create_mode_options(layout)
        
        # Buttons
        self._create_buttons(layout)
    
    def _create_header(self, layout):
        """Create header section"""
        # Show current redshift value
        redshift_info = QtWidgets.QLabel(f"Selected Redshift: z = {self.redshift_value:.6f}")
        redshift_info.setFont(QtGui.QFont(self._ui_font_family(), 11, QtGui.QFont.Weight.Bold))
        redshift_info.setAlignment(QtCore.Qt.AlignCenter)
        redshift_info.setStyleSheet(f"""
            background: {self.colors['bg_secondary']};
            border: 2px solid {self.colors['accent_primary']};
            border-radius: 6px;
            padding: 4px 8px;
            color: {self.colors['accent_primary']};
        """)
        layout.addWidget(redshift_info)
    
    def _create_mode_options(self, layout):
        """Create mode selection options"""
        options_group = QtWidgets.QGroupBox("Analysis Options")
        options_layout = QtWidgets.QVBoxLayout(options_group)
        options_layout.setSpacing(12)
        
        # Create button group for exclusive selection
        self.mode_group = QtWidgets.QButtonGroup(self)
        
        # Fixed redshift option
        self.fixed_radio = QtWidgets.QRadioButton("Force Exact Redshift")
        self.fixed_radio.setChecked(True)  # Default selection
        self.mode_group.addButton(self.fixed_radio, 0)
        options_layout.addWidget(self.fixed_radio)
        
        fixed_desc = QtWidgets.QLabel(
            f"Use exactly z = {self.redshift_value:.6f} for all template matching.\n"
            "Faster analysis with precise redshift constraint."
        )
        fixed_desc.setFont(QtGui.QFont(self._ui_font_family(), 9))
        fixed_desc.setStyleSheet(f"color: {self.colors['text_secondary']}; margin-left: 20px; margin-bottom: 8px;")
        fixed_desc.setWordWrap(True)
        options_layout.addWidget(fixed_desc)
        
        # Search around redshift option
        self.search_radio = QtWidgets.QRadioButton("Search Around Redshift")
        self.mode_group.addButton(self.search_radio, 1)
        options_layout.addWidget(self.search_radio)
        
        search_desc = QtWidgets.QLabel(
            f"Search for optimal redshift near z = {self.redshift_value:.6f}.\n"
            "Standard SNID analysis with initial guess (recommended)."
        )
        search_desc.setFont(QtGui.QFont(self._ui_font_family(), 9))
        search_desc.setStyleSheet(f"color: {self.colors['text_secondary']}; margin-left: 20px;")
        search_desc.setWordWrap(True)
        options_layout.addWidget(search_desc)
        
        # Search range input
        range_layout = QtWidgets.QHBoxLayout()
        range_layout.setContentsMargins(20, 8, 0, 0)
        
        range_label = QtWidgets.QLabel("Search Range: ±")
        range_label.setFont(QtGui.QFont(self._ui_font_family(), 9, QtGui.QFont.Weight.Bold))
        range_layout.addWidget(range_label)
        
        self.range_input = FlexibleNumberInput()
        self.range_input.setValue(0.0005)
        self.range_input.setRange(0.0, 1.0)
        self.range_input.setMaximumWidth(80)
        self.range_input.setFont(QtGui.QFont(self._ui_font_family(), 9))
        self.range_input.setToolTip("Search range around redshift (any precision)")
        range_layout.addWidget(self.range_input)
        
        # Live hint showing the actual redshift interval that will be searched
        self.range_help = QtWidgets.QLabel("")
        self.range_help.setFont(QtGui.QFont(self._ui_font_family(), 8))
        self.range_help.setStyleSheet(f"color: {self.colors['text_secondary']};")
        range_layout.addWidget(self.range_help)

        # Update the hint initially and whenever the value changes
        def _update_range_help_label():
            value = self.range_input.value() or 0.0
            zmin = max(0.0, self.redshift_value - value)
            zmax = self.redshift_value + value
            self.range_help.setText(f"Will search z in [{zmin:.6f}, {zmax:.6f}]")

        _update_range_help_label()
        # Connect both text and value changes to be robust to partial edits
        if hasattr(self.range_input, 'valueChanged'):
            self.range_input.valueChanged.connect(lambda _v: _update_range_help_label())
        if hasattr(self.range_input, 'textChanged'):
            self.range_input.textChanged.connect(lambda _t: _update_range_help_label())
        
        range_layout.addStretch()
        options_layout.addLayout(range_layout)
        
        layout.addWidget(options_group)
    
    def _create_buttons(self, layout):
        """Create dialog buttons"""
        # Add some spacing before buttons
        layout.addSpacing(8)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.setFont(QtGui.QFont(self._ui_font_family(), 10, QtGui.QFont.Weight.Bold))
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        # Apply button
        self.apply_btn = QtWidgets.QPushButton("Continue Analysis")
        self.apply_btn.setObjectName("primary_btn")
        self.apply_btn.setMinimumWidth(140)
        self.apply_btn.setFont(QtGui.QFont(self._ui_font_family(), 10, QtGui.QFont.Weight.Bold))
        self.apply_btn.clicked.connect(self._on_apply)
        self.apply_btn.setDefault(True)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_enhanced_buttons(self):
        """Setup enhanced button styling and animations"""
        if not ENHANCED_BUTTONS_AVAILABLE:
            _LOGGER.info("Enhanced buttons not available, using standard styling")
            return

        try:
            # Use the redshift_mode_dialog preset
            self.button_manager = enhance_dialog_with_preset(
                self, 'redshift_mode_dialog'
            )
            _LOGGER.info("Enhanced buttons successfully applied to redshift mode dialog")

        except Exception as e:
            _LOGGER.error(f"Failed to setup enhanced buttons: {e}")
    
    def _on_apply(self):
        """Handle apply button"""
        try:
            if self.fixed_radio.isChecked():
                self.result = {
                    'redshift': self.redshift_value,
                    'mode': 'force',
                    'forced_redshift': self.redshift_value,
                    'description': f'Forced redshift z = {self.redshift_value:.6f}'
                }
                _LOGGER.debug(f"Forced redshift mode selected: z = {self.redshift_value:.6f}")
                
            elif self.search_radio.isChecked():
                search_range = self.range_input.value()
                if search_range is None or search_range <= 0:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Invalid Range",
                        "Please enter a valid positive number for the search range."
                    )
                    return
                
                self.result = {
                    'redshift': self.redshift_value,
                    'mode': 'search',
                    'forced_redshift': None,
                    'search_range': search_range,
                    'min_redshift': max(0.0, self.redshift_value - search_range),
                    'max_redshift': self.redshift_value + search_range,
                    'description': f'Search around z = {self.redshift_value:.6f} ± {search_range:.6f}'
                }
                _LOGGER.debug(f"Search mode selected: z = {self.redshift_value:.6f} ± {search_range:.6f}")
            
            self.accept()
            
        except Exception as e:
            _LOGGER.error(f"Error in redshift mode selection: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error processing redshift mode selection:\n{e}"
            )
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the result redshift mode configuration"""
        return self.result

    @staticmethod
    def _ui_font_family() -> str:
        """Return a UI font family that exists on the current platform."""
        if sys.platform == 'darwin':
            return 'Arial'
        if sys.platform == 'win32':
            return 'Segoe UI'
        # Linux and others: pick commonly available sans
        return 'DejaVu Sans'


def show_redshift_mode_dialog(parent, redshift_value: float) -> Optional[Dict[str, Any]]:
    """
    Show redshift mode dialog and return the configuration.
    
    Args:
        parent: Parent window
        redshift_value: The redshift value to configure
        
    Returns:
        Dictionary with mode configuration or None if cancelled
    """
    dialog = PySide6RedshiftModeDialog(parent, redshift_value)
    result = dialog.exec()
    
    if result == QtWidgets.QDialog.Accepted:
        return dialog.get_result()
    else:
        return None 