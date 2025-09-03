"""
SNID SAGE - Preprocessing Selection Dialog - PySide6 Version
==========================================================

Simple dialog to choose between quick and advanced preprocessing options.
Uses radio button style similar to redshift selection dialog.
"""

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_preprocessing_selection')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_preprocessing_selection')

# Enhanced dialog button styling
try:
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
    ENHANCED_BUTTONS_AVAILABLE = True
except Exception:
    ENHANCED_BUTTONS_AVAILABLE = False

class PySide6PreprocessingSelectionDialog(QtWidgets.QDialog):
    """Dialog for selecting preprocessing mode - PySide6 version"""
    
    def __init__(self, parent):
        """
        Initialize preprocessing selection dialog
        
        Parameters:
        -----------
        parent : QWidget
            Reference to the main GUI instance
        """
        super().__init__(parent)
        self.parent_gui = parent
        self.result = None
        
        # Color scheme matching other dialogs
        self.colors = {
            'bg': '#f8fafc',
            'panel_bg': '#ffffff',
            'primary': '#3b82f6',
            'success': '#22c55e',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'border': '#e2e8f0',
            'hover': '#f1f5f9'
        }
        
        # Override all text-related colours to black for a consistent monochrome look
        for key in ['primary', 'success', 'warning', 'danger', 'text_primary', 'text_secondary']:
            self.colors[key] = 'black'
        
        self._setup_dialog()
        self._create_interface()
    
    def _setup_dialog(self):
        """Setup dialog window properties"""
        self.setWindowTitle("Preprocess Spectrum")
        self.resize(600, 480)
        self.setFixedSize(600, 480)  # Non-resizable to match original
        
        # Apply dialog styling (do not override global indicator styling)
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.colors['bg']};
                color: {self.colors['text_primary']};
                font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                background: {self.colors['panel_bg']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {self.colors['text_primary']};
            }}
            
            QRadioButton {{
                font-size: 11pt;
                font-weight: bold;
                spacing: 8px;
                color: {self.colors['text_primary']};
            }}
            
            /* Radio indicators inherit from theme manager to keep emission style */
            
            QPushButton {{
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 24px;
                font-weight: bold;
                font-size: 10pt;
                background: {self.colors['panel_bg']};
            }}
            
            QPushButton:hover {{
                background: {self.colors['hover']};
            }}
            
            QPushButton#primary_btn {{
                background: {self.colors['success']};
                color: white;
                border: 2px solid {self.colors['success']};
            }}
            
            QPushButton#primary_btn:hover {{
                background: #16a34a;
                border: 2px solid #16a34a;
            }}
            
            QPushButton#cancel_btn {{
                background: {self.colors['text_secondary']};
                color: white;
                border: 2px solid {self.colors['text_secondary']};
            }}
            
            QPushButton#cancel_btn:hover {{
                background: #334155;
                border: 2px solid #334155;
            }}
            
            QLabel {{
                background: transparent;
                color: {self.colors['text_primary']};
            }}
        """)
    
    def _create_interface(self):
        """Create the dialog interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self._create_header(layout)
        
        # Mode options
        self._create_mode_options(layout)
        
        # Buttons
        self._create_buttons(layout)
    
    def _create_header(self, layout):
        """Create header section"""
        header_label = QtWidgets.QLabel("Choose Preprocessing Mode")
        header_label.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(header_label)
        
        desc_label = QtWidgets.QLabel(
            "Select how you want to preprocess your spectrum before SNID analysis"
        )
        desc_label.setFont(QtGui.QFont("Segoe UI", 11))
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        desc_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        layout.addWidget(desc_label)
    
    def _create_mode_options(self, layout):
        """Create mode selection options"""
        options_group = QtWidgets.QGroupBox("Preprocessing Options")
        options_layout = QtWidgets.QVBoxLayout(options_group)
        options_layout.setSpacing(15)
        
        # Create button group for exclusive selection
        self.mode_group = QtWidgets.QButtonGroup(self)
        
        # Quick preprocessing option
        quick_frame = QtWidgets.QFrame()
        quick_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['panel_bg']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame:hover {{
                border: 2px solid {self.colors['primary']};
            }}
        """)
        
        quick_layout = QtWidgets.QVBoxLayout(quick_frame)
        quick_layout.setSpacing(8)
        
        self.quick_radio = QtWidgets.QRadioButton("Quick Preprocessing (Recommended)")
        self.quick_radio.setChecked(True)  # Default selection
        self.mode_group.addButton(self.quick_radio, 0)
        quick_layout.addWidget(self.quick_radio)
        
        quick_desc = QtWidgets.QLabel(
            "• Automatic parameter selection\n"
            "• Standard clipping and filtering\n"
            "• Optimized for most spectra\n"
            "• Fast processing (~5 seconds)"
        )
        quick_desc.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 10pt; margin-left: 26px;")
        quick_layout.addWidget(quick_desc)
        
        options_layout.addWidget(quick_frame)
        
        # Advanced preprocessing option
        advanced_frame = QtWidgets.QFrame()
        advanced_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['panel_bg']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame:hover {{
                border: 2px solid {self.colors['primary']};
            }}
        """)
        
        advanced_layout = QtWidgets.QVBoxLayout(advanced_frame)
        advanced_layout.setSpacing(8)
        
        self.advanced_radio = QtWidgets.QRadioButton("Advanced Preprocessing")
        self.mode_group.addButton(self.advanced_radio, 1)
        advanced_layout.addWidget(self.advanced_radio)
        
        advanced_desc = QtWidgets.QLabel(
            "• Interactive parameter configuration\n"
            "• Custom clipping and masking\n"
            "• Real-time preview\n"
            "• Full control over processing steps"
        )
        advanced_desc.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 10pt; margin-left: 26px;")
        advanced_layout.addWidget(advanced_desc)
        
        options_layout.addWidget(advanced_frame)
        
        layout.addWidget(options_group)
        
        
        notice_label = QtWidgets.QLabel(
            "💡 Tip: Quick preprocessing works well for most astronomical spectra. "
            "Use advanced mode only if you need specific parameter control."
        )
        notice_label.setWordWrap(True)
        notice_label.setStyleSheet(f"""
            color: {self.colors['text_secondary']};
            font-style: italic;
            font-size: 10pt;
            padding: 8px;
            background: {self.colors['hover']};
            border-radius: 4px;
        """)
        layout.addWidget(notice_label)
    
    def _create_buttons(self, layout):
        """Create dialog buttons"""
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        # Apply button
        self.apply_btn = QtWidgets.QPushButton("Proceed with Preprocessing")
        self.apply_btn.setObjectName("primary_btn")
        self.apply_btn.clicked.connect(self._on_apply)
        self.apply_btn.setDefault(True)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)

        # Apply enhanced styles
        try:
            if ENHANCED_BUTTONS_AVAILABLE:
                self.button_manager = enhance_dialog_with_preset(self, 'preprocessing_selection_dialog')
        except Exception as e:
            _LOGGER.warning(f"Failed to apply enhanced button styling: {e}")
    
    def _on_apply(self):
        """Handle apply button"""
        if self.quick_radio.isChecked():
            self.result = 'quick'
            _LOGGER.debug("Quick preprocessing mode selected")
        else:
            self.result = 'advanced'
            _LOGGER.debug("Advanced preprocessing mode selected")
        
        self.accept()
    
    def get_result(self):
        """Get the selected preprocessing mode"""
        return self.result


def show_preprocessing_selection_dialog(parent):
    """
    Show preprocessing selection dialog and return the selected mode.
    
    Args:
        parent: Parent window
        
    Returns:
        'quick', 'advanced', or None if cancelled
    """
    dialog = PySide6PreprocessingSelectionDialog(parent)
    result = dialog.exec()
    
    if result == QtWidgets.QDialog.Accepted:
        return dialog.get_result()
    else:
        return None 