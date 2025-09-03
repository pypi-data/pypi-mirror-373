"""
SNID SAGE GUI Dialogs
====================

Collection of dialog windows for the SNID SAGE GUI interface.

Available dialogs:
- PreprocessingDialog: Spectrum preprocessing configuration
- PreprocessingSelectionDialog: Preprocessing mode selection
- ConfigurationDialog: SNID analysis parameters configuration  
- MaskManagerDialog: Spectrum masking management
- AISummaryDialog: LLM-generated analysis summaries
- ResultsDialog: Analysis results viewing
- SettingsDialog: GUI settings and preferences
- ShortcutsDialog: Keyboard shortcuts and hotkeys reference
- ManualRedshiftDialog: Manual galaxy redshift determination
- MultiStepEmissionAnalysisDialog: Multi-step supernova emission line analysis tool
"""

# preprocessing_dialog moved to OLD_ - use PySide6 version instead
# from .preprocessing_dialog import PreprocessingDialog
# preprocessing_selection_dialog moved to OLD_ - use PySide6 version instead
# from .preprocessing_selection_dialog import PreprocessingSelectionDialog
# configuration_dialog moved to OLD_ - use PySide6 version instead
# from .configuration_dialog import ModernSNIDOptionsDialog, show_snid_options_dialog
# mask_manager_dialog moved to OLD_ - use PySide6 version instead
# from .mask_manager_dialog import MaskManagerDialog

# settings_dialog moved to OLD_ - use PySide6 version instead
# from .settings_dialog import GUISettingsDialog, show_gui_settings_dialog
# manual_redshift_dialog moved to OLD_ - use PySide6 version instead
# from .manual_redshift_dialog import ManualRedshiftDialog, show_manual_redshift_dialog
# multi_step_emission_dialog moved to OLD_ - use PySide6 version instead
# from .multi_step_emission_dialog import MultiStepEmissionAnalysisDialog, show_multi_step_emission_dialog
# snid_analysis_dialog moved to OLD_ - use PySide6 version instead
# from .snid_analysis_dialog import SNIDAnalysisDialog, show_snid_analysis_dialog

__all__ = [
    # All dialogs moved to OLD_ - use PySide6 versions instead
    # 'PreprocessingDialog',  # Moved to OLD_ - use PySide6 version
    # 'PreprocessingSelectionDialog',  # Moved to OLD_ - use PySide6 version
    # 'ModernSNIDOptionsDialog',  # Moved to OLD_ - use PySide6 version
    # 'show_snid_options_dialog',  # Moved to OLD_ - use PySide6 version
    # 'MaskManagerDialog',  # Moved to OLD_ - use PySide6 version
    # 'AISummaryDialog',  # Moved to OLD_ - use PySide6 version
    
    # 'GUISettingsDialog',  # Moved to OLD_ - use PySide6 version
    # 'show_gui_settings_dialog',  # Moved to OLD_ - use PySide6 version
    # 'ManualRedshiftDialog',  # Moved to OLD_ - use PySide6 version
    # 'show_manual_redshift_dialog',  # Moved to OLD_ - use PySide6 version
    # 'MultiStepEmissionAnalysisDialog',  # Moved to OLD_ - use PySide6 version
    # 'show_multi_step_emission_dialog',  # Moved to OLD_ - use PySide6 version
    # 'SNIDAnalysisDialog',  # Moved to OLD_ - use PySide6 version
    # 'show_snid_analysis_dialog'  # Moved to OLD_ - use PySide6 version
] 
