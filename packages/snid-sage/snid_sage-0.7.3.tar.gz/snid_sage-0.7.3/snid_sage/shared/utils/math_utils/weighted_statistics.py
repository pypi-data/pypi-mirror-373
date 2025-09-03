"""
Statistically rigorous weighted calculations for redshift and age estimation in SNID SAGE.

This module implements RLAP-Cos weighted estimation methods for optimal redshift 
and age estimation with full covariance analysis.
"""

import numpy as np
from typing import Union, List, Tuple, Optional
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


def calculate_combined_weights(
    rlap_cos_values: Union[np.ndarray, List[float]],
    uncertainties: Union[np.ndarray, List[float]]
) -> np.ndarray:
    """
    Calculate combined weights using both RLAP-Cos quality and individual uncertainties.
    
    This implements the statistically correct approach for weighted averaging when
    both quality indicators (RLAP-Cos) and individual uncertainties are available.
    
    Parameters
    ----------
    rlap_cos_values : array-like
        RLAP-Cos quality scores for each template
    uncertainties : array-like
        Individual uncertainty estimates for each template (e.g., redshift errors)
        
    Returns
    -------
    np.ndarray
        Combined weights = exp(rlap_cos) / σ²
        
    Notes
    -----
    Statistical Formulation:
    - Quality weight: q_i = exp(rlap_cos_i) 
    - Precision weight: p_i = 1/σ²_i
    - Combined weight: w_i = q_i × p_i = exp(rlap_cos_i) / σ²_i
    
    This gives high-quality templates with low uncertainty the highest influence,
    which is statistically optimal for uncertainty propagation.
    """
    rlap_cos_values = np.asarray(rlap_cos_values, dtype=float)
    uncertainties = np.asarray(uncertainties, dtype=float)
    
    # Validate inputs
    if len(rlap_cos_values) != len(uncertainties):
        raise ValueError("RLAP-Cos values and uncertainties must have same length")
    
    if len(rlap_cos_values) == 0:
        return np.array([])
    
    # Handle zero uncertainties (perfect measurements) by using a small floor value
    # This prevents infinite weights while preserving the relative ordering
    min_uncertainty = np.min(uncertainties[uncertainties > 0]) if np.any(uncertainties > 0) else 1e-6
    uncertainty_floor = min_uncertainty * 0.1
    safe_uncertainties = np.maximum(uncertainties, uncertainty_floor)
    
    # Calculate combined weights
    quality_weights = np.exp(rlap_cos_values)  # Exponential quality weighting
    precision_weights = 1.0 / (safe_uncertainties ** 2)  # Inverse variance weighting
    combined_weights = quality_weights * precision_weights
    
    logger.debug(f"Combined weighting: RLAP-Cos [{rlap_cos_values.min():.2f}, {rlap_cos_values.max():.2f}], "
                f"uncertainties [{uncertainties.min():.4f}, {uncertainties.max():.4f}], "
                f"weights [{combined_weights.min():.2e}, {combined_weights.max():.2e}]")
    
    return combined_weights


