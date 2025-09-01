"""
Unified Results Formatter
========================

Shared utility for formatting SNID analysis results consistently across CLI and GUI interfaces.
Ensures all output formats (display, export, save) use the same information and structure.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import numpy as np
import re


def clean_template_name(template_name: str) -> str:
    """
    Clean template name by removing _epoch_X suffix if present.
    
    Args:
        template_name: The original template name that may contain _epoch_X suffix
        
    Returns:
        Cleaned template name without the _epoch_X suffix
        
    Examples:
        >>> clean_template_name("sn1999em_epoch_3")
        "sn1999em"
        >>> clean_template_name("sn2003jo_epoch_0")
        "sn2003jo"
        >>> clean_template_name("sn1999em")
        "sn1999em"
    """
    if not template_name:
        return template_name
    
    # Use regex to match _epoch_ followed by digits at the end of the string
    import re
    # This pattern matches _epoch_ followed by one or more digits at the end of the string
    pattern = r'_epoch_\d+$'
    
    # Remove the _epoch_X suffix if it exists at the end
    cleaned_name = re.sub(pattern, '', template_name)
    
    return cleaned_name


class UnifiedResultsFormatter:
    """
    Unified formatter for SNID analysis results that ensures consistency
    between CLI and GUI output formats.
    """
    
    def __init__(self, result, spectrum_name: str = None, spectrum_path: str = None):
        """
        Initialize formatter with SNID result object.
        
        Args:
            result: SNIDResult object
            spectrum_name: Name of the spectrum (optional)
            spectrum_path: Path to spectrum file (optional)
        """
        self.result = result
        # Prefer explicit path; fall back to attributes on result
        path_from_result = getattr(result, 'spectrum_path', '') or getattr(result, 'input_file', '')
        self.spectrum_path = spectrum_path or path_from_result

        # Determine spectrum name with robust fallbacks
        if spectrum_name:
            self.spectrum_name = spectrum_name
        elif self.spectrum_path:
            try:
                self.spectrum_name = Path(self.spectrum_path).stem
            except Exception:
                self.spectrum_name = getattr(result, 'spectrum_name', 'Unknown')
        else:
            self.spectrum_name = getattr(result, 'spectrum_name', 'Unknown')
        
        # Determine which metric is being used
        self.use_rlap_cos = False
        # Default to RLAP-CCC when any enhanced metric is available on best match; fallback to RLAP
        self.metric_name = "RLAP"
        if hasattr(result, 'clustering_results') and result.clustering_results:
            self.use_rlap_cos = result.clustering_results.get('use_rlap_cos', False)
            self.metric_name = result.clustering_results.get('metric_used', 'RLAP-CCC' if self.use_rlap_cos else 'RLAP')
        else:
            try:
                # Inspect best match to decide metric label
                best_list = getattr(result, 'filtered_matches', None) or getattr(result, 'best_matches', None) or []
                if best_list and isinstance(best_list, list) and ('rlap_ccc' in best_list[0]):
                    self.metric_name = 'RLAP-CCC'
            except Exception:
                pass
        
        # Create standardized summary data
        self.summary_data = self._create_standardized_summary()
    
    def _create_standardized_summary(self) -> Dict[str, Any]:
        """Create standardized summary data structure used by all output formats"""
        result = self.result
        
        # Get the winning cluster (user selected or automatic best)
        winning_cluster = None
        cluster_label = ""
        cluster_index = -1
        is_manual_selection = False
        
        if hasattr(result, 'clustering_results') and result.clustering_results:
            clustering_results = result.clustering_results
            if clustering_results.get('success'):
                if 'user_selected_cluster' in clustering_results:
                    winning_cluster = clustering_results['user_selected_cluster']
                    cluster_index = clustering_results.get('user_selected_index', -1)
                    cluster_label = f"User Selected Cluster #{cluster_index + 1}"
                    
                    # Check if this is actually a manual selection (different from automatic best)
                    if 'best_cluster' in clustering_results:
                        best_cluster = clustering_results['best_cluster']
                        
                        # Compare the clusters to see if they're different
                        # Compare multiple fields to ensure we catch all differences
                        is_same_cluster = (
                            winning_cluster.get('type') == best_cluster.get('type') and
                            winning_cluster.get('cluster_id') == best_cluster.get('cluster_id') and
                            winning_cluster.get('size') == best_cluster.get('size')
                        )
                        
                        # Additional fallback comparison - check if they're the same object
                        is_same_object = (winning_cluster is best_cluster)
                        
                        # Use the more reliable comparison
                        if is_same_object or is_same_cluster:
                            # User selected the same cluster that was automatically chosen as best
                            cluster_label = "Best Cluster (Auto-Selected)"
                            is_manual_selection = False
                        else:
                            # User selected a different cluster than the automatic best
                            is_manual_selection = True
                    else:
                        # No best_cluster to compare against, assume it's manual
                        is_manual_selection = True
                elif 'best_cluster' in clustering_results:
                    winning_cluster = clustering_results['best_cluster']
                    cluster_label = "Best Cluster (Auto-Selected)"
                    # Find index of best cluster
                    all_candidates = clustering_results.get('all_candidates', [])
                    for i, cluster in enumerate(all_candidates):
                        if cluster == winning_cluster:
                            cluster_index = i
                            break
        
        # Get cluster matches if available
        cluster_matches = []
        if winning_cluster:
            cluster_matches = winning_cluster.get('matches', [])
            # Sort by best available metric (RLAP-CCC if available, otherwise RLAP) descending
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            cluster_matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
        
        # Use cluster matches if available, otherwise fall back to regular matches
        active_matches = cluster_matches if cluster_matches else (
            getattr(result, 'filtered_matches', []) or getattr(result, 'best_matches', [])
        )
        
        # Calculate enhanced estimates from cluster if available
        enhanced_redshift = result.consensus_redshift
        enhanced_redshift_error = result.consensus_redshift_error
        enhanced_age = getattr(result, 'consensus_age', 0)
        enhanced_age_error = getattr(result, 'consensus_age_error', 0)
        
        # Store both subtype-specific and full cluster redshift/age for display options
        subtype_redshift = None
        subtype_redshift_error = None
        subtype_template_count = 0
        subtype_age = None
        subtype_age_error = None
        subtype_age_template_count = 0
        full_cluster_redshift = None
        full_cluster_redshift_error = None
        full_cluster_age = enhanced_age
        full_cluster_age_error = enhanced_age_error
        # Initialize covariance terms to safe defaults so downstream access is always defined
        subtype_redshift_age_covariance = np.nan
        full_cluster_redshift_age_covariance = np.nan
        
        if winning_cluster and cluster_matches:
            # Check if subtype-specific joint estimates are available
            subtype_redshift = winning_cluster.get('subtype_redshift')
            subtype_redshift_error = winning_cluster.get('subtype_redshift_error')
            subtype_template_count = winning_cluster.get('subtype_template_count', 0)
            subtype_age = winning_cluster.get('subtype_age')
            subtype_age_error = winning_cluster.get('subtype_age_error')
            subtype_age_template_count = winning_cluster.get('subtype_age_template_count', 0)
            subtype_redshift_age_covariance = winning_cluster.get('subtype_redshift_age_covariance', np.nan)
            
            # Get full cluster joint estimates
            full_cluster_redshift = winning_cluster.get('enhanced_redshift', result.consensus_redshift)
            full_cluster_redshift_error = winning_cluster.get('weighted_redshift_uncertainty', result.consensus_redshift_error)
            full_cluster_age = winning_cluster.get('cluster_age', enhanced_age)
            full_cluster_age_error = winning_cluster.get('cluster_age_error', enhanced_age_error)
            full_cluster_redshift_age_covariance = winning_cluster.get('cluster_redshift_age_covariance', np.nan)
            
            # Use subtype redshift as primary if available and valid, otherwise fall back to cluster redshift
            if (subtype_redshift is not None and not np.isnan(subtype_redshift) and 
                subtype_redshift_error is not None and not np.isnan(subtype_redshift_error) and
                subtype_template_count > 0):
                enhanced_redshift = subtype_redshift
                enhanced_redshift_error = subtype_redshift_error
            else:
                # Fall back to full cluster redshift
                enhanced_redshift = full_cluster_redshift
                enhanced_redshift_error = full_cluster_redshift_error
            
            # Use subtype age as primary if available and valid, otherwise fall back to cluster age
            if (subtype_age is not None and not np.isnan(subtype_age) and 
                subtype_age_error is not None and not np.isnan(subtype_age_error) and
                subtype_age_template_count > 0):
                enhanced_age = subtype_age
                enhanced_age_error = subtype_age_error
            else:
                # Calculate enhanced age from ALL cluster matches (fallback behavior)
                try:
                    from snid_sage.shared.utils.math_utils import calculate_weighted_age
                    ages = []
                    age_rlaps = []
                    for m in cluster_matches:
                        template = m.get('template', {})
                        age = template.get('age', 0.0) if template else 0.0
                        # Check for valid age (negative ages are valid for pre-peak)
                        if age is not None and np.isfinite(age):
                            ages.append(age)
                            # Use RLAP-cos if available, otherwise RLAP
                            from snid_sage.shared.utils.math_utils import get_best_metric_value
                            age_rlaps.append(get_best_metric_value(m))
                    
                    if ages:
                        ages = np.array(ages)
                        # Use RLAP-cos instead of RLAP for age weighting
                        from snid_sage.shared.utils.math_utils import get_best_metric_value
                        age_rlaps = np.array([get_best_metric_value(m) for m in cluster_matches 
                                             if m.get('template', {}).get('age', 0.0) is not None and 
                                             np.isfinite(m.get('template', {}).get('age', 0.0))])
                        age_mean, age_total_error = calculate_weighted_age(
                            ages, age_rlaps
                        )
                        full_cluster_age = age_mean
                        full_cluster_age_error = age_total_error
                        enhanced_age = age_mean
                        enhanced_age_error = age_total_error
                except ImportError:
                    pass  # Fall back to consensus values
        
        # Calculate subtype information for the active cluster (not the original result)
        subtype_confidence = 0
        subtype_margin_over_second = 0
        second_best_subtype = None
        consensus_subtype = result.best_subtype  # Default to original
        
        if winning_cluster and cluster_matches:
            # First, try to use pre-calculated subtype information from the cluster
            if 'subtype_info' in winning_cluster:
                subtype_info = winning_cluster['subtype_info']
                consensus_subtype = subtype_info.get('best_subtype', result.best_subtype)
                subtype_confidence = subtype_info.get('subtype_confidence', 0)
                subtype_margin_over_second = subtype_info.get('subtype_margin_over_second', 0)
                second_best_subtype = subtype_info.get('second_best_subtype', None)
            else:
                # Fall back to recalculating subtype information for the active cluster
                try:
                    from snid_sage.snid.cosmological_clustering import choose_subtype_weighted_voting
                    
                    # Get the cluster type and matches
                    cluster_type = winning_cluster.get('type', 'Unknown')
                    type_matches = [m for m in cluster_matches if m['template'].get('type') == cluster_type]
                    
                    if type_matches and hasattr(result, 'clustering_results') and result.clustering_results:
                        clustering_results = result.clustering_results
                        # Find the cluster index within its type
                        type_data = clustering_results.get('type_data', {})
                        if cluster_type in type_data:
                            type_clusters = type_data[cluster_type].get('clusters', [])
                            # Find which cluster this is within the type
                            cluster_idx = None
                            for i, cluster in enumerate(type_clusters):
                                if cluster == winning_cluster:
                                    cluster_idx = i
                                    break
                            
                            if cluster_idx is not None:
                                gamma = type_data[cluster_type].get('gamma', np.array([]))
                                if gamma.size > 0:
                                    consensus_subtype, subtype_confidence, subtype_margin_over_second, second_best_subtype = choose_subtype_weighted_voting(
                                        cluster_type, cluster_idx, type_matches, gamma
                                    )
                except (ImportError, Exception) as e:
                    # Fall back to original values if calculation fails
                    subtype_confidence = getattr(result, 'subtype_confidence', 0)
                    subtype_margin_over_second = getattr(result, 'subtype_margin_over_second', 0)
                    second_best_subtype = getattr(result, 'second_best_subtype', None)
        else:
            # Use original values if no clustering
            subtype_confidence = getattr(result, 'subtype_confidence', 0)
            subtype_margin_over_second = getattr(result, 'subtype_margin_over_second', 0)
            second_best_subtype = getattr(result, 'second_best_subtype', None)
        
        # If there is no clustering and one or two surviving matches, adopt top match subtype
        try:
            if (winning_cluster is None) and isinstance(active_matches, list) and (1 <= len(active_matches) <= 2):
                single_match = active_matches[0]
                single_tpl = single_match.get('template', {}) if isinstance(single_match.get('template'), dict) else {}
                single_subtype = single_tpl.get('subtype', '') if isinstance(single_tpl, dict) else ''
                if single_subtype and single_subtype.strip() != '' and single_subtype != 'Unknown':
                    consensus_subtype = single_subtype
        except Exception:
            pass

        # Create standardized summary
        summary = {
            # Basic identification
            'spectrum_name': self.spectrum_name,
            'spectrum_path': self.spectrum_path,
            'success': result.success,
            'timestamp': datetime.now().isoformat(),
            
            # Primary classification results
            'best_template': result.template_name,
            'best_template_type': result.template_type,
            'best_template_subtype': result.template_subtype,
            'consensus_type': result.consensus_type,
            'consensus_subtype': consensus_subtype,  # Use recalculated subtype
            
            # Primary measurements
            'redshift': result.redshift,
            'redshift_error': result.redshift_error,
            'rlap': result.rlap,
            'r_value': getattr(result, 'r', 0),
            'lap_value': getattr(result, 'lap', 0),
            
            # Enhanced estimates (cluster-weighted when available)
            'enhanced_redshift': enhanced_redshift,
            'enhanced_redshift_error': enhanced_redshift_error,
            'enhanced_age': enhanced_age,
            'enhanced_age_error': enhanced_age_error,
            
            # Joint estimation breakdown for display options
            'subtype_redshift': subtype_redshift,
            'subtype_redshift_error': subtype_redshift_error,
            'subtype_age': subtype_age,
            'subtype_age_error': subtype_age_error,
            'subtype_redshift_age_covariance': subtype_redshift_age_covariance,
            'subtype_template_count': subtype_template_count,
            'subtype_age_template_count': subtype_age_template_count,
            'using_subtype_estimates': (subtype_redshift is not None and not np.isnan(subtype_redshift) and 
                                      subtype_age is not None and not np.isnan(subtype_age) and 
                                      subtype_age_template_count > 0),
            
            # Full cluster joint estimates
            'full_cluster_redshift': full_cluster_redshift,
            'full_cluster_redshift_error': full_cluster_redshift_error,
            'full_cluster_age': full_cluster_age,
            'full_cluster_age_error': full_cluster_age_error,
            'full_cluster_redshift_age_covariance': full_cluster_redshift_age_covariance,
            
            # Legacy compatibility flags  
            'using_subtype_redshift': (subtype_redshift is not None and not np.isnan(subtype_redshift) and subtype_template_count > 0),
            'using_subtype_age': (subtype_age is not None and not np.isnan(subtype_age) and subtype_age_template_count > 0),
            
            # Security and confidence
            'subtype_confidence': subtype_confidence,  # Use recalculated confidence
            'subtype_margin_over_second': subtype_margin_over_second,  # Use recalculated margin
            'second_best_subtype': second_best_subtype,  # Use recalculated second best
            
            # Analysis metadata
            'runtime_seconds': result.runtime_sec,
            'total_matches': len(getattr(result, 'best_matches', [])),
            'analysis_method': 'GMM Clustering' if winning_cluster else 'Standard Analysis',
            
            # Clustering information
            'has_clustering': winning_cluster is not None,
            'cluster_label': cluster_label,
            'cluster_index': cluster_index,
            'is_manual_selection': is_manual_selection,  # Store manual selection flag
            'cluster_size': len(cluster_matches) if cluster_matches else 0,
            'cluster_type': winning_cluster.get('type', '') if winning_cluster else '',
            'cluster_quality': winning_cluster.get('redshift_quality', '') if winning_cluster else '',
            'cluster_mean_rlap': winning_cluster.get('mean_rlap', 0) if winning_cluster else 0,
            'cluster_mean_metric': winning_cluster.get('mean_metric', winning_cluster.get('mean_rlap', 0)) if winning_cluster else 0,
            'cluster_score': winning_cluster.get('composite_score', 0) if winning_cluster else 0,
            
            # New quality metrics
            'cluster_quality_level': winning_cluster.get('quality_assessment', {}).get('quality_category', '') if winning_cluster else '',
            'cluster_quality_description': winning_cluster.get('quality_assessment', {}).get('quality_description', '') if winning_cluster else '',
            'cluster_mean_top_5': winning_cluster.get('quality_assessment', {}).get('mean_top_5', 0) if winning_cluster else 0,
            'cluster_penalized_score': winning_cluster.get('quality_assessment', {}).get('penalized_score', 0) if winning_cluster else 0,
            'cluster_confidence_level': winning_cluster.get('confidence_assessment', {}).get('confidence_level', '') if winning_cluster else '',
            'cluster_confidence_description': winning_cluster.get('confidence_assessment', {}).get('confidence_description', '') if winning_cluster else '',
            'cluster_statistical_significance': winning_cluster.get('confidence_assessment', {}).get('statistical_significance', '') if winning_cluster else '',
            'cluster_second_best_type': winning_cluster.get('confidence_assessment', {}).get('second_best_type', '') if winning_cluster else '',
            
            # Template matches (ALL from active matches if clustering, otherwise respect engine-selected count)
            'template_matches': (
                self._format_template_matches(cluster_matches)
                if winning_cluster and cluster_matches
                else self._format_template_matches(
                    active_matches[: max(1, len(getattr(result, 'best_matches', []) or []))]
                )
            ),
            
            # Additional clustering statistics
            'clustering_overview': self._get_clustering_overview() if hasattr(result, 'clustering_results') else None,
        }
        
        return summary
    
    def _format_template_matches(self, matches: List[Dict]) -> List[Dict[str, Any]]:
        """Format template matches for consistent display - now includes ALL matches from cluster"""
        formatted_matches = []
        
        # If we have clustering, get ALL matches from the winning cluster, not just top 10
        # Check clustering state directly from result object to avoid circular dependency
        has_clustering = (hasattr(self.result, 'clustering_results') and 
                         self.result.clustering_results and 
                         self.result.clustering_results.get('success'))
        
        if has_clustering:
            winning_cluster = self._get_active_cluster()
            if winning_cluster:
                cluster_matches = winning_cluster.get('matches', [])
                # Sort by best available metric (RLAP-CCC if available, otherwise RLAP) descending
                from snid_sage.shared.utils.math_utils import get_best_metric_value
                matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
        
        for i, match in enumerate(matches, 1):
            template = match.get('template', {})
            template_name_original = match.get('name', template.get('name', 'Unknown'))
            template_name = clean_template_name(template_name_original)
            
            # Get type and subtype separately
            main_type = match.get('type', template.get('type', 'Unknown'))
            subtype = template.get('subtype', '')
            if not subtype or subtype == 'Unknown':
                subtype = ''
            
            # Get age from template
            age = template.get('age', 0.0) if template else 0.0
            
            # Get redshift error from correlation analysis
            redshift_error = match.get('redshift_error', 0)
            
            # Get all available metric values for display
            from snid_sage.shared.utils.math_utils import get_metric_display_values, get_best_metric_value
            metric_values = get_metric_display_values(match)
            
            formatted_match = {
                'rank': i,
                'template_name': template_name,
                'display_type': subtype if subtype else main_type,  # Prefer subtype for display
                'full_type': main_type,
                'subtype': subtype,
                'age_days': age,
                'redshift': match.get('redshift', 0),
                'redshift_error': redshift_error,
                'rlap': match.get('rlap', 0),
                'correlation': match.get('correlation', 0),
                'grade': match.get('grade', ''),
                
                # Enhanced metric information
                'primary_metric': metric_values['primary_metric'],
                'metric_name': metric_values['metric_name'],
                'best_metric_value': get_best_metric_value(match)
            }
            
            # Add RLAP-CCC specific fields if available
            if 'rlap_cos' in metric_values:
                formatted_match.update({
                    'rlap_cos': metric_values['rlap_cos'],
                    'cosine_similarity': metric_values['cosine_similarity'],
                    'cosine_similarity_capped': metric_values['cosine_similarity_capped']
                })
            
            formatted_matches.append(formatted_match)
        
        return formatted_matches
    
    def _get_clustering_overview(self) -> Optional[Dict[str, Any]]:
        """Get clustering overview information"""
        if not hasattr(self.result, 'clustering_results') or not self.result.clustering_results:
            return None
        
        clustering_results = self.result.clustering_results
        if not clustering_results.get('success'):
            return None
        
        all_candidates = clustering_results.get('all_candidates', [])
        if len(all_candidates) <= 1:
            return None
        
        # Get active cluster
        active_cluster = None
        if 'user_selected_cluster' in clustering_results:
            active_cluster = clustering_results['user_selected_cluster']
        elif 'best_cluster' in clustering_results:
            active_cluster = clustering_results['best_cluster']
        
        # Get other clusters (top 3)
        other_clusters = [c for c in all_candidates if c != active_cluster][:3]
        
        return {
            'total_clusters_found': len(all_candidates),
            'active_cluster_type': active_cluster.get('type', 'Unknown') if active_cluster else 'Unknown',
            'other_top_clusters': [
                {
                    'type': c.get('type', 'Unknown'),
                    'size': c.get('size', 0),
                    'mean_rlap': c.get('mean_rlap', 0),
                    'mean_metric': c.get('mean_metric', c.get('mean_rlap', 0))
                }
                for c in other_clusters
            ]
        }
    
    def get_display_summary(self) -> str:
        """Get formatted summary for display (CLI/GUI)"""
        s = self.summary_data
        
        # Use the manual selection flag from summary data
        is_manual_selection = s.get('is_manual_selection', False)
        
        # Build display summary
        lines = [
            "SNID-SAGE CLASSIFICATION RESULTS",
            "=" * 50,
            "",
        ]
        
        # Add file name line
        try:
            file_name = Path(self.spectrum_path).name if self.spectrum_path else self.spectrum_name
        except Exception:
            file_name = self.spectrum_name
        lines.append(f"File: {file_name}")
        lines.append("")
        
        # Removed the "FINAL CLASSIFICATION (...)" line per requirements

        # Winning single template and its info (with cleaned name)
        try:
            best_template_entry = s['template_matches'][0] if s.get('template_matches') else None
        except Exception:
            best_template_entry = None

        if best_template_entry:
            best_template_name = clean_template_name(best_template_entry.get('template_name', s.get('best_template', 'Unknown')))
            best_template_type = best_template_entry.get('full_type', s.get('best_template_type', 'Unknown'))
            best_template_subtype = best_template_entry.get('subtype', s.get('best_template_subtype', ''))
            best_metric_name = best_template_entry.get('metric_name', self.metric_name)
            best_metric_value = best_template_entry.get('best_metric_value', best_template_entry.get('rlap', s.get('rlap', 0)))
            best_z = best_template_entry.get('redshift', s.get('redshift', 0))
            best_z_err = best_template_entry.get('redshift_error', s.get('redshift_error', 0))
            best_age = best_template_entry.get('age_days', None)
        else:
            best_template_name = clean_template_name(s.get('best_template', 'Unknown'))
            best_template_type = s.get('best_template_type', 'Unknown')
            best_template_subtype = s.get('best_template_subtype', '')
            best_metric_name = self.metric_name
            best_metric_value = s.get('rlap', 0)
            best_z = s.get('redshift', 0)
            best_z_err = s.get('redshift_error', 0)
            best_age = None

        lines.append(f"Best Template: {best_template_name}")
        type_sub_line = f"   └─ Type: {best_template_type}"
        if best_template_subtype and best_template_subtype != 'Unknown':
            type_sub_line += f", Subtype: {best_template_subtype}"
        lines.append(type_sub_line)
        age_text = f"{best_age:.1f}" if best_age is not None and np.isfinite(best_age) else "N/A"
        z_err_text = f"{best_z_err:.6f}" if best_z_err and best_z_err > 0 else "N/A"
        lines.append(f"   └─ {best_metric_name}: {best_metric_value:.1f} | z={best_z:.6f} ± {z_err_text} | age={age_text}")
        lines.append("")
        
        # Type with quality, plus confidence and margin consolidated into parentheses
        best_type_info_parts = []
        if s['has_clustering'] and s['cluster_quality_level']:
            best_type_info_parts.append(f"Quality: {s['cluster_quality_level'].title()}")
        # Add confidence level and type margin ONLY for automatic selection
        if not is_manual_selection and s['has_clustering'] and s['cluster_confidence_level']:
            best_type_info_parts.append(f"Confidence: {s['cluster_confidence_level'].title()}")
            if s['cluster_confidence_description']:
                second_best_type = s.get('cluster_second_best_type', None)
                if second_best_type and second_best_type != 'N/A':
                    # Try to extract the margin percentage from the description
                    margin_text = None
                    if '% better than second best' in s['cluster_confidence_description']:
                        margin_match = re.search(r'(\d+\.?\d*)% better than second best', s['cluster_confidence_description'])
                        if margin_match:
                            margin_text = margin_match.group(1)
                    if margin_text is None:
                        # Fallback: extract text before phrase
                        margin_text = s['cluster_confidence_description'].split('% better than second best')[0].strip()
                    if margin_text:
                        best_type_info_parts.append(f"margin over next-best type {second_best_type}: +{margin_text}%")
        # Compose Best Type line
        lines.append(
            f"Best Type: {s['consensus_type']} ({'; '.join(best_type_info_parts)})" if best_type_info_parts else f"Best Type: {s['consensus_type']}"
        )
        
        # Subtype with confidence and margin consolidated into parentheses (no indent) and renamed to Best Subtype
        if s['consensus_subtype'] and s['consensus_subtype'] != 'Unknown':
            subtype_info_parts = []
            if s['subtype_confidence'] > 0:
                # Convert numeric confidence to qualitative level (like CLI)
                if s['subtype_confidence'] > 0.7:
                    confidence_level = "High"
                elif s['subtype_confidence'] > 0.4:
                    confidence_level = "Medium"
                else:
                    confidence_level = "Low"
                subtype_info_parts.append(f"confidence: {confidence_level}")
            second_best = s.get('second_best_subtype')
            margin = s.get('subtype_margin_over_second', 0)
            if second_best and second_best != s['consensus_subtype']:
                if margin == 0:
                    subtype_info_parts.append(f"tied with {second_best}")
                else:
                    subtype_info_parts.append(f"margin over next-best subtype {second_best}: +{margin:.1f}% based on weighted voting")
            if subtype_info_parts:
                lines.append(f"Best Subtype: {s['consensus_subtype']} ({'; '.join(subtype_info_parts)})")
            else:
                lines.append(f"Best Subtype: {s['consensus_subtype']}")
        
        # Measurements are integrated into the Best Type section (no separate header)
        
        # Use enhanced (weighted) redshift if clustering was used, otherwise regular
        # Suppress redshift display when not clustered and matches are too few (≤2)
        template_count = len(s.get('template_matches', [])) if isinstance(s.get('template_matches', []), list) else 0
        suppress_redshift_age = (not s['has_clustering']) and (template_count <= 2)
        if (not suppress_redshift_age) and s['has_clustering'] and s['enhanced_redshift'] != s['redshift']:
            # Check if we're using subtype-specific redshift
            if s.get('using_subtype_redshift', False):
                # Show subtype-specific redshift as primary
                subtype_name = s.get('consensus_subtype', 'Unknown')
                template_count = s.get('subtype_template_count', 0)
                weight_note = f"weighted from {template_count} {subtype_name} subtype templates"
                redshift_text = (
                    f"Redshift: {s['enhanced_redshift']:.6f} ± {s['enhanced_redshift_error']:.6f} "
                    f"({weight_note})"
                )
                lines.append(redshift_text)
                
                # Optionally show full cluster redshift if different and user wants to see it
                full_cluster_z = s.get('full_cluster_redshift')
                full_cluster_z_err = s.get('full_cluster_redshift_error')
                if (full_cluster_z is not None and full_cluster_z_err is not None and 
                    abs(full_cluster_z - s['enhanced_redshift']) > 0.0001):  # Only show if meaningfully different
                    lines.append(f"   └─ Full cluster redshift: {full_cluster_z:.6f} ± {full_cluster_z_err:.6f} (from {s['cluster_size']} total templates)")
            else:
                # Fall back to full cluster redshift display
                notes = []
                # Optionally show components of uncertainty in parentheses
                try:
                    winning_cluster = self._get_active_cluster()
                    if winning_cluster:
                        stat_error = winning_cluster.get('statistical_redshift_uncertainty', 0)
                        sys_error = winning_cluster.get('systematic_redshift_uncertainty', 0)
                        if stat_error > 0 and sys_error > 0:
                            notes.append(f"stat: ±{stat_error:.6f}")
                            notes.append(f"sys: ±{sys_error:.6f}")
                except:
                    pass  # If components not available, just show combined
                notes.append(f"weighted from {s['cluster_size']} cluster templates, includes individual errors + cluster scatter τ")
                notes_str = f" ({'; '.join(notes)})" if notes else ""
                redshift_text = f"Redshift: {s['enhanced_redshift']:.6f} ± {s['enhanced_redshift_error']:.6f}{notes_str}"
                lines.append(redshift_text)
        elif not suppress_redshift_age:
            # Regular redshift from best template
            lines.append(f"Redshift: {s['redshift']:.6f} ± {s['redshift_error']:.6f} (correlation fit uncertainty)")
        
        # Display age information (suppress in weak/no-cluster small-match cases)
        if (not suppress_redshift_age) and s['enhanced_age'] is not None and np.isfinite(s['enhanced_age']):
            # Check if we're using subtype-specific age
            if s.get('using_subtype_age', False):
                # Show subtype-specific age as primary with inline weighting note
                subtype_name = s.get('consensus_subtype', 'Unknown')
                age_template_count = s.get('subtype_age_template_count', 0)
                weight_note = f"weighted from {age_template_count} {subtype_name} subtype templates"
                lines.append(f"Age: {s['enhanced_age']:.1f} ± {s['enhanced_age_error']:.1f} days ({weight_note})")
                
                # Optionally show full cluster age if different and meaningful
                full_cluster_age = s.get('full_cluster_age')
                full_cluster_age_err = s.get('full_cluster_age_error')
                if (full_cluster_age is not None and np.isfinite(full_cluster_age) and full_cluster_age_err is not None and
                    abs(full_cluster_age - s['enhanced_age']) > 5):  # Only show if meaningfully different (>5 days)
                    # Count total templates with ages in cluster
                    cluster_age_count = len([m for m in s.get('template_matches', []) 
                                           if m.get('age_days', 0) is not None and np.isfinite(m.get('age_days', 0))])
                    lines.append(f"   └─ Full cluster age: {full_cluster_age:.1f} ± {full_cluster_age_err:.1f} days (from {cluster_age_count} total templates)")
            else:
                # Fall back to standard age display
                lines.append(f"Age: {s['enhanced_age']:.1f} ± {s['enhanced_age_error']:.1f} days")
        
        lines.append("")
        # Clustering overview removed per updated summary requirements
        

        
        # Template matches - show ALL from winning cluster with detailed info and improved formatting
        if s['template_matches']:
            cluster_note = f" (from {s['cluster_label']})" if s['has_clustering'] else ""

            # Determine display metric name from first match (RLAP-CCC if available, else RLAP)
            try:
                first_metric_name = s['template_matches'][0].get('metric_name', self.metric_name)
            except Exception:
                first_metric_name = self.metric_name

            # Compact, consistently aligned columns
            rank_w = 3
            template_w = 16
            type_w = 6
            subtype_w = 9
            metric_w = max(8, len(str(first_metric_name)))
            redshift_w = 11
            error_w = 11
            age_w = 6

            header = (
                f"{'#':>{rank_w}} "
                f"{'Template':<{template_w}} "
                f"{'Type':<{type_w}} "
                f"{'Subtype':<{subtype_w}} "
                f"{first_metric_name:>{metric_w}} "
                f"{'Redshift':>{redshift_w}} "
                f"{'±Error':>{error_w}} "
                f"{'Age':>{age_w}}"
            )

            lines.extend([
                f"TEMPLATE MATCHES{cluster_note}:",
                header,
                "-" * len(header),
            ])
            
            for match in s['template_matches']:
                age_val = match['age_days'] if match['age_days'] is not None else None
                redshift_error_val = match.get('redshift_error', 0)
                
                # Use best available metric value
                metric_value = match.get('best_metric_value', match['rlap'])
                
                # Prepare fields with alignment and truncation
                template_name = (match['template_name'] or '')[:template_w]
                full_type = (match['full_type'] or '')[:type_w]
                subtype = (match['subtype'] or '')[:subtype_w]

                if isinstance(redshift_error_val, (int, float)) and redshift_error_val > 0:
                    redshift_error_str = f"{redshift_error_val:.6f}"
                else:
                    redshift_error_str = "N/A"

                if isinstance(age_val, (int, float)):
                    age_str = f"{age_val:.1f}"
                else:
                    age_str = "N/A"

                lines.append(
                    f"{match['rank']:>{rank_w}} "
                    f"{template_name:<{template_w}} "
                    f"{full_type:<{type_w}} "
                    f"{subtype:<{subtype_w}} "
                    f"{metric_value:>{metric_w}.1f} "
                    f"{match['redshift']:>{redshift_w}.6f} "
                    f"{redshift_error_str:>{error_w}} "
                    f"{age_str:>{age_w}}"
                )
        
        # Weak/no-match note for cases with no clustering and very few thresholded matches
        try:
            # If clustering failed or absent, check number of filtered matches that survive RLAP-CCC threshold
            result = self.result
            failure_reason = getattr(result, 'clustering_failure_reason', '')
            has_clusters = bool(getattr(result, 'clustering_results', None)) and getattr(result, 'clustering_results', {}).get('success', False)
            if not has_clusters:
                fm = getattr(result, 'filtered_matches', []) or []
                # Determine if best metric is RLAP-CCC by inspecting fields
                any_ccc = any(('rlap_ccc' in m) for m in fm)
                surviving = len(fm)
                if surviving == 0:
                    lines.append("")
                    lines.append("No matches above RLAP-CCC threshold. Try Advanced Preprocessing or different parameters.")
                elif surviving <= 2:
                    lines.append("")
                    lines.append("Only weak match(es) above RLAP-CCC threshold. Results may be unreliable.")
        except Exception:
            pass

        # Filter out empty strings and join
        return "\n".join(line for line in lines if line is not None)
    
    def get_export_data(self) -> Dict[str, Any]:
        """Get data structure for export (JSON, CSV, etc.)"""
        return self.summary_data.copy()
    
    def get_cli_one_line_summary(self) -> str:
        """Get one-line summary for CLI batch processing"""
        s = self.summary_data
        
        # Format type display
        type_display = f"{s['consensus_type']} {s['consensus_subtype']}".strip()
        
        # Use enhanced redshift if clustering was used
        if s['has_clustering']:
            redshift = s['enhanced_redshift']
            z_marker = "🎯"  # Cluster analysis marker
        else:
            redshift = s['redshift']
            z_marker = ""
        
        # Get best metric value
        if s['template_matches']:
            best_metric = s['template_matches'][0].get('best_metric_value', s['rlap'])
        else:
            best_metric = s['rlap']
        
        return f"{self.spectrum_name}: {type_display} z={redshift:.6f} {self.metric_name}={best_metric:.1f} {z_marker}"
    
    def save_to_file(self, filename: str, format_type: str = 'txt'):
        """Save results to file in specified format"""
        if format_type.lower() == 'json':
            self._save_json(filename)
        elif format_type.lower() == 'csv':
            self._save_csv(filename)
        else:  # txt
            self._save_txt(filename)
    
    def _save_json(self, filename: str):
        """Save results as JSON"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.get_export_data(), f, indent=2, default=str)
    
    def _save_csv(self, filename: str):
        """Save results as CSV"""
        import csv
        data = self.get_export_data()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Basic information
            writer.writerow(['Property', 'Value'])
            for key, value in data.items():
                if not isinstance(value, (list, dict)) or value is None:
                    writer.writerow([key, value])
            
            # Template matches
            if data['template_matches']:
                writer.writerow([])
                writer.writerow(['Template Matches'])
                writer.writerow(['Rank', 'Template', 'Type', 'Subtype', 'Age', 'Redshift', self.metric_name])
                
                for match in data['template_matches']:
                    writer.writerow([
                        match['rank'], match['template_name'], match['full_type'],
                        match['subtype'], match['age_days'], match['redshift'], 
                        match.get('best_metric_value', match['rlap'])
                    ])
    
    def _save_txt(self, filename: str):
        """Save results as text"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(self.get_display_summary())
    
    def _get_active_cluster(self):
        """Get the active cluster being used"""
        if not hasattr(self.result, 'clustering_results') or not self.result.clustering_results:
            return None
        
        clustering_results = self.result.clustering_results
        if not clustering_results.get('success'):
            return None
        
        if 'user_selected_cluster' in clustering_results:
            return clustering_results['user_selected_cluster']
        elif 'best_cluster' in clustering_results:
            return clustering_results['best_cluster']
        
        return None


def create_unified_formatter(result, spectrum_name: str = None, spectrum_path: str = None) -> UnifiedResultsFormatter:
    """
    Convenience function to create a unified results formatter.
    
    Args:
        result: SNIDResult object
        spectrum_name: Name of the spectrum (optional)
        spectrum_path: Path to spectrum file (optional)
    
    Returns:
        UnifiedResultsFormatter instance
    """
    return UnifiedResultsFormatter(result, spectrum_name, spectrum_path) 