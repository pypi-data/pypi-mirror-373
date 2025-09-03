"""
SNID SAGE - Shared Constants Package
====================================

This package contains all constants used throughout SNID SAGE including
physical constants, astronomical constants, and analysis parameters.
"""

# Import all physical constants
from .physical import *

# Version information  
__version__ = '1.0.0'
__author__ = 'SNID SAGE Team'

# Make key constants easily accessible
__all__ = [
    # Speed of light
    'SPEED_OF_LIGHT',
    'SPEED_OF_LIGHT_KMS',
    
    # Hydrogen lines
    'HYDROGEN_ALPHA',
    'HYDROGEN_BETA', 
    'HYDROGEN_GAMMA',
    'HYDROGEN_DELTA',
    
    # Helium lines
    'HELIUM_I_5876',
    'HELIUM_I_6678',
    'HELIUM_I_7065',
    
    # Calcium lines
    'CALCIUM_II_H',
    'CALCIUM_II_K',
    
    # Silicon lines
    'SILICON_II_6355',
    'SILICON_II_5972',
    
    # Iron lines
    'IRON_II_5169',
    'IRON_III_5129',
    
    # Sodium lines
    'SODIUM_D1',
    'SODIUM_D2',
    
    # Oxygen lines
    'OXYGEN_I_7774',
    'OXYGEN_I_8446',
    
    # Supernova emission lines database
    'SUPERNOVA_EMISSION_LINES',
    'SN_LINE_CATEGORIES',
    
    # Galaxy lines database
    'GALAXY_LINES',
    
    # Analysis constants
    'REDSHIFT_TOLERANCE',
    'WAVELENGTH_TOLERANCE',
    'DEFAULT_VELOCITY_RANGE',
    
    # Conversion factors
    'ANGSTROM_TO_NM',
    'ANGSTROM_TO_MICRON',
    
    # Wavelength ranges
    'OPTICAL_BLUE_MIN',
    'OPTICAL_BLUE_MAX',
    'OPTICAL_RED_MIN',
    'OPTICAL_RED_MAX',
    'NEAR_IR_MIN', 
    'NEAR_IR_MAX',
    
    # Template constants
    'MIN_CORRELATION_LENGTH',
    'DEFAULT_TEMPLATE_RESOLUTION'
] 