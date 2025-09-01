"""
Core Exceptions for SNID SAGE
=============================

Custom exception classes for better error handling and debugging
throughout the SNID SAGE application.
"""


class SNIDError(Exception):
    """
    Base exception class for all SNID-related errors.
    
    All other SNID exceptions inherit from this base class,
    allowing for easy catching of any SNID-related error.
    """
    pass


class SpectrumLoadError(SNIDError):
    """
    Raised when there is an error loading a spectrum file.
    
    This includes file format errors, missing files, corrupted data,
    or unsupported spectrum formats.
    """
    pass


class SpectrumProcessingError(SNIDError):
    """
    Raised when there is an error during spectrum preprocessing.
    
    This includes errors in smoothing, normalization, rebinning,
    or other spectrum processing operations.
    """
    pass


class AnalysisError(SNIDError):
    """
    Raised when there is an error during SNID analysis.
    
    This includes correlation failures, template matching errors,
    or other analysis-related problems.
    """
    pass


class TemplateError(SNIDError):
    """
    Raised when there is an error with template handling.
    
    This includes missing templates, corrupted template files,
    template loading errors, or template format problems.
    """
    pass


class ConfigurationError(SNIDError):
    """
    Raised when there is an error with configuration settings.
    
    This includes invalid parameter values, missing configuration files,
    or incompatible configuration options.
    """
    pass


class RedshiftError(SNIDError):
    """
    Raised when there is an error with redshift calculations.
    
    This includes invalid redshift ranges, calculation failures,
    or redshift fitting problems.
    """
    pass


class MaskingError(SNIDError):
    """
    Raised when there is an error with wavelength masking operations.
    
    This includes invalid mask ranges, mask application failures,
    or mask parsing errors.
    """
    pass


class PlottingError(SNIDError):
    """
    Raised when there is an error with plotting operations.
    
    This includes matplotlib errors, plot generation failures,
    or plot saving problems.
    """
    pass


class LLMError(SNIDError):
    """
    Raised when there is an error with LLM (Large Language Model) operations.
    
    This includes API connection errors, response parsing failures,
    or LLM configuration problems.
    """
    pass


class ImportError(SNIDError):
    """
    Raised when there is an error importing required dependencies.
    
    This includes missing packages, version incompatibilities,
    or module loading failures.
    """
    pass


class ValidationError(SNIDError):
    """
    Raised when data validation fails.
    
    This includes invalid input data, parameter validation failures,
    or data consistency checks.
    """
    pass 