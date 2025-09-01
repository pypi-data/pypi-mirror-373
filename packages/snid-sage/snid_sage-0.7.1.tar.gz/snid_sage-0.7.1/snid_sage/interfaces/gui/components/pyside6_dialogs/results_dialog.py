"""
SNID SAGE - Analysis Results Dialog - PySide6 Version
===================================================

Comprehensive analysis results dialog for displaying SNID classification results.
PySide6 implementation of results summary.

Features:
- Clean classification summary with key results
- Detailed template match table with sorting
- Subtype statistics and proportions
- Quality and confidence assessment
- Copy/export functionality
- Modern Qt styling
"""

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_results')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_results')

# Enhanced dialog button styling
try:
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
    ENHANCED_BUTTONS_AVAILABLE = True
except Exception:
    ENHANCED_BUTTONS_AVAILABLE = False

# Import analysis utilities
try:
    from snid_sage.shared.utils.math_utils import get_best_metric_value, get_metric_name_for_match
except ImportError:
    _LOGGER.warning("Some analysis utilities not available - results may be limited")


class PySide6AnalysisResultsDialog(QtWidgets.QDialog):
    """
    PySide6 dialog for comprehensive analysis results display.
    
    Shows classification results, template matches, statistics, and quality assessment.
    """
    
    def __init__(self, parent, analysis_results=None, cluster_index=0):
        """
        Initialize analysis results dialog.
        
        Args:
            parent: Parent window
            analysis_results: SNID analysis results object
            cluster_index: Index of the cluster to display (default: 0 for winning cluster)
        """
        super().__init__(parent)
        
        self.parent_gui = parent
        self.analysis_results = analysis_results
        self.cluster_index = cluster_index
        
        # Extract cluster data from SNID results structure
        self.selected_cluster = None
        self.all_candidates = []
        self.analyzer = None
        
        # FIXED: Extract clustering data from the correct SNID results structure
        if analysis_results and hasattr(analysis_results, 'clustering_results') and analysis_results.clustering_results:
            clustering_results = analysis_results.clustering_results
            
            if clustering_results.get('success', False):
                # Get all cluster candidates
                self.all_candidates = clustering_results.get('all_candidates', [])
                
                # Get the winning cluster (user selected or automatic best)
                if 'user_selected_cluster' in clustering_results:
                    self.selected_cluster = clustering_results['user_selected_cluster']
                elif 'best_cluster' in clustering_results:
                    self.selected_cluster = clustering_results['best_cluster']
                elif self.all_candidates and cluster_index < len(self.all_candidates):
                    self.selected_cluster = self.all_candidates[cluster_index]
                
                # Create analyzer with the selected cluster
        
        # Fallback: if no clustering results, try to create a single cluster from best_matches
        if not self.analyzer and analysis_results and hasattr(analysis_results, 'best_matches'):
            # Fallback: simple pseudo-cluster without analyzer
            # Create a pseudo-cluster from the best matches
            self.selected_cluster = {
                'type': getattr(analysis_results, 'consensus_type', 'Unknown'),
                'matches': analysis_results.best_matches,
                'size': len(analysis_results.best_matches),
                'cluster_id': 0
            }
            self.all_candidates = [self.selected_cluster]
        
        # UI components
        self.summary_text = None
        self.matches_table = None
        self.copy_btn = None
        self.export_btn = None
        
        # Color scheme matching other dialogs
        self.colors = {
            'bg': '#f8fafc',
            'panel_bg': '#ffffff',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'border': '#e2e8f0',
            'success': '#22c55e',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'accent': '#3b82f6'
        }
        
        self._setup_dialog()
        self._create_interface()
        self._populate_results()
    
    def _setup_dialog(self):
        """Setup dialog window properties"""
        cluster_type = self.selected_cluster.get('type', 'Unknown') if self.selected_cluster else 'Unknown'
        cluster_num = self.cluster_index + 1
        
        self.setWindowTitle(f"Analysis Results - {cluster_type} (Cluster #{cluster_num})")
        # Made smaller and more compact as requested
        self.setMinimumSize(700, 500)
        self.resize(900, 650)
        self.setModal(False)  # Allow interaction with main window
        
        # Apply styling
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.colors['bg']};
                color: {self.colors['text_primary']};
                font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                background: {self.colors['panel_bg']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {self.colors['text_primary']};
            }}
            
            QTextEdit {{
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                background: {self.colors['panel_bg']};
                font-family: "Consolas", "Monaco", monospace;
                font-size: 10pt;
                padding: 8px;
                selection-background-color: {self.colors['accent']};
            }}
            
            QTableWidget {{
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                background: {self.colors['panel_bg']};
                selection-background-color: {self.colors['accent']};
                gridline-color: {self.colors['border']};
            }}
            
            QTableWidget::item {{
                padding: 6px;
                border: none;
            }}
            
            QHeaderView::section {{
                background: #e2e8f0;
                border: 1px solid {self.colors['border']};
                padding: 8px;
                font-weight: bold;
                font-size: 9pt;
            }}
            
            QPushButton {{
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                background: {self.colors['panel_bg']};
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background: #f1f5f9;
            }}
            
            QPushButton:pressed {{
                background: #e2e8f0;
            }}
            
            /* Primary button ID style removed in favor of unified enhancer */
            
            QTabWidget::pane {{
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                background: {self.colors['panel_bg']};
            }}
            
            QTabBar::tab {{
                background: #e2e8f0;
                border: 1px solid {self.colors['border']};
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
            }}
            
            QTabBar::tab:selected {{
                background: {self.colors['panel_bg']};
                border-bottom: none;
            }}
        """)
    
    def _create_interface(self):
        """Create the dialog interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header
        self._create_header(layout)
        
        # Main content with tabs
        self._create_tabbed_content(layout)
        
        # Button bar
        self._create_button_bar(layout)
    
    def _create_header(self, layout):
        """Create dialog header - removed per user request to make summary text the protagonist"""
        # Header removed to make summary text the protagonist
        pass
    
    def _create_tabbed_content(self, layout):
        """Create main content area - simplified to show only CLI-style summary"""
        # Create summary widget directly without tabs
        summary_widget = QtWidgets.QWidget()
        summary_layout = QtWidgets.QVBoxLayout(summary_widget)
        summary_layout.setContentsMargins(15, 15, 15, 15)
        
        # Summary text display using CLI-style format
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QtGui.QFont("Consolas", 10))  # Monospace for CLI-style formatting
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_widget, 1)  # Expand to fill space
    

    

    

    
    def _create_button_bar(self, layout):
        """Create bottom button bar with quick actions on left and close on right"""
        button_layout = QtWidgets.QHBoxLayout()
        
        # Quick actions on the left (no group box, no section name)
        copy_summary_btn = QtWidgets.QPushButton("Copy Summary")
        copy_summary_btn.setObjectName("copy_summary_btn")
        copy_summary_btn.clicked.connect(self._copy_summary)
        button_layout.addWidget(copy_summary_btn)
        
        save_results_btn = QtWidgets.QPushButton("Save Results")
        save_results_btn.setObjectName("save_results_btn")
        save_results_btn.clicked.connect(self._save_results)
        button_layout.addWidget(save_results_btn)
        
        # Stretch to push Close button to the right
        button_layout.addStretch()
        
        # Close button on the right
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)

        # Apply enhanced styles for consistent colors and states
        try:
            if ENHANCED_BUTTONS_AVAILABLE:
                self.button_manager = enhance_dialog_with_preset(self, 'results_dialog')
        except Exception as e:
            _LOGGER.warning(f"Failed to apply enhanced button styling: {e}")
    
    def _populate_results(self):
        """Populate the dialog with analysis results using CLI-style formatter"""
        if not self.analysis_results:
            self._show_no_results()
            return
        
        try:
            # Use the unified formatter to get CLI-style output
            from snid_sage.shared.utils.results_formatter import create_unified_formatter
            
            # Get spectrum name from analysis results or parent GUI
            spectrum_name = "Unknown"
            if hasattr(self.parent_gui, 'input_file_path') and self.parent_gui.input_file_path:
                import os
                spectrum_name = os.path.splitext(os.path.basename(self.parent_gui.input_file_path))[0]
            elif hasattr(self.analysis_results, 'spectrum_name') and self.analysis_results.spectrum_name:
                spectrum_name = self.analysis_results.spectrum_name
            
            # Create formatter and get CLI-style summary
            spectrum_path = None
            try:
                if hasattr(self.parent_gui, 'app_controller') and getattr(self.parent_gui.app_controller, 'current_file_path', None):
                    spectrum_path = self.parent_gui.app_controller.current_file_path
                elif hasattr(self.analysis_results, 'input_file') and self.analysis_results.input_file:
                    spectrum_path = self.analysis_results.input_file
                elif hasattr(self.analysis_results, 'spectrum_path') and self.analysis_results.spectrum_path:
                    spectrum_path = self.analysis_results.spectrum_path
            except Exception:
                spectrum_path = None

            formatter = create_unified_formatter(self.analysis_results, spectrum_name, spectrum_path)
            cli_summary_text = formatter.get_display_summary()
            
            # Set the CLI-style text
            self.summary_text.setPlainText(cli_summary_text)
            
        except Exception as e:
            _LOGGER.error(f"Error populating results: {e}")
            self._show_error(f"Error displaying results: {str(e)}")
    
    def _show_no_results(self):
        """Show message when no results are available"""
        no_results_msg = """
🚫 No Analysis Results Available

No SNID analysis results were found to display.
Please run the analysis first to see classification results.
        """.strip()
        
        self.summary_text.setPlainText(no_results_msg)
    
    def _show_error(self, error_msg):
        """Show error message"""
        error_text = f"""
Error Loading Results

{error_msg}

Please try running the analysis again or check the logs for more details.
        """.strip()
        
        self.summary_text.setPlainText(error_text)
    

    

    
    def _copy_summary(self):
        """Copy summary to clipboard"""
        if self.summary_text:
            QtWidgets.QApplication.clipboard().setText(self.summary_text.toPlainText())
            self._show_status_message("Summary copied to clipboard!")
    
    def _save_results(self):
        """Save CLI-style summary to file"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Analysis Results",
            "snid_analysis_results.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.summary_text.toPlainText())
                
                self._show_status_message(f"Results saved to {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save results:\n{str(e)}"
                )
    

    
    def _show_status_message(self, message):
        """Show a temporary status message"""
        # Could implement a status bar or temporary tooltip
        _LOGGER.info(message)


def show_analysis_results_dialog(parent, analysis_results=None, cluster_index=0):
    """
    Show the analysis results dialog.
    
    Args:
        parent: Parent window
        analysis_results: SNID analysis results object
        cluster_index: Index of cluster to display (default: 0 for winning cluster)
        
    Returns:
        PySide6AnalysisResultsDialog instance
    """
    dialog = PySide6AnalysisResultsDialog(parent, analysis_results, cluster_index)
    dialog.show()
    return dialog 