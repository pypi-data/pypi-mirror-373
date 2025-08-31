from PySide6 import QtWidgets


def create_options(dialog, layout: QtWidgets.QVBoxLayout) -> None:
    desc = QtWidgets.QLabel("Review the complete preprocessing pipeline and finalize settings.")
    desc.setWordWrap(True)
    desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
    layout.addWidget(desc)

    summary_group = QtWidgets.QGroupBox("Preprocessing Summary")
    summary_layout = QtWidgets.QVBoxLayout(summary_group)
    dialog.summary_text = QtWidgets.QTextEdit()
    dialog.summary_text.setReadOnly(True)
    dialog.summary_text.setMaximumHeight(200)
    _update_summary(dialog)
    summary_layout.addWidget(dialog.summary_text)
    layout.addWidget(summary_group)


def _update_summary(dialog):
    if not hasattr(dialog, 'summary_text') or not dialog.preview_calculator:
        return
    summary = "Applied Preprocessing Steps:\n\n"
    steps = getattr(dialog.preview_calculator, 'applied_steps', [])
    if len(steps) == 0:
        summary += "No preprocessing steps applied yet.\n"
    else:
        for i, step in enumerate(steps):
            summary += f"{i+1}. {step['type'].replace('_', ' ').title()}\n"
            if 'kwargs' in step:
                for key, value in step['kwargs'].items():
                    if key != 'step_index':
                        summary += f"   {key}: {value}\n"
            summary += "\n"
    dialog.summary_text.setPlainText(summary)


