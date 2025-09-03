# Naylence Fame Core

**Fame Core** is the low-level messaging backbone for the [Naylence](https://github.com/naylence) platform, providing the essential types, protocols, and interfaces for high-performance, addressable, and semantically routable message passing between AI agents and services.

> Part of the Naylence stack. See the full platform [here](https://github.com/naylence).

## Development & Publishing

This project uses Poetry for dependency management and GitHub Actions for automated testing and publishing.

### Local Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .
poetry run black --check .

# Build package
poetry build
```

#### Using local sibling dependencies during development

This project depends on `naylence-factoria`. In development, you can point Poetry to a local checkout without changing `pyproject.toml`:

```bash
# Option A: temporary override (current venv only)
poetry run pip install -e ../naylence-factoria-python

# Option B: Poetry path override (persisted in poetry.lock)
poetry add --path ../naylence-factoria-python naylence-factoria

# Option C: PEP 582 editable via uv (optional)
uv pip install -e ../naylence-factoria-python
```

When committing, keep `pyproject.toml` referencing the normal package (not the local path). CI will install from PyPI/TestPyPI via configured sources.

### Publishing

- **Automatic**: Create a GitHub release to automatically publish to PyPI
- **Manual**: Use the "Publish to PyPI" workflow dispatch to publish to TestPyPI or PyPI
- **Local**: Use `poetry publish -r testpypi` or `poetry publish` for local testing
