# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## \[Unreleased\]

## \[0.1.3\] - 2025-09-01

### Features

- Complete Python list API implementation with all standard list methods
- Comprehensive type safety with improved error handling
- Context manager support for automatic resource cleanup
- Professional warning system for memory-intensive operations

### Improvements

- Updated comprehensive usage example to use smaller dataset to avoid memory warnings
- Improved CLI help text for clearer user guidance
- Enhanced test coverage to 94% with comprehensive edge case testing

### Bug Fixes

- Resolved memory warning issues in example usage
- Fixed CLI example command to run without performance warnings
- Improved error handling in destructor and edge cases

### Development & Testing

- Added 152+ comprehensive test cases across all functionality
- Improved code coverage from 78% to 94%
- Enhanced development workflow with better testing infrastructure

## \[0.1.2\] - 2025-08-31

### Documentation

- Added Read the Docs configuration (.readthedocs.yaml)
- Created comprehensive Sphinx documentation structure
- Added API reference documentation with autodoc
- Created quickstart guide and examples documentation
- Updated documentation with PyPI badges and links
- Improved README with status badges and package information
- Updated project URLs to use Read the Docs for documentation

### Infrastructure

- Updated GitHub Actions to latest versions (upload-artifact v4, download-artifact v4, setup-python v5)
- Fixed deprecation warnings in CI/CD pipeline

## \[0.1.1\] - 2025-08-31

### CI/CD

- GitHub Actions workflow fixes for PyPI publishing

## \[0.1.0\] - 2025-08-31

### Added

- **Initial Project Release**

  - Complete `paged_list` package with disk-backed list implementation
  - Memory-efficient chunked data storage with automatic disk overflow
  - List-like interface supporting indexing, slicing, and iteration
  - Parallel processing with built-in map and serialization functions
  - Type safety with comprehensive type hints for dictionary handling
  - Context manager support for automatic cleanup

- **Development Infrastructure**

  - Modern Python packaging with `pyproject.toml`
  - Support for Python 3.9-3.13 with compatibility testing
  - Comprehensive test suite with 69 tests and 77% coverage
  - Pre-commit hooks for automatic code formatting (Black, isort, mdformat)
  - Cross-platform line ending normalization
  - CI/CD workflows for automated testing

- **Documentation & Examples**

  - Complete README with installation and usage instructions
  - Contributing guidelines and development setup
  - Example scripts demonstrating core functionality
  - Tox configuration for multi-version testing

- **Quality Assurance**

  - Automated testing across multiple Python versions
  - Code formatting and import organization
  - Markdown formatting and documentation standards
  - Git attributes for consistent cross-platform development
