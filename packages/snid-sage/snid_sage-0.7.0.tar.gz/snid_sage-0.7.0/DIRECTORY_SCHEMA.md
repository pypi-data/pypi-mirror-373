```
SNID_SAGE/                                    # project root
├── pyproject.toml                            # Project configuration (215 lines)
├── README.md                                 # Project documentation (148 lines)
├── LICENSE                                   # License file (35 lines)
├── MANIFEST.in                               # Package manifest (58 lines)
├── mkdocs.yml                                # Documentation configuration (100 lines)
├── snid_sage/                                # main package
│   ├── __init__.py                          # Main package initialization (42 lines)
│   ├── snid/                                # CORE ENGINE - Main SNID analysis pipeline
│   │   ├── __init__.py                      # Package initialization (29 lines)
│   │   ├── snid.py                          # Main SNID pipeline with vectorized FFT cross-correlation (2481 lines)
│   │   ├── io.py                            # File I/O operations with FITS support and template plots (1456 lines)
│   │   ├── preprocessing.py                 # Spectrum preprocessing (764 lines)
│   │   ├── fft_tools.py                     # FFT correlation tools (521 lines)
│   │   ├── snidtype.py                      # Type classification with 10 main types and 53 subtypes (656 lines)
│   │   ├── plotting.py                      # Plotting functions with no-title styling and unified theme integration (2291 lines)
│   │   ├── cosmological_clustering.py       # Cosmological GMM clustering with ln(1+z) transformation (1039 lines)
│   │   ├── plotting_3d.py                   # 3D visualization for clustering results (474 lines)
│   │   ├── template_manager.py              # Template utilities (399 lines)
│   │   ├── games.py                         # Space Debris Cleanup game (1892 lines)
│   │   ├── snid_test.py                     # Core engine test script (233 lines)
│   │   ├── template_fft_storage.py          # Unified template FFT storage system - Single HDF5 file (855 lines)
│   │   ├── optimization_integration.py      # Legacy optimization compatibility layer (224 lines)
│   │   ├── vectorized_peak_finder.py        # Vectorized peak finding utilities (441 lines)
│   │   └── core/                            # FFT CORE: Vectorized FFT cross-correlation system
│   │       ├── __init__.py                  # Core module initialization with unified storage exports (36 lines)
│   │       ├── config.py                    # Centralized configuration management with FFT optimization settings (421 lines)
│   │       └── integration.py               # Unified FFT storage with vectorized cross-correlation (510 lines)
│   │
│   ├── interfaces/                          # user interfaces
│   │   ├── __init__.py                      # Package initialization (31 lines)
│   │   ├── gui/                             # PySide6 GUI
│   │   │   ├── __init__.py                  # GUI package initialization (13 lines)
│   │   │   ├── utils/                     # GUI utilities
│   │   │   │   ├── __init__.py            # init
│   │   │   │   ├── pyside6_theme_manager.py # theme
│   │   │   │   ├── unified_pyside6_layout_manager.py # layout
│   │   │   │   ├── logo_manager.py        # logos
│   │   │   │   ├── pyside6_helpers.py     # Qt helpers
│   │   │   │   ├── pyside6_message_utils.py # messages
│   │   │   │   ├── cross_platform_window.py # window utils
│   │   │   │   ├── twemoji_manager.py     # emoji
│   │   │   │   └── ...                    # other helpers
│   │   │   ├── components/                  # GUI components
│   │   │   │   ├── __init__.py              # Components package init (17 lines)
│   │   │   │   ├── **PYSIDE6 DIALOGS** (All exist):
│   │   │   │   │   └── pyside6_dialogs/     # **COMPLETE** PySide6 Qt native dialog components
│   │   │   │   │       ├── __init__.py      # PySide6 dialogs package init (95 lines)
│   │   │   │   │       ├── analysis_progress_dialog.py  # Analysis progress dialog (570 lines)
│   │   │   │   │       ├── button_palette_demo_dialog.py # Button palette demo dialog (506 lines)
│   │   │   │   │       ├── cluster_selection_dialog.py  # Cluster selection dialog (844 lines)
│   │   │   │   │       ├── configuration_dialog.py      # Qt configuration dialog (1104 lines)
│   │   │   │   │       ├── dialog_manager.py            # Dialog manager (500+ lines)
│   │   │   │   │       ├── emission_dialog_events.py    # Emission dialog event handlers (494 lines)
│   │   │   │   │       ├── emission_dialog_ui.py        # Emission dialog UI builder (511 lines)
│   │   │   │   │       ├── enhanced_ai_assistant_dialog.py # Enhanced AI assistant dialog (1507 lines)
│   │   │   │   │       ├── games_dialog.py              # Games dialog (336 lines)
│   │   │   │   │       ├── gmm_clustering_dialog.py     # GMM clustering dialog (850 lines)
│   │   │   │   │       ├── manual_redshift_dialog.py    # Qt manual redshift dialog (1352 lines)
│   │   │   │   │       ├── mask_manager_dialog.py       # Qt mask manager dialog (486 lines)
│   │   │   │   │       ├── multi_step_emission_dialog.py # Multi-step emission dialog (1742 lines)
│   │   │   │   │       ├── multi_step_emission_dialog_step2.py # Emission dialog step 2 (626 lines)
│   │   │   │   │       ├── preprocessing_dialog.py      # Qt preprocessing dialog (1545 lines)
│   │   │   │   │       ├── preprocessing_selection_dialog.py # Preprocessing selection (327 lines)
│   │   │   │   │       ├── progress_dialog.py           # Basic progress dialog (225 lines)
│   │   │   │   │       ├── redshift_age_dialog.py       # Redshift age dialog (655 lines)
│   │   │   │   │       ├── redshift_mode_dialog.py      # Qt redshift mode dialog (363 lines)
│   │   │   │   │       ├── results_dialog.py            # Qt results dialog (425 lines)
│   │   │   │   │       ├── settings_dialog.py           # Qt settings dialog (710 lines)
│   │   │   │   │       └── shortcuts_dialog.py          # Qt shortcuts dialog (288 lines)
│   │   │   │   ├── **TKINTER DIALOGS** (Legacy):
│   │   │   │   │   └── dialogs/             # Tkinter dialog components
│   │   │   │   │       ├── __init__.py      # Dialogs package init (48 lines)
│   │   │   │   │       ├── enhanced_ai_assistant_dialog.py # Enhanced AI assistant dialog (985 lines)
│   │   │   │   │       ├── redshift_mode_dialog.py      # Redshift mode selection dialog (352 lines)
│   │   │   │   │       ├── manual_redshift_dialog.py    # Manual redshift selection dialog (1568 lines)
│   │   │   │   │       ├── cluster_selection_dialog.py  # Cluster selection dialog (1341 lines)
│   │   │   │   │       ├── configuration_dialog.py      # Configuration dialog (1296 lines)
│   │   │   │   │       ├── snid_analysis_dialog.py      # SNID analysis dialog (440 lines)
│   │   │   │   │       ├── continuum_editor_dialog.py   # Continuum editor dialog (392 lines)
│   │   │   │   │       ├── multi_step_emission_dialog.py # Multi-step emission line analysis (2978 lines)
│   │   │   │   │       ├── preprocessing_dialog.py      # Preprocessing dialog (2075 lines)
│   │   │   │   │       ├── settings_dialog.py           # Settings dialog (761 lines)
│   │   │   │   │       ├── results_dialog.py            # Results dialog (685 lines)
│   │   │   │   │       ├── preprocessing_selection_dialog.py # Preprocessing selection dialog (268 lines)
│   │   │   │   │       ├── wind_velocity_dialog.py      # Wind velocity analysis dialog (826 lines)
│   │   │   │   │       ├── shortcuts_dialog.py          # Keyboard shortcuts dialog (200+ lines)
│   │   │   │   │       └── mask_manager_dialog.py       # Wavelength mask management (275 lines)
│   │   │   │   ├── plots/                   # Plotting components
│   │   │   │   │   ├── __init__.py          # Plots package init (18 lines)
│   │   │   │   │   ├── **PYSIDE6 PLOTS:**
│   │   │   │   │   │   ├── enhanced_plot_widget.py      # Enhanced/Simple PyQtGraph widgets (511 lines)
│   │   │   │   │   │   ├── pyside6_plot_manager.py      # PySide6 plot manager (946 lines)
│   │   │   │   │   │   └── pyside6_analysis_plotter.py  # PySide6 analysis plotter (537 lines)
│   │   │   │   │   ├── **SHARED PLOTS:**
│   │   │   │   │   │   ├── spectrum_plotter.py          # Spectrum plotting (402 lines)
│   │   │   │   │   │   ├── preview_plot_manager.py      # Preview plot management (688 lines)
│   │   │   │   │   │   ├── summary_plotter.py           # Results summary plotting (433 lines)
│   │   │   │   │   │   └── interactive_tools.py         # Interactive plot tools (391 lines)
│   │   │   │   └── widgets/                 # Custom widgets
│   │   │   │       ├── __init__.py          # Widgets package init (40 lines)
│   │   │   │       ├── **PYSIDE6 WIDGETS:**
│   │   │   │       │   ├── pyside6_interactive_continuum_widget.py # PySide6 continuum widget (590 lines)
│   │   │   │       │   └── pyside6_interactive_masking_widget.py   # PySide6 masking widget (612 lines)
│   │   │   │       ├── **SHARED WIDGETS:**
│   │   │   │       │   ├── interactive_continuum_widget.py # Tkinter continuum widget (763 lines)
│   │   │   │       │   ├── config_widgets.py            # Configuration widgets (555 lines)
│   │   │   │       │   ├── theme_widgets.py             # Theme widgets (352 lines)
│   │   │   │       │   ├── progress_widgets.py          # Progress display widgets (657 lines)
│   │   │   │       │   ├── custom_toggles.py            # Custom toggle widgets (447 lines)
│   │   │   │       │   └── advanced_controls.py         # Advanced control widgets (573 lines)
│   │   │   ├── controllers/                 # MVC controllers
│   │   │   │   ├── __init__.py              # Controllers package init (22 lines)
│   │   │   │   ├── app_controller.py        # Main Tkinter application controller (573 lines)
│   │   │   │   ├── pyside6_app_controller.py # PySide6 application controller (350+ lines)
│   │   │   │   ├── pyside6_preprocessing_controller.py # PySide6 preprocessing controller 
│   │   │   │   ├── dialog_controller.py     # Dialog management controller (424 lines)
│   │   │   │   ├── file_controller.py       # File operations controller (700 lines)
│   │   │   │   ├── plot_controller.py       # Plot management controller (1193 lines)
│   │   │   │   └── view_controller.py       # View management controller (222 lines)
│   │   │   ├── dialogs/                     # Dialog compatibility layer
│   │   │   │   └── __init__.py              # Dialogs compatibility init
│   │   │   ├── features/                    # Feature modules
│   │   │   │   ├── __init__.py              # Features package init (10 lines)
│   │   │   │   ├── analysis/                # Analysis features
│   │   │   │   │   ├── __init__.py          # Analysis features init (23 lines)
│   │   │   │   │   ├── analysis_controller.py # Analysis workflow controller (1579 lines)
│   │   │   │   │   ├── cluster_summary.py   # Cluster analysis summary (556 lines)
│   │   │   │   │   ├── emission_line_overlay_controller.py # Emission line analysis (391 lines)
│   │   │   │   │   ├── games_integration.py # Fun games during analysis (358 lines)
│   │   │   │   │   ├── line_detection.py    # Line detection controller (827 lines)
│   │   │   │   │   ├── manual_selection_controller.py # Manual line selection controller (565 lines)
│   │   │   │   │   └── wind_velocity_controller.py # Wind velocity analysis controller (486 lines)
│   │   │   │   ├── configuration/           # Configuration features
│   │   │   │   │   ├── __init__.py          # Configuration features init (19 lines)
│   │   │   │   │   ├── config_controller.py # Configuration management (595 lines)
│   │   │   │   │   └── gui_settings_controller.py # GUI settings with unified storage integration (545 lines)
│   │   │   │   ├── preprocessing/           # Preprocessing features
│   │   │   │   │   ├── __init__.py          # Preprocessing features init (17 lines)
│   │   │   │   │   ├── preprocessing_controller.py # Preprocessing workflow (352 lines)
│   │   │   │   │   ├── preview_calculator.py # Preview calculation utilities (536 lines)
│   │   │   │   │   └── spectrum_preprocessor.py # Spectrum preprocessing utilities (631 lines)
│   │   │   │   └── results/                 # Results features
│   │   │   │       ├── __init__.py          # Results features init (10 lines)
│   │   │   │       ├── llm_integration.py   # LLM integration (480 lines)
│   │   │   │       └── results_manager.py   # Results management (540 lines)
│   │   │   ├── utils/                       # GUI utilities with unified theme consistency system
│   │   │   │   ├── __init__.py              # Utils package init (40 lines)
│   │   │   │   ├── window_event_handlers.py # Window event handling with anti-jump protection (223 lines)
│   │   │   │   ├── state_manager.py         # Application state management (498 lines)
│   │   │   │   ├── no_title_plot_manager.py # Unified no-title plot styling manager (349 lines)
│   │   │   │   ├── startup_manager.py       # Startup sequence management (367 lines)
│   │   │   │   ├── layout_utils.py          # Layout utilities with unified button color system (969 lines)
│   │   │   │   ├── improved_button_workflow.py # Improved button workflow system (301 lines)
│   │   │   │   ├── workflow_integration.py  # Workflow integration utilities (296 lines)
│   │   │   │   ├── gui_helpers.py           # GUI helper functions (473 lines)
│   │   │   │   ├── spectrum_reset_manager.py # Spectrum state reset utilities (623 lines)
│   │   │   │   ├── cross_platform_window.py # Cross-platform window management with fixed icon handling (545 lines)
│   │   │   │   ├── universal_window_manager.py # Cross-platform window management with F11 fullscreen (420 lines)
│   │   │   │   ├── unified_font_manager.py  # Platform-aware font scaling system (313 lines)
│   │   │   │   ├── unified_theme_manager.py # Tkinter theme management utilities (660 lines)
│   │   │   │   ├── pyside6_theme_manager.py # **NEW** Unified PySide6 theme manager with complete Qt stylesheet generation (400+ lines)
│   │   │   │   ├── pyside6_workflow_manager.py # **REFACTORED** PySide6 workflow and button state management using unified theme system (250+ lines)
│   │   │   │   ├── pyside6_layout_manager.py # **ENHANCED** Modular PySide6 layout management system with theme integration (430+ lines)
│   │   │   │   ├── logo_manager.py          # Logo and branding management (241 lines)
│   │   │   │   ├── import_manager.py        # Import management (237 lines)
│   │   │   │   └── event_handlers.py        # Event handling utilities (393 lines)
│   │   │   └── widgets/                     # Widget compatibility layer
│   │   │       └── __init__.py              # Widgets package init
│   │   ├── cli/                             # command line
│   │   │   ├── __init__.py                  # Package initialization (28 lines)
│   │   │   ├── main.py                      # CLI entry point with enhanced output (150+ lines)
│   │   │   ├── identify.py                  # Spectrum identification with enhanced subtype display (375 lines)
│   │   │   ├── template.py                  # Template management (401 lines)
│   │   │   ├── batch.py                     # Batch processing (301 lines)
│   │   │   └── config.py                    # Configuration (279 lines)
│   │   ├── line_manager/                   # lines mini-GUI
│   │   │   ├── __init__.py                 # init
│   │   │   ├── launcher.py                 # launcher
│   │   │   └── main_window.py              # main window
│   │   ├── template_manager/               # templates mini-GUI
│   │   │   ├── __init__.py                 # init
│   │   │   ├── components/                 # components
│   │   │   ├── dialogs/                    # dialogs
│   │   │   ├── launcher.py                 # launcher
│   │   │   ├── main_window.py              # main window
│   │   │   ├── utils/                      # util
│   │   │   └── widgets/                    # widgets
│   │   └── ui_core/                        # shared UI core
│   │       ├── __init__.py                 # re-exports
│   │       ├── layout.py                   # layout facade
│   │       ├── logo.py                     # logo facade
│   │       ├── theme.py                    # theme facade
│   │       └── twemoji.py                  # emoji facade
│   │   └── llm/                             # LLM integration
│   │       ├── __init__.py                  # LLM package initialization with enhanced exports (12 lines)
│   │       ├── analysis/                    # Advanced LLM analysis utilities
│   │       │   ├── __init__.py              # Analysis package init (6 lines)
│   │       │   └── llm_utils.py             # Enhanced LLM utilities with 4 specialized analysis types (660 lines)
│   │       ├── openrouter/                  # OpenRouter cloud provider integration
│   │       │   ├── __init__.py              # OpenRouter package init (6 lines)
│   │       │   ├── openrouter_llm.py        # Core OpenRouter API integration with model selection (901 lines)
│   │       │   └── openrouter_summary.py    # Enhanced summary generation with modern tabbed UI (774 lines)
│   │       └── ui/                          # Enhanced LLM UI components
│   │           └── __init__.py              # UI package init (14 lines)
│   │
│   ├── shared/                              # shared utilities
│   │   ├── __init__.py                      # Shared package initialization
│   │   ├── constants/                       # Physical constants and emission line database
│   │   │   ├── __init__.py                  # Constants package init
│   │   │   └── physical.py                  # Physical constants and comprehensive emission line database
│   │   ├── exceptions/                      # Custom exception classes
│   │   │   ├── __init__.py                  # Exceptions package init
│   │   │   └── core_exceptions.py           # Core exception definitions
│   │   ├── types/                           # Type definitions and data structures
│   │   │   ├── __init__.py                  # Types package init
│   │   │   ├── result_types.py              # Analysis result type definitions
│   │   │   └── spectrum_types.py            # Spectrum data type definitions
│   │   └── utils/                           # Shared utility functions
│   │       ├── __init__.py                  # Utils package init
│   │       ├── config/                      # Configuration utilities
│   │       │   ├── __init__.py              # Config package init
│   │       │   ├── configuration_manager.py # Configuration management utilities
│   │       │   └── platform_config.py       # **ENHANCED** Platform configuration with PySide6 optimizations
│   │       ├── data_io/                     # Data input/output utilities
│   │       │   ├── __init__.py              # Data I/O package init
│   │       │   └── spectrum_loader.py       # Spectrum loading utilities
│   │       ├── line_detection/              # Line detection and analysis utilities
│   │       │   ├── __init__.py              # Line detection package init with comprehensive exports (133 lines)
│   │       │   ├── line_detection_utils.py  # Line detection utilities (1130 lines)
│   │       │   ├── nist_search.py           # NIST line database search (684 lines)
│   │       │   ├── line_presets.py          # Line preset configurations (282 lines)
│   │       │   ├── line_selection_utils.py  # Line selection and filtering utilities (298 lines)
│   │       │   ├── fwhm_analysis.py         # FWHM analysis utilities with advanced fitting functions (433 lines)
│   │       │   ├── interactive_fwhm_analyzer.py # Enhanced interactive FWHM analyzer (503 lines)
│   │       │   ├── line_analysis.py         # Line analysis utilities (170 lines)
│   │       │   └── spectrum_utils.py        # Spectrum plotting utilities (186 lines)
│   │       ├── logging/                     # Logging configuration
│   │       │   ├── __init__.py              # Logging package init
│   │       │   ├── config.py                # Logging configuration
│   │       │   └── snid_logger.py           # SNID logger implementation
│   │       ├── mask_utils/                  # Wavelength masking utilities
│   │       │   ├── __init__.py              # Mask utils package init
│   │       │   └── mask_utils.py            # Mask utility functions
│   │       ├── math_utils/                  # Mathematical utilities
│   │       │   ├── __init__.py              # Math utils package init
│   │       │   ├── similarity_metrics.py    # **NEW** Similarity metrics for template matching
│   │       │   └── weighted_statistics.py   # Weighted statistical calculations
│   │       ├── plotting/                    # Plotting utilities
│   │       │   ├── __init__.py              # Plotting package init with comprehensive exports (45 lines)
│   │       │   ├── plot_theming.py          # Plot theming utilities (513 lines)
│   │       │   ├── font_sizes.py            # **NEW** Font size management for cross-platform consistency
│   │       │   └── spectrum_utils.py        # Spectrum plotting utilities (259 lines)
│   │       ├── results_formatter.py         # Results formatting utilities
│   │       ├── simple_template_finder.py    # Simple template finding utilities
│   │       ├── version_checker.py           # **NEW** Version checking and update utilities
│   │       └── wind_analysis/               # Wind velocity analysis utilities
│   │           ├── __init__.py              # Wind analysis package init
│   │           ├── pcygni_fitting.py        # P Cygni profile fitting
│   │           └── wind_calculations.py     # Wind velocity calculations
│   │
│   └── templates/                           # template data
│       ├── template_index.json              # Template metadata and indexing
│       ├── templates_AGN.hdf5               # Active Galactic Nuclei templates
│       ├── templates_Galaxy.hdf5            # Galaxy templates
│       ├── templates_GAP.hdf5               # GAP templates
│       ├── templates_Ia.hdf5                # Type Ia supernova templates
│       ├── templates_Ib.hdf5                # Type Ib supernova templates
│       ├── templates_Ibn.hdf5               # Type Ibn supernova templates
│       ├── templates_Ic.hdf5                # Type Ic supernova templates
│       ├── templates_Icn.hdf5               # Type Icn supernova templates
│       ├── templates_II.hdf5                # Type II supernova templates
│       ├── templates_KN.hdf5                # Kilonova templates
│       ├── templates_LFBOT.hdf5             # Luminous Fast Blue Optical Transient templates
│       ├── templates_SLSN.hdf5              # Super Luminous Supernova templates
│       ├── templates_Star.hdf5              # Stellar templates
│       └── templates_TDE.hdf5               # Tidal Disruption Event templates
│
├── images/                                 # branding assets
│   ├── icon.ico                            # Windows icon file
│   ├── icon.png                            # Primary PNG icon
│   ├── icon_dark.png                       # Dark theme icon
│   ├── light.png                           # Light theme assets
│   ├── Screenshot.png                       # Application screenshot
│   ├── icon.iconset/                       # macOS iconset directory
│   │   ├── icon_16x16.png                  # 16x16 icon
│   │   ├── icon_32x32.png                  # 32x32 icon
│   │   ├── icon_64x64.png                  # 64x64 icon
│   │   ├── icon_128x128.png                # 128x128 icon
│   │   ├── icon_256x256.png                # 256x256 icon
│   │   ├── icon_512x512.png                # 512x512 icon
│   │   └── icon_1024x1024.png              # 1024x1024 icon
│   ├── icon_dark.iconset/                  # Dark theme macOS iconset
│   │   └── (same structure as above)       # Dark theme icon sizes
│   └── OLD_ICONS/                          # Legacy icons archive
│       ├── ChatGPT Image May 3, 2025, 03_59_02 PM.png
│       ├── ChatGPT Image May 3, 2025, 04_04_56 PM.png
│       ├── ChatGPT Image May 3, 2025, 04_10_18 PM.png
│       ├── ChatGPT Image May 3, 2025, 04_12_52 PM.png
│       ├── dark.png                        # Legacy dark icon
│       └── icon.png                        # Legacy icon
│
├── docs/                                   # documentation
│   ├── installation/                       # install guides
│   ├── quickstart/                         # quickstart
│   ├── troubleshooting/                    # troubleshooting
│   └── index.md                            # docs index
├── plots/                                  # output plots
├── results/                                # output results
├── tests/                                  # tests
│   ├── test_cli_integration.py             # CLI tests
│   └── test_cross_platform.py              # cross-platform tests
```
```
