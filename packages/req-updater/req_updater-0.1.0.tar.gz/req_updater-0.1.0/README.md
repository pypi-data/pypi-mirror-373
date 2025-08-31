# req-updater

Automatically update package versions in requirements.txt files with the latest available versions from PyPI.

## Overview

req-updater is a Python package that simplifies dependency management by automatically:
- Reading and parsing requirements.txt files
- Removing version specifiers to get the latest versions
- Creating and managing virtual environments
- Installing the latest package versions
- Generating updated requirements.txt files with exact versions
- Providing detailed progress output

## Installation

### From PyPI (when published)

```bash
pip install req-updater
```

### From Source

```bash
git clone https://github.com/Sohail342/req-updater.git
cd req-updater
pip install -e .
```

## Quick Start

```bash
# Basic usage - update requirements.txt in current directory
req-updater

# Update a specific requirements file
req-updater -r dev-requirements.txt

# Use a custom virtual environment path
req-updater --venv .myenv

# Enable verbose output for debugging
req-updater -v

# Remove virtual environment after updating
req-updater --cleanup
```

## Features

- **Automatic Updates**: Updates all packages to their latest compatible versions
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Virtual Environment Management**: Automatically creates and manages virtual environments
- **Clean Requirements**: Generates clean requirements.txt with exact versions
- **Error Handling**: Comprehensive error handling with helpful messages
- **Verbose Mode**: Detailed progress output for debugging
- **Backup Creation**: Automatically creates backups of original requirements files
- **CLI Interface**: Easy-to-use command-line interface with help documentation

## Command-Line Interface

### Usage

```
req-updater [OPTIONS]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `-r, --requirements` | Path to requirements file | `-r dev.txt` |
| `--venv` | Custom virtual environment path | `--venv .env` |
| `-v, --verbose` | Enable verbose output | `-v` |
| `--cleanup` | Remove virtual environment after update | `--cleanup` |
| `--version` | Show version information | `--version` |
| `-h, --help` | Show help message | `-h` |

### Examples

```bash
# Update requirements.txt in current directory
req-updater

# Update specific file with verbose output
req-updater -r requirements-dev.txt -v

# Use custom virtual environment
req-updater --venv .venv

# Update and cleanup virtual environment
req-updater --cleanup
```

## Python API

You can also use req-updater programmatically:

```python
from req_updater import RequirementsUpdater

# Basic usage
updater = RequirementsUpdater()
updater.run()

# Custom paths
updater = RequirementsUpdater(
    requirements_path='dev-requirements.txt',
    venv_path='.myenv'
)
updater.run(verbose=True)

# Get installed versions
versions = updater.get_installed_versions()
print(versions)

# Cleanup virtual environment
updater.cleanup_venv()
```

## Requirements

- Python 3.7 or higher
- setuptools 42 or higher
- packaging library (automatically installed)

## Development

### Setting up Development Environment

```bash
git clone https://github.com/Sohail342/req-updater.git
cd req-updater
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Building Package

```bash
python -m build
```

## How It Works

1. **Parse Requirements**: Reads your requirements.txt file and extracts package names
2. **Create Environment**: Sets up a new virtual environment (or uses existing)
3. **Install Packages**: Installs the latest versions of all packages
4. **Freeze Versions**: Uses `pip freeze` to get exact versions
5. **Update File**: Writes the updated requirements back to your file

## Error Handling

The package includes comprehensive error handling for:
- Missing requirements files
- Invalid file formats
- Network connectivity issues
- Permission errors
- Virtual environment creation failures
- Package installation failures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
- Check the [Issues](https://github.com/Sohail342/req-updater/issues) page
- Create a new issue with detailed information
- Include your operating system, Python version, and error messages

## Changelog

### 0.1.0 (Initial Release)
- Basic requirements.txt updating functionality
- Cross-platform support (Windows, Linux, macOS)
- CLI interface with argument parsing
- Virtual environment management
- Comprehensive error handling
- Verbose mode for debugging