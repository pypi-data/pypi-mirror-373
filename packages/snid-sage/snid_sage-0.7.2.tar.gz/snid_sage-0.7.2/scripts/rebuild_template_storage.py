#!/usr/bin/env python3
"""
Rebuild Template Storage - Complete H5 Generation Script
========================================================

This is the SINGLE script users need to rebuild H5 template storage files.
It consolidates all template processing functionality with these optimizations:

✅ FILTERING IMPROVEMENTS:
   - Automatically filters out epochs with -999.0 age (useless for analysis)
   - Uses first valid age for template metadata (not -999.0)

✅ DATA CORRECTIONS:
   - SN2005ek type corrected from 'US-Ic' to 'Ic'

✅ PERFORMANCE OPTIMIZATIONS:
   - Pre-rebins all templates to standard grid (1024 points, 2500-10000Å)
   - Pre-computes FFTs for fast correlation
   - Creates type-specific H5 files for better organization
   - Memory-efficient processing with progress tracking

Usage:
    python scripts/rebuild_template_storage.py [template_dir]
    
Examples:
    python scripts/rebuild_template_storage.py                    # Use default 'templates/' directory
    python scripts/rebuild_template_storage.py templates/         # Specify template directory
    python scripts/rebuild_template_storage.py --force           # Force rebuild even if up to date
    python scripts/rebuild_template_storage.py --verbose         # Detailed logging
    
Output:
    - templates_<TYPE>.hdf5 files (one per supernova type)
    - template_index.json (fast lookup index)
    
The rebuilt storage will be automatically used by SNID SAGE for faster analysis.
"""

import sys
import argparse
import logging
import time
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from snid_sage.snid.template_fft_storage import create_unified_storage

def setup_logging(verbose: bool = False):
    """Setup logging for the build process."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_template_directory(template_dir: Path) -> int:
    """Validate template directory and return number of templates found."""
    logger = logging.getLogger(__name__)
    
    if not template_dir.exists():
        logger.error(f"❌ Template directory does not exist: {template_dir}")
        return 0
    
    if not template_dir.is_dir():
        logger.error(f"❌ Template path is not a directory: {template_dir}")
        return 0
    
    # Count template files
    template_files = list(template_dir.glob('*.lnw'))
    if not template_files:
        logger.error(f"❌ No template files (*.lnw) found in: {template_dir}")
        return 0
    
    logger.info(f"📁 Found {len(template_files)} template files in {template_dir}")
    return len(template_files)

def show_improvements():
    """Show the improvements made in this version."""
    logger = logging.getLogger(__name__)
    logger.info("")
    logger.info("🔧 IMPROVEMENTS IN THIS VERSION:")
    logger.info("   ✅ Epochs with -999.0 age automatically filtered out")
    logger.info("   ✅ SN2005ek type corrected from 'US-Ic' to 'Ic'")
    logger.info("   ✅ Templates pre-rebinned to standard grid for faster analysis")
    logger.info("   ✅ Pre-computed FFTs stored for optimal performance")
    logger.info("   ✅ Type-specific H5 files for better organization")
    logger.info("   ✅ Memory-efficient processing with progress tracking")

def show_storage_stats(stats: Dict[str, Any]):
    """Display detailed storage statistics."""
    logger = logging.getLogger(__name__)
    
    total_templates = stats.get('total_templates', 0)
    logger.info(f"   📊 Total templates: {total_templates}")
    
    # Calculate total storage size and show breakdown
    total_size_mb = 0
    valid_files = 0
    
    if 'storage_files' in stats:
        logger.info("   🏷️  Type breakdown:")
        for file_info in sorted(stats['storage_files'], key=lambda x: x['type']):
            if file_info.get('exists', False):
                type_name = file_info['type']
                count = file_info['templates']
                size_mb = file_info.get('size_mb', 0)
                total_size_mb += size_mb
                valid_files += 1
                logger.info(f"      {type_name:>8}: {count:>3} templates ({size_mb:>5.1f} MB)")
        
        logger.info(f"   💾 Total storage: {total_size_mb:.1f} MB in {valid_files} files")
    
    return total_size_mb, valid_files

def main():
    """Main rebuild function."""
    parser = argparse.ArgumentParser(
        description='Rebuild template storage with filtering and optimizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'template_dir',
        nargs='?',
        default='templates',
        help='Directory containing template files (default: templates/)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force rebuild even if storage is up to date'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging with detailed progress'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default=None,
        help='Directory to write HDF5 and index files (default: same as template_dir)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Show header
    logger.info("="*60)
    logger.info("🚀 SNID SAGE - Template Storage Rebuild")
    logger.info("="*60)
    
    # Validate template directory
    template_dir = Path(args.template_dir)
    num_templates = validate_template_directory(template_dir)
    if num_templates == 0:
        sys.exit(1)
    
    # Show improvements
    show_improvements()
    
    # Start building
    logger.info("")
    logger.info("🔨 BUILDING TEMPLATE STORAGE...")
    start_time = time.time()
    
    try:
        # Create unified storage with all improvements
        storage = create_unified_storage(str(template_dir), force_rebuild=args.force, output_dir=args.output_dir)
        
        build_time = time.time() - start_time
        
        # Get and show statistics
        stats = storage.get_storage_stats()
        
        logger.info("")
        logger.info("="*60)
        logger.info("✅ TEMPLATE STORAGE BUILT SUCCESSFULLY!")
        logger.info("="*60)
        
        total_size_mb, num_files = show_storage_stats(stats)
        
        logger.info(f"   ⏱️  Build time: {build_time:.1f} seconds")
        if build_time > 0 and num_templates > 0:
            rate = num_templates / build_time
            logger.info(f"   🚀 Processing rate: {rate:.1f} templates/second")
        
        logger.info(f"   📋 Index file: {storage.index_file}")
        
        # Performance summary
        logger.info("")
        logger.info("🎯 PERFORMANCE BENEFITS:")
        logger.info("   - No rebinning needed during SNID analysis runs")
        logger.info("   - Pre-computed FFTs enable instant correlations")
        logger.info("   - Type-specific files reduce memory usage")
        logger.info("   - Filtered epochs improve analysis quality")
        
        logger.info("")
        logger.info("🚀 READY FOR ANALYSIS!")
        logger.info("   The rebuilt storage will be automatically used by SNID SAGE.")
        logger.info("   You can now run spectrum analysis with optimal performance.")
        
        return 0
        
    except Exception as e:
        build_time = time.time() - start_time
        logger.error("")
        logger.error("="*60)
        logger.error("❌ TEMPLATE STORAGE BUILD FAILED!")
        logger.error("="*60)
        logger.error(f"   Error: {e}")
        logger.error(f"   Build time: {build_time:.1f} seconds")
        
        if args.verbose:
            logger.error("")
            logger.error("Full error traceback:")
            import traceback
            traceback.print_exc()
        else:
            logger.error("")
            logger.error("💡 Use --verbose flag for detailed error information")
        
        return 1

if __name__ == '__main__':
    sys.exit(main()) 