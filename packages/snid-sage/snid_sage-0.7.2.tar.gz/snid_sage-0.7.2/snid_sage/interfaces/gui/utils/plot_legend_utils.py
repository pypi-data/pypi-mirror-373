"""
Utility functions for adaptive legend positioning in plots.
Ensures template legends remain visible and consistent across different views.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Dict, Any


def find_optimal_legend_position(ax, 
                                preferred_position='upper right',
                                avoid_data_overlap=True,
                                padding_factor=0.02) -> Tuple[str, Dict[str, float]]:
    """
    Find the optimal position for a legend that avoids data overlap.
    
    Args:
        ax: Matplotlib axis object
        preferred_position: Preferred legend position ('upper right', 'upper left', etc.)
        avoid_data_overlap: Whether to check for data overlap and adjust position
        padding_factor: Padding from plot edges as fraction of plot size
        
    Returns:
        Tuple of (position, bbox_to_anchor_dict) for legend placement
    """
    
    # Default positions to try in order of preference
    position_order = [
        'upper right',
        'upper left', 
        'lower right',
        'lower left',
        'center right',
        'center left'
    ]
    
    # Move preferred position to front if not already there
    if preferred_position in position_order:
        position_order.remove(preferred_position)
        position_order.insert(0, preferred_position)
    
    if not avoid_data_overlap:
        return preferred_position, {}
    
    # Get plot data bounds
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    
    # Calculate padding in data coordinates
    x_padding = (x_max - x_min) * padding_factor
    y_padding = (y_max - y_min) * padding_factor
    
    # Define corner regions where legend might be placed
    legend_regions = {
        'upper right': (x_max - x_padding, x_max, y_max - y_padding, y_max),
        'upper left': (x_min, x_min + x_padding, y_max - y_padding, y_max),
        'lower right': (x_max - x_padding, x_max, y_min, y_min + y_padding),
        'lower left': (x_min, x_min + x_padding, y_min, y_min + y_padding),
        'center right': (x_max - x_padding, x_max, y_min + (y_max-y_min)*0.4, y_min + (y_max-y_min)*0.6),
        'center left': (x_min, x_min + x_padding, y_min + (y_max-y_min)*0.4, y_min + (y_max-y_min)*0.6)
    }
    
    # Check data density in each region
    lines = ax.get_lines()
    
    for position in position_order:
        region = legend_regions.get(position)
        if not region:
            continue
            
        x_region_min, x_region_max, y_region_min, y_region_max = region
        
        # Count data points in this region
        data_density = 0
        total_points = 0
        
        for line in lines:
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            
            if len(x_data) == 0 or len(y_data) == 0:
                continue
                
            # Find points in the legend region
            in_x_range = (x_data >= x_region_min) & (x_data <= x_region_max)
            in_y_range = (y_data >= y_region_min) & (y_data <= y_region_max)
            in_region = in_x_range & in_y_range
            
            data_density += np.sum(in_region)
            total_points += len(x_data)
        
        # Use this position if it has low data density
        density_ratio = data_density / max(total_points, 1)
        if density_ratio < 0.1:  # Less than 10% of data in this region
            return position, {}
    
    # If all positions have significant data overlap, use preferred with bbox adjustment
    return preferred_position, {'bbox_to_anchor': (1.0, 1.0)}


def add_adaptive_template_info(ax, 
                              template_info: str,
                              position='auto',
                              theme_colors: Optional[Dict] = None,
                              fontsize: int = 10) -> None:
    """
    Add template information text to plot with adaptive positioning.
    
    Args:
        ax: Matplotlib axis object
        template_info: Template information string
        position: Position preference ('auto', 'upper right', 'upper left', etc.)
        theme_colors: Theme color dictionary
        fontsize: Font size for the text
    """
    
    # Default theme colors
    if theme_colors is None:
        theme_colors = {
            'text_primary': 'black',
            'bg_tertiary': 'lightcyan'
        }
    
    # Position mappings
    position_coords = {
        'upper right': (0.98, 0.98, 'top', 'right'),
        'upper left': (0.02, 0.98, 'top', 'left'),
        'lower right': (0.98, 0.02, 'bottom', 'right'),
        'lower left': (0.02, 0.02, 'bottom', 'left'),
        'center right': (0.98, 0.5, 'center', 'right'),
        'center left': (0.02, 0.5, 'center', 'left')
    }
    
    # Auto-select position if requested
    if position == 'auto':
        optimal_pos, _ = find_optimal_legend_position(ax, preferred_position='upper right')
        position = optimal_pos
    
    # Get position coordinates
    coords = position_coords.get(position, position_coords['upper right'])
    x, y, va, ha = coords
    
    # Add text with background
    ax.text(x, y, template_info, 
           transform=ax.transAxes,
           verticalalignment=va, 
           horizontalalignment=ha,
           fontsize=fontsize, 
           color=theme_colors.get('text_primary', 'black'),
           bbox=dict(boxstyle='round,pad=0.5', 
                    facecolor=theme_colors.get('bg_tertiary', 'lightcyan'), 
                    alpha=0.8,
                    edgecolor='gray',
                    linewidth=0.5))


def get_pyqtgraph_legend_position(plot_item, 
                                 preferred_corner='upper_right',
                                 padding_fraction=0.05) -> Tuple[float, float]:
    """
    Calculate optimal legend position for PyQtGraph plots.
    
    Args:
        plot_item: PyQtGraph PlotItem
        preferred_corner: Preferred corner ('upper_right', 'upper_left', etc.)
        padding_fraction: Padding from edges as fraction of plot size
        
    Returns:
        Tuple of (x, y) coordinates in data space
    """
    
    try:
        # Get current view range
        view_range = plot_item.getViewBox().viewRange()
        x_range = view_range[0]
        y_range = view_range[1]
        
        x_min, x_max = x_range
        y_min, y_max = y_range
        
        # Calculate padding
        x_padding = (x_max - x_min) * padding_fraction
        y_padding = (y_max - y_min) * padding_fraction
        
        # Position mappings
        positions = {
            'upper_right': (x_max - x_padding, y_max - y_padding),
            'upper_left': (x_min + x_padding, y_max - y_padding),
            'lower_right': (x_max - x_padding, y_min + y_padding),
            'lower_left': (x_min + x_padding, y_min + y_padding)
        }
        
        return positions.get(preferred_corner, positions['upper_right'])
        
    except Exception:
        # Fallback to default position
        return (0, 0)


def update_pyqtgraph_legend_on_view_change(plot_item, text_item, corner='upper_right'):
    """
    Update PyQtGraph text item position when view changes.
    
    Args:
        plot_item: PyQtGraph PlotItem
        text_item: PyQtGraph TextItem to reposition
        corner: Corner to position the legend in
    """
    
    try:
        x, y = get_pyqtgraph_legend_position(plot_item, corner)
        text_item.setPos(x, y)
    except Exception:
        # Silently handle positioning errors
        pass 