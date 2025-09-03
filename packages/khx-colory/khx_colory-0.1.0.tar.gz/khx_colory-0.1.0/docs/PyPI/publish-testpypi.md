# Publish to TestPyPI (Safe Rehearsal)

TestPyPI is a separate index for validating packaging and distribution before publishing to the real PyPI. You’ll upload the same artifacts there and test installation in a clean environment.

## Prerequisites

- Build artifacts present in `dist/` (wheel + sdist)
  - If not built yet: `python -m build`
- Twine installed: `python -m pip install --upgrade twine`

## 1) Validate artifacts

```powershell
python -m twine check dist/*
```

## 2) Set credentials (environment variables)

Use an API token from your TestPyPI account. Never commit tokens to source control.

PowerShell (Windows):
```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-<your-testpypi-token>"
```

Bash (macOS/Linux):
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-testpypi-token>
```

## 3) Upload to TestPyPI

```powershell
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Twine prints a URL to your project on TestPyPI when the upload succeeds.

## 4) Install from TestPyPI to verify

TestPyPI does not mirror PyPI, so include the real PyPI index as a fallback for dependencies.

```powershell
python -m venv .testenv
.\.testenv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple your-package-name==X.Y.Z
python -c "import your_package; print(getattr(your_package, '__version__', 'n/a'))"
```

## Troubleshooting

- 400 File already exists: bump the version and rebuild.
- 403 Invalid or missing credentials: confirm token, username `__token__`, and index URL.
- Long description errors: fix `README.md` and re-build; use `twine check` to validate.

