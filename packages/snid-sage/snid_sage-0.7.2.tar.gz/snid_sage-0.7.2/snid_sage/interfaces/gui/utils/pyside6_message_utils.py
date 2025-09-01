"""
SNID SAGE - PySide6 Message Utilities
====================================

Utility functions providing message dialogs using PySide6 equivalents.
"""

import sys
from typing import Optional, Any

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_message_utils')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_message_utils')

try:
    import PySide6.QtWidgets as QtWidgets
    import PySide6.QtCore as QtCore
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    _LOGGER.warning("PySide6 not available, falling back to console messages")


def _get_app_and_parent():
    """Get QApplication instance and determine parent window"""
    if not PYSIDE6_AVAILABLE:
        return None, None
        
    # Get or create QApplication
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv if hasattr(sys, 'argv') else [])
    
    # Try to find an active window as parent
    parent = None
    for widget in app.allWidgets():
        if isinstance(widget, QtWidgets.QMainWindow) and widget.isVisible():
            parent = widget
            break
    
    return app, parent


def showerror(title: str, message: str, parent: Optional[Any] = None) -> None:
    """Show error message dialog"""
    if not PYSIDE6_AVAILABLE:
        print(f"ERROR [{title}]: {message}")
        return
    
    try:
        app, qt_parent = _get_app_and_parent()
        if app is None:
            print(f"ERROR [{title}]: {message}")
            return
        
        parent_widget = parent if isinstance(parent, QtWidgets.QWidget) else qt_parent
        msg = QtWidgets.QMessageBox(parent_widget)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()
        
    except Exception as e:
        _LOGGER.error(f"Error showing error dialog: {e}")
        print(f"ERROR [{title}]: {message}")


def showwarning(title: str, message: str, parent: Optional[Any] = None) -> None:
    """Show warning message dialog"""
    if not PYSIDE6_AVAILABLE:
        print(f"WARNING [{title}]: {message}")
        return
    
    try:
        app, qt_parent = _get_app_and_parent()
        if app is None:
            print(f"WARNING [{title}]: {message}")
            return
        
        parent_widget = parent if isinstance(parent, QtWidgets.QWidget) else qt_parent
        msg = QtWidgets.QMessageBox(parent_widget)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()
        
    except Exception as e:
        _LOGGER.error(f"Error showing warning dialog: {e}")
        print(f"WARNING [{title}]: {message}")


def showinfo(title: str, message: str, parent: Optional[Any] = None) -> None:
    """Show info message dialog"""
    if not PYSIDE6_AVAILABLE:
        print(f"INFO [{title}]: {message}")
        return
    
    try:
        app, qt_parent = _get_app_and_parent()
        if app is None:
            print(f"INFO [{title}]: {message}")
            return
        
        parent_widget = parent if isinstance(parent, QtWidgets.QWidget) else qt_parent
        msg = QtWidgets.QMessageBox(parent_widget)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()
        
    except Exception as e:
        _LOGGER.error(f"Error showing info dialog: {e}")
        print(f"INFO [{title}]: {message}")


def askyesno(title: str, message: str, parent: Optional[Any] = None) -> bool:
    """Show yes/no question dialog (replacement for tkinter.messagebox.askyesno)"""
    if not PYSIDE6_AVAILABLE:
        print(f"QUESTION [{title}]: {message}")
        # In non-GUI mode, default to 'no' for safety
        return False
    
    try:
        app, qt_parent = _get_app_and_parent()
        if app is None:
            print(f"QUESTION [{title}]: {message}")
            return False
        
        parent_widget = parent if isinstance(parent, QtWidgets.QWidget) else qt_parent
        msg = QtWidgets.QMessageBox(parent_widget)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        
        result = msg.exec()
        return result == QtWidgets.QMessageBox.StandardButton.Yes
        
    except Exception as e:
        _LOGGER.error(f"Error showing question dialog: {e}")
        print(f"QUESTION [{title}]: {message}")
        return False


def askokcancel(title: str, message: str, parent: Optional[Any] = None) -> bool:
    """Show ok/cancel question dialog (replacement for tkinter.messagebox.askokcancel)"""
    if not PYSIDE6_AVAILABLE:
        print(f"QUESTION [{title}]: {message}")
        return False
    
    try:
        app, qt_parent = _get_app_and_parent()
        if app is None:
            print(f"QUESTION [{title}]: {message}")
            return False
        
        parent_widget = parent if isinstance(parent, QtWidgets.QWidget) else qt_parent
        msg = QtWidgets.QMessageBox(parent_widget)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Ok | 
            QtWidgets.QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Cancel)
        
        result = msg.exec()
        return result == QtWidgets.QMessageBox.StandardButton.Ok
        
    except Exception as e:
        _LOGGER.error(f"Error showing ok/cancel dialog: {e}")
        print(f"QUESTION [{title}]: {message}")
        return False


# Create a mock messagebox module for drop-in replacement
class MessageBox:
    """Drop-in replacement for tkinter.messagebox"""
    showerror = staticmethod(showerror)
    showwarning = staticmethod(showwarning)
    showinfo = staticmethod(showinfo)
    askyesno = staticmethod(askyesno)
    askokcancel = staticmethod(askokcancel)


# Create instance for import
messagebox = MessageBox() 