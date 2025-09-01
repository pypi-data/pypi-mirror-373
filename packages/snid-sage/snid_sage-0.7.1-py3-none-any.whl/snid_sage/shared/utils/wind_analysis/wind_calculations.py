"""
SNID SAGE - Wind Velocity Calculations
======================================

Core calculations for wind velocity analysis in supernova spectra.
Implements proper astrophysical formulas for P-Cygni profile analysis.

Part of the SNID SAGE shared utilities.
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any
import warnings

# Import physical constants
try:
    from snid_sage.shared.constants.physical import SPEED_OF_LIGHT_KMS
except ImportError:
    SPEED_OF_LIGHT_KMS = 299792.458  # km/s

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('wind_calculations')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('wind_calculations')


def calculate_wind_velocity(emission_wavelength, absorption_wavelength, rest_wavelength, 
                           method='doppler', relativistic=False):
    """
    Calculate wind velocity from P-Cygni profile measurements
    
    Args:
        emission_wavelength (float): Observed emission peak wavelength (Å)
        absorption_wavelength (float): Observed absorption minimum wavelength (Å) 
        rest_wavelength (float): Rest wavelength of the line (Å)
        method (str): Calculation method ('doppler', 'terminal', 'average')
        relativistic (bool): Use relativistic formula for high velocities
        
    Returns:
        dict: Wind velocity results including velocity, uncertainty, and method info
    """
    try:
        # Validate inputs
        if not all([emission_wavelength, absorption_wavelength, rest_wavelength]):
            raise ValueError("All wavelength values must be provided and non-zero")
        
        if emission_wavelength <= 0 or absorption_wavelength <= 0 or rest_wavelength <= 0:
            raise ValueError("All wavelength values must be positive")
        
        # Calculate velocity based on method
        if method == 'doppler':
            velocity = _calculate_doppler_velocity(emission_wavelength, absorption_wavelength, 
                                                 rest_wavelength, relativistic)
        elif method == 'terminal':
            velocity = _calculate_terminal_velocity(absorption_wavelength, rest_wavelength, 
                                                  relativistic)
        elif method == 'average':
            v_doppler = _calculate_doppler_velocity(emission_wavelength, absorption_wavelength, 
                                                  rest_wavelength, relativistic)
            v_terminal = _calculate_terminal_velocity(absorption_wavelength, rest_wavelength, 
                                                    relativistic)
            velocity = (v_doppler + v_terminal) / 2.0
        else:
            raise ValueError(f"Unknown calculation method: {method}")
        
        # Estimate uncertainty (basic approximation)
        uncertainty = _estimate_velocity_uncertainty(velocity, rest_wavelength)
        
        # Determine if relativistic effects are significant
        is_relativistic = velocity > 10000  # > 10,000 km/s
        
        result = {
            'wind_velocity': abs(velocity),  # Take absolute value
            'velocity_uncertainty': uncertainty,
            'method': method,
            'relativistic': relativistic or is_relativistic,
            'emission_wavelength': emission_wavelength,
            'absorption_wavelength': absorption_wavelength,
            'rest_wavelength': rest_wavelength,
            'wavelength_separation': abs(emission_wavelength - absorption_wavelength)
        }
        
        _LOGGER.debug(f"Calculated wind velocity: {result['wind_velocity']:.1f} ± {uncertainty:.1f} km/s")
        return result
        
    except Exception as e:
        _LOGGER.error(f"Error calculating wind velocity: {e}")
        raise


def _calculate_doppler_velocity(emission_wavelength, absorption_wavelength, rest_wavelength, 
                               relativistic=False):
    """Calculate velocity using Doppler formula"""
    # Use the wavelength separation for velocity calculation
    delta_lambda = abs(emission_wavelength - absorption_wavelength)
    
    if relativistic:
        # Relativistic Doppler formula
        z = delta_lambda / rest_wavelength
        if z >= 1.0:
            warnings.warn("Extremely high redshift detected, capping at z=0.99")
            z = 0.99
        
        # v = c * [(1+z)² - 1] / [(1+z)² + 1]
        z_plus_1_squared = (1 + z) ** 2
        velocity = SPEED_OF_LIGHT_KMS * (z_plus_1_squared - 1) / (z_plus_1_squared + 1)
    else:
        # Non-relativistic Doppler approximation: v = c * Δλ / λ₀
        velocity = (delta_lambda / rest_wavelength) * SPEED_OF_LIGHT_KMS
    
    return velocity


def _calculate_terminal_velocity(absorption_wavelength, rest_wavelength, relativistic=False):
    """Calculate terminal velocity from absorption minimum"""
    # Calculate redshift of absorption minimum
    z_abs = (absorption_wavelength - rest_wavelength) / rest_wavelength
    
    if relativistic:
        # Relativistic formula
        if abs(z_abs) >= 1.0:
            warnings.warn("Extremely high redshift detected, capping velocity")
            z_abs = 0.99 if z_abs > 0 else -0.99
        
        if z_abs > 0:
            velocity = SPEED_OF_LIGHT_KMS * ((1 + z_abs)**2 - 1) / ((1 + z_abs)**2 + 1)
        else:
            velocity = -SPEED_OF_LIGHT_KMS * (1 - (1 + z_abs)**2) / (1 + (1 + z_abs)**2)
    else:
        # Non-relativistic approximation
        velocity = z_abs * SPEED_OF_LIGHT_KMS
    
    return abs(velocity)  # Return absolute value for terminal velocity


def calculate_doppler_shift(observed_wavelength, rest_wavelength, relativistic=False):
    """
    Calculate Doppler shift and corresponding velocity
    
    Args:
        observed_wavelength (float): Observed wavelength (Å)
        rest_wavelength (float): Rest wavelength (Å)
        relativistic (bool): Use relativistic formula
        
    Returns:
        dict: Doppler shift results
    """
    try:
        # Calculate redshift
        z = (observed_wavelength - rest_wavelength) / rest_wavelength
        
        # Calculate velocity
        if relativistic and abs(z) > 0.01:  # Use relativistic for z > 1%
            if abs(z) >= 1.0:
                warnings.warn("Extremely high redshift detected")
                z = 0.99 if z > 0 else -0.99
            
            # Relativistic formula
            if z > 0:
                velocity = SPEED_OF_LIGHT_KMS * ((1 + z)**2 - 1) / ((1 + z)**2 + 1)
            else:
                velocity = -SPEED_OF_LIGHT_KMS * (1 - (1 + z)**2) / (1 + (1 + z)**2)
        else:
            # Non-relativistic approximation
            velocity = z * SPEED_OF_LIGHT_KMS
        
        return {
            'redshift': z,
            'velocity': velocity,
            'observed_wavelength': observed_wavelength,
            'rest_wavelength': rest_wavelength,
            'relativistic': relativistic and abs(z) > 0.01
        }
        
    except Exception as e:
        _LOGGER.error(f"Error calculating Doppler shift: {e}")
        raise


def estimate_terminal_velocity(absorption_wavelength, rest_wavelength, line_type='permitted'):
    """
    Estimate terminal velocity from absorption minimum
    
    Args:
        absorption_wavelength (float): Absorption minimum wavelength (Å)
        rest_wavelength (float): Rest wavelength (Å)
        line_type (str): Type of line ('permitted', 'forbidden', 'semi-forbidden')
        
    Returns:
        dict: Terminal velocity estimation results
    """
    try:
        # Calculate basic terminal velocity
        doppler_result = calculate_doppler_shift(absorption_wavelength, rest_wavelength, 
                                               relativistic=True)
        terminal_velocity = abs(doppler_result['velocity'])
        
        # Apply corrections based on line type
        correction_factor = 1.0
        if line_type == 'permitted':
            correction_factor = 1.0  # No correction for permitted lines
        elif line_type == 'semi-forbidden':
            correction_factor = 0.8  # Semi-forbidden lines form slightly deeper
        elif line_type == 'forbidden':
            correction_factor = 0.6  # Forbidden lines form much deeper
        
        corrected_velocity = terminal_velocity * correction_factor
        
        # Estimate uncertainty based on line type
        if line_type == 'permitted':
            uncertainty_factor = 0.1  # 10% uncertainty
        elif line_type == 'semi-forbidden':
            uncertainty_factor = 0.15  # 15% uncertainty
        else:
            uncertainty_factor = 0.2  # 20% uncertainty for forbidden lines
        
        uncertainty = corrected_velocity * uncertainty_factor
        
        return {
            'terminal_velocity': corrected_velocity,
            'raw_velocity': terminal_velocity,
            'correction_factor': correction_factor,
            'velocity_uncertainty': uncertainty,
            'line_type': line_type,
            'absorption_wavelength': absorption_wavelength,
            'rest_wavelength': rest_wavelength
        }
        
    except Exception as e:
        _LOGGER.error(f"Error estimating terminal velocity: {e}")
        raise


def analyze_pcygni_profile(wavelength, flux, rest_wavelength, redshift=0.0):
    """
    Analyze a P-Cygni profile to extract wind velocity information
    
    Args:
        wavelength (array): Wavelength array (Å)
        flux (array): Flux array
        rest_wavelength (float): Rest wavelength of the line (Å)
        redshift (float): Systemic redshift
        
    Returns:
        dict: P-Cygni profile analysis results
    """
    try:
        wavelength = np.array(wavelength)
        flux = np.array(flux)
        
        if len(wavelength) != len(flux):
            raise ValueError("Wavelength and flux arrays must have same length")
        
        # Expected line position with redshift
        expected_wavelength = rest_wavelength * (1 + redshift)
        
        # Define search range around expected position (±50 Å)
        search_range = 50.0
        mask = np.abs(wavelength - expected_wavelength) <= search_range
        
        if not np.any(mask):
            raise ValueError("No data found in search range around expected line position")
        
        search_wave = wavelength[mask]
        search_flux = flux[mask]
        
        # Find continuum level (average of edges)
        edge_fraction = 0.1  # Use 10% of data from each edge
        n_edge = max(1, int(len(search_flux) * edge_fraction))
        
        continuum_level = np.mean(np.concatenate([
            search_flux[:n_edge],
            search_flux[-n_edge:]
        ]))
        
        # Find emission peak (maximum above continuum)
        emission_candidates = search_flux > continuum_level * 1.1  # 10% above continuum
        if np.any(emission_candidates):
            emission_idx = np.argmax(search_flux[emission_candidates])
            emission_indices = np.where(emission_candidates)[0]
            emission_wavelength = search_wave[emission_indices[emission_idx]]
            emission_flux = search_flux[emission_indices[emission_idx]]
        else:
            emission_wavelength = None
            emission_flux = None
        
        # Find absorption minimum (minimum below continuum)
        absorption_candidates = search_flux < continuum_level * 0.9  # 10% below continuum
        if np.any(absorption_candidates):
            absorption_idx = np.argmin(search_flux[absorption_candidates])
            absorption_indices = np.where(absorption_candidates)[0]
            absorption_wavelength = search_wave[absorption_indices[absorption_idx]]
            absorption_flux = search_flux[absorption_indices[absorption_idx]]
        else:
            absorption_wavelength = None
            absorption_flux = None
        
        # Calculate profile characteristics
        profile_strength = None
        equivalent_width = None
        
        if emission_flux is not None and absorption_flux is not None:
            profile_strength = (emission_flux - absorption_flux) / continuum_level
            
            # Estimate equivalent width (simplified)
            line_mask = (search_wave >= min(absorption_wavelength, emission_wavelength) - 5) & \
                       (search_wave <= max(absorption_wavelength, emission_wavelength) + 5)
            if np.any(line_mask):
                continuum_flux = continuum_level * np.ones_like(search_wave[line_mask])
                flux_ratio = 1 - search_flux[line_mask] / continuum_flux
                equivalent_width = np.trapz(flux_ratio, search_wave[line_mask])
        
        return {
            'emission_wavelength': emission_wavelength,
            'emission_flux': emission_flux,
            'absorption_wavelength': absorption_wavelength,
            'absorption_flux': absorption_flux,
            'continuum_level': continuum_level,
            'profile_strength': profile_strength,
            'equivalent_width': equivalent_width,
            'expected_wavelength': expected_wavelength,
            'search_range': search_range,
            'has_emission': emission_wavelength is not None,
            'has_absorption': absorption_wavelength is not None,
            'is_pcygni': emission_wavelength is not None and absorption_wavelength is not None
        }
        
    except Exception as e:
        _LOGGER.error(f"Error analyzing P-Cygni profile: {e}")
        raise


def validate_wind_measurement(emission_wavelength, absorption_wavelength, rest_wavelength, 
                             min_separation=1.0, max_velocity=50000):
    """
    Validate wind velocity measurements for physical reasonableness
    
    Args:
        emission_wavelength (float): Emission peak wavelength (Å)
        absorption_wavelength (float): Absorption minimum wavelength (Å)
        rest_wavelength (float): Rest wavelength (Å)
        min_separation (float): Minimum wavelength separation (Å)
        max_velocity (float): Maximum reasonable velocity (km/s)
        
    Returns:
        dict: Validation results with warnings and recommendations
    """
    try:
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'recommendations': [],
            'quality_score': 1.0
        }
        
        # Check wavelength separation
        separation = abs(emission_wavelength - absorption_wavelength)
        if separation < min_separation:
            validation_result['warnings'].append(
                f"Small wavelength separation ({separation:.2f} Å) may indicate poor resolution"
            )
            validation_result['quality_score'] *= 0.7
        
        # Check for reasonable wavelength ordering (absorption should be bluer)
        if absorption_wavelength > emission_wavelength:
            validation_result['warnings'].append(
                "Absorption wavelength is redder than emission - unusual for P-Cygni profiles"
            )
            validation_result['quality_score'] *= 0.8
        
        # Calculate velocity for validation
        velocity_result = calculate_wind_velocity(emission_wavelength, absorption_wavelength, 
                                                rest_wavelength, method='doppler')
        velocity = velocity_result['wind_velocity']
        
        # Check velocity magnitude
        if velocity > max_velocity:
            validation_result['warnings'].append(
                f"Very high velocity ({velocity:.0f} km/s) - check measurements"
            )
            validation_result['quality_score'] *= 0.6
        elif velocity < 100:
            validation_result['warnings'].append(
                f"Very low velocity ({velocity:.0f} km/s) - may not be wind-driven"
            )
            validation_result['quality_score'] *= 0.8
        
        # Check relative separations
        relative_separation = separation / rest_wavelength
        if relative_separation < 0.001:  # < 0.1% of rest wavelength
            validation_result['warnings'].append(
                "Wavelength separation is very small relative to rest wavelength"
            )
            validation_result['quality_score'] *= 0.7
        
        
        if validation_result['quality_score'] < 0.8:
            validation_result['recommendations'].append(
                "Consider remeasuring line positions for better accuracy"
            )
        
        if velocity > 20000:
            validation_result['recommendations'].append(
                "High velocity suggests relativistic effects - consider using relativistic formula"
            )
        
        if len(validation_result['warnings']) > 2:
            validation_result['is_valid'] = False
            validation_result['recommendations'].append(
                "Multiple issues detected - measurement may not be reliable"
            )
        
        # Add velocity to result
        validation_result['calculated_velocity'] = velocity
        validation_result['wavelength_separation'] = separation
        validation_result['relative_separation'] = relative_separation
        
        return validation_result
        
    except Exception as e:
        _LOGGER.error(f"Error validating wind measurement: {e}")
        return {
            'is_valid': False,
            'warnings': [f"Validation error: {str(e)}"],
            'recommendations': ["Check input data and try again"],
            'quality_score': 0.0
        }


def _estimate_velocity_uncertainty(velocity, rest_wavelength, wavelength_precision=0.1):
    """
    Estimate uncertainty in velocity measurement
    
    Args:
        velocity (float): Measured velocity (km/s)
        rest_wavelength (float): Rest wavelength (Å)
        wavelength_precision (float): Precision of wavelength measurement (Å)
        
    Returns:
        float: Estimated velocity uncertainty (km/s)
    """
    # Basic uncertainty from wavelength measurement precision
    relative_uncertainty = wavelength_precision / rest_wavelength
    velocity_uncertainty = velocity * relative_uncertainty
    
    # Add systematic uncertainties (minimum 50 km/s for typical measurements)
    systematic_uncertainty = 50.0
    
    # Combine in quadrature
    total_uncertainty = np.sqrt(velocity_uncertainty**2 + systematic_uncertainty**2)
    
    return total_uncertainty