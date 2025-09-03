"""
SNID SAGE - FWHM Analysis Utilities
===================================

Utilities for measuring Full Width at Half Maximum (FWHM) of spectral lines.
Part of the SNID SAGE shared utilities.
"""

import numpy as np
from scipy import optimize, interpolate
from typing import Dict, List, Tuple, Optional, Any

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('fwhm_analysis')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('fwhm_analysis')


class FWHMAnalyzer:
    """FWHM analysis for spectral lines."""
    
    def __init__(self):
        self.last_fit_params = None
        self.last_fit_model = None
        
    def measure_fwhm_auto(self, wavelength: np.ndarray, flux: np.ndarray, 
                         line_center: float, window_width: float = 50.0) -> Dict[str, Any]:
        """Automatically measure FWHM using multiple methods."""
        # Extract line region
        mask = np.abs(wavelength - line_center) <= window_width / 2
        if np.sum(mask) < 10:
            return {'error': 'Insufficient data points in line region'}
        
        line_wave = wavelength[mask]
        line_flux = flux[mask]
        
        # Remove NaN/infinite values
        valid_mask = np.isfinite(line_wave) & np.isfinite(line_flux)
        if np.sum(valid_mask) < 5:
            return {'error': 'Insufficient valid data points'}
            
        line_wave = line_wave[valid_mask]
        line_flux = line_flux[valid_mask]
        
        results = {
            'line_center': line_center,
            'window_width': window_width,
            'analysis_region': {'wavelength': line_wave, 'flux': line_flux}
        }
        
        # Detect line type
        line_type = self._detect_line_type(line_wave, line_flux, line_center)
        results['line_type'] = line_type
        
        # Try multiple methods
        methods = ['gaussian', 'interpolation']
        for method in methods:
            try:
                if method == 'gaussian':
                    fit_result = self._fit_gaussian(line_wave, line_flux, line_type)
                elif method == 'interpolation':
                    fit_result = self._measure_fwhm_interpolation(line_wave, line_flux, line_type)
                
                if fit_result and 'fwhm' in fit_result:
                    results[f'{method}_fwhm'] = fit_result['fwhm']
                    results[f'{method}_fit'] = fit_result
                    
            except Exception as e:
                _LOGGER.warning(f"FWHM measurement failed for {method}: {e}")
                results[f'{method}_error'] = str(e)
        
        # Calculate best estimate
        fwhm_values = []
        for method in methods:
            if f'{method}_fwhm' in results:
                fwhm_values.append(results[f'{method}_fwhm'])
        
        if fwhm_values:
            results['best_fwhm'] = np.median(fwhm_values)
            results['fwhm_std'] = np.std(fwhm_values) if len(fwhm_values) > 1 else 0.0
        else:
            results['error'] = 'All FWHM measurement methods failed'
        
        return results
    
    def _detect_line_type(self, wavelength: np.ndarray, flux: np.ndarray, center: float) -> str:
        """Detect if line is emission or absorption."""
        center_idx = np.argmin(np.abs(wavelength - center))
        center_flux = flux[center_idx]
        
        # Estimate continuum from edges
        edge_indices = np.concatenate([
            np.arange(0, min(5, len(flux))),
            np.arange(max(0, len(flux)-5), len(flux))
        ])
        
        if len(edge_indices) > 0:
            continuum_level = np.median(flux[edge_indices])
        else:
            continuum_level = np.median(flux)
        
        return 'emission' if center_flux > continuum_level else 'absorption'
    
    def _fit_gaussian(self, wavelength: np.ndarray, flux: np.ndarray, line_type: str) -> Dict[str, Any]:
        """Fit Gaussian profile to measure FWHM."""
        def gaussian(x, amplitude, center, sigma, offset):
            return offset + amplitude * np.exp(-0.5 * ((x - center) / sigma) ** 2)
        
        # Initial estimates
        center_guess = wavelength[np.argmax(flux) if line_type == 'emission' else np.argmin(flux)]
        offset_guess = np.median([flux[0], flux[-1]])
        
        if line_type == 'emission':
            amplitude_guess = np.max(flux) - offset_guess
        else:
            amplitude_guess = np.min(flux) - offset_guess
        
        sigma_guess = (wavelength[-1] - wavelength[0]) / 10
        
        try:
            popt, pcov = optimize.curve_fit(
                gaussian, wavelength, flux, 
                p0=[amplitude_guess, center_guess, sigma_guess, offset_guess],
                maxfev=1000
            )
            
            amplitude, center, sigma, offset = popt
            fwhm = 2.355 * abs(sigma)  # FWHM for Gaussian
            
            fitted_flux = gaussian(wavelength, *popt)
            r_squared = 1 - (np.sum((flux - fitted_flux)**2) / np.sum((flux - np.mean(flux))**2))
            
            # Derive velocity in km/s relative to fitted center wavelength
            try:
                velocity_kms = 299792.458 * (float(fwhm) / float(center))
            except Exception:
                velocity_kms = None
            return {
                'fwhm': fwhm,
                'fwhm_vel': velocity_kms,
                'center': center,
                'amplitude': amplitude,
                'sigma': sigma,
                'offset': offset,
                'r_squared': r_squared,
                'fitted_flux': fitted_flux
            }
            
        except Exception as e:
            return {'error': f'Gaussian fit failed: {str(e)}'}
    
    def _measure_fwhm_interpolation(self, wavelength: np.ndarray, flux: np.ndarray, line_type: str) -> Dict[str, Any]:
        """Measure FWHM using interpolation method."""
        try:
            # Find line peak/trough
            if line_type == 'emission':
                peak_idx = np.argmax(flux)
                peak_flux = flux[peak_idx]
                continuum_flux = np.median([flux[0], flux[-1]])
                half_max = continuum_flux + (peak_flux - continuum_flux) / 2
            else:
                peak_idx = np.argmin(flux)
                peak_flux = flux[peak_idx]
                continuum_flux = np.median([flux[0], flux[-1]])
                half_max = continuum_flux + (peak_flux - continuum_flux) / 2
            
            peak_wavelength = wavelength[peak_idx]
            
            # Create interpolation function
            interp_func = interpolate.interp1d(wavelength, flux, kind='linear', 
                                             bounds_error=False, fill_value='extrapolate')
            
            # Find FWHM crossings
            dense_wave = np.linspace(wavelength[0], wavelength[-1], len(wavelength) * 10)
            dense_flux = interp_func(dense_wave)
            
            # Find crossings
            crossings = []
            for i in range(len(dense_flux) - 1):
                if ((dense_flux[i] <= half_max <= dense_flux[i+1]) or 
                    (dense_flux[i] >= half_max >= dense_flux[i+1])):
                    alpha = (half_max - dense_flux[i]) / (dense_flux[i+1] - dense_flux[i])
                    crossing_wave = dense_wave[i] + alpha * (dense_wave[i+1] - dense_wave[i])
                    crossings.append(crossing_wave)
            
            if len(crossings) >= 2:
                crossings = sorted(crossings)
                fwhm = crossings[-1] - crossings[0]
                
                # Derive velocity in km/s relative to peak wavelength
                try:
                    velocity_kms = 299792.458 * (float(fwhm) / float(peak_wavelength))
                except Exception:
                    velocity_kms = None
                return {
                    'fwhm': fwhm,
                    'fwhm_vel': velocity_kms,
                    'center': peak_wavelength,
                    'peak_flux': peak_flux,
                    'half_max': half_max,
                    'crossings': crossings,
                    'method': 'interpolation'
                }
            else:
                return {'error': 'Could not find FWHM crossings'}
                
        except Exception as e:
            return {'error': f'Interpolation FWHM failed: {str(e)}'}


