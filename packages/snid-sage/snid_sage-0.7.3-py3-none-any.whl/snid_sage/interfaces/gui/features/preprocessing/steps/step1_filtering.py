from PySide6 import QtWidgets

from snid_sage.interfaces.gui.components.widgets.flexible_number_input import (
    create_flexible_int_input,
)


def create_options(dialog, layout: QtWidgets.QVBoxLayout) -> None:
    desc = QtWidgets.QLabel("Apply Savitzky-Golay smoothing filter to reduce noise in the spectrum.")
    desc.setWordWrap(True)
    desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
    layout.addWidget(desc)

    filter_group = QtWidgets.QGroupBox("Filter Configuration")
    filter_layout = QtWidgets.QVBoxLayout(filter_group)

    dialog.filter_type_group = QtWidgets.QButtonGroup()
    dialog.no_filter_rb = QtWidgets.QRadioButton("No filtering")
    dialog.no_filter_rb.setChecked(dialog.processing_params['filter_type'] == 'none')
    dialog.no_filter_rb.toggled.connect(lambda *_: _on_filter_type_changed(dialog))
    dialog.filter_type_group.addButton(dialog.no_filter_rb, 0)
    filter_layout.addWidget(dialog.no_filter_rb)

    fixed_layout = QtWidgets.QHBoxLayout()
    dialog.fixed_filter_rb = QtWidgets.QRadioButton("Fixed window:")
    dialog.fixed_filter_rb.setChecked(dialog.processing_params['filter_type'] == 'fixed')
    dialog.fixed_filter_rb.toggled.connect(lambda *_: _on_filter_type_changed(dialog))
    dialog.filter_type_group.addButton(dialog.fixed_filter_rb, 1)
    fixed_layout.addWidget(dialog.fixed_filter_rb)

    dialog.fixed_window_spin = create_flexible_int_input(min_val=3, max_val=101, default=11)
    filter_window = dialog.processing_params.get('filter_window', 11)
    dialog.fixed_window_spin.setValue(filter_window)
    # Use valueChanged to update preview immediately (editingFinished only fires on focus-out)
    dialog.fixed_window_spin.valueChanged.connect(lambda *_: _on_fixed_filter_params_changed(dialog))
    fixed_layout.addWidget(dialog.fixed_window_spin)

    fixed_layout.addWidget(QtWidgets.QLabel("order:"))
    dialog.polyorder_spin = create_flexible_int_input(min_val=1, max_val=10, default=3)
    dialog.polyorder_spin.setValue(dialog.processing_params['filter_order'])
    # Match continuum knots behavior for live updates
    dialog.polyorder_spin.valueChanged.connect(lambda *_: _on_fixed_filter_params_changed(dialog))
    fixed_layout.addWidget(dialog.polyorder_spin)

    fixed_layout.addStretch()
    filter_layout.addLayout(fixed_layout)

    try:
        dialog.filter_type_group.buttonClicked.connect(lambda *_: _on_filter_type_changed(dialog))
    except Exception:
        pass

    _update_filter_inputs_enabled_state(dialog)
    layout.addWidget(filter_group)
    dialog._update_preview()


def apply_step(dialog) -> None:
    # Determine filter type
    try:
        if hasattr(dialog, 'fixed_filter_rb') and dialog.fixed_filter_rb.isChecked():
            filter_type = 'fixed'
        elif hasattr(dialog, 'no_filter_rb') and dialog.no_filter_rb.isChecked():
            filter_type = 'none'
        else:
            filter_type = dialog.processing_params.get('filter_type', 'none')
    except Exception:
        filter_type = dialog.processing_params.get('filter_type', 'none')

    if filter_type != 'fixed':
        return

    window = 11
    polyorder = 3
    try:
        if hasattr(dialog, 'fixed_window_spin'):
            window = int(dialog.fixed_window_spin.value())
        if hasattr(dialog, 'polyorder_spin'):
            polyorder = int(dialog.polyorder_spin.value())
    except Exception:
        pass

    dialog.preview_calculator.apply_step(
        "savgol_filter", filter_type="fixed", value=window, polyorder=polyorder, step_index=1
    )


def calculate_preview(dialog):
    filter_type = dialog.processing_params.get('filter_type', 'none')
    if filter_type == 'none':
        return dialog.preview_calculator.get_current_state()

    try:
        polyorder_val = None
        if hasattr(dialog, 'polyorder_spin') and dialog.polyorder_spin is not None:
            polyorder_val = int(dialog.polyorder_spin.value())
        if polyorder_val is None:
            polyorder_val = int(dialog.processing_params.get('filter_order', 3))

        if filter_type == 'fixed':
            win_val = None
            if hasattr(dialog, 'fixed_window_spin') and dialog.fixed_window_spin is not None:
                win_val = int(dialog.fixed_window_spin.value())
            if win_val is None:
                win_val = int(dialog.processing_params.get('filter_window', 11))
            return dialog.preview_calculator.preview_step(
                "savgol_filter", filter_type='fixed', value=win_val, polyorder=polyorder_val
            )
    except Exception:
        pass
    return dialog.preview_calculator.get_current_state()


def _on_filter_type_changed(dialog):
    if dialog.no_filter_rb.isChecked():
        dialog.processing_params['filter_type'] = 'none'
    elif dialog.fixed_filter_rb.isChecked():
        dialog.processing_params['filter_type'] = 'fixed'
    _update_filter_inputs_enabled_state(dialog)
    dialog._update_preview()


def _update_filter_inputs_enabled_state(dialog):
    fixed = dialog.processing_params.get('filter_type') == 'fixed'
    if hasattr(dialog, 'fixed_window_spin') and dialog.fixed_window_spin is not None:
        dialog.fixed_window_spin.setEnabled(fixed)
    if hasattr(dialog, 'polyorder_spin') and dialog.polyorder_spin is not None:
        dialog.polyorder_spin.setEnabled(fixed)


def _on_fixed_filter_params_changed(dialog):
    try:
        if hasattr(dialog, 'fixed_window_spin'):
            dialog.processing_params['filter_window'] = int(dialog.fixed_window_spin.value())
        if hasattr(dialog, 'polyorder_spin'):
            dialog.processing_params['filter_order'] = int(dialog.polyorder_spin.value())
    except Exception:
        pass
    dialog._update_preview()


