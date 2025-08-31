from PySide6 import QtWidgets

from snid_sage.interfaces.gui.components.widgets.flexible_number_input import (
    create_flexible_double_input,
)


def create_options(dialog, layout: QtWidgets.QVBoxLayout) -> None:
    desc = QtWidgets.QLabel("Apply edge tapering to prevent artifacts at spectrum boundaries.")
    desc.setWordWrap(True)
    desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
    layout.addWidget(desc)

    apod_group = QtWidgets.QGroupBox("Apodization Configuration")
    apod_layout = QtWidgets.QVBoxLayout(apod_group)

    dialog.apodize_cb = QtWidgets.QCheckBox("Apply edge apodization")
    dialog.apodize_cb.setChecked(dialog.processing_params['apply_apodization'])
    dialog.apodize_cb.toggled.connect(lambda *_: _on_apodize_toggled(dialog))
    apod_layout.addWidget(dialog.apodize_cb)

    param_layout = QtWidgets.QHBoxLayout()
    param_layout.addWidget(QtWidgets.QLabel("Edge fraction:"))
    dialog.apod_percent_spin = create_flexible_double_input(min_val=1.0, max_val=50.0, suffix=" %", default=10.0)
    dialog.apod_percent_spin.setValue(dialog.processing_params['apod_percent'])
    dialog.apod_percent_spin.valueChanged.connect(lambda *_: _on_apod_percent_changed(dialog))
    param_layout.addWidget(dialog.apod_percent_spin)
    param_layout.addStretch()
    apod_layout.addLayout(param_layout)
    layout.addWidget(apod_group)

    info_text = QtWidgets.QLabel(
        "Apodization applies a smooth taper to the spectrum edges, preventing discontinuities that could affect Fourier-based analysis."
    )
    info_text.setWordWrap(True)
    info_text.setStyleSheet("color: #64748b; font-size: 10pt; font-style: italic;")
    layout.addWidget(info_text)


def apply_step(dialog) -> None:
    apply_apodization = False
    percent = 10.0
    try:
        if hasattr(dialog, 'apodize_cb') and dialog.apodize_cb is not None:
            apply_apodization = bool(dialog.apodize_cb.isChecked())
        if hasattr(dialog, 'apod_percent_spin') and dialog.apod_percent_spin is not None:
            percent = float(dialog.apod_percent_spin.value())
    except Exception:
        pass
    if apply_apodization:
        dialog.preview_calculator.apply_step("apodization", percent=percent, step_index=4)


def calculate_preview(dialog):
    try:
        if hasattr(dialog, 'apodize_cb') and dialog.apodize_cb.isChecked():
            percent = dialog.apod_percent_spin.value() if hasattr(dialog, 'apod_percent_spin') else 10.0
            if 0 <= percent <= 50:
                return dialog.preview_calculator.preview_step("apodization", percent=percent)
    except Exception:
        pass
    return dialog.preview_calculator.get_current_state()


def _on_apodize_toggled(dialog):
    dialog.processing_params['apply_apodization'] = bool(dialog.apodize_cb.isChecked()) if hasattr(dialog, 'apodize_cb') else False
    dialog._update_preview()


def _on_apod_percent_changed(dialog):
    try:
        if hasattr(dialog, 'apod_percent_spin') and dialog.apod_percent_spin is not None:
            dialog.processing_params['apod_percent'] = float(dialog.apod_percent_spin.value())
    except Exception:
        pass
    dialog._update_preview()


