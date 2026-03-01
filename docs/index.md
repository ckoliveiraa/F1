# F1 Dashboard

Streamlit dashboard showing the **5 fastest laps per circuit** using the [OpenF1 API](https://openf1.org).

## Features

- Real-time lap time data via OpenF1 API
- Top 5 fastest laps per session with driver comparison
- Interactive Plotly charts
- Configurable via environment variables

## Quick Start

```bash
# Install dependencies
poetry install --with dev

# Start the dashboard
poetry run streamlit run src/f1/dashboard.py
```

The dashboard will be available at `http://localhost:8501`.

## Available Tasks

| Task | Command | Description |
|------|---------|-------------|
| `test` | `poetry run task test` | Run unit tests with coverage |
| `test-all` | `poetry run task test-all` | Run all tests (unit + integration) |
| `lint` | `poetry run task lint` | Check code style |
| `lint-fix` | `poetry run task lint-fix` | Auto-fix lint errors |
| `format` | `poetry run task format` | Format source code |
| `docs` | `poetry run task docs` | Serve docs locally |
| `docs-build` | `poetry run task docs-build` | Build static docs site |
