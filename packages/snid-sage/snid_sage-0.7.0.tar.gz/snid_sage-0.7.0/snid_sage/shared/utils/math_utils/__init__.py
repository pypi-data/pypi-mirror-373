"""
Mathematical utility functions for SNID SAGE.

This module provides statistically rigorous weighted calculations for
redshift and age estimation using template quality metrics.
"""

from .weighted_statistics import (
    calculate_combined_weights,
    apply_exponential_weighting,
    calculate_weighted_redshift_balanced,  # NEW: Recommended for redshift estimation
    calculate_weighted_age_estimate,       # NEW: Recommended for age estimation
    calculate_uncertainty_aware_estimates,
    calculate_joint_uncertainty_aware_estimates,
    calculate_joint_weighted_estimates,
    calculate_weighted_redshift,
    calculate_weighted_age,
    calculate_weighted_median,
    validate_joint_result,
    validate_weighted_calculation
)

from .similarity_metrics import (
    concordance_correlation_coefficient,
    compute_rlap_ccc_metric,
    compute_locality_metric,
    compute_chi_square_metric,
    get_best_metric_value,
    get_best_metric_name,
    get_metric_name_for_match,
    get_metric_display_values
)

__all__ = [
    # Weighted statistics
    'calculate_combined_weights',
    'apply_exponential_weighting',
    'calculate_weighted_redshift_balanced',  # NEW: Recommended for redshift estimation
    'calculate_weighted_age_estimate',       # NEW: Recommended for age estimation
    'calculate_uncertainty_aware_estimates',
    'calculate_joint_uncertainty_aware_estimates',
    'calculate_joint_weighted_estimates',
    'calculate_weighted_redshift',
    'calculate_weighted_age',
    'calculate_weighted_median',
    'validate_joint_result',
    'validate_weighted_calculation',
    # Similarity metrics
    'concordance_correlation_coefficient',
    'compute_rlap_ccc_metric',
    'compute_locality_metric',
    'compute_chi_square_metric',
    'get_best_metric_value',
    'get_best_metric_name',
    'get_metric_name_for_match',
    'get_metric_display_values'
]