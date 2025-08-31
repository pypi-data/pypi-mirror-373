"""
SNID Template Manager - Main Window
==================================

Main window for the SNID Template Manager GUI.
"""

import sys
import json
import logging
from typing import Dict, Any, Optional
from PySide6 import QtWidgets, QtCore, QtGui

# Import components
from .components.template_tree import TemplateTreeWidget
from .components.template_visualization import TemplateVisualizationWidget
from .widgets.template_creator import TemplateCreatorWidget
from .widgets.template_manager import TemplateManagerWidget

# Import utilities
from .utils.theme_manager import get_template_theme_manager
from .utils.layout_manager import get_template_layout_manager

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.main')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.main')


class SNIDTemplateManagerGUI(QtWidgets.QMainWindow):
    """Main template manager GUI window"""
    
    def __init__(self):
        super().__init__()
        self.theme_manager = get_template_theme_manager()
        self.layout_manager = get_template_layout_manager()
        self.setup_window()
        self.setup_theme()
        self.create_interface()
        
    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle("SNID Template Manager")
        
        # Try to use centralized logo manager icon if available
        try:
            from snid_sage.interfaces.ui_core.logo import get_logo_manager
            icon_path = get_logo_manager().get_icon_path()
            if icon_path:
                self.setWindowIcon(QtGui.QIcon(str(icon_path)))
            else:
                self.setWindowIcon(QtGui.QIcon())
        except Exception:
            self.setWindowIcon(QtGui.QIcon())
        
        # Setup window with layout manager
        self.layout_manager.setup_main_window(self)
        
    def setup_theme(self):
        """Setup theme matching main GUI"""
        try:
            stylesheet = self.theme_manager.generate_complete_stylesheet()
            self.setStyleSheet(stylesheet)
        except Exception as e:
            _LOGGER.warning(f"Could not apply theme: {e}")
            
    def create_interface(self):
        """Create the main interface"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        self.layout_manager.apply_panel_layout(central_widget, main_layout)
        
        # Create main splitter
        splitter = self.layout_manager.create_main_splitter()
        main_layout.addWidget(splitter)
        
        # Left panel - Template browser
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Tabbed interface
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Create status bar
        self.create_status_bar()
        
    def create_left_panel(self) -> QtWidgets.QWidget:
        """Create the left panel with template browser"""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        self.layout_manager.apply_panel_layout(panel, layout)
        
        # Header
        header = QtWidgets.QLabel("Template Library")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Search and filters
        search_frame = QtWidgets.QFrame()
        search_layout = QtWidgets.QVBoxLayout(search_frame)
        
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search templates...")
        self.search_edit.textChanged.connect(self._filter_templates)
        search_layout.addWidget(self.search_edit)
        
        self.type_filter = QtWidgets.QComboBox()
        # Populate dynamically from merged index
        try:
            from .services.template_service import get_template_service
            by_type = get_template_service().get_merged_index().get('by_type', {})
            dynamic_types = sorted(list(by_type.keys()))
            self.type_filter.addItem("All Types")
            self.type_filter.addItems(dynamic_types)
        except Exception:
            # Fallback to minimal defaults
            self.type_filter.addItems(["All Types", "Ia", "Ib", "Ic", "II", "AGN", "Galaxy", "Star"])
        self.type_filter.currentTextChanged.connect(self._filter_templates)
        search_layout.addWidget(self.type_filter)
        
        layout.addWidget(search_frame)
        
        # Template tree
        self.template_tree = TemplateTreeWidget()
        self.template_tree.template_selected.connect(self.on_template_selected)
        self.layout_manager.setup_template_browser(self.template_tree)
        layout.addWidget(self.template_tree)
        
        # Refresh button
        refresh_btn = self.layout_manager.create_action_button("Refresh", "🔄")
        refresh_btn.clicked.connect(self.template_tree.load_templates)
        layout.addWidget(refresh_btn)
        
        return panel
        
    def _filter_templates(self):
        """Filter templates based on search text and type"""
        search_text = self.search_edit.text()
        type_filter = self.type_filter.currentText()
        self.template_tree.filter_templates(search_text, type_filter)
        
    def create_right_panel(self) -> QtWidgets.QWidget:
        """Create the right panel with tabbed interface"""
        self.tab_widget = QtWidgets.QTabWidget()
        self.layout_manager.setup_tab_widget(self.tab_widget)
        
        # Template Viewer tab
        self.viewer_widget = TemplateVisualizationWidget()
        self.tab_widget.addTab(self.viewer_widget, "Template Viewer")
        
        # Template Creator tab
        self.creator_widget = TemplateCreatorWidget()
        self.tab_widget.addTab(self.creator_widget, "Create Template")
        
        # Template Manager tab
        self.manager_widget = TemplateManagerWidget()
        self.tab_widget.addTab(self.manager_widget, "Manage Templates")

        # Apply Twemoji tab icons now that tabs are ready
        try:
            self.layout_manager.apply_tab_icons(self.tab_widget)
        except Exception:
            pass
        
        return self.tab_widget
        
    def create_status_bar(self):
        """Create the status bar"""
        status_bar = self.statusBar()
        
        # Template count label
        self.template_count_label = QtWidgets.QLabel("Templates: Loading...")
        status_bar.addWidget(self.template_count_label)
        
        status_bar.addPermanentWidget(QtWidgets.QLabel("SNID Template Manager v1.0"))
        
        # Update template count
        QtCore.QTimer.singleShot(1000, self.update_template_count)
        
    def update_template_count(self):
        """Update the template count in status bar"""
        try:
            count = self.template_tree.get_template_count()
            self.template_count_label.setText(f"Templates: {count}")
        except Exception as e:
            self.template_count_label.setText("Templates: Error")
            _LOGGER.error(f"Error updating template count: {e}")
            
    @QtCore.Slot(str, dict)
    def on_template_selected(self, template_name: str, template_info: Dict[str, Any]):
        """Handle template selection from tree"""
        # Switch to viewer tab and update display
        self.tab_widget.setCurrentIndex(0)
        self.viewer_widget.set_template(template_name, template_info)
        
        # Update manager widget with selected template
        self.manager_widget.set_template_for_editing(template_name, template_info)
        
        # Update status bar
        template_type = template_info.get('type', 'Unknown')
        subtype = template_info.get('subtype', 'Unknown')
        epochs = template_info.get('epochs', 1)
        # Clean template name to remove _epoch_X suffix
        from snid_sage.shared.utils import clean_template_name
        clean_name = clean_template_name(template_name)
        self.statusBar().showMessage(f"Selected: {clean_name} ({template_type}/{subtype}, {epochs} epochs)")
    
    def get_current_template(self) -> Optional[tuple]:
        """Get the currently selected template"""
        return self.template_tree.get_selected_template()
    
    def refresh_template_library(self):
        """Refresh the template library"""
        self.template_tree.load_templates()
        self.update_template_count()
    
    def show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self,
            "About SNID Template Manager",
            "SNID Template Manager v1.0\n\n"
            "A comprehensive GUI for managing SNID templates.\n\n"
            "Features:\n"
            "• Browse and visualize templates\n"
            "• Create new templates\n"
            "• Manage template metadata\n\n"
            "Developed by Fiorenzo Stoppa for SNID SAGE"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Exit Template Manager',
            'Are you sure you want to exit the Template Manager?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()