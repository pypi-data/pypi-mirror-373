"""
SNID SAGE - Line Selection Utilities
====================================

Utilities for selecting and filtering emission lines based on various criteria.
Part of the SNID SAGE shared utilities.
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from snid_sage.shared.constants.physical import SUPERNOVA_EMISSION_LINES

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('line_selection')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('line_selection')


def calculate_redshift_from_velocity(velocity_km_s: float) -> float:
    """Calculate redshift component from velocity in km/s"""
    SPEED_OF_LIGHT_KMS = 299792.458
    return velocity_km_s / SPEED_OF_LIGHT_KMS


def is_line_in_spectrum_range(line_data: Dict[str, Any], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> bool:
    """Check if line is within spectrum wavelength range"""
    if not spectrum_data or 'wavelength' not in spectrum_data:
        return True
    
    obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
    wavelength = spectrum_data['wavelength']
    return wavelength[0] <= obs_wavelength <= wavelength[-1]


def get_line_color(line_data: Dict[str, Any], line_origin: str = 'sn') -> str:
    """Get appropriate color for a line based on its properties"""
    # Element-based color palette for lines (improved for dark backgrounds)
    element_colors = {
        'hydrogen': '#ff6666',      # Brighter red
        'helium': '#88ccff',        # Much brighter blue (was too dark)
        'oxygen': '#66dddd',        # Brighter cyan
        'carbon': '#ffaa66',        # Brighter orange
        'nitrogen': '#cc66ff',      # Brighter purple
        'silicon': '#aa88ff',       # Much brighter violet
        'iron': '#ffcc66',          # Brighter yellow
        'calcium': '#66cc66',       # Brighter green
        'galaxy': '#66ff99',        # Much brighter green for galaxy lines
        'flash_ion': '#ff66ee'      # Brighter pink
    }
    
    # First try to get color from line data
    if 'color' in line_data and line_data['color']:
        return line_data['color']
    
    # Get category-based color
    category = line_data.get('category', 'unknown')
    if category in element_colors:
        return element_colors[category]
    
    # Fallback to origin-based colors
    if line_origin == 'sn':
        return '#ff4444'  # Red for SN
    else:
        return '#66ff99'  # Bright green for galaxy (better visibility)


def find_closest_line(click_wavelength: float, sn_lines: Dict, galaxy_lines: Dict, tolerance: float = 10.0) -> Tuple[str, Dict, float]:
    """Find the closest line to the given wavelength"""
    closest_line = None
    min_distance = float('inf')
    
    # Check all selected lines
    all_lines = {**sn_lines, **galaxy_lines}
    
    for line_name, (obs_wavelength, line_data) in all_lines.items():
        distance = abs(obs_wavelength - click_wavelength)
        
        if distance < tolerance and distance < min_distance:
            min_distance = distance
            closest_line = (line_name, line_data, distance)
    
    return closest_line


def add_nearby_lines(click_wavelength: float, current_redshift: float, current_mode: str, 
                    sn_lines: Dict, galaxy_lines: Dict, tolerance: float = 12.0) -> List[Tuple]:
    """Find and return nearby lines for addition"""
    nearby_lines = []
    
    # Find lines within tolerance
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        rest_wavelength = line_data['wavelength']
        obs_wavelength = rest_wavelength * (1 + current_redshift)
        distance = abs(obs_wavelength - click_wavelength)
        
        if distance <= tolerance:
            # Filter by current mode using same logic as faint overlay
            origin = line_data.get('origin', '').lower()
            sn_types = line_data.get('sn_types', [])
            category = line_data.get('category', '')
            
            is_sn_line = (origin == 'sn' or 'supernova' in origin or bool(sn_types) or 
                         category in ['hydrogen', 'helium', 'silicon', 'calcium', 'iron', 'oxygen'])
            is_galaxy_line = (origin == 'galaxy' or 'galactic' in origin or 
                             category in ['galaxy', 'interstellar'])
            
            mode_matches = ((current_mode == 'sn' and is_sn_line) or 
                           (current_mode == 'galaxy' and is_galaxy_line))
            
            if mode_matches:
                nearby_lines.append((line_name, line_data, distance, obs_wavelength))
    
    # Sort by distance and take closest matches
    nearby_lines.sort(key=lambda x: x[2])
    
    # Return up to 3 closest lines
    return nearby_lines[:3]


def add_lines_by_type(sn_types: List[str], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines matching specific SN types"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        line_sn_types = line_data.get('sn_types', [])
        if any(sn_type in line_sn_types for sn_type in sn_types):
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_category(category: str, current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by element category"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        if line_data.get('category') == category:
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_origin(origin: str, current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by origin (sn/galaxy)"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        if line_data.get('origin') == origin:
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_strength(strengths: List[str], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by strength"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        if line_data.get('strength') in strengths:
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_type_and_phase(sn_types: List[str], phases: List[str], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines matching specific SN types and phases"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        line_sn_types = line_data.get('sn_types', [])
        line_phase = line_data.get('phase', '')
        
        type_match = any(sn_type in line_sn_types for sn_type in sn_types)
        phase_match = line_phase in phases
        
        if type_match and (phase_match or not phases):
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_phase(phases: List[str], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by phase"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        line_phase = line_data.get('phase', '')
        if line_phase in phases:
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_name_pattern(patterns: List[str], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines matching name patterns"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        for pattern in patterns:
            if pattern in line_name:
                if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                    obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                    lines_to_add[line_name] = (obs_wavelength, line_data)
                break
    
    return lines_to_add


def add_lines_by_category_and_strength(category: str, strengths: List[str], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by category and strength"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        if (line_data.get('category') == category and 
            line_data.get('strength') in strengths):
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_category_and_phase(category: str, phases: List[str], current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by category and phase"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        if (line_data.get('category') == category and 
            line_data.get('phase') in phases):
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def add_lines_by_line_type(line_type: str, current_redshift: float, spectrum_data: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, Dict]]:
    """Add lines by emission/absorption type"""
    lines_to_add = {}
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        if line_data.get('type') == line_type:
            if is_line_in_spectrum_range(line_data, current_redshift, spectrum_data):
                obs_wavelength = line_data['wavelength'] * (1 + current_redshift)
                lines_to_add[line_name] = (obs_wavelength, line_data)
    
    return lines_to_add


def get_faint_overlay_lines(current_mode: str, current_redshift: float, spectrum_data: Dict[str, np.ndarray], 
                           sn_lines: Dict, galaxy_lines: Dict) -> Dict[str, float]:
    """Get lines for faint overlay display"""
    if not spectrum_data or 'wavelength' not in spectrum_data:
        return {}
    
    wavelength = spectrum_data['wavelength']
    min_wave, max_wave = min(wavelength), max(wavelength)
    
    faint_lines = {}
    
    # Draw all lines in current mode very faintly
    for line_name, line_data in SUPERNOVA_EMISSION_LINES.items():
        # Skip lines already selected
        if line_name in sn_lines or line_name in galaxy_lines:
            continue
        
        # Filter by current mode
        origin = line_data.get('origin', '').lower()
        sn_types = line_data.get('sn_types', [])
        category = line_data.get('category', '')
        
        is_sn_line = (origin == 'sn' or 'supernova' in origin or bool(sn_types) or 
                     category in ['hydrogen', 'helium', 'silicon', 'calcium', 'iron', 'oxygen'])
        is_galaxy_line = (origin == 'galaxy' or 'galactic' in origin or 
                         category in ['galaxy', 'interstellar'])
        
        mode_matches = ((current_mode == 'sn' and is_sn_line) or 
                       (current_mode == 'galaxy' and is_galaxy_line))
        
        if not mode_matches:
            continue
        
        # Calculate observed wavelength
        rest_wavelength = line_data.get('wavelength', 0)
        if rest_wavelength <= 0:
            continue
        
        obs_wavelength = rest_wavelength * (1 + current_redshift)
        
        # Only show lines within spectrum range
        if min_wave <= obs_wavelength <= max_wave:
            faint_lines[line_name] = obs_wavelength
    
    return faint_lines 