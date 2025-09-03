"""
PySide6 Shortcuts Dialog for SNID SAGE GUI
==========================================

This module provides a PySide6 dialog to display keyboard shortcuts and hotkeys
available in the SNID SAGE GUI interface.
"""

import platform
import sys
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_shortcuts_dialog')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_shortcuts_dialog')

# Import platform configuration
from snid_sage.shared.utils.config.platform_config import get_platform_config


class PySide6ShortcutsDialog(QtWidgets.QDialog):
    """PySide6 dialog to display keyboard shortcuts"""
    
    def __init__(self, parent=None):
        """Initialize shortcuts dialog"""
        super().__init__(parent)
        self.is_mac = platform.system() == "Darwin"
        
        # Get platform-specific shortcuts
        try:
            from snid_sage.interfaces.gui.utils.cross_platform_window import CrossPlatformWindowManager
            self.shortcuts = CrossPlatformWindowManager.get_keyboard_shortcuts()
        except ImportError:
            self.shortcuts = self._get_default_shortcuts()
        
        self.setup_ui()
        # Ensure consistent cross-platform theming for table colors
        try:
            from snid_sage.interfaces.gui.utils.pyside6_theme_manager import apply_theme_to_widget
            apply_theme_to_widget(self)
        except Exception:
            pass
    
    def _get_default_shortcuts(self):
        """Get default shortcuts if cross-platform manager unavailable"""
        if self.is_mac:
            return {
                'quick_workflow': 'Cmd+Enter',
                'quit': 'Cmd+Q',
                'copy': 'Cmd+C',
                'paste': 'Cmd+V'
            }
        else:  # Windows/Linux
            return {
                'quick_workflow': 'Ctrl+Enter',
                'quit': 'Ctrl+Q',
                'copy': 'Ctrl+C',
                'paste': 'Ctrl+V'
            }
    
    def _get_platform_modifier(self):
        """Get the platform-specific modifier key text"""
        return "Cmd" if self.is_mac else "Ctrl"
    
    def _get_platform_alt(self):
        """Get the platform-specific alt key text"""
        return "Option" if self.is_mac else "Alt"
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("SNID SAGE - Keyboard Shortcuts")
        self.setMinimumSize(750, 550)
        self.resize(750, 550)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Create scrollable area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Create shortcuts tables
        self._create_shortcuts_tables(scroll_layout)
        
        # Add tips section
        self._create_tips_section(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Set window icon and properties
        self.setModal(False)  # Allow window to be non-modal
        
        # Enable escape key to close
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        _LOGGER.info("✅ PySide6 Shortcuts dialog opened")
    
    def _create_shortcuts_tables(self, layout):
        """Create table-style shortcuts display with improved formatting"""
        
        mod_key = self._get_platform_modifier()
        alt_key = self._get_platform_alt()
        
        # Define shortcuts data organized by category with OS-aware shortcuts
        shortcuts_data = [
            {
                "category": "🚀 QUICK WORKFLOW",
                "shortcuts": [
                    {"action": "Open Spectrum", "shortcut": f"{mod_key}+O", "description": "Load spectrum file"},
                    {"action": "Quick Analysis", "shortcut": f"{mod_key}+Enter", "description": "Preprocessing + Analysis"},
                     {"action": "Extended Quick Analysis", "shortcut": f"{mod_key}+Shift+Enter", "description": "Preprocessing + Analysis + Auto Cluster"},
                    {"action": "Reset Application", "shortcut": f"{mod_key}+Shift+R", "description": "Reset all analysis and plots"}
                ]
            },
            {
                "category": "⚙️ CONFIGURATION & ANALYSIS", 
                "shortcuts": [
                    {"action": "SNID Configuration", "shortcut": f"{mod_key}+Shift+O", "description": "Configure SNID parameters"},
                    {"action": "Run Analysis", "shortcut": "F5", "description": "Run SNID analysis"},
                    {"action": "Preprocessing", "shortcut": "F6", "description": "Open Preprocessing dialog"},
                    {"action": "Settings", "shortcut": f"{mod_key}+,", "description": "Open application settings"},
                    {"action": "Save Plot (PNG/JPG)", "shortcut": f"{mod_key}+S", "description": "Save the current plot as PNG/JPG"},
                    {"action": "Save Plot (SVG)", "shortcut": f"{mod_key}+Shift+S", "description": "Save the current plot as SVG"}
                ]
            },
            {
                "category": "🧭 TEMPLATE NAVIGATION",
                "shortcuts": [
                    {"action": "Previous Template", "shortcut": "← (Left Arrow)", "description": "Go to previous template"},
                    {"action": "Next Template", "shortcut": "→ (Right Arrow)", "description": "Go to next template"},
                    
                ]
            },
            {
                "category": "👁️ VIEW CONTROLS",
                "shortcuts": [
                    {"action": "Flux View", "shortcut": "F", "description": "Switch to Flux view"},
                    {"action": "Flat View", "shortcut": "T", "description": "Switch to Flat view"},
                    {"action": "Toggle View Mode", "shortcut": "Spacebar", "description": "Cycle between view modes"}
                ]
            },
            {
                "category": "🔬 ADVANCED FEATURES",
                "shortcuts": [
                    {"action": "Games", "shortcut": f"{mod_key}+G", "description": "Start entertainment games"}
                ]
            },
            {
                "category": "❓ HELP & APPLICATION",
                "shortcuts": [
                    {"action": "Show Shortcuts", "shortcut": "F1", "description": "Show this help dialog"},
                    {"action": "Show Shortcuts", "shortcut": f"{mod_key}+/", "description": "Alternative shortcut help"},
                    {"action": "Quit Application", "shortcut": f"{mod_key}+Q", "description": "Exit SNID SAGE"}
                ]
            }
        ]
        
        # Create tables for each category
        for category_data in shortcuts_data:
            self._create_category_table(layout, category_data)
    
    def _create_category_table(self, layout, category_data):
        """Create a table for a specific category of shortcuts"""
        
        # Category header
        category_label = QtWidgets.QLabel(category_data["category"])
        category_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2563eb;
                padding: 8px 0px 4px 0px;
                border-bottom: 2px solid #e5e7eb;
            }
        """)
        layout.addWidget(category_label)
        
        # Create table
        table = QtWidgets.QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Action", "Shortcut", "Description"])
        table.setRowCount(len(category_data["shortcuts"]))
        
        # Configure table appearance (no alternating row colors)
        table.setAlternatingRowColors(False)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        # Populate table
        for row, shortcut_info in enumerate(category_data["shortcuts"]):
            # Action column
            action_item = QtWidgets.QTableWidgetItem(shortcut_info["action"])
            action_item.setFont(QtGui.QFont(self._ui_font_family(), 10, QtGui.QFont.Weight.Bold))
            table.setItem(row, 0, action_item)
            
            # Shortcut column  
            shortcut_item = QtWidgets.QTableWidgetItem(shortcut_info["shortcut"])
            shortcut_item.setFont(QtGui.QFont(self._mono_font_family(), 10))
            shortcut_item.setBackground(QtGui.QColor(240, 248, 255))  # Light blue background
            table.setItem(row, 1, shortcut_item)
            
            # Description column
            desc_item = QtWidgets.QTableWidgetItem(shortcut_info["description"])
            table.setItem(row, 2, desc_item)
        
        # Set table height to fit contents
        table.resizeRowsToContents()
        table_height = table.verticalHeader().sectionSize(0) * table.rowCount() + table.horizontalHeader().height() + 10
        table.setMaximumHeight(table_height)
        table.setMinimumHeight(table_height)
        
        layout.addWidget(table)
    @staticmethod
    def _ui_font_family() -> str:
        if sys.platform == 'darwin':
            return 'Arial'
        if sys.platform == 'win32':
            return 'Segoe UI'
        return 'DejaVu Sans'

    @staticmethod
    def _mono_font_family() -> str:
        if sys.platform == 'win32':
            return 'Consolas'
        if sys.platform == 'darwin':
            return 'Menlo'
        return 'DejaVu Sans Mono'
    
    def _create_tips_section(self, layout):
        """Create tips section at the bottom"""
        tips_frame = QtWidgets.QFrame()
        tips_frame.setFrameShape(QtWidgets.QFrame.Box)
        tips_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        tips_layout = QtWidgets.QVBoxLayout(tips_frame)
        tips_layout.setContentsMargins(12, 12, 12, 12)
        
        mod_display = "Cmd" if self.is_mac else "Ctrl"
        tips_text = f"💡 TIPS: Start with {mod_display}+O to open a spectrum, then {mod_display}+Enter for quick analysis. Press Escape to close this dialog."
        
        tips_label = QtWidgets.QLabel(tips_text)
        tips_label.setWordWrap(True)
        tips_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-style: italic;
                color: #1e40af;
                background: transparent;
                border: none;
            }
        """)
        tips_layout.addWidget(tips_label)
        
        layout.addWidget(tips_frame)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event"""
        _LOGGER.debug("PySide6 Shortcuts dialog closed")
        super().closeEvent(event) 