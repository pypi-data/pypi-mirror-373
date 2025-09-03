"""
SNID SAGE - P-Cygni Profile Fitting
===================================

Utilities for fitting and analyzing P-Cygni profiles in supernova spectra.
Provides automated detection of emission peaks and absorption minima.

Part of the SNID SAGE shared utilities.
"""

import numpy as np
from scipy import optimize, signal
from typing import Tuple, Optional, Dict, Any, List
import warnings

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('pcygni_fitting')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('pcygni_fitting')


def fit_pcygni_profile(wavelength, flux, rest_wavelength, redshift=0.0, fit_model='gaussian'):
    """
    Fit a P-Cygni profile to extract emission and absorption components
    
    Args:
        wavelength (array): Wavelength array (Å)
        flux (array): Flux array
        rest_wavelength (float): Rest wavelength of the line (Å)
        redshift (float): Systemic redshift
        fit_model (str): Fitting model ('gaussian', 'voigt', 'simple')
        
    Returns:
        dict: Fitting results with emission and absorption parameters
    """
    try:
        wavelength = np.array(wavelength)
        flux = np.array(flux)
        
        if len(wavelength) != len(flux):
            raise ValueError("Wavelength and flux arrays must have same length")
        
        # Expected line position
        expected_wavelength = rest_wavelength * (1 + redshift)
        
        # Define fitting region (±100 Å around expected position)
        fit_range = 100.0
        mask = np.abs(wavelength - expected_wavelength) <= fit_range
        
        if not np.any(mask):
            raise ValueError("No data in fitting range")
        
        fit_wave = wavelength[mask]
        fit_flux = flux[mask]
        
        # Estimate continuum
        continuum = _estimate_continuum(fit_wave, fit_flux)
        normalized_flux = fit_flux / continuum
        
        # Find initial guesses for emission and absorption
        emission_guess = find_emission_peak(fit_wave, normalized_flux)
        absorption_guess = find_absorption_minimum(fit_wave, normalized_flux)
        
        if fit_model == 'gaussian':
            fit_result = _fit_gaussian_pcygni(fit_wave, normalized_flux, 
                                            emission_guess, absorption_guess)
        elif fit_model == 'voigt':
            fit_result = _fit_voigt_pcygni(fit_wave, normalized_flux, 
                                         emission_guess, absorption_guess)
        else:  # simple
            fit_result = _fit_simple_pcygni(fit_wave, normalized_flux,
                                          emission_guess, absorption_guess)
        
        # Add metadata
        fit_result.update({
            'rest_wavelength': rest_wavelength,
            'expected_wavelength': expected_wavelength,
            'redshift': redshift,
            'fit_model': fit_model,
            'continuum_level': continuum,
            'fit_range': fit_range,
            'n_points': len(fit_wave)
        })
        
        return fit_result
        
    except Exception as e:
        _LOGGER.error(f"Error fitting P-Cygni profile: {e}")
        raise


def find_emission_peak(wavelength, flux, smooth_window=5):
    """
    Find emission peak in spectrum
    
    Args:
        wavelength (array): Wavelength array
        flux (array): Flux array (should be normalized)
        smooth_window (int): Smoothing window size
        
    Returns:
        dict: Emission peak parameters
    """
    try:
        wavelength = np.array(wavelength)
        flux = np.array(flux)
        
        # Smooth flux for peak finding
        if smooth_window > 1 and len(flux) > smooth_window:
            smoothed_flux = signal.savgol_filter(flux, smooth_window, 2)
        else:
            smoothed_flux = flux
        
        # Find peaks above continuum (flux > 1.0 for normalized flux)
        peaks, properties = signal.find_peaks(smoothed_flux, 
                                            height=1.02,  # 2% above continuum
                                            distance=3)    # Minimum 3 points apart
        
        if len(peaks) == 0:
            # No clear peaks found, use maximum
            peak_idx = np.argmax(smoothed_flux)
            peak_height = smoothed_flux[peak_idx]
            peak_prominence = peak_height - 1.0
        else:
            # Use strongest peak
            peak_heights = properties['peak_heights']
            strongest_peak_idx = np.argmax(peak_heights)
            peak_idx = peaks[strongest_peak_idx]
            peak_height = peak_heights[strongest_peak_idx]
            peak_prominence = peak_height - 1.0
        
        # Estimate peak width (FWHM)
        peak_width = _estimate_peak_width(wavelength, smoothed_flux, peak_idx)
        
        return {
            'wavelength': wavelength[peak_idx],
            'flux': flux[peak_idx],
            'smoothed_flux': smoothed_flux[peak_idx],
            'height': peak_height,
            'prominence': peak_prominence,
            'width': peak_width,
            'index': peak_idx,
            'found_peak': len(peaks) > 0
        }
        
    except Exception as e:
        _LOGGER.error(f"Error finding emission peak: {e}")
        return {
            'wavelength': None,
            'flux': None,
            'height': None,
            'prominence': None,
            'width': None,
            'index': None,
            'found_peak': False
        }


