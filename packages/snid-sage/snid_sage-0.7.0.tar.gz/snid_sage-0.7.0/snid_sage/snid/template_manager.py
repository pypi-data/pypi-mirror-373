#!/usr/bin/env python
"""
Template Manager for SNID.

Command-line tool to manage SNID template libraries.
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any, Optional
import glob
import numpy as np
import matplotlib.pyplot as plt

from snid_sage.snid import __version__
from snid_sage.snid.io import (
    read_spectrum, create_template_library, add_template, 
    remove_template, get_template_info, merge_template_libraries,
    read_template
)
from snid_sage.snid.preprocessing import log_rebin, flatten_spectrum

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('template_manager')

def list_templates(args):
    """List templates in a library."""
    library_path = args.library
    
    # Check if library exists
    if not os.path.exists(library_path):
        logger.error(f"Template library not found: {library_path}")
        return 1
    
    # Get template info
    info = get_template_info(library_path)
    
    # Print summary
    print(f"\nTemplate Library: {info.get('name', os.path.basename(library_path))}")
    print(f"Path: {info['path']}")
    print(f"Total templates: {info['total']}")
    
    # Print type counts
    if info['types']:
        print("\nTemplate types:")
        for t, count in sorted(info['types'].items()):
            print(f"  {t}: {count}")
    
    # Print template list if requested
    if args.verbose:
        print("\nTemplates:")
        for template in sorted(info['templates'], key=lambda x: x['name']):
            age_str = f", Age: {template['age']:.1f}" if template['age'] is not None else ""
            print(f"  {template['name']} ({template['type']}/{template['subtype']}{age_str})")
    
    return 0

def create_library(args):
    """Create a new template library."""
    # Create library
    library_path = create_template_library(args.output_dir, args.name)
    
    print(f"\nCreated template library:")
    print(f"  Name: {args.name}")
    print(f"  Path: {library_path}")
    
    return 0

def add_templates(args):
    """Add templates to a library."""
    library_path = args.library
    
    # Check if library exists
    if not os.path.exists(library_path):
        if args.create:
            # Create library if requested
            library_path = create_template_library(
                os.path.dirname(library_path) if os.path.dirname(library_path) else ".",
                os.path.basename(library_path)
            )
            logger.info(f"Created new template library: {library_path}")
        else:
            logger.error(f"Template library not found: {library_path}")
            return 1
    
    # Get list of files to add
    files_to_add = []
    for pattern in args.files:
        matched_files = glob.glob(pattern)
        if not matched_files:
            logger.warning(f"No files match pattern: {pattern}")
        files_to_add.extend(matched_files)
    
    if not files_to_add:
        logger.error("No files to add")
        return 1
    
    # Add templates
    added_count = 0
    for file_path in files_to_add:
        try:
            # Parse type, subtype, age from filename if not specified
            basename = os.path.basename(file_path)
            name_parts = os.path.splitext(basename)[0].split('_')
            
            template_info = {
                'name': name_parts[0],
                'type': args.type if args.type else (name_parts[1] if len(name_parts) > 1 else "Unknown"),
                'subtype': args.subtype if args.subtype else (name_parts[2] if len(name_parts) > 2 else "Unknown"),
                'flatten': not args.no_flatten
            }
            
            if args.age is not None:
                template_info['age'] = args.age
            elif len(name_parts) > 3:
                try:
                    template_info['age'] = float(name_parts[3])
                except ValueError:
                    pass
            
            # Add template
            template_file = add_template(
                library_path, 
                file_path, 
                template_info,
                force_rebin=args.force_rebin
            )
            
            logger.info(f"Added template: {os.path.basename(template_file)}")
            added_count += 1
            
        except Exception as e:
            logger.error(f"Error adding template {file_path}: {e}")
    
    print(f"\nAdded {added_count} templates to {library_path}")
    
    return 0

def remove_templates(args):
    """Remove templates from a library."""
    library_path = args.library
    
    # Check if library exists
    if not os.path.exists(library_path):
        logger.error(f"Template library not found: {library_path}")
        return 1
    
    # Get templates to remove
    removed_count = 0
    for template_name in args.templates:
        try:
            # Remove template
            success = remove_template(library_path, template_name)
            
            if success:
                logger.info(f"Removed template: {template_name}")
                removed_count += 1
            else:
                logger.warning(f"Template not found: {template_name}")
                
        except Exception as e:
            logger.error(f"Error removing template {template_name}: {e}")
    
    print(f"\nRemoved {removed_count} templates from {library_path}")
    
    return 0

def merge_libraries(args):
    """Merge multiple template libraries."""
    # Check if libraries exist
    for lib_path in args.libraries:
        if not os.path.exists(lib_path):
            logger.error(f"Template library not found: {lib_path}")
            return 1
    
    # Merge libraries
    merged_path = merge_template_libraries(args.output_dir, args.libraries, args.name)
    
    # Get info about merged library
    info = get_template_info(merged_path)
    
    print(f"\nMerged {len(args.libraries)} libraries into {merged_path}")
    print(f"Total templates: {info['total']}")
    
    return 0

def visualize_templates(args):
    """Visualize templates in a library."""
    library_path = args.library
    
    # Check if library exists
    if not os.path.exists(library_path):
        logger.error(f"Template library not found: {library_path}")
        return 1
    
    # Get template info
    info = get_template_info(library_path)
    
    # Get templates to visualize
    template_files = []
    if args.templates:
        for template_name in args.templates:
            template_file = os.path.join(library_path, f"{template_name}.lnw")
            if os.path.exists(template_file):
                template_files.append(template_file)
            else:
                logger.warning(f"Template not found: {template_name}")
    else:
        # Show all templates (or limited by type)
        for template_info in info['templates']:
            if not args.type or template_info['type'] == args.type:
                template_file = os.path.join(library_path, template_info['file'])
                template_files.append(template_file)
    
    if not template_files:
        logger.error("No templates to visualize")
        return 1
    
    # Limit number of templates to avoid overloading the plot
    max_templates = 10
    if len(template_files) > max_templates:
        logger.warning(f"Too many templates to display. Showing first {max_templates}.")
        template_files = template_files[:max_templates]
    
    # Create plot
    plt.figure(figsize=(12, 8))
    
    for i, template_file in enumerate(template_files):
        try:
            # Read template
            template = read_template(template_file)
            
            # Plot template
            plt.plot(template['wave'], template['flux'] + i*0.5,  # Offset for visibility
                     label=f"{template['name']} ({template.get('type', 'Unknown')})")
            
        except Exception as e:
            logger.error(f"Error visualizing template {template_file}: {e}")
    
    plt.xlabel('Log Wavelength')
    plt.ylabel('Normalized Flux (offset for visibility)')
    plt.title('SNID Templates')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    
    if args.output:
        plt.savefig(args.output, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {args.output}")
    else:
        plt.show()
    
    return 0

def convert_spectrum(args):
    """Convert a regular spectrum to .lnw format."""
    # Check if input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Read spectrum
    try:
        wave, flux = read_spectrum(args.input)
        
        # Flatten if requested (do this before log rebinning)
        if not args.no_flatten:
            # flatten_spectrum now handles both flattening and log rebinning in correct order
            flattened_result = flatten_spectrum(
                wave, flux,
                apodize_percent=5.0,
                median_filter_type="none", 
                median_filter_value=0.0
            )
            log_wave = flattened_result['wave']
            log_flux = flattened_result['flux']
        else:
            # If not flattening, just do log rebinning
            log_wave, log_flux = log_rebin(wave, flux, num_points=args.num_points)
        
        # Create header info
        header_info = {}
        if args.type:
            header_info['Type'] = args.type
        if args.subtype:
            header_info['Subtype'] = args.subtype
        if args.age is not None:
            header_info['Age'] = str(args.age)
        
        # Determine output filename
        if args.output:
            output_file = args.output
        else:
            basename = os.path.splitext(os.path.basename(args.input))[0]
            output_file = f"{basename}.lnw"
        
        # Save as .lnw file
        from snid_sage.snid.io import save_template
        save_template(log_wave, log_flux, output_file, header_info)
        
        print(f"Converted {args.input} to {output_file}")
        
    except Exception as e:
        logger.error(f"Error converting spectrum: {e}")
        return 1
    
    return 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="SNID Template Manager",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--version', action='version', version=f'SNID Python {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List templates command
    list_parser = subparsers.add_parser('list', help='List templates in a library')
    list_parser.add_argument('library', help='Path to template library')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
    
    # Create library command
    create_parser = subparsers.add_parser('create', help='Create a new template library')
    create_parser.add_argument('name', help='Name of the template library')
    create_parser.add_argument('-o', '--output-dir', help='Output directory', default='.')
    
    # Add templates command
    add_parser = subparsers.add_parser('add', help='Add templates to a library')
    add_parser.add_argument('library', help='Path to template library')
    add_parser.add_argument('files', nargs='+', help='Files to add as templates (supports wildcards)')
    add_parser.add_argument('-t', '--type', help='SN type for the templates')
    add_parser.add_argument('-s', '--subtype', help='SN subtype for the templates')
    add_parser.add_argument('-a', '--age', type=float, help='SN age in days')
    add_parser.add_argument('--no-flatten', action='store_true', help='Do not flatten the spectra')
    add_parser.add_argument('--force-rebin', action='store_true', help='Force rebinning even for .lnw files')
    add_parser.add_argument('--create', action='store_true', help='Create library if it does not exist')
    
    # Remove templates command
    remove_parser = subparsers.add_parser('remove', help='Remove templates from a library')
    remove_parser.add_argument('library', help='Path to template library')
    remove_parser.add_argument('templates', nargs='+', help='Names of templates to remove')
    
    # Merge libraries command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple template libraries')
    merge_parser.add_argument('libraries', nargs='+', help='Paths to template libraries to merge')
    merge_parser.add_argument('-n', '--name', help='Name for the merged library', default='Merged')
    merge_parser.add_argument('-o', '--output-dir', help='Output directory', default='.')
    
    # Visualize templates command
    visualize_parser = subparsers.add_parser('visualize', help='Visualize templates in a library')
    visualize_parser.add_argument('library', help='Path to template library')
    visualize_parser.add_argument('-t', '--templates', nargs='+', help='Names of templates to visualize')
    visualize_parser.add_argument('--type', help='Only show templates of this type')
    visualize_parser.add_argument('-o', '--output', help='Save plot to file instead of displaying')
    
    # Convert spectrum command
    convert_parser = subparsers.add_parser('convert', help='Convert a spectrum to .lnw format')
    convert_parser.add_argument('input', help='Input spectrum file')
    convert_parser.add_argument('-o', '--output', help='Output file name')
    convert_parser.add_argument('-t', '--type', help='SN type')
    convert_parser.add_argument('-s', '--subtype', help='SN subtype')
    convert_parser.add_argument('-a', '--age', type=float, help='SN age in days')
    convert_parser.add_argument('-n', '--num-points', type=int, default=1024, help='Number of points in log grid')
    convert_parser.add_argument('-m', '--median-filter', type=int, default=101, help='Median filter width')
    convert_parser.add_argument('--no-flatten', action='store_true', help='Do not flatten the spectrum')
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'list':
        return list_templates(args)
    elif args.command == 'create':
        return create_library(args)
    elif args.command == 'add':
        return add_templates(args)
    elif args.command == 'remove':
        return remove_templates(args)
    elif args.command == 'merge':
        return merge_libraries(args)
    elif args.command == 'visualize':
        return visualize_templates(args)
    elif args.command == 'convert':
        return convert_spectrum(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main()) 