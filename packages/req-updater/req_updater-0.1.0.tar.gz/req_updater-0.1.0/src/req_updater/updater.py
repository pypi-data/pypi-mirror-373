"""
Requirements Updater - Automatically update package versions in requirements.txt files.

This module provides the RequirementsUpdater class for managing and updating
Python package dependencies in requirements.txt files.
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Optional


class RequirementsUpdater:
    """
    A class to automatically update package versions in requirements.txt files.
    
    This class handles reading requirements files, managing virtual environments,
    installing latest package versions, and generating updated requirements files.
    """
    
    def __init__(self, requirements_path: str = 'requirements.txt', venv_path: Optional[str] = None):
        """
        Initialize the RequirementsUpdater.
        
        Args:
            requirements_path (str): Path to the requirements.txt file.
            venv_path (str, optional): Path to the virtual environment directory.
                                       If None, checks for existing 'venv' or '.venv' directories,
                                       otherwise creates '.venv'.
        """
        self.requirements_path = Path(requirements_path)
        
        if venv_path:
            self.venv_path = Path(venv_path)
        else:
            # Check for existing virtual environments in priority order
            venv_dir = Path('venv')
            dot_venv_dir = Path('.venv')
            
            if venv_dir.exists() and venv_dir.is_dir():
                self.venv_path = venv_dir
            elif dot_venv_dir.exists() and dot_venv_dir.is_dir():
                self.venv_path = dot_venv_dir
            else:
                # Create new .venv if neither exists
                self.venv_path = dot_venv_dir
                
        self.verbose = False
        
    def run(self, verbose: bool = False) -> None:
        """
        Run the complete requirements update process.
        
        Args:
            verbose (bool): Enable verbose output for debugging.
        """
        self.verbose = verbose
        
        try:
            print("Starting requirements update process...")
            
            self._validate_requirements_file()
            packages = self._parse_requirements()
            
            if not packages:
                print("No packages found in requirements.txt")
                return
                
            self._setup_venv()
            self._install_packages(packages)
            self._generate_new_requirements()
            
            print("Successfully updated requirements.txt")
            
        except Exception as e:
            print(f"Error during update process: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            raise
            
    def _validate_requirements_file(self) -> None:
        """
        Validate that the requirements file exists and is readable.
        
        Raises:
            FileNotFoundError: If the requirements file doesn't exist.
            PermissionError: If the requirements file isn't readable.
        """
        if not self.requirements_path.exists():
            raise FileNotFoundError(f"{self.requirements_path} not found")
        
        if not self.requirements_path.is_file():
            raise ValueError(f"{self.requirements_path} is not a file")
            
        if not os.access(self.requirements_path, os.R_OK):
            raise PermissionError(f"Cannot read {self.requirements_path}")
            
        if self.verbose:
            print(f"Validated requirements file: {self.requirements_path}")
            
    def _parse_requirements(self) -> List[str]:
        """
        Parse the requirements file and extract package names without version specifiers.
        
        Returns:
            List[str]: List of package names without version specifiers.
            
        Raises:
            ValueError: If the requirements file is empty or malformed.
        """
        print("Parsing requirements...")
        
        try:
            with open(self.requirements_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                raise ValueError("Requirements file is empty")
                
            packages = []
            for line in content.splitlines():
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Handle editable installs (-e flag)
                if line.startswith('-e '):
                    package = line[3:].strip()
                else:
                    # Remove version specifiers and extras
                    package = re.sub(r'[=<>!~].*$', '', line.strip())
                    package = re.sub(r'\[.*\]', '', package)  # Remove extras like package[extra]
                    
                if package:
                    packages.append(package.strip())
                    
            if self.verbose:
                print(f"Found {len(packages)} packages: {', '.join(packages)}")
                
            return packages
            
        except UnicodeDecodeError:
            raise ValueError("Requirements file contains invalid UTF-8 characters")
            
    def _setup_venv(self) -> None:
        """
        Set up a virtual environment for package installation.
        
        Uses existing venv or .venv directory if found, otherwise creates new .venv.
        
        Raises:
            RuntimeError: If virtual environment creation fails.
        """
        print("Setting up virtual environment...")
        
        try:
            if self.venv_path.exists():
                if self.verbose:
                    print(f"Using existing virtual environment: {self.venv_path}")
                return
                
            cmd = [sys.executable, '-m', 'venv', str(self.venv_path)]
            
            if self.verbose:
                print(f"Creating new virtual environment: {self.venv_path}")
                print(f"Running: {' '.join(cmd)}")
                
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if self.verbose and result.stdout:
                print(result.stdout)
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create virtual environment: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Python executable not found for virtual environment creation")
            
    def _get_pip_path(self) -> str:
        """
        Get the correct pip executable path based on the operating system.
        
        Returns:
            str: Path to the pip executable in the virtual environment.
        """
        if os.name == 'nt':  # Windows
            pip_path = self.venv_path / 'Scripts' / 'pip.exe'
        else:  # Unix-like systems
            pip_path = self.venv_path / 'bin' / 'pip'
            
        if not pip_path.exists():
            raise RuntimeError(f"pip executable not found at: {pip_path}")
            
        return str(pip_path)
        
    def _get_python_path(self) -> str:
        """
        Get the correct Python executable path based on the operating system.
        
        Returns:
            str: Path to the Python executable in the virtual environment.
        """
        if os.name == 'nt':  # Windows
            python_path = self.venv_path / 'Scripts' / 'python.exe'
        else:  # Unix-like systems
            python_path = self.venv_path / 'bin' / 'python'
            
        if not python_path.exists():
            raise RuntimeError(f"Python executable not found at: {python_path}")
            
        return str(python_path)
        
    def _install_packages(self, packages: List[str]) -> None:
        """
        Install the latest versions of specified packages in the virtual environment.
        
        Args:
            packages (List[str]): List of package names to install.
            
        Raises:
            RuntimeError: If package installation fails.
        """
        if not packages:
            print("No packages to install")
            return
            
        print("Installing latest package versions...")
        
        try:
            pip_path = self._get_pip_path()
            cmd = [pip_path, 'install', '--upgrade'] + packages
            
            if self.verbose:
                print(f"Running: {' '.join(cmd)}")
                
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if self.verbose and result.stdout:
                print(result.stdout)
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install packages: {e.stderr}"
            if self.verbose and e.stdout:
                error_msg += f"\nOutput: {e.stdout}"
            raise RuntimeError(error_msg)
            
    def _generate_new_requirements(self) -> None:
        """
        Generate a new requirements.txt file with exact package versions.
        
        Uses pip freeze to get the exact versions of all installed packages
        and writes them to the requirements.txt file.
        
        Raises:
            RuntimeError: If requirements generation fails.
        """
        print("Generating updated requirements...")
        
        try:
            pip_path = self._get_pip_path()
            cmd = [pip_path, 'freeze']
            
            if self.verbose:
                print(f"Running: {' '.join(cmd)}")
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                raise RuntimeError("pip freeze returned empty output")
                
            # Backup original requirements file
            backup_path = self.requirements_path.with_suffix('.txt.backup')
            try:
                self.requirements_path.rename(backup_path)
                if self.verbose:
                    print(f"Backed up original requirements to: {backup_path}")
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not create backup: {e}")
                
            # Write new requirements
            with open(self.requirements_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
                
            if self.verbose:
                print(f"Updated requirements written to: {self.requirements_path}")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to generate requirements: {e.stderr}")
        except IOError as e:
            raise RuntimeError(f"Failed to write requirements file: {e}")
            
    def get_installed_versions(self) -> dict:
        """
        Get the currently installed package versions from the virtual environment.
        
        Returns:
            dict: Dictionary mapping package names to their versions.
            
        Raises:
            RuntimeError: If getting package versions fails.
        """
        try:
            pip_path = self._get_pip_path()
            cmd = [pip_path, 'freeze']
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            versions = {}
            for line in result.stdout.splitlines():
                if '==' in line:
                    package, version = line.split('==', 1)
                    versions[package.strip()] = version.strip()
                    
            return versions
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get installed versions: {e.stderr}")
            
    def cleanup_venv(self) -> None:
        """
        Remove the virtual environment directory.
        
        Useful for cleaning up after testing or when switching environments.
        """
        if self.venv_path.exists():
            import shutil
            shutil.rmtree(self.venv_path)
            print(f"Removed virtual environment: {self.venv_path}")
        else:
            print("Virtual environment does not exist")