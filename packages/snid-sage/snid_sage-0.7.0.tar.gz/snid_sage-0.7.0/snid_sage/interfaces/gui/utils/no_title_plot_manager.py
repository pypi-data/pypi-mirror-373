"""
SNID SAGE No-Title Plot Manager
==============================

Provides consistent plot styling without titles and optimizes space usage:
- Removes all plot titles and reclaims title space
- Implements consistent plot styling across all GUI plots
- Theme-aware plot appearance with proper spacing
- Matplotlib configuration optimization for GUI usage
- Font management integration for plot text elements

This ensures all GUI plots are clean, consistent, and maximize data visualization space.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, Dict, Any, Union, Tuple
import numpy as np

# Import font management (optional; the module may be removed during Tk cleanup)
try:
    from .unified_font_manager import get_font_manager, FontCategory
    FONT_MANAGER_AVAILABLE = True
except Exception:
    FONT_MANAGER_AVAILABLE = False

# Import centralized logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.plots')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.plots')


class NoTitlePlotManager:
    """
    Manager for creating clean, title-less plots optimized for GUI display.
    
    This class ensures all GUI plots have consistent styling without titles,
    proper spacing optimization, and theme-aware appearance.
    """
    
    def __init__(self, theme_manager=None):
        """
        Initialize the plot manager
        
        Args:
            theme_manager: Optional theme manager for color coordination
        """
        self.theme_manager = theme_manager
        self.font_manager = get_font_manager() if FONT_MANAGER_AVAILABLE else None
        
        # Setup matplotlib parameters for GUI optimization
        self._setup_matplotlib_defaults()
        
        _LOGGER.debug("🎨 No-Title Plot Manager initialized")
    
    def _setup_matplotlib_defaults(self):
        """Setup matplotlib defaults optimized for GUI plots without titles"""
        # Font and text settings with proper scaling
        if self.font_manager:
            axis_font = self.font_manager.get_matplotlib_font_dict(FontCategory.PLOT_AXIS)
            legend_font = self.font_manager.get_matplotlib_font_dict(FontCategory.PLOT_LEGEND)
            
            mpl.rcParams.update({
                'font.family': axis_font['family'],
                'font.size': axis_font['size'],
                'axes.labelsize': axis_font['size'] + 2,        # Axis label font
                'xtick.labelsize': axis_font['size'] + 2,       # X-tick font (larger)
                'ytick.labelsize': axis_font['size'] + 2,       # Y-tick font (larger)
                'legend.fontsize': legend_font['size'] + 2,     # Legend font
                # Grid styling – faint light-gray
                'grid.color': '#cccccc',
            })
        else:
            # Fallback sizes when font manager unavailable
            mpl.rcParams.update({
                'font.size': 14,
                'axes.labelsize': 16,
                'xtick.labelsize': 15,
                'ytick.labelsize': 15,
                'legend.fontsize': 15,
                # Grid styling – faint light-gray
                'grid.color': '#cccccc',
            })
        
        # Title settings - minimize space allocation
        mpl.rcParams.update({
            'axes.titlesize': 0,           # Effectively disable titles
            'axes.titlepad': 0,            # No padding for titles
            'figure.titlesize': 0,         # No figure titles
        })
        
        # Layout optimization for maximum plot area
        mpl.rcParams.update({
            'figure.subplot.top': 0.95,    # Minimize top margin
            'figure.subplot.bottom': 0.12, # Space for x-axis labels
            'figure.subplot.left': 0.12,   # Space for y-axis labels  
            'figure.subplot.right': 0.95,  # Minimize right margin
            'figure.subplot.hspace': 0.3,  # Reasonable spacing between subplots
            'figure.subplot.wspace': 0.3,  # Reasonable spacing between subplots
        })
        
        # Grid and styling
        mpl.rcParams.update({
            'axes.grid': True,
            'grid.alpha': 0.08,
            'grid.linewidth': 0.5,
            'axes.axisbelow': True,        # Grid behind data
        })
    
    def create_figure(self, figsize: Tuple[float, float] = (10, 6), 
                     dpi: Optional[int] = None) -> Tuple[Figure, Axes]:
        """
        Create a new figure optimized for GUI display without titles
        
        Args:
            figsize: Figure size in inches
            dpi: Optional DPI override
            
        Returns:
            Tuple of (figure, axes) objects
        """
        # Use theme-aware DPI if available
        if dpi is None:
            dpi = 100  # Good default for GUI
        
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        
        # Apply no-title styling
        self.apply_no_title_styling(fig, ax)
        
        return fig, ax
    
    def apply_no_title_styling(self, fig: Figure, ax: Union[Axes, np.ndarray], 
                              xlabel: str = "Wavelength (Å)", 
                              ylabel: str = "Flux"):
        """
        Apply consistent no-title styling to existing figure/axes
        
        Args:
            fig: Matplotlib figure
            ax: Matplotlib axes (single or array)
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        # Handle multiple axes
        if isinstance(ax, np.ndarray):
            axes_list = ax.flatten()
        else:
            axes_list = [ax]
        
        for single_ax in axes_list:
            # Remove title completely
            single_ax.set_title('')
            single_ax.title.set_visible(False)
            
            # Set axis labels with proper fonts
            if self.font_manager:
                axis_font_dict = self.font_manager.get_matplotlib_font_dict(FontCategory.PLOT_AXIS)
                # Increase axis label font size for clearer readability
                axis_font_dict = axis_font_dict.copy()
                axis_font_dict['size'] = axis_font_dict.get('size', 12) + 2
                single_ax.set_xlabel(xlabel, fontdict=axis_font_dict)
                single_ax.set_ylabel(ylabel, fontdict=axis_font_dict)
                
                # Explicitly enlarge tick label font sizes to match updated axis labels
                tick_font_size = axis_font_dict['size'] - 1  # Slightly smaller than axis labels
                single_ax.tick_params(axis='both', labelsize=tick_font_size)
            else:
                single_ax.set_xlabel(xlabel, fontsize=14)
                single_ax.set_ylabel(ylabel, fontsize=14)
                # Set tick label size for fallback mode
                single_ax.tick_params(axis='both', labelsize=13)
            
            # Apply theme colors if available (also reapplies grid styling)
            if self.theme_manager:
                self._apply_theme_colors(single_ax)
            else:
                # Ensure a faint grid even without theme manager (slightly higher alpha for saved PNG visibility)
                single_ax.grid(True, color='#cccccc', alpha=0.50, linestyle='-', linewidth=0.8)
            
            # Ensure grid is on with faint styling
            single_ax.grid(True, alpha=0.50, linestyle='-', linewidth=0.8)
            single_ax.set_axisbelow(True)
        
        # Optimize figure layout to reclaim title space
        fig.tight_layout(pad=0.5)  # Minimal padding
        
        # Additional space optimization
        try:
            fig.subplots_adjust(top=0.95)  # Maximize top space
        except:
            pass  # In case of layout conflicts
    
    def _apply_theme_colors(self, ax: Axes):
        """Apply theme-aware colors to axes"""
        try:
            colors = self.theme_manager.get_current_colors()
            
            # Background and face colors
            ax.set_facecolor(colors.get('plot_bg', 'white'))
            
            # Text colors
            text_color = colors.get('plot_text', 'black')
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.tick_params(colors=text_color, labelcolor=text_color)
            
            # Grid color
            grid_color = colors.get('plot_grid', '#cccccc')
            ax.grid(color=grid_color, alpha=0.50, linestyle='-', linewidth=0.8)
            
            # Spine colors
            for spine in ax.spines.values():
                spine.set_color(colors.get('border', '#cccccc'))
                spine.set_linewidth(0.8)
                
        except Exception as e:
            _LOGGER.debug(f"Could not apply theme colors to plot: {e}")
    
    def setup_correlation_plot(self, fig: Figure, ax: Axes):
        """Setup styling specific to correlation plots"""
        self.apply_no_title_styling(fig, ax, 
                                   xlabel="Velocity (km/s)", 
                                   ylabel="Correlation")
        
        # Correlation-specific styling
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    
    def setup_spectrum_plot(self, fig: Figure, ax: Axes, 
                           plot_type: str = "flux"):
        """
        Setup styling specific to spectrum plots
        
        Args:
            fig: Figure object
            ax: Axes object  
            plot_type: Type of spectrum plot ('flux', 'flat', 'original')
        """
        if plot_type == "flat":
            self.apply_no_title_styling(fig, ax,
                                       xlabel="Wavelength (Å)",
                                       ylabel="Flattened Flux")
        elif plot_type == "original":
            self.apply_no_title_styling(fig, ax,
                                       xlabel="Wavelength (Å)", 
                                       ylabel="Flux")
        else:  # default flux
            self.apply_no_title_styling(fig, ax,
                                       xlabel="Wavelength (Å)",
                                       ylabel="Flux")
    
    def setup_comparison_plot(self, fig: Figure, axes: np.ndarray):
        """Setup styling for multi-panel comparison plots"""
        # Apply to all subplots
        self.apply_no_title_styling(fig, axes, 
                                   xlabel="Wavelength (Å)", 
                                   ylabel="Flux")
        
        # Additional spacing optimization for multi-panel
        fig.subplots_adjust(hspace=0.3, wspace=0.3, top=0.95)
    
    def setup_clustering_plot(self, fig: Figure, ax: Axes):
        """Setup styling for clustering/GMM plots"""
        self.apply_no_title_styling(fig, ax,
                                   xlabel="Feature 1",
                                   ylabel="Feature 2")
        
        # Make legend more compact
        if ax.get_legend():
            legend = ax.get_legend()
            if self.font_manager:
                legend_font = self.font_manager.get_matplotlib_font_dict(FontCategory.PLOT_LEGEND)
                legend.set_fontsize(legend_font['size'])
            legend.set_framealpha(0.9)
    
    def setup_redshift_age_plot(self, fig: Figure, ax: Axes):
        """Setup styling for redshift-age scatter plots"""
        self.apply_no_title_styling(fig, ax,
                                   xlabel="Redshift (z)",
                                   ylabel="Age (days)")
    
    def optimize_for_gui(self, fig: Figure):
        """Apply final optimizations for GUI display"""
        # Ensure tight layout without title space
        fig.tight_layout(pad=0.3)
        
        # Final adjustment to maximize plot area
        try:
            fig.subplots_adjust(top=0.96, bottom=0.1, left=0.1, right=0.96)
        except:
            pass
    
    def clear_and_optimize(self, ax: Axes):
        """Clear axes and apply optimal styling for new plot"""
        ax.clear()
        
        # Remove any lingering title
        ax.set_title('')
        ax.title.set_visible(False)
        
        # Apply theme if available
        if self.theme_manager:
            self._apply_theme_colors(ax)
    
    def finalize_plot(self, fig: Figure, ax: Union[Axes, np.ndarray]):
        """Final plot preparation before display"""
        # Ensure no titles are visible
        if isinstance(ax, np.ndarray):
            for single_ax in ax.flatten():
                single_ax.set_title('')
                single_ax.title.set_visible(False)
        else:
            ax.set_title('')  
            ax.title.set_visible(False)
        
        # Final layout optimization
        self.optimize_for_gui(fig)


# Global plot manager instance
_PLOT_MANAGER = None

def get_plot_manager(theme_manager=None) -> NoTitlePlotManager:
    """Get the global plot manager instance"""
    global _PLOT_MANAGER
    if _PLOT_MANAGER is None:
        _PLOT_MANAGER = NoTitlePlotManager(theme_manager)
    return _PLOT_MANAGER


def create_gui_figure(figsize: Tuple[float, float] = (10, 6), 
                     theme_manager=None) -> Tuple[Figure, Axes]:
    """Convenience function to create optimized GUI figure"""
    return get_plot_manager(theme_manager).create_figure(figsize)


def apply_no_title_styling(fig: Figure, ax: Union[Axes, np.ndarray], 
                          xlabel: str = "Wavelength (Å)", 
                          ylabel: str = "Flux",
                          theme_manager=None):
    """Convenience function to apply no-title styling"""
    get_plot_manager(theme_manager).apply_no_title_styling(fig, ax, xlabel, ylabel) 
