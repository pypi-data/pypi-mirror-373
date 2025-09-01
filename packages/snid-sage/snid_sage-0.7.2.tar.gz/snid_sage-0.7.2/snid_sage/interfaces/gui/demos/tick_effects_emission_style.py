"""
Emission-style Tick Effects Demo (PySide6)
=========================================

Replicates the Emission Lines dialog visual style for selection controls:
- Pill-style QRadioButton and QCheckBox with accent variants
- Hover/checked effects like the SN/Galaxy buttons
- Size variants via dynamic properties

Usage: python snid_sage/interfaces/gui/demos/tick_effects_emission_style.py
"""

from PySide6 import QtCore, QtGui, QtWidgets


ACCENTS = {
    "primary": ("#3b82f6", "#2563eb"),
    "success": ("#10b981", "#059669"),
    "warning": ("#f59e0b", "#d97706"),
    "danger": ("#ef4444", "#dc2626"),
    "neutral": ("#6b7280", "#4b5563"),
}


class EmissionTickDemo(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Emission-style Tick Effects Demo")
        self.resize(900, 600)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(self._build_radio_group())
        layout.addWidget(self._build_checkbox_group())
        layout.addStretch()

        self._apply_emission_stylesheet()

    def _build_radio_group(self) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox("Radio buttons (pill-style, accent + size variants)")
        vbox = QtWidgets.QVBoxLayout(group)
        vbox.setSpacing(6)

        row1 = QtWidgets.QHBoxLayout(); vbox.addLayout(row1)
        rb1 = QtWidgets.QRadioButton("SN Mode (primary)")
        rb1.setProperty("accent", "primary")
        rb1.setProperty("size", "normal")
        rb1.setChecked(True)
        row1.addWidget(rb1)

        rb2 = QtWidgets.QRadioButton("Galaxy Mode (neutral)")
        rb2.setProperty("accent", "neutral")
        rb2.setProperty("size", "normal")
        row1.addWidget(rb2)

        row2 = QtWidgets.QHBoxLayout(); vbox.addLayout(row2)
        rb3 = QtWidgets.QRadioButton("Success (green)")
        rb3.setProperty("accent", "success")
        rb3.setProperty("size", "small")
        row2.addWidget(rb3)

        rb4 = QtWidgets.QRadioButton("Warning (orange)")
        rb4.setProperty("accent", "warning")
        rb4.setProperty("size", "large")
        row2.addWidget(rb4)

        # Group them so only one can be selected per row
        g1 = QtWidgets.QButtonGroup(group); g1.addButton(rb1); g1.addButton(rb2)
        g2 = QtWidgets.QButtonGroup(group); g2.addButton(rb3); g2.addButton(rb4)

        return group

    def _build_checkbox_group(self) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox("Checkboxes (pill-style, accent + size variants)")
        vbox = QtWidgets.QVBoxLayout(group)
        vbox.setSpacing(6)

        row1 = QtWidgets.QHBoxLayout(); vbox.addLayout(row1)
        cb1 = QtWidgets.QCheckBox("Overlay SN lines")
        cb1.setProperty("accent", "primary"); cb1.setProperty("size", "normal")
        cb1.setChecked(True)
        row1.addWidget(cb1)

        cb2 = QtWidgets.QCheckBox("Overlay galaxy lines")
        cb2.setProperty("accent", "neutral"); cb2.setProperty("size", "normal")
        row1.addWidget(cb2)

        row2 = QtWidgets.QHBoxLayout(); vbox.addLayout(row2)
        cb3 = QtWidgets.QCheckBox("Auto analyze (success)")
        cb3.setProperty("accent", "success"); cb3.setProperty("size", "small")
        cb3.setChecked(True)
        row2.addWidget(cb3)

        cb4 = QtWidgets.QCheckBox("Danger action")
        cb4.setProperty("accent", "danger"); cb4.setProperty("size", "large")
        row2.addWidget(cb4)

        row3 = QtWidgets.QHBoxLayout(); vbox.addLayout(row3)
        cb5 = QtWidgets.QCheckBox("Disabled example")
        cb5.setProperty("accent", "primary")
        cb5.setEnabled(False); cb5.setChecked(True)
        row3.addWidget(cb5)

        return group

    def _apply_emission_stylesheet(self) -> None:
        # Base colors akin to your Emission dialog
        base_bg = "#f8fafc"; base_text = "#1e293b"; border = "#cbd5e1"

        # Dynamic QSS with accent selectors and size variants
        qss = f"""
        QWidget {{ font-family: 'Segoe UI', Arial, sans-serif; color: {base_text}; }}
        QGroupBox {{ font-weight: bold; border: 1px solid {border}; border-radius: 6px; padding-top: 10px; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; }}

        /* Pill-style radios/checkboxes: hide default indicator and style the control itself */
        QRadioButton, QCheckBox {{
            background: {base_bg};
            border: 2px solid {border};
            border-radius: 18px;
            padding: 6px 12px;
        }}
        QRadioButton:hover, QCheckBox:hover {{ background: #f1f5f9; }}
        QRadioButton:focus, QCheckBox:focus {{ border-color: #2563eb; }}
        QRadioButton:disabled, QCheckBox:disabled {{ color: #94a3b8; border-color: #e2e8f0; }}

        /* Remove the default indicators for a clean pill look */
        QRadioButton::indicator, QCheckBox::indicator {{ width: 0px; height: 0px; }}

        /* Size variants */
        QRadioButton[size="small"], QCheckBox[size="small"] {{ padding: 4px 10px; font-size: 9pt; border-radius: 15px; }}
        QRadioButton[size="normal"], QCheckBox[size="normal"] {{ padding: 6px 12px; font-size: 10pt; }}
        QRadioButton[size="large"], QCheckBox[size="large"] {{ padding: 8px 14px; font-size: 11pt; border-radius: 20px; }}

        /* Checked state default (primary) */
        QRadioButton:checked, QCheckBox:checked {{
            background: {ACCENTS['primary'][0]};
            border: 2px solid {ACCENTS['primary'][1]};
            color: white;
        }}
        QRadioButton:checked:hover, QCheckBox:checked:hover {{ background: {ACCENTS['primary'][1]}; }}

        /* Accent overrides */
        QRadioButton[accent="neutral"]:checked, QCheckBox[accent="neutral"]:checked {{
            background: {ACCENTS['neutral'][0]}; border-color: {ACCENTS['neutral'][1]};
        }}
        QRadioButton[accent="neutral"]:checked:hover, QCheckBox[accent="neutral"]:checked:hover {{
            background: {ACCENTS['neutral'][1]};
        }}

        QRadioButton[accent="success"]:checked, QCheckBox[accent="success"]:checked {{
            background: {ACCENTS['success'][0]}; border-color: {ACCENTS['success'][1]};
        }}
        QRadioButton[accent="success"]:checked:hover, QCheckBox[accent="success"]:checked:hover {{
            background: {ACCENTS['success'][1]};
        }}

        QRadioButton[accent="warning"]:checked, QCheckBox[accent="warning"]:checked {{
            background: {ACCENTS['warning'][0]}; border-color: {ACCENTS['warning'][1]};
        }}
        QRadioButton[accent="warning"]:checked:hover, QCheckBox[accent="warning"]:checked:hover {{
            background: {ACCENTS['warning'][1]};
        }}

        QRadioButton[accent="danger"]:checked, QCheckBox[accent="danger"]:checked {{
            background: {ACCENTS['danger'][0]}; border-color: {ACCENTS['danger'][1]};
        }}
        QRadioButton[accent="danger"]:checked:hover, QCheckBox[accent="danger"]:checked:hover {{
            background: {ACCENTS['danger'][1]};
        }}
        """
        self.setStyleSheet(qss)


def main() -> None:
    app = QtWidgets.QApplication([])
    win = EmissionTickDemo()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()


