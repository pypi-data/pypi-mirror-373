"""
Layout Configuration Manager

This module handles saving and loading layout settings for the SNID SAGE GUI,
allowing users to persist their preferred spacing and positioning settings.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)


class LayoutConfigManager:
    """Manager for layout configuration persistence"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize layout config manager
        
        Args:
            config_dir: Directory to store config files (defaults to user config dir)
        """
        if config_dir is None:
            # Use user's config directory
            if os.name == 'nt':  # Windows
                config_dir = os.path.expanduser("~/AppData/Local/SNID_SAGE")
            else:  # Unix-like
                config_dir = os.path.expanduser("~/.config/snid_sage")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.layout_config_file = self.config_dir / "layout_settings.json"
        
        _LOGGER.debug(f"Layout config manager initialized: {self.layout_config_file}")
    
    def save_layout_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """
        Save layout settings to config file
        
        Args:
            settings_dict: Dictionary of layout settings
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Add metadata
            config_data = {
                "version": "1.0",
                "layout_settings": settings_dict,
                "last_updated": self._get_timestamp()
            }
            
            with open(self.layout_config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            _LOGGER.debug(f"Layout settings saved to {self.layout_config_file}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error saving layout settings: {e}")
            return False
    
    def load_layout_settings(self) -> Optional[Dict[str, Any]]:
        """
        Load layout settings from config file
        
        Returns:
            Dictionary of layout settings if found, None otherwise
        """
        try:
            if not self.layout_config_file.exists():
                _LOGGER.debug("No layout config file found, using defaults")
                return None
            
            with open(self.layout_config_file, 'r') as f:
                config_data = json.load(f)
            
            # Extract layout settings
            layout_settings = config_data.get("layout_settings", {})
            _LOGGER.debug(f"Layout settings loaded from {self.layout_config_file}")
            return layout_settings
            
        except Exception as e:
            _LOGGER.error(f"Error loading layout settings: {e}")
            return None
    
    def get_default_layout_settings(self) -> Dict[str, Any]:
        """
        Get default layout settings
        
        Returns:
            Dictionary of default layout settings
        """
        return {
            'plot_controls_spacing': 15,
            'button_group_spacing': 15,
            'controls_frame_height': 36,  # Single row with all buttons integrated
            'plot_margin_top': 8,
            'plot_margin_bottom': 5,
            'plot_margin_left': 5,
            'plot_margin_right': 5,
            'view_controls_width': 120,
            'nav_controls_width': 80,
            'analysis_controls_width': 160,
            'independent_plot_positioning': True,
            'button_layout_style': 'horizontal',
            'plot_expansion_mode': 'fill_remaining'
        }
    
    def reset_to_defaults(self) -> bool:
        """
        Reset layout settings to defaults
        
        Returns:
            True if reset successfully, False otherwise
        """
        default_settings = self.get_default_layout_settings()
        return self.save_layout_settings(default_settings)
    
    def backup_current_settings(self) -> bool:
        """
        Create a backup of current settings
        
        Returns:
            True if backup created successfully, False otherwise
        """
        try:
            if not self.layout_config_file.exists():
                _LOGGER.debug("No current settings to backup")
                return True
            
            backup_file = self.config_dir / f"layout_settings_backup_{self._get_timestamp().replace(':', '-')}.json"
            
            # Copy current settings to backup
            with open(self.layout_config_file, 'r') as src:
                with open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            _LOGGER.debug(f"Settings backed up to {backup_file}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error creating settings backup: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize layout settings
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            Validated and sanitized settings
        """
        defaults = self.get_default_layout_settings()
        validated = {}
        
        for key, default_value in defaults.items():
            if key in settings:
                value = settings[key]
                
                # Type validation and range checking
                if isinstance(default_value, int):
                    try:
                        value = int(value)
                        # Apply reasonable ranges
                        if key.endswith('_spacing'):
                            value = max(0, min(50, value))  # 0-50px spacing
                        elif key.endswith('_height'):
                            value = max(20, min(80, value))  # 20-80px height
                        elif key.endswith('_margin'):
                            value = max(0, min(30, value))   # 0-30px margins
                        elif key.endswith('_width'):
                            value = max(50, min(300, value)) # 50-300px width
                    except ValueError:
                        value = default_value
                        
                elif isinstance(default_value, bool):
                    value = bool(value)
                    
                elif isinstance(default_value, str):
                    if key == 'button_layout_style':
                        value = value if value in ['horizontal', 'vertical'] else default_value
                    elif key == 'plot_expansion_mode':
                        value = value if value in ['fill_remaining', 'fixed_size'] else default_value
                
                validated[key] = value
            else:
                validated[key] = default_value
        
        return validated


# Global config manager instance
_config_manager = None

def get_layout_config_manager() -> LayoutConfigManager:
    """Get the global layout config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = LayoutConfigManager()
    return _config_manager 