"""
SNID SAGE - Progress Dialog - PySide6 Version
=============================================

Simple progress dialog for showing analysis progress.
"""

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
from typing import Optional

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_progress')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_progress')

# Enhanced dialog button styling
try:
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
    ENHANCED_BUTTONS_AVAILABLE = True
except Exception:
    ENHANCED_BUTTONS_AVAILABLE = False

class PySide6ProgressDialog(QtWidgets.QDialog):
    """
    Progress dialog for showing analysis progress.
    
    Features:
    - Indeterminate progress bar
    - Status text updates
    - Cancel button
    - Modern styling
    """
    
    # Signal emitted when cancel is requested
    cancel_requested = QtCore.Signal()
    
    def __init__(self, parent, title="Analysis Progress", initial_message="Starting analysis..."):
        """
        Initialize progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            initial_message: Initial status message
        """
        super().__init__(parent)
        self.title = title
        self.cancelled = False
        
        self._setup_dialog()
        self._create_interface(initial_message)
        
    def _setup_dialog(self):
        """Setup dialog properties"""
        self.setWindowTitle(self.title)
        self.setFixedSize(400, 150)
        self.setModal(True)
        
        # Remove window close button and make it non-resizable
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
                color: #1e293b;
                font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
            }
            
            QLabel {
                color: #1e293b;
                font-size: 11pt;
                background: transparent;
            }
            
            QProgressBar {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                text-align: center;
                font-size: 10pt;
                font-weight: bold;
                background: #ffffff;
                min-height: 20px;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 4px;
            }
            
            QPushButton {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                background: #ffffff;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background: #f1f5f9;
                border: 2px solid #ef4444;
            }
            
            QPushButton:pressed {
                background: #e2e8f0;
            }
        """)
    
    def _create_interface(self, initial_message: str):
        """Create the dialog interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Status label
        self.status_label = QtWidgets.QLabel(initial_message)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Progress bar (indeterminate)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Apply enhanced styles
        try:
            if ENHANCED_BUTTONS_AVAILABLE:
                self.button_manager = enhance_dialog_with_preset(self, 'progress_dialog')
        except Exception as e:
            _LOGGER.warning(f"Failed to apply enhanced button styling: {e}")
    
    def update_status(self, message: str):
        """Update the status message"""
        try:
            self.status_label.setText(message)
            QtWidgets.QApplication.processEvents()  # Update UI immediately
        except Exception as e:
            _LOGGER.warning(f"Error updating progress status: {e}")
    
    def set_progress(self, value: int, maximum: int = 100):
        """
        Set determinate progress.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        try:
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(value)
            QtWidgets.QApplication.processEvents()
        except Exception as e:
            _LOGGER.warning(f"Error setting progress: {e}")
    
    def set_indeterminate(self):
        """Set progress bar to indeterminate mode"""
        try:
            self.progress_bar.setRange(0, 0)
            QtWidgets.QApplication.processEvents()
        except Exception as e:
            _LOGGER.warning(f"Error setting indeterminate progress: {e}")
    
    def _on_cancel(self):
        """Handle cancel button click"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Cancel Analysis",
            "Are you sure you want to cancel the analysis?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.cancelled = True
            self.cancel_requested.emit()
            self.update_status("Cancelling analysis...")
            self.cancel_btn.setEnabled(False)
    
    def is_cancelled(self) -> bool:
        """Check if analysis was cancelled"""
        return self.cancelled
    
    def close_dialog(self):
        """Close the dialog"""
        try:
            self.accept()
        except Exception as e:
            _LOGGER.warning(f"Error closing progress dialog: {e}")


def show_progress_dialog(parent, title="Analysis Progress", message="Starting analysis...") -> PySide6ProgressDialog:
    """
    Show progress dialog and return the dialog instance.
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Initial message
        
    Returns:
        Progress dialog instance
    """
    dialog = PySide6ProgressDialog(parent, title, message)
    dialog.show()
    return dialog 