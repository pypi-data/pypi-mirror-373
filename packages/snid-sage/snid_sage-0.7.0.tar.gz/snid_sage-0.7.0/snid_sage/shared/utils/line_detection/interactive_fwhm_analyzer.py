"""
SNID SAGE - Interactive FWHM Analysis
====================================

Enhanced FWHM analyzer with manual controls, flexible region selection,
and multiple fitting methods for challenging spectral features.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

try:
    from scipy.optimize import curve_fit
    from scipy import interpolate
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from snid_sage.shared.constants.physical import SPEED_OF_LIGHT_KMS
except ImportError:
    SPEED_OF_LIGHT_KMS = 299792.458

_LOGGER = logging.getLogger(__name__)


class InteractiveFWHMAnalyzer:
    """Enhanced FWHM analyzer with interactive capabilities"""
    
    def __init__(self):
        self.measurements = {}
        self.manual_regions = {}
        self.manual_points = {}
        self.manual_baselines = {}
        self.manual_peaks = {}
        
        self.fitting_methods = {
            'gaussian': self._fit_gaussian_enhanced,
            'lorentzian': self._fit_lorentzian,
            'empirical': self._fit_empirical_enhanced,
            'simple_width': self._fit_simple_width
        }
    
    def measure_fwhm_interactive(self, wavelength: np.ndarray, flux: np.ndarray, 
                                line_center: float, analysis_config: Dict) -> Dict[str, Any]:
        """Enhanced FWHM measurement with interactive controls"""
        try:
            # Step 1: Determine analysis region
            wave_region, flux_region, region_info = self._get_analysis_region(
                wavelength, flux, line_center, analysis_config)
            
            if len(wave_region) < analysis_config.get('min_points', 3):
                return {
                    'error': f'Insufficient data points: {len(wave_region)} < {analysis_config.get("min_points", 3)}',
                    'region_info': region_info
                }
            
            # Step 2: Apply manual point selection if specified
            if analysis_config.get('use_manual_points', False):
                wave_region, flux_region = self._apply_manual_point_selection(
                    wave_region, flux_region, line_center, analysis_config)
            
            # Step 3: Handle baseline
            baseline_corrected_flux = self._handle_baseline(
                wave_region, flux_region, analysis_config)
            
            # Step 4: Multiple fitting attempts with fallbacks
            result = self._fit_with_fallbacks(
                wave_region, baseline_corrected_flux, line_center, analysis_config)
            
            # Step 5: Add metadata
            result.update({
                'region_info': region_info,
                'analysis_config': analysis_config,
                'n_points_used': len(wave_region),
                'wavelength_range': (wave_region[0], wave_region[-1])
            })
            
            return result
            
        except Exception as e:
            _LOGGER.error(f"Error in interactive FWHM measurement: {e}")
            return {'error': str(e)}
    
    def _get_analysis_region(self, wavelength: np.ndarray, flux: np.ndarray, 
                           line_center: float, config: Dict) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Determine the analysis region using various methods"""
        
        region_info = {'method': 'unknown', 'original_range': None, 'final_range': None}
        
        if config.get('use_manual_region', False) and line_center in self.manual_regions:
            # Use manually defined region
            start_wave, end_wave = self.manual_regions[line_center]
            mask = (wavelength >= start_wave) & (wavelength <= end_wave)
            region_info['method'] = 'manual_region'
            region_info['manual_range'] = (start_wave, end_wave)
            
        elif config.get('adaptive_region', True):
            # Adaptive region sizing based on spectrum characteristics
            mask = self._get_adaptive_region_mask(wavelength, flux, line_center)
            region_info['method'] = 'adaptive'
            
        else:
            # Fixed region (fallback to original method)
            window_width = config.get('window_width', 40.0)  # Increased default
            mask = (wavelength >= line_center - window_width/2) & (wavelength <= line_center + window_width/2)
            region_info['method'] = 'fixed'
            region_info['window_width'] = window_width
        
        wave_region = wavelength[mask]
        flux_region = flux[mask]
        
        if len(wave_region) > 0:
            region_info['original_range'] = (wave_region[0], wave_region[-1])
            region_info['n_points'] = len(wave_region)
        
        # Auto-expand if insufficient points
        if len(wave_region) < config.get('min_points', 5):
            wave_region, flux_region = self._expand_region_automatically(
                wavelength, flux, line_center, config)
            if len(wave_region) > 0:
                region_info['expanded'] = True
                region_info['final_range'] = (wave_region[0], wave_region[-1])
        
        return wave_region, flux_region, region_info
    
    def _get_adaptive_region_mask(self, wavelength: np.ndarray, flux: np.ndarray, 
                                line_center: float) -> np.ndarray:
        """Create adaptive region mask based on spectrum characteristics"""
        
        # Start with a small region around the line
        base_width = 10.0  # Angstroms
        mask = (wavelength >= line_center - base_width) & (wavelength <= line_center + base_width)
        
        if np.sum(mask) < 5:
            # Expand if we don't have enough points
            base_width = 20.0
            mask = (wavelength >= line_center - base_width) & (wavelength <= line_center + base_width)
        
        return mask
    
    def _expand_region_automatically(self, wavelength: np.ndarray, flux: np.ndarray, 
                                   line_center: float, config: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Automatically expand region to get more data points"""
        
        # Progressive expansion
        expansions = [30.0, 50.0, 80.0, 100.0]  # Angstrom widths to try
        min_points = config.get('min_points', 5)
        
        for width in expansions:
            mask = (wavelength >= line_center - width/2) & (wavelength <= line_center + width/2)
            if np.sum(mask) >= min_points:
                return wavelength[mask], flux[mask]
        
        # Last resort: take all available data around the line
        center_idx = np.argmin(np.abs(wavelength - line_center))
        start_idx = max(0, center_idx - 100)
        end_idx = min(len(wavelength), center_idx + 100)
        
        return wavelength[start_idx:end_idx], flux[start_idx:end_idx]
    
    def _apply_manual_point_selection(self, wavelength: np.ndarray, flux: np.ndarray,
                                    line_center: float, config: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Apply manual point selection if available"""
        
        if line_center not in self.manual_points:
            return wavelength, flux
        
        selected_indices = self.manual_points[line_center]
        
        # Convert global indices to local indices within the current region
        local_indices = []
        for global_idx in selected_indices:
            # Find closest match in current wavelength array
            local_idx = np.argmin(np.abs(wavelength - global_idx))
            if local_idx not in local_indices:
                local_indices.append(local_idx)
        
        if local_indices:
            local_indices = sorted(local_indices)
            return wavelength[local_indices], flux[local_indices]
        
        return wavelength, flux
    
    def _handle_baseline(self, wavelength: np.ndarray, flux: np.ndarray, 
                        config: Dict) -> np.ndarray:
        """Handle baseline correction"""
        
        baseline_method = config.get('baseline_method', 'edges')
        
        if baseline_method == 'edges':
            # Use edge points to estimate baseline
            n_edge_points = min(3, len(flux) // 4)
            if n_edge_points > 0:
                left_baseline = np.median(flux[:n_edge_points])
                right_baseline = np.median(flux[-n_edge_points:])
                baseline = np.linspace(left_baseline, right_baseline, len(flux))
                return flux - baseline
        
        # Return original flux if baseline correction fails
        return flux
    
    def _fit_with_fallbacks(self, wavelength: np.ndarray, flux: np.ndarray, 
                          line_center: float, config: Dict) -> Dict[str, Any]:
        """Try multiple fitting methods with fallbacks"""
        
        primary_method = config.get('method', 'gaussian')
        fallback_methods = config.get('fallback_methods', ['empirical', 'simple_width'])
        
        # Try primary method first
        result = self._try_single_method(wavelength, flux, line_center, primary_method, config)
        if 'error' not in result:
            result['fitting_method'] = primary_method
            result['used_fallback'] = False
            return result
        
        # Try fallback methods
        for method in fallback_methods:
            if method != primary_method:
                result = self._try_single_method(wavelength, flux, line_center, method, config)
                if 'error' not in result:
                    result['fitting_method'] = method
                    result['used_fallback'] = True
                    return result
        
        # All methods failed
        return {
            'error': 'All fitting methods failed',
            'attempted_methods': [primary_method] + fallback_methods,
            'fitting_method': 'none'
        }
    
    def _try_single_method(self, wavelength: np.ndarray, flux: np.ndarray, 
                          line_center: float, method: str, config: Dict) -> Dict[str, Any]:
        """Try a single fitting method"""
        
        if method in self.fitting_methods:
            try:
                return self.fitting_methods[method](wavelength, flux, line_center, config)
            except Exception as e:
                return {'error': f'{method} fitting failed: {str(e)}'}
        else:
            return {'error': f'Unknown fitting method: {method}'}
    
    def _fit_gaussian_enhanced(self, wavelength: np.ndarray, flux: np.ndarray, 
                             line_center: float, config: Dict) -> Dict[str, Any]:
        """Enhanced Gaussian fitting with better initial guesses"""
        
        if not SCIPY_AVAILABLE:
            return {'error': 'SciPy not available for Gaussian fitting'}
        
        try:
            # Define Gaussian function
            def gaussian(x, amplitude, center, sigma, baseline):
                return baseline + amplitude * np.exp(-((x - center) / sigma) ** 2 / 2)
            
            # Better initial parameter estimation
            baseline = np.median([flux[0], flux[-1]]) if len(flux) > 2 else np.median(flux)
            
            # Detect if line is emission or absorption
            center_idx = np.argmin(np.abs(wavelength - line_center))
            line_flux = flux[center_idx] if center_idx < len(flux) else np.mean(flux)
            
            is_emission = line_flux > baseline
            
            if is_emission:
                amplitude = np.max(flux) - baseline
                peak_idx = np.argmax(flux)
            else:
                amplitude = np.min(flux) - baseline
                peak_idx = np.argmin(flux)
            
            # Better center estimate
            center = wavelength[peak_idx] if peak_idx < len(wavelength) else line_center
            
            # Better sigma estimate from data width
            sigma = (wavelength[-1] - wavelength[0]) / 6  # Start with 1/6 of total width
            
            # Fit with bounds to prevent unreasonable parameters
            bounds = (
                [-np.inf, wavelength[0], 0.1, -np.inf],  # Lower bounds
                [np.inf, wavelength[-1], (wavelength[-1] - wavelength[0]), np.inf]   # Upper bounds
            )
            
            popt, pcov = curve_fit(
                gaussian, wavelength, flux, 
                p0=[amplitude, center, sigma, baseline],
                bounds=bounds,
                maxfev=2000
            )
            
            amplitude_fit, center_fit, sigma_fit, baseline_fit = popt
            
            # Calculate FWHM in Angstroms
            fwhm_angstrom = 2.355 * abs(sigma_fit)
            
            # Convert to velocity (km/s)
            fwhm_velocity = (fwhm_angstrom / center_fit) * SPEED_OF_LIGHT_KMS
            
            # Peak velocity offset from rest wavelength
            peak_velocity = ((center_fit - line_center) / line_center) * SPEED_OF_LIGHT_KMS
            
            # Calculate fit quality metrics
            fitted_flux = gaussian(wavelength, *popt)
            residuals = flux - fitted_flux
            
            # R-squared
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((flux - np.mean(flux)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                'fwhm_angstrom': fwhm_angstrom,
                'fwhm_velocity': fwhm_velocity,
                'peak_velocity': peak_velocity,
                'fitted_center': center_fit,
                'fitted_amplitude': amplitude_fit,
                'fitted_sigma': sigma_fit,
                'baseline': baseline_fit,
                'fit_quality': r_squared,
                'fitted_flux': fitted_flux,
                'residuals': residuals,
                'method': 'gaussian_enhanced'
            }
            
        except Exception as e:
            return {'error': f'Enhanced Gaussian fitting failed: {e}'}
    
    def _fit_lorentzian(self, wavelength: np.ndarray, flux: np.ndarray, 
                       line_center: float, config: Dict) -> Dict[str, Any]:
        """Lorentzian profile fitting"""
        
        return {'error': 'Lorentzian fitting not yet implemented'}
    
    def _fit_empirical_enhanced(self, wavelength: np.ndarray, flux: np.ndarray, 
                               line_center: float, config: Dict) -> Dict[str, Any]:
        """Enhanced empirical FWHM measurement"""
        
        try:
            # Find peak and baseline
            baseline = np.median([flux[0], flux[-1]]) if len(flux) > 2 else np.median(flux)
            
            # Determine if emission or absorption
            center_idx = np.argmin(np.abs(wavelength - line_center))
            line_flux = flux[center_idx] if center_idx < len(flux) else np.mean(flux)
            is_emission = line_flux > baseline
            
            if is_emission:
                peak_flux = np.max(flux)
                peak_idx = np.argmax(flux)
            else:
                peak_flux = np.min(flux)
                peak_idx = np.argmin(flux)
            
            # Half maximum level
            half_max = baseline + (peak_flux - baseline) / 2
            
            # Find crossings using interpolation
            if len(flux) < 3:
                return {'error': 'Insufficient points for empirical FWHM'}
            
            # Create high-resolution interpolation if possible
            if SCIPY_AVAILABLE and len(wavelength) > 3:
                interp_func = interpolate.interp1d(wavelength, flux, kind='linear', 
                                                 bounds_error=False, fill_value='extrapolate')
                
                # High-resolution wavelength array
                wave_hr = np.linspace(wavelength[0], wavelength[-1], len(wavelength) * 10)
                flux_hr = interp_func(wave_hr)
                
                # Find crossings
                crossings = []
                for i in range(len(flux_hr) - 1):
                    if ((flux_hr[i] <= half_max <= flux_hr[i+1]) or 
                        (flux_hr[i] >= half_max >= flux_hr[i+1])):
                        # Linear interpolation to find exact crossing
                        alpha = (half_max - flux_hr[i]) / (flux_hr[i+1] - flux_hr[i])
                        crossing_wave = wave_hr[i] + alpha * (wave_hr[i+1] - wave_hr[i])
                        crossings.append(crossing_wave)
                
                if len(crossings) >= 2:
                    crossings = sorted(crossings)
                    fwhm_angstrom = crossings[-1] - crossings[0]
                else:
                    # Fallback method
                    above_half = flux >= half_max if is_emission else flux <= half_max
                    
                    if not np.any(above_half):
                        return {'error': 'No points at half maximum'}
                    
                    indices = np.where(above_half)[0]
                    if len(indices) < 2:
                        return {'error': 'Insufficient points at half maximum'}
                    
                    fwhm_angstrom = wavelength[indices[-1]] - wavelength[indices[0]]
            else:
                # Simple method without interpolation
                above_half = flux >= half_max if is_emission else flux <= half_max
                
                if not np.any(above_half):
                    return {'error': 'No points at half maximum'}
                
                indices = np.where(above_half)[0]
                if len(indices) < 2:
                    return {'error': 'Insufficient points at half maximum'}
                
                fwhm_angstrom = wavelength[indices[-1]] - wavelength[indices[0]]
            
            # Convert to velocity
            peak_wavelength = wavelength[peak_idx]
            fwhm_velocity = (fwhm_angstrom / peak_wavelength) * SPEED_OF_LIGHT_KMS
            peak_velocity = ((peak_wavelength - line_center) / line_center) * SPEED_OF_LIGHT_KMS
            
            return {
                'fwhm_angstrom': fwhm_angstrom,
                'fwhm_velocity': fwhm_velocity,
                'peak_velocity': peak_velocity,
                'peak_wavelength': peak_wavelength,
                'half_max_level': half_max,
                'method': 'empirical_enhanced'
            }
            
        except Exception as e:
            return {'error': f'Enhanced empirical FWHM failed: {e}'}
    
    def _fit_simple_width(self, wavelength: np.ndarray, flux: np.ndarray, 
                         line_center: float, config: Dict) -> Dict[str, Any]:
        """Simple width measurement as last resort"""
        
        try:
            # Very basic width measurement
            baseline = np.median([flux[0], flux[-1]]) if len(flux) > 2 else np.median(flux)
            
            # Find peak
            center_idx = np.argmin(np.abs(wavelength - line_center))
            line_flux = flux[center_idx] if center_idx < len(flux) else np.mean(flux)
            is_emission = line_flux > baseline
            
            if is_emission:
                peak_flux = np.max(flux)
                peak_idx = np.argmax(flux)
            else:
                peak_flux = np.min(flux)
                peak_idx = np.argmin(flux)
            
            # Find 20% and 80% levels (crude FWHM approximation)
            level_20 = baseline + 0.2 * (peak_flux - baseline)
            level_80 = baseline + 0.8 * (peak_flux - baseline)
            
            above_20 = flux >= level_20 if is_emission else flux <= level_20
            above_80 = flux >= level_80 if is_emission else flux <= level_80
            
            if np.any(above_20) and np.any(above_80):
                indices_20 = np.where(above_20)[0]
                indices_80 = np.where(above_80)[0]
                
                width_20 = wavelength[indices_20[-1]] - wavelength[indices_20[0]]
                width_80 = wavelength[indices_80[-1]] - wavelength[indices_80[0]]
                
                # Crude FWHM estimate
                fwhm_angstrom = (width_20 + width_80) / 2
            else:
                # Last resort: total width
                fwhm_angstrom = wavelength[-1] - wavelength[0]
            
            peak_wavelength = wavelength[peak_idx]
            fwhm_velocity = (fwhm_angstrom / peak_wavelength) * SPEED_OF_LIGHT_KMS
            peak_velocity = ((peak_wavelength - line_center) / line_center) * SPEED_OF_LIGHT_KMS
            
            return {
                'fwhm_angstrom': fwhm_angstrom,
                'fwhm_velocity': fwhm_velocity,
                'peak_velocity': peak_velocity,
                'peak_wavelength': peak_wavelength,
                'method': 'simple_width',
                'warning': 'Used simple width measurement - results may be inaccurate'
            }
            
        except Exception as e:
            return {'error': f'Simple width measurement failed: {e}'}
    
    # Manual selection management methods
    def set_manual_region(self, line_center: float, start_wave: float, end_wave: float):
        """Set manual analysis region for a line"""
        self.manual_regions[line_center] = (start_wave, end_wave)
    
    def set_manual_points(self, line_center: float, selected_indices: List[int]):
        """Set manually selected points for a line"""
        self.manual_points[line_center] = selected_indices
    
    def clear_manual_selections(self, line_center: Optional[float] = None):
        """Clear manual selections for a line or all lines"""
        if line_center is not None:
            self.manual_regions.pop(line_center, None)
            self.manual_points.pop(line_center, None)
            self.manual_baselines.pop(line_center, None)
            self.manual_peaks.pop(line_center, None)
        else:
            self.manual_regions.clear()
            self.manual_points.clear()
            self.manual_baselines.clear()
            self.manual_peaks.clear() 