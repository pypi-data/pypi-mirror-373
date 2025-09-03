"""
Platform-specific configuration for SNID SAGE
==============================================

This module handles platform-specific configurations and dependencies,
ensuring consistent behavior across different operating systems.
"""

import sys
import platform
from typing import Dict, Any, Optional
import logging

# Import centralized logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('platform_config')
except ImportError:
    _LOGGER = logging.getLogger('platform_config')


class PlatformConfig:
    """Platform-specific configuration manager"""
    
    def __init__(self):
        self.platform_name = platform.system().lower()
        self.is_windows = self.platform_name == 'windows'
        self.is_macos = self.platform_name == 'darwin'
        self.is_linux = self.platform_name == 'linux'
        
        _LOGGER.info(f"Platform detected: {self.platform_name}")
    
    def get_click_text(self, click_type: str = "right") -> str:
        """
        Get platform-appropriate click text for GUI instructions.
        
        Args:
            click_type: Type of click ("right", "left", "middle")
            
        Returns:
            Platform-appropriate text for the click type
        """
        if click_type.lower() == "right":
            return "Two finger click" if self.is_macos else "Right click"
        elif click_type.lower() == "left":
            return "Click" if self.is_macos else "Left click"
        elif click_type.lower() == "middle":
            return "Middle click"  # Same across platforms
        else:
            return f"{click_type.capitalize()} click"
    
    def get_gui_config(self) -> Dict[str, Any]:
        """Get platform-specific GUI configuration"""
        base_config = {
            'use_native_dialogs': True,
            'window_scaling': 1.0,
            'font_scaling': 1.0,
            'theme_style': 'default',
        }
        
        if self.is_macos:
            return {
                **base_config,
                'use_native_dialogs': True,
                'window_scaling': 1.0,
                'font_scaling': 1.1,  # Slightly larger fonts on macOS
                'theme_style': 'aqua',
                'button_style': 'rounded',
                'menu_style': 'native',
                'title_bar_style': 'native',
                'scrollbar_style': 'overlay',
                'focus_highlight': True,
                'use_system_colors': True,
            }
        elif self.is_windows:
            return {
                **base_config,
                'use_native_dialogs': True,
                'window_scaling': 1.0,
                'font_scaling': 1.0,
                'theme_style': 'vista',
                'button_style': 'flat',
                'menu_style': 'modern',
                'title_bar_style': 'custom',
                'scrollbar_style': 'standard',
                'focus_highlight': False,
                'use_system_colors': False,
            }
        elif self.is_linux:
            return {
                **base_config,
                'use_native_dialogs': False,
                'window_scaling': 1.0,
                'font_scaling': 1.0,
                'theme_style': 'clam',
                'button_style': 'flat',
                'menu_style': 'gtk',
                'title_bar_style': 'custom',
                'scrollbar_style': 'standard',
                'focus_highlight': True,
                'use_system_colors': True,
            }
        
        return base_config
    
    def get_dependency_config(self) -> Dict[str, Any]:
        """Get platform-specific dependency configuration"""
        config = {
            'numpy_version': '>=1.20.0',
            'matplotlib_backend': 'QtAgg',
            'use_system_fonts': True,
        }
        
        if self.is_macos:
            config.update({
                'matplotlib_backend': 'QtAgg',
                'use_system_fonts': True,
                'font_smoothing': True,
                'retina_support': True,
            })
        elif self.is_windows:
            config.update({
                'matplotlib_backend': 'QtAgg',
                'use_system_fonts': False,
                'font_smoothing': False,
                'high_dpi_support': True,
            })
        
        return config
    
    def get_styling_config(self) -> Dict[str, Any]:
        """Get platform-specific styling configuration"""
        base_styling = {
            'button_padding': (10, 5),
            'frame_padding': 10,
            'widget_spacing': 5,
            'border_width': 1,
        }
        
        if self.is_macos:
            return {
                **base_styling,
                'button_padding': (12, 8),
                'frame_padding': 12,
                'widget_spacing': 8,
                'border_width': 0,
                'corner_radius': 6,
                'shadow_enabled': True,
                'animation_enabled': True,
            }
        elif self.is_windows:
            return {
                **base_styling,
                'button_padding': (10, 5),
                'frame_padding': 10,
                'widget_spacing': 5,
                'border_width': 1,
                'corner_radius': 0,
                'shadow_enabled': False,
                'animation_enabled': False,
            }
        
        return base_styling
    
    def apply_platform_fixes(self):
        """Apply platform-specific fixes and workarounds"""
        if self.is_macos:
            self._apply_macos_fixes()
        elif self.is_windows:
            self._apply_windows_fixes()
        elif self.is_linux:
            self._apply_linux_fixes()
    
    def _apply_macos_fixes(self):
        """Apply macOS-specific fixes"""
        try:
            # No Tkinter-specific fixes required for PySide6/Qt backend
            _LOGGER.info("Applied macOS-specific fixes (Qt backend)")
        except Exception as e:
            _LOGGER.warning(f"Failed to apply macOS fixes: {e}")
    
    def _apply_windows_fixes(self):
        """Apply Windows-specific fixes"""
        try:
            # Windows DPI awareness
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
            
            _LOGGER.info("Applied Windows-specific fixes")
        except Exception as e:
            _LOGGER.warning(f"Failed to apply Windows fixes: {e}")
    
    def _apply_linux_fixes(self):
        """Apply Linux-specific fixes"""
        try:
            # Linux-specific configurations
            _LOGGER.info("Applied Linux-specific fixes")
        except Exception as e:
            _LOGGER.warning(f"Failed to apply Linux fixes: {e}")


# Global platform config instance
_platform_config = None

def get_platform_config() -> PlatformConfig:
    """Get the global platform configuration instance"""
    global _platform_config
    if _platform_config is None:
        _platform_config = PlatformConfig()
    return _platform_config

def is_macos() -> bool:
    """Check if running on macOS"""
    return get_platform_config().is_macos

def is_windows() -> bool:
    """Check if running on Windows"""
    return get_platform_config().is_windows

def is_linux() -> bool:
    """Check if running on Linux"""
    return get_platform_config().is_linux 