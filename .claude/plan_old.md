# F1 Dashboard — Plano de Implementação

## Context
Criar um dashboard Streamlit que exibe as **5 voltas mais rápidas por circuito** com o piloto que as realizou, consumindo a API OpenF1. O projeto segue estritamente as boas práticas do SKILL.md: Poetry, Ruff, pytest ≥50% coverage, type hints, logging estruturado, injeção de dependência.

---

## Estrutura de Arquivos

Apenas `src/f1/__init__.py` e `tests/__init__.py` existem. Criar tudo abaixo:

```
src/f1/
├── ingestion/
│   ├── __init__.py
│   ├── http_client.py        # requests.Session com retry/timeout
│   └── openf1_client.py      # 4 repos concretos (Meeting, Session, Lap, Driver)
├── processing/
│   ├── __init__.py
│   └── lap_processor.py      # filter_valid_laps + compute_top_n_laps (pura lógica)
├── domain/
│   ├── __init__.py
│   ├── models.py             # Pydantic v2: Meeting, Session, Lap, Driver, FastestLapEntry
│   ├── repositories.py       # ABCs: MeetingRepo, SessionRepo, LapRepo, DriverRepo
│   └── services.py           # F1DashboardService (orquestra repos + processing)
├── utils/
│   ├── __init__.py
│   ├── logger.py             # get_logger(name) → logging.Logger
│   └── config.py             # BASE_URL, REQUEST_TIMEOUT, DEFAULT_YEAR, TOP_N_LAPS
└── dashboard.py              # Streamlit app (composition root + UI)

tests/
├── conftest.py               # fixtures: sample_laps, sample_drivers
├── unit/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_lap_processor.py
│   └── test_services.py
└── integration/
    ├── __init__.py
    └── test_openf1_client.py

.env.example                  # OPENF1_BASE_URL, REQUEST_TIMEOUT_SECONDS, DEFAULT_YEAR, TOP_N_LAPS
.gitignore                    # .env, __pycache__, .venv, htmlcov
```

---

## Arquivos Críticos a Modificar

- `pyproject.toml` — adicionar deps + config de ruff/pytest
- `src/f1/__init__.py` — já existe, manter vazio
- `tests/__init__.py` — já existe, manter vazio

---

## Passos de Implementação

### 1. Atualizar `pyproject.toml`
Adicionar via `poetry add`:
```bash
# Produção
poetry add streamlit requests pydantic plotly pandas python-dotenv

# Dev
poetry add --group dev pytest pytest-cov ruff pytest-mock pre-commit
```

Adicionar ao pyproject.toml:
```toml
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "N"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["f1"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/f1 --cov-report=term-missing --cov-fail-under=50"
markers = ["integration: testes de integração com API externa"]
```

### 2. `src/f1/utils/logger.py` + `config.py`
- `get_logger(name)` retorna Logger configurado (sem print)
- `config.py`: constantes tipadas lidas de env vars com defaults

### 3. `src/f1/domain/models.py`
Pydantic v2 models:
- `Meeting(meeting_key, meeting_name, country_name, circuit_short_name, date_start, year)`
- `Session(session_key, session_name, session_type)`
- `Lap(lap_number, lap_duration: float|None, driver_number, is_pit_out_lap=False)`
- `Driver(driver_number, full_name, name_acronym, team_name, team_colour)`
- `FastestLapEntry(rank, driver_name, driver_acronym, team_name, team_colour, lap_number, lap_duration)`

### 4. `src/f1/domain/repositories.py`
4 ABCs com `@abstractmethod`: `get_meetings(year)`, `get_sessions(meeting_key, session_name)`, `get_laps(session_key)`, `get_drivers(session_key)`

### 5. `src/f1/processing/lap_processor.py`
Funções puras (sem I/O):
- `filter_valid_laps(laps)` → remove `lap_duration=None` e `is_pit_out_lap=True`
- `build_driver_index(drivers)` → `dict[int, Driver]`
- `compute_top_n_laps(laps, drivers, top_n=5)` → `list[FastestLapEntry]` ordenado por tempo

### 6. `src/f1/ingestion/http_client.py`
`HttpClient` com `requests.Session` + retry (3x, backoff 0.5s, status 429/5xx). Método `get(path, params) → list[dict]`.

### 7. `src/f1/ingestion/openf1_client.py`
4 classes concretas implementando os ABCs:
`OpenF1MeetingRepository`, `OpenF1SessionRepository`, `OpenF1LapRepository`, `OpenF1DriverRepository`.
Cada uma recebe `HttpClient` no construtor e parseia JSON → Pydantic.

### 8. `src/f1/domain/services.py`
`F1DashboardService` recebe os 4 repos por injeção. Métodos:
- `get_meetings_for_year(year) → list[Meeting]`
- `get_top_laps_for_meeting(meeting_key, session_name) → list[FastestLapEntry]`

### 9. `src/f1/dashboard.py`
Streamlit app:
- `@st.cache_resource` → singleton `F1DashboardService` (wires HttpClient + repos)
- Sidebar: seletor de ano (2023/2024/2025), tipo de sessão (Race/Qualifying)
- `@st.cache_data(ttl=3600)` → lista de etapas por ano
- Loop por meeting: `st.expander` com tabela + gráfico de barras Plotly (cores das equipes)

### 10. Testes
**Unit (sem rede):**
- `test_models.py`: validação Pydantic, defaults
- `test_lap_processor.py`: filter_valid_laps, build_driver_index, compute_top_n_laps com edge cases
- `test_services.py`: mocks dos 4 repos via MagicMock, verifica delegação correta

**Integration (rede real, marcados `@pytest.mark.integration`):**
- `test_openf1_client.py`: GET real para reuniões 2024, parse correto para Pydantic

---

## Fluxo de Dados

```
Streamlit UI → F1DashboardService → ABCs → OpenF1*Repository → HttpClient → API
                                                ↓
                                         Pydantic models
                                                ↓
                                      compute_top_n_laps()
                                                ↓
                                      list[FastestLapEntry] → Tabela + Gráfico
```

---

## Como Executar

```bash
# Setup
poetry install --with dev

# Dashboard
poetry run streamlit run src/f1/dashboard.py

# Lint
poetry run ruff check .

# Testes unitários
poetry run pytest tests/unit/

# Testes com coverage HTML
poetry run pytest --cov=src/f1 --cov-report=html
```

---

## Verificação

1. `poetry run ruff check .` → zero erros
2. `poetry run pytest tests/unit/` → ≥50% coverage, todos passam
3. `poetry run streamlit run src/f1/dashboard.py` → dashboard abre em http://localhost:8501, mostra etapas com tabela + gráfico para ano selecionado
