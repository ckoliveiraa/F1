# Plano de Criação — Dashboard F1 (OpenF1)

## Contexto

Este plano define a criação de um projeto Python para consumir a **OpenF1 API** (`https://api.openf1.org/v1/`) e expor um dashboard interativo de telemetria, voltas, pilotos e sessões da Fórmula 1. O projeto deve seguir integralmente o padrão de engenharia descrito em [.claude/SKILL.md](.claude/SKILL.md) (Poetry, arquitetura em camadas, Ruff, pytest ≥50%, MkDocs Material) e usar os endpoints documentados em [.claude/doc_api.md](.claude/doc_api.md).

A motivação é entregar uma base reproduzível, testável e documentada que permita explorar dados históricos de F1 (a partir de 2023) sem autenticação, com possibilidade futura de plugar dados em tempo real.

---

## 1. Stack e Decisões

| Item | Escolha | Justificativa |
|---|---|---|
| Gerenciador | Poetry | Obrigatório por [SKILL.md §2](.claude/SKILL.md) |
| Python | `^3.12` | Compatível com Streamlit e dependências |
| HTTP | `httpx` + retry/backoff | Cliente moderno, suporta timeouts |
| Modelos | `pydantic` v2 | Validação tipada dos payloads OpenF1 |
| UI | `streamlit` (`<2.0.0`) | Dashboard rápido, pinado por pandas `<3` |
| Lint/Format | `ruff` | Obrigatório por [SKILL.md §4.2](.claude/SKILL.md) |
| Testes | `pytest` + `pytest-cov` + `pytest-mock` | Cobertura mínima 50% |
| Docs | `mkdocs-material` | Obrigatório por [SKILL.md §6](.claude/SKILL.md) |
| Config | `python-dotenv` | `.env` para `ENVIRONMENT`, base URL |

---

## 2. Estrutura de Diretórios

Segue o layout exigido em [SKILL.md §1](.claude/SKILL.md):

```
F1/
├── pyproject.toml
├── poetry.lock
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── README.md                       # ASCII-only
├── mkdocs.yml
├── src/
│   └── f1/
│       ├── __init__.py
│       ├── dashboard.py            # composition root Streamlit
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── http_client.py      # HttpClient com retry/backoff
│       │   └── openf1_client.py    # repos concretos (Meetings, Sessions, Drivers, Laps, ...)
│       ├── processing/
│       │   ├── __init__.py
│       │   └── lap_processor.py    # filter_valid_laps, build_driver_index, compute_top_n_laps
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models.py           # Meeting, Session, Driver, Lap, FastestLapEntry, Stint, Weather
│       │   ├── repositories.py     # ABCs por endpoint
│       │   └── services.py         # F1DashboardService
│       └── utils/
│           ├── __init__.py
│           ├── config.py           # carrega .env (BASE_URL, ENVIRONMENT, TIMEOUT)
│           └── logger.py           # get_logger
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_lap_processor.py
│   │   ├── test_services.py
│   │   ├── test_models.py
│   │   └── test_http_client.py
│   └── integration/
│       └── test_openf1_live.py     # @pytest.mark.integration
└── docs/
    └── docs/
        ├── index.md
        ├── architecture.md
        ├── project-structure.md
        ├── running-locally.md
        ├── running-tests.md
        └── contributing.md
```

---

## 3. Camadas e Responsabilidades

Conforme [SKILL.md §3](.claude/SKILL.md), regra de dependência: **UI → Domain ← Ingestion / Processing**. `domain/` não importa infraestrutura.

