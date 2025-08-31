"""
SNID SAGE - Wind Analysis Utilities
===================================

Utility functions for wind velocity analysis in supernova spectra.
Provides calculations and analysis tools for P-Cygni profile analysis.

Part of the SNID SAGE shared utilities.
"""

from .wind_calculations import (
    calculate_wind_velocity,
    calculate_doppler_shift,
    estimate_terminal_velocity,
    analyze_pcygni_profile,
    validate_wind_measurement
)

from .pcygni_fitting import (
    fit_pcygni_profile,
    find_emission_peak,
    find_absorption_minimum,
    estimate_profile_parameters
)

__all__ = [
    'calculate_wind_velocity',
    'calculate_doppler_shift', 
    'estimate_terminal_velocity',
    'analyze_pcygni_profile',
    'validate_wind_measurement',
    'fit_pcygni_profile',
    'find_emission_peak',
    'find_absorption_minimum',
    'estimate_profile_parameters'
] 