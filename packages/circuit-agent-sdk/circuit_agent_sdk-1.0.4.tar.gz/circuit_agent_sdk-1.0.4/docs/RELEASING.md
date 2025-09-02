# Release Guide

This guide explains how to release new versions of the circuit-agent-sdk package to PyPI.

## Prerequisites

### 1. PyPI Account Setup
1. Create an account at [PyPI.org](https://pypi.org)
2. Go to [Account Settings → API Tokens](https://pypi.org/manage/account/token/)
3. Click "Add API token"
4. Configure the token:
   - **Token name**: Choose a descriptive name (e.g., "circuit-agent-sdk")
   - **Scope**: "Entire account (all projects)" or specific to "circuit-agent-sdk"
5. **Copy the token immediately** - it starts with `pypi-` and will only be shown once

### 2. TestPyPI Account (Optional, for testing)
1. Create an account at [TestPyPI.org](https://test.pypi.org)
2. Follow the same steps as above to create a token

## ⚠️ Important: Authentication Format

PyPI now **requires** token authentication with a specific format:
- **Username**: Must be exactly `__token__` (literal string, NOT your PyPI username)
- **Password**: Your API token (starts with `pypi-`)

## Local Release Process

### Quick Release (Recommended)
```bash
# Set your PyPI token
export PYPI_TOKEN='pypi-AgEIcH...' # Your actual token

# Run the release command (runs tests, creates git tag, publishes)
make release
```

### Manual Release Steps
```bash
# 1. Run all checks first
make all

# 2. Update version in pyproject.toml if needed
# Edit pyproject.toml and change the version field

# 3. Commit and tag
git add -A
git commit -m "Release v0.3.1"
git tag v0.3.1

# 4. Push to GitHub
git push origin main
git push origin v0.3.1

# 5. Publish to PyPI
export PYPI_TOKEN='pypi-AgEIcH...'
make publish-pypi
```

### Testing with TestPyPI
```bash
# Set TestPyPI token
export TEST_PYPI_TOKEN='pypi-AgEIcH...' # Your test token

# Publish to TestPyPI
make publish-test

# Test installation
pip install -i https://test.pypi.org/simple/ circuit-agent-sdk
```

## GitHub Actions Release

The repository includes automated release via GitHub Actions.

### Setup GitHub Secrets
1. Go to your repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Add a new repository secret:
   - **Name**: `PYPI_TOKEN`
   - **Value**: Your PyPI API token (starting with `pypi-`)

### Trigger a Release
Releases are automatically triggered when you:
1. Create a release on GitHub
2. Or manually trigger the workflow from Actions tab

The GitHub workflow is already configured to use:
- Username: `__token__`
- Password: The secret from `PYPI_TOKEN`

## Manual Configuration Examples

### Using .pypirc (Optional)
If you want to use `twine` manually, create `~/.pypirc`:
```ini
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJDNmMTlhZDAwLTMyZDE...
```

### Direct twine command
```bash
twine upload dist/* --username __token__ --password pypi-YOUR-TOKEN-HERE
```

### Environment variables for twine
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-TOKEN-HERE
twine upload dist/*
```

## Troubleshooting

### Authentication Failed
- **Check username**: Must be exactly `__token__` (not your PyPI username!)
- **Check token**: Must start with `pypi-`
- **Check token scope**: Token must have upload permissions

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid or non-existent authentication" | Wrong username | Use `__token__` as username |
| "Invalid API Token" | Token format wrong | Ensure token starts with `pypi-` |
| "User 'yourusername' does not have permission" | Using PyPI username instead of __token__ | Change username to `__token__` |
| "403 Forbidden" | Token lacks permissions | Create new token with upload scope |

### Environment Variable Issues
```bash
# Check if token is set
echo $PYPI_TOKEN

# Set token for current session
export PYPI_TOKEN='pypi-...'

# Set token permanently (add to ~/.bashrc or ~/.zshrc)
echo "export PYPI_TOKEN='pypi-...'" >> ~/.zshrc
source ~/.zshrc
```

## Release Checklist

Before releasing:
- [ ] Run `make all` to ensure all tests pass
- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG if you have one
- [ ] Ensure PyPI token is set (`echo $PYPI_TOKEN`)
- [ ] Verify token uses `__token__` username format

## Quick Reference

```bash
# Development workflow
make install    # Setup environment
make fix        # Fix code issues
make test       # Run tests
make all        # Fix + type-check + test

# Release workflow
export PYPI_TOKEN='pypi-...'  # Set token (username is __token__)
make release                   # Interactive release
make publish-pypi              # Just publish to PyPI
make publish-test              # Publish to TestPyPI
```
