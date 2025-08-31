"""
PySide6 Mask Manager Dialog Component

This module handles the wavelength mask management dialog functionality including:
- Viewing current mask regions
- Adding new mask ranges
- Removing existing masks
- Interactive masking integration
- Save and load mask configurations

Modern PySide6 Qt interface.
"""

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
from typing import List, Tuple, Optional

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_mask_manager')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_mask_manager')


class PySide6MaskManagerDialog(QtWidgets.QDialog):
    """
    PySide6 version of the wavelength mask management dialog.
    
    This class provides a comprehensive interface for managing wavelength masks
    that are used to exclude specific spectral regions from analysis.
    """
    
    def __init__(self, parent, current_masks: List[Tuple[float, float]] = None):
        """
        Initialize the mask manager dialog.
        
        Args:
            parent: Parent widget (main GUI instance)
            current_masks: List of current mask regions as (min_wave, max_wave) tuples
        """
        super().__init__(parent)
        self.parent_gui = parent
        self.current_masks = current_masks or []
        self.result = None
        
        # Theme colors (matching PySide6 main GUI)
        self.colors = {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#f1f5f9',
            'text_primary': '#1e293b',
            'text_secondary': '#475569',
            'border': '#cbd5e1',
            'btn_primary': '#3b82f6',
            'btn_success': '#10b981',
            'btn_danger': '#ef4444',
            'btn_warning': '#f59e0b',
        }
        
        self._setup_dialog()
        self._create_interface()
        self._populate_mask_list()
    
    def _setup_dialog(self):
        """Setup dialog window properties"""
        self.setWindowTitle("Wavelength Mask Management")
        self.resize(600, 500)
        self.setMinimumSize(500, 400)
        
        # Apply dialog styling (use platform-aware font stack)
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.colors['bg_primary']};
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
                background: {self.colors['bg_secondary']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {self.colors['text_primary']};
            }}
            
            QPushButton {{
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 24px;
                font-weight: bold;
                font-size: 10pt;
                background: {self.colors['bg_tertiary']};
            }}
            
            QPushButton:hover {{
                background: {self.colors['border']};
            }}
            
            QPushButton#primary_btn {{
                background: {self.colors['btn_primary']};
                color: white;
                border: 2px solid {self.colors['btn_primary']};
            }}
            
            QPushButton#primary_btn:hover {{
                background: #2563eb;
                border: 2px solid #2563eb;
            }}
            
            QPushButton#success_btn {{
                background: {self.colors['btn_success']};
                color: white;
                border: 2px solid {self.colors['btn_success']};
            }}
            
            QPushButton#success_btn:hover {{
                background: #059669;
                border: 2px solid #059669;
            }}
            
            QPushButton#danger_btn {{
                background: {self.colors['btn_danger']};
                color: white;
                border: 2px solid {self.colors['btn_danger']};
            }}
            
            QPushButton#danger_btn:hover {{
                background: #dc2626;
                border: 2px solid #dc2626;
            }}
            
            QListWidget {{
                background: {self.colors['bg_secondary']};
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-family: "Consolas", monospace;
                font-size: 10pt;
                selection-background-color: {self.colors['btn_primary']};
            }}
            
            QLineEdit {{
                background: {self.colors['bg_secondary']};
                border: 2px solid {self.colors['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {self.colors['btn_primary']};
            }}
            
            QLabel {{
                background: transparent;
                color: {self.colors['text_primary']};
            }}
        """)
    
    def _create_interface(self):
        """Create the main interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QtWidgets.QLabel("Wavelength Mask Management")
        title_label.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Current masks section
        self._create_current_masks_section(layout)
        
        # Add new mask section
        self._create_add_mask_section(layout)
        
        # Buttons
        self._create_buttons(layout)
    
    def _create_current_masks_section(self, layout):
        """Create current masks display section"""
        masks_group = QtWidgets.QGroupBox("Current Mask Regions")
        masks_layout = QtWidgets.QVBoxLayout(masks_group)
        
        # List widget for masks
        self.masks_list = QtWidgets.QListWidget()
        self.masks_list.setMinimumHeight(200)
        masks_layout.addWidget(self.masks_list)
        
        # Remove selected button
        remove_layout = QtWidgets.QHBoxLayout()
        remove_layout.addStretch()
        
        self.remove_btn = QtWidgets.QPushButton("Remove Selected")
        self.remove_btn.setObjectName("danger_btn")
        self.remove_btn.clicked.connect(self._remove_selected_mask)
        remove_layout.addWidget(self.remove_btn)
        
        self.clear_all_btn = QtWidgets.QPushButton("Clear All")
        self.clear_all_btn.setObjectName("danger_btn")
        self.clear_all_btn.clicked.connect(self._clear_all_masks)
        remove_layout.addWidget(self.clear_all_btn)
        
        masks_layout.addLayout(remove_layout)
        layout.addWidget(masks_group)
    
    def _create_add_mask_section(self, layout):
        """Create add new mask section"""
        add_group = QtWidgets.QGroupBox("Add New Mask Region")
        add_layout = QtWidgets.QVBoxLayout(add_group)
        
        # Input row
        input_layout = QtWidgets.QHBoxLayout()
        
        input_layout.addWidget(QtWidgets.QLabel("Wavelength Range:"))
        
        self.min_wave_input = QtWidgets.QLineEdit()
        self.min_wave_input.setPlaceholderText("Min wavelength (Å)")
        self.min_wave_input.setMaximumWidth(150)
        input_layout.addWidget(self.min_wave_input)
        
        input_layout.addWidget(QtWidgets.QLabel("to"))
        
        self.max_wave_input = QtWidgets.QLineEdit()
        self.max_wave_input.setPlaceholderText("Max wavelength (Å)")
        self.max_wave_input.setMaximumWidth(150)
        input_layout.addWidget(self.max_wave_input)
        
        self.add_mask_btn = QtWidgets.QPushButton("Add Mask")
        self.add_mask_btn.setObjectName("success_btn")
        self.add_mask_btn.clicked.connect(self._add_new_mask)
        input_layout.addWidget(self.add_mask_btn)
        
        input_layout.addStretch()
        add_layout.addLayout(input_layout)
        
        # Instructions
        instructions = QtWidgets.QLabel(
            "💡 Tip: Enter wavelength values in Angstroms (Å). "
            "Masked regions will be excluded from SNID analysis."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"color: {self.colors['text_secondary']}; font-style: italic;")
        add_layout.addWidget(instructions)
        
        layout.addWidget(add_group)
    
    def _create_buttons(self, layout):
        """Create dialog buttons"""
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        # Save & Load buttons
        self.save_btn = QtWidgets.QPushButton("Save Masks")
        self.save_btn.clicked.connect(self._save_masks)
        button_layout.addWidget(self.save_btn)
        
        self.load_btn = QtWidgets.QPushButton("Load Masks")
        self.load_btn.clicked.connect(self._load_masks)
        button_layout.addWidget(self.load_btn)
        
        button_layout.addSpacing(20)
        
        # Cancel and Apply buttons
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.apply_btn.setObjectName("primary_btn")
        self.apply_btn.clicked.connect(self._apply_masks)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_mask_list(self):
        """Populate the mask list with current masks"""
        self.masks_list.clear()
        
        if not self.current_masks:
            item = QtWidgets.QListWidgetItem("No mask regions defined")
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
            item.setForeground(QtGui.QColor(self.colors['text_secondary']))
            self.masks_list.addItem(item)
        else:
            for i, (min_wave, max_wave) in enumerate(self.current_masks):
                mask_text = f"Mask {i+1}: {min_wave:.1f} - {max_wave:.1f} Å"
                item = QtWidgets.QListWidgetItem(mask_text)
                item.setData(QtCore.Qt.UserRole, (min_wave, max_wave))
                self.masks_list.addItem(item)
    
    def _add_new_mask(self):
        """Add a new mask region"""
        try:
            min_wave = float(self.min_wave_input.text())
            max_wave = float(self.max_wave_input.text())
            
            if min_wave >= max_wave:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Invalid Range", 
                    "Maximum wavelength must be greater than minimum wavelength."
                )
                return
            
            if min_wave < 0 or max_wave < 0:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Invalid Values", 
                    "Wavelength values must be positive."
                )
                return
            
            # Add to current masks
            self.current_masks.append((min_wave, max_wave))
            
            # Update display
            self._populate_mask_list()
            
            # Clear inputs
            self.min_wave_input.clear()
            self.max_wave_input.clear()
            
            _LOGGER.debug(f"Added mask region: {min_wave:.1f} - {max_wave:.1f} Å")
            
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 
                "Invalid Input", 
                "Please enter valid numerical wavelength values."
            )
    
    def _remove_selected_mask(self):
        """Remove selected mask region"""
        current_item = self.masks_list.currentItem()
        if current_item and current_item.data(QtCore.Qt.UserRole) is not None:
            mask_data = current_item.data(QtCore.Qt.UserRole)
            if mask_data in self.current_masks:
                self.current_masks.remove(mask_data)
                self._populate_mask_list()
                _LOGGER.debug(f"Removed mask region: {mask_data[0]:.1f} - {mask_data[1]:.1f} Å")
    
    def _clear_all_masks(self):
        """Clear all mask regions"""
        if self.current_masks:
            reply = QtWidgets.QMessageBox.question(
                self, 
                "Clear All Masks", 
                "Are you sure you want to remove all mask regions?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                self.current_masks.clear()
                self._populate_mask_list()
                _LOGGER.debug("Cleared all mask regions")
    
    def _save_masks(self):
        """Save masks to file"""
        if not self.current_masks:
            QtWidgets.QMessageBox.information(
                self, 
                "No Masks", 
                "No mask regions to save."
            )
            return
        
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Mask Regions",
            "mask_regions.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("# SNID SAGE Mask Regions\n")
                    f.write("# Format: min_wavelength max_wavelength\n")
                    for min_wave, max_wave in self.current_masks:
                        f.write(f"{min_wave:.3f} {max_wave:.3f}\n")
                
                QtWidgets.QMessageBox.information(
                    self, 
                    "Masks Saved", 
                    f"Mask regions saved to {filename}"
                )
                _LOGGER.info(f"Saved {len(self.current_masks)} mask regions to {filename}")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Save Error", 
                    f"Error saving mask file:\n{e}"
                )
    
    def _load_masks(self):
        """Load masks from file"""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load Mask Regions",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                loaded_masks = []
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split()
                            if len(parts) >= 2:
                                min_wave = float(parts[0])
                                max_wave = float(parts[1])
                                loaded_masks.append((min_wave, max_wave))
                
                if loaded_masks:
                    # Ask whether to replace or append
                    if self.current_masks:
                        reply = QtWidgets.QMessageBox.question(
                            self,
                            "Load Masks",
                            f"Found {len(loaded_masks)} mask regions in file.\n\n"
                            "Replace current masks or append to existing?",
                            QtWidgets.QMessageBox.StandardButton.Yes | 
                            QtWidgets.QMessageBox.StandardButton.No | 
                            QtWidgets.QMessageBox.StandardButton.Cancel
                        )
                        
                        if reply == QtWidgets.QMessageBox.Cancel:
                            return
                        elif reply == QtWidgets.QMessageBox.Yes:
                            # Replace
                            self.current_masks = loaded_masks
                        else:
                            # Append
                            self.current_masks.extend(loaded_masks)
                    else:
                        self.current_masks = loaded_masks
                    
                    self._populate_mask_list()
                    QtWidgets.QMessageBox.information(
                        self, 
                        "Masks Loaded", 
                        f"Loaded {len(loaded_masks)} mask regions from {filename}"
                    )
                    _LOGGER.info(f"Loaded {len(loaded_masks)} mask regions from {filename}")
                else:
                    QtWidgets.QMessageBox.warning(
                        self, 
                        "No Masks Found", 
                        "No valid mask regions found in the file."
                    )
                    
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Load Error", 
                    f"Error loading mask file:\n{e}"
                )
    
    def _apply_masks(self):
        """Apply the current mask configuration"""
        self.result = self.current_masks.copy()
        _LOGGER.info(f"Applied {len(self.current_masks)} mask regions")
        self.accept()
    
    def get_result(self) -> Optional[List[Tuple[float, float]]]:
        """Get the result mask regions"""
        return self.result 