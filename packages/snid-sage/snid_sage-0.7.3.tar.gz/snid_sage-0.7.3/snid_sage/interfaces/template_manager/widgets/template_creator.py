"""
Template Creator Widget
======================

Widget for creating new templates from spectra.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui

# Import flexible number input widget
from snid_sage.interfaces.gui.components.widgets.flexible_number_input import create_flexible_double_input

# Import layout manager
from ..utils.layout_manager import get_template_layout_manager
from ..services.template_service import get_template_service

# Import main GUI preprocessing dialog if available
try:
    from snid_sage.interfaces.gui.components.pyside6_dialogs.preprocessing_dialog import PySide6PreprocessingDialog
    MAIN_GUI_AVAILABLE = True
except ImportError:
    MAIN_GUI_AVAILABLE = False

# SNID imports
try:
    from snid_sage.snid.snid import preprocess_spectrum
    SNID_AVAILABLE = True
except ImportError:
    SNID_AVAILABLE = False

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.creator')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.creator')


class TemplateCreatorWidget(QtWidgets.QWidget):
    """Widget for creating new templates from spectra"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_spectrum = None
        self.layout_manager = get_template_layout_manager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the template creation interface"""
        layout = QtWidgets.QVBoxLayout(self)
        self.layout_manager.apply_panel_layout(self, layout)
        
        # File selection
        file_group = QtWidgets.QGroupBox("Input Spectrum")
        self.layout_manager.setup_group_box(file_group)
        file_layout = QtWidgets.QHBoxLayout(file_group)
        
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_edit.setPlaceholderText("Select a spectrum file...")
        
        browse_btn = self.layout_manager.create_action_button("Browse", "📁")
        browse_btn.clicked.connect(self.browse_spectrum_file)
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # Template metadata
        metadata_group = QtWidgets.QGroupBox("Template Metadata")
        self.layout_manager.setup_group_box(metadata_group)
        metadata_layout = QtWidgets.QFormLayout(metadata_group)
        self.layout_manager.setup_form_layout(metadata_layout)
        
        self.name_edit = QtWidgets.QLineEdit()
        self.type_combo = QtWidgets.QComboBox()
        # Populate dynamically from merged index
        try:
            svc = get_template_service()
            by_type = svc.get_merged_index().get('by_type', {})
            dynamic_types = sorted(list(by_type.keys()))
            if dynamic_types:
                self.type_combo.addItems(dynamic_types)
            else:
                self.type_combo.addItems(["Ia", "Ib", "Ic", "II", "AGN", "Galaxy", "Star"])  # minimal fallback
        except Exception:
            self.type_combo.addItems(["Ia", "Ib", "Ic", "II", "AGN", "Galaxy", "Star"])  # fallback
        
        self.subtype_edit = QtWidgets.QLineEdit()
        self.age_spinbox = create_flexible_double_input(min_val=-999.9, max_val=999.9, suffix=" days", default=0.0)
        
        self.redshift_spinbox = create_flexible_double_input(min_val=0.0, max_val=5.0, default=0.0)
        
        metadata_layout.addRow("Template Name:", self.name_edit)
        metadata_layout.addRow("Type:", self.type_combo)
        metadata_layout.addRow("Subtype:", self.subtype_edit)
        metadata_layout.addRow("Age:", self.age_spinbox)
        metadata_layout.addRow("Redshift:", self.redshift_spinbox)
        
        layout.addWidget(metadata_group)
        
        # Preprocessing controls
        preprocess_group = QtWidgets.QGroupBox("Preprocessing Options")
        self.layout_manager.setup_group_box(preprocess_group)
        preprocess_layout = QtWidgets.QVBoxLayout(preprocess_group)
        
        self.preprocess_btn = self.layout_manager.create_action_button("Advanced Preprocessing", "🔧")
        self.preprocess_btn.clicked.connect(self.open_preprocessing_dialog)
        
        self.quick_preprocess_btn = self.layout_manager.create_action_button("Quick Preprocessing", "⚡")
        self.quick_preprocess_btn.clicked.connect(self.run_quick_preprocessing)
        
        preprocess_layout.addWidget(self.preprocess_btn)
        preprocess_layout.addWidget(self.quick_preprocess_btn)
        
        layout.addWidget(preprocess_group)
        
        # Create template button
        create_btn = self.layout_manager.create_create_button()
        create_btn.clicked.connect(self.create_template)
        
        layout.addWidget(create_btn)
        layout.addStretch()
        
    def browse_spectrum_file(self):
        """Browse for a spectrum file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Select Spectrum File",
            "",
            "All Supported (*.txt *.dat *.ascii *.asci *.fits *.flm);;Text Files (*.txt *.dat *.ascii *.asci *.flm);;FITS Files (*.fits);;FLM Files (*.flm);;All Files (*.*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            # Auto-populate template name from filename
            basename = os.path.splitext(os.path.basename(file_path))[0]
            self.name_edit.setText(basename)
            
    def open_preprocessing_dialog(self):
        """Open the advanced preprocessing dialog"""
        if not MAIN_GUI_AVAILABLE:
            QtWidgets.QMessageBox.warning(self, "Feature Unavailable", "Advanced preprocessing requires main GUI components.")
            return
            
        spectrum_file = self.file_path_edit.text()
        if not spectrum_file or not os.path.exists(spectrum_file):
            QtWidgets.QMessageBox.warning(self, "No Spectrum", "Please select a valid spectrum file first.")
            return
            
        try:
            # Load spectrum data
            wave, flux = self._load_spectrum(spectrum_file)
            
            dialog = PySide6PreprocessingDialog(self, (wave, flux))
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                self.current_spectrum = dialog.result
                QtWidgets.QMessageBox.information(self, "Success", "Preprocessing completed. You can now create the template.")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error in preprocessing: {e}")
            _LOGGER.error(f"Preprocessing error: {e}")
            
    def run_quick_preprocessing(self):
        """Run quick preprocessing with default parameters"""
        spectrum_file = self.file_path_edit.text()
        if not spectrum_file or not os.path.exists(spectrum_file):
            QtWidgets.QMessageBox.warning(self, "No Spectrum", "Please select a valid spectrum file first.")
            return
            
        if not SNID_AVAILABLE:
            QtWidgets.QMessageBox.warning(self, "Feature Unavailable", "Preprocessing requires SNID core components.")
            return
            
        try:
            # Run quick preprocessing
            processed_spectrum, trace = preprocess_spectrum(
                spectrum_path=spectrum_file,
                verbose=True
            )
            
            self.current_spectrum = processed_spectrum
            QtWidgets.QMessageBox.information(self, "Success", "Quick preprocessing completed. You can now create the template.")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error in quick preprocessing: {e}")
            _LOGGER.error(f"Quick preprocessing error: {e}")
            
    def create_template(self):
        """Create the template with current settings"""
        # Validate inputs
        if not self.name_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "Missing Information", "Please enter a template name.")
            return
            
        if not self.file_path_edit.text() or not os.path.exists(self.file_path_edit.text()):
            QtWidgets.QMessageBox.warning(self, "Missing File", "Please select a valid spectrum file.")
            return
            
        # Prepare template metadata
        template_info = {
            'name': self.name_edit.text().strip(),
            'type': self.type_combo.currentText(),
            'subtype': self.subtype_edit.text().strip() or 'Unknown',
            'age': self.age_spinbox.value(),
            'redshift': self.redshift_spinbox.value(),
            'phase': 'Unknown',
            'epochs': 1
        }
        
        try:
            # Use preprocessed spectrum if available, otherwise load and preprocess
            if self.current_spectrum:
                spectrum_data = self.current_spectrum
            else:
                # Load spectrum and apply quick preprocessing
                wave, flux = self._load_spectrum(self.file_path_edit.text())
                
                if SNID_AVAILABLE:
                    processed_spectrum, trace = preprocess_spectrum(
                        input_spectrum=(wave, flux),
                        verbose=False
                    )
                    spectrum_data = processed_spectrum
                else:
                    # Simple dictionary structure if SNID not available
                    spectrum_data = {
                        'wave': wave,
                        'flux': flux,
                        'fluxed': flux,
                        'flat': flux / np.median(flux)
                    }
            
            # Extract wave/flux arrays
            wave = spectrum_data.get('processed_wave') or spectrum_data.get('wave') or spectrum_data.get('wavelength')
            flux = spectrum_data.get('flat') or spectrum_data.get('processed_flux') or spectrum_data.get('flux')
            if wave is None or flux is None:
                raise ValueError("No valid wave/flux in spectrum data")

            wave = np.asarray(wave, dtype=float)
            flux = np.asarray(flux, dtype=float)

            # De-redshift to rest-frame if needed
            try:
                z_input = float(template_info.get('redshift', 0.0) or 0.0)
            except Exception:
                z_input = 0.0
            if z_input != 0.0 and wave.size > 0:
                wave = wave / (1.0 + z_input)

            # Persist via HDF5-only service
            svc = get_template_service()
            success = svc.add_template_from_arrays(
                name=template_info['name'],
                ttype=template_info['type'],
                subtype=template_info['subtype'],
                age=float(template_info['age']),
                redshift=float(template_info['redshift']),
                phase=template_info['phase'],
                wave=wave,
                flux=flux,
            )
            
            if success:
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    f"Template '{template_info['name']}' created successfully!\n\n"
                    f"Type: {template_info['type']}/{template_info['subtype']}\n"
                    f"Age: {template_info['age']} days\n"
                    f"Redshift: {template_info['redshift']}"
                )
                
                # Clear form for next template
                self._clear_form()
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to create template. Check logs for details.")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error creating template: {str(e)}")
            _LOGGER.error(f"Template creation error: {e}")
            
    def _save_template(self, template_info: Dict[str, Any], spectrum_data: Dict[str, np.ndarray]) -> bool:
        """Deprecated: LNW saving removed. Use TemplateService instead."""
        _LOGGER.error("_save_template legacy path invoked; this method is deprecated in HDF5-only mode.")
        return False
            
    def _clear_form(self):
        """Clear the template creation form"""
        self.file_path_edit.clear()
        self.name_edit.clear()
        self.subtype_edit.clear()
        self.age_spinbox.setValue(0.0)
        self.redshift_spinbox.setValue(0.0)
        self.current_spectrum = None
        
    def _load_spectrum(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load spectrum from file"""
        try:
            # Try different file formats (LNW removed)
            if file_path.endswith('.fits'):
                return self._load_fits_spectrum(file_path)
            elif file_path.endswith('.flm'):
                return self._load_ascii_spectrum(file_path)  # FLM files are text-based
            else:
                return self._load_ascii_spectrum(file_path)
        except Exception as e:
            _LOGGER.error(f"Error loading spectrum: {e}")
            # Return dummy data on error
            wave = np.linspace(3000, 9000, 1000)
            flux = np.random.normal(1, 0.1, 1000)
            return wave, flux
            
    def _load_fits_spectrum(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load spectrum from FITS file"""
        try:
            from astropy.io import fits
            with fits.open(file_path) as hdul:
                # Try to find spectrum data in different extensions
                for hdu in hdul:
                    if hdu.data is not None:
                        data = hdu.data
                        if len(data.shape) == 1:
                            # 1D spectrum - assume wavelength is indices
                            flux = data
                            wave = np.arange(len(flux)) + 1
                            return wave, flux
                        elif len(data.shape) == 2:
                            # 2D - assume first column is wavelength, second is flux
                            wave = data[:, 0]
                            flux = data[:, 1]
                            return wave, flux
        except ImportError:
            raise ImportError("astropy required for FITS files: pip install astropy")
            
    # LNW loading removed
        
    def _load_ascii_spectrum(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load spectrum from ASCII file"""
        try:
            # Try to load as two-column ASCII
            data = np.loadtxt(file_path)
            if data.shape[1] >= 2:
                wave = data[:, 0]
                flux = data[:, 1]
                return wave, flux
            else:
                # Single column - assume flux only
                flux = data
                wave = np.arange(len(flux)) + 1
                return wave, flux
        except Exception as e:
            raise ValueError(f"Could not load ASCII spectrum: {e}")
    
    def set_spectrum_file(self, file_path: str):
        """Set the spectrum file path programmatically"""
        if os.path.exists(file_path):
            self.file_path_edit.setText(file_path)
            basename = os.path.splitext(os.path.basename(file_path))[0]
            self.name_edit.setText(basename)
    
    def get_current_template_info(self) -> Dict[str, Any]:
        """Get the current template information from the form"""
        return {
            'name': self.name_edit.text().strip(),
            'type': self.type_combo.currentText(),
            'subtype': self.subtype_edit.text().strip() or 'Unknown',
            'age': self.age_spinbox.value(),
            'redshift': self.redshift_spinbox.value(),
            'spectrum_file': self.file_path_edit.text()
        }
    
    def validate_form(self) -> Tuple[bool, str]:
        """Validate the current form state"""
        if not self.name_edit.text().strip():
            return False, "Template name is required"
        
        if not self.file_path_edit.text():
            return False, "Spectrum file is required"
        
        if not os.path.exists(self.file_path_edit.text()):
            return False, "Spectrum file does not exist"
        
        return True, "Form is valid"