def find_absorption_minimum(wavelength, flux, smooth_window=5):
    """
    Find absorption minimum in spectrum
    
    Args:
        wavelength (array): Wavelength array
        flux (array): Flux array (should be normalized)
        smooth_window (int): Smoothing window size
        
    Returns:
        dict: Absorption minimum parameters
    """
    try:
        wavelength = np.array(wavelength)
        flux = np.array(flux)
        
        # Smooth flux for minimum finding
        if smooth_window > 1 and len(flux) > smooth_window:
            smoothed_flux = signal.savgol_filter(flux, smooth_window, 2)
        else:
            smoothed_flux = flux
        
        # Find minima below continuum (flux < 1.0 for normalized flux)
        # Invert flux to find minima as peaks
        inverted_flux = -smoothed_flux
        peaks, properties = signal.find_peaks(inverted_flux,
                                            height=-0.98,  # 2% below continuum
                                            distance=3)    # Minimum 3 points apart
        
        if len(peaks) == 0:
            # No clear minima found, use minimum
            min_idx = np.argmin(smoothed_flux)
            min_depth = 1.0 - smoothed_flux[min_idx]
        else:
            # Use deepest minimum
            min_depths = -properties['peak_heights']  # Convert back from inverted
            deepest_min_idx = np.argmax(-min_depths)  # Deepest (most negative)
            min_idx = peaks[deepest_min_idx]
            min_depth = 1.0 - smoothed_flux[min_idx]
        
        # Estimate minimum width
        min_width = _estimate_peak_width(wavelength, -smoothed_flux, min_idx)
        
        return {
            'wavelength': wavelength[min_idx],
            'flux': flux[min_idx],
            'smoothed_flux': smoothed_flux[min_idx],
            'depth': min_depth,
            'width': min_width,
            'index': min_idx,
            'found_minimum': len(peaks) > 0
        }
        
    except Exception as e:
        _LOGGER.error(f"Error finding absorption minimum: {e}")
        return {
            'wavelength': None,
            'flux': None,
            'depth': None,
            'width': None,
            'index': None,
            'found_minimum': False
        }


def estimate_profile_parameters(wavelength, flux, emission_data, absorption_data):
    """
    Estimate P-Cygni profile parameters from emission and absorption data
    
    Args:
        wavelength (array): Wavelength array
        flux (array): Flux array
        emission_data (dict): Emission peak data
        absorption_data (dict): Absorption minimum data
        
    Returns:
        dict: Profile parameter estimates
    """
    try:
        if (emission_data['wavelength'] is None or 
            absorption_data['wavelength'] is None):
            return _empty_profile_parameters()
        
        # Basic measurements
        emission_wavelength = emission_data['wavelength']
        absorption_wavelength = absorption_data['wavelength']
        wavelength_separation = abs(emission_wavelength - absorption_wavelength)
        
        # Profile characteristics
        emission_strength = emission_data.get('prominence', 0)
        absorption_depth = absorption_data.get('depth', 0)
        profile_asymmetry = (emission_wavelength - absorption_wavelength) / wavelength_separation
        
        # Estimate velocity characteristics
        from .wind_calculations import calculate_doppler_shift
        
        # Get rest wavelength from middle of profile
        estimated_rest = (emission_wavelength + absorption_wavelength) / 2.0
        
        # Calculate velocities
        emission_velocity = calculate_doppler_shift(emission_wavelength, estimated_rest)
        absorption_velocity = calculate_doppler_shift(absorption_wavelength, estimated_rest)
        
        # Profile quality assessment
        quality_score = _assess_profile_quality(emission_data, absorption_data, 
                                              wavelength_separation)
        
        return {
            'emission_wavelength': emission_wavelength,
            'absorption_wavelength': absorption_wavelength,
            'wavelength_separation': wavelength_separation,
            'emission_strength': emission_strength,
            'absorption_depth': absorption_depth,
            'profile_asymmetry': profile_asymmetry,
            'emission_velocity': emission_velocity['velocity'],
            'absorption_velocity': absorption_velocity['velocity'],
            'quality_score': quality_score,
            'has_valid_profile': quality_score > 0.5,
            'estimated_rest_wavelength': estimated_rest
        }
        
    except Exception as e:
        _LOGGER.error(f"Error estimating profile parameters: {e}")
        return _empty_profile_parameters()


