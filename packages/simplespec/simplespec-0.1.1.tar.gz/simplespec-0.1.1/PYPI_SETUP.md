# PyPI Token Setup Guide

## For GitHub Codespaces (Recommended)

### Option 1: Set as Codespaces Secret
1. Go to your GitHub repository settings
2. Navigate to **Settings > Secrets and variables > Codespaces**
3. Click **New repository secret**
4. Name: `PYPI_API_TOKEN`
5. Value: Your PyPI token (starts with `pypi-`)
6. Restart your Codespace

### Option 2: Temporary Environment Variable (This Session Only)
```bash
export PYPI_API_TOKEN="your_pypi_token_here"
```

### Option 3: Secure File Method
```bash
# Save token to a secure file (not committed to git)
echo "your_pypi_token_here" > ~/.pypi_token
chmod 600 ~/.pypi_token

# Load it when needed
export PYPI_API_TOKEN=$(cat ~/.pypi_token)
```

## Publishing the Package

### Method 1: Using the Publish Script
```bash
# Set your token (if not already set as Codespaces secret)
export PYPI_API_TOKEN="your_pypi_token_here"

# Run the publish script
./publish.sh
```

### Method 2: Manual Steps
```bash
# Set token
export PYPI_API_TOKEN="your_pypi_token_here"

# Build and publish
uv build
uv run twine upload dist/* --username __token__ --password $PYPI_API_TOKEN
```

## For GitHub Actions (Automated Releases)

1. Go to your repository **Settings > Environments**
2. Create/edit the `publish` environment
3. Add secret: `PYPI_API_TOKEN` with your token value
4. Push a tag to trigger release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

## Security Notes

- ✅ Never commit tokens to git
- ✅ Use GitHub secrets for automation
- ✅ Use environment variables for local development
- ✅ The `.gitignore` excludes `.pypirc` to prevent accidental commits
- ✅ Tokens are masked in GitHub Actions logs
