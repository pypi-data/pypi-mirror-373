"""
Simple Template Discovery Utility
=================================

Simplified template finder for both GitHub installations and installed packages.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from snid_sage.shared.utils.logging import get_logger

logger = get_logger('simple_template_finder')


def find_templates_directory() -> Optional[Path]:
    """
    Find the templates directory for both GitHub installations and installed packages.
    
    For GitHub installations, templates are in the 'templates' directory at the project root.
    For installed packages, templates are included in the package data.
    
    Returns:
        Path to templates directory if found, None otherwise
    """
    # Strategy 1: Check if we're in an installed package using importlib.resources
    try:
        import importlib.resources as pkg_resources
        
        # For Python 3.9+ with improved traversable API
        if hasattr(pkg_resources, 'files'):
            try:
                # Try to access the templates directory within the installed package
                # The package name will be snid_sage when installed via pip
                templates_package = pkg_resources.files('snid_sage') / 'templates'
                if templates_package.exists():
                    # Convert to Path and validate
                    templates_dir = Path(str(templates_package))
                    if _validate_templates_directory(templates_dir):
                        logger.debug(f"✅ Found templates in installed package (files API): {templates_dir}")
                        return templates_dir
            except Exception as e:
                logger.debug(f"Files API with snid_sage failed: {e}")
                
            # Try alternative access methods for different Python versions
            for pkg_name in ['snid_sage', '.']:
                try:
                    templates_package = pkg_resources.files(pkg_name) / 'templates'
                    if templates_package.exists():
                        templates_dir = Path(str(templates_package))
                        if _validate_templates_directory(templates_dir):
                            logger.debug(f"✅ Found templates in package {pkg_name} (files API): {templates_dir}")
                            return templates_dir
                except Exception as e:
                    logger.debug(f"Files API with {pkg_name} failed: {e}")
        
        # Fallback for older Python versions or if files API fails
        # Try accessing package resources directly
        for pkg_structure in [
            ('snid_sage', 'templates/template_index.json'),
            ('snid_sage.templates', 'template_index.json'), 
        ]:
            try:
                pkg_name, resource_path = pkg_structure
                with pkg_resources.path(pkg_name, resource_path) as template_path:
                    if 'templates/' in resource_path:
                        templates_dir = template_path.parent
                    else:
                        templates_dir = template_path.parent
                    if _validate_templates_directory(templates_dir):
                        logger.debug(f"✅ Found templates in package {pkg_name} (path API): {templates_dir}")
                        return templates_dir
            except Exception as e:
                logger.debug(f"Path API with {pkg_structure} failed: {e}")
            
    except ImportError:
        logger.debug("importlib.resources not available")
    
    # Strategy 2: Check site-packages for installed package
    try:
        # Look for snid-sage in site-packages
        for path in sys.path:
            if 'site-packages' in path:
                site_packages = Path(path)
                
                # Check for different possible installation names
                for pkg_name in ['snid_sage', 'snid-sage', 'SNID_SAGE']:
                    pkg_dir = site_packages / pkg_name
                    if pkg_dir.exists():
                        templates_dir = pkg_dir / 'templates'
                        if _validate_templates_directory(templates_dir):
                            logger.debug(f"✅ Found templates in site-packages: {templates_dir}")
                            return templates_dir
    except Exception as e:
        logger.debug(f"Site-packages search failed: {e}")
    
    # Strategy 3: Check current working directory
    cwd = Path.cwd()
    templates_dir = cwd / 'templates'
    if _validate_templates_directory(templates_dir):
        logger.debug(f"✅ Found templates in current directory: {templates_dir}")
        return templates_dir
    
    # Strategy 4: Check relative to snid_sage package in current directory
    cwd = Path.cwd()
    templates_dir = cwd / 'snid_sage' / 'templates'
    if _validate_templates_directory(templates_dir):
        logger.debug(f"✅ Found templates in current directory snid_sage package: {templates_dir}")
        return templates_dir
    
    # Strategy 5: Find project root by looking for key files
    current = Path(__file__).resolve().parent
    for _ in range(10):  # Limit search depth
        # Look for project markers
        if any((current / marker).exists() for marker in ['pyproject.toml', 'setup.py', 'README.md']):
            # Check for snid_sage package structure first
            templates_dir = current / 'snid_sage' / 'templates'
            if _validate_templates_directory(templates_dir):
                logger.debug(f"✅ Found templates in project snid_sage package: {templates_dir}")
                return templates_dir
            # Fallback to root templates directory
            templates_dir = current / 'templates'
            if _validate_templates_directory(templates_dir):
                logger.debug(f"✅ Found templates relative to project root: {templates_dir}")
                return templates_dir
        current = current.parent
        if current == current.parent:  # Reached filesystem root
            break
    
    # Strategy 6: Check relative to module location (go up directories)
    current = Path(__file__).resolve().parent
    for _ in range(10):
        # Check for snid_sage package structure
        templates_dir = current / 'snid_sage' / 'templates'
        if _validate_templates_directory(templates_dir):
            logger.debug(f"✅ Found templates in snid_sage package relative to module: {templates_dir}")
            return templates_dir
        # Check for templates directory
        templates_dir = current / 'templates'
        if _validate_templates_directory(templates_dir):
            logger.info(f"✅ Found templates relative to module: {templates_dir}")
            return templates_dir
        current = current.parent
        if current == current.parent:
            break
    
    # Strategy 7: Check common installation paths
    common_paths = [
        Path.home() / '.local' / 'lib' / 'python*' / 'site-packages' / 'snid_sage' / 'templates',
        Path.home() / '.local' / 'share' / 'snid-sage' / 'templates',
        Path('/usr/local/lib/python*/site-packages/snid_sage/templates'),
        Path('/usr/share/snid-sage/templates'),
    ]
    
    for template_path in common_paths:
        # Handle wildcards in path
        if '*' in str(template_path):
            parent = template_path.parent
            pattern = template_path.name
            try:
                for candidate in parent.glob(pattern):
                        if _validate_templates_directory(candidate):
                            logger.debug(f"✅ Found templates in common path: {candidate}")
                        return candidate
            except Exception:
                continue
        else:
            if _validate_templates_directory(template_path):
                logger.debug(f"✅ Found templates in common path: {template_path}")
                return template_path
    
    logger.warning("No valid templates directory found")
    return None


def _validate_templates_directory(templates_dir: Path) -> bool:
    """
    Validate that a directory contains valid SNID templates.
    
    OPTIMIZED: Only checks for template_index.json instead of scanning all HDF5 files
    to avoid startup delays. Full validation happens during analysis when needed.
    
    Args:
        templates_dir: Path to check
        
    Returns:
        True if directory contains valid templates
    """
    try:
        if not templates_dir.exists() or not templates_dir.is_dir():
            return False
        
        # FAST CHECK: Only look for template index file (preferred for HDF5 storage)
        index_file = templates_dir / 'template_index.json'
        if index_file.exists():
            logger.debug(f"Found template index file in {templates_dir}")
            return True
        
        # FAST FALLBACK: Quick check for any template-like files without full enumeration
        # Check if directory has potential template files without listing all
        has_hdf5 = any(templates_dir.glob('templates_*.hdf5'))
        if has_hdf5:
            logger.debug(f"Found HDF5 template files in {templates_dir}")
            return True
        
        logger.debug(f"No template files found in {templates_dir}")
        return False
        
    except Exception as e:
        logger.debug(f"Error validating templates directory {templates_dir}: {e}")
        return False


def find_templates_directory_or_raise() -> Path:
    """
    Find templates directory or raise an exception.
    
    Returns:
        Path to templates directory
        
    Raises:
        FileNotFoundError: If templates directory cannot be found
    """
    templates_dir = find_templates_directory()
    if templates_dir is None:
        raise FileNotFoundError(
            "Could not find SNID templates directory.\n"
            "For GitHub installations, ensure you have cloned the full repository:\n"
            "  git clone https://github.com/FiorenSt/SNID-SAGE.git\n"
            "For pip installations, ensure templates were included in the package.\n"
            "Templates should be in the 'snid_sage/templates/' directory."
        )
    return templates_dir


# For backward compatibility
def get_templates_directory() -> Optional[Path]:
    """Legacy function name - use find_templates_directory() instead."""
    return find_templates_directory()


def find_images_directory() -> Optional[Path]:
    """
    Find the images directory for both GitHub installations and installed packages.
    Now always prioritizes snid_sage/images/ as the canonical location.
    """
    # Strategy 1: Check if we're in an installed package using importlib.resources
    try:
        import importlib.resources as pkg_resources
        if hasattr(pkg_resources, 'files'):
            try:
                images_package = pkg_resources.files('snid_sage') / 'images'
                if images_package.exists():
                    images_dir = Path(str(images_package))
                    if _validate_images_directory(images_dir):
                        logger.info(f"✅ Found images in installed package (files API): {images_dir}")
                        return images_dir
            except Exception as e:
                logger.debug(f"Files API with snid_sage images failed: {e}")
    except ImportError:
        logger.debug("importlib.resources not available")

    # Strategy 2: Check site-packages for installed package
    try:
        for path in sys.path:
            if 'site-packages' in path:
                site_packages = Path(path)
                for pkg_name in ['snid_sage', 'snid-sage', 'SNID_SAGE']:
                    pkg_dir = site_packages / pkg_name
                    if pkg_dir.exists():
                        images_dir = pkg_dir / 'images'
                        if _validate_images_directory(images_dir):
                            logger.info(f"✅ Found images in site-packages: {images_dir}")
                            return images_dir
    except Exception as e:
        logger.debug(f"Site-packages search for images failed: {e}")

    # Strategy 3: Check snid_sage/images in current working directory
    cwd = Path.cwd()
    images_dir = cwd / 'snid_sage' / 'images'
    if _validate_images_directory(images_dir):
        logger.info(f"✅ Found images in current directory snid_sage package: {images_dir}")
        return images_dir

    # Strategy 4: Check relative to snid_sage package in current directory
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if any((current / marker).exists() for marker in ['pyproject.toml', 'setup.py', 'README.md']):
            images_dir = current / 'snid_sage' / 'images'
            if _validate_images_directory(images_dir):
                logger.info(f"✅ Found images in project snid_sage package: {images_dir}")
                return images_dir
        current = current.parent
        if current == current.parent:
            break

    # Strategy 5: Check relative to module location (go up directories)
    current = Path(__file__).resolve().parent
    for _ in range(10):
        images_dir = current / 'snid_sage' / 'images'
        if _validate_images_directory(images_dir):
            logger.info(f"✅ Found images in snid_sage package relative to module: {images_dir}")
            return images_dir
        current = current.parent
        if current == current.parent:
            break

    logger.warning("No valid images directory found")
    return None


def _validate_images_directory(images_dir: Path) -> bool:
    """
    Validate that a directory contains valid image files.
    
    Args:
        images_dir: Path to check
        
    Returns:
        True if directory contains valid images
    """
    try:
        if not images_dir.exists() or not images_dir.is_dir():
            return False

        # Check for common image files (include SVG for QSS icons)
        image_extensions = ['*.png', '*.ico', '*.icns', '*.jpg', '*.jpeg', '*.svg']
        image_files = []
        for ext in image_extensions:
            image_files.extend(list(images_dir.glob(ext)))

        if image_files:
            logger.debug(f"Found {len(image_files)} image files in {images_dir}")
            return True

        logger.debug(f"No image files found in {images_dir}")
        return False

    except Exception as e:
        logger.debug(f"Error validating images directory {images_dir}: {e}")
        return False


if __name__ == "__main__":
    logger.info("SNID Simple Template Directory Finder")
    logger.info("=" * 50)
    
    templates_dir = find_templates_directory()
    if templates_dir:
        logger.info(f"✅ Templates found: {templates_dir}")
        
        # Show what's in the directory
        hdf5_files = list(templates_dir.glob('templates_*.hdf5'))
        
        if hdf5_files:
            logger.info(f"   📁 HDF5 template files: {len(hdf5_files)}")
            for hdf5_file in hdf5_files[:5]:  # Show first 5
                logger.info(f"      - {hdf5_file.name}")
            if len(hdf5_files) > 5:
                logger.info(f"      ... and {len(hdf5_files) - 5} more")
    else:
        logger.error("❌ No templates directory found")
        logger.error("Ensure you have cloned the full SNID-SAGE repository from GitHub")
        logger.error("or that templates were included in your pip installation") 