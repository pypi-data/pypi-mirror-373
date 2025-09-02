# OHA Shared SDK

A collection of shared utilities, patterns, and components for OHA applications.

## Installation

### From GitHub Packages

```bash
pip install --index-url https://pypi.pkg.github.com/your-org/simple/ oha-shared
```

### Using Poetry

```bash
poetry add oha-shared
```

## Usage

```python
from oha_shared.mediator import init_mediator
# Use the shared components in your application
```

## Development

1. Install dependencies: `poetry install`
2. Run linting: `poetry run ruff check src`
3. Build package: `poetry build`

## Publishing

The package is automatically published to GitHub Packages when a new release is created.
