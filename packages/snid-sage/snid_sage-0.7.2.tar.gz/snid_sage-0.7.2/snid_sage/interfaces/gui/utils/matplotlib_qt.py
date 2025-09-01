"""
Matplotlib + Qt configuration helper for PySide6 GUI
===================================================

Provides a single, consistent entry-point to obtain Matplotlib objects
configured for the Qt backend (QtAgg) and embedded usage in PySide6.

Usage:
    from snid_sage.interfaces.gui.utils.matplotlib_qt import get_qt_mpl
    plt, Figure, FigureCanvas, NavigationToolbar = get_qt_mpl()

This ensures the backend is set once and interactive mode is disabled to
prevent external windows. It also applies a few rcParams suitable for
embedded figures.
"""

from __future__ import annotations

from typing import Tuple


def get_qt_mpl() -> Tuple["object", "object", "object", "object"]:
    """Return Matplotlib objects configured for Qt (QtAgg) embedding.

    Returns a tuple: (plt, Figure, FigureCanvas, NavigationToolbar)
    """
    # Delay imports until called to avoid early backend selection elsewhere
    import os
    import matplotlib

    # If we are running the PySide6 GUI, ensure a Qt backend
    backend = (matplotlib.get_backend() or "").lower()
    if "qt" not in backend:
        try:
            # QtAgg is the modern Qt backend in recent Matplotlib versions
            matplotlib.use("QtAgg", force=True)
        except Exception:
            # Fallback: if QtAgg is not available, try Qt5Agg; otherwise leave as-is
            try:
                matplotlib.use("Qt5Agg", force=True)
            except Exception:
                pass

    # Now import pyplot and Qt canvas/toolbar
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    try:
        from matplotlib.backends.backend_qtagg import (
            FigureCanvasQTAgg as FigureCanvas,
            NavigationToolbar2QT as NavigationToolbar,
        )
    except Exception:
        # Older Matplotlib fallback
        from matplotlib.backends.backend_qt5agg import (
            FigureCanvasQTAgg as FigureCanvas,
            NavigationToolbar2QT as NavigationToolbar,
        )

    # Embedded-friendly defaults
    import matplotlib as mpl
    plt.ioff()  # Prevent external interactive windows
    mpl.rcParams.setdefault("figure.raise_window", False)
    mpl.rcParams.setdefault("figure.autolayout", True)
    mpl.rcParams.setdefault("savefig.dpi", "figure")

    return plt, Figure, FigureCanvas, NavigationToolbar


