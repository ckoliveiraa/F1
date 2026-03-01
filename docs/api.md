# API Reference

## Domain Models

### `Lap`
Represents a single lap recorded during a session.

| Field | Type | Description |
|-------|------|-------------|
| `driver_number` | `int` | Car number |
| `lap_duration` | `float \| None` | Lap time in seconds |
| `lap_number` | `int` | Lap number within the session |
| `session_key` | `int` | Unique session identifier |

### `Driver`
Represents an F1 driver.

| Field | Type | Description |
|-------|------|-------------|
| `driver_number` | `int` | Car number |
| `full_name` | `str` | Driver full name |
| `team_name` | `str` | Constructor name |
| `name_acronym` | `str` | 3-letter code (e.g. `VER`) |

### `Session`
Represents a race weekend session.

| Field | Type | Description |
|-------|------|-------------|
| `session_key` | `int` | Unique identifier |
| `session_name` | `str` | Name (e.g. `Race`, `Qualifying`) |
| `date_start` | `datetime` | Session start time (UTC) |
| `location` | `str` | Circuit location |

## Processing Functions

### `filter_valid_laps(laps)`
Returns only laps where `lap_duration` is a positive number.

### `build_driver_index(drivers)`
Returns a `dict[int, Driver]` mapping `driver_number` to `Driver`.

### `compute_top_n_laps(laps, n)`
Returns the `n` fastest laps sorted ascending by `lap_duration`.

## Service

### `F1DashboardService`

```python
service = F1DashboardService(
    lap_repo=...,
    driver_repo=...,
    session_repo=...,
)

data = service.get_top_laps(session_key=9159, top_n=5)
```

Returns a list of dicts ready for display, each containing driver name, team, lap number, and duration.
