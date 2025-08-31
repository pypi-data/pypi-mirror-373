"""
Result Type Definitions for SNID SAGE
=====================================

Data structures for analysis results, output formatting, and report generation.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from enum import Enum
import json


class OutputFormat(Enum):
    """Supported output formats"""
    JSON = "json"
    TEXT = "text" 
    HTML = "html"
    CSV = "csv"
    FITS = "fits"


class AnalysisStatus(Enum):
    """Analysis status codes"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    RUNNING = "running"
    QUEUED = "queued"


@dataclass
class AnalysisSession:
    """
    Complete analysis session information.
    
    Contains all information about an analysis run including metadata.
    """
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    input_file: Optional[str] = None
    status: AnalysisStatus = AnalysisStatus.QUEUED
    runtime: float = 0.0
    memory_usage: Optional[float] = None
    version: str = "1.0.0"
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Optional[Any] = None  # Will contain SNIDResult
    logs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SummaryReport:
    """
    High-level summary of analysis results.
    
    Contains the most important results in a condensed format.
    """
    classification: str = "Unknown"
    subtype: Optional[str] = None
    redshift: float = 0.0
    redshift_error: float = 0.0
    age: Optional[float] = None
    age_error: Optional[float] = None
    confidence: float = 0.0
    quality_score: float = 0.0
    best_templates: List[str] = field(default_factory=list)
    key_lines: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass 
class DetailedReport:
    """
    Detailed analysis report with full results.
    
    Contains comprehensive information about the analysis.
    """
    summary: SummaryReport
    session: AnalysisSession
    spectrum_info: Dict[str, Any] = field(default_factory=dict)
    processing_info: Dict[str, Any] = field(default_factory=dict)
    template_matches: List[Dict[str, Any]] = field(default_factory=list)
    line_identifications: List[Dict[str, Any]] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    plots: List[str] = field(default_factory=list)  # Plot file paths
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization"""
        return {
            'summary': {
                'classification': self.summary.classification,
                'subtype': self.summary.subtype,
                'redshift': self.summary.redshift,
                'redshift_error': self.summary.redshift_error,
                'age': self.summary.age,
                'age_error': self.summary.age_error,
                'confidence': self.summary.confidence,
                'quality_score': self.summary.quality_score,
                'best_templates': self.summary.best_templates,
                'key_lines': self.summary.key_lines,
                'notes': self.summary.notes
            },
            'session': {
                'session_id': self.session.session_id,
                'timestamp': self.session.timestamp.isoformat(),
                'input_file': self.session.input_file,
                'status': self.session.status.value,
                'runtime': self.session.runtime,
                'version': self.session.version,
                'parameters': self.session.parameters
            },
            'spectrum_info': self.spectrum_info,
            'processing_info': self.processing_info,
            'template_matches': self.template_matches,
            'line_identifications': self.line_identifications,
            'quality_metrics': self.quality_metrics,
            'plots': self.plots
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class ExportOptions:
    """
    Options for exporting analysis results.
    
    Controls how results are formatted and exported.
    """
    format: OutputFormat = OutputFormat.JSON
    include_plots: bool = True
    include_templates: bool = False
    include_processing_steps: bool = True
    include_line_identifications: bool = True
    max_templates: int = 10
    precision: int = 4  # Decimal places for numerical values
    compress: bool = False
    output_directory: Optional[str] = None
    filename_prefix: str = "snid_result"


@dataclass
class ComparisonResult:
    """
    Result of comparing multiple analyses.
    
    Used for batch processing or comparing different parameter sets.
    """
    input_files: List[str]
    results: List[Any] = field(default_factory=list)  # List of SNIDResult objects
    consensus: Optional[Dict[str, Any]] = None
    agreements: Dict[str, float] = field(default_factory=dict)
    discrepancies: List[str] = field(default_factory=list)
    statistics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """
    Result of validating analysis results against known data.
    
    Used for testing and quality assurance.
    """
    true_type: str
    true_redshift: Optional[float] = None
    true_age: Optional[float] = None
    predicted_type: str = "Unknown"
    predicted_redshift: float = 0.0
    predicted_age: Optional[float] = None
    type_correct: bool = False
    redshift_error: Optional[float] = None
    age_error: Optional[float] = None
    confidence_score: float = 0.0
    notes: str = ""


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for analysis runs.
    
    Used for optimization and monitoring.
    """
    total_runtime: float = 0.0
    preprocessing_time: float = 0.0
    correlation_time: float = 0.0
    template_loading_time: float = 0.0
    memory_peak: Optional[float] = None
    cpu_usage: Optional[float] = None
    templates_processed: int = 0
    correlations_computed: int = 0
    success_rate: float = 0.0 