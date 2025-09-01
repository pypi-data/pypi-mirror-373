"""
Line Preset Functions for Emission Line Analysis

Collection of preset functions for quickly adding specific types/categories of emission lines.
These functions support the dropdown menu system in the multi-step emission analysis dialog.
"""

from typing import Dict, List, Tuple, Any
from snid_sage.shared.utils.line_detection.line_db_loader import filter_lines

def get_type_ia_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Type Ia supernova lines"""
    return _add_lines_by_type(['Ia'], current_redshift, spectrum_data)

def get_type_ii_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Type II supernova lines"""
    return _add_lines_by_type(['II', 'IIn', 'IIb'], current_redshift, spectrum_data)

def get_type_ibc_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Type Ib/c supernova lines"""
    return _add_lines_by_type(['Ib', 'Ic'], current_redshift, spectrum_data)

def get_hydrogen_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add hydrogen lines"""
    return _add_lines_by_category('hydrogen', current_redshift, spectrum_data)

def get_helium_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add helium lines"""
    return _add_lines_by_category('helium', current_redshift, spectrum_data)

def get_silicon_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add silicon lines"""
    return _add_lines_by_category('silicon', current_redshift, spectrum_data)

def get_calcium_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add calcium lines"""
    return _add_lines_by_category('calcium', current_redshift, spectrum_data)

def get_oxygen_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add oxygen lines"""
    return _add_lines_by_category('oxygen', current_redshift, spectrum_data)

def get_iron_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add all iron lines"""
    return _add_lines_by_category('iron', current_redshift, spectrum_data)

def get_main_galaxy_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add main galaxy emission lines"""
    return _add_lines_by_origin('galaxy', current_redshift, spectrum_data)

def get_strong_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add only strong lines"""
    return _add_lines_by_strength(['very_strong', 'strong'], current_redshift, spectrum_data)

# Type II Submenu Methods
def get_early_type_ii(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add early Type II lines"""
    return _add_lines_by_type_and_phase(['II', 'IIn', 'IIb'], ['early', 'very_early'], current_redshift, spectrum_data)

