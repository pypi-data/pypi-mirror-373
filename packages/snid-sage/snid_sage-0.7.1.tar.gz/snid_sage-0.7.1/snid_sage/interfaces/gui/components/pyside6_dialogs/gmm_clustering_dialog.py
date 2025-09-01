"""
SNID SAGE - GMM Clustering Dialog - PySide6 Version
=================================================

Interactive GMM clustering visualization dialog for SNID analysis results.
Displays redshift distribution, cluster assignments, and clustering quality metrics.

Features:
- Interactive PyQtGraph plots of redshift vs metric values
- Cluster identification with different colors
- Winning cluster highlighting
- Quality metrics and statistics
- Export functionality for plots and data
- Modern Qt styling
"""

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json

# PyQtGraph for high-performance plotting (software rendering only for WSL compatibility)
try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
    # Configure PyQtGraph for complete software rendering
    pg.setConfigOptions(
        useOpenGL=False,     # Disable OpenGL completely
        antialias=True,      # Keep antialiasing for quality
        enableExperimental=False,  # Disable experimental features
        crashWarning=False   # Reduce warnings
    )
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    pg = None

# Matplotlib for 3D plotting (Qt helper, consistent with other dialogs)
try:
    from snid_sage.interfaces.gui.utils.matplotlib_qt import get_qt_mpl
    plt, Figure, FigureCanvas, _NavigationToolbar = get_qt_mpl()
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    FigureCanvas = None
    Figure = None

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_gmm')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_gmm')

# Enhanced dialog button styling
try:
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
    ENHANCED_BUTTONS_AVAILABLE = True
except Exception:
    ENHANCED_BUTTONS_AVAILABLE = False
# Import GMM clustering utilities
try:
    from snid_sage.snid.cosmological_clustering import perform_direct_gmm_clustering
    from snid_sage.shared.utils.math_utils import get_best_metric_value, get_metric_name_for_match
    GMM_AVAILABLE = True
except ImportError:
    _LOGGER.warning("GMM clustering not available")
    GMM_AVAILABLE = False


