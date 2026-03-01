# Development

## Requirements

- Python 3.12+
- [Poetry](https://python-poetry.org/) 2.x

## Setup

```bash
git clone <repo>
cd F1
poetry install --with dev
```

Copy the environment file and adjust as needed:

```bash
cp .env.example .env
```

## Running Tests

```bash
# Unit tests only (fast, no network)
poetry run task test

# All tests including integration (requires network)
poetry run task test-all
```

Coverage threshold is set at **50%**. Current coverage: ~75%.

## Linting and Formatting

```bash
poetry run task lint        # check
poetry run task lint-fix    # auto-fix
poetry run task format      # format with ruff
poetry run task format-check
```

## Documentation

```bash
# Live preview with hot-reload
poetry run task docs

# Build static site to site/
poetry run task docs-build
```

## Pre-commit Hooks

```bash
pre-commit install
```

Hooks run `ruff check` and `ruff format --check` on every commit.

## Project Layout

```
F1/
├── src/f1/           # Application source
├── tests/
│   ├── unit/         # Pure unit tests (mocked)
│   └── integration/  # Live API tests (marked)
├── docs/             # MkDocs source pages
├── mkdocs.yml
├── pyproject.toml
└── .env.example
```
