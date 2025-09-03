"""
Tick Visuals Demo (PySide6 + PyQtGraph)
=======================================

Showcases:
- Custom checkbox indicator (tick) styles via QSS
- QSlider tick positions/intervals
- PyQtGraph axis tick font, custom ticks, and grid alpha
"""

from typing import List, Tuple

from PySide6 import QtCore, QtGui, QtWidgets

try:
    import pyqtgraph as pg  # type: ignore
    PYQTGRAPH_AVAILABLE = True
except Exception:
    PYQTGRAPH_AVAILABLE = False
    pg = None  # type: ignore


class TickDemoWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tick Visuals Demo - PySide6")
        self.resize(900, 600)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        layout.addWidget(self._build_checkbox_group())
        layout.addWidget(self._build_slider_group())
        layout.addWidget(self._build_plot_group())

        # Apply local stylesheet for checkbox indicator demo
        # This is self-contained and does not depend on global theme
        self._apply_local_styles()

    def _build_checkbox_group(self) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox("Checkbox tick styles")
        vbox = QtWidgets.QVBoxLayout(group)
        vbox.setSpacing(6)

        # Default styled checkbox
        self.cb_default = QtWidgets.QCheckBox("Default (primary blue)")
        self.cb_default.setChecked(True)
        vbox.addWidget(self.cb_default)

        # Success variant using dynamic property for QSS targeting
        self.cb_success = QtWidgets.QCheckBox("Success variant (rounded green)")
        self.cb_success.setProperty("variant", "success")
        self.cb_success.setChecked(True)
        vbox.addWidget(self.cb_success)

        # Neutral/disabled showcase
        self.cb_disabled = QtWidgets.QCheckBox("Disabled state")
        self.cb_disabled.setChecked(True)
        self.cb_disabled.setEnabled(False)
        vbox.addWidget(self.cb_disabled)

        return group

    def _build_slider_group(self) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox("QSlider with ticks")
        vbox = QtWidgets.QVBoxLayout(group)
        vbox.setSpacing(6)

        info = QtWidgets.QLabel("Demonstrates tick positions and interval")
        info.setStyleSheet("color: #64748b; font-style: italic;")
        vbox.addWidget(info)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(40)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(10)  # major tick every 10 units
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        vbox.addWidget(self.slider)

        return group

    def _build_plot_group(self) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox("PyQtGraph axis ticks and grid")
        vbox = QtWidgets.QVBoxLayout(group)
        vbox.setSpacing(6)

        if not PYQTGRAPH_AVAILABLE:
            fallback = QtWidgets.QLabel("PyQtGraph not available. Install with: pip install pyqtgraph")
            fallback.setAlignment(QtCore.Qt.AlignCenter)
            fallback.setStyleSheet("color: #ef4444; font-weight: bold;")
            vbox.addWidget(fallback)
            return group

        # Configure PG for CPU rendering and white background
        pg.setConfigOptions(useOpenGL=False, antialias=True, background='w', foreground='k')

        self.plot_widget = pg.PlotWidget()
        plot_item = self.plot_widget.getPlotItem()

        # Labels
        plot_item.setLabels(left='Flux', bottom='Wavelength (Å)')

        # Axis pens and tick font
        axis_font = QtGui.QFont("Segoe UI", 9)
        for name in ('left', 'bottom'):
            axis = plot_item.getAxis(name)
            axis.setPen(pg.mkPen(color='black', width=1))
            axis.setTextPen(pg.mkPen(color='black'))
            axis.setTickFont(axis_font)

        # Stronger grid like preprocessing dialog
        plot_item.showGrid(x=True, y=True, alpha=0.3)

        # Demo data
        import numpy as np
        x = np.linspace(3000, 10000, 1200)
        y = np.sin((x - 3000) / 400.0) * 0.5 + 0.5
        plot_item.plot(x, y, pen=pg.mkPen(color='#3b82f6', width=2))

        # Custom bottom ticks: major every 1000 Å, minor every 500 Å
        major_ticks: List[Tuple[float, str]] = [(w, f"{w}") for w in range(3000, 11000, 1000)]
        minor_ticks: List[Tuple[float, str]] = [(w, "") for w in range(3500, 10500, 500) if w % 1000 != 0]
        plot_item.getAxis('bottom').setTicks([major_ticks, minor_ticks])

        # Set ranges with margin
        plot_item.setXRange(3000, 10000, padding=0)
        y_min = float(np.min(y)); y_max = float(np.max(y))
        pad = (y_max - y_min) * 0.1
        plot_item.setYRange(y_min - pad, y_max + pad, padding=0)

        vbox.addWidget(self.plot_widget)
        return group

    def _apply_local_styles(self) -> None:
        # Self-contained QSS for checkbox indicator styles and a simple slider theme
        qss = """
        QWidget { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9pt; }

        /* Checkbox indicator (global default: square blue) */
        QCheckBox { spacing: 6px; }
        QCheckBox::indicator {
            width: 16px; height: 16px;
            border: 2px solid #cbd5e1; border-radius: 3px; background: #ffffff;
        }
        QCheckBox::indicator:checked {
            background: #3b82f6; border: 2px solid #3b82f6;
        }
        /* Success variant (rounded green) via dynamic property */
        QCheckBox[variant="success"]::indicator {
            border-radius: 8px;
        }
        QCheckBox[variant="success"]::indicator:checked {
            background: #10b981; border-color: #10b981;
        }

        /* Simple slider styling */
        QSlider::groove:horizontal { height: 6px; background: #e5e7eb; border-radius: 3px; }
        QSlider::sub-page:horizontal { background: #3b82f6; border-radius: 3px; }
        QSlider::handle:horizontal { width: 14px; height: 14px; margin: -6px 0; background: white; border: 2px solid #3b82f6; border-radius: 7px; }
        """
        self.setStyleSheet(qss)


def main() -> None:
    app = QtWidgets.QApplication([])
    win = TickDemoWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()


