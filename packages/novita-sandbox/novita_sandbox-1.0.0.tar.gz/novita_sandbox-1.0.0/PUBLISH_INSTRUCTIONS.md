# PyPI Publishing Instructions

## 1. Configure PyPI credentials

```bash
# Configure Test PyPI (for testing)
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry config pypi-token.test-pypi YOUR_TEST_PYPI_TOKEN

# Configure Production PyPI
poetry config pypi-token.pypi YOUR_PRODUCTION_PYPI_TOKEN
```

## 2. Test publish to Test PyPI first (RECOMMENDED)

```bash
# Build the package
poetry build

# Publish to Test PyPI first
poetry publish --repository test-pypi

# Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ novita-sandbox==2.0.0
```

## 3. Publish to Production PyPI

```bash
# Once you've verified everything works on Test PyPI:
poetry publish
```

## 4. Verify publication

```bash
# Check your package on PyPI
# https://pypi.org/project/novita-sandbox/

# Test install from production PyPI
pip install novita-sandbox==2.0.0
```

## 5. Package installation commands for users

After publishing, users can install your package with:

```bash
# Basic installation
pip install novita-sandbox

# With code interpreter support
pip install novita-sandbox[code-interpreter]

# With desktop automation support  
pip install novita-sandbox[desktop]

# With all optional dependencies
pip install novita-sandbox[all]
```

## 6. Version management

To release a new version:

```bash
# Update version in pyproject.toml
# Then rebuild and republish
poetry version patch  # or minor/major
poetry build
poetry publish
```
