"""
Logo Manager Module for SNID SAGE GUI (Qt/PySide6)
==================================================

Qt-based logo loading and management for light/dark themes using QPixmap/QIcon.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

# Use centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.utils.logo_manager')
except ImportError:  # pragma: no cover - fallback for environments without shared logger
    import logging
    _LOGGER = logging.getLogger('gui.utils.logo_manager')

from PySide6 import QtCore, QtGui, QtWidgets


class QtLogoManager:
    """Qt-based manager for handling logos and branding elements."""

    def __init__(self) -> None:
        self.pixmap_light: Optional[QtGui.QPixmap] = None
        self.pixmap_dark: Optional[QtGui.QPixmap] = None
        self.current_pixmap: Optional[QtGui.QPixmap] = None
        self.logo_label: Optional[QtWidgets.QLabel] = None
        self.logo_height: int = 100
        self.max_logo_width: int = 180

        # Load pixmaps at construction time if possible
        try:
            self.load_pixmaps()
        except Exception as exc:  # pragma: no cover
            _LOGGER.warning(f"Error initializing logo pixmaps: {exc}")

    def _images_dir(self) -> Optional[Path]:
        """Locate the images directory inside the installed package.

        Returns None if not found.
        """
        try:
            import snid_sage as _pkg
            pkg_dir = Path(_pkg.__file__).resolve().parent
            images = pkg_dir / 'images'
            return images if images.exists() else None
        except Exception as exc:  # pragma: no cover
            _LOGGER.debug(f"Could not resolve images directory: {exc}")
            return None

    def _first_existing(self, candidates: list[Path]) -> Optional[Path]:
        for path in candidates:
            if path.exists():
                return path
        return None

    def get_icon_path(self) -> Optional[Path]:
        """Return a path to the preferred light-mode application icon if available."""
        images_dir = self._images_dir()
        if not images_dir:
            return None

        candidates = [
            images_dir / 'icon.png',
            images_dir / 'light.png',
            images_dir / 'logo.png',
            images_dir / 'snid_logo.png',
        ]
        return self._first_existing(candidates)

    def _dark_icon_path(self) -> Optional[Path]:
        images_dir = self._images_dir()
        if not images_dir:
            return None
        candidates = [
            images_dir / 'icon_dark.png',
            images_dir / 'dark.png',
            images_dir / '@dark.png',
            images_dir / 'logo@dark.png',
            images_dir / 'snid_logo_dark.png',
        ]
        return self._first_existing(candidates)

    def _load_scaled_pixmap(self, image_path: Path) -> Optional[QtGui.QPixmap]:
        try:
            pm = QtGui.QPixmap(str(image_path))
            if pm.isNull():
                return None
            aspect_ratio = pm.width() / pm.height() if pm.height() else 1.0
            target_width = int(self.logo_height * aspect_ratio)
            if target_width > self.max_logo_width:
                target_width = self.max_logo_width
                self.logo_height = int(self.max_logo_width / max(aspect_ratio, 1e-6))
            return pm.scaled(
                target_width,
                self.logo_height,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        except Exception as exc:  # pragma: no cover
            _LOGGER.warning(f"Failed to load pixmap from {image_path}: {exc}")
            return None

    def load_pixmaps(self) -> None:
        """Load SNID SAGE logos for light and dark modes using QPixmap."""
        try:
            light_path = self.get_icon_path()
            dark_path = self._dark_icon_path()

            self.pixmap_light = self._load_scaled_pixmap(light_path) if light_path else None
            self.pixmap_dark = self._load_scaled_pixmap(dark_path) if dark_path else None

            if not self.pixmap_dark and self.pixmap_light:
                self.pixmap_dark = self.pixmap_light

            self._set_initial_logo()
        except Exception as exc:  # pragma: no cover
            _LOGGER.warning(f"Error loading logo pixmaps: {exc}")
            self.pixmap_light = None
            self.pixmap_dark = None
            self.current_pixmap = None

    def _set_initial_logo(self) -> None:
        """Set initial logo - current implementation always uses light mode."""
        self.current_pixmap = self.pixmap_light

    def update_logo(self, dark_mode_enabled: Optional[bool] = None) -> None:
        """Update the current logo. Currently defaults to light logo."""
        new_pm = self.pixmap_light if self.pixmap_light is not None else None
        self.current_pixmap = new_pm

        if new_pm and self.logo_label is not None:
            try:
                self.logo_label.setPixmap(new_pm)
            except Exception as exc:  # pragma: no cover
                _LOGGER.warning(f"Error updating logo label: {exc}")

    def set_logo_label(self, logo_label: QtWidgets.QLabel) -> None:
        self.logo_label = logo_label

    def get_current_logo(self) -> Optional[QtGui.QPixmap]:
        return self.current_pixmap

    def has_logos(self) -> bool:
        return (self.pixmap_light is not None) or (self.pixmap_dark is not None)

    def create_logo_widget(self, parent: QtWidgets.QWidget) -> QtWidgets.QLabel:
        """Create and return a QLabel configured with the current logo, or text fallback."""
        label = QtWidgets.QLabel(parent)
        if self.current_pixmap is not None:
            label.setPixmap(self.current_pixmap)
        else:
            label.setText("SNID SAGE")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.set_logo_label(label)
        return label

    def cleanup(self) -> None:
        self.pixmap_light = None
        self.pixmap_dark = None
        self.current_pixmap = None
        self.logo_label = None
        _LOGGER.debug("Logo manager cleanup completed")


_qt_logo_manager: Optional[QtLogoManager] = None


def get_logo_manager() -> QtLogoManager:
    """Return a singleton QtLogoManager instance."""
    global _qt_logo_manager
    if _qt_logo_manager is None:
        _qt_logo_manager = QtLogoManager()
    return _qt_logo_manager
