# Architecture

The project follows a layered architecture with clear separation of concerns.

## Layer Overview

```
src/f1/
├── utils/          # Cross-cutting concerns (logger, config)
├── domain/         # Business models, repository ABCs, service
├── processing/     # Pure data transformation functions
├── ingestion/      # HTTP client + OpenF1 API adapters
└── dashboard.py    # Streamlit composition root
```

## Layers

### Utils
- `utils/logger.py` — `get_logger(name)` returns a configured Python logger
- `utils/config.py` — reads environment variables (base URL, timeouts, etc.)

### Domain
- `domain/models.py` — Pydantic v2 models: `Lap`, `Driver`, `Session`
- `domain/repositories.py` — abstract base classes (`LapRepository`, `DriverRepository`, `SessionRepository`)
- `domain/services.py` — `F1DashboardService` orchestrates repos to produce dashboard data

### Processing
- `processing/lap_processor.py` — pure functions:
    - `filter_valid_laps` — removes laps with missing or invalid times
    - `build_driver_index` — maps driver number to `Driver` object
    - `compute_top_n_laps` — returns the N fastest laps for each driver

### Ingestion
- `ingestion/http_client.py` — `HttpClient` with configurable retry logic
- `ingestion/openf1_client.py` — concrete repository implementations against the OpenF1 REST API

### Dashboard
- `dashboard.py` — Streamlit app that wires all layers together (composition root)

## Data Flow

```
OpenF1 API
    └─► HttpClient (retry)
        └─► OpenF1Repositories
            └─► F1DashboardService
                └─► lap_processor (filter + rank)
                    └─► Streamlit UI (Plotly charts)
```
