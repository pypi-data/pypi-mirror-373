#!/usr/bin/env python3
"""
SNID SAGE Command Line Interface
================================

Main entry point for the SNID SAGE CLI application.
This provides comprehensive command-line access to SNID SAGE functionality.

Version 1.0.0 - Developed by Fiorenzo Stoppa
Based on the original Fortran SNID by Stéphane Blondin & John L. Tonry
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Import the core SNID functionality
from snid_sage.snid.snid import run_snid
import snid_sage.interfaces.cli.identify as identify_module
import snid_sage.interfaces.cli.batch as batch_module
import snid_sage.interfaces.cli.config as config_module
from snid_sage.shared.utils.logging import add_logging_arguments, configure_from_args
from snid_sage.shared.utils.logging import VerbosityLevel

# Import version
try:
    from snid_sage import __version__
except ImportError:
    __version__ = "unknown"


def _start_update_check_nonblocking() -> None:
    """Kick off a background check for a newer PyPI release and notify if found.

    Runs quickly in a background thread and is safe if offline.
    Only prints a short notice when an update is available.
    """
    try:
        # Local import to avoid any startup import cost/errors if dependencies change
        from snid_sage.shared.utils.version_checker import VersionChecker
    except Exception:
        return

    def _notify_if_update_available(info: dict) -> None:
        try:
            if info and info.get("update_available"):
                current = info.get("current_version", "unknown")
                latest = info.get("latest_version", "unknown")
                print(
                    f"Update available: {current} -> {latest}. "
                    f"Update with: pip install --upgrade snid-sage",
                    file=sys.stderr,
                )
        except Exception:
            # Never let update notifications interfere with CLI
            pass

    try:
        VersionChecker(timeout=3.0).check_for_updates_async(_notify_if_update_available)
    except Exception:
        # Silently ignore any issues with starting the check
        pass


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="SNID SAGE: SuperNova IDentification with Spectrum Analysis and Guided Enhancement",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Developed by Fiorenzo Stoppa, based on the original Fortran SNID by Stéphane Blondin & John L. Tonry"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"SNID SAGE v{__version__}"
    )
    
    # Logging options (global)
    add_logging_arguments(parser)

    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command", 
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Identify command (main SNID functionality)
    identify_parser = subparsers.add_parser(
        "identify", 
        help="Identify supernova spectrum",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    identify_module.add_arguments(identify_parser)
    
    # Batch processing commands
    batch_parser = subparsers.add_parser(
        "batch", 
        help="Batch process multiple spectra",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    batch_module.add_arguments(batch_parser)
    
    # Configuration commands
    config_parser = subparsers.add_parser(
        "config", 
        help="Manage SNID SAGE configuration",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    config_module.add_arguments(config_parser)
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = create_parser()
    
    # If no arguments provided, show help
    if not argv:
        parser.print_help()
        return 0
    
    # Special case: if first argument looks like a spectrum file,
    # treat it as the default "identify" command for convenience
    if len(argv) >= 1 and not argv[0].startswith('-') and argv[0] not in ['identify', 'batch', 'config']:
        # Implicit identify mode: sage <spectrum> [templates/]
        # Show a brief interactive tip only in verbose/debug to avoid default noise
        try:
            wants_verbose = any(f in argv for f in ['-v', '--verbose', '-d', '--debug'])
            if sys.stderr.isatty() and wants_verbose:
                print(
                    "Tip: 'sage <file>' runs 'sage identify <file>'. Use 'sage identify' for clarity.",
                    file=sys.stderr
                )
        except Exception:
            # Never let optional tips interfere with CLI behavior
            pass
        argv = ['identify'] + argv
    
    args = parser.parse_args(argv)
    
    # Configure logging once at the top-level based on global flags
    try:
        # Default CLI verbosity set to QUIET to reduce noise unless user opts-in
        configure_from_args(args, gui_mode=False, default_verbosity=VerbosityLevel.QUIET)
    except Exception:
        pass

    # Fire-and-forget update check (non-blocking). Only warns when update is available.
    _start_update_check_nonblocking()

    try:
        if args.command == "identify":
            return identify_module.main(args)
        elif args.command == "batch":
            return batch_module.main(args)
        elif args.command == "config":
            return config_module.main(args)
        else:
            parser.print_help()
            return 0
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 