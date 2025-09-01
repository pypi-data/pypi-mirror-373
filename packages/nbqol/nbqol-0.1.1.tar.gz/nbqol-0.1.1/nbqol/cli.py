#!/usr/bin/env python3
"""
Command-line interface for NB-QOL.
"""

import argparse
import sys
import os
from pathlib import Path

def print_version():
    """Print the package version."""
    from nbqol import __version__
    print(f"NB-QOL version {__version__}")

def device_info():
    """Show CUDA device information."""
    try:
        from nbqol.devices import cuda_device_report
        cuda_device_report()
    except ImportError:
        print("CUDA tools not available. Make sure required dependencies are installed.")
        return 1
    return 0

def style_notebook():
    """Apply styling to the current notebook environment."""
    try:
        from nbqol.stylizer import auto_style
        auto_style()
        print("Styling applied successfully.")
    except ImportError:
        print("Styling not available. This command is intended to be run in a Jupyter environment.")
        return 1
    return 0

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="NB-QOL: Quality-of-life toolkit for Jupyter notebooks")
    
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Device info command
    device_parser = subparsers.add_parser('device-info', help='Show CUDA device information')
    
    # Style command
    style_parser = subparsers.add_parser('style', help='Apply styling to the current notebook environment')
    
    args = parser.parse_args()
    
    if args.version:
        print_version()
        return 0
    
    if args.command == 'device-info':
        return device_info()
    elif args.command == 'style':
        return style_notebook()
    else:
        # If no command is provided, show help
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())