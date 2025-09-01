"""
SNID Line Manager Launcher
=========================

Professional launcher for the Line Manager GUI with:
- Consistent logging via shared logging utilities
- Optional verbosity flags
- Environment setup aligned with the main SNID-SAGE GUI
"""

from __future__ import annotations

import os
import sys
import argparse
from typing import Optional

from PySide6 import QtWidgets, QtCore

from .main_window import SNIDLineManagerGUI


def _configure_environment(verbose: bool = False) -> None:
    """Configure environment for robust Qt rendering and consistent backend."""
    # Ensure we are using the PySide6 backend consistently
    os.environ['SNID_SAGE_GUI_BACKEND'] = 'PySide6'

    # Reuse the main GUI rendering environment configuration if available
    try:
        # Importing a private helper is acceptable within this package for consistency
        from snid_sage.interfaces.gui.launcher import _configure_rendering_environment  # type: ignore
        _configure_rendering_environment(verbose=verbose)
    except Exception:
        # Fall back silently – defaults are fine on most platforms
        pass


def _install_exception_hook() -> None:
    """Show unhandled exceptions in a dialog and ensure they are logged."""
    try:
        from snid_sage.shared.utils.logging import get_logger
        logger = get_logger('line_manager.launcher')
    except Exception:
        import logging
        logger = logging.getLogger('line_manager.launcher')

    def handle_exception(exc_type, exc_value, exc_traceback):
        # Log error
        try:
            logger.exception("Unhandled exception in Line Manager", exc_info=(exc_type, exc_value, exc_traceback))
        except Exception:
            pass
        # Show dialog (best-effort)
        try:
            QtWidgets.QMessageBox.critical(
                None,
                "SNID Line Manager - Error",
                f"An unexpected error occurred:\n\n{exc_value}",
            )
        except Exception:
            pass

    sys.excepthook = handle_exception


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments, integrating standard logging flags."""
    parser = argparse.ArgumentParser(description="SNID Line Manager GUI")
    try:
        from snid_sage.shared.utils.logging import add_logging_arguments
        add_logging_arguments(parser)
    except Exception:
        # Minimal fallback flags
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        group.add_argument('--debug', '-d', action='store_true', help='Debug output')
        group.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
        parser.add_argument('--silent', action='store_true', help='Silent mode')

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for launching the SNID Line Manager GUI."""
    args = _parse_args(argv)

    # Configure logging
    try:
        from snid_sage.shared.utils.logging import configure_from_args, get_logger
        configure_from_args(args, gui_mode=True)
        logger = get_logger('line_manager.launcher')
    except Exception:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('line_manager.launcher')

    verbose = bool(getattr(args, 'verbose', False) or getattr(args, 'debug', False))
    _configure_environment(verbose=verbose)
    _install_exception_hook()

    logger.info("Starting SNID Line Manager")

    # High DPI pixmaps help on HiDPI displays
    try:
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    except Exception:
        pass

    app = QtWidgets.QApplication(sys.argv if argv is None else argv)
    app.setApplicationName("SNID Line Manager")
    app.setOrganizationName("SNID SAGE")

    window = SNIDLineManagerGUI()
    window.show()
    rc = app.exec()
    logger.info("Line Manager shutting down")
    return int(rc)


if __name__ == "__main__":
    sys.exit(main())