### 3.1 `domain/models.py` (Pydantic v2)
Modelos espelhando o payload da OpenF1 ([doc_api.md](.claude/doc_api.md)):
- `Meeting` — `meeting_key`, `meeting_name`, `country_name`, `circuit_short_name`, `year`, `date_start`
- `Session` — `session_key`, `session_name`, `session_type`, `date_start`, `date_end`, `country_name`, `year`
- `Driver` — `driver_number`, `full_name`, `name_acronym`, `team_name`, `team_colour`, `headshot_url`
- `Lap` — `lap_number`, `lap_duration`, `duration_sector_1/2/3`, `i1_speed`, `i2_speed`, `st_speed`, `is_pit_out_lap`, `driver_number`
- `FastestLapEntry` — projeção pós-processamento (driver + melhor volta)
- (Opcionais para evolução) `Stint`, `Weather`, `RaceControlMessage`, `Pit`

### 3.2 `domain/repositories.py`
ABCs (uma por endpoint usado):
- `MeetingRepository.list(year, country=None)`
- `SessionRepository.list(meeting_key)`
- `DriverRepository.list(session_key)`
- `LapRepository.list(session_key, driver_number=None)`

### 3.3 `domain/services.py`
`F1DashboardService` recebe os 4 repositórios por injeção de dependência ([SKILL.md §3.4](.claude/SKILL.md)). Expõe:
- `list_meetings(year)`
- `list_sessions(meeting_key)`
- `get_session_overview(session_key)` → drivers + top N voltas + estatísticas
- `get_top_n_fastest_laps(session_key, n=10)`

### 3.4 `processing/lap_processor.py` (puro, sem I/O)
- `filter_valid_laps(laps: list[Lap]) -> list[Lap]` — remove voltas sem `lap_duration` ou `is_pit_out_lap`
- `build_driver_index(drivers: list[Driver]) -> dict[int, Driver]`
- `compute_top_n_laps(laps, drivers_index, n) -> list[FastestLapEntry]`

### 3.5 `ingestion/http_client.py`
`HttpClient` com `httpx`, timeout configurável, retry exponencial (3 tentativas) em 5xx e timeout. Suporta filtros via query string (operadores `=`, `>=`, `<=`, `>`, `<` conforme [doc_api.md](.claude/doc_api.md)).

### 3.6 `ingestion/openf1_client.py`
Implementações concretas das ABCs. Cada repo:
- monta query com `session_key`/`meeting_key`/etc.
- chama `HttpClient.get`
- valida cada item com Pydantic, **logando e ignorando** itens inválidos (resiliência)

### 3.7 `dashboard.py` (Streamlit)
Composition root: instancia `HttpClient`, repos concretos, `F1DashboardService`. Páginas:
1. Seleção de temporada → meeting → sessão
2. Tabela de Top 10 voltas mais rápidas (com cores da equipe)
3. Cards com piloto/equipe/tempo
Usa `@st.cache_resource` (service singleton) e `@st.cache_data` (resultados por sessão).

---

## 4. Configuração e Qualidade

### 4.1 `pyproject.toml` essencial
Conforme [SKILL.md §2.5 e §4.2](.claude/SKILL.md): pacote `f1` em `src/`, grupos `dev` e `docs`, configuração Ruff (`line-length=88`, regras `E,W,F,I,B,C4,UP,N`, `known-first-party=["f1"]`) e `pytest` (`testpaths=["tests"]`, `--cov=src/f1 --cov-fail-under=50`).

