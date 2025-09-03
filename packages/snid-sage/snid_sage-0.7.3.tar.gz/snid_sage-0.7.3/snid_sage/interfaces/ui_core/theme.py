"""
UI Core Theme Facade
--------------------

Re-exports the main PySide6 theme manager so all interfaces can share a single
implementation without importing from each other.
"""

from typing import Any


def get_theme_manager() -> Any:
    """Return the global PySide6 theme manager from the main GUI utils.

    Kept as a thin wrapper to avoid breaking behavior. This allows small GUIs
    (lines/templates) to depend on a stable path (`interfaces.ui_core`) while
    we keep the implementation in `interfaces.gui.utils`.
    """
    from snid_sage.interfaces.gui.utils.pyside6_theme_manager import (
        get_pyside6_theme_manager,
    )

    return get_pyside6_theme_manager()


