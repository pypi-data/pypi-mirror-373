"""
SNID Line Manager Interface
==========================

Lightweight GUI for browsing and editing spectral lines and presets.
Exposes a consistent `main()` entry point for launching the GUI.
"""

from .main_window import SNIDLineManagerGUI
from .launcher import main

__all__ = ["SNIDLineManagerGUI", "main"]
