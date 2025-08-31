"""
Unified UI Core for PySide6
===========================

Lightweight facade exposing shared GUI utilities (theme, layout, icons) for all
SNID SAGE interfaces without causing cross-dependencies between apps.

This module intentionally re-exports existing, stable implementations to avoid
behavior changes. Interfaces can migrate their imports to this package without
breaking.
"""

from .theme import get_theme_manager  # noqa: F401
from .layout import get_layout_manager  # noqa: F401
from .logo import get_logo_manager  # noqa: F401
from .twemoji import get_twemoji_manager  # noqa: F401

__all__ = [
    "get_theme_manager",
    "get_layout_manager",
    "get_logo_manager",
    "get_twemoji_manager",
]


