"""
Command-line interface for req-updater package.

This module provides the main entry point for the req-updater CLI tool.
"""

import argparse
import sys
from pathlib import Path

from .updater import RequirementsUpdater


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the CLI.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog='req-updater',
        description='Automatically update package versions in requirements.txt files',
        epilog='Examples:\n'
               '  req-updater                    # Update requirements.txt in current directory\n'
               '  req-updater -r dev.txt         # Update dev.txt instead\n'
               '  req-updater -v                 # Verbose output\n'
               '  req-updater --venv .env        # Use custom virtual environment path',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-r', '--requirements',
        default='requirements.txt',
        help='Path to requirements file (default: requirements.txt)'
    )
    
    parser.add_argument(
        '--venv',
        help='Path to virtual environment directory (default: venv)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for debugging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove the virtual environment after updating'
    )
    
    return parser


def validate_paths(requirements_path: str, venv_path: str | None) -> None:
    """
    Validate that provided paths are valid.
    
    Args:
        requirements_path (str): Path to requirements file.
        venv_path (str | None): Path to virtual environment directory. None means auto-detect.
        
    Raises:
        SystemExit: If paths are invalid.
    """
    requirements_file = Path(requirements_path)
    
    if not requirements_file.exists():
        print(f"Error: Requirements file '{requirements_path}' not found", file=sys.stderr)
        sys.exit(1)
        
    if requirements_file.is_dir():
        print(f"Error: '{requirements_path}' is a directory, not a file", file=sys.stderr)
        sys.exit(1)
    
    # Only validate venv_path if explicitly provided
    if venv_path is not None:
        venv_dir = Path(venv_path)
        if venv_dir.exists() and not venv_dir.is_dir():
            print(f"Error: Virtual environment path '{venv_path}' is not a directory", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """
    Main entry point for the CLI.
    
    This function parses command-line arguments and orchestrates the requirements update process.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Validate paths
        validate_paths(args.requirements, args.venv)

        # Create updater instance
        updater = RequirementsUpdater(
            requirements_path=args.requirements,
            venv_path=args.venv
        )
        
        # Run the update process
        updater.run(verbose=args.verbose)
        
        # Cleanup if requested
        if args.cleanup:
            updater.cleanup_venv()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()