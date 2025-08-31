# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Copier template** for creating multilingual online courses using Jupyter Book. The template enables educators to create interactive, internationalized documentation with support for multiple languages (default: English and Korean).

## Architecture

### Template Structure
- **Copier Configuration**: `copier.yaml` defines template variables and questions for project generation
- **Template Files**: Located in `.copier-template/` subdirectory (configured but currently empty in this instance)
- **Book Content**: Multi-language Jupyter Book structure in `book/` directory
  - `en/` - English content
  - `ko/` - Korean content
  - `_scripts/` - Build and publishing scripts
  - `_addons/` - Custom HTML/JS components for language switching and comments

### Key Components
1. **Package**: `src/hypercourse/` - Python package with CLI support
2. **Documentation**: Jupyter Book-based course materials with internationalization
3. **CI/CD**: Automated builds and releases via GitHub Actions
4. **Testing**: pytest-based test suite in `tests/`

## Common Commands

### Development Setup
```bash
make install        # Install virtual environment with uv and pre-commit hooks
uv sync            # Sync dependencies
```

### Code Quality
```bash
make check         # Run all code quality checks (lint, type check, dependency check)
uv run ruff check src/  # Run linter only
uv run ruff format src/  # Format code with ruff
uv run mypy --config-file pyproject.toml src/   # Run type checking only
uv run deptry .    # Check for obsolete dependencies
```

### Testing
```bash
make test          # Run all tests with coverage
uv run pytest      # Run tests without coverage
uv run pytest tests/hypercourse/test_cli.py  # Run specific test file
uv run tox-uv      # Test across Python 3.9-3.13
```

### Building & Publishing
```bash
make build         # Build wheel file using hatchling
make publish       # Publish to PyPI (requires credentials)
uvx twine upload dist/*  # Manual upload to PyPI
```

### Book Building
```bash
# Build the book (both languages)
poe book-build

# Build with all outputs
poe book-build-all

# Test documentation build
make docs-test
```

### Template Operations
```bash
# Initialize a new project from this template
make init-project  # Warning: only run once on new projects

# Reinitialize/update template (preserves .copierignore files)
make reinit-project

# Test template generation
make test-init-project  # Creates in tmp/ directory
```

### Utilities
```bash
# Clean build artifacts
poe clean

# Show available make targets
make help

# Lock dependencies
uv lock

# Update dependencies
uv lock --upgrade

# Show available POE tasks
poe --help
```

## Template Usage

When using this as a Copier template:
1. The template prompts for project configuration (name, author, license, etc.)
2. It optionally applies a secondary code template if specified
3. Generated projects include:
   - Multi-language Jupyter Book structure
   - Python package skeleton (if `use_source_code_skeleton=true`)
   - CI/CD workflows for building and publishing
   - Pre-configured development tools (black, isort, flake8, mypy, pytest)

## Important Notes

- This is a template repository - avoid modifying template-specific files directly
- The `book/` directory contains the actual course content structure
- Language configuration is in `book/{lang}/_config.yml`
- Table of contents in `book/{lang}/_toc.yml`
- Build scripts handle preprocessing, building both language versions, and postprocessing
- **UV** manages Python dependencies and packaging with 10-100x faster resolution
- **Ruff** provides fast linting and formatting (replaces flake8, black, isort for new code)
- **Hatchling** as the build backend following PEP 517/621 standards
- **Pre-commit hooks** with deptry for dependency checking
- **Tox-UV** for testing across Python versions 3.9-3.13
- **Python-semantic-release** for automated versioning with Angular commit convention
- POE (poethepoet) provides task automation for book building and legacy workflows