def perform_line_fitting(spectrum_data, line_wavelength, method, zoom_range=30.0):
    """
    Perform line fitting and return comprehensive results.
    
    Args:
        spectrum_data: Dict with 'wavelength' and 'flux' arrays
        line_wavelength: Center wavelength for analysis
        method: Fitting method ('auto', 'gaussian', 'empirical')
        zoom_range: Range around line for analysis (Angstroms)
    
    Returns:
        Dict with fit results or None if failed
    """
    # Get spectrum data
    wavelength = spectrum_data['wavelength']
    flux = spectrum_data['flux']
    
    # Filter to analysis region around the line
    fit_range = zoom_range / 2  # Use half the zoom range for fitting
    mask = (wavelength >= line_wavelength - fit_range) & \
           (wavelength <= line_wavelength + fit_range)
    wl_region = wavelength[mask]
    flux_region = flux[mask]
    
    if len(wl_region) < 5:
        return None
        
    try:
        # Import scipy for Gaussian fitting
        try:
            from scipy.optimize import curve_fit
            SCIPY_AVAILABLE = True
        except ImportError:
            SCIPY_AVAILABLE = False
            
        if method == 'gaussian' and SCIPY_AVAILABLE:
            return gaussian_line_fit(wl_region, flux_region, line_wavelength)
        elif method == 'empirical':
            return empirical_line_fit(wl_region, flux_region, line_wavelength)
        else:  # method == 'auto'
            # Try Gaussian first if scipy available, else empirical
            if SCIPY_AVAILABLE:
                gaussian_result = gaussian_line_fit(wl_region, flux_region, line_wavelength)
                if gaussian_result:
                    return gaussian_result
            return empirical_line_fit(wl_region, flux_region, line_wavelength)
            
    except Exception as e:
        _LOGGER.warning(f"Line fitting failed: {e}")
        return None


