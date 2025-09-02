# tirex-mirror

Unofficial mirror of [NX-AI/tirex](https://github.com/NX-AI/tirex) for packaging.

## Legal Notice

This is an unofficial mirror of [NX-AI/tirex](https://github.com/NX-AI/tirex).
See [NOTICE.txt](NOTICE.txt) and [LICENSE_MIRROR.txt](LICENSE_MIRROR.txt) for attribution details.
The original project is licensed under the terms in [LICENSE](LICENSE).

## Purpose

This repository automatically mirrors the upstream TiRex project and publishes it to PyPI as `tirex-mirror` for packaging and distribution purposes.

**Installation**: `pip install tirex-mirror`  
**Import**: `import tirex`

## Development Notes

### Setting up local environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install build dependencies
pip install build toml twine
```

### Dry run workflow steps locally

Run commands from `publish.yml`.

Test building the package
```bash
python -m build
```

### Manual publishing

Check package contents
```bash
twine check dist/*
```

Test upload to TestPyPI (optional)
```bash
twine upload --repository testpypi dist/*
```

Real upload to PyPI
```bash
twine upload dist/*
```

Test the package (from testpypi):
```bash
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  tirex-mirror==2025.06.09
```

### GitHub Releases

The workflow automatically creates GitHub releases alongside PyPI releases.

```bash
# View releases
gh release list

# Create manual release (if needed)
VERSION="2025.06.09"
gh release create "v$VERSION" \
  --title "TiRex Mirror v$VERSION" \
  --notes "Manual release" \
  dist/*

# Manual workflow trigger
gh workflow run publish.yml

# Check workflow status
gh run list --workflow=publish.yml
```

### Cleanup after testing

Remove all untracked and ignored files and folders
```bash
git ls-files -o -i --exclude-standard | grep -vE '^(\.venv|venv)/' | xargs -r rm -rf
```
