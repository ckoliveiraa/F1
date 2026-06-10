# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install --with dev

# Run all unit tests
poetry run pytest tests/unit/

# Run a single test file
poetry run pytest tests/unit/test_lap_processor.py

# Run a single test by name
poetry run pytest tests/unit/test_services.py::test_function_name

# Run integration tests (hits live OpenF1 API)
poetry run pytest tests/integration/ -m integration

# Lint and format
poetry run ruff check .
poetry run ruff format .

# Start the dashboard
poetry run streamlit run src/f1/dashboard.py

# Serve docs locally
poetry run task docs

# Build docs
poetry run task docs-build
```

Pre-commit hooks (ruff lint + format, trailing whitespace, YAML/TOML checks) run on every commit.

## Architecture

Clean/layered architecture with strict dependency direction: UI → Domain ← Ingestion/Processing.

```
src/f1/
├── dashboard.py          # Streamlit composition root — wires all dependencies, no business logic
├── domain/               # Core layer, no external dependencies
│   ├── models.py         # Pydantic v2 models: Meeting, Session, Lap, Driver, FastestLapEntry
│   ├── repositories.py   # Abstract base classes (interfaces) for all data access
│   └── services.py       # F1DashboardService — orchestrates repos and processing
├── ingestion/            # OpenF1 API adapters implementing domain repository ABCs
│   ├── http_client.py    # HttpClient with retry/backoff logic
│   └── openf1_client.py  # Concrete repo implementations (Meeting, Session, Lap, Driver)
├── processing/           # Pure stateless functions, no I/O
│   └── lap_processor.py  # filter_valid_laps, build_driver_index, compute_top_n_laps
└── utils/
    ├── config.py         # Env-var config loader
    └── logger.py         # get_logger factory
```

**Key design decisions:**
- `F1DashboardService` depends only on abstract repositories — swap implementations freely.
- `lap_processor.py` has zero side effects; all unit tests for it require no mocking.
- `openf1_client.py` repos swallow individual item validation errors (log + skip) so a single bad API response doesn't abort the whole fetch.
- `dashboard.py` uses `@st.cache_resource` / `@st.cache_data` to avoid re-fetching on re-renders.

## Key Constraints

- **README.md must stay ASCII-only** — the file is UTF-8 but any non-ASCII characters break `poetry install`.
- Python target is 3.12; `pyproject.toml` pins `python = ">=3.12"`.
- `streamlit` is pinned `<2.0.0` because `pandas <3` is required.
- Minimum test coverage is 50% (enforced by pytest-cov in CI).
- CI deploys docs to GitHub Pages on pushes to `main` only.
