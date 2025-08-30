# Publishing Gymix Python SDK to PyPI

This guide walks you through publishing the Gymix Python SDK to PyPI.

## Prerequisites

1. **Install build tools**:

   ```bash
   pip install build twine
   ```

2. **Create PyPI accounts**:

   - Regular PyPI: https://pypi.org/account/register/
   - Test PyPI: https://test.pypi.org/account/register/

3. **Configure API tokens** (recommended over username/password):

   - Create API tokens on both PyPI and TestPyPI
   - Store them in `~/.pypirc`:

   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-your-testpypi-token-here
   ```

## Publication Steps

### 1. Prepare for Release

```bash
# Ensure you're in the project directory
cd /path/to/gymix-python-sdk

# Clean previous builds
make clean

# Run all checks
make check-all
```

### 2. Update Version and Changelog

1. **Update version** in these files:

   - `setup.py` (version="1.0.0")
   - `pyproject.toml` (version = "1.0.0")
   - `gymix/__init__.py` (**version** = "1.0.0")

2. **Update CHANGELOG.md** with release notes

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Release version 1.0.0"
   git tag v1.0.0
   ```

### 3. Build the Package

```bash
# Build source distribution and wheel
python -m build

# Or use Makefile
make build
```

This creates files in `dist/`:

- `gymix-1.0.0.tar.gz` (source distribution)
- `gymix-1.0.0-py3-none-any.whl` (wheel)

### 4. Test on TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Or use Makefile
make upload-test
```

### 5. Test Installation from TestPyPI

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ gymix

# Test the installation
python -c "
from gymix import GymixClient
client = GymixClient('test-token')
print('✅ Package imported successfully!')
print(f'Version: {client.__class__.__module__.split('.')[0]}')
"
```

### 6. Upload to PyPI

If testing is successful:

```bash
# Upload to PyPI
python -m twine upload dist/*

# Or use Makefile
make upload
```

### 7. Verify Publication

```bash
# Check on PyPI
open https://pypi.org/project/gymix/

# Install from PyPI in a fresh environment
pip install gymix

# Test installation
python -c "import gymix; print('✅ Successfully installed from PyPI!')"
```

## Automated Release Script

You can use the build script we created:

```bash
# Make executable
chmod +x build_package.py

# Run build process
python build_package.py
```

## Post-Release Steps

1. **Create GitHub release**:

   ```bash
   git push origin main
   git push origin v1.0.0
   ```

2. **Update documentation** if needed

3. **Announce release** on relevant channels

## Troubleshooting

### Common Issues

1. **Package name already exists**:

   - Choose a different name
   - Contact PyPI if you believe you have rights to the name

2. **Version already exists**:

   - Increment version number
   - You cannot re-upload the same version

3. **Authentication errors**:

   - Check your API tokens
   - Verify `~/.pypirc` configuration

4. **Build errors**:
   - Run `make check-all` to identify issues
   - Ensure all dependencies are properly specified

### Testing Checklist

Before publishing, ensure:

- [ ] All tests pass
- [ ] Code is properly formatted (black)
- [ ] No linting errors (flake8)
- [ ] Type checking passes (mypy)
- [ ] Version numbers are updated
- [ ] CHANGELOG.md is updated
- [ ] README.md is accurate
- [ ] All files are included in MANIFEST.in
- [ ] Package installs correctly from TestPyPI

## Maintenance

### Future Releases

1. **Semantic Versioning**:

   - MAJOR.MINOR.PATCH (e.g., 1.0.0)
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

2. **Release frequency**:

   - Regular updates for bug fixes
   - Feature releases as needed
   - Security updates immediately

3. **Backwards compatibility**:
   - Maintain API compatibility when possible
   - Provide migration guides for breaking changes
   - Use deprecation warnings before removing features
