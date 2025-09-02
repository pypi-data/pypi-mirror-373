# Development Guide for Elluminate SDK

This guide provides detailed information for developers who want to contribute to or modify the Elluminate SDK.

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- uv package manager
- Git

### Initial Setup

1. Clone the repository:

```bash
git clone git@github.com:ellamind/elluminate-platform-django.git
```

2. Navigate to the SDK directory:

```bash
cd elluminate-platform-django/elluminate_sdk
```

3. Install development dependencies:

```bash
uv sync --dev
```

This creates a `.venv` directory in `elluminate_sdk`. Note that this is separate from the Platform's virtual environment.

### Environment Configuration

The SDK supports different environments through the `ELLUMINATE_BASE_URL` variable:

```bash
# For local development
export ELLUMINATE_BASE_URL=http://localhost:8000

# For staging
export ELLUMINATE_BASE_URL=https://dev.elluminate.de

# For production
export ELLUMINATE_BASE_URL=https://app.elluminate.de
```

## Testing

1. Ensure you're in the `elluminate_sdk` directory and have installed development dependencies

2. Run the basic test suite:

```bash
uv run pytest
```

3. Run tests with coverage report:

```bash
uv run pytest --cov=elluminate --cov-report=term-missing
```

## Publishing Process

### Version Management

1. Update version in `elluminate/__init__.py` following semantic versioning (X.Y.Z)
2. Push changes to GitHub
3. Create a new version commit:

```bash
git commit -m "Bump version to X.Y.Z"
```

### Publishing to PyPI

The SDK is published to PyPI through GitHub Actions:

1. Navigate to the "Actions" tab in the GitHub repository
2. Select "Publish SDK to PyPI" workflow
3. Click "Run workflow"
4. Enter the version number (must match `__init__.py`)
5. The action will:
   - Verify the version matches
   - Build the package
   - Publish to PyPI
