"""
Standardized Font Size Configuration for SNID SAGE Plots
=======================================================

This module provides centralized font size constants that ensure consistent
typography across all plots in both GUI and CLI modes.

All font sizes are carefully chosen for readability and consistency:
- Based on analysis of existing code and user feedback
- Optimized for both screen display and print output
- Accessible for users with different visual needs
- Consistent with modern scientific plotting standards
"""

# ---------------------------------------------------------------------------
# Main Plot Elements
# ---------------------------------------------------------------------------
# These are the primary font sizes used throughout the application

PLOT_TITLE_FONTSIZE: int = 14        # Plot titles (when used)
PLOT_AXIS_LABEL_FONTSIZE: int = 14   # X/Y axis labels
PLOT_TICK_FONTSIZE: int = 10         # Axis tick labels
PLOT_LEGEND_FONTSIZE: int = 11       # Legend text
PLOT_ANNOTATION_FONTSIZE: int = 10   # Text annotations on plots

# ---------------------------------------------------------------------------
# Specialized Elements
# ---------------------------------------------------------------------------
# Font sizes for specific plot elements

PLOT_INFO_TEXT_FONTSIZE: int = 9     # Info boxes and detailed text
PLOT_TABLE_FONTSIZE: int = 9         # Table text in plots
PLOT_PIE_AUTOPCT_FONTSIZE: int = 10  # Pie chart percentage labels
PLOT_BAR_VALUE_FONTSIZE: int = 8     # Bar chart value labels

# ---------------------------------------------------------------------------
# Error/Status Messages
# ---------------------------------------------------------------------------
# Font sizes for user-facing messages

PLOT_ERROR_FONTSIZE: int = 14        # Error messages on plots
PLOT_STATUS_FONTSIZE: int = 12       # Status/info messages on plots

# ---------------------------------------------------------------------------
# Matplotlib RCParams Configuration
# ---------------------------------------------------------------------------
# Dictionary for setting matplotlib global font parameters

MATPLOTLIB_FONT_CONFIG = {
    'font.size': 10,
    'axes.titlesize': PLOT_TITLE_FONTSIZE,
    'axes.labelsize': PLOT_AXIS_LABEL_FONTSIZE,
    'xtick.labelsize': PLOT_TICK_FONTSIZE,
    'ytick.labelsize': PLOT_TICK_FONTSIZE,
    'legend.fontsize': PLOT_LEGEND_FONTSIZE,
}

# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------

def get_font_config() -> dict:
    """
    Get the complete matplotlib font configuration dictionary.
    
    Returns:
        dict: Font configuration for matplotlib rcParams
    """
    return MATPLOTLIB_FONT_CONFIG.copy()


def apply_font_config():
    """
    Apply the standardized font configuration to matplotlib globally.
    
    This function should be called early in the application lifecycle
    to ensure all plots use consistent font sizes.
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    
    plt.rcParams.update(MATPLOTLIB_FONT_CONFIG)
    mpl.rcParams.update(MATPLOTLIB_FONT_CONFIG)


def get_font_size(category: str) -> int:
    """
    Get font size for a specific category.
    
    Args:
        category: Font category ('title', 'axis_label', 'tick', 'legend', etc.)
        
    Returns:
        int: Font size for the specified category
        
    Raises:
        ValueError: If category is not recognized
    """
    font_sizes = {
        'title': PLOT_TITLE_FONTSIZE,
        'axis_label': PLOT_AXIS_LABEL_FONTSIZE,
        'tick': PLOT_TICK_FONTSIZE,
        'legend': PLOT_LEGEND_FONTSIZE,
        'annotation': PLOT_ANNOTATION_FONTSIZE,
        'info_text': PLOT_INFO_TEXT_FONTSIZE,
        'table': PLOT_TABLE_FONTSIZE,
        'pie_autopct': PLOT_PIE_AUTOPCT_FONTSIZE,
        'bar_value': PLOT_BAR_VALUE_FONTSIZE,
        'error': PLOT_ERROR_FONTSIZE,
        'status': PLOT_STATUS_FONTSIZE,
    }
    
    if category not in font_sizes:
        raise ValueError(f"Unknown font category: {category}. "
                        f"Available categories: {list(font_sizes.keys())}")
    
    return font_sizes[category] 