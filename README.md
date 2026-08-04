# F1 Dashboard


Dashboard interativo de Formula 1 desenvolvido com Streamlit, exibindo as 5 voltas mais rapidas por circuito usando dados em tempo real da API OpenF1.

Este projeto foi criado como parte de uma aula pratica de Python, com foco em boas praticas de desenvolvimento: arquitetura em camadas, testes automatizados, linting e documentacao.

## Tecnologias

- Python 3.14
- Streamlit — interface web interativa
- Pydantic v2 — validacao e modelagem de dados
- OpenF1 API — dados oficiais de Formula 1
- Poetry — gerenciamento de dependencias
- Pytest — testes unitarios
- Ruff — linting e formatacao

## Estrutura do Projeto

```
src/f1/
  dashboard.py          # Aplicacao Streamlit (entry point)
  domain/               # Modelos, repositorios e servicos
  ingestion/            # Clientes HTTP e integracao com OpenF1
  processing/           # Logica de processamento de voltas
  utils/                # Logger e configuracoes
tests/
  unit/                 # Testes unitarios (37 testes, cobertura >= 50%)
docs/                   # Documentacao com MkDocs Material
```

## Instalacao

```bash
poetry install --with dev
```

## Executar o Dashboard

```bash
poetry run streamlit run src/f1/dashboard.py
```

## Testes

```bash
poetry run pytest tests/unit/
```

## Lint

```bash
poetry run ruff check .
```

## Documentacao

```bash
# Servir localmente em http://127.0.0.1:8000
poetry run task docs

# Gerar build estatico
poetry run task docs-build
```