def _estimate_continuum(wavelength, flux, edge_fraction=0.15):
    """Estimate continuum level from spectrum edges"""
    n_points = len(flux)
    n_edge = max(3, int(n_points * edge_fraction))
    
    # Use median of edge regions for robustness
    left_continuum = np.median(flux[:n_edge])
    right_continuum = np.median(flux[-n_edge:])
    
    # Use average of both edges
    continuum = (left_continuum + right_continuum) / 2.0
    
    return continuum


def _estimate_peak_width(wavelength, flux, peak_idx, fraction=0.5):
    """Estimate peak width at given fraction of peak height"""
    try:
        if peak_idx <= 0 or peak_idx >= len(flux) - 1:
            return 0.0
        
        peak_flux = flux[peak_idx]
        
        # For emission peaks (positive), find half maximum
        # For absorption peaks (negative flux), find half minimum
        if peak_flux > 0:
            target_flux = peak_flux * fraction
            comparison = lambda f: f >= target_flux
        else:
            target_flux = peak_flux * fraction
            comparison = lambda f: f <= target_flux
        
        # Find left and right boundaries
        left_idx = peak_idx
        while left_idx > 0 and comparison(flux[left_idx]):
            left_idx -= 1
        
        right_idx = peak_idx
        while right_idx < len(flux) - 1 and comparison(flux[right_idx]):
            right_idx += 1
        
        # Calculate width in wavelength units
        if right_idx > left_idx:
            width = wavelength[right_idx] - wavelength[left_idx]
        else:
            width = 0.0
        
        return width
        
    except:
        return 0.0


def _fit_gaussian_pcygni(wavelength, flux, emission_guess, absorption_guess):
    """Fit Gaussian components to P-Cygni profile"""
    try:
        # Define Gaussian function
        def gaussian(x, amp, center, sigma):
            return amp * np.exp(-0.5 * ((x - center) / sigma) ** 2)
        
        # Define P-Cygni model: continuum + emission Gaussian - absorption Gaussian
        def pcygni_model(x, cont, em_amp, em_center, em_sigma, abs_amp, abs_center, abs_sigma):
            emission = gaussian(x, em_amp, em_center, em_sigma)
            absorption = gaussian(x, abs_amp, abs_center, abs_sigma)
            return cont + emission - absorption
        
        # Initial parameter guess
        p0 = [
            1.0,  # continuum
            emission_guess.get('prominence', 0.1),  # emission amplitude
            emission_guess.get('wavelength', np.mean(wavelength)),  # emission center
            emission_guess.get('width', 5.0),  # emission sigma
            absorption_guess.get('depth', 0.1),  # absorption amplitude
            absorption_guess.get('wavelength', np.mean(wavelength)),  # absorption center
            absorption_guess.get('width', 5.0)  # absorption sigma
        ]
        
        # Parameter bounds
        bounds = (
            [0.5, 0.0, np.min(wavelength), 0.1, 0.0, np.min(wavelength), 0.1],  # lower
            [2.0, 1.0, np.max(wavelength), 50.0, 1.0, np.max(wavelength), 50.0]  # upper
        )
        
        # Fit the model
        popt, pcov = optimize.curve_fit(pcygni_model, wavelength, flux, p0=p0, bounds=bounds)
        
        # Calculate fit quality
        model_flux = pcygni_model(wavelength, *popt)
        residuals = flux - model_flux
        chi_squared = np.sum(residuals**2) / len(residuals)
        
        # Extract parameters
        cont, em_amp, em_center, em_sigma, abs_amp, abs_center, abs_sigma = popt
        
        return {
            'fit_successful': True,
            'continuum': cont,
            'emission_amplitude': em_amp,
            'emission_center': em_center,
            'emission_sigma': em_sigma,
            'absorption_amplitude': abs_amp,
            'absorption_center': abs_center,
            'absorption_sigma': abs_sigma,
            'chi_squared': chi_squared,
            'model_flux': model_flux,
            'residuals': residuals,
            'covariance_matrix': pcov
        }
        
    except Exception as e:
        _LOGGER.warning(f"Gaussian fitting failed: {e}")
        return _empty_fit_result()


