# Update Version and Release (TestPyPI → PyPI)

This guide shows how to bump your package version, publish to TestPyPI for validation, and then publish the same build to PyPI.

## 1) Choose the next version

- Follow semantic versioning when possible: MAJOR.MINOR.PATCH
- Examples: `0.2.0 → 0.2.1` (patch), `0.2.0 → 0.3.0` (minor)

## 2) Update the version in metadata (and code, if mirrored)

- In `pyproject.toml` under `[project]`, set `version = "X.Y.Z"`.
- If you expose `__version__` in code (e.g., `src/your_package/__init__.py`), update it to the same value.

## 3) Update docs/changelog (recommended)

- Update `README.md` examples if needed.
- Update `CHANGELOG.md` with notable changes.

## 4) Clean old artifacts and build

```powershell
Remove-Item -Recurse -Force dist/*  # or delete the folder
python -m build
python -m twine check dist/*
```

## 5) Publish to TestPyPI and validate install

```powershell
# Set TestPyPI token in env (do not commit secrets)
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-<your-testpypi-token>"

python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Validate from a clean venv
python -m venv .testenv
.\.testenv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple your-package-name==X.Y.Z
python -c "import your_package; print(getattr(your_package, '__version__', 'n/a'))"
```

## 6) Publish to PyPI

```powershell
# Set PyPI token in env
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-<your-pypi-token>"

python -m twine upload dist/*
```

## 7) Post-release

- Tag the release in git (e.g., `git tag vX.Y.Z && git push --tags`).
- Monitor installs and issues; consider yanking if needed (with caution).

## Important

- PyPI and TestPyPI disallow overwriting an existing version. If you need to re-publish, bump the version.
- Keep tokens out of version control and CI logs.