def get_peak_type_ii(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add peak Type II lines"""
    return _add_lines_by_type_and_phase(['II', 'IIn', 'IIb'], ['maximum', 'peak'], current_redshift, spectrum_data)

def get_nebular_type_ii(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add nebular Type II lines"""
    return _add_lines_by_type_and_phase(['II', 'IIn', 'IIb'], ['nebular', 'late'], current_redshift, spectrum_data)

def get_type_iin_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Type IIn lines"""
    return _add_lines_by_type(['IIn'], current_redshift, spectrum_data)

def get_type_iib_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Type IIb lines"""
    return _add_lines_by_type(['IIb'], current_redshift, spectrum_data)

# Hydrogen Submenu Methods
def get_balmer_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Balmer series hydrogen lines"""
    return _add_lines_by_name_pattern(['H-alpha', 'H-beta', 'H-gamma', 'H-delta'], current_redshift, spectrum_data)

def get_paschen_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Paschen series hydrogen lines"""
    return _add_lines_by_name_pattern(['Pa-alpha', 'Pa-beta', 'Pa-gamma'], current_redshift, spectrum_data)

def get_halpha_only(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add only H-alpha line"""
    return _add_lines_by_name_pattern(['H-alpha'], current_redshift, spectrum_data)

def get_hbeta_only(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add only H-beta line"""
    return _add_lines_by_name_pattern(['H-beta'], current_redshift, spectrum_data)

def get_strong_hydrogen(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add strong hydrogen lines"""
    return _add_lines_by_category_and_strength('hydrogen', ['very_strong', 'strong'], current_redshift, spectrum_data)

# Iron Submenu Methods
def get_fe_ii_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Fe II lines"""
    return _add_lines_by_name_pattern(['Fe II'], current_redshift, spectrum_data)

def get_fe_iii_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add Fe III lines"""
    return _add_lines_by_name_pattern(['Fe III'], current_redshift, spectrum_data)

def get_early_iron(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add early iron lines"""
    return _add_lines_by_category_and_phase('iron', ['early', 'very_early', 'maximum'], current_redshift, spectrum_data)

def get_late_iron(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add late iron lines"""
    return _add_lines_by_category_and_phase('iron', ['late', 'nebular'], current_redshift, spectrum_data)

# Additional Methods
def get_early_sn_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add early phase supernova lines"""
    return _add_lines_by_phase(['very_early', 'early'], current_redshift, spectrum_data)

def get_maximum_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add maximum light lines"""
    return _add_lines_by_phase(['maximum', 'peak'], current_redshift, spectrum_data)

def get_late_phase_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add late phase lines"""
    return _add_lines_by_phase(['late'], current_redshift, spectrum_data)

def get_nebular_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add nebular lines"""
    return _add_lines_by_phase(['nebular'], current_redshift, spectrum_data)

def get_diagnostic_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add galaxy diagnostic lines"""
    return _add_lines_by_name_pattern(['[O III]', '[N II]', '[S II]', '[O I]'], current_redshift, spectrum_data)

def get_emission_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add emission lines only"""
    return _add_lines_by_line_type('emission', current_redshift, spectrum_data)

def get_absorption_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add absorption lines only"""
    return _add_lines_by_line_type('absorption', current_redshift, spectrum_data)

def get_very_strong_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add very strong lines"""
    return _add_lines_by_strength(['very_strong'], current_redshift, spectrum_data)

def get_common_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add all common lines"""
    return _add_lines_by_strength(['very_strong', 'strong', 'medium'], current_redshift, spectrum_data)

def get_flash_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add flash ionization lines"""
    return _add_lines_by_category('flash_ion', current_redshift, spectrum_data)

def get_interaction_lines(current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add interaction/CSM lines"""
    return _add_lines_by_category('nitrogen', current_redshift, spectrum_data)

# ========================================
# BULK LINE ADDITION UTILITY FUNCTIONS
# ========================================

def _add_lines_by_type(sn_types: List[str], current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add lines matching specific SN types (from JSON DB)."""
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(sn_types=sn_types):
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_category(category: str, current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by element category (from JSON DB)."""
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(category=category):
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_origin(origin: str, current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by origin (sn/galaxy) from JSON DB."""
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(origin=origin):
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_strength(strengths: List[str], current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Placeholder: strength not encoded in JSON DB; fallback to common categories."""
    # Keep behavior by mapping to category groups commonly considered strong
    categories = ['silicon', 'hydrogen', 'calcium', 'iron'] if strengths else []
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for cat in categories:
        for line in filter_lines(category=cat):
            line_name = line.get('key')
            if not line_name:
                continue
            line_data = {
                'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
                'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
                'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
                'sn_types': list(line.get('sn_types', []) or []),
                'category': line.get('category'),
                'origin': line.get('origin'),
            }
            if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_type_and_phase(sn_types: List[str], phases: List[str], current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add lines matching specific SN types and string phase labels from JSON DB."""
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(sn_types=sn_types, phase_labels=phases):
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_phase(phases: List[str], current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by phase labels across any SN type from JSON DB."""
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(phase_labels=phases):
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_name_pattern(patterns: List[str], current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add lines matching name patterns from JSON DB."""
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(name_patterns=patterns):
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_category_and_strength(category: str, strengths: List[str], current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Placeholder mapping for strength filters using JSON DB categories."""
    return _add_lines_by_category(category, current_redshift, spectrum_data)

def _add_lines_by_category_and_phase(category: str, phases: List[str], current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by category and phase (from JSON DB labels)."""
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(phase_labels=phases, category=category):
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _add_lines_by_line_type(line_type: str, current_redshift: float, spectrum_data: Dict) -> Dict[str, Tuple[float, Dict]]:
    """Approximate emission/absorption with category heuristics using JSON DB."""
    # Absorption-dominant categories (approx)
    if line_type == 'absorption':
        cats = ['silicon', 'stellar_absorption']
    else:
        cats = None
    lines_to_add: Dict[str, Tuple[float, Dict]] = {}
    for line in filter_lines(category=None if cats is None else None):
        # If cats specified, skip non-matching categories
        if cats is not None and line.get('category') not in cats:
            continue
        line_name = line.get('key')
        if not line_name:
            continue
        line_data = {
            'wavelength': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_air': float(line.get('wavelength_air', 0.0) or 0.0),
            'wavelength_vacuum': float(line.get('wavelength_vacuum', 0.0) or 0.0),
            'sn_types': list(line.get('sn_types', []) or []),
            'category': line.get('category'),
            'origin': line.get('origin'),
        }
        if _is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
            obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
            lines_to_add[line_name] = (obs_wavelength, line_data)
    return lines_to_add

def _is_line_in_spectrum_range(line_data: Dict, current_redshift: float, spectrum_data: Dict) -> bool:
    """Check if line is within spectrum wavelength range"""
    if not spectrum_data or 'wavelength' not in spectrum_data:
        return True
    
    obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
    wavelength = spectrum_data['wavelength']
    return wavelength[0] <= obs_wavelength <= wavelength[-1] 