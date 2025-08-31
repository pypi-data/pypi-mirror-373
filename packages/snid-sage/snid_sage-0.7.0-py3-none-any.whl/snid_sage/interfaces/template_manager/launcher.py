"""
SNID Template Manager Launcher
=============================

Professional launcher for the Template Manager GUI with unified logging,
argument parsing, and environment setup consistent with the main SNID-SAGE GUI.
"""

from __future__ import annotations

import os
import sys
import argparse
from typing import Optional

from PySide6 import QtWidgets, QtCore

from .main_window import SNIDTemplateManagerGUI


def _configure_environment(verbose: bool = False) -> None:
    """Configure environment for robust Qt rendering and consistent backend."""
    os.environ['SNID_SAGE_GUI_BACKEND'] = 'PySide6'
    try:
        from snid_sage.interfaces.gui.launcher import _configure_rendering_environment  # type: ignore
        _configure_rendering_environment(verbose=verbose)
    except Exception:
        pass


def _install_exception_hook() -> None:
    """Install a global exception hook to log and display exceptions."""
    try:
        from snid_sage.shared.utils.logging import get_logger
        logger = get_logger('template_manager.launcher')
    except Exception:
        import logging
        logger = logging.getLogger('template_manager.launcher')

    def handle_exception(exc_type, exc_value, exc_traceback):
        try:
            logger.exception("Unhandled exception in Template Manager", exc_info=(exc_type, exc_value, exc_traceback))
        except Exception:
            pass
        try:
            QtWidgets.QMessageBox.critical(
                None,
                "SNID Template Manager - Error",
                f"An unexpected error occurred:\n\n{exc_value}",
            )
        except Exception:
            pass

    sys.excepthook = handle_exception


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SNID Template Manager GUI")
    try:
        from snid_sage.shared.utils.logging import add_logging_arguments
        add_logging_arguments(parser)
    except Exception:
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        group.add_argument('--debug', '-d', action='store_true', help='Debug output')
        group.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
        parser.add_argument('--silent', action='store_true', help='Silent mode')
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

    # Configure logging
    try:
        from snid_sage.shared.utils.logging import configure_from_args, get_logger
        configure_from_args(args, gui_mode=True)
        logger = get_logger('template_manager.launcher')
    except Exception:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('template_manager.launcher')

    verbose = bool(getattr(args, 'verbose', False) or getattr(args, 'debug', False))
    _configure_environment(verbose=verbose)
    _install_exception_hook()

    logger.info("Starting SNID Template Manager")

    try:
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    except Exception:
        pass

    app = QtWidgets.QApplication(sys.argv if argv is None else argv)
    app.setApplicationName("SNID Template Manager")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("SNID SAGE")
    app.setOrganizationDomain("snid-sage.org")
    app.setQuitOnLastWindowClosed(True)

    try:
        window = SNIDTemplateManagerGUI()
        window.show()
        logger.info("Template Manager started successfully")
        return int(app.exec())
    except Exception as e:
        logger.error(f"Error starting Template Manager: {e}")
        try:
            QtWidgets.QMessageBox.critical(
                None,
                "Startup Error",
                f"Failed to start Template Manager:\n\n{e}\n\nCheck the logs for details.",
            )
        except Exception:
            pass
        return 1
    finally:
        logger.info("Template Manager shutting down")


if __name__ == "__main__":
    sys.exit(main())