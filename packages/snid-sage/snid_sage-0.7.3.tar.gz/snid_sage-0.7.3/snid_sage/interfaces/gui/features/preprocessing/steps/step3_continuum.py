from PySide6 import QtWidgets, QtCore

from snid_sage.interfaces.gui.components.widgets.flexible_number_input import (
    create_flexible_int_input,
)


def create_options(dialog, layout: QtWidgets.QVBoxLayout) -> None:
    desc = QtWidgets.QLabel("Fit and subtract the continuum. Use interactive editing for fine-tuning.")
    desc.setWordWrap(True)
    desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
    layout.addWidget(desc)

    method_group = QtWidgets.QGroupBox("Spline Continuum Fitting")
    method_layout = QtWidgets.QVBoxLayout(method_group)

    spline_layout = QtWidgets.QHBoxLayout()
    spline_label = QtWidgets.QLabel("Number of knots:")
    spline_label.setStyleSheet("color: #374151; font-weight: 500;")
    spline_layout.addWidget(spline_label)

    dialog.spline_knots_spin = create_flexible_int_input(min_val=3, max_val=50, default=13)
    dialog.spline_knots_spin.setValue(dialog.processing_params['spline_knots'])
    dialog.spline_knots_spin.valueChanged.connect(lambda *_: _on_spline_knots_changed(dialog))
    spline_layout.addWidget(dialog.spline_knots_spin)

    spline_layout.addStretch()
    method_layout.addLayout(spline_layout)
    layout.addWidget(method_group)

    # Interactive controls
    if dialog.continuum_widget:
        continuum_controls = dialog.continuum_widget.create_interactive_controls(dialog.options_frame)
        layout.addWidget(continuum_controls)
        _initialize_continuum_points_if_needed(dialog)
    else:
        unavailable_group = QtWidgets.QGroupBox("Interactive Continuum Editing (Unavailable)")
        unavailable_layout = QtWidgets.QVBoxLayout(unavailable_group)
        msg = QtWidgets.QLabel("Interactive continuum editing requires PyQtGraph.\nInstall with: pip install pyqtgraph")
        msg.setStyleSheet("color: #f59e0b; font-style: italic;")
        msg.setWordWrap(True)
        unavailable_layout.addWidget(msg)
        layout.addWidget(unavailable_group)


def apply_step(dialog) -> None:
    if dialog.continuum_widget and dialog.continuum_widget.is_interactive_mode():
        wave_grid, manual_continuum = dialog.continuum_widget.get_manual_continuum_array()
        if len(manual_continuum) > 0:
            dialog.preview_calculator.apply_step(
                "interactive_continuum", manual_continuum=manual_continuum, wave_grid=wave_grid, step_index=3
            )
        return

    knotnum = 13
    try:
        if hasattr(dialog, 'spline_knots_spin') and dialog.spline_knots_spin is not None:
            knotnum = int(dialog.spline_knots_spin.value())
    except Exception:
        pass
    dialog.preview_calculator.apply_step("continuum_fit", method="spline", knotnum=knotnum, step_index=3)


def calculate_preview(dialog):
    method = dialog.processing_params['continuum_method']
    if method == 'spline':
        knotnum = dialog.processing_params.get('spline_knots', 13)
        return dialog.preview_calculator.preview_step("continuum_fit", method="spline", knotnum=knotnum)
    return dialog.preview_calculator.get_current_state()


def _on_spline_knots_changed(dialog):
    dialog.processing_params['spline_knots'] = dialog.spline_knots_spin.value()
    if dialog.current_step == 3 and dialog.continuum_widget and dialog.processing_params['continuum_method'] == 'spline':
        knotnum = dialog.spline_knots_spin.value()
        dialog.continuum_widget.update_continuum_from_fit(knotnum)
        dialog.continuum_widget._has_manual_changes = False
    dialog._update_preview()


def _initialize_continuum_points_if_needed(dialog):
    if dialog.current_step == 3 and dialog.continuum_widget:
        current_points = dialog.continuum_widget.get_continuum_points()
        if not current_points:
            _update_continuum_points_for_current_settings(dialog)
            dialog._update_preview()


def _update_continuum_points_for_current_settings(dialog):
    if dialog.current_step == 3 and dialog.continuum_widget:
        if hasattr(dialog.continuum_widget, 'has_manual_changes') and dialog.continuum_widget.has_manual_changes():
            return
        method = dialog.processing_params['continuum_method']
        dialog.continuum_widget.set_current_method(method)
        dialog.continuum_widget.reset_to_fitted_continuum()