class PySide6GMMClusteringDialog(QtWidgets.QDialog):
    """
    PySide6 dialog for GMM clustering visualization.
    
    Shows redshift distribution, cluster assignments, quality metrics, and allows
    interactive exploration of clustering results.
    """
    
    def __init__(self, parent, analysis_results=None):
        """
        Initialize GMM clustering dialog.
        
        Args:
            parent: Parent window
            analysis_results: SNID analysis results object
        """
        super().__init__(parent)
        # Ensure full cleanup on close to avoid stale Matplotlib/Qt references when reopening
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        self.parent_gui = parent
        self.analysis_results = analysis_results
        
        # Clustering data
        self.all_matches = []
        self.clustering_results = {}
        self.plot_data = {}
        
        # UI components
        self.plot_widget = None
        self.info_text = None
        self.cluster_table = None
        
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
        
        # Cluster colors for plotting
        self.cluster_colors = [
            '#3b82f6',  # Blue
            '#ef4444',  # Red  
            '#22c55e',  # Green
            '#f59e0b',  # Orange
            '#8b5cf6',  # Purple
            '#06b6d4',  # Cyan
            '#ec4899',  # Pink
            '#84cc16',  # Lime
            '#f97316',  # Orange alt
            '#6366f1'   # Indigo
        ]
        
        self._setup_dialog()
        self._create_interface()
        self._extract_data_and_cluster()
        self._populate_results()
    
    def _setup_dialog(self):
        """Setup dialog window properties"""
        self.setWindowTitle("GMM Clustering Analysis")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setModal(False)  # Allow interaction with main window
        
        # Apply styling
        # Use platform-aware font stack for macOS
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
            
            QPushButton#primary_btn {{
                background: {self.colors['success']};
                border: 2px solid {self.colors['success']};
                color: white;
            }}
            
            QPushButton#primary_btn:hover {{
                background: #16a34a;
            }}
        """)
    
    def _create_interface(self):
        """Create the dialog interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header
        self._create_header(layout)
        
        # Main content - horizontal split
        content_layout = QtWidgets.QHBoxLayout()
        
        # Left panel - plot
        self._create_plot_panel(content_layout)
        
        # Right panel - info and controls
        self._create_info_panel(content_layout)
        
        layout.addLayout(content_layout, 1)
        
        # Button bar
        self._create_button_bar(layout)
    
    def _create_header(self, layout):
        """Create dialog header"""
        header_frame = QtWidgets.QFrame()
        header_layout = QtWidgets.QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QtWidgets.QLabel("GMM Clustering Analysis")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #3b82f6;
            margin: 10px 0;
        """)
        header_layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Gaussian Mixture Model clustering of template matches")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 12pt;
            color: #64748b;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
    
    def _create_plot_panel(self, layout):
        """Create plot panel with matplotlib 3D (Qt backend, no OpenGL)"""
        plot_group = QtWidgets.QGroupBox("3D GMM Clustering Visualization")
        plot_layout = QtWidgets.QVBoxLayout(plot_group)
        
        # Guard against headless environments or missing Matplotlib
        screens = QtGui.QGuiApplication.screens()
        if not screens or not MATPLOTLIB_AVAILABLE:
            fallback_label = QtWidgets.QLabel(
                ("No display screens available" if not screens else "Matplotlib Required for 3D Plotting") +
                "\n\n3D GMM clustering visualization is unavailable in the current environment.\n\n"
                "Clustering analysis will still be available in the text summary."
            )
            fallback_label.setAlignment(QtCore.Qt.AlignCenter)
            fallback_label.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 12pt;")
            fallback_label.setWordWrap(True)
            plot_layout.addWidget(fallback_label)
        else:
            # Create matplotlib figure with white background
            self.fig = Figure(figsize=(10, 8), facecolor='white')
            self.fig.patch.set_facecolor('white')
            
            # Create 3D axes
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.ax.set_facecolor('white')
            
            # Create Qt canvas widget (ownership managed by layout)
            self.plot_widget = FigureCanvas(self.fig)
            self.plot_widget.setMinimumHeight(400)
            
            plot_layout.addWidget(self.plot_widget)
        
        layout.addWidget(plot_group, 2)  # 2/3 of width
    
    def _create_info_panel(self, layout):
        """Create information and controls panel"""
        info_widget = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Clustering summary
        summary_group = QtWidgets.QGroupBox("Clustering Summary")
        summary_layout = QtWidgets.QVBoxLayout(summary_group)
        
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(250)
        summary_layout.addWidget(self.info_text)
        
        info_layout.addWidget(summary_group)
        
        # Cluster details table
        table_group = QtWidgets.QGroupBox("Cluster Details")
        table_layout = QtWidgets.QVBoxLayout(table_group)
        
        self.cluster_table = QtWidgets.QTableWidget()
        self.cluster_table.setAlternatingRowColors(False)
        self.cluster_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        # Set up table columns
        columns = ['Cluster', 'Type', 'Count', 'Quality', 'Mean z', 'z Scatter']
        self.cluster_table.setColumnCount(len(columns))
        self.cluster_table.setHorizontalHeaderLabels(columns)
        
        # Configure column widths
        header = self.cluster_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i, width in enumerate([60, 80, 60, 80, 80, 80]):
            self.cluster_table.setColumnWidth(i, width)
        
        table_layout.addWidget(self.cluster_table)
        
        # Table controls
        table_controls = QtWidgets.QHBoxLayout()
        
        highlight_btn = QtWidgets.QPushButton("Highlight Winning")
        highlight_btn.clicked.connect(self._highlight_winning_cluster)
        table_controls.addWidget(highlight_btn)
        
        export_data_btn = QtWidgets.QPushButton("Export Data")
        export_data_btn.clicked.connect(self._export_clustering_data)
        table_controls.addWidget(export_data_btn)
        
        table_controls.addStretch()
        table_layout.addLayout(table_controls)
        
        info_layout.addWidget(table_group)
        
        layout.addWidget(info_widget, 1)  # 1/3 of width
    
    def _create_button_bar(self, layout):
        """Create bottom button bar"""
        button_layout = QtWidgets.QHBoxLayout()
        
        # Refresh clustering button
        refresh_btn = QtWidgets.QPushButton("Refresh Clustering")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(self._refresh_clustering)
        button_layout.addWidget(refresh_btn)
        
        # Export plot button
        if PYQTGRAPH_AVAILABLE:
            export_plot_btn = QtWidgets.QPushButton("Export Plot")
            export_plot_btn.setObjectName("export_plot_btn")
            export_plot_btn.clicked.connect(self._export_plot)
            button_layout.addWidget(export_plot_btn)
        
        button_layout.addStretch()
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)

        # Apply enhanced styles
        try:
            if ENHANCED_BUTTONS_AVAILABLE:
                self.button_manager = enhance_dialog_with_preset(self, 'gmm_clustering_dialog')
        except Exception as e:
            _LOGGER.warning(f"Failed to apply enhanced button styling: {e}")
    
    def _extract_data_and_cluster(self):
        """Extract template matches and perform GMM clustering"""
        if not self.analysis_results:
            _LOGGER.warning("No analysis results available for GMM clustering")
            return
        
        try:
            # Extract all template matches from analysis results
            if hasattr(self.analysis_results, 'best_matches'):
                self.all_matches = self.analysis_results.best_matches
            elif hasattr(self.analysis_results, 'clusters') and self.analysis_results.clusters:
                # If we have clusters, extract matches from all clusters
                self.all_matches = []
                for cluster in self.analysis_results.clusters:
                    if 'matches' in cluster:
                        self.all_matches.extend(cluster['matches'])
            else:
                _LOGGER.warning("No template matches found in analysis results")
                return
            
            if not self.all_matches:
                _LOGGER.warning("No template matches available for clustering")
                return
            
            # Perform GMM clustering if available
            if GMM_AVAILABLE and len(self.all_matches) >= 1:  # Allow clustering with any matches
                _LOGGER.info(f"Running GMM clustering on {len(self.all_matches)} template matches")
                
                self.clustering_results = perform_direct_gmm_clustering(
                    matches=self.all_matches,
                    min_matches_per_type=1,  # Accept any type with at least 1 match
                    quality_threshold=0.02,
                    max_clusters_per_type=10,
                    top_percentage=0.10,
                    verbose=True,
                    use_rlap_cos=True,  # Use RLAP-Cos for better discrimination
                    rlap_ccc_threshold=1.5  # Default RLAP-CCC threshold
                )
                
                _LOGGER.info(f"GMM clustering completed successfully")
                
            else:
                _LOGGER.warning("GMM clustering not available or insufficient matches")
                # Create basic grouping by type as fallback
                self._create_fallback_clustering()
        
        except Exception as e:
            _LOGGER.error(f"Error during GMM clustering: {e}")
            self._create_fallback_clustering()
    
    def _create_fallback_clustering(self):
        """Create basic type-based clustering as fallback"""
        type_groups = {}
        for match in self.all_matches:
            sn_type = match.get('template', {}).get('type', 'Unknown')
            if sn_type not in type_groups:
                type_groups[sn_type] = []
            type_groups[sn_type].append(match)
        
        # Create simple clustering results structure
        clusters = []
        for i, (sn_type, matches) in enumerate(type_groups.items()):
            if len(matches) >= 2:  # Only include types with multiple matches
                redshifts = [m.get('redshift', 0) for m in matches]
                mean_redshift = np.mean(redshifts)
                redshift_scatter = np.std(redshifts)
                
                clusters.append({
                    'cluster_id': i,
                    'type': sn_type,
                    'matches': matches,
                    'size': len(matches),
                    'mean_redshift': mean_redshift,
                    'redshift_scatter': redshift_scatter,
                    'quality_score': len(matches) * 10,  # Simple quality metric
                    'is_winning': i == 0  # First (largest) cluster as winning
                })
        
        self.clustering_results = {
            'success': True,
            'clusters': clusters,
            'winning_cluster': clusters[0] if clusters else None,
            'method': 'type_grouping_fallback'
        }
    
    def _populate_results(self):
        """Populate the dialog with clustering results"""
        try:
            # Populate summary text
            self._populate_summary()
            
            # Populate cluster table
            self._populate_cluster_table()
            
            # Create plot if matplotlib 3D is available
            if hasattr(self, 'ax'):
                self._create_clustering_plot()
            
        except Exception as e:
            _LOGGER.error(f"Error populating results: {e}")
            self._show_error(f"Error displaying clustering results: {str(e)}")
    
    def _populate_summary(self):
        """Populate the clustering summary text"""
        if not self.clustering_results.get('success', False):
            error_text = """
