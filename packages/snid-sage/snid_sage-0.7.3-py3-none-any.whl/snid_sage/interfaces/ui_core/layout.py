"""
UI Core Layout Adapter
----------------------

Provides a small, stable layout API used by the mini GUIs (lines/templates)
without depending on each other's packages. Internally, `setup_main_window`
delegates to the main unified layout manager to keep window behavior consistent.
Other helpers are implemented locally to avoid cross-GUI coupling.
"""

from typing import Any, Optional


class UiCoreLayout:
    def __init__(self) -> None:
        self._twemoji = None
        try:
            from .twemoji import get_twemoji_manager  # lazy import

            self._twemoji = get_twemoji_manager()
        except Exception:
            self._twemoji = None

    # Window setup delegates to the main unified layout for consistency
    def setup_main_window(self, window: Any) -> None:
        try:
            from snid_sage.interfaces.gui.utils.unified_pyside6_layout_manager import (
                get_unified_layout_manager,
            )

            manager = get_unified_layout_manager()
            manager.setup_main_window(window)
        except Exception:
            # Minimal fallback
            try:
                window.setMinimumSize(700, 500)
                window.resize(950, 650)
                from PySide6 import QtWidgets

                screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
                rect = window.frameGeometry()
                rect.moveCenter(screen.center())
                window.move(rect.topLeft())
            except Exception:
                pass

    # Panel/layout helpers used by mini GUIs
    def apply_panel_layout(self, widget: Any, layout: Any) -> None:
        try:
            layout.setSpacing(10)
            layout.setContentsMargins(10, 10, 10, 10)
            widget.setLayout(layout)
        except Exception:
            pass

    def create_main_splitter(self) -> Any:
        from PySide6 import QtWidgets, QtCore

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        try:
            splitter.setSizes([250, 650])
            splitter.setChildrenCollapsible(False)
        except Exception:
            pass
        return splitter

    def create_vertical_splitter(self) -> Any:
        from PySide6 import QtWidgets, QtCore

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        try:
            splitter.setSizes([350, 200])
            splitter.setChildrenCollapsible(False)
        except Exception:
            pass
        return splitter

    def setup_form_layout(self, form_layout: Any) -> None:
        try:
            from PySide6 import QtWidgets

            form_layout.setSpacing(8)
            form_layout.setContentsMargins(5, 5, 5, 5)
            form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        except Exception:
            pass

    def setup_group_box(self, group_box: Any) -> None:
        try:
            group_box.setContentsMargins(8, 8, 8, 8)
        except Exception:
            pass

    def create_action_button(self, text: str, emoji: Optional[str] = None) -> Any:
        from PySide6 import QtWidgets

        button = QtWidgets.QPushButton()
        if emoji:
            button.setText(f"{emoji} {text}")
            if self._twemoji:
                try:
                    self._twemoji.set_button_icon(button, emoji, keep_text=True)
                except Exception:
                    pass
        else:
            button.setText(text)

        try:
            button.setMinimumHeight(35)
            button.setMinimumWidth(120)
        except Exception:
            pass
        return button

    def setup_table_widget(self, table: Any) -> None:
        try:
            from PySide6 import QtWidgets

            table.setAlternatingRowColors(False)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            vh = table.verticalHeader()
            if vh:
                vh.setDefaultSectionSize(25)
                vh.setVisible(False)
            hh = table.horizontalHeader()
            if hh:
                hh.setFixedHeight(30)
                hh.setStretchLastSection(True)
        except Exception:
            pass

    def setup_tab_widget(self, tab_widget: Any) -> None:
        try:
            from PySide6 import QtWidgets

            tab_widget.setTabPosition(QtWidgets.QTabWidget.North)
            tab_widget.setMovable(False)
            tab_widget.setUsesScrollButtons(True)
        except Exception:
            pass


def get_layout_manager(*_args, **_kwargs) -> UiCoreLayout:
    """Return the UI core layout adapter used by mini GUIs."""
    return UiCoreLayout()


