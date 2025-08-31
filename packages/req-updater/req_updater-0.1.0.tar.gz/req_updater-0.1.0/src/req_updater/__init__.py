"""
req-updater: Automatically update package versions in requirements.txt files.

This package provides tools for automatically updating Python package dependencies
in requirements.txt files by installing the latest versions and regenerating
the requirements file with exact versions.

Example:
    >>> from req_updater import RequirementsUpdater
    >>> updater = RequirementsUpdater()
    >>> updater.run()
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .updater import RequirementsUpdater

__all__ = ['RequirementsUpdater']