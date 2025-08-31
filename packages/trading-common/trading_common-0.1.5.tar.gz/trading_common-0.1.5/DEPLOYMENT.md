# Deployment Guide

This document describes how to deploy and publish the `trading-common` package.

## Prerequisites

- Python 3.10+
- pip and build tools
- Access to PyPI (for publishing)
- GitHub repository with configured secrets

## Local Development Setup

1. **Clone and install in development mode:**
   ```bash
   cd trading-common-py
   pip install -e ".[dev]"
   ```

2. **Run tests:**
   ```bash
   pytest
   ```

3. **Format and lint code:**
   ```bash
   black src tests
   isort src tests
   mypy src
   ```

## Building the Package

1. **Clean previous builds:**
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. **Build package:**
   ```bash
   python -m build
   ```

3. **Verify build artifacts:**
   ```bash
   ls -la dist/
   # Should show:
   # trading_common-0.1.0-py3-none-any.whl
   # trading_common-0.1.0.tar.gz
   ```

## Publishing to PyPI

### GitHub Actions (Recommended)

The repository includes GitHub Actions workflows for automated publishing:

1. **Manual Build and Publish:**
   - Go to Actions → Manual Build and Publish to PyPI
   - Enter version number and click "Run workflow"
   - Optionally create git tag

2. **Automatic Publish on Tag:**
   - Create and push a tag: `git tag trading-common-v0.1.0 && git push origin trading-common-v0.1.0`
   - The Publish Package workflow will automatically run

3. **Required Secrets:**
   - `PYPI_TOKEN`: Your PyPI API token
   - `GITHUB_TOKEN`: Automatically provided by GitHub

### Manual Publishing

#### Test PyPI (Recommended for testing)

1. **Upload to test PyPI:**
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. **Test installation:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ trading-common
   ```

### Production PyPI

1. **Upload to production PyPI:**
   ```bash
   python -m twine upload dist/*
   ```

2. **Verify installation:**
   ```bash
   pip install trading-common
   ```

## Version Management

1. **Update version in `pyproject.toml`:**
   ```toml
   [project]
   version = "0.2.0"  # Increment version
   ```

2. **Update CHANGELOG.md with new version**

3. **Create git tag:**
   ```bash
   git tag -a trading-common-v0.2.0 -m "Release trading-common v0.2.0"
   git push origin trading-common-v0.2.0
   ```

## Using in Services

After publishing, services can install the package:

```bash
# In service requirements.txt or pyproject.toml
trading-common>=0.1.0

# Or install directly
pip install trading-common
```

## Troubleshooting

### Build Errors
- Ensure all dependencies are installed: `pip install -e ".[dev]"`
- Check Python version compatibility
- Verify `pyproject.toml` syntax

### Upload Errors
- Check PyPI credentials in `~/.pypirc`
- Ensure package name is unique
- Verify package metadata in `pyproject.toml`

### Import Errors in Services
- Check package version compatibility
- Verify all dependencies are installed
- Check Python path and virtual environment
