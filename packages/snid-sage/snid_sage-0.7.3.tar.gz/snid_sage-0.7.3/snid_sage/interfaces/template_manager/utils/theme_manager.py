"""
SNID Template Manager - Theme Manager
====================================

Centralized theme management for the Template Manager GUI, providing:
- Consistent color schemes matching the main SNID-SAGE GUI
- Platform-specific theme adjustments
- Centralized Qt stylesheet generation
- Theme color access for custom components

This manager ensures the Template Manager maintains visual consistency
with the main SNID-SAGE interface while being self-contained.

Developed by Fiorenzo Stoppa for SNID SAGE
"""

from typing import Dict, Any, Optional
import platform

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.theme')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.theme')

# Import shared UI core theme manager for base stylesheet consistency
try:
    from snid_sage.interfaces.ui_core import get_theme_manager as _get_base_theme
    MAIN_THEME_AVAILABLE = True
except Exception:
    MAIN_THEME_AVAILABLE = False
    _get_base_theme = None  # type: ignore


class TemplateManagerThemeManager:
    """
    Theme manager for the Template Manager GUI
    
    This class provides centralized theme management that maintains
    consistency with the main SNID-SAGE GUI while being self-contained.
    """
    
    def __init__(self):
        """Initialize the Template Manager theme manager"""
        self._main_theme = None
        if MAIN_THEME_AVAILABLE and _get_base_theme is not None:
            try:
                # Use the shared theme manager instance for base styles
                self._main_theme = _get_base_theme()
            except Exception as e:
                _LOGGER.warning(f"Could not initialize base theme manager: {e}")
        
        # Template Manager specific colors
        self._template_colors = {
            'template_browser': '#34495e',
            'template_selected': '#3498db',
            'template_creator': '#10B981',
            'template_manager': '#8B5CF6',
            'template_viewer': '#06B6D4'
        }
        
    def get_base_colors(self) -> Dict[str, str]:
        """Get base color palette, delegating to main theme if available"""
        # Local base palette (kept stable to avoid depending on base theme internals)
        return {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444',
            'background': '#ecf0f1',
            'surface': '#ffffff',
            'text_primary': '#2c3e50',
            'text_secondary': '#7f8c8d',
            'border': '#bdc3c7'
        }
    
    def get_template_colors(self) -> Dict[str, str]:
        """Get Template Manager specific colors"""
        return self._template_colors.copy()
    
    def get_workflow_colors(self) -> Dict[str, str]:
        """Get workflow button colors, delegating to main theme if available"""
        # Local workflow palette
        return {
            'preprocessing': '#3498db',
            'identification': '#e74c3c', 
            'analysis': '#2ecc71',
            'results': '#9b59b6',
            'visualization': '#f39c12'
        }
    
    def generate_complete_stylesheet(self) -> str:
        """Generate complete stylesheet for Template Manager"""
        if self._main_theme:
            # Use main theme as base and add template-specific styles
            base_stylesheet = self._main_theme.generate_complete_stylesheet()
            template_styles = self._generate_template_specific_styles()
            return f"{base_stylesheet}\n\n/* Template Manager Specific Styles */\n{template_styles}"
        
        # Generate fallback stylesheet
        return self._generate_fallback_stylesheet()
    
    def _generate_template_specific_styles(self) -> str:
        """Generate Template Manager specific styles"""
        colors = self.get_template_colors()
        
        return f"""
        /* Template Browser */
        TemplateTreeWidget {{
            background-color: white;
            border: 1px solid #bdc3c7;
            selection-background-color: {colors['template_selected']};
        }}
        
        /* Template Tabs */
        QTabWidget::tab-bar {{
            alignment: center;
        }}
        
        QTabBar::tab {{
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['template_viewer']};
            color: white;
        }}
        
        /* Template Creator Styles */
        TemplateCreatorWidget QPushButton[objectName="create_btn"] {{
            background-color: {colors['template_creator']};
            color: white;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
        }}
        
        TemplateCreatorWidget QPushButton[objectName="create_btn"]:hover {{
            background-color: #059669;
        }}
        
        /* Template Manager Styles */
        TemplateManagerWidget {{
            background-color: {colors['template_manager']};
        }}
        
        /* Comparison and Statistics tabs removed */
        """
    
    def _generate_fallback_stylesheet(self) -> str:
        """Generate fallback stylesheet when main theme is not available"""
        base_colors = self.get_base_colors()
        template_colors = self.get_template_colors()
        
        return f"""
        /* Base Styles */
        QMainWindow {{
            background-color: {base_colors['primary']};
            color: {base_colors['background']};
        }}
        
        QWidget {{
            background-color: {base_colors['background']};
            color: {base_colors['text_primary']};
        }}
        
        /* Group Box Styles */
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {base_colors['secondary']};
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 5px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        
        /* Button Styles */
        QPushButton {{
            background-color: {base_colors['accent']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: #2980b9;
        }}
        
        QPushButton:pressed {{
            background-color: #21618c;
        }}
        
        /* Tree Widget Styles */
        QTreeWidget {{
            background-color: white;
            border: 1px solid {base_colors['border']};
            selection-background-color: {template_colors['template_selected']};
        }}
        
        /* Tab Widget Styles */
        QTabWidget::pane {{
            border: 1px solid {base_colors['secondary']};
        }}
        
        QTabBar::tab {{
            background-color: {base_colors['secondary']};
            padding: 8px 12px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {base_colors['accent']};
            color: white;
        }}
        
        /* Line Edit Styles */
        QLineEdit {{
            border: 1px solid {base_colors['border']};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: {base_colors['surface']};
        }}
        
        /* ComboBox Styles */
        QComboBox {{
            border: 1px solid {base_colors['border']};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: {base_colors['surface']};
        }}
        
        /* Text Edit Styles */
        QTextEdit {{
            border: 1px solid {base_colors['border']};
            border-radius: 4px;
            background-color: {base_colors['surface']};
        }}
        
        /* Table Widget Styles */
        QTableWidget {{
            border: 1px solid {base_colors['border']};
            background-color: {base_colors['surface']};
            gridline-color: {base_colors['border']};
        }}
        
        QHeaderView::section {{
            background-color: {base_colors['secondary']};
            color: white;
            padding: 4px 8px;
            border: none;
        }}
        
        {self._generate_template_specific_styles()}
        """

    def get_color(self, color_key: str) -> str:
        """Get a specific color by key"""
        base_colors = self.get_base_colors()
        template_colors = self.get_template_colors()
        workflow_colors = self.get_workflow_colors()
        
        # Check template colors first
        if color_key in template_colors:
            return template_colors[color_key]
        elif color_key in base_colors:
            return base_colors[color_key]
        elif color_key in workflow_colors:
            return workflow_colors[color_key]
        else:
            _LOGGER.warning(f"Color key '{color_key}' not found")
            return base_colors.get('primary', '#2c3e50')


# Global instance
_template_theme_manager = None

def get_template_theme_manager() -> TemplateManagerThemeManager:
    """Get the global Template Manager theme manager instance"""
    global _template_theme_manager
    if _template_theme_manager is None:
        _template_theme_manager = TemplateManagerThemeManager()
    return _template_theme_manager