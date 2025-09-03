# Publish to Real PyPI

Once you validate on TestPyPI, publish the exact same version to the real PyPI. Versions on PyPI are immutable—if an upload for a version exists, you must bump the version for changes.

## Prerequisites

- Build artifacts in `dist/` (wheel + sdist)
- Twine installed: `python -m pip install --upgrade twine`
- A PyPI API token with project or account scope

## 1) Validate artifacts (optional but recommended)

```powershell
python -m twine check dist/*
```

## 2) Set credentials (environment variables)

Use an API token from your PyPI account. Never commit tokens to source control.

PowerShell (Windows):
```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-<your-pypi-token>"
```

Bash (macOS/Linux):
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-pypi-token>
```

## 3) Upload to PyPI

```powershell
python -m twine upload dist/*
```

Twine prints a URL to your project on PyPI when the upload succeeds.

## 4) Verify from a clean environment

```powershell
python -m venv .prodenv
.\.prodenv\Scripts\Activate.ps1
pip install --upgrade pip
pip install your-package-name==X.Y.Z
python -c "import your_package; print(getattr(your_package, '__version__', 'n/a'))"
```

## Notes

- If you enable 2FA on PyPI, API tokens remain the recommended non-interactive auth.
- Consider adding a CHANGELOG and git tag per release.