❌ GMM Clustering Failed

GMM clustering could not be performed on the analysis results.
This may be due to:
• Insufficient template matches (need at least 4)
• Missing GMM clustering module
• Data format issues

Fallback type-based grouping may be available in the table below.
            """.strip()
            self.info_text.setPlainText(error_text)
            return
        
        clusters = self.clustering_results.get('clusters', [])
        winning_cluster = self.clustering_results.get('winning_cluster')
        method = self.clustering_results.get('method', 'direct_gmm')
        
        # Build summary text
        lines = [
            "GMM CLUSTERING ANALYSIS",
            "=" * 40,
            "",
            f"METHOD: {method.replace('_', ' ').title()}",
            f"TOTAL MATCHES: {len(self.all_matches)}",
            f"CLUSTERS FOUND: {len(clusters)}",
            ""
        ]
        
        if winning_cluster:
            lines.extend([
                "🏆 WINNING CLUSTER:",
                f"   Type: {winning_cluster.get('type', 'Unknown')}",
                f"   Size: {winning_cluster.get('size', 0)} templates",
                f"   Mean z: {winning_cluster.get('mean_redshift', 0):.5f}",
                f"   z Scatter: {winning_cluster.get('redshift_scatter', 0):.5f}",
                f"   Quality: {winning_cluster.get('quality_score', 0):.1f}",
                ""
            ])
        
        # Cluster summary
        if len(clusters) > 1:
            lines.append("ALL CLUSTERS:")
            for i, cluster in enumerate(clusters):
                winner_mark = " 🏆" if cluster.get('is_winning', False) else ""
                lines.append(
                    f"   {i+1}. {cluster.get('type', 'Unknown')}: "
                    f"{cluster.get('size', 0)} templates, "
                    f"z={cluster.get('mean_redshift', 0):.6f}{winner_mark}"
                )
        
        lines.extend([
            "",
            "🎨 PLOT LEGEND:",
            "   Different colors = Different clusters",
            "   Larger points = Higher RLAP values",
            "   Winning cluster highlighted"
        ])
        
        self.info_text.setPlainText("\n".join(lines))
    
    def _populate_cluster_table(self):
        """Populate the cluster details table"""
        clusters = self.clustering_results.get('clusters', [])
        
        if not clusters:
            return
        
        # Set table size
        self.cluster_table.setRowCount(len(clusters))
        
        # Populate table rows
        for i, cluster in enumerate(clusters):
            # Create table items
            cluster_id = cluster.get('cluster_id', i)
            cluster_type = cluster.get('type', 'Unknown')
            count = cluster.get('size', 0)
            quality = cluster.get('quality_score', 0)
            mean_z = cluster.get('mean_redshift', 0)
            z_scatter = cluster.get('redshift_scatter', 0)
            is_winning = cluster.get('is_winning', False)
            
            # Add winner indicator
            display_id = f"{cluster_id+1}" + (" 🏆" if is_winning else "")
            
            items = [
                QtWidgets.QTableWidgetItem(display_id),
                QtWidgets.QTableWidgetItem(cluster_type),
                QtWidgets.QTableWidgetItem(str(count)),
                QtWidgets.QTableWidgetItem(f"{quality:.1f}"),
                QtWidgets.QTableWidgetItem(f"{mean_z:.5f}"),
                QtWidgets.QTableWidgetItem(f"{z_scatter:.5f}")
            ]
            
            # Set items in table
            for j, item in enumerate(items):
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make read-only
                if is_winning:
                    item.setBackground(QtGui.QBrush(QtGui.QColor("#dcfce7")))  # Light green background
                self.cluster_table.setItem(i, j, item)
        
        # Auto-resize columns to content
        self.cluster_table.resizeColumnsToContents()
    
    def _create_clustering_plot(self):
        """Create the 3D clustering plot using matplotlib (no OpenGL required)"""
        if not hasattr(self, 'ax') or not self.clustering_results.get('success', False):
            return
        
        try:
            # Clear the existing plot
            self.ax.clear()
            
            clusters = self.clustering_results.get('clusters', [])
            
            if not clusters:
                self.ax.text(0.5, 0.5, 0.5, 'No clustering data available', 
                           ha='center', va='center', transform=self.ax.transAxes)
                self.plot_widget.draw()
                return
            
            # Define color map for clusters
            import matplotlib.cm as cm
            colors = cm.Set1(np.linspace(0, 1, len(clusters)))
            
            # Plot each cluster with 3D coordinates
            legend_elements = []
            
            for i, cluster in enumerate(clusters):
                matches = cluster.get('matches', [])
                if not matches:
                    continue
                
                # Extract data for this cluster
                redshifts = []
                metrics = []
                z_coords = []
                
                for match in matches:
                    redshift = match.get('redshift', 0)
                    metric = get_best_metric_value(match)
                    
                    # Create some spread in Z for visualization
                    z_spread = np.random.normal(i * 0.5, 0.2)  # Offset each cluster in Z
                    
                    redshifts.append(redshift)
                    metrics.append(metric)
                    z_coords.append(z_spread)
                
                if not redshifts:
                    continue
                
                # Get color for this cluster
                color = colors[i % len(colors)]
                
                # Determine size and alpha based on whether it's the winning cluster
                is_winning = cluster.get('is_winning', False)
                size = 80 if is_winning else 40
                alpha = 0.8 if is_winning else 0.6
                marker = 'o' if is_winning else '^'
                
                # Create 3D scatter plot
                scatter = self.ax.scatter(
                    redshifts, metrics, z_coords,
                    c=[color], s=size, alpha=alpha, marker=marker,
                    label=f'Cluster {i+1}{"" if not is_winning else " (Best)"}'
                )
                
                legend_elements.append(scatter)
            
            # Set labels and title
            self.ax.set_xlabel('Redshift', fontsize=12)
            self.ax.set_ylabel('Metric Value', fontsize=12)
            self.ax.set_zlabel('Cluster Separation', fontsize=12)
            self.ax.set_title('3D GMM Clustering Visualization', fontsize=14, fontweight='bold')
            
            # Set white background
            self.ax.set_facecolor('white')
            
            # Add legend
            if legend_elements:
                self.ax.legend(loc='upper right', fontsize=10)
            
            # Set view angle
            self.ax.view_init(elev=20, azim=45)
            
            # Enable rotation
            self.ax.mouse_init()
            
            # Refresh the plot
            self.plot_widget.draw()
            
            _LOGGER.info(f"Created 3D GMM plot with matplotlib: {len(clusters)} clusters")
            
        except Exception as e:
            _LOGGER.error(f"Error creating 3D clustering plot: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_error(self, error_msg):
        """Show error message in info text"""
        error_text = f"""
