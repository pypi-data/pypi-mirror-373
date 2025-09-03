#!/usr/bin/env python3
"""
Build Unified Template FFT Storage
==================================

This script builds the unified FFT storage files for SNID templates with optimizations:
- Filters out epochs with -999.0 age (useless for analysis)
- Pre-rebins all templates to standard grid for faster processing
- Pre-computes FFTs for optimal correlation performance
- Creates type-specific H5 files for better organization

Run this once after setting up templates or when templates are updated.

Usage:
    python scripts/build_unified_storage.py [template_dir]
    
Example:
    python scripts/build_unified_storage.py templates/
    
Options:
    --force     Force rebuild even if storage is up to date
    --verbose   Enable detailed logging
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from snid_sage.snid.template_fft_storage import create_unified_storage

def setup_logging():
    """Setup logging for the build process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main build function."""
    parser = argparse.ArgumentParser(
        description='Build unified template FFT storage',
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
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_logging()
    
    logger = logging.getLogger(__name__)
    
    # Validate template directory
    template_dir = Path(args.template_dir)
    if not template_dir.exists():
        logger.error(f"Template directory does not exist: {template_dir}")
        sys.exit(1)
    
    if not template_dir.is_dir():
        logger.error(f"Template path is not a directory: {template_dir}")
        sys.exit(1)
    
    # Count template files
    template_files = list(template_dir.glob('*.lnw'))
    if not template_files:
        logger.error(f"No template files (*.lnw) found in: {template_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(template_files)} template files in {template_dir}")
    
    try:
        # Create unified storage
        logger.info("Creating unified template storage...")
        storage = create_unified_storage(str(template_dir), force_rebuild=args.force)
        
        # Get statistics
        stats = storage.get_storage_stats()
        
        logger.info("✅ Unified storage built successfully!")
        logger.info(f"   📊 Templates: {stats.get('total_templates', 0)}")
        
        # Calculate total storage size
        total_size_mb = 0
        if 'storage_files' in stats:
            for file_info in stats['storage_files']:
                if file_info.get('exists', False):
                    total_size_mb += file_info.get('size_mb', 0)
        
        logger.info(f"   💾 Storage size: {total_size_mb:.1f} MB")
        logger.info(f"   📋 Index file: {storage.index_file}")
        
        # Show type breakdown
        if 'storage_files' in stats:
            logger.info("   🏷️  Type breakdown:")
            for file_info in stats['storage_files']:
                if file_info.get('exists', False):
                    type_name = file_info['type']
                    count = file_info['templates']
                    size_mb = file_info.get('size_mb', 0)
                    logger.info(f"      {type_name}: {count} templates ({size_mb:.1f} MB)")
        
        # Show filtering improvements
        logger.info("")
        logger.info("🔧 Improvements in this version:")
        logger.info("   - Epochs with -999.0 age are automatically filtered out")
        logger.info("   - Templates pre-rebinned to standard grid for faster analysis")
        logger.info("   - Pre-computed FFTs stored for optimal performance")
        
        logger.info("")
        logger.info("🚀 Templates are now ready for fast analysis!")
        logger.info("   The unified storage will automatically be used by SNID SAGE.")
        
    except Exception as e:
        logger.error(f"❌ Failed to build unified storage: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 