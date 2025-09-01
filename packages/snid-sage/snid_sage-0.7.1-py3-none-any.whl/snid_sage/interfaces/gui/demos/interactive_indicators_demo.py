"""
Interactive Indicators Demo
===========================

This demo shows the enhanced checkbox and radio button indicators:
- Traditional square checkboxes with nice tick marks
- Traditional circular radio buttons with nice dots
- Interactive hover effects on the indicators only
- Enhanced visual styling while keeping text areas unchanged

Usage: python snid_sage/interfaces/gui/demos/interactive_indicators_demo.py
"""

import sys
from PySide6 import QtCore, QtGui, QtWidgets

# Import the theme manager
from snid_sage.interfaces.gui.utils.pyside6_theme_manager import get_pyside6_theme_manager


class InteractiveIndicatorsDemo(QtWidgets.QMainWindow):
    """Demo showing enhanced checkbox and radio button indicators"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SNID SAGE - Interactive Indicators Demo")
        self.resize(700, 600)
        
        # Apply the complete theme with enhanced indicators
        theme_manager = get_pyside6_theme_manager()
        self.setStyleSheet(theme_manager.generate_complete_stylesheet())
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the demo user interface"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QtWidgets.QLabel("Interactive Indicators Demo")
        title.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QtWidgets.QLabel(
            "These controls keep the traditional square/circle appearance but have enhanced indicators.\n"
            "Notice the hover effects on the checkboxes and radio buttons - only the indicators change,\n"
            "not the text areas. The tick marks and dots are also more visually appealing."
        )
        desc.setWordWrap(True)
        desc.setAlignment(QtCore.Qt.AlignCenter)
        desc.setStyleSheet("color: #64748b; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Checkbox section
        checkbox_group = QtWidgets.QGroupBox("Enhanced Checkboxes")
        checkbox_layout = QtWidgets.QVBoxLayout(checkbox_group)
        
        # Regular checkboxes
        self.checkbox1 = QtWidgets.QCheckBox("Enable feature A (hover over the square!)")
        self.checkbox1.setChecked(True)
        checkbox_layout.addWidget(self.checkbox1)
        
        self.checkbox2 = QtWidgets.QCheckBox("Auto-save documents")
        checkbox_layout.addWidget(self.checkbox2)
        
        self.checkbox3 = QtWidgets.QCheckBox("Show advanced options")
        self.checkbox3.setChecked(True)
        checkbox_layout.addWidget(self.checkbox3)
        
        # Accent color checkboxes using emission-style indicators
        self.checkbox_success = QtWidgets.QCheckBox("Success style checkbox (green indicator)")
        self.checkbox_success.setProperty("accent", "success")
        self.checkbox_success.setChecked(True)
        checkbox_layout.addWidget(self.checkbox_success)
        
        self.checkbox_warning = QtWidgets.QCheckBox("Warning style checkbox (orange indicator)")
        self.checkbox_warning.setProperty("accent", "warning")
        checkbox_layout.addWidget(self.checkbox_warning)
        
        self.checkbox_danger = QtWidgets.QCheckBox("Danger style checkbox (red indicator)")
        self.checkbox_danger.setProperty("accent", "danger")
        checkbox_layout.addWidget(self.checkbox_danger)
        
        layout.addWidget(checkbox_group)
        
        # Radio button section
        radio_group = QtWidgets.QGroupBox("Enhanced Radio Buttons")
        radio_layout = QtWidgets.QVBoxLayout(radio_group)
        
        # Create radio buttons
        self.radio1 = QtWidgets.QRadioButton("Option 1 (hover over the circle!)")
        self.radio1.setChecked(True)
        radio_layout.addWidget(self.radio1)
        
        self.radio2 = QtWidgets.QRadioButton("Option 2")
        radio_layout.addWidget(self.radio2)
        
        self.radio3 = QtWidgets.QRadioButton("Option 3")
        radio_layout.addWidget(self.radio3)
        
        # Button group for exclusive selection
        self.radio_button_group = QtWidgets.QButtonGroup(self)
        self.radio_button_group.addButton(self.radio1, 0)
        self.radio_button_group.addButton(self.radio2, 1)
        self.radio_button_group.addButton(self.radio3, 2)
        
        # Accent color radio buttons using emission-style indicators
        radio_accent_group = QtWidgets.QGroupBox("Accent Color Radio Buttons")
        radio_accent_layout = QtWidgets.QVBoxLayout(radio_accent_group)
        
        self.radio_success = QtWidgets.QRadioButton("Success style radio button (green indicator)")
        self.radio_success.setProperty("accent", "success")
        radio_accent_layout.addWidget(self.radio_success)
        
        self.radio_warning = QtWidgets.QRadioButton("Warning style radio button (orange indicator)")
        self.radio_warning.setProperty("accent", "warning")
        self.radio_warning.setChecked(True)
        radio_accent_layout.addWidget(self.radio_warning)
        
        self.radio_danger = QtWidgets.QRadioButton("Danger style radio button (red indicator)")
        self.radio_danger.setProperty("accent", "danger")
        radio_accent_layout.addWidget(self.radio_danger)
        
        # Button group for accent radios
        self.accent_radio_group = QtWidgets.QButtonGroup(self)
        self.accent_radio_group.addButton(self.radio_success, 0)
        self.accent_radio_group.addButton(self.radio_warning, 1)
        self.accent_radio_group.addButton(self.radio_danger, 2)
        
        layout.addWidget(radio_accent_group)
        
        layout.addWidget(radio_group)
        
        # Status display
        self.status_label = QtWidgets.QLabel("Hover over the checkboxes and radio buttons to see the enhanced indicators!")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #3b82f6; font-weight: bold; padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px; background: #f8fafc;")
        layout.addWidget(self.status_label)
        
        # Connect signals to show interaction
        self._connect_signals()
        
        layout.addStretch()
        
    def _connect_signals(self):
        """Connect signals to demonstrate interactivity"""
        # Checkbox signals
        self.checkbox1.toggled.connect(lambda checked: self._update_status("Feature A", checked))
        self.checkbox2.toggled.connect(lambda checked: self._update_status("Auto-save", checked))
        self.checkbox3.toggled.connect(lambda checked: self._update_status("Advanced options", checked))
        
        # Radio button signals
        self.radio1.toggled.connect(lambda checked: self._update_status("Option 1", checked))
        self.radio2.toggled.connect(lambda checked: self._update_status("Option 2", checked))
        self.radio3.toggled.connect(lambda checked: self._update_status("Option 3", checked))
    
    def _update_status(self, control_name: str, checked: bool):
        """Update status display when controls change"""
        if checked:
            self.status_label.setText(f"✓ {control_name} is now enabled")
            self.status_label.setStyleSheet("color: #10b981; font-weight: bold; padding: 15px; border: 1px solid #d1fae5; border-radius: 6px; background: #ecfdf5;")
        else:
            self.status_label.setText(f"✗ {control_name} is now disabled")
            self.status_label.setStyleSheet("color: #ef4444; font-weight: bold; padding: 15px; border: 1px solid #fecaca; border-radius: 6px; background: #fef2f2;")


def main():
    """Run the interactive indicators demo"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("SNID SAGE Interactive Indicators Demo")
    app.setOrganizationName("SNID SAGE")
    
    # Create and show demo window
    demo = InteractiveIndicatorsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
