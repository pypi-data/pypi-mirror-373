"""
SNID SAGE - Button Palette Demo (PySide6)
=========================================

A developer/demo dialog to preview and tweak the colors used for dialog buttons
and compare them with the main GUI workflow button palette. It supports:
- Live preview of dialog button types (apply, cancel, utility, etc.)
- Quick editing of base colors (auto-generates hover/pressed variants)
- Reset to defaults or to main GUI workflow palette
- Export current palette to JSON (clipboard)

This does NOT change global theme permanently; it's a preview/testing tool.
"""

from typing import Dict, List
import json

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.button_palette_demo')
except Exception:  # pragma: no cover
    import logging
    _LOGGER = logging.getLogger('gui.button_palette_demo')


# Enhanced dialog button manager (provides the button type system and colors)
from snid_sage.interfaces.gui.utils.enhanced_dialog_button_manager import (
    EnhancedDialogButtonManager,
)

# Theme manager (for main GUI workflow/button palette reference)
try:
    from snid_sage.interfaces.gui.utils.pyside6_theme_manager import (
        get_pyside6_theme_manager,
    )
    THEME_MANAGER_AVAILABLE = True
except Exception:
    THEME_MANAGER_AVAILABLE = False


class PySide6ButtonPaletteDemoDialog(QtWidgets.QDialog):
    """Dialog to preview and tweak dialog button colors with live updates."""

    # Button types we expose for editing (keys must match EnhancedDialogButtonManager.BUTTON_COLORS base keys)
    EDITABLE_TYPES: List[str] = [
        'apply', 'secondary', 'cancel', 'utility', 'info', 'reset', 'navigation', 'neutral', 'accent'
    ]

    WORKFLOW_KEYS: List[str] = [
        'btn_load', 'btn_preprocessing', 'btn_redshift', 'btn_analysis', 'btn_advanced',
        'btn_ai', 'btn_settings', 'btn_reset'
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Button Palette Demo")
        self.resize(980, 640)
        self.setModal(False)

        # Make a local manager to help with lighten/darken and re-style
        self.button_manager = EnhancedDialogButtonManager()

        # Keep a deep copy of original colors so we can reset
        self.original_colors: Dict[str, str] = dict(EnhancedDialogButtonManager.BUTTON_COLORS)

        # Build UI
        self._build_ui()
        self._populate_workflow_palette()
        self._register_demo_buttons()

    # ---------- UI construction ----------
    def _build_ui(self) -> None:
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Left: live previews
        left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_layout.addWidget(left_splitter, 2)

        # Group 1: Dialog button types preview
        types_group = QtWidgets.QGroupBox("Dialog Button Types (live preview)")
        types_layout = QtWidgets.QGridLayout(types_group)
        types_layout.setContentsMargins(10, 10, 10, 10)
        types_layout.setHorizontalSpacing(8)
        types_layout.setVerticalSpacing(8)

        self.preview_buttons: Dict[str, QtWidgets.QPushButton] = {}
        row = 0
        for i, btn_type in enumerate(self.EDITABLE_TYPES):
            label = QtWidgets.QLabel(btn_type.title())
            types_layout.addWidget(label, row, 0)

            # Normal-size button
            normal_btn = QtWidgets.QPushButton("Sample")
            normal_btn.setObjectName(f"demo_{btn_type}_normal")
            self.preview_buttons[f"{btn_type}_normal"] = normal_btn
            types_layout.addWidget(normal_btn, row, 1)

            # Small-size button
            small_btn = QtWidgets.QPushButton("Small")
            small_btn.setObjectName(f"demo_{btn_type}_small")
            self.preview_buttons[f"{btn_type}_small"] = small_btn
            types_layout.addWidget(small_btn, row, 2)

            row += 1

        left_splitter.addWidget(types_group)

        # Group 2: Main GUI workflow colors (reference)
        workflow_group = QtWidgets.QGroupBox("Main GUI Workflow Colors (reference)")
        workflow_layout = QtWidgets.QGridLayout(workflow_group)
        workflow_layout.setContentsMargins(10, 10, 10, 10)
        workflow_layout.setHorizontalSpacing(8)
        workflow_layout.setVerticalSpacing(8)

        self.workflow_color_labels: Dict[str, QtWidgets.QLabel] = {}
        self.workflow_color_buttons: Dict[str, QtWidgets.QPushButton] = {}
        for idx, key in enumerate(self.WORKFLOW_KEYS):
            text = key.replace('btn_', '').title()
            lbl = QtWidgets.QLabel(text)
            workflow_layout.addWidget(lbl, idx, 0)

            # Color swatch button (disabled, just displays color)
            swatch = QtWidgets.QPushButton()
            swatch.setEnabled(False)
            swatch.setFixedWidth(140)
            self.workflow_color_buttons[key] = swatch
            workflow_layout.addWidget(swatch, idx, 1)

            # Hex label
            hex_lbl = QtWidgets.QLabel("")
            self.workflow_color_labels[key] = hex_lbl
            workflow_layout.addWidget(hex_lbl, idx, 2)

        left_splitter.addWidget(workflow_group)

        # Right: controls to edit colors
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(8)
        main_layout.addWidget(right_panel, 1)

        # Editor table
        self.editor_table = QtWidgets.QTableWidget()
        self.editor_table.setColumnCount(4)
        self.editor_table.setHorizontalHeaderLabels(["Type", "Base Color", "Pick", "Apply"])
        self.editor_table.horizontalHeader().setStretchLastSection(True)
        self.editor_table.setRowCount(len(self.EDITABLE_TYPES))

        self.hex_inputs: Dict[str, QtWidgets.QLineEdit] = {}
        for row_idx, t in enumerate(self.EDITABLE_TYPES):
            self.editor_table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(t))

            # Hex input
            hex_edit = QtWidgets.QLineEdit(self._get_base_color_hex(t))
            hex_edit.setMaxLength(7)
            hex_edit.setPlaceholderText("#RRGGBB")
            self.hex_inputs[t] = hex_edit
            self.editor_table.setCellWidget(row_idx, 1, hex_edit)

            # Pick button
            pick_btn = QtWidgets.QPushButton("Pick…")
            pick_btn.clicked.connect(lambda _, tp=t: self._pick_color(tp))
            self.editor_table.setCellWidget(row_idx, 2, pick_btn)

            # Apply button
            apply_btn = QtWidgets.QPushButton("Apply")
            apply_btn.clicked.connect(lambda _, tp=t: self._apply_color_for_type(tp))
            self.editor_table.setCellWidget(row_idx, 3, apply_btn)

        right_layout.addWidget(self.editor_table)

        # Interactive color picker
        self._build_color_picker(right_layout)

        # Actions
        actions_layout = QtWidgets.QHBoxLayout()
        right_layout.addLayout(actions_layout)

        self.reset_defaults_btn = QtWidgets.QPushButton("Reset to Defaults")
        self.reset_defaults_btn.clicked.connect(self._reset_to_defaults)
        actions_layout.addWidget(self.reset_defaults_btn)

        self.reset_main_gui_btn = QtWidgets.QPushButton("Reset to Main GUI Palette")
        self.reset_main_gui_btn.clicked.connect(self._reset_to_main_gui)
        actions_layout.addWidget(self.reset_main_gui_btn)

        actions_layout.addStretch()

        export_btn = QtWidgets.QPushButton("Copy JSON to Clipboard")
        export_btn.clicked.connect(self._export_palette_json)
        right_layout.addWidget(export_btn)

        # Footer info
        note = QtWidgets.QLabel("This tool previews colors only. It does not persist changes.")
        note.setStyleSheet("color: #64748b; font-style: italic;")
        right_layout.addWidget(note)

    # ---------- Helpers ----------
    def _register_demo_buttons(self) -> None:
        """Register all preview buttons with the manager using current colors."""
        for key, btn in self.preview_buttons.items():
            btn_type = key.split('_')[0]
            size = 'small' if key.endswith('small') else 'normal'
            self.button_manager.register_button(btn, button_type=btn_type, custom_config={'size_class': size})

    # ---------- Interactive picker ----------
    def _build_color_picker(self, parent_layout: QtWidgets.QVBoxLayout) -> None:
        group = QtWidgets.QGroupBox("Interactive Color Picker")
        layout = QtWidgets.QVBoxLayout(group)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Target type selector
        selector_row = QtWidgets.QHBoxLayout()
        selector_row.addWidget(QtWidgets.QLabel("Target Type:"))
        self.picker_type_combo = QtWidgets.QComboBox()
        self.picker_type_combo.addItems(self.EDITABLE_TYPES)
        self.picker_type_combo.currentTextChanged.connect(self._sync_picker_to_type)
        selector_row.addWidget(self.picker_type_combo)
        selector_row.addStretch()
        layout.addLayout(selector_row)

        # Hue slider
        hue_row = QtWidgets.QHBoxLayout()
        self.hue_label = QtWidgets.QLabel("Hue: 0")
        self.hue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.hue_slider.setRange(0, 359)
        self.hue_slider.valueChanged.connect(self._on_hue_changed)
        hue_row.addWidget(self.hue_label)
        hue_row.addWidget(self.hue_slider)
        layout.addLayout(hue_row)

        # SV selector + preview
        sv_row = QtWidgets.QHBoxLayout()
        self.sv_selector = _ColorSVSelector()
        self.sv_selector.colorChanged.connect(self._on_picker_color_changed)
        sv_row.addWidget(self.sv_selector, 1)

        preview_col = QtWidgets.QVBoxLayout()
        preview_col.addWidget(QtWidgets.QLabel("Selected:"))
        self.picker_preview = QtWidgets.QLabel()
        self.picker_preview.setFixedSize(56, 56)
        self.picker_preview.setStyleSheet("border: 1px solid #cbd5e1; border-radius: 4px;")
        preview_col.addWidget(self.picker_preview)
        preview_col.addStretch()
        sv_row.addLayout(preview_col)
        layout.addLayout(sv_row)

        # Apply button
        apply_row = QtWidgets.QHBoxLayout()
        self.picker_apply_btn = QtWidgets.QPushButton("Apply to Selected Type")
        self.picker_apply_btn.clicked.connect(self._apply_picker_to_type)
        apply_row.addWidget(self.picker_apply_btn)
        apply_row.addStretch()
        layout.addLayout(apply_row)

        parent_layout.addWidget(group)

        # Initialize picker from current type
        self._sync_picker_to_type(self.picker_type_combo.currentText())

    def _populate_workflow_palette(self) -> None:
        """Populate the main workflow color swatches from the theme manager if available."""
        if not THEME_MANAGER_AVAILABLE:
            return
        tm = get_pyside6_theme_manager()
        colors = tm.get_all_colors()
        for key in self.WORKFLOW_KEYS:
            hex_color = colors.get(key, '#999999')
            self._set_swatch(self.workflow_color_buttons[key], hex_color)
            self.workflow_color_labels[key].setText(hex_color)

    def _set_swatch(self, button: QtWidgets.QPushButton, hex_color: str) -> None:
        button.setStyleSheet(
            f"background-color: {hex_color}; border: 1px solid #cbd5e1; border-radius: 4px; min-height: 22px;"
        )

    def _get_base_color_hex(self, btn_type: str) -> str:
        """Get base color hex for a type from the manager's palette."""
        return EnhancedDialogButtonManager.BUTTON_COLORS.get(btn_type, '#888888')

    def _lighten(self, hex_color: str, factor: float) -> str:
        # Reuse manager's logic via a temporary method call
        return self.button_manager._lighten_color(hex_color, factor)

    def _darken(self, hex_color: str, factor: float) -> str:
        return self.button_manager._darken_color(hex_color, factor)

    # ---------- Actions ----------
    def _pick_color(self, btn_type: str) -> None:
        current_hex = self.hex_inputs[btn_type].text().strip() or self._get_base_color_hex(btn_type)
        color = QtGui.QColor(current_hex)
        if not color.isValid():
            color = QtGui.QColor('#888888')
        chosen = QtWidgets.QColorDialog.getColor(color, self, f"Pick color for {btn_type}")
        if chosen.isValid():
            new_hex = chosen.name().lower()
            self.hex_inputs[btn_type].setText(new_hex)
            self._apply_color_for_type(btn_type)

    def _on_hue_changed(self, value: int) -> None:
        self.hue_label.setText(f"Hue: {value}")
        self.sv_selector.setHue(value)

    def _on_picker_color_changed(self, color: QtGui.QColor) -> None:
        # Update preview swatch
        self.picker_preview.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #cbd5e1; border-radius: 4px;"
        )
        # Live-update hex input for selected type
        btn_type = self.picker_type_combo.currentText()
        self.hex_inputs[btn_type].setText(color.name())
        # Live-apply to preview buttons
        self._apply_color_for_type(btn_type)

    def _apply_picker_to_type(self) -> None:
        btn_type = self.picker_type_combo.currentText()
        hex_color = self.sv_selector.currentColor().name()
        self.hex_inputs[btn_type].setText(hex_color)
        self._apply_color_for_type(btn_type)

    def _sync_picker_to_type(self, btn_type: str) -> None:
        hex_color = self._get_base_color_hex(btn_type)
        qc = QtGui.QColor(hex_color)
        # Handle gray (no hue) case gracefully
        hue = qc.hue() if qc.hue() >= 0 else 0
        sat = qc.saturationF() if qc.isValid() else 0.0
        val = qc.valueF() if qc.isValid() else 1.0
        self.hue_slider.blockSignals(True)
        self.hue_slider.setValue(hue)
        self.hue_slider.blockSignals(False)
        self.sv_selector.blockSignals(True)
        self.sv_selector.setHue(hue)
        self.sv_selector.setSV(sat, val)
        self.sv_selector.blockSignals(False)
        self._on_picker_color_changed(self.sv_selector.currentColor())

    def _apply_color_for_type(self, btn_type: str) -> None:
        base_hex = self.hex_inputs[btn_type].text().strip()
        if not base_hex.startswith('#') or len(base_hex) != 7:
            QtWidgets.QMessageBox.warning(self, "Invalid Color", f"Enter a valid hex color for {btn_type} (e.g., #3b82f6)")
            return

        # Update global palette for the type and its hover/pressed variants
        EnhancedDialogButtonManager.BUTTON_COLORS[btn_type] = base_hex
        EnhancedDialogButtonManager.BUTTON_COLORS[f"{btn_type}_hover"] = self._darken(base_hex, 0.10)
        EnhancedDialogButtonManager.BUTTON_COLORS[f"{btn_type}_pressed"] = self._darken(base_hex, 0.18)

        # Re-apply styling to preview buttons of this type
        for key, btn in self.preview_buttons.items():
            if key.startswith(btn_type + "_"):
                # Trigger a restyle by toggling enabled state
                self.button_manager.update_button_state(btn, enabled=True)

    def _reset_to_defaults(self) -> None:
        EnhancedDialogButtonManager.BUTTON_COLORS.update(self.original_colors)
        # Refresh editor inputs
        for t in self.EDITABLE_TYPES:
            self.hex_inputs[t].setText(self._get_base_color_hex(t))
            self._apply_color_for_type(t)

    def _reset_to_main_gui(self) -> None:
        """Reset dialog button types to colors inspired by main GUI workflow palette."""
        # Map dialog types to workflow palette keys
        if THEME_MANAGER_AVAILABLE:
            tm = get_pyside6_theme_manager()
            c = tm.get_all_colors()
            mapping = {
                'apply': c.get('btn_success', '#10b981'),
                'secondary': c.get('btn_analysis', '#BC5090'),
                'cancel': c.get('btn_reset', '#A65965'),
                'utility': c.get('btn_advanced', '#58508D'),
                'info': c.get('btn_primary', '#3b82f6'),
                'reset': c.get('btn_reset', '#A65965'),
                'navigation': c.get('btn_preprocessing', '#FF6361'),
                'neutral': c.get('btn_ai', '#003F5C'),
                'accent': c.get('btn_success', '#10b981'),
            }
        else:
            # Fallback constants matching current defaults
            mapping = {
                'apply': '#22c55e',
                'secondary': '#BC5090',
                'cancel': '#A65965',
                'utility': '#58508D',
                'info': '#6366f1',
                'reset': '#6E6E6E',
                'navigation': '#FF6361',
                'neutral': '#003F5C',
                'accent': '#22c55e',
            }

        for t, hex_color in mapping.items():
            self.hex_inputs[t].setText(hex_color)
            self._apply_color_for_type(t)

    def _export_palette_json(self) -> None:
        """Copy current base colors for editable types as JSON to clipboard."""
        export = {t: self._get_base_color_hex(t) for t in self.EDITABLE_TYPES}
        json_text = json.dumps(export, indent=2)
        QtWidgets.QApplication.clipboard().setText(json_text)
        QtWidgets.QMessageBox.information(self, "Exported", "Current palette copied to clipboard as JSON")


