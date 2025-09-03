"""
SNID SAGE - Spectrum Plotting Utilities
=======================================

Utilities for spectrum plotting and visualization tasks.
Part of the SNID SAGE shared utilities.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional
from snid_sage.shared.utils.line_detection import get_line_color, get_faint_overlay_lines

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('spectrum_utils')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('spectrum_utils')


def plot_spectrum_with_lines(ax, spectrum_data: Dict[str, np.ndarray], sn_lines: Dict = None, 
                            galaxy_lines: Dict = None, line_colors: Dict = None):
    """Plot spectrum with emission line overlays"""
    if sn_lines is None:
        sn_lines = {}
    if galaxy_lines is None:
        galaxy_lines = {}
        
    # Plot spectrum (keep in observed wavelengths - lines will be redshifted to match)
    wavelength = spectrum_data['wavelength']
    flux = spectrum_data['flux']
    
    ax.plot(wavelength, flux, 'k-', linewidth=1, alpha=0.8)
    
    # Plot SN lines (solid lines)
    for line_name, (obs_wavelength, line_data) in sn_lines.items():
        color = get_line_color(line_data, 'sn')
        
        # Vertical line
        line = ax.axvline(obs_wavelength, color=color, linestyle='-', 
                         alpha=0.7, linewidth=2)
        line._emission_line = True
        
        # Label
        y_pos = ax.get_ylim()[1] * 0.9
        text = ax.text(obs_wavelength, y_pos, line_name, 
                      rotation=90, ha='right', va='top', 
                      color=color, fontsize=10, weight='bold', alpha=0.9)
        text._emission_label = True
    
    # Plot galaxy lines (dashed lines)
    for line_name, (obs_wavelength, line_data) in galaxy_lines.items():
        color = get_line_color(line_data, 'galaxy')
        
        # Vertical line
        line = ax.axvline(obs_wavelength, color=color, linestyle='--', 
                         alpha=0.6, linewidth=2)
        line._emission_line = True
        
        # Label
        y_pos = ax.get_ylim()[1] * 0.8
        text = ax.text(obs_wavelength, y_pos, line_name, 
                      rotation=90, ha='right', va='top', 
                      color=color, fontsize=10, weight='bold', alpha=0.9)
        text._emission_label = True


def clear_plot_lines(ax):
    """Remove existing line markers and labels from plot"""
    # Remove existing line markers and labels
    lines_to_remove = [line for line in ax.lines if hasattr(line, '_emission_line')]
    for line in lines_to_remove:
        line.remove()
    
    texts_to_remove = [text for text in ax.texts if hasattr(text, '_emission_label')]
    for text in texts_to_remove:
        text.remove()


def show_faint_overlay_on_plot(ax, current_mode: str, current_redshift: float, 
                              spectrum_data: Dict[str, np.ndarray], sn_lines: Dict, 
                              galaxy_lines: Dict, alpha: float = 0.45) -> Dict[str, Any]:
    """Show all available lines in very faint colors as overlay"""
    faint_line_artists = {}
    
    try:
        # Get faint overlay lines
        faint_lines = get_faint_overlay_lines(current_mode, current_redshift, spectrum_data, 
                                             sn_lines, galaxy_lines)
        
        # Draw faint lines
        for line_name, obs_wavelength in faint_lines.items():
            # Get line data for color
            from snid_sage.shared.constants.physical import SUPERNOVA_EMISSION_LINES
            line_data = SUPERNOVA_EMISSION_LINES.get(line_name, {})
            color = get_line_color(line_data, current_mode)
            
            # Moderately visible line for better visibility
            faint_line = ax.axvline(obs_wavelength, color=color, 
                                  linestyle=':', linewidth=1, alpha=alpha, zorder=0)
            
            faint_line_artists[line_name] = faint_line
        
    except Exception as e:
        _LOGGER.error(f"Error showing faint overlay: {e}")
    
    return faint_line_artists


def clear_faint_overlay_from_plot(faint_line_artists: Dict[str, Any]):
    """Clear the faint overlay lines from plot"""
    try:
        for line_artist in faint_line_artists.values():
            if line_artist:
                line_artist.remove()
        faint_line_artists.clear()
    except Exception as e:
        _LOGGER.error(f"Error clearing faint overlay: {e}")


def plot_focused_spectrum_region(ax, spectrum_data: Dict[str, np.ndarray], 
                                center_wavelength: float, zoom_range: float = 30.0,
                                line_name: str = None, line_data: Dict = None, 
                                line_origin: str = 'sn'):
    """Plot spectrum focused on a specific wavelength region"""
    # Calculate wavelength range
    wl_min = center_wavelength - zoom_range
    wl_max = center_wavelength + zoom_range
    
    # Get spectrum data
    wavelength = spectrum_data['wavelength']
    flux = spectrum_data['flux']
    
    # Filter to zoom range
    mask = (wavelength >= wl_min) & (wavelength <= wl_max)
    wl_zoom = wavelength[mask]
    flux_zoom = flux[mask]
    
    if len(wl_zoom) == 0:
        # No data in range, show message
        ax.text(0.5, 0.5, f"No spectrum data in range\n{wl_min:.1f} - {wl_max:.1f} Å",
               transform=ax.transAxes, ha='center', va='center',
               fontsize=14, color='red')
        return False
    
    # Plot spectrum in zoom range
    ax.plot(wl_zoom, flux_zoom, 'k-', linewidth=1.5, alpha=0.8)
    
    # Highlight the center line if provided
    if line_name and line_data:
        color = get_line_color(line_data, line_origin)
        ax.axvline(center_wavelength, color=color, linestyle='-', 
                  alpha=0.9, linewidth=3, label=line_name)
    
    return True


def plot_other_lines_in_range(ax, available_lines: List[str], sn_lines: Dict, galaxy_lines: Dict,
                              wl_min: float, wl_max: float, exclude_line: str = None):
    """Plot other lines that fall within the current zoom range"""
    for line_name in available_lines:
        if line_name == exclude_line:
            continue
            
        # Get line info
        if line_name in sn_lines:
            obs_wavelength, line_data = sn_lines[line_name]
            line_origin = 'sn'
        elif line_name in galaxy_lines:
            obs_wavelength, line_data = galaxy_lines[line_name]
            line_origin = 'galaxy'
        else:
            continue
        
        if wl_min <= obs_wavelength <= wl_max:
            color = get_line_color(line_data, line_origin)
            linestyle = '-' if line_origin == 'sn' else '--'
            alpha = 0.6
            
            ax.axvline(obs_wavelength, color=color, linestyle=linestyle, 
                      alpha=alpha, linewidth=2, label=line_name)


def plot_manual_points_with_contour(ax, selected_manual_points: List[Tuple[float, float]], 
                                   wl_min: float, wl_max: float):
    """Plot manual points with enhanced visualization and connecting contour"""
    if not selected_manual_points:
        return
        
    # Show selected manual points with enhanced visualization
    visible_points = [(x, y) for x, y in selected_manual_points if wl_min <= x <= wl_max]
    
    if not visible_points:
        return
        
    # Sort points by wavelength for connecting lines
    visible_points.sort(key=lambda p: p[0])
    x_points = [p[0] for p in visible_points]
    y_points = [p[1] for p in visible_points]
    
    # Draw connecting lines between points to show peak contour
    if len(visible_points) > 1:
        ax.plot(x_points, y_points, 'r--', linewidth=2, alpha=0.6, 
               label='Manual Contour')
    
    # Draw individual points with enhanced styling
    for i, (x, y) in enumerate(visible_points):
        # Use different colors/shapes for different types of points
        if i == 0 or i == len(visible_points) - 1:
            # Boundary points - square markers
            ax.plot(x, y, 'rs', markersize=10, alpha=0.8, 
                   markeredgecolor='darkred', markeredgewidth=2)
        else:
            # Peak/interior points - circle markers  
            ax.plot(x, y, 'ro', markersize=10, alpha=0.8,
                   markeredgecolor='darkred', markeredgewidth=2)


def plot_fit_curve(ax, line_fit_results: Dict, current_line_name: str, wl_min: float, wl_max: float):
    """Plot fit curve if available for the current line"""
    if current_line_name not in line_fit_results:
        return
        
    fit_data = line_fit_results[current_line_name]
    fit_wl = fit_data['fit_wavelength']
    fit_flux = fit_data['fit_flux']
    
    # Filter fit curve to visible range
    fit_mask = (fit_wl >= wl_min) & (fit_wl <= wl_max)
    if not np.any(fit_mask):
        return
        
    fit_wl_visible = fit_wl[fit_mask]
    fit_flux_visible = fit_flux[fit_mask]
    
    # Choose color based on fit method
    fit_color = '#00aa00' if fit_data['method'] == 'gaussian' else '#0066cc'
    fit_label = f"{fit_data['method'].title()} Fit"
    
    ax.plot(fit_wl_visible, fit_flux_visible, 
           color=fit_color, linewidth=3, alpha=0.8,
           label=fit_label, linestyle='-')


def style_spectrum_plot(ax, title: str = None, show_legend: bool = True):
    """Apply consistent styling to spectrum plots"""
    # Styling
    ax.set_xlabel('Wavelength (Å)', color='black', fontsize=12)
    ax.set_ylabel('Flux', color='black', fontsize=12)
    ax.tick_params(colors='black')
    ax.grid(True, alpha=0.3)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Add legend if there are multiple lines and requested
    if show_legend and len(ax.get_lines()) > 1:
        ax.legend(fontsize=10, loc='upper right') 