def _fit_voigt_pcygni(wavelength, flux, emission_guess, absorption_guess):
    """Fit Voigt profile components (simplified as Gaussian for now)"""
    # For now, use Gaussian fitting as Voigt is more complex
    # In a full implementation, this would include Lorentzian broadening
    _LOGGER.info("Voigt fitting requested, using Gaussian approximation")
    return _fit_gaussian_pcygni(wavelength, flux, emission_guess, absorption_guess)


def _fit_simple_pcygni(wavelength, flux, emission_guess, absorption_guess):
    """Simple P-Cygni fitting using direct measurements"""
    try:
        emission_wave = emission_guess.get('wavelength')
        absorption_wave = absorption_guess.get('wavelength')
        
        if emission_wave is None or absorption_wave is None:
            return _empty_fit_result()
        
        # Find flux values at measured positions
        em_idx = np.argmin(np.abs(wavelength - emission_wave))
        abs_idx = np.argmin(np.abs(wavelength - absorption_wave))
        
        emission_flux = flux[em_idx]
        absorption_flux = flux[abs_idx]
        
        # Estimate continuum
        continuum = _estimate_continuum(wavelength, flux)
        
        return {
            'fit_successful': True,
            'continuum': continuum,
            'emission_center': emission_wave,
            'emission_flux': emission_flux,
            'absorption_center': absorption_wave,
            'absorption_flux': absorption_flux,
            'emission_strength': emission_flux - continuum,
            'absorption_depth': continuum - absorption_flux,
            'fit_method': 'simple_measurement'
        }
        
    except Exception as e:
        _LOGGER.warning(f"Simple fitting failed: {e}")
        return _empty_fit_result()


def _assess_profile_quality(emission_data, absorption_data, wavelength_separation):
    """Assess the quality of P-Cygni profile detection"""
    quality_score = 0.0
    
    # Check if both components were found
    if emission_data.get('found_peak', False):
        quality_score += 0.3
    if absorption_data.get('found_minimum', False):
        quality_score += 0.3
    
    # Check component strengths
    emission_prominence = emission_data.get('prominence', 0)
    absorption_depth = absorption_data.get('depth', 0)
    
    if emission_prominence > 0.02:  # 2% above continuum
        quality_score += 0.2
    if absorption_depth > 0.02:  # 2% below continuum
        quality_score += 0.2
    
    # Check wavelength separation (should be reasonable)
    if 1.0 <= wavelength_separation <= 100.0:
        quality_score += 0.1
    
    # Bonus for strong features
    if emission_prominence > 0.1 and absorption_depth > 0.1:
        quality_score += 0.1
    
    return min(quality_score, 1.0)


def _empty_profile_parameters():
    """Return empty profile parameters structure"""
    return {
        'emission_wavelength': None,
        'absorption_wavelength': None,
        'wavelength_separation': 0,
        'emission_strength': 0,
        'absorption_depth': 0,
        'profile_asymmetry': 0,
        'emission_velocity': 0,
        'absorption_velocity': 0,
        'quality_score': 0,
        'has_valid_profile': False,
        'estimated_rest_wavelength': None
    }


def _empty_fit_result():
    """Return empty fit result structure"""
    return {
        'fit_successful': False,
        'continuum': 1.0,
        'emission_center': None,
        'absorption_center': None,
        'chi_squared': np.inf,
        'model_flux': None,
        'residuals': None
    }