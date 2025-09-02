# 📦 Publishing AutoPurple to PyPI

## Prerequisites

```bash
# Install build and publishing tools
pip install build twine

# Get PyPI account and API token from https://pypi.org/
```

## Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Verify build contents
tar -tzf dist/autopurple-1.0.0.tar.gz | head -20
```

## Test Installation Locally

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from local build
pip install dist/autopurple-1.0.0.tar.gz

# Test the CLI
autopurple --help
autopurple health

# Clean up
deactivate
rm -rf test_env
```

## Publish to PyPI

### Test PyPI (Recommended First)

```bash
# Upload to test PyPI
twine upload --repository testpypi dist/*

# Test installation from test PyPI  
pip install --index-url https://test.pypi.org/simple/ autopurple

# Verify it works
autopurple --help
```

### Production PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Verify on PyPI.org
# https://pypi.org/project/autopurple/
```

## Post-Publication

### Verify Installation

```bash
# Test fresh installation
pip install autopurple

# Test with all features
pip install autopurple[ai,aws,dev]

# Verify CLI
autopurple --help
autopurple health
```

### Update Documentation

```bash
# Update badges in README.md
# Add PyPI version badge: https://badge.fury.io/py/autopurple
# Add download stats: https://pepy.tech/project/autopurple
```

## Version Management

### For Next Release

```bash
# Update version in pyproject.toml
sed -i 's/version = "1.0.0"/version = "1.0.1"/' pyproject.toml

# Update version in __init__.py
sed -i 's/__version__ = "1.0.0"/__version__ = "1.0.1"/' autopurple/__init__.py

# Build and publish new version
python -m build
twine upload dist/*
```

## Package Structure Verification

```bash
# Check package contents
python -c "
import autopurple
print(f'Version: {autopurple.__version__}')
print(f'Pipeline available: {hasattr(autopurple, \"AutoPurplePipeline\")}')
"

# Check CLI entry point
which autopurple
autopurple --version
```

## Troubleshooting

### Build Issues
```bash
# Missing dependencies
pip install -e .[dev]

# Clean and rebuild
rm -rf build/ *.egg-info/
python -m build
```

### Upload Issues
```bash
# Check credentials
twine check dist/*

# Force re-upload (increment version first!)
twine upload --skip-existing dist/*
```

### Installation Issues
```bash
# Check Python version compatibility
python --version  # Needs >=3.11

# Install with verbose output
pip install -v autopurple

# Check import issues
python -c "import autopurple; print('OK')"
```

## Release Checklist

- [ ] Update version in pyproject.toml
- [ ] Update version in autopurple/__init__.py  
- [ ] Update CHANGELOG.md
- [ ] Test locally: `python -m build && pip install dist/autopurple-X.X.X.tar.gz`
- [ ] Test CLI: `autopurple --help && autopurple health`
- [ ] Upload to test PyPI: `twine upload --repository testpypi dist/*`
- [ ] Test from test PyPI: `pip install --index-url https://test.pypi.org/simple/ autopurple`
- [ ] Upload to production PyPI: `twine upload dist/*`
- [ ] Verify on PyPI.org
- [ ] Test fresh install: `pip install autopurple`
- [ ] Create GitHub release with tag
- [ ] Update documentation with new version

## Expected Result

After publishing, users can install with:

```bash
# Basic installation
pip install autopurple

# With AI features (includes Claude)
pip install autopurple[ai]

# Full development setup
pip install autopurple[ai,aws,dev]

# Use the CLI
autopurple run --region us-east-1 --claude-api-key sk-ant-...
```
