# Python package wrapper for Vercel CLI

[![CI](https://github.com/nuage-studio/vercel-cli-python/actions/workflows/test.yml/badge.svg)](https://github.com/nuage-studio/vercel-cli-python/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/nuage-studio/vercel-cli-python/graph/badge.svg)](https://codecov.io/gh/nuage-studio/vercel-cli-python)
[![Supported Python Versions](https://img.shields.io/badge/python-3.8--3.13-blue.svg)](https://www.python.org/)

**vercel-cli** packages the npm `vercel` CLI for Python environments. It vendors the npm package under `vercel_cli/vendor/` and uses the bundled Node.js runtime provided by `nodejs-wheel-binaries`, so you can run `vercel` without installing Node.js.

It provides both a command-line interface and a Python API that other libraries can use programmatically instead of resorting to subprocess calls.

## Quick start

- **Install**:

```bash
pip install vercel-cli
```

- **Use** (same arguments and behavior as the official npm CLI):

```bash
vercel --version
vercel login
vercel deploy
```

- **Use programmatically in Python** (for libraries that depend on this package):

```python
from vercel_cli import run_vercel

# Deploy current directory
exit_code = run_vercel(["deploy"])

# Deploy specific directory with custom environment
exit_code = run_vercel(
    ["deploy", "--prod"],
    cwd="/path/to/project",
    env={"VERCEL_TOKEN": "my-token"}
)

# Check version
exit_code = run_vercel(["--version"])
```

## What this provides

- **No system Node.js required**: The CLI runs via the Node binary from `nodejs-wheel-binaries` (currently Node 22.x).
- **Vendored npm package**: The `vercel` npm package (production deps only) is checked into `vercel_cli/vendor/`.
- **Console entrypoint**: The `vercel` command maps to `vercel_cli.run:main`, which executes `vercel_cli/vendor/dist/vc.js` with the bundled Node runtime.
- **Python API**: The `run_vercel()` function allows other Python libraries to use Vercel CLI programmatically without subprocess calls, with secure environment variable handling.

## Requirements

- Python 3.8+
- macOS, Linux, or Windows supported by the Node wheels

## How it works

At runtime, `vercel_cli.run` locates `vercel_cli/vendor/dist/vc.js` and launches it via the Node executable exposed by `nodejs_wheel_binaries`. CLI arguments are passed through unchanged, while environment variables are handled securely.

## Programmatic usage

When using this package as a dependency in other Python libraries, you can call Vercel CLI commands directly without using subprocess:

```python
from vercel_cli import run_vercel
import tempfile
import os

def deploy_my_app(source_dir: str, token: str) -> bool:
    """Deploy an application to Vercel programmatically."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy your app to temp directory and modify as needed
        # ...

        # Deploy with custom environment
        env = {
            "VERCEL_TOKEN": token,
            "NODE_ENV": "production"
        }

        exit_code = run_vercel(
            ["deploy", "--prod", "--yes"],
            cwd=temp_dir,
            env=env
        )

        return exit_code == 0

# Usage
success = deploy_my_app("./my-app", "my-vercel-token")
```

The `run_vercel()` function accepts:

- `args`: List of CLI arguments (same as command line)
- `cwd`: Working directory for the command
- `env`: Environment variables to set (passed directly to the Node.js runtime)

## Security considerations

When using the `env` parameter, only explicitly provided environment variables are passed to the Vercel CLI. This prevents accidental leakage of sensitive environment variables from your Python process while still allowing you to set necessary variables like `VERCEL_TOKEN`.

Example with secure token handling:

```python
from vercel_cli import run_vercel

# Secure: only VERCEL_TOKEN is passed to the CLI
exit_code = run_vercel(
    ["deploy", "--prod"],
    env={"VERCEL_TOKEN": "your-secure-token"}
)
```

This approach avoids common security pitfalls of subprocess environment variable handling.

## Updating the vendored Vercel CLI (maintainers)

There are two ways to update the vendored npm package under `vercel_cli/vendor/`:

1) Manual update to a specific version

```bash
# Using the console script defined in pyproject.toml
uv run update-vendor 46.0.2
# or equivalently
uv run python scripts/update_vendor.py 46.0.2
```

This will:

- fetch `vercel@46.0.2` from npm,
- verify integrity/shasum,
- install production dependencies with `npm install --omit=dev`, and
- copy the result into `vercel_cli/vendor/`.

1) Automatic check-and-release (GitHub Actions)

The workflow `.github/workflows/release.yml` checks npm `latest` and, if newer than the vendored version, will:

- vendor the new version using `scripts/check_and_update.py`,
- commit the changes and create a tag `v<version>`,
- build distributions, and
- publish to PyPI (requires `PYPI_API_TOKEN`).

## Versioning

The Python package version is derived dynamically from the vendored `package.json` via Hatch’s version source:

```toml
[tool.hatch.version]
path = "vercel_cli/vendor/package.json"
pattern = '"version"\s*:\s*"(?P<version>[^\\"]+)"'
```

## Development

- Build backend: `hatchling`
- Dependency management: `uv` (see `uv.lock`)
- Tests: `pytest` with coverage in `tests/`
- Lint/format: `ruff`; type-check: `basedpyright`

Common commands (using `uv`):

```bash
# Run tests with coverage
uv run pytest --cov=vercel_cli --cov-report=term-missing

# Lint and format
uv run ruff check .
uv run ruff format .

# Type-check
uv run basedpyright

# Build wheel and sdist
uv run --with build python -m build
```
