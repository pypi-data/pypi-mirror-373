# Publishing to PyPI

This guide explains how to publish the `consumableai-aeo` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **Test PyPI Account**: Create an account on [Test PyPI](https://test.pypi.org/account/register/)
3. **API Tokens**: Generate API tokens for both services

## Getting API Tokens

### Main PyPI
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
2. Click "Add API token"
3. Give it a name (e.g., "consumableai-aeo-publish")
4. Select "Entire project (all projects)"
5. Copy the token (starts with `pypi-`)

### Test PyPI
1. Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/token/)
2. Click "Add API token"
3. Give it a name (e.g., "consumableai-aeo-test")
4. Select "Entire project (all projects)"
5. Copy the token (starts with `pypi-`)

## Publishing Methods

### Method 1: Using the Automated Script (Recommended)

1. **Set environment variables**:
   ```bash
   # For Test PyPI
   export TEST_PYPI_TOKEN=pypi-<your-test-pypi-token>
   
   # For Production PyPI
   export PYPI_TOKEN=pypi-<your-main-pypi-token>
   ```

2. **Publish to Test PyPI first**:
   ```bash
   ./publish.sh test
   ```

3. **Test the package**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ consumableai-aeo
   ```

4. **If everything works, publish to Production PyPI**:
   ```bash
   ./publish.sh prod
   ```

### Method 2: Using Environment Variables with Twine

1. **For Test PyPI**:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-<your-test-pypi-token>
   export TWINE_REPOSITORY_URL=https://test.pypi.org/legacy/
   python -m twine upload --repository testpypi dist/*
   ```

2. **For Production PyPI**:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-<your-main-pypi-token>
   python -m twine upload dist/*
   ```

### Method 3: Using .pypirc File

1. **Copy the example file**:
   ```bash
   cp .pypirc.example ~/.pypirc
   ```

2. **Edit ~/.pypirc** and replace the placeholder tokens with your actual tokens

3. **Publish**:
   ```bash
   # To Test PyPI
   python -m twine upload --repository testpypi dist/*
   
   # To Production PyPI
   python -m twine upload dist/*
   ```

## Build Process

Before publishing, ensure the package is built:

```bash
# Activate virtual environment
source venv/bin/activate

# Install build tools
pip install build twine

# Build the package
python -m build

# Check the distribution files
python -m twine check dist/*
```

## Verification

After publishing, verify the package:

1. **Check Test PyPI**: [https://test.pypi.org/project/consumableai-aeo/](https://test.pypi.org/project/consumableai-aeo/)
2. **Check Production PyPI**: [https://pypi.org/project/consumableai-aeo/](https://pypi.org/project/consumableai-aeo/)

## Testing Installation

Test the published package:

```bash
# From Test PyPI
pip install --index-url https://test.pypi.org/simple/ consumableai-aeo

# From Production PyPI
pip install consumableai-aeo

# Test the CLI
consumableai-aeo --help
```

## Troubleshooting

### Common Issues

1. **"Package already exists"**: Update the version in `pyproject.toml`
2. **"Authentication failed"**: Check your API token and username
3. **"Build failed"**: Ensure all dependencies are installed and the package builds locally

### Version Management

To update the package:

1. **Increment version** in `pyproject.toml`
2. **Rebuild** the package: `python -m build`
3. **Publish** the new version

## Security Notes

- Never commit API tokens to version control
- Use environment variables or `.pypirc` file in your home directory
- Regularly rotate your API tokens
- Use Test PyPI for testing before publishing to production

## Support

If you encounter issues:

1. Check the [PyPI documentation](https://packaging.python.org/guides/publishing-package-distribution-using-twine/)
2. Verify your package structure and configuration
3. Ensure all required files are present and properly formatted
