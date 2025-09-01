# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## \[Unreleased\]

## \[1.0.0\] - 2025-08-30

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
