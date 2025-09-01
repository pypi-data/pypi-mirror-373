"""
Line detection utilities for spectral analysis.
"""

from typing import List, Dict

import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.optimize import curve_fit


def gaussian_function(x: np.ndarray, amplitude: float, center: float, sigma: float) -> np.ndarray:
    return amplitude * np.exp(-((x - center) ** 2) / (2 * sigma ** 2))


def fit_gaussian_line(
    wavelength: np.ndarray,
    flux: np.ndarray,
    center_guess: float,
    amplitude_guess: float,
    sigma_guess: float = 2.0,
) -> Dict[str, float] | None:
    try:
        initial_guess = [amplitude_guess, center_guess, sigma_guess]

        amplitude_bounds = (0, amplitude_guess * 5)
        center_bounds = (center_guess - 5, center_guess + 5)
        sigma_bounds = (0.5, 8.0)

        bounds = (
            [amplitude_bounds[0], center_bounds[0], sigma_bounds[0]],
            [amplitude_bounds[1], center_bounds[1], sigma_bounds[1]],
        )

        popt, pcov = curve_fit(
            gaussian_function, wavelength, flux, p0=initial_guess, bounds=bounds, maxfev=1000
        )

        amplitude, center, sigma = popt
        param_errors = np.sqrt(np.diag(pcov))
        center_err = param_errors[1] if len(param_errors) > 1 else None

        return {
            "amplitude": float(amplitude),
            "center": float(center),
            "sigma": float(sigma),
            "center_error": float(center_err) if center_err is not None else None,
            "fwhm": float(sigma * 2.355),
        }
    except Exception:
        return None


def detect_and_fit_lines(
    wavelength: np.ndarray,
    flux: np.ndarray,
    min_width: int = 1,
    max_width: int = 10,
    min_snr: float = 2.0,
    max_fit_window: int = 20,
    smoothing_window: int = 5,
    use_smoothing: bool = True,
) -> List[Dict[str, float]]:
    """
    Detect spectral lines using scipy-based peak detection and Gaussian fitting.
    Returns a list of dictionaries with fields: wavelength, uncertainty, type,
    amplitude, sigma, and snr.
    """

    flux_mean = float(np.mean(flux))
    if abs(flux_mean) < 0.5:
        flux = flux + 1.0

    if use_smoothing and len(flux) > smoothing_window:
        if smoothing_window % 2 == 0:
            smoothing_window += 1
        flux_smooth = savgol_filter(flux, smoothing_window, 2)
    else:
        flux_smooth = flux.copy()

    flux_median = float(np.median(flux_smooth))
    noise_level = float(np.median(np.abs(flux_smooth - flux_median)) * 1.4826)
    noise_level = max(noise_level, 0.01 * float(np.max(np.abs(flux_smooth))))

    all_lines: List[Dict[str, float]] = []

    # Emission lines (positive peaks)
    try:
        peak_indices, _ = find_peaks(
            flux_smooth,
            height=noise_level * min_snr,
            distance=min_width,
            prominence=noise_level * min_snr * 0.5,
            width=min_width * 0.5,
        )

        for peak_idx in peak_indices:
            window_size = max(min_width * 2, 10)
            min_idx = max(0, int(peak_idx) - window_size)
            max_idx = min(len(wavelength) - 1, int(peak_idx) + window_size)
            if max_idx - min_idx < 5:
                continue

            peak_wl = wavelength[min_idx : max_idx + 1]
            peak_flux = flux_smooth[min_idx : max_idx + 1]

            baseline = float(np.percentile(peak_flux, 10))
            peak_flux_adj = peak_flux - baseline

            try:
                amp_guess = float(peak_flux_adj[int(peak_idx) - min_idx])
                cen_guess = float(wavelength[int(peak_idx)])
                sigma_guess = 2.0 / 2.355

                fit_result = fit_gaussian_line(peak_wl, peak_flux_adj, cen_guess, amp_guess, sigma_guess)
                if fit_result is not None:
                    amp = fit_result["amplitude"]
                    cen = fit_result["center"]
                    sigma = fit_result["sigma"]
                    cen_err = fit_result["center_error"]

                    if amp > noise_level * 0.8:
                        all_lines.append(
                            {
                                "wavelength": cen,
                                "uncertainty": cen_err,
                                "type": "emission",
                                "amplitude": amp,
                                "sigma": sigma,
                                "snr": amp / noise_level if noise_level > 0 else None,
                            }
                        )
            except Exception:
                all_lines.append(
                    {
                        "wavelength": float(wavelength[int(peak_idx)]),
                        "uncertainty": None,
                        "type": "emission",
                        "amplitude": float(flux_smooth[int(peak_idx)] - baseline),
                        "sigma": 2.0,
                        "snr": (float(flux_smooth[int(peak_idx)] - baseline) / noise_level) if noise_level > 0 else None,
                    }
                )
    except Exception:
        pass

    # Absorption lines (negative peaks)
    try:
        negative_flux = -flux_smooth
        trough_indices, _ = find_peaks(
            negative_flux,
            height=noise_level * min_snr,
            distance=min_width,
            prominence=noise_level * min_snr * 0.5,
            width=min_width * 0.5,
        )

        for trough_idx in trough_indices:
            window_size = max(min_width * 2, 10)
            min_idx = max(0, int(trough_idx) - window_size)
            max_idx = min(len(wavelength) - 1, int(trough_idx) + window_size)
            if max_idx - min_idx < 5:
                continue

            trough_wl = wavelength[min_idx : max_idx + 1]
            trough_flux = flux_smooth[min_idx : max_idx + 1]

            baseline = float(np.percentile(trough_flux, 90))
            trough_flux_adj = -(trough_flux - baseline)

            try:
                amp_guess = float(trough_flux_adj[int(trough_idx) - min_idx])
                cen_guess = float(wavelength[int(trough_idx)])
                sigma_guess = 2.0 / 2.355

                fit_result = fit_gaussian_line(trough_wl, trough_flux_adj, cen_guess, amp_guess, sigma_guess)
                if fit_result is not None:
                    amp = fit_result["amplitude"]
                    cen = fit_result["center"]
                    sigma = fit_result["sigma"]
                    cen_err = fit_result["center_error"]

                    if amp > noise_level * 0.8:
                        all_lines.append(
                            {
                                "wavelength": cen,
                                "uncertainty": cen_err,
                                "type": "absorption",
                                "amplitude": amp,
                                "sigma": sigma,
                                "snr": amp / noise_level if noise_level > 0 else None,
                            }
                        )
            except Exception:
                all_lines.append(
                    {
                        "wavelength": float(wavelength[int(trough_idx)]),
                        "uncertainty": None,
                        "type": "absorption",
                        "amplitude": float(negative_flux[int(trough_idx)] - baseline),
                        "sigma": 2.0,
                        "snr": (float(negative_flux[int(trough_idx)] - baseline) / noise_level) if noise_level > 0 else None,
                    }
                )
    except Exception:
        pass

    filtered_lines: List[Dict[str, float]] = []
    seen_wavelengths = set()
    sorted_lines = sorted(all_lines, key=lambda x: x.get("snr", 0) or 0, reverse=True)

    for line in sorted_lines:
        rounded_wave = round(float(line["wavelength"]) * 10) / 10
        if rounded_wave not in seen_wavelengths:
            seen_wavelengths.add(rounded_wave)
            filtered_lines.append(line)

    return sorted(filtered_lines, key=lambda x: x["wavelength"])  # type: ignore[arg-type]


