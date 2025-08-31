"""
Centralized plot theming utilities for SNID SAGE.

This module provides comprehensive theming support for matplotlib plots,
ensuring consistent visual appearance across light and dark modes.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from typing import Dict, Optional, Tuple, Any, Union
import numpy as np

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('shared.plotting')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('shared.plotting')

# Import centralized font size configuration
try:
    from snid_sage.shared.utils.plotting.font_sizes import get_font_config
    FONT_CONFIG = get_font_config()
except ImportError:
    # Fallback font configuration
    FONT_CONFIG = {
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 11,
    }


class ThemePlotManager:
    """Centralized plot theming manager for consistent matplotlib styling"""
    
    def __init__(self, theme_manager=None):
        """Initialize with optional theme manager reference"""
        self.theme_manager = theme_manager
        self._default_colors = self._get_default_colors()
    
    def _get_default_colors(self) -> Dict[str, Dict[str, str]]:
        """Get default color schemes when theme manager is not available"""
        return {
            'light': {
                'plot_bg': '#ffffff',
                'plot_text': '#000000',
                'plot_grid': '#cbd5e1',
                'plot_line': '#1f77b4',
                'plot_accent': '#667eea',
                'bg_secondary': '#f8fafc',
                'border': '#cbd5e1'
            },
            'dark': {
                'plot_bg': '#1e293b',
                'plot_text': '#f8fafc',
                'plot_grid': '#475569',
                'plot_line': '#4da6ff',
                'plot_accent': '#6366f1',
                'bg_secondary': '#334155',
                'border': '#475569'
            }
        }
    
    def get_current_colors(self) -> Dict[str, str]:
        """Get current theme colors, with fallback to defaults"""
        if self.theme_manager:
            try:
                return self.theme_manager.get_current_colors()
            except:
                pass
        
        # Fallback to default light theme
        return self._default_colors['light']
    
    def is_dark_mode(self) -> bool:
        """Check if current theme is dark mode"""
        if self.theme_manager:
            try:
                return self.theme_manager.is_dark_mode()
            except:
                pass
        return False
    
    def setup_global_theme(self, force_theme: str = None):
        """Setup global matplotlib theme"""
        if force_theme:
            colors = self._default_colors.get(force_theme, self._default_colors['light'])
        else:
            colors = self.get_current_colors()
        
        # Clear any existing styles
        plt.rcdefaults()
        
        # Comprehensive matplotlib parameters
        mpl_params = {
            # Figure and axes backgrounds
            'figure.facecolor': colors['plot_bg'],
            'axes.facecolor': colors['plot_bg'],
            'savefig.facecolor': colors['plot_bg'],
            
            # Text colors
            'axes.edgecolor': colors['plot_grid'],
            'axes.labelcolor': colors['plot_text'],
            'text.color': colors['plot_text'],
            'xtick.color': colors['plot_text'],
            'ytick.color': colors['plot_text'],
            'xtick.labelcolor': colors['plot_text'],
            'ytick.labelcolor': colors['plot_text'],
            
            # Grid styling
            'grid.color': colors['plot_grid'],
            'grid.alpha': 0.08,
            'grid.linestyle': '-',
            'grid.linewidth': 0.5,
            'axes.axisbelow': True,
            
            # Spines
            'axes.spines.left': True,
            'axes.spines.bottom': True,
            'axes.spines.top': False,
            'axes.spines.right': False,
            
            # Legend styling
            'legend.facecolor': colors['plot_bg'],
            'legend.edgecolor': colors['plot_grid'],
            'legend.frameon': True,
            'legend.framealpha': 0.9,
            
            # Line and patch colors
            'lines.color': colors['plot_line'],
            'patch.edgecolor': colors['plot_grid'],
            
            # Font settings - standardized across all plots
            **FONT_CONFIG
        }
        
        # Apply parameters
        plt.rcParams.update(mpl_params)
        mpl.rcParams.update(mpl_params)
        
        # Set theme-appropriate color cycle
        if self.is_dark_mode() or force_theme == 'dark':
            color_cycle = ['#4da6ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#fd79a8', '#6c5ce7']
        else:
            color_cycle = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        plt.rcParams['axes.prop_cycle'] = plt.cycler('color', color_cycle)
        
        _LOGGER.debug(f"🎨 Applied global matplotlib theme: {force_theme or 'auto'}")


# Global theme manager instance
_theme_plot_manager = ThemePlotManager()


def setup_plot_theme(theme_manager=None, force_theme: str = None):
    """
    Setup matplotlib theme globally
    
    Args:
        theme_manager: GUI theme manager instance
        force_theme: Force specific theme ('light' or 'dark')
    """
    global _theme_plot_manager
    if theme_manager:
        _theme_plot_manager.theme_manager = theme_manager
    
    _theme_plot_manager.setup_global_theme(force_theme)


def get_themed_colors(theme_manager=None) -> Dict[str, str]:
    """
    Get current theme colors
    
    Args:
        theme_manager: Optional theme manager instance
        
    Returns:
        Dictionary of theme colors
    """
    global _theme_plot_manager
    if theme_manager:
        _theme_plot_manager.theme_manager = theme_manager
    
    return _theme_plot_manager.get_current_colors()


def create_themed_figure(figsize: Tuple[float, float] = (10, 6), 
                        theme_manager=None,
                        **kwargs) -> Tuple[Figure, plt.Axes]:
    """
    Create a matplotlib figure with proper theming
    
    Args:
        figsize: Figure size (width, height)
        theme_manager: Optional theme manager instance
        **kwargs: Additional arguments for plt.subplots
        
    Returns:
        Tuple of (figure, axes)
    """
    global _theme_plot_manager
    if theme_manager:
        _theme_plot_manager.theme_manager = theme_manager
    
    colors = _theme_plot_manager.get_current_colors()
    
    # Create figure with themed colors
    fig, ax = plt.subplots(figsize=figsize, 
                          facecolor=colors['plot_bg'], 
                          **kwargs)
    
    # Apply theming
    apply_theme_to_plot(fig, ax, theme_manager)
    
    return fig, ax


def apply_theme_to_plot(fig: Figure, ax: plt.Axes, theme_manager=None):
    """
    Apply current theme to an existing matplotlib plot
    
    Args:
        fig: Matplotlib figure
        ax: Matplotlib axes
        theme_manager: Optional theme manager instance
    """
    global _theme_plot_manager
    if theme_manager:
        _theme_plot_manager.theme_manager = theme_manager
    
    colors = _theme_plot_manager.get_current_colors()
    
    try:
        # Update figure and axes backgrounds
        fig.patch.set_facecolor(colors['plot_bg'])
        ax.set_facecolor(colors['plot_bg'])
        
        # Update text elements
        ax.tick_params(colors=colors['plot_text'], labelcolor=colors['plot_text'])
        ax.xaxis.label.set_color(colors['plot_text'])
        ax.yaxis.label.set_color(colors['plot_text'])
        ax.title.set_color(colors['plot_text'])
        
        # Update tick labels explicitly
        plt.setp(ax.get_xticklabels(), color=colors['plot_text'])
        plt.setp(ax.get_yticklabels(), color=colors['plot_text'])
        
        # Update grid
        ax.grid(True, alpha=0.3, color=colors['plot_grid'], linestyle='-', linewidth=0.5)
        
        # Update spines
        for spine in ax.spines.values():
            spine.set_color(colors['plot_grid'])
            spine.set_linewidth(0.8)
        
        # Hide top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Update legend if present
        legend = ax.get_legend()
        if legend:
            legend.get_frame().set_facecolor(colors['plot_bg'])
            legend.get_frame().set_edgecolor(colors['plot_grid'])
            legend.get_frame().set_alpha(0.9)
            legend.get_frame().set_linewidth(0.5)
            for text in legend.get_texts():
                text.set_color(colors['plot_text'])
        
        # Update text annotations
        for text in ax.texts:
            # Only update if it's a default black/white color
            if text.get_color() in ['black', 'white', '#000000', '#ffffff', (0,0,0,1), (1,1,1,1)]:
                text.set_color(colors['plot_text'])
        
    except Exception as e:
        _LOGGER.warning(f"Warning: Could not fully apply theme to plot: {e}")


def create_themed_bbox(style: str = 'round', alpha: float = 0.8, 
                      pad: float = 0.3, theme_manager=None) -> Dict[str, Any]:
    """
    Create a theme-aware bounding box for text annotations
    
    Args:
        style: Box style ('round', 'square', etc.)
        alpha: Transparency
        pad: Padding
        theme_manager: Optional theme manager instance
        
    Returns:
        Dictionary with bbox properties
    """
    global _theme_plot_manager
    if theme_manager:
        _theme_plot_manager.theme_manager = theme_manager
    
    colors = _theme_plot_manager.get_current_colors()
    
    return dict(
        boxstyle=f"{style},pad={pad}",
        facecolor=colors.get('bg_secondary', '#f8fafc'),
        edgecolor=colors.get('border', '#cbd5e1'),
        alpha=alpha,
        linewidth=0.5
    )


def fix_hardcoded_colors_in_plot(fig: Figure, ax: plt.Axes, theme_manager=None):
    """
    Fix hardcoded colors in existing plots to be theme-aware
    
    Args:
        fig: Matplotlib figure
        ax: Matplotlib axes  
        theme_manager: Optional theme manager instance
    """
    global _theme_plot_manager
    if theme_manager:
        _theme_plot_manager.theme_manager = theme_manager
    
    colors = _theme_plot_manager.get_current_colors()
    is_dark = _theme_plot_manager.is_dark_mode()
    
    try:
        # Map of hardcoded colors to theme-aware alternatives
        color_mapping = {
            'white': colors['plot_bg'],
            '#ffffff': colors['plot_bg'],
            'black': colors['plot_text'],
            '#000000': colors['plot_text'],
            'lightblue': colors['plot_accent'] if not is_dark else '#64b5f6',
            'lightgreen': '#4caf50' if not is_dark else '#81c784',
            'lightyellow': '#ffeb3b' if not is_dark else '#fff176',
            'lightcyan': '#00bcd4' if not is_dark else '#4dd0e1',
            'lightgray': colors['plot_grid'],
            'gray': colors['plot_grid'],
            'grey': colors['plot_grid'],
        }
        
        # Update line colors
        for line in ax.get_lines():
            color = line.get_color()
            if color in color_mapping:
                line.set_color(color_mapping[color])
        
        # Update text annotations with hardcoded colors
        for text in ax.texts:
            # Check if text has a bbox with hardcoded colors
            bbox = text.get_bbox_patch()
            if bbox:
                face_color = bbox.get_facecolor()
                if face_color in color_mapping:
                    bbox.set_facecolor(color_mapping[face_color])
                    bbox.set_edgecolor(colors['border'])
        
        _LOGGER.debug("🎨 Fixed hardcoded colors in plot")
        
    except Exception as e:
        _LOGGER.warning(f"Warning: Could not fix all hardcoded colors: {e}")


def create_themed_annotation(ax: plt.Axes, text: str, xy: Tuple[float, float],
                           xytext: Optional[Tuple[float, float]] = None,
                           theme_manager=None, **kwargs) -> plt.Annotation:
    """
    Create a theme-aware annotation
    
    Args:
        ax: Matplotlib axes
        text: Annotation text
        xy: Point to annotate
        xytext: Text position (optional)
        theme_manager: Optional theme manager instance
        **kwargs: Additional annotation arguments
        
    Returns:
        Matplotlib annotation object
    """
    global _theme_plot_manager
    if theme_manager:
        _theme_plot_manager.theme_manager = theme_manager
    
    colors = _theme_plot_manager.get_current_colors()
    
    # Set default theme-aware styling
    default_kwargs = {
        'color': colors['plot_text'],
        'bbox': create_themed_bbox(theme_manager=theme_manager),
        'fontsize': 10,
        'ha': 'center',
        'va': 'center'
    }
    
    # Merge with user kwargs (user takes precedence)
    final_kwargs = {**default_kwargs, **kwargs}
    
    if xytext:
        final_kwargs['xytext'] = xytext
        if 'arrowprops' not in final_kwargs:
            final_kwargs['arrowprops'] = dict(
                arrowstyle='->',
                color=colors['plot_text'],
                alpha=0.7
            )
    
    return ax.annotate(text, xy, **final_kwargs)


def create_plot_with_proper_theming(figsize: Tuple[float, float] = (10, 6), 
                                   theme_manager=None, **kwargs) -> Tuple[Figure, plt.Axes]:
    """
    Create a matplotlib figure with guaranteed proper theming.
    
    This function ensures consistent plot backgrounds regardless of which
    theme system is being used.
    """
    # Get current colors from theme manager
    if theme_manager:
        colors = theme_manager.get_current_colors()
        plot_bg = colors.get('plot_bg', '#ffffff')
        plot_text = colors.get('plot_text', '#000000')
        plot_grid = colors.get('plot_grid', '#cccccc')
    else:
        # Fallback colors
        plot_bg = '#ffffff'
        plot_text = '#000000'
        plot_grid = '#cccccc'
    
    # Create figure with explicit background
    fig, ax = plt.subplots(figsize=figsize, facecolor=plot_bg, **kwargs)
    
    # Set axes background
    ax.set_facecolor(plot_bg)
    
    # Apply text colors
    ax.tick_params(colors=plot_text, labelcolor=plot_text)
    
    # Set up grid
    ax.grid(True, color=plot_grid, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Hide top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Set spine colors
    for spine in ax.spines.values():
        spine.set_color(plot_grid)
    
    return fig, ax


def fix_hardcoded_plot_background(fig: Figure, ax: plt.Axes, theme_manager=None):
    """
    Fix plots that have hardcoded white backgrounds.
    
    This function can be called on any existing plot to ensure it
    respects the current theme.
    """
    if theme_manager:
        colors = theme_manager.get_current_colors()
        plot_bg = colors.get('plot_bg', '#ffffff')
        plot_text = colors.get('plot_text', '#000000')
        plot_grid = colors.get('plot_grid', '#cccccc')
        
        # Fix backgrounds
        fig.patch.set_facecolor(plot_bg)
        ax.set_facecolor(plot_bg)
        
        # Fix text colors
        ax.tick_params(colors=plot_text, labelcolor=plot_text)
        if hasattr(ax, 'xaxis') and ax.xaxis.label:
            ax.xaxis.label.set_color(plot_text)
        if hasattr(ax, 'yaxis') and ax.yaxis.label:
            ax.yaxis.label.set_color(plot_text)
        
        # Fix grid
        ax.grid(True, color=plot_grid, alpha=0.3)
        
        # Fix spines
        for spine in ax.spines.values():
            spine.set_color(plot_grid)


def ensure_plot_theme_consistency(theme_manager=None):
    """
    Ensure all open matplotlib figures have consistent theming.
    
    This function updates all existing plots to match the current theme.
    """
    if not theme_manager:
        return
        
    try:
        colors = theme_manager.get_current_colors()
        
        for fig_num in plt.get_fignums():
            fig = plt.figure(fig_num)
            
            # Ensure figure background is correct
            fig.patch.set_facecolor(colors.get('plot_bg', '#ffffff'))
            
            for ax in fig.get_axes():
                # Apply consistent theming
                fix_hardcoded_plot_background(fig, ax, theme_manager)
            
            # Force redraw
            try:
                fig.canvas.draw_idle()
            except:
                pass
        
        _LOGGER.debug(f"🎨 Updated {len(plt.get_fignums())} matplotlib figures for theme consistency")
        
    except Exception as e:
        _LOGGER.warning(f"Error ensuring plot theme consistency: {e}") 