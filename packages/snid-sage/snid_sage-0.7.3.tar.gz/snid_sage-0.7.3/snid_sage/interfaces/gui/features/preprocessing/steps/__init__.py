"""
Step handlers for the Advanced Preprocessing workflow (PySide6 GUI).

Each step module exposes three primary call points that operate on the
`PySide6PreprocessingDialog` instance passed as `dialog`:

- create_options(dialog, layout): Build the left-panel options UI for the step
- apply_step(dialog): Apply the step to the dialog's preview calculator
- calculate_preview(dialog): Return (wave, flux) preview for the current step

This keeps the main dialog short and focused on orchestration.
"""

from .step0_masking import create_options as create_step0_options, apply_step as apply_step0, calculate_preview as calculate_step0_preview
from .step1_filtering import create_options as create_step1_options, apply_step as apply_step1, calculate_preview as calculate_step1_preview
from .step2_rebinning import create_options as create_step2_options, apply_step as apply_step2, calculate_preview as calculate_step2_preview
from .step3_continuum import create_options as create_step3_options, apply_step as apply_step3, calculate_preview as calculate_step3_preview
from .step4_apodization import create_options as create_step4_options, apply_step as apply_step4, calculate_preview as calculate_step4_preview
from .step5_review import create_options as create_step5_options

__all__ = [
    "create_step0_options", "apply_step0", "calculate_step0_preview",
    "create_step1_options", "apply_step1", "calculate_step1_preview",
    "create_step2_options", "apply_step2", "calculate_step2_preview",
    "create_step3_options", "apply_step3", "calculate_step3_preview",
    "create_step4_options", "apply_step4", "calculate_step4_preview",
    "create_step5_options",
]