def show_button_palette_demo(parent=None) -> PySide6ButtonPaletteDemoDialog:
    dialog = PySide6ButtonPaletteDemoDialog(parent)
    dialog.show()
    return dialog


class _ColorSVSelector(QtWidgets.QWidget):
    """Simple Saturation/Value selector with fixed hue and live color reporting."""
    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        self._hue = 0  # 0..359
        self._s = 1.0  # 0..1
        self._v = 1.0  # 0..1
        self._cache_img: QtGui.QImage | None = None
        self._cache_hue: int | None = None
        # Do not track passive mouse moves; only update on click/drag
        self.setMouseTracking(False)

    def setHue(self, hue: int) -> None:
        hue = max(0, min(359, int(hue)))
        if hue != self._hue:
            self._hue = hue
            self._cache_img = None
            self.update()
            self.colorChanged.emit(self.currentColor())

    def setSV(self, s: float, v: float) -> None:
        s = max(0.0, min(1.0, float(s)))
        v = max(0.0, min(1.0, float(v)))
        if s != self._s or v != self._v:
            self._s, self._v = s, v
            self.update()
            self.colorChanged.emit(self.currentColor())

    def currentColor(self) -> QtGui.QColor:
        return QtGui.QColor.fromHsv(self._hue, int(self._s * 255), int(self._v * 255))

    def _ensure_cache(self) -> None:
        if self._cache_img is not None and self._cache_hue == self._hue and \
           self._cache_img.size() == self.size():
            return
        w, h = self.width(), self.height()
        img = QtGui.QImage(w, h, QtGui.QImage.Format_RGB32)
        for y in range(h):
            v = 1.0 - (y / max(1, h - 1))
            for x in range(w):
                s = x / max(1, w - 1)
                qc = QtGui.QColor.fromHsv(self._hue, int(s * 255), int(v * 255))
                img.setPixel(x, y, qc.rgb())
        self._cache_img = img
        self._cache_hue = self._hue

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        self._ensure_cache()
        painter = QtGui.QPainter(self)
        if self._cache_img is not None:
            painter.drawImage(0, 0, self._cache_img)
        # Draw selection marker
        x = self._s * (self.width() - 1)
        y = (1.0 - self._v) * (self.height() - 1)
        pen = QtGui.QPen(QtGui.QColor('#ffffff'))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(QtCore.QPointF(x, y), 6, 6)
        pen = QtGui.QPen(QtGui.QColor('#000000'))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawEllipse(QtCore.QPointF(x, y), 7, 7)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._update_from_pos(event.position())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # Only update while dragging with left button
        if event.buttons() & QtCore.Qt.LeftButton:
            self._update_from_pos(event.position())

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self._cache_img = None
        super().resizeEvent(event)

    def _update_from_pos(self, pos: QtCore.QPointF) -> None:
        w, h = max(1, self.width() - 1), max(1, self.height() - 1)
        s = max(0.0, min(1.0, pos.x() / w))
        v = max(0.0, min(1.0, 1.0 - (pos.y() / h)))
        if s != self._s or v != self._v:
            self._s, self._v = s, v
            self.update()
            self.colorChanged.emit(self.currentColor())


