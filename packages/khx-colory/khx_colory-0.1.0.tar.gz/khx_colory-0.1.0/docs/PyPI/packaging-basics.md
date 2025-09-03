# Packaging a Python Project for PyPI (General Guide)

This guide shows how to create a minimal, modern Python package that can be built and published to PyPI. It uses the recommended "src/" layout and PEP 621 metadata in `pyproject.toml` with Hatchling as the build backend.

## Prerequisites

- Python 3.9+
- pip and build tools: `python -m pip install --upgrade pip build twine`

## Project Structure (src layout)

```
your-project/
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ src/
│  └─ your_package/
│     ├─ __init__.py
│     └─ cli.py        # optional
└─ tests/              # optional
```

Notes:
- The top-level directory name (e.g., `your-project`) can differ from the package import name (e.g., `your_package`).
- Keep code under `src/` to prevent accidental implicit imports during development.

## Minimal `pyproject.toml` (PEP 621 + Hatchling)

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "your-package-name"            # must be unique on PyPI
version = "0.1.0"
description = "One-line package summary."
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "you@example.com" }]
classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
]
dependencies = [
  # e.g. "requests>=2"
]

[project.scripts]  # optional console entry points
your-cli = "your_package.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/your_package"]

[tool.hatch.build]
exclude = [
  "/.venv", "/dist", "/build", "/.git", "__pycache__", "*.pyc"
]
```

## Package Code

- `src/your_package/__init__.py` should expose your public API and optionally `__version__`.

```python
# src/your_package/__init__.py
__all__ = ["__version__", "do_something"]
__version__ = "0.1.0"

def do_something() -> str:
    return "hello"
```

- Optional CLI:

```python
# src/your_package/cli.py
def main() -> None:
    print("your-package says hi!")
```

## README and LICENSE

- `README.md` becomes your long description on PyPI.
- Include a license file (e.g., MIT, Apache-2.0).

## Build Artifacts

```powershell
python -m pip install --upgrade build
python -m build           # creates dist/*.whl and dist/*.tar.gz
python -m twine check dist/*
```

## Common Tips

- Choose a unique `project.name` (use hyphens; import name uses underscores).
- Keep a single source of truth for the version (e.g., only in `pyproject.toml`, or mirror it in code with automation if desired).
- Each released version is immutable on PyPI—bump the version for every new upload.
- Exclude local environments from the sdist/wheel to keep packages small.

