"""
Calculator helpers for advanced preprocessing previews.

Currently provides continuum-related preview helpers extracted from the
monolithic preview calculator to keep responsibilities focused and files small.
"""

from .continuum import (
    fit_continuum_improved,
    preview_continuum_fit,
    calculate_manual_continuum_preview,
    calculate_interactive_continuum_preview,
)

__all__ = [
    "fit_continuum_improved",
    "preview_continuum_fit",
    "calculate_manual_continuum_preview",
    "calculate_interactive_continuum_preview",
]


