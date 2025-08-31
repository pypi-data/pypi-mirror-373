import numpy as np

try:
    from snid_sage.snid.preprocessing import fit_continuum
    SNID_AVAILABLE = True
except Exception:
    SNID_AVAILABLE = False


def fit_continuum_improved(flux: np.ndarray, method: str = "spline", **kwargs):
    """Improved continuum fitting with robust fallbacks."""
    if not SNID_AVAILABLE:
        try:
            from scipy.signal import savgol_filter as _sg
            n = len(flux)
            if n < 7:
                return np.zeros_like(flux), np.ones_like(flux)
            w = max(7, (n // 15) | 1)
            cont = _sg(np.maximum(flux, 0.0), w, 3)
        except Exception:
            k = max(5, len(flux) // 21)
            if k % 2 == 0:
                k += 1
            pad = k // 2
            padded = np.pad(np.maximum(flux, 0.0), (pad, pad), mode='edge')
            kernel = np.ones(k) / k
            cont = np.convolve(padded, kernel, mode='valid')
        flat = np.zeros_like(flux)
        mask = (flux > 0) & (cont > 0)
        flat[mask] = flux[mask] / cont[mask] - 1.0
        return flat, cont

    if method == "spline":
        knotnum = kwargs.get('knotnum', 13)
        flat_flux, continuum = fit_continuum(flux, method="spline", knotnum=knotnum)
        return flat_flux, continuum
    return np.zeros_like(flux), np.ones_like(flux)


def preview_continuum_fit(current_wave: np.ndarray, current_flux: np.ndarray, method: str = 'spline', **kwargs):
    if method != 'spline':
        return current_wave.copy(), current_flux.copy(), None
    knotnum = kwargs.get('knotnum', 13)
    flat_flux, continuum = fit_continuum_improved(current_flux, method='spline', knotnum=knotnum)
    return current_wave.copy(), flat_flux, continuum


def calculate_manual_continuum_preview(current_wave: np.ndarray, current_flux: np.ndarray, manual_continuum: np.ndarray):
    temp_wave = current_wave.copy()
    temp_flux = current_flux.copy()
    positive_mask = temp_flux > 0
    continuum_mask = manual_continuum > 0
    valid_mask = positive_mask & continuum_mask
    flat_flux = np.zeros_like(temp_flux)
    flat_flux[valid_mask] = (temp_flux[valid_mask] / manual_continuum[valid_mask]) - 1.0
    return temp_wave, flat_flux


def calculate_interactive_continuum_preview(current_wave, current_flux, continuum_points):
    if len(continuum_points) < 2:
        return current_wave.copy(), current_flux.copy()
    wave_points = np.array([p[0] for p in continuum_points])
    continuum_values = np.array([p[1] for p in continuum_points])
    continuum = np.interp(current_wave, wave_points, continuum_values)
    temp_flux = current_flux.copy()
    positive_mask = temp_flux > 0
    continuum_mask = continuum > 0
    valid_mask = positive_mask & continuum_mask
    flat_flux = np.zeros_like(temp_flux)
    flat_flux[valid_mask] = (temp_flux[valid_mask] / continuum[valid_mask]) - 1.0
    return current_wave.copy(), flat_flux, continuum