❌ Error Loading Clustering Results

{error_msg}

Please try running the analysis again or check the logs for more details.
        """.strip()
        
        self.info_text.setPlainText(error_text)
    
    def _highlight_winning_cluster(self):
        """Highlight the winning cluster in the plot"""
        if not hasattr(self, 'ax'):
            return
        
        # Refresh the plot to show the winning cluster highlighted
        self._create_clustering_plot()
        
        # Show a message
        QtWidgets.QMessageBox.information(
            self,
            "Winning Cluster",
            "The winning cluster is marked with larger circles and highlighted in the table."
        )
    
    def _refresh_clustering(self):
        """Refresh the clustering analysis"""
        try:
            self._extract_data_and_cluster()
            self._populate_results()
            
            QtWidgets.QMessageBox.information(
                self,
                "Clustering Refreshed",
                "GMM clustering analysis has been refreshed with current data."
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Refresh Error",
                f"Failed to refresh clustering:\n{str(e)}"
            )
    
    def _export_clustering_data(self):
        """Export clustering data to JSON file"""
        if not self.clustering_results:
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Clustering Data",
            "gmm_clustering_results.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Prepare export data (make it JSON serializable)
                export_data = {
                    'clustering_method': self.clustering_results.get('method', 'unknown'),
                    'total_matches': len(self.all_matches),
                    'num_clusters': len(self.clustering_results.get('clusters', [])),
                    'clusters': []
                }
                
                for cluster in self.clustering_results.get('clusters', []):
                    cluster_data = {
                        'cluster_id': cluster.get('cluster_id', -1),
                        'type': cluster.get('type', 'Unknown'),
                        'size': cluster.get('size', 0),
                        'mean_redshift': float(cluster.get('mean_redshift', 0)),
                        'redshift_scatter': float(cluster.get('redshift_scatter', 0)),
                        'quality_score': float(cluster.get('quality_score', 0)),
                        'is_winning': cluster.get('is_winning', False)
                    }
                    export_data['clusters'].append(cluster_data)
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                self._show_status_message(f"Clustering data exported to {file_path}")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export clustering data:\n{str(e)}"
                )
    
    def _export_plot(self):
        """Export the plot to image file"""
        if not hasattr(self, 'fig'):
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Plot",
            "gmm_clustering_plot.png",
            "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                # Export matplotlib figure
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight', 
                               facecolor='white', edgecolor='none')
                
                self._show_status_message(f"Plot exported to {file_path}")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export plot:\n{str(e)}"
                )
    
    def _show_status_message(self, message):
        """Show a temporary status message"""
        _LOGGER.info(message)


def show_gmm_clustering_dialog(parent, analysis_results=None):
    """
    Show the GMM clustering dialog.
    
    Args:
        parent: Parent window
        analysis_results: SNID analysis results object
        
    Returns:
        PySide6GMMClusteringDialog instance
    """
    dialog = PySide6GMMClusteringDialog(parent, analysis_results)
    dialog.show()
    return dialog 