### 4.2 `.env.example`
```
OPENF1_BASE_URL=https://api.openf1.org/v1
OPENF1_TIMEOUT=10
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 4.3 `.pre-commit-config.yaml`
Hooks: `ruff` (`--fix`), `ruff-format`, `detect-secrets`, `trailing-whitespace`, `check-yaml`, `check-toml`.

### 4.4 Padrões obrigatórios
- Type hints em todas as funções públicas ([SKILL.md §7.1](.claude/SKILL.md))
- `get_logger(__name__)` ao invés de `print` ([SKILL.md §7.2](.claude/SKILL.md))
- Imports absolutos `from f1.<pkg>...` ([SKILL.md §9.2](.claude/SKILL.md))
- Nomenclatura: `snake_case` p/ funções e módulos, `PascalCase` p/ classes ([SKILL.md §9.1](.claude/SKILL.md))

---

## 5. Testes

### 5.1 Unitários (`tests/unit/`)
- `test_lap_processor.py` — funções puras, sem mocks
- `test_models.py` — parsing de payloads OpenF1 (fixtures JSON com exemplos da [doc_api.md](.claude/doc_api.md))
- `test_services.py` — `F1DashboardService` com repos `MagicMock`
- `test_http_client.py` — `httpx.MockTransport` para simular retry/timeout

### 5.2 Integração (`tests/integration/`)
- `test_openf1_live.py` — marcado `@pytest.mark.integration`, atinge `session_key=latest` para Meetings/Sessions/Drivers/Laps. Roda fora do CI padrão.

### 5.3 Meta
- Cobertura ≥ **50%** (alvo realista: 70%+).
- Execução: `poetry run pytest tests/unit/` e `poetry run pytest tests/integration/ -m integration`.

---

## 6. Documentação (MkDocs Material)

Páginas mínimas obrigatórias ([SKILL.md §6.2](.claude/SKILL.md)):
- `index.md` — propósito, link p/ OpenF1
- `architecture.md` — diagrama em camadas e fluxo de injeção
- `project-structure.md` — árvore comentada
- `running-locally.md` — Poetry + `streamlit run`
- `running-tests.md` — pytest e cobertura
- `contributing.md` — checklist de PR

`mkdocs.yml`: tema Material, idioma `pt`, navegação por abas.

---

## 7. Plano de Execução (ordem)

1. **Bootstrap**: `poetry init`, configurar `pyproject.toml`, `.gitignore`, `.env.example`, `.pre-commit-config.yaml`.
2. **Utils**: `logger.py`, `config.py`.
3. **Domain**: `models.py` → `repositories.py` → `services.py`.
4. **Processing**: `lap_processor.py` + testes unitários (funções puras, primeiros testes verdes).
5. **Ingestion**: `http_client.py` → `openf1_client.py` + testes com `MockTransport`.
6. **Service tests**: mocks dos repos cobrindo `F1DashboardService`.
7. **Dashboard**: `dashboard.py` (Streamlit) com caching.
8. **Docs**: páginas MkDocs + `mkdocs.yml`.
9. **CI/Pre-commit**: instalar hooks, garantir `ruff check .` e `pytest` verdes.
10. **README.md** ASCII-only com guia rápido.

---

## 8. Verificação Fim-a-Fim

```bash
poetry install --with dev
poetry run ruff check .                       # zero erros
poetry run pytest tests/unit/                 # todos passando, cov >= 50%
poetry run pytest tests/integration/ -m integration   # opcional, requer internet
poetry run streamlit run src/f1/dashboard.py  # abrir em http://localhost:8501
poetry run mkdocs serve                       # docs em http://127.0.0.1:8000
```

Critério de "pronto":
- Lint 100% verde
- Cobertura ≥ 50%
- Dashboard renderiza Top 10 voltas para uma sessão real (`session_key=latest`)
- Documentação acessível localmente

---

## 9. Arquivos Críticos a Criar

- [pyproject.toml](pyproject.toml)
- [src/f1/domain/models.py](src/f1/domain/models.py)
- [src/f1/domain/repositories.py](src/f1/domain/repositories.py)
- [src/f1/domain/services.py](src/f1/domain/services.py)
- [src/f1/processing/lap_processor.py](src/f1/processing/lap_processor.py)
- [src/f1/ingestion/http_client.py](src/f1/ingestion/http_client.py)
- [src/f1/ingestion/openf1_client.py](src/f1/ingestion/openf1_client.py)
- [src/f1/dashboard.py](src/f1/dashboard.py)
- [tests/unit/test_lap_processor.py](tests/unit/test_lap_processor.py)
- [mkdocs.yml](mkdocs.yml)