def apply_exponential_weighting(rlap_cos_values: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Apply exponential weighting to RLAP-Cos values for enhanced template prioritization.
    
    Based on analysis of different weighting functions, exponential weighting provides
    optimal balance between template quality discrimination and statistical robustness.
    
    Parameters
    ----------
    rlap_cos_values : array-like
        Raw RLAP-Cos values from template matching
        
    Returns
    -------
    np.ndarray
        Exponentially weighted values
        
    Notes
    -----
    Transformation: w_exp = exp(rlap_cos)
    
    This gives higher-quality templates exponentially more influence while
    maintaining the relative ordering and statistical properties needed for
    robust weighted estimation.
    """
    rlap_cos_values = np.asarray(rlap_cos_values, dtype=float)
    
    # Handle empty input
    if len(rlap_cos_values) == 0:
        return np.array([])
    
    # Apply exponential weighting
    # Use base e (natural exponential) as determined by analysis
    exponential_weights = np.exp(rlap_cos_values)
    
    # Log the transformation for debugging
    if len(rlap_cos_values) > 0:
        logger.debug(f"Exponential weighting: RLAP-Cos range [{rlap_cos_values.min():.2f}, {rlap_cos_values.max():.2f}] "
                    f"→ weight range [{exponential_weights.min():.2e}, {exponential_weights.max():.2e}]")
    
    return exponential_weights


def calculate_weighted_redshift_balanced(
    redshifts: Union[np.ndarray, List[float]], 
    redshift_errors: Union[np.ndarray, List[float]],
    rlap_cos_values: Union[np.ndarray, List[float]]
) -> Tuple[float, float]:
    """
    Calculate weighted redshift estimate with balanced uncertainty propagation.
    
    This function implements a statistically sound approach that balances:
    1. Template quality weighting (exponential RLAP-Cos)
    2. Precision weighting (inverse variance) 
    3. Proper uncertainty propagation
    
    Parameters
    ----------
    redshifts : array-like
        Redshift values from templates
    redshift_errors : array-like
        Individual redshift uncertainties for each template
    rlap_cos_values : array-like
        RLAP-Cos quality scores for each template
        
    Returns
    -------
    Tuple[float, float]
        (weighted_redshift, final_uncertainty)
        
    Notes
    -----
    Statistical Method:
    - Combined weights: w_i = exp(rlap_cos_i) / σ²_i
    - Weighted mean: z = Σ(w_i * z_i) / Σ(w_i)  
    - Final uncertainty: σ_final = √(Σ(w_i * σ_i²)) / Σ(w_i)
    
    This gives high-quality templates with low uncertainty the highest influence
    while properly propagating uncertainties using weighted RMS.
    """
    redshifts = np.asarray(redshifts, dtype=float)
    redshift_errors = np.asarray(redshift_errors, dtype=float)
    rlap_cos_values = np.asarray(rlap_cos_values, dtype=float)
    
    # Validate inputs
    if len(redshifts) == 0:
        return np.nan, np.nan
        
    if not (len(redshifts) == len(redshift_errors) == len(rlap_cos_values)):
        logger.error("Mismatched input lengths for balanced redshift estimation")
        return np.nan, np.nan
    
    # Remove invalid data points
    valid_mask = (np.isfinite(redshifts) & np.isfinite(redshift_errors) & 
                  np.isfinite(rlap_cos_values) & (redshift_errors > 0))
    
    if not np.any(valid_mask):
        logger.warning("No valid (redshift, error, rlap_cos) triplets found")
        return np.nan, np.nan
        
    valid_z = redshifts[valid_mask]
    valid_sigma = redshift_errors[valid_mask]
    valid_rlap = rlap_cos_values[valid_mask]
    N = len(valid_z)
    
    if N == 1:
        return float(valid_z[0]), float(valid_sigma[0])
    
    # Calculate combined weights (quality × precision)
    combined_weights = calculate_combined_weights(valid_rlap, valid_sigma)
    
    # Weighted mean
    sum_w = np.sum(combined_weights)
    z_weighted = np.sum(combined_weights * valid_z) / sum_w
    
    # Final uncertainty using weighted RMS
    weighted_var = np.sum(combined_weights * valid_sigma**2) / sum_w
    sigma_final = np.sqrt(weighted_var)
    
    logger.info(f"Balanced redshift: {z_weighted:.6f}±{sigma_final:.6f}, N={N}")
    
    return float(z_weighted), float(sigma_final)


def calculate_weighted_age_estimate(
    ages: Union[np.ndarray, List[float]],
    rlap_cos_values: Union[np.ndarray, List[float]]
) -> float:
    """
    Calculate weighted age estimate using exponential RLAP-Cos weighting.
    
    Ages typically don't have well-defined individual uncertainties, so this
    function uses simple exponential quality weighting without uncertainty propagation.
    
    Parameters
    ----------
    ages : array-like
        Age values from templates (in days)
    rlap_cos_values : array-like
        RLAP-Cos quality scores for each template
        
    Returns
    -------
    float
        Weighted age estimate
        
    Notes
    -----
    Statistical Method:
    - Weights: w_i = exp(rlap_cos_i)
    - Weighted mean: age = Σ(w_i * age_i) / Σ(w_i)
    
    No uncertainty is computed since individual age uncertainties are 
    typically not available or well-defined in template libraries.
    """
    ages = np.asarray(ages, dtype=float)
    rlap_cos_values = np.asarray(rlap_cos_values, dtype=float)
    
    # Validate inputs
    if len(ages) == 0:
        return np.nan
        
    if len(ages) != len(rlap_cos_values):
        logger.error("Mismatched input lengths for age estimation")
        return np.nan
    
    # Remove invalid data points
    # Note: Ages can be negative (before peak), so no age > 0 filter
    valid_mask = (np.isfinite(ages) & np.isfinite(rlap_cos_values))
    
    if not np.any(valid_mask):
        logger.warning("No valid (age, rlap_cos) pairs found")
        return np.nan
        
    valid_ages = ages[valid_mask]
    valid_rlap = rlap_cos_values[valid_mask]
    N = len(valid_ages)
    
    if N == 1:
        return float(valid_ages[0])
    
    # Calculate exponential weights
    weights = apply_exponential_weighting(valid_rlap)
    
    # Weighted mean
    sum_w = np.sum(weights)
    age_weighted = np.sum(weights * valid_ages) / sum_w
    
    logger.info(f"Weighted age: {age_weighted:.1f} days, N={N}")
    
    return float(age_weighted)


def calculate_uncertainty_aware_estimates(
    redshifts: Union[np.ndarray, List[float]], 
    redshift_errors: Union[np.ndarray, List[float]],
    rlap_cos_values: Union[np.ndarray, List[float]]
) -> Tuple[float, float]:
    """
    Calculate weighted redshift estimate with proper uncertainty propagation.
    
    This function implements the statistically correct approach for combining
    measurements with individual uncertainties and quality weights.
    
    Parameters
    ----------
    redshifts : array-like
        Redshift values from templates
    redshift_errors : array-like
        Individual redshift uncertainties for each template
    rlap_cos_values : array-like
        RLAP-Cos quality scores for each template
        
    Returns
    -------
    Tuple[float, float]
        (weighted_redshift, final_uncertainty)
        
    Notes
    -----
    Statistical Method (Inverse Variance Weighting with Quality):
    - Combined weights: w_i = exp(rlap_cos_i) / σ²_i
    - Weighted mean: z = Σ(w_i * z_i) / Σ(w_i)  
    - Final uncertainty: σ_final = 1 / √(Σ(w_i))
    
    This properly propagates individual template uncertainties while 
    prioritizing high-quality templates exponentially.
    """
    redshifts = np.asarray(redshifts, dtype=float)
    redshift_errors = np.asarray(redshift_errors, dtype=float)
    rlap_cos_values = np.asarray(rlap_cos_values, dtype=float)
    
    # Validate inputs
    if len(redshifts) == 0:
        return np.nan, np.nan
        
    if not (len(redshifts) == len(redshift_errors) == len(rlap_cos_values)):
        logger.error("Mismatched input lengths for uncertainty-aware estimation")
        return np.nan, np.nan
    
    # Remove invalid data points
    valid_mask = (np.isfinite(redshifts) & np.isfinite(redshift_errors) & 
                  np.isfinite(rlap_cos_values) & (redshift_errors > 0))
    
    if not np.any(valid_mask):
        logger.warning("No valid (redshift, error, rlap_cos) triplets found")
        return np.nan, np.nan
        
    valid_z = redshifts[valid_mask]
    valid_sigma = redshift_errors[valid_mask]
    valid_rlap = rlap_cos_values[valid_mask]
    N = len(valid_z)
    
    if N == 1:
        return float(valid_z[0]), float(valid_sigma[0])
    
    # Calculate combined weights (quality × precision)
    combined_weights = calculate_combined_weights(valid_rlap, valid_sigma)
    
    # Weighted mean
    sum_w = np.sum(combined_weights)
    z_weighted = np.sum(combined_weights * valid_z) / sum_w
    
    # Final uncertainty (inverse variance formula)
    sigma_final = 1.0 / np.sqrt(sum_w)
    
    logger.info(f"Uncertainty-aware redshift: {z_weighted:.6f}±{sigma_final:.6f}, N={N}")
    
    return float(z_weighted), float(sigma_final)


def calculate_joint_uncertainty_aware_estimates(
    redshifts: Union[np.ndarray, List[float]], 
    redshift_errors: Union[np.ndarray, List[float]],
    ages: Union[np.ndarray, List[float]],
    age_errors: Union[np.ndarray, List[float]],
    rlap_cos_values: Union[np.ndarray, List[float]]
) -> Tuple[float, float, float, float, float]:
    """
    Calculate joint weighted estimates for redshift and age with proper uncertainty propagation.
    
    This function implements the statistically correct approach for combining
    measurements with individual uncertainties and quality weights for both
    redshift and age simultaneously.
    
    Parameters
    ----------
    redshifts : array-like
        Redshift values from templates
    redshift_errors : array-like
        Individual redshift uncertainties for each template
    ages : array-like
        Age values from templates (in days)
    age_errors : array-like
        Individual age uncertainties for each template
    rlap_cos_values : array-like
        RLAP-Cos quality scores for each template
        
    Returns
    -------
    Tuple[float, float, float, float, float]
        (weighted_redshift, weighted_age, redshift_uncertainty, age_uncertainty, covariance)
        
    Notes
    -----
    Statistical Method:
    For simplicity, this uses separate inverse variance weighting for each parameter.
    The covariance is estimated from the scatter in the weighted residuals.
    
    Future Enhancement: Could implement full 2D inverse covariance weighting
    if template covariances between redshift and age become available.
    """
    # Convert to arrays
    redshifts = np.asarray(redshifts, dtype=float)
    redshift_errors = np.asarray(redshift_errors, dtype=float)
    ages = np.asarray(ages, dtype=float)
    age_errors = np.asarray(age_errors, dtype=float)
    rlap_cos_values = np.asarray(rlap_cos_values, dtype=float)
    
    # Validate inputs
    if len(redshifts) == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan
        
    lengths = [len(redshifts), len(redshift_errors), len(ages), len(age_errors), len(rlap_cos_values)]
    if not all(l == lengths[0] for l in lengths):
        logger.error("Mismatched input lengths for joint uncertainty-aware estimation")
        return np.nan, np.nan, np.nan, np.nan, np.nan
    
    # Remove invalid data points (need valid data for both redshift and age)
    valid_mask = (np.isfinite(redshifts) & np.isfinite(redshift_errors) & 
                  np.isfinite(ages) & np.isfinite(age_errors) &
                  np.isfinite(rlap_cos_values) & 
                  (redshift_errors > 0) & (age_errors > 0))
    
    if not np.any(valid_mask):
        logger.warning("No valid (redshift, age, errors, rlap_cos) quintuplets found")
        return np.nan, np.nan, np.nan, np.nan, np.nan
        
    valid_z = redshifts[valid_mask]
    valid_z_err = redshift_errors[valid_mask]
    valid_t = ages[valid_mask]
    valid_t_err = age_errors[valid_mask]
    valid_rlap = rlap_cos_values[valid_mask]
    N = len(valid_z)
    
    if N == 1:
        return float(valid_z[0]), float(valid_t[0]), float(valid_z_err[0]), float(valid_t_err[0]), 0.0
    
    # Calculate separate combined weights for redshift and age
    z_weights = calculate_combined_weights(valid_rlap, valid_z_err)
    t_weights = calculate_combined_weights(valid_rlap, valid_t_err)
    
    # Weighted means
    z_weighted = np.sum(z_weights * valid_z) / np.sum(z_weights)
    t_weighted = np.sum(t_weights * valid_t) / np.sum(t_weights)
    
    # Final uncertainties (inverse variance formula)
    z_uncertainty = 1.0 / np.sqrt(np.sum(z_weights))
    t_uncertainty = 1.0 / np.sqrt(np.sum(t_weights))
    
    # Estimate covariance from weighted residuals
    # This is approximate - proper implementation would need template covariances
    z_residuals = valid_z - z_weighted
    t_residuals = valid_t - t_weighted
    # Use geometric mean of weights for covariance estimation
    cov_weights = np.sqrt(z_weights * t_weights)
    covariance = np.sum(cov_weights * z_residuals * t_residuals) / np.sum(cov_weights) if np.sum(cov_weights) > 0 else 0.0
    
    logger.info(f"Joint uncertainty-aware estimates: "
                f"z={z_weighted:.6f}±{z_uncertainty:.6f}, age={t_weighted:.1f}±{t_uncertainty:.1f} days, "
                f"cov={covariance:.8f}, N={N}")
    
    return float(z_weighted), float(t_weighted), float(z_uncertainty), float(t_uncertainty), float(covariance)


def calculate_joint_weighted_estimates(
    redshifts: Union[np.ndarray, List[float]], 
    ages: Union[np.ndarray, List[float]],
    weights: Union[np.ndarray, List[float]]
) -> Tuple[float, float, float, float, float]:
    """
    Calculate joint weighted estimates for redshift and age with full covariance.
    
    This implements a statistically robust joint estimation approach that:
    1. Uses exponentially-weighted RLAP-Cos values as quality-based weights
    2. Computes weighted centroids in (redshift, age) space  
    3. Estimates the full 2×2 weighted covariance matrix
    4. Extracts marginal uncertainties and correlation from the covariance matrix
    
    Parameters
    ----------
    redshifts : array-like
        Redshift values from templates
    ages : array-like  
        Age values from templates (in days)
    weights : array-like
        Quality weights for each template (should be exponentially transformed)
        
    Returns
    -------
    Tuple[float, float, float, float, float]
        (weighted_redshift, weighted_age, redshift_uncertainty, age_uncertainty, redshift_age_covariance)
        
    Notes
    -----
    Statistical Method:
    - Weighted mean: μ = Σ(wᵢ xᵢ) / Σ(wᵢ)
    - Weighted covariance: Cov = Σ(wᵢ (xᵢ-μ)(yᵢ-ν)ᵀ) / Σ(wᵢ) × N_eff/(N_eff-1)
    - Effective sample size: N_eff = (Σwᵢ)² / Σ(wᵢ²)
    - Standard errors: σ_x = √(Var(x)/N_eff), σ_y = √(Var(y)/N_eff)
    
    Weight Transformation:
    - For optimal results, weights should be exponentially transformed: w = exp(rlap_cos)
    - Use apply_exponential_weighting() function before calling this function
    """
    redshifts = np.asarray(redshifts, dtype=float)
    ages = np.asarray(ages, dtype=float)
    weights = np.asarray(weights, dtype=float)
    
    # Validate inputs
    if len(redshifts) == 0 or len(ages) == 0 or len(weights) == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan
        
    if not (len(redshifts) == len(ages) == len(weights)):
        logger.error("Mismatched input lengths for joint estimation")
        return np.nan, np.nan, np.nan, np.nan, np.nan
    
    # Remove invalid data points
    valid_mask = (np.isfinite(redshifts) & np.isfinite(ages) & 
                  np.isfinite(weights) & (weights > 0))
    
    if not np.any(valid_mask):
        logger.warning("No valid (redshift, age, weight) triplets found")
        return np.nan, np.nan, np.nan, np.nan, np.nan
        
    valid_z = redshifts[valid_mask]
    valid_t = ages[valid_mask]
    valid_w = weights[valid_mask]
    N = len(valid_z)
    
    if N == 1:
        return float(valid_z[0]), float(valid_t[0]), 0.0, 0.0, 0.0
    
    # Calculate weighted means (centroids)
    sum_w = np.sum(valid_w)
    z_mean = np.sum(valid_w * valid_z) / sum_w
    t_mean = np.sum(valid_w * valid_t) / sum_w
    
    # Calculate effective sample size (handles clustering effects)
    sum_w_sq = np.sum(valid_w ** 2)
    N_eff = (sum_w ** 2) / sum_w_sq
    
    # Calculate weighted covariance matrix elements
    z_dev = valid_z - z_mean
    t_dev = valid_t - t_mean
    
    # Weighted variances and covariance (population estimates)
    var_z_pop = np.sum(valid_w * z_dev ** 2) / sum_w
    var_t_pop = np.sum(valid_w * t_dev ** 2) / sum_w  
    cov_zt_pop = np.sum(valid_w * z_dev * t_dev) / sum_w
    
    # Apply bias correction for finite sample size to get sample estimates
    if N_eff > 1:
        bias_correction = N_eff / (N_eff - 1)
        var_z_sample = var_z_pop * bias_correction
        var_t_sample = var_t_pop * bias_correction  
        cov_zt_sample = cov_zt_pop * bias_correction
    else:
        var_z_sample = var_z_pop
        var_t_sample = var_t_pop
        cov_zt_sample = cov_zt_pop
    
    # Standard errors of the weighted means (uncertainty in the means themselves)
    se_z = np.sqrt(var_z_sample / N_eff) if N_eff > 0 else np.inf
    se_t = np.sqrt(var_t_sample / N_eff) if N_eff > 0 else np.inf
    
    # Covariance of the means
    cov_means = cov_zt_sample / N_eff if N_eff > 0 else 0.0
    
    logger.info(f"Joint weighted estimates: "
                f"z={z_mean:.6f}±{se_z:.6f}, age={t_mean:.1f}±{se_t:.1f} days, "
                f"cov(z,t)={cov_means:.8f}, N_eff={N_eff:.1f}")
    
    result = (float(z_mean), float(t_mean), float(se_z), float(se_t), float(cov_means))
    return result


def calculate_weighted_redshift(
    redshifts: Union[np.ndarray, List[float]], 
    weights: Union[np.ndarray, List[float]]
) -> Tuple[float, float]:
    """
    Calculate weighted redshift estimate.
    
    Parameters
    ----------
    redshifts : array-like
        Redshift values from templates
    weights : array-like
        Quality weights for each template (should be exponentially transformed)
        
    Returns
    -------
    Tuple[float, float]
        (weighted_redshift, redshift_uncertainty)
    """
    redshifts = np.asarray(redshifts, dtype=float)
    weights = np.asarray(weights, dtype=float)
    
    if len(redshifts) == 0 or len(weights) == 0:
        return np.nan, np.nan
        
    if len(redshifts) != len(weights):
        logger.error("Mismatched input lengths for redshift estimation")
        return np.nan, np.nan
    
    # Remove invalid data points  
    # Weights should be > 0 (RLAP, cosine similarity, or RLAP-cos are all positive metrics)
    valid_mask = (np.isfinite(redshifts) & np.isfinite(weights) & (weights > 0))
    
    if not np.any(valid_mask):
        logger.warning("No valid (redshift, weight) pairs found")
        return np.nan, np.nan
        
    valid_z = redshifts[valid_mask]
    valid_w = weights[valid_mask]
    N = len(valid_z)
    
    if N == 1:
        return float(valid_z[0]), 0.0
    
    # Calculate weighted mean
    sum_w = np.sum(valid_w)
    z_mean = np.sum(valid_w * valid_z) / sum_w
    
    # Calculate effective sample size and uncertainty
    sum_w_sq = np.sum(valid_w ** 2)
    N_eff = (sum_w ** 2) / sum_w_sq
    
    # Weighted variance with bias correction
    z_dev = valid_z - z_mean
    var_z = np.sum(valid_w * z_dev ** 2) / sum_w
    
    if N_eff > 1:
        bias_correction = N_eff / (N_eff - 1)
        var_z *= bias_correction
    
    # Standard error of the weighted mean
    se_z = np.sqrt(var_z / N_eff) if N_eff > 0 else np.inf
    
    logger.info(f"Weighted redshift: {z_mean:.6f}±{se_z:.6f}, N_eff={N_eff:.1f}")
    
    return float(z_mean), float(se_z)


def calculate_weighted_age(
    ages: Union[np.ndarray, List[float]], 
    weights: Union[np.ndarray, List[float]]
) -> Tuple[float, float]:
    """
    Calculate weighted age estimate.
    
    Parameters
    ----------
    ages : array-like
        Age values in days
    weights : array-like
        Quality weights for each template (should be exponentially transformed)
        
    Returns
    -------
    Tuple[float, float]
        (weighted_age, age_uncertainty)
    """
    ages = np.asarray(ages, dtype=float)
    weights = np.asarray(weights, dtype=float)
    
    if len(ages) == 0 or len(weights) == 0:
        return np.nan, np.nan
        
    if len(ages) != len(weights):
        logger.error("Mismatched input lengths for age estimation")
        return np.nan, np.nan
    
    # Remove invalid data points
    # Note: Ages can be negative (before peak), so no age > 0 filter
    # Weights should be > 0 (RLAP, cosine similarity, or RLAP-cos are all positive metrics)
    valid_mask = (np.isfinite(ages) & np.isfinite(weights) & (weights > 0))
    
    if not np.any(valid_mask):
        # Count different types of invalid data for better diagnostics
        invalid_ages = np.sum(~np.isfinite(ages))  # Only non-finite ages are invalid
        invalid_weights = np.sum(~np.isfinite(weights) | (weights <= 0))  # Non-finite or non-positive weights
        total_pairs = len(ages)
        
        logger.warning(
            f"No valid (age, weight) pairs found from {total_pairs} templates. "
            f"Invalid ages: {invalid_ages} (non-finite), invalid weights: {invalid_weights} (≤0 or non-finite). "
            f"Note: Negative ages are valid (pre-peak). This typically means templates have low quality scores."
        )
        return np.nan, np.nan
        
    valid_t = ages[valid_mask]
    valid_w = weights[valid_mask]
    N = len(valid_t)
    
    if N == 1:
        return float(valid_t[0]), 0.0
    
    # Calculate weighted mean
    sum_w = np.sum(valid_w)
    t_mean = np.sum(valid_w * valid_t) / sum_w
    
    # Calculate effective sample size and uncertainty
    sum_w_sq = np.sum(valid_w ** 2)
    N_eff = (sum_w ** 2) / sum_w_sq
    
    # Weighted variance with bias correction
    t_dev = valid_t - t_mean
    var_t = np.sum(valid_w * t_dev ** 2) / sum_w
    
    if N_eff > 1:
        bias_correction = N_eff / (N_eff - 1)
        var_t *= bias_correction
    
    # Standard error of the weighted mean
    se_t = np.sqrt(var_t / N_eff) if N_eff > 0 else np.inf
    
    logger.info(f"Weighted age: {t_mean:.1f}±{se_t:.1f} days, N_eff={N_eff:.1f}")
    
    return float(t_mean), float(se_t)


def calculate_weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    """Calculate weighted median."""
    if len(values) == 0:
        return np.nan
        
    if len(values) == 1:
        return float(values[0])
    
    # Remove invalid data
    valid_mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(valid_mask):
        return np.nan
        
    valid_values = values[valid_mask]
    valid_weights = weights[valid_mask]
    
    if len(valid_values) == 1:
        return float(valid_values[0])
    
    # Sort by values
    sorted_indices = np.argsort(valid_values)
    sorted_values = valid_values[sorted_indices]
    sorted_weights = valid_weights[sorted_indices]
    
    # Calculate cumulative weights
    cumsum_weights = np.cumsum(sorted_weights)
    total_weight = cumsum_weights[-1]
    
    # Find median position
    median_weight = total_weight / 2.0
    
    # Find the value(s) at median position
    idx = np.searchsorted(cumsum_weights, median_weight)
    
    if idx == 0:
        return float(sorted_values[0])
    elif idx >= len(sorted_values):
        return float(sorted_values[-1])
    else:
        # Linear interpolation between adjacent values
        w1 = cumsum_weights[idx-1]
        w2 = cumsum_weights[idx]
        if w1 == median_weight:
            return float(sorted_values[idx-1])
        elif w2 == median_weight:
            return float((sorted_values[idx-1] + sorted_values[idx]) / 2.0)
        else:
            # Interpolate
            alpha = (median_weight - w1) / (w2 - w1)
            return float(sorted_values[idx-1] + alpha * (sorted_values[idx] - sorted_values[idx-1]))


def validate_joint_result(
    redshifts: np.ndarray,
    ages: np.ndarray, 
    weights: np.ndarray,
    result: Tuple[float, float, float, float, float]
) -> bool:
    """
    Validate a joint weighted calculation result.
    
    Parameters
    ----------
    redshifts : np.ndarray
        Input redshift values
    ages : np.ndarray
        Input age values
    weights : np.ndarray
        Input weights
    result : Tuple[float, float, float, float, float]
        (z_mean, t_mean, z_uncertainty, t_uncertainty, zt_covariance)
        
    Returns
    -------
    bool
        True if result is valid, False otherwise
    """
    z_mean, t_mean, z_uncertainty, t_uncertainty, zt_covariance = result
    
    # Check for finite values
    if not all(np.isfinite([z_mean, t_mean, z_uncertainty, t_uncertainty, zt_covariance])):
        # Allow NaN if inputs are empty
        if len(redshifts) == 0 or len(ages) == 0:
            return all(np.isnan([z_mean, t_mean, z_uncertainty, t_uncertainty, zt_covariance]))
        return False
    
    # Empty input case
    if len(redshifts) == 0 or len(ages) == 0:
        return all(np.isnan([z_mean, t_mean, z_uncertainty, t_uncertainty, zt_covariance]))
    
    # Check if means are within input bounds
    min_z, max_z = np.min(redshifts), np.max(redshifts)
    min_t, max_t = np.min(ages), np.max(ages)
    
    if not (min_z <= z_mean <= max_z):
        return False
    if not (min_t <= t_mean <= max_t):
        return False
        
    # Check if uncertainties are positive and reasonable
    z_range = max_z - min_z if len(redshifts) > 1 else 1.0
    t_range = max_t - min_t if len(ages) > 1 else 1.0
    
    if z_uncertainty < 0 or z_uncertainty > z_range:
        return False
    if t_uncertainty < 0 or t_uncertainty > t_range:
        return False
    
    # Check for single-template case (uncertainties should be 0)
    if len(redshifts) == 1 or len(ages) == 1:
        return z_uncertainty == 0.0 and t_uncertainty == 0.0 and zt_covariance == 0.0
        
    # Check correlation coefficient constraint: |ρ| ≤ 1
    if z_uncertainty > 0 and t_uncertainty > 0:
        correlation = zt_covariance / (z_uncertainty * t_uncertainty)
        if abs(correlation) > 1.0 + 1e-10:  # Allow small numerical errors
            logger.debug(f"Invalid correlation coefficient: ρ={correlation:.3f}")
            return False
        
    # Check covariance matrix positive semidefinite constraint
    z_var = z_uncertainty**2
    t_var = t_uncertainty**2
    determinant = z_var * t_var - zt_covariance**2
    
    # Allow small numerical errors (relative to the matrix scale)
    tolerance = 1e-10 * max(z_var * t_var, 1e-20)
    if determinant < -tolerance:
        logger.debug(f"Covariance matrix not positive semidefinite")
        return False
        
    return True


def validate_weighted_calculation(
    values: np.ndarray, 
    weights: np.ndarray, 
    result: Tuple[float, float]
) -> bool:
    """Validate a weighted calculation result."""
    weighted_mean, uncertainty = result
    
    if not np.isfinite(weighted_mean) or not np.isfinite(uncertainty):
        return False
        
    if len(values) == 0:
        return np.isnan(weighted_mean) and np.isnan(uncertainty)
        
    # Check if result is within reasonable bounds
    min_val, max_val = np.min(values), np.max(values)
    if not (min_val <= weighted_mean <= max_val):
        return False
        
    # Check if uncertainty is positive and reasonable
    if uncertainty < 0 or uncertainty > (max_val - min_val):
        return False
        
    return True


# Exports
__all__ = [
    'calculate_combined_weights',
    'apply_exponential_weighting',
    'calculate_weighted_redshift_balanced', 
    'calculate_weighted_age_estimate',      
    'calculate_uncertainty_aware_estimates',
    'calculate_joint_uncertainty_aware_estimates', 
    'calculate_joint_weighted_estimates',
    'calculate_weighted_redshift', 
    'calculate_weighted_age',
    'calculate_weighted_median',
    'validate_joint_result',
    'validate_weighted_calculation'
]