"""
Shared plotting utilities with comprehensive theme support.

This module provides theme-aware plotting functions and utilities
that work consistently across all SNID SAGE components.
"""

from .plot_theming import (
    setup_plot_theme,
    create_themed_figure,
    apply_theme_to_plot,
    get_themed_colors,
    create_themed_bbox,
    ThemePlotManager
)

from .spectrum_utils import (
    plot_spectrum_with_lines,
    clear_plot_lines,
    show_faint_overlay_on_plot,
    clear_faint_overlay_from_plot,
    plot_focused_spectrum_region,
    plot_other_lines_in_range,
    plot_manual_points_with_contour,
    plot_fit_curve,
    style_spectrum_plot
)

__all__ = [
    'setup_plot_theme',
    'create_themed_figure', 
    'apply_theme_to_plot',
    'get_themed_colors',
    'create_themed_bbox',
    'ThemePlotManager',
    'plot_spectrum_with_lines',
    'clear_plot_lines',
    'show_faint_overlay_on_plot',
    'clear_faint_overlay_from_plot',
    'plot_focused_spectrum_region',
    'plot_other_lines_in_range',
    'plot_manual_points_with_contour',
    'plot_fit_curve',
    'style_spectrum_plot'
] 