def gaussian_line_fit(wl_region, flux_region, line_wavelength):
    """
    Perform Gaussian line fitting with comprehensive analysis.
    
    Args:
        wl_region: Wavelength array for fitting region
        flux_region: Flux array for fitting region  
        line_wavelength: Expected line center wavelength
    
    Returns:
        Dict with fit parameters and analysis results
    """
    try:
        from scipy.optimize import curve_fit
    except ImportError:
        return None
        
    # Define Gaussian function
    def gaussian(x, amplitude, center, sigma, continuum):
        return amplitude * np.exp(-((x - center)**2) / (2 * sigma**2)) + continuum
    
    # Initial parameter estimates
    peak_idx = np.argmax(flux_region)
    peak_flux = flux_region[peak_idx]
    peak_wl = wl_region[peak_idx]
    
    # Estimate continuum as median of edge regions
    edge_size = max(1, len(flux_region) // 10)
    continuum_est = np.median(np.concatenate([flux_region[:edge_size], flux_region[-edge_size:]]))
    
    amplitude_est = peak_flux - continuum_est
    sigma_est = 2.0  # Initial guess for width in Angstroms
    
    # Initial guess
    p0 = [amplitude_est, peak_wl, sigma_est, continuum_est]
    
    try:
        # Perform fit
        popt, pcov = curve_fit(gaussian, wl_region, flux_region, p0=p0, maxfev=1000)
        amplitude, center, sigma, continuum = popt
        
        # Calculate fit curve
        fit_wl = np.linspace(wl_region[0], wl_region[-1], 200)
        fit_flux = gaussian(fit_wl, *popt)
        
        # Calculate FWHM
        fwhm_ang = 2.355 * abs(sigma)  # 2.355 = 2*sqrt(2*ln(2))
        fwhm_vel = (fwhm_ang / center) * 299792.458  # km/s
        
        # Calculate R-squared
        ss_res = np.sum((flux_region - gaussian(wl_region, *popt)) ** 2)
        ss_tot = np.sum((flux_region - np.mean(flux_region)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Calculate parameter uncertainties
        param_errors = np.sqrt(np.diag(pcov)) if pcov is not None else [0, 0, 0, 0]
        
        analysis_text = f"Gaussian Fit Results:\n"
        analysis_text += f"Peak wavelength: {center:.2f} ± {param_errors[1]:.2f} Å\n"
        analysis_text += f"Peak flux: {amplitude + continuum:.3f}\n"
        analysis_text += f"FWHM: {fwhm_ang:.2f} Å ({fwhm_vel:.1f} km/s)\n"
        analysis_text += f"Continuum: {continuum:.3f} ± {param_errors[3]:.3f}\n"
        analysis_text += f"R-squared: {r_squared:.3f}\n"
        analysis_text += f"Amplitude: {amplitude:.3f} ± {param_errors[0]:.3f}\n"
        analysis_text += f"Sigma: {sigma:.2f} ± {param_errors[2]:.2f} Å\n"
        
        return {
            'method': 'gaussian',
            'parameters': popt,
            'parameter_errors': param_errors,
            'fit_wavelength': fit_wl,
            'fit_flux': fit_flux,
            'fwhm_ang': fwhm_ang,
            'fwhm_vel': fwhm_vel,
            'r_squared': r_squared,
            'center': center,
            'amplitude': amplitude,
            'sigma': sigma,
            'continuum': continuum,
            'analysis_text': analysis_text
        }
        
    except Exception as e:
        _LOGGER.warning(f"Gaussian fit failed: {e}")
        return None


def empirical_line_fit(wl_region, flux_region, line_wavelength):
    """
    Perform empirical FWHM measurement with visualization curve.
    
    Args:
        wl_region: Wavelength array for fitting region
        flux_region: Flux array for fitting region
        line_wavelength: Expected line center wavelength
    
    Returns:
        Dict with empirical analysis results
    """
    # Find peak
    peak_idx = np.argmax(flux_region)
    peak_flux = flux_region[peak_idx]
    peak_wl = wl_region[peak_idx]
    
    # Estimate continuum
    edge_size = max(1, len(flux_region) // 10)
    continuum = np.median(np.concatenate([flux_region[:edge_size], flux_region[-edge_size:]]))
    
    # FWHM measurement
    half_max = continuum + (peak_flux - continuum) / 2
    
    # Find half-maximum points
    left_idx = np.where(flux_region[:peak_idx] <= half_max)[0]
    right_idx = np.where(flux_region[peak_idx:] <= half_max)[0]
    
    if len(left_idx) > 0 and len(right_idx) > 0:
        left_wl = wl_region[left_idx[-1]]
        right_wl = wl_region[peak_idx + right_idx[0]]
        fwhm_ang = right_wl - left_wl
        
        # Improved interpolation for more accurate FWHM
        try:
            from scipy import interpolate
            
            # Interpolate to find more precise half-max crossings
            interp_func = interpolate.interp1d(wl_region, flux_region, kind='cubic', 
                                             bounds_error=False, fill_value='extrapolate')
            
            # Dense sampling around half-max regions
            left_region = np.linspace(left_wl - 2, left_wl + 2, 100)
            right_region = np.linspace(right_wl - 2, right_wl + 2, 100)
            
            left_flux_interp = interp_func(left_region)
            right_flux_interp = interp_func(right_region)
            
            # Find precise crossings
            left_crossing = left_region[np.argmin(np.abs(left_flux_interp - half_max))]
            right_crossing = right_region[np.argmin(np.abs(right_flux_interp - half_max))]
            
            fwhm_ang = right_crossing - left_crossing
            
        except ImportError:
            # Fallback to simple method if scipy not available
            pass
    else:
        # Estimate based on peak width
        fwhm_ang = (wl_region[-1] - wl_region[0]) / 4
        
    fwhm_vel = (fwhm_ang / peak_wl) * 299792.458  # km/s
    
    # Create visualization curve using Gaussian approximation
    fit_wl = np.linspace(wl_region[0], wl_region[-1], 200)
    sigma_approx = fwhm_ang / 2.355
    fit_flux = continuum + (peak_flux - continuum) * np.exp(-((fit_wl - peak_wl)**2) / (2 * sigma_approx**2))
    
    # Calculate equivalent width for emission lines
    delta_lambda = np.diff(wl_region)[0] if len(wl_region) > 1 else 1.0
    equivalent_width = np.sum((flux_region - continuum) * delta_lambda) / continuum
    
    analysis_text = f"Empirical Analysis Results:\n"
    analysis_text += f"Peak wavelength: {peak_wl:.2f} Å\n"
    analysis_text += f"Peak flux: {peak_flux:.3f}\n"
    analysis_text += f"FWHM: {fwhm_ang:.2f} Å ({fwhm_vel:.1f} km/s)\n"
    analysis_text += f"Continuum: {continuum:.3f}\n"
    analysis_text += f"Equivalent width: {equivalent_width:.2f} Å\n"
    analysis_text += f"Peak height above continuum: {peak_flux - continuum:.3f}\n"
    
    return {
        'method': 'empirical',
        'parameters': [peak_flux - continuum, peak_wl, sigma_approx, continuum],
        'fit_wavelength': fit_wl,
        'fit_flux': fit_flux,
        'fwhm_ang': fwhm_ang,
        'fwhm_vel': fwhm_vel,
        'center': peak_wl,
        'peak_flux': peak_flux,
        'continuum': continuum,
        'equivalent_width': equivalent_width,
        'analysis_text': analysis_text
    }
