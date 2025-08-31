"""
Legacy NIST utilities removed in new GUI.
This module is retained only to avoid import errors if referenced.
"""

import numpy as np

def search_nist_database(*args, **kwargs):
    return None

def compare_spectral_lines(obs_lines, tmpl_lines, velocity_threshold=200.0):
    """
    Compare observed and template spectral lines to find matches
    
    Args:
        obs_lines: List of observed line wavelengths
        tmpl_lines: List of template line wavelengths
        velocity_threshold: Maximum velocity difference for a match in km/s
        
    Returns:
        Dictionary with matches and unmatched lines
    """
    from .spectrum_utils import wavelength_to_velocity
    
    # Prepare result structure
    result = {
        'matches': [],  # (obs_idx, tmpl_idx, velocity_diff, match_type)
        'unmatched_obs': [],
        'unmatched_tmpl': [],
        'obs_table': {'wavelength': obs_lines},
        'tmpl_table': {'wavelength': tmpl_lines}
    }
    
    # Track which lines have been matched
    obs_matched = [False] * len(obs_lines)
    tmpl_matched = [False] * len(tmpl_lines)
    
    # Solid match threshold (lower velocity difference)
    solid_threshold = velocity_threshold / 2
    
    # Compare each observed line with each template line
    for i, obs_wl in enumerate(obs_lines):
        best_match = None
        min_vel_diff = float('inf')
        
        for j, tmpl_wl in enumerate(tmpl_lines):
            # Calculate velocity difference
            vel_diff = abs(wavelength_to_velocity(obs_wl, tmpl_wl))
            
            # If within threshold and better than previous match, update
            if vel_diff < velocity_threshold and vel_diff < min_vel_diff:
                min_vel_diff = vel_diff
                best_match = j
        
        # If a match was found, record it
        if best_match is not None:
            match_type = 'solid' if min_vel_diff <= solid_threshold else 'weak'
            result['matches'].append((i, best_match, min_vel_diff, match_type))
            obs_matched[i] = True
            tmpl_matched[best_match] = True
    
    # Record unmatched lines
    result['unmatched_obs'] = [i for i, matched in enumerate(obs_matched) if not matched]
    result['unmatched_tmpl'] = [i for i, matched in enumerate(tmpl_matched) if not matched]
    
    return result

def detect_lines(data, smoothing_window=3, noise_factor=1.5, use_smoothing=True):
    """
    Detect emission and absorption lines in spectrum data
    
    Args:
        data: Numpy array with wavelength and flux data
        smoothing_window: Window size for smoothing
        noise_factor: Factor to multiply noise estimate by for peak detection
        use_smoothing: Whether to apply smoothing
        
    Returns:
        Dictionary with detected lines
    """
    from scipy.signal import find_peaks, savgol_filter
    from .spectrum_utils import apply_moving_average
    
    # Extract wavelength and flux
    x = data[:, 0]
    y = data[:, 1]
    
    if use_smoothing:
        # Apply a Savitzky-Golay filter for smoothing
        y_smooth = savgol_filter(y, max(3, smoothing_window), 2)
    else:
        y_smooth = y
    
    # Baseline correction using polynomial fit
    def estimate_baseline(x, y, poly_order=5):
        coeffs = np.polyfit(x, y, poly_order)
        baseline = np.polyval(coeffs, x)
        return baseline
    
    baseline = estimate_baseline(x, y_smooth)
    y_norm = y_smooth - baseline
    
    # Estimate noise level from the normalized spectrum
    noise_level = np.std(y_norm) * noise_factor
    
    # Find emission peaks
    emission_peaks, _ = find_peaks(y_norm, height=noise_level, distance=smoothing_window)
    
    # Find absorption peaks (negative)
    absorption_peaks, _ = find_peaks(-y_norm, height=noise_level, distance=smoothing_window)
    
    # Collect results
    emission_lines = x[emission_peaks]
    absorption_lines = x[absorption_peaks]
    
    return {
        'emission': emission_lines,
        'absorption': absorption_lines,
        'all': np.concatenate([emission_lines, absorption_lines]),
        'emission_indices': emission_peaks,
        'absorption_indices': absorption_peaks,
        'normalized_flux': y_norm,
        'baseline': baseline
    }