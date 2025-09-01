"""
Template Tree Widget
===================

Tree widget for displaying and selecting templates organized by type/subtype.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from PySide6 import QtWidgets, QtCore

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.tree')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.tree')


class TemplateTreeWidget(QtWidgets.QTreeWidget):
    """Custom tree widget for displaying templates by type/subtype"""
    
    template_selected = QtCore.Signal(str, dict)  # template_name, template_info
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Template", "Type"])
        self.setSelectionMode(QtWidgets.QTreeWidget.SingleSelection)
        self.itemClicked.connect(self._on_item_clicked)
        
        # Load templates on initialization
        self.load_templates()
        
    def load_templates(self):
        """Load templates from the template index"""
        try:
            # Use merged index (built-in + user)
            try:
                from snid_sage.interfaces.template_manager.services.template_service import get_template_service
                index_data = get_template_service().get_merged_index()
            except Exception as e:
                _LOGGER.warning(f"Falling back to legacy index loading: {e}")
                template_index_path = self._find_template_index()
                if not template_index_path:
                    _LOGGER.warning("Template index not found")
                    self._create_sample_templates()
                    return
                with open(template_index_path, 'r') as f:
                    index_data = json.load(f)
                
            self.clear()
            
            # Group templates by type
            for template_type, type_info in index_data.get('by_type', {}).items():
                type_item = QtWidgets.QTreeWidgetItem(self, [template_type, f"{type_info['count']} templates"])
                type_item.setExpanded(True)
                
                # Add individual templates
                for template_name in type_info.get('template_names', []):
                    template_info = index_data['templates'][template_name]
                    
                    subtype = template_info.get('subtype', 'Unknown')
                    
                    template_item = QtWidgets.QTreeWidgetItem(type_item, [
                        template_name, 
                        f"{template_type}/{subtype}"
                    ])
                    template_item.setData(0, QtCore.Qt.UserRole, template_info)
                    
        except Exception as e:
            _LOGGER.error(f"Error loading templates: {e}")
            self._create_sample_templates()
    
    def _create_sample_templates(self):
        """Create sample templates for testing when index is not available"""
        _LOGGER.info("Creating sample templates for testing")
        
        sample_data = {
            'Ia': [
                {'name': 'sn1991T', 'subtype': 'Ia-91T', 'age': 0.0, 'epochs': 5},
                {'name': 'sn1994D', 'subtype': 'Ia-norm', 'age': 5.0, 'epochs': 3},
                {'name': 'sn2011fe', 'subtype': 'Ia-norm', 'age': -3.0, 'epochs': 7},
            ],
            'II': [
                {'name': 'sn1993J', 'subtype': 'IIb', 'age': 10.0, 'epochs': 4},
                {'name': 'sn1999em', 'subtype': 'IIP', 'age': 0.0, 'epochs': 6},
            ],
            'Ib': [
                {'name': 'sn2008D', 'subtype': 'Ib', 'age': 15.0, 'epochs': 3},
                {'name': 'sn1999ex', 'subtype': 'Ib', 'age': 8.0, 'epochs': 4},
            ],
            'Ic': [
                {'name': 'sn1998bw', 'subtype': 'Ic-BL', 'age': 12.0, 'epochs': 5},
                {'name': 'sn2002ap', 'subtype': 'Ic', 'age': 7.0, 'epochs': 3},
            ]
        }
        
        self.clear()
        
        for template_type, templates in sample_data.items():
            type_item = QtWidgets.QTreeWidgetItem(self, [template_type, f"{len(templates)} templates"])
            type_item.setExpanded(True)
            
            for template_data in templates:
                template_info = {
                    'type': template_type,
                    'subtype': template_data['subtype'],
                    'age': template_data['age'],
                    'epochs': template_data['epochs'],
                    'redshift': 0.01,
                    'storage_file': f'templates_{template_type}.hdf5'
                }
                
                template_item = QtWidgets.QTreeWidgetItem(type_item, [
                    template_data['name'],
                    f"{template_type}/{template_data['subtype']}"
                ])
                template_item.setData(0, QtCore.Qt.UserRole, template_info)
            
    def _find_template_index(self) -> Optional[str]:
        """Find the template index file"""
        possible_paths = [
            "snid_sage/templates/template_index.json",
            "templates/template_index.json",
            "template_index.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                _LOGGER.info(f"Found template index at: {path}")
                return path
        _LOGGER.warning("Template index not found in any of the expected locations")
        return None
        
    def _on_item_clicked(self, item, column):
        """Handle template selection"""
        template_info = item.data(0, QtCore.Qt.UserRole)
        if template_info:
            template_name = item.text(0)
            self.template_selected.emit(template_name, template_info)
    
    def filter_templates(self, search_text: str = "", type_filter: str = "All Types"):
        """Filter templates based on search text and selected type.
        Types are dynamic; no special 'Other' bucket.
        """
        search_text = search_text.lower()

        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            type_item = root.child(i)
            type_name = type_item.text(0)

            type_visible = (type_filter == "All Types" or type_filter == type_name)

            template_count = 0
            visible_templates = 0

            for j in range(type_item.childCount()):
                template_item = type_item.child(j)
                template_name = template_item.text(0).lower()
                template_type = template_item.text(1).lower()

                search_visible = (not search_text or search_text in template_name or search_text in template_type)

                template_visible = type_visible and search_visible
                template_item.setHidden(not template_visible)

                template_count += 1
                if template_visible:
                    visible_templates += 1

            if visible_templates > 0:
                type_item.setText(0, f"{type_name} ({visible_templates}/{template_count})")
                type_item.setHidden(False)
            else:
                type_item.setHidden(not type_visible or bool(search_text))
                if not type_item.isHidden():
                    type_item.setText(0, f"{type_name} (0/{template_count})")
    
    def get_selected_template(self) -> Optional[tuple]:
        """Get the currently selected template"""
        current_item = self.currentItem()
        if current_item:
            template_info = current_item.data(0, QtCore.Qt.UserRole)
            if template_info:
                template_name = current_item.text(0)
                return (template_name, template_info)
        return None
    
    def select_template_by_name(self, template_name: str) -> bool:
        """Select a template by name"""
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            type_item = root.child(i)
            for j in range(type_item.childCount()):
                template_item = type_item.child(j)
                if template_item.text(0) == template_name:
                    self.setCurrentItem(template_item)
                    template_info = template_item.data(0, QtCore.Qt.UserRole)
                    if template_info:
                        self.template_selected.emit(template_name, template_info)
                    return True
        return False
    
    def get_all_templates(self) -> List[tuple]:
        """Get all templates as a list of (name, info) tuples"""
        templates = []
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            type_item = root.child(i)
            for j in range(type_item.childCount()):
                template_item = type_item.child(j)
                template_info = template_item.data(0, QtCore.Qt.UserRole)
                if template_info:
                    template_name = template_item.text(0)
                    templates.append((template_name, template_info))
        return templates
    
    def get_template_count(self) -> int:
        """Get the total number of templates"""
        count = 0
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            type_item = root.child(i)
            count += type_item.childCount()
        return count
    
    def get_type_counts(self) -> Dict[str, int]:
        """Get template counts by type"""
        counts = {}
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            type_item = root.child(i)
            type_name = type_item.text(0).split(' (')[0]  # Remove count from display
            counts[type_name] = type_item.childCount()
        return counts