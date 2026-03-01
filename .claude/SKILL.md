# SKILL.md — Padrões e Boas Práticas de Engenharia de Dados

> **Documento oficial do time de Engenharia de Dados.**
> Este guia define os padrões obrigatórios de desenvolvimento, qualidade de código, testes, documentação e fluxo de trabalho. Toda contribuição ao repositório deve estar em conformidade com as diretrizes aqui estabelecidas.

---

## Sumário

1. [Estrutura de Diretórios](#1-estrutura-de-diretórios)
2. [Gerenciamento de Ambiente com Poetry](#2-gerenciamento-de-ambiente-com-poetry)
3. [Modularização e Arquitetura](#3-modularização-e-arquitetura)
4. [Qualidade de Código](#4-qualidade-de-código)
5. [Testes](#5-testes)
6. [Documentação](#6-documentação)
7. [Boas Práticas Adicionais](#7-boas-práticas-adicionais)
8. [Padrões de Pull Request](#8-padrões-de-pull-request)
9. [Convenções de Nomenclatura](#9-convenções-de-nomenclatura)

---

## 1. Estrutura de Diretórios

Todo projeto deve seguir obrigatoriamente a estrutura abaixo. Desvios precisam de justificativa técnica documentada e aprovação do time.

```
projeto/
├── pyproject.toml          # Configuração central do projeto e dependências
├── poetry.lock             # Lock file gerado pelo Poetry (não editar manualmente)
├── .env.example            # Exemplo de variáveis de ambiente (sem valores reais)
├── .gitignore              # Arquivos e diretórios ignorados pelo Git
├── .pre-commit-config.yaml # Configuração de hooks de pre-commit (recomendado)
├── README.md               # Visão geral e guia de início rápido
├── src/
│   └── projeto/
│       ├── __init__.py
│       ├── ingestion/      # Camada de ingestão de dados
│       │   └── __init__.py
│       ├── processing/     # Camada de processamento e transformação
│       │   └── __init__.py
│       ├── domain/         # Regras de negócio e entidades de domínio
│       │   └── __init__.py
│       └── utils/          # Utilitários transversais (logging, config, helpers)
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── unit/               # Testes unitários isolados
│   │   └── __init__.py
│   └── integration/        # Testes de integração com dependências externas
│       └── __init__.py
└── docs/
    ├── mkdocs.yml          # Configuração do MkDocs
    └── docs/
        ├── index.md
        ├── architecture.md
        ├── project-structure.md
        ├── running-locally.md
        ├── running-tests.md
        └── contributing.md
```

---

## 2. Gerenciamento de Ambiente com Poetry

### 2.1 Obrigatoriedade

O uso do **Poetry** é obrigatório para gerenciamento de dependências e ambientes virtuais. O uso direto de `pip install` é **estritamente proibido** em qualquer etapa do projeto.

> **Razão:** O Poetry garante ambientes reproduzíveis, resolução determinística de dependências via `poetry.lock` e versionamento semântico consistente.

### 2.2 Instalação do Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verifique a instalação:

```bash
poetry --version
```

### 2.3 Comandos Essenciais

#### Instalação do projeto

```bash
# Instalar todas as dependências definidas no pyproject.toml
poetry install

# Instalar apenas dependências de produção (sem as de desenvolvimento)
poetry install --only main
```

#### Adição de dependências

```bash
# Adicionar dependência de produção
poetry add pandas

# Adicionar dependência de desenvolvimento
poetry add --group dev pytest ruff

# Adicionar dependência de documentação
poetry add --group docs mkdocs-material
```

#### Execução de comandos no ambiente virtual

```bash
# Executar scripts e ferramentas sem ativar o shell
poetry run python src/projeto/main.py
poetry run pytest
poetry run ruff check .
```

#### Ativação do ambiente virtual

```bash
# Ativar o shell do ambiente virtual (uso local/interativo)
poetry shell
```

#### Atualização de dependências

```bash
# Atualizar todas as dependências dentro dos constraints definidos
poetry update

# Atualizar uma dependência específica
poetry update pandas
```

### 2.4 Versionamento Semântico

O campo `version` no `pyproject.toml` deve seguir o padrão **SemVer** (`MAJOR.MINOR.PATCH`):

| Tipo de mudança | Ação |
|---|---|
| Breaking change na API pública | Incrementar `MAJOR` |
| Nova funcionalidade retrocompatível | Incrementar `MINOR` |
| Correção de bug retrocompatível | Incrementar `PATCH` |

### 2.5 Configuração mínima do `pyproject.toml`

```toml
[tool.poetry]
name = "projeto"
version = "0.1.0"
description = "Descrição objetiva do projeto"
authors = ["Time de Engenharia de Dados <data-eng@empresa.com>"]
readme = "README.md"
packages = [{ include = "projeto", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-cov = "^5.0"
ruff = "^0.4"

[tool.poetry.group.docs.dependencies]
mkdocs-material = "^9.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## 3. Modularização e Arquitetura

### 3.1 Separação por Camadas

O código deve ser organizado em camadas com responsabilidades bem definidas. Cada camada deve ser coesa e ter acoplamento mínimo com as demais.

| Camada | Responsabilidade |
|---|---|
| `ingestion/` | Conexão com fontes de dados, leitura e carregamento bruto |
| `processing/` | Transformações, limpeza, enriquecimento e agregações |
| `domain/` | Modelos de domínio, regras de negócio, validações |
| `utils/` | Configurações, logging, helpers genéricos reutilizáveis |

### 3.2 Funções Pequenas e Reutilizáveis

- Cada função deve ter **uma única responsabilidade** (Princípio da Responsabilidade Única).
- Funções devem ser testáveis de forma isolada.
- Prefira composição de funções a funções longas e complexas.

```python
# Correto: funções pequenas e compostas
def extract_raw_data(source_path: str) -> pd.DataFrame:
    return pd.read_parquet(source_path)


def filter_active_records(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["status"] == "active"]


def load_to_warehouse(df: pd.DataFrame, table_name: str) -> None:
    # lógica de carregamento
    ...


def run_pipeline(source_path: str, table_name: str) -> None:
    raw = extract_raw_data(source_path)
    filtered = filter_active_records(raw)
    load_to_warehouse(filtered, table_name)
```

### 3.3 Proibições

- Scripts monolíticos com lógica de negócio, I/O e transformações misturadas são **proibidos**.
- A camada de `ingestion/` não deve conter regras de negócio.
- A camada de `domain/` não deve ter dependências de infraestrutura (banco, S3, APIs).

### 3.4 Separação entre Regra de Negócio e Infraestrutura

Use **injeção de dependência** e **abstrações** para desacoplar regras de negócio de implementações de infraestrutura. Isso viabiliza testes unitários sem dependências externas.

```python
# domain/services.py
from abc import ABC, abstractmethod
import pandas as pd


class DataRepository(ABC):
    @abstractmethod
    def fetch(self, query: str) -> pd.DataFrame:
        ...


class SalesService:
    def __init__(self, repository: DataRepository) -> None:
        self._repository = repository

    def get_monthly_revenue(self, month: int, year: int) -> float:
        df = self._repository.fetch(f"SELECT * FROM sales WHERE month={month}")
        return df["revenue"].sum()
```

---

## 4. Qualidade de Código

### 4.1 PEP 8

O padrão **PEP 8** é obrigatório. O cumprimento é verificado automaticamente pelo Ruff. Código fora do padrão não deve ser submetido em Pull Request.

### 4.2 Ruff — Linter, Formatter e Organização de Imports

O **Ruff** é a ferramenta oficial do time para lint, formatação e organização automática de imports. Sua configuração deve estar centralizada no `pyproject.toml`.

#### Configuração obrigatória no `pyproject.toml`

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort (organização de imports)
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "N",   # pep8-naming
]
ignore = [
    "E501",  # line too long (gerenciado pelo formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["projeto"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

#### Comandos de uso

```bash
# Verificar lint sem alterar arquivos
poetry run ruff check .

# Aplicar correções automáticas
poetry run ruff check . --fix

# Formatar código
poetry run ruff format .

# Verificar formatação sem alterar
poetry run ruff format . --check
```

### 4.3 Critério de Aprovação

O código **deve passar 100% no lint** (`ruff check .` sem erros) antes de abrir um Pull Request. Pipelines de CI devem bloquear merges com falha de lint.

---

## 5. Testes

### 5.1 Framework Obrigatório

O uso do **pytest** é obrigatório. Testes devem ser executados exclusivamente via Poetry:

```bash
poetry run pytest
```

### 5.2 Cobertura Mínima

A cobertura mínima obrigatória é de **50%**. Projetos novos devem atingir esse patamar antes da primeira entrega. Reduções de cobertura em PRs devem ser justificadas.

Configuração do `pytest-cov` no `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/projeto --cov-report=term-missing --cov-fail-under=50"
```

Executar com relatório de cobertura:

```bash
poetry run pytest --cov=src/projeto --cov-report=html
```

### 5.3 Testes Unitários

- Devem ser **isolados**: sem acesso a banco de dados, sistemas de arquivos reais ou APIs externas.
- Utilize `unittest.mock` ou `pytest-mock` para simular dependências externas.
- Devem ser rápidos (< 1s por teste).

```python
# tests/unit/test_sales_service.py
from unittest.mock import MagicMock
import pandas as pd
import pytest
from projeto.domain.services import SalesService


@pytest.fixture
def mock_repository() -> MagicMock:
    repo = MagicMock()
    repo.fetch.return_value = pd.DataFrame({"revenue": [100.0, 200.0, 300.0]})
    return repo


def test_get_monthly_revenue_returns_sum(mock_repository: MagicMock) -> None:
    service = SalesService(repository=mock_repository)
    result = service.get_monthly_revenue(month=1, year=2024)
    assert result == 600.0
```

### 5.4 Testes de Integração

- Devem residir exclusivamente em `tests/integration/`.
- Podem interagir com sistemas externos (bancos de dados de teste, arquivos reais).
- Devem ser explicitamente marcados para controle de execução:

```python
# tests/integration/test_database.py
import pytest

@pytest.mark.integration
def test_database_connection() -> None:
    ...
```

Execute apenas testes unitários em CI padrão:

```bash
poetry run pytest tests/unit/
```

Execute testes de integração separadamente quando necessário:

```bash
poetry run pytest tests/integration/ -m integration
```

### 5.5 Fixtures

- Use fixtures para configuração compartilhada entre testes.
- Fixtures de escopo amplo (`session`, `module`) devem ser definidas em `conftest.py`.

```python
# tests/conftest.py
import pytest
import pandas as pd


@pytest.fixture(scope="module")
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10.0, 20.0, 30.0],
        "status": ["active", "inactive", "active"],
    })
```

---

## 6. Documentação

### 6.1 Ferramenta Obrigatória

O uso do **MkDocs com o tema Material** (`mkdocs-material`) é obrigatório para documentação técnica.

```bash
# Iniciar servidor local de documentação
poetry run mkdocs serve

# Gerar build estático
poetry run mkdocs build
```

### 6.2 Conteúdo Mínimo Obrigatório

Todo projeto deve conter, no mínimo, as seguintes páginas de documentação:

| Página | Arquivo | Conteúdo esperado |
|---|---|---|
| Visão Geral | `docs/index.md` | Propósito, contexto e links rápidos |
| Arquitetura | `docs/architecture.md` | Diagrama de componentes, decisões técnicas |
| Estrutura do Projeto | `docs/project-structure.md` | Árvore de diretórios comentada |
| Como Rodar Local | `docs/running-locally.md` | Pré-requisitos, instalação e execução passo a passo |
| Como Rodar Testes | `docs/running-tests.md` | Comandos de teste, flags e interpretação de cobertura |
| Como Contribuir | `docs/contributing.md` | Fluxo de PR, padrões e checklist |

### 6.3 Configuração Mínima do `mkdocs.yml`

```yaml
site_name: Nome do Projeto
site_description: Descrição técnica do projeto
repo_url: https://github.com/empresa/projeto
repo_name: empresa/projeto

theme:
  name: material
  language: pt
  features:
    - navigation.tabs
    - navigation.sections
    - content.code.copy

nav:
  - Início: index.md
  - Arquitetura: architecture.md
  - Estrutura do Projeto: project-structure.md
  - Como Rodar Local: running-locally.md
  - Como Rodar Testes: running-tests.md
  - Como Contribuir: contributing.md

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - admonition
```

### 6.4 Versionamento da Documentação

A documentação deve ser **versionada junto ao código** no mesmo repositório. Mudanças que alterem comportamento, arquitetura ou contratos de interface devem ser acompanhadas de atualização da documentação no mesmo Pull Request.

---

## 7. Boas Práticas Adicionais

### 7.1 Tipagem Estática (Type Hints)

O uso de **type hints** é obrigatório em todas as funções e métodos. O Ruff valida violações de nomenclatura; para validação de tipos em runtime, o uso de `mypy` é recomendado.

```python
# Correto
def calculate_average(values: list[float]) -> float:
    return sum(values) / len(values)


# Proibido
def calculate_average(values):
    return sum(values) / len(values)
```

### 7.2 Logging Estruturado

O uso de `print()` para fins de logging é **proibido** em código de produção. Utilize o módulo `logging` da biblioteca padrão com configuração estruturada.

```python
# utils/logger.py
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

Uso:

```python
from projeto.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Pipeline iniciado", extra={"source": "s3://bucket/path"})
logger.error("Falha na conexão com o banco de dados")
```

### 7.3 Variáveis de Ambiente e `.env`

- **Nunca hardcode** credenciais, URLs de banco de dados, chaves de API ou qualquer configuração sensível no código.
- Utilize variáveis de ambiente carregadas via `python-dotenv`.
- Mantenha um arquivo `.env.example` no repositório com todas as variáveis necessárias, **sem valores reais**.
- O arquivo `.env` deve estar no `.gitignore`.

```bash
# .env.example
DATABASE_URL=postgresql://user:password@host:5432/dbname
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
ENVIRONMENT=development
```

```python
# utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.environ["DATABASE_URL"]
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
```

### 7.4 Não Commitar Secrets

- Adicione ao `.gitignore`: `.env`, `*.pem`, `*.key`, `credentials.json`, `*.secret`.
- Configure um hook de pre-commit com `detect-secrets` para prevenção ativa.
- Em caso de vazamento acidental de secret, trate como incidente de segurança imediato: revogue a credencial e notifique o time.

### 7.5 Pre-commit (Recomendado)

O uso de `pre-commit` é recomendado para garantir qualidade antes de cada commit local.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
```

Instalação:

```bash
poetry add --group dev pre-commit
poetry run pre-commit install
```

### 7.6 Separação de Ambientes

O projeto deve suportar pelo menos três ambientes distintos:

| Ambiente | Propósito |
|---|---|
| `development` | Desenvolvimento local, dados sintéticos ou amostras |
| `staging` | Validação em ambiente espelho de produção |
| `production` | Ambiente produtivo com dados reais |

A variável `ENVIRONMENT` deve controlar comportamentos específicos por ambiente, como nível de log, endpoints e configurações de performance.

---

## 8. Padrões de Pull Request

### 8.1 Critérios Obrigatórios para Aprovação

Um Pull Request só pode ser aprovado e mergeado se **todos** os critérios abaixo forem atendidos:

- [ ] O código passa 100% no lint: `poetry run ruff check .` sem erros.
- [ ] O código passa em todos os testes: `poetry run pytest` sem falhas.
- [ ] A cobertura de testes não cai abaixo do mínimo definido (50%).
- [ ] O PR contém descrição clara do que foi alterado e por quê.
- [ ] A documentação foi atualizada, se aplicável.
- [ ] Nenhum secret ou dado sensível foi incluído.

### 8.2 Proibições

- **Merge direto na branch `main` é proibido.** Todo código deve passar por Pull Request.
- Não é permitido fazer bypass de checks de CI (`--no-verify` ou equivalente).
- Não é permitido aprovar o próprio Pull Request.

### 8.3 Estrutura da Descrição do PR

```markdown
## O que foi feito
Descrição objetiva das mudanças realizadas.

## Por que foi feito
Contexto técnico ou de negócio que justifica a alteração.

## Como testar
Passo a passo para validar as mudanças localmente.

## Checklist
- [ ] Lint passou (`poetry run ruff check .`)
- [ ] Testes passaram (`poetry run pytest`)
- [ ] Documentação atualizada (se aplicável)
- [ ] Sem secrets no código
```

---

## 9. Convenções de Nomenclatura

### 9.1 Padrões por Elemento

| Elemento | Padrão | Exemplo |
|---|---|---|
| Variáveis | `snake_case` | `total_records`, `raw_dataframe` |
| Funções | `snake_case` | `extract_data()`, `calculate_revenue()` |
| Métodos de classe | `snake_case` | `self.fetch_records()` |
| Classes | `PascalCase` | `DataIngestionService`, `SalesRepository` |
| Constantes | `UPPER_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Módulos/arquivos | `snake_case` | `data_loader.py`, `sales_service.py` |
| Pacotes/diretórios | `snake_case` | `ingestion/`, `data_processing/` |

### 9.2 Imports Absolutos

O uso de **imports absolutos** é obrigatório. Imports relativos são proibidos, pois dificultam a rastreabilidade e refatorações.

```python
# Correto: import absoluto
from projeto.domain.services import SalesService
from projeto.utils.logger import get_logger

# Proibido: import relativo
from ..domain.services import SalesService
from .logger import get_logger
```

### 9.3 Organização de Imports

A ordem de imports deve ser mantida automaticamente pelo Ruff (`isort`):

1. Imports da biblioteca padrão (`os`, `sys`, `logging`, etc.)
2. Imports de bibliotecas de terceiros (`pandas`, `boto3`, `pydantic`, etc.)
3. Imports internos do projeto (`from projeto.utils...`)

```python
# Correto: ordem gerenciada pelo Ruff
import os
from datetime import datetime

import pandas as pd
from pydantic import BaseModel

from projeto.domain.models import SalesRecord
from projeto.utils.logger import get_logger
```

---

*Documento mantido pelo time de Engenharia de Dados. Última revisão: 2026-03-01. Para sugestões ou dúvidas, abra uma issue no repositório ou entre em contato com o tech lead do time.*
