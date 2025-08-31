"""
Unit tests for req-updater package.

This module contains comprehensive tests for the RequirementsUpdater class
and CLI functionality.
"""

import os
import tempfile
import pytest
from pathlib import Path

from req_updater.updater import RequirementsUpdater


class TestRequirementsUpdater:
    """Test cases for the RequirementsUpdater class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create a sample requirements file
        self.requirements_file = self.temp_path / "requirements.txt"
        self.requirements_file.write_text("requests\ndjango>=3.0\npytest==7.0.0\n")
        
        self.venv_path = self.temp_path / "test_venv"
        
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        self.temp_dir.cleanup()
        
    def test_init_default_paths(self):
        """Test initialization with default paths."""
        updater = RequirementsUpdater()
        assert updater.requirements_path.name == "requirements.txt"
        assert updater.venv_path.name == "venv"
        
    def test_init_custom_paths(self):
        """Test initialization with custom paths."""
        updater = RequirementsUpdater(
            requirements_path=str(self.requirements_file),
            venv_path=str(self.venv_path)
        )
        assert updater.requirements_path == self.requirements_file
        assert updater.venv_path == self.venv_path
        
    def test_validate_requirements_file_exists(self):
        """Test validation of existing requirements file."""
        updater = RequirementsUpdater(str(self.requirements_file))
        updater._validate_requirements_file()  # Should not raise
        
    def test_validate_requirements_file_not_exists(self):
        """Test validation with non-existent requirements file."""
        non_existent = self.temp_path / "nonexistent.txt"
        updater = RequirementsUpdater(str(non_existent))
        
        with pytest.raises(FileNotFoundError):
            updater._validate_requirements_file()
            
    def test_parse_requirements(self):
        """Test parsing of requirements file."""
        updater = RequirementsUpdater(str(self.requirements_file))
        packages = updater._parse_requirements()
        
        expected_packages = ["requests", "django", "pytest"]
        assert sorted(packages) == sorted(expected_packages)
        
    def test_parse_requirements_empty_file(self):
        """Test parsing empty requirements file."""
        empty_file = self.temp_path / "empty.txt"
        empty_file.write_text("")
        
        updater = RequirementsUpdater(str(empty_file))
        
        with pytest.raises(ValueError, match="Requirements file is empty"):
            updater._parse_requirements()
            
    def test_parse_requirements_with_comments(self):
        """Test parsing requirements file with comments and empty lines."""
        content = """# This is a comment
requests
# Another comment
django>=3.0

pytest==7.0.0
"""
        self.requirements_file.write_text(content)
        
        updater = RequirementsUpdater(str(self.requirements_file))
        packages = updater._parse_requirements()
        
        expected_packages = ["requests", "django", "pytest"]
        assert sorted(packages) == sorted(expected_packages)
        
    def test_get_pip_path_windows(self):
        """Test getting pip path on Windows."""
        # Mock os.name to simulate Windows
        original_name = os.name
        os.name = 'nt'
        
        try:
            updater = RequirementsUpdater(venv_path=str(self.venv_path))
            pip_path = updater._get_pip_path()
            assert "Scripts\\pip.exe" in pip_path
        finally:
            os.name = original_name
            
    def test_get_pip_path_unix(self):
        """Test getting pip path on Unix-like systems."""
        # Mock os.name to simulate Unix
        original_name = os.name
        os.name = 'posix'
        
        try:
            updater = RequirementsUpdater(venv_path=str(self.venv_path))
            pip_path = updater._get_pip_path()
            assert "bin/pip" in pip_path
        finally:
            os.name = original_name


class TestCLI:
    """Test cases for CLI functionality."""
    
    def test_cli_help(self):
        """Test CLI help output."""
        from req_updater.__main__ import create_parser
        
        parser = create_parser()
        help_text = parser.format_help()
        
        assert "req-updater" in help_text
        assert "requirements.txt" in help_text
        assert "--verbose" in help_text


if __name__ == "__main__":
    pytest.main([__file__])