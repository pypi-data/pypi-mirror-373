"""
PySide6 Multi-Step Spectral Line Analysis Dialog - Step 2 (Peak Analysis)
========================================================================

This module contains all the Step 2 analysis functionality for the spectral lines dialog.
Separated from the main dialog to keep the code organized and manageable.

Step 2 Features:
- Line selection and navigation
- Peak analysis methods (Auto Detection, Gaussian Fit, Empirical Analysis, Manual Points)
- FWHM measurements
- Line fitting and analysis
- Results export
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from PySide6 import QtWidgets, QtCore, QtGui

# PyQtGraph for plotting
try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    pg = None

# Enhanced interactive analysis (scipy for peak analysis)
try:
    from scipy import signal
    from scipy.optimize import curve_fit
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_emission_step2')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_emission_step2')

# Import platform configuration
from snid_sage.shared.utils.config.platform_config import get_platform_config


class EmissionLineStep2Analysis:
    """
    Step 2 analysis functionality for emission line peak analysis and FWHM measurements.
    This class handles all the complex analysis methods separated from the main dialog.
    """
    
    def __init__(self, parent_dialog):
        """Initialize Step 2 analysis with reference to parent dialog"""
        self.parent = parent_dialog
        self.spectrum_data = parent_dialog.spectrum_data
        self.colors = parent_dialog.colors
        
        # Step 2 specific data
        self.available_lines = []
        self.current_line_index = 0
        self.line_analysis_results = {}
        self.selected_manual_points = []
        self.line_fit_results = {}
        
        # UI components (will be set by parent)
        self.line_dropdown = None
        self.method_combo = None
        self.line_counter_label = None
        self.current_result_text = None
        self.summary_text = None
        
    def create_step_2_interface(self, layout):
        """Create Step 2 peak analysis interface (simplified - only Manual Points method)"""
        # Description
        desc = QtWidgets.QLabel(
            "Manual point selection for spectral line analysis. "
            "Use the toolbar above to navigate lines and adjust zoom level."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {self.colors['text_secondary']}; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Manual Points Instructions (always visible since it's the only method)
        # Get platform-appropriate click text
        platform_config = get_platform_config()
        right_click_text = platform_config.get_click_text("right")

        self.manual_instructions = QtWidgets.QLabel(
            "Manual Selection Instructions:\n"
            "• Left Click: Add point snapped to nearest bin\n"
            "• Ctrl/Cmd+Click: Add free-floating point anywhere\n"
            f"• {right_click_text}: Remove closest point\n"
            "• Velocity preview appears after selecting at least 5 points"
        )
        self.manual_instructions.setWordWrap(True)
        self.manual_instructions.setStyleSheet(f"color: {self.colors.get('text_secondary', '#666')}; padding: 5px;")
        layout.addWidget(self.manual_instructions)
        
        # Manual point controls removed in favor of toolbar button
        
        # Single minimal summary
        summary_group = QtWidgets.QGroupBox("📋 Line Summary")
        summary_layout = QtWidgets.QVBoxLayout(summary_group)
        
        summary_controls = QtWidgets.QHBoxLayout()
        
        copy_summary_btn = QtWidgets.QPushButton("Copy Summary")
        copy_summary_btn.clicked.connect(self.copy_summary)
        summary_controls.addWidget(copy_summary_btn)
        
        export_btn = QtWidgets.QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        summary_controls.addWidget(export_btn)
        
        summary_controls.addStretch()
        summary_layout.addLayout(summary_controls)
        
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.summary_text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        summary_layout.addWidget(self.summary_text, 1)
        
        layout.addWidget(summary_group, 1)
        
        # Initialize - will be properly connected by parent
        self.populate_line_dropdown()
        # No method visibility update needed since only Manual Points is supported
    
    def populate_line_dropdown(self):
        """Populate line dropdown with available lines"""
        if not self.line_dropdown:
            return
            
        self.line_dropdown.clear()
        self.available_lines = []
        
        # Add SN lines
        for line_name in self.parent.sn_lines.keys():
            self.available_lines.append(('sn', line_name))
            self.line_dropdown.addItem(f"🌟 {line_name}")
        
        # Add Galaxy lines
        for line_name in self.parent.galaxy_lines.keys():
            self.available_lines.append(('galaxy', line_name))
            self.line_dropdown.addItem(f"🌌 {line_name}")
        
        self.update_line_counter()
        self.update_line_navigation_buttons()
    
    def on_line_selection_changed(self, text):
        """Handle line selection change"""
        if not text or not self.available_lines:
            return
        
        # Find the index of the selected line
        for i, (line_type, line_name) in enumerate(self.available_lines):
            display_name = f"{'🌟' if line_type == 'sn' else '🌌'} {line_name}"
            if display_name == text:
                self.current_line_index = i
                break
        
        # Clear any existing manual points when switching lines
        self.selected_manual_points.clear()
        self.update_line_counter()
        self.plot_focused_line()
    
    def previous_line(self):
        """Go to previous line"""
        if self.current_line_index > 0:
            self.current_line_index -= 1
            self.update_line_selection()
    
    def next_line(self):
        """Go to next line"""
        if self.current_line_index < len(self.available_lines) - 1:
            self.current_line_index += 1
            self.update_line_selection()
    
    def update_line_selection(self):
        """Update line selection in dropdown"""
        if self.available_lines and 0 <= self.current_line_index < len(self.available_lines):
            line_type, line_name = self.available_lines[self.current_line_index]
            display_name = f"{'🌟' if line_type == 'sn' else '🌌'} {line_name}"
            if self.line_dropdown:
                self.line_dropdown.setCurrentText(display_name)
            # Clear any existing manual points when switching lines
            self.selected_manual_points.clear()
            self.update_line_counter()
            self.plot_focused_line()
    
    def update_line_counter(self):
        """Update line counter display"""
        total_lines = len(self.available_lines)
        current = self.current_line_index + 1 if total_lines > 0 else 0
        if self.line_counter_label:
            self.line_counter_label.setText(f"Line {current} of {total_lines}")
    
    def update_line_navigation_buttons(self):
        """Update navigation button states"""
        has_lines = len(self.available_lines) > 0
        # Use the correct button references from the dialog
        if hasattr(self.parent, 'step2_prev_btn'):
            self.parent.step2_prev_btn.setEnabled(has_lines and self.current_line_index > 0)
        if hasattr(self.parent, 'step2_next_btn'):
            self.parent.step2_next_btn.setEnabled(has_lines and self.current_line_index < len(self.available_lines) - 1)
    
    def on_zoom_changed(self, value):
        """Handle zoom range change with fixed zoom value of 150"""
        # Fixed zoom value of 100 Å - always plot focused line
        self.plot_focused_line()
    
    def show_full_spectrum(self):
        """Show full spectrum view with all lines marked"""
        if not PYQTGRAPH_AVAILABLE or not self.parent.plot_item:
            return
        
        # Use parent's full spectrum plotting method
        self.parent._update_plot()
    
    def on_method_changed(self, method_text):
        """Handle analysis method change"""
        self.update_method_visibility()
    
    def update_method_visibility(self):
        """Update visibility of method-specific controls (Manual Points only)"""
        if hasattr(self, 'manual_instructions') and self.manual_instructions:
            self.manual_instructions.setVisible(True)
        # No left-panel Clear Points button anymore
        if hasattr(self, 'clear_points_btn') and self.clear_points_btn:
            self.clear_points_btn.setVisible(False)
    
    def clear_selected_points(self):
        """Clear manually selected points"""
        self.selected_manual_points.clear()
        self.plot_focused_line()  # Refresh plot
    
    def auto_detect_contour(self):
        """Auto-detect contour points around current line"""
        if not self.available_lines or not SCIPY_AVAILABLE:
            return
        
        try:
            # Get current line info
            line_type, line_name = self.available_lines[self.current_line_index]
            line_collection = self.parent.sn_lines if line_type == 'sn' else self.parent.galaxy_lines
            obs_wavelength, line_data = line_collection[line_name]
            
            # Get spectrum data around the line
            wave = self.spectrum_data.get('wave', np.array([]))
            flux = self.spectrum_data.get('flux', np.array([]))
            
            if len(wave) == 0 or len(flux) == 0:
                return
            
            # Find region around line
            zoom_range = 150  # Fixed zoom value
            mask = (wave >= obs_wavelength - zoom_range) & (wave <= obs_wavelength + zoom_range)
            
            if not np.any(mask):
                return
            
            region_wave = wave[mask]
            region_flux = flux[mask]
            
            # Simple peak detection
            peaks, _ = signal.find_peaks(region_flux, height=np.median(region_flux))
            
            # Add detected points
            self.selected_manual_points.clear()
            for peak_idx in peaks:
                self.selected_manual_points.append((region_wave[peak_idx], region_flux[peak_idx]))
            
            self.plot_focused_line()
            
        except Exception as e:
            _LOGGER.error(f"Error in auto contour detection: {e}")
    
    # Removed point counter per simplified UI
    
    def analyze_current_line(self):
        """Analyze the currently selected line using Manual Points method"""
        if not self.available_lines:
            # Update minimal summary area when no lines
            if self.summary_text:
                self.summary_text.setPlainText("No lines available for analysis.")
            return
        
        try:
            # Get current line info
            line_type, line_name = self.available_lines[self.current_line_index]
            line_collection = self.parent.sn_lines if line_type == 'sn' else self.parent.galaxy_lines
            obs_wavelength, line_data = line_collection[line_name]
            
            # Always use Manual Points method (only method available)
            result = self.analyze_manual_points(line_name, obs_wavelength)
            
            # Store and display result
            self.line_analysis_results[line_name] = result
            self.refresh_summary()
            
        except Exception as e:
            error_msg = f"Error analyzing line: {e}"
            if self.summary_text:
                self.summary_text.setPlainText(error_msg)
            _LOGGER.error(error_msg)
    
    def analyze_manual_points(self, line_name, obs_wavelength):
        """Analyze line using manual points"""
        if not self.selected_manual_points:
            return {"error": "No manual points selected"}
        
        # Simple analysis of manual points
        # Sort by wavelength for consistent analysis
        pts = sorted(self.selected_manual_points, key=lambda p: p[0])
        wavelengths = [p[0] for p in pts]
        fluxes = [p[1] for p in pts]
        
        result = {
            "method": "Manual Points",
            "line_name": line_name,
            "observed_wavelength": obs_wavelength,
            "num_points": len(self.selected_manual_points),
            "wavelength_range": f"{min(wavelengths):.2f} - {max(wavelengths):.2f} Å",
            "flux_range": f"{min(fluxes):.3f} - {max(fluxes):.3f}",
            "peak_flux": max(fluxes),
            "peak_wavelength": wavelengths[fluxes.index(max(fluxes))]
        }

        # Attempt to compute FWHM from manual points
        fwhm_tuple = self._compute_fwhm_from_points(wavelengths, fluxes)
        if fwhm_tuple is not None:
            fwhm, left_lambda, right_lambda, half_level = fwhm_tuple
            result.update({
                'fwhm': fwhm,
                'fwhm_left': left_lambda,
                'fwhm_right': right_lambda,
                'half_max_level': half_level
            })

            # Derive velocity (km/s) using rest wavelength when available
            c_km_s = 299792.458
            rest_lambda = 0.0
            try:
                # Prefer metadata-stored rest wavelength if present
                if line_name in self.parent.sn_lines:
                    _, meta = self.parent.sn_lines.get(line_name, (None, {}))
                    rest_lambda = float(meta.get('rest_wavelength', 0.0) or 0.0)
                if rest_lambda <= 0.0 and line_name in self.parent.galaxy_lines:
                    _, meta = self.parent.galaxy_lines.get(line_name, (None, {}))
                    rest_lambda = float(meta.get('rest_wavelength', 0.0) or 0.0)
            except Exception:
                rest_lambda = 0.0
            if rest_lambda <= 0.0:
                try:
                    rest_lambda = float(self.parent._get_rest_wavelength_for_line(line_name) or 0.0)
                except Exception:
                    rest_lambda = 0.0
            # Fallback to peak wavelength, then observed wavelength
            if rest_lambda <= 0.0:
                rest_lambda = float(result.get('peak_wavelength') or 0.0) or float(result.get('observed_wavelength') or 0.0) or 0.0
            if rest_lambda > 0.0 and fwhm is not None:
                try:
                    velocity_kms = c_km_s * (float(fwhm) / float(rest_lambda))
                    result['velocity_kms'] = float(velocity_kms)
                except Exception:
                    pass
        
        return result
    
    def analyze_auto_detection(self, line_name, obs_wavelength):
        """Analyze line using auto detection"""
        return {
            "method": "Auto Detection",
            "line_name": line_name,
            "observed_wavelength": obs_wavelength,
            "status": "Not implemented yet"
        }
    
    def analyze_gaussian_fit(self, line_name, obs_wavelength):
        """Analyze line using Gaussian fitting"""
        return {
            "method": "Gaussian Fit",
            "line_name": line_name,
            "observed_wavelength": obs_wavelength,
            "status": "Not implemented yet"
        }
    
    def analyze_empirical(self, line_name, obs_wavelength):
        """Analyze line using empirical methods"""
        return {
            "method": "Empirical Analysis",
            "line_name": line_name,
            "observed_wavelength": obs_wavelength,
            "status": "Not implemented yet"
        }
    
    def _format_minimal_result_line(self, result: Dict[str, Any]) -> str:
        """Return a minimal, two-line HTML summary: bold name on first line, extracted info on second."""
        name = result.get('line_name', 'Unknown')
        if "error" in result:
            return f"<b>{name}</b><br/>Error: {result['error']}"

        observed_wavelength = result.get('observed_wavelength')
        fwhm_value = result.get('fwhm') or result.get('FWHM')
        velocity_value = result.get('velocity_kms') or result.get('fwhm_vel')
        peak_wavelength = result.get('peak_wavelength')
        num_points = result.get('num_points')

        details_parts = []
        if observed_wavelength is not None:
            try:
                details_parts.append(f"λobs={float(observed_wavelength):.2f} Å")
            except Exception:
                details_parts.append(f"λobs={observed_wavelength}")

        if velocity_value is not None:
            try:
                details_parts.append(f"v={float(velocity_value):.0f} km/s")
            except Exception:
                details_parts.append(f"v={velocity_value} km/s")
        elif fwhm_value is not None:
            try:
                details_parts.append(f"FWHM={float(fwhm_value):.2f} Å")
            except Exception:
                details_parts.append(f"FWHM={fwhm_value} Å")
        elif peak_wavelength is not None:
            try:
                details_parts.append(f"peak={float(peak_wavelength):.2f} Å")
            except Exception:
                details_parts.append(f"peak={peak_wavelength} Å")
        elif num_points is not None:
            details_parts.append(f"points={num_points}")

        details_line = ", ".join(details_parts) if details_parts else "No details available"
        return f"<b>{name}</b><br/>{details_line}"
    
    def copy_summary(self):
        """Copy summary to clipboard"""
        QtWidgets.QApplication.clipboard().setText(self.summary_text.toPlainText())
    
    def refresh_summary(self):
        """Refresh the analysis summary"""
        if not self.summary_text:
            return
        if not self.line_analysis_results:
            self.summary_text.setPlainText("No analysis results yet.")
            return
        lines = []
        for _, result in self.line_analysis_results.items():
            lines.append(self._format_minimal_result_line(result))
        # Enable rich text to allow bold name on first line and details on second
        self.summary_text.setHtml("<br/>".join(lines))

    def _compute_fwhm_from_points(self, wavelengths: List[float], fluxes: List[float]):
        """Compute FWHM from ordered points using linear interpolation at half maximum.

        Returns tuple (fwhm, left_lambda, right_lambda, half_level) or None if not derivable.
        """
        try:
            # Require a minimum number of points for stability
            if len(wavelengths) < 5:
                return None
            # Ensure strictly increasing by sorting (callers already sort, but keep safe)
            pts = sorted(zip(wavelengths, fluxes), key=lambda p: p[0])
            w = [p[0] for p in pts]
            f = [p[1] for p in pts]
            # Estimate baseline (continuum) from edges
            if len(f) >= 4:
                edge_vals = [f[0], f[1], f[-2], f[-1]]
            else:
                edge_vals = [f[0], f[-1]]
            baseline = float(np.median(edge_vals))

            # Determine if feature is emission (peak above baseline) or absorption (trough below)
            max_flux = float(np.max(f))
            min_flux = float(np.min(f))
            is_emission = (max_flux - baseline) >= (baseline - min_flux)

            # Choose central index and compute half level
            center_idx = int(np.argmax(f)) if is_emission else int(np.argmin(f))
            center_flux = f[center_idx]
            if is_emission:
                half = baseline + 0.5 * (center_flux - baseline)
            else:
                half = baseline - 0.5 * (baseline - center_flux)

            # Left crossing
            li = center_idx
            while li > 0 and ((f[li] > half) if is_emission else (f[li] < half)):
                li -= 1
            if li == center_idx:
                return None
            left_lambda = w[li]
            if f[li] != f[li + 1]:
                # Interpolate between li and li+1 (li is below/at half after loop)
                x0, x1 = w[li], w[li + 1]
                y0, y1 = f[li], f[li + 1]
                left_lambda = x0 + (half - y0) * (x1 - x0) / (y1 - y0)

            # Right crossing
            ri = center_idx
            while ri < len(f) - 1 and ((f[ri] > half) if is_emission else (f[ri] < half)):
                ri += 1
            if ri == center_idx:
                return None
            right_lambda = w[ri]
            if f[ri] != f[ri - 1]:
                x0, x1 = w[ri - 1], w[ri]
                y0, y1 = f[ri - 1], f[ri]
                right_lambda = x0 + (half - y0) * (x1 - x0) / (y1 - y0)

            fwhm = float(max(0.0, right_lambda - left_lambda))
            return (fwhm, left_lambda, right_lambda, half)
        except Exception:
            return None
    
    def export_results(self):
        """Export analysis results to file"""
        if not self.line_analysis_results:
            QtWidgets.QMessageBox.information(
                self.parent, "No Results",
                "No analysis results to export."
            )
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.parent,
            "Export Analysis Results",
            "emission_line_analysis.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("Emission Line Analysis Results\n")
                    f.write("=" * 40 + "\n\n")
                    
                    for line_name, result in self.line_analysis_results.items():
                        f.write(f"Line: {line_name}\n")
                        for key, value in result.items():
                            if key != 'line_name':
                                f.write(f"  {key}: {value}\n")
                        f.write("\n")
                
                QtWidgets.QMessageBox.information(
                    self.parent, "Export Complete",
                    f"Results exported to:\n{file_path}"
                )
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.parent, "Export Error",
                    f"Failed to export results:\n{str(e)}"
                )
    
    def plot_focused_line(self):
        """Plot focused view of current line with fixed zoom value of 150"""
        if not PYQTGRAPH_AVAILABLE or not self.parent.plot_item or not self.available_lines:
            return
        
        try:
            # Get current line info
            line_type, line_name = self.available_lines[self.current_line_index]
            line_collection = self.parent.sn_lines if line_type == 'sn' else self.parent.galaxy_lines
            obs_wavelength, line_data = line_collection[line_name]
            
            # Fixed zoom value of 150 Å
            zoom_range = 150
            
            # Get spectrum data
            wave = self.spectrum_data.get('wave', np.array([]))
            flux = self.spectrum_data.get('flux', np.array([]))
            
            if len(wave) == 0 or len(flux) == 0:
                return
            
            # Clear and start fresh plot
            self.parent.plot_item.clear()
            
            # Always plot the full spectrum first (in light gray)
            self.parent.plot_item.plot(wave, flux, pen=pg.mkPen(color='lightgray', width=1), name='Full Spectrum')
            
            # Create focused plot region mask
            mask = (wave >= obs_wavelength - zoom_range) & (wave <= obs_wavelength + zoom_range)
            
            if np.any(mask):
                # Plot focused region in darker color
                focused_wave = wave[mask]
                focused_flux = flux[mask]
                self.parent.plot_item.plot(focused_wave, focused_flux, pen=pg.mkPen(color='black', width=2), name='Focused Region')
                
                # Set view range to focused area
                self.parent.plot_widget.setXRange(obs_wavelength - zoom_range, obs_wavelength + zoom_range)
                
                # Set Y range to focused region with some padding
                if len(focused_flux) > 0:
                    flux_min, flux_max = np.min(focused_flux), np.max(focused_flux)
                    flux_padding = (flux_max - flux_min) * 0.1
                    self.parent.plot_widget.setYRange(flux_min - flux_padding, flux_max + flux_padding)
            
            # Plot the central line marker
            line_color = 'red' if line_type == 'sn' else 'blue'
            line_marker = pg.InfiniteLine(
                pos=obs_wavelength,
                angle=90,
                pen=pg.mkPen(color=line_color, width=3),
                label=line_name
            )
            self.parent.plot_item.addItem(line_marker)
            
            # Plot manual points if any, and connect them by lines
            if self.selected_manual_points:
                # Sort by wavelength to connect in order
                pts = sorted(self.selected_manual_points, key=lambda p: p[0])
                point_waves = [p[0] for p in pts]
                point_fluxes = [p[1] for p in pts]
                # Line connecting the points
                self.parent.plot_item.plot(
                    point_waves,
                    point_fluxes,
                    pen=pg.mkPen(color='orange', width=2, style=QtCore.Qt.SolidLine),
                    name='Manual Points Path'
                )
                # Scatter markers on top
                scatter = pg.ScatterPlotItem(
                    x=point_waves,
                    y=point_fluxes,
                    size=8,
                    brush='orange',
                    pen=pg.mkPen(color='red', width=1)
                )
                self.parent.plot_item.addItem(scatter)

                # Compute FWHM from points for immediate visual feedback (require >=5 points)
                fwhm_tuple = None
                if len(point_waves) >= 5:
                    fwhm_tuple = self._compute_fwhm_from_points(point_waves, point_fluxes)
                if fwhm_tuple is not None:
                    fwhm, left_lambda, right_lambda, half_level = fwhm_tuple
                    # Draw horizontal FWHM line segment at half-max between left and right
                    self.parent.plot_item.plot(
                        [left_lambda, right_lambda],
                        [half_level, half_level],
                        pen=pg.mkPen(color=(0, 150, 0), width=2, style=QtCore.Qt.DashLine),
                        name='FWHM'
                    )
                    # Stash into latest result if it exists
                    if self.available_lines:
                        lt, ln = self.available_lines[self.current_line_index]
                        if ln in self.line_analysis_results:
                            self.line_analysis_results[ln]['fwhm'] = fwhm
                            self.line_analysis_results[ln]['fwhm_left'] = left_lambda
                            self.line_analysis_results[ln]['fwhm_right'] = right_lambda
                            self.line_analysis_results[ln]['half_max_level'] = half_level
                            # Compute and store velocity (km/s) using rest wavelength when available
                            try:
                                c_km_s = 299792.458
                                rest_lambda = 0.0
                                # Prefer metadata-stored rest wavelength
                                if lt == 'sn' and ln in self.parent.sn_lines:
                                    _, meta = self.parent.sn_lines.get(ln, (None, {}))
                                    rest_lambda = float(meta.get('rest_wavelength', 0.0) or 0.0)
                                if rest_lambda <= 0.0 and lt == 'galaxy' and ln in self.parent.galaxy_lines:
                                    _, meta = self.parent.galaxy_lines.get(ln, (None, {}))
                                    rest_lambda = float(meta.get('rest_wavelength', 0.0) or 0.0)
                                if rest_lambda <= 0.0:
                                    rest_lambda = float(self.parent._get_rest_wavelength_for_line(ln) or 0.0)
                                if rest_lambda <= 0.0:
                                    rest_lambda = float(self.line_analysis_results[ln].get('peak_wavelength') or 0.0) or float(self.line_analysis_results[ln].get('observed_wavelength') or 0.0) or 0.0
                                if rest_lambda > 0.0:
                                    self.line_analysis_results[ln]['velocity_kms'] = float(c_km_s * (float(fwhm) / rest_lambda))
                            except Exception:
                                pass
                        # Refresh minimal summary to reflect velocity quickly
                        self.refresh_summary()
            
        except Exception as e:
            _LOGGER.error(f"Error plotting focused line: {e}") 