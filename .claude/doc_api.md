# OpenF1 API — Documentação Resumida

> Fonte oficial: https://openf1.org/docs

---

## Visão Geral

A **OpenF1** é uma API aberta e não-oficial que fornece dados de telemetria e temporização da Fórmula 1 em formato **JSON** ou **CSV**.

- **Dados históricos** (a partir de 2023): gratuitos, sem autenticação
- **Dados em tempo real**: requerem assinatura paga
- **URL base:** `https://api.openf1.org/v1/`

---

## Autenticação

Nenhuma autenticação necessária para dados históricos. Para acesso em tempo real, é necessária uma assinatura — consulte o site oficial.

---

## Filtragem e Dicas de Consulta

Todos os endpoints aceitam parâmetros de filtragem via query string.

| Operador | Exemplo |
|----------|---------|
| Igual | `driver_number=44` |
| Maior ou igual | `speed>=300` |
| Menor ou igual | `lap_duration<=90` |
| Maior que | `rpm>12000` |
| Menor que | `throttle<50` |

**Dicas úteis:**
- Use `session_key=latest` ou `meeting_key=latest` para obter dados da sessão/etapa mais recente
- Adicione `csv=true` a qualquer query para exportar em formato CSV
- Datas aceitam ISO 8601, texto ou formato relativo

---

## Endpoints

### 1. Car Data — Telemetria do Carro
**URL:** `https://api.openf1.org/v1/car_data`

Dados de telemetria do carro a ~3,7 Hz.

| Campo | Descrição |
|-------|-----------|
| `brake` | Freio: 100 (pressionado) ou 0 (solto) |
| `date` | Timestamp UTC (ISO 8601) |
| `driver_number` | Número do piloto |
| `drs` | Status do DRS (ver tabela abaixo) |
| `n_gear` | Marcha atual (0–8) |
| `rpm` | Rotação do motor |
| `speed` | Velocidade em km/h |
| `throttle` | Porcentagem de acelerador (0–99) |

**Exemplo:**
```
GET /v1/car_data?driver_number=55&session_key=9159&speed>=315
```

---

### 2. Drivers — Informações dos Pilotos
**URL:** `https://api.openf1.org/v1/drivers`

Dados dos pilotos por sessão, populados no início de cada sessão.

| Campo | Descrição |
|-------|-----------|
| `broadcast_name` | Nome de transmissão |
| `driver_number` | Número do piloto |
| `full_name` | Nome completo |
| `name_acronym` | Abreviação (ex: VER, HAM) |
| `team_name` | Nome da equipe |
| `team_colour` | Cor hexadecimal da equipe |
| `headshot_url` | URL da foto do piloto |

**Exemplo:**
```
GET /v1/drivers?driver_number=1&session_key=9158
```

---

### 3. Meetings — Etapas/Fins de Semana
**URL:** `https://api.openf1.org/v1/meetings`

Metadados sobre Grandes Prêmios ou testes. Atualizado diariamente à meia-noite UTC.

| Campo | Descrição |
|-------|-----------|
| `meeting_key` | Identificador único da etapa |
| `meeting_name` | Nome do GP |
| `country_name` | País |
| `circuit_short_name` | Nome curto do circuito |
| `location` | Cidade/local |
| `date_start` | Data de início |
| `year` | Temporada |

**Exemplo:**
```
GET /v1/meetings?year=2026&country_name=Singapore
```

---

### 4. Sessions — Sessões
**URL:** `https://api.openf1.org/v1/sessions`

Períodos distintos de atividade na pista: treinos, classificação, corrida, sprint.

| Campo | Descrição |
|-------|-----------|
| `session_key` | Identificador único da sessão |
| `session_name` | Nome (Practice 1, Qualifying, Race...) |
| `session_type` | Tipo (Practice, Qualifying, Race) |
| `date_start` / `date_end` | Período da sessão |
| `country_name` | País |
| `year` | Temporada |

**Exemplo:**
```
GET /v1/sessions?country_name=Belgium&session_name=Sprint%20Qualifying&year=2023
```

---

### 5. Laps — Voltas
**URL:** `https://api.openf1.org/v1/laps`

Detalhes volta a volta: tempos de setor, velocidades e mini-setores.

| Campo | Descrição |
|-------|-----------|
| `lap_number` | Número da volta |
| `lap_duration` | Tempo total da volta (s) |
| `duration_sector_1/2/3` | Tempo de cada setor |
| `i1_speed` / `i2_speed` | Velocidade no ponto de medição |
| `st_speed` | Velocidade na linha de chegada |
| `segments_sector_1/2/3` | Mini-setores (array de cores) |
| `is_pit_out_lap` | Indica saída dos pits |

**Exemplo:**
```
GET /v1/laps?session_key=9161&driver_number=63&lap_number=8
```

---

### 6. Location — Localização no Circuito
**URL:** `https://api.openf1.org/v1/location`

Posição aproximada do carro no circuito em coordenadas 3D a ~3,7 Hz.

| Campo | Descrição |
|-------|-----------|
| `x` / `y` / `z` | Coordenadas no circuito |
| `date` | Timestamp UTC |
| `driver_number` | Piloto |

---

### 7. Position — Posição na Corrida
**URL:** `https://api.openf1.org/v1/position`

Mudanças de posição dos pilotos ao longo da sessão.

| Campo | Descrição |
|-------|-----------|
| `position` | Posição atual |
| `date` | Timestamp da mudança |
| `driver_number` | Piloto |

---

### 8. Intervals — Intervalos
**URL:** `https://api.openf1.org/v1/intervals`

Gap entre pilotos e para o líder, atualizado a cada ~4 segundos.

| Campo | Descrição |
|-------|-----------|
| `gap_to_leader` | Intervalo para o 1º colocado |
| `interval` | Intervalo para o carro à frente |
| `date` | Timestamp |
| `driver_number` | Piloto |

> Requer assinatura para dados em tempo real.

---

### 9. Pit — Paradas nos Pits
**URL:** `https://api.openf1.org/v1/pit`

Informações sobre cada parada no pit lane.

| Campo | Descrição |
|-------|-----------|
| `lap_number` | Volta em que entrou nos pits |
| `pit_duration` | Duração total da parada (s) |
| `driver_number` | Piloto |

---

### 10. Stints — Stints de Pneus
**URL:** `https://api.openf1.org/v1/stints`

Períodos de corrida por conjunto de pneus.

| Campo | Descrição |
|-------|-----------|
| `compound` | Composto (SOFT, MEDIUM, HARD, etc.) |
| `lap_start` / `lap_end` | Voltas do stint |
| `tyre_age_at_start` | Idade do pneu no início do stint |
| `driver_number` | Piloto |

---

### 11. Race Control — Controle de Corrida
**URL:** `https://api.openf1.org/v1/race_control`

Mensagens da direção de prova: bandeiras, safety car, incidentes, status de sessão.

| Campo | Descrição |
|-------|-----------|
| `category` | Tipo (Flag, SafetyCar, SessionStatus, CarEvent) |
| `flag` | Bandeira (GREEN, YELLOW, RED, CHEQUERED...) |
| `message` | Mensagem da direção |
| `driver_number` | Piloto envolvido (se aplicável) |
| `date` | Timestamp |

---

### 12. Weather — Clima
**URL:** `https://api.openf1.org/v1/weather`

Condições climáticas na pista, atualizadas a cada minuto.

| Campo | Descrição |
|-------|-----------|
| `air_temperature` | Temperatura do ar (°C) |
| `track_temperature` | Temperatura da pista (°C) |
| `humidity` | Umidade relativa (%) |
| `wind_speed` | Velocidade do vento (m/s) |
| `wind_direction` | Direção do vento (graus) |
| `rainfall` | Indicador de chuva (0/1) |
| `pressure` | Pressão atmosférica (mbar) |

---

### 13. Team Radio — Rádio de Equipe
**URL:** `https://api.openf1.org/v1/team_radio`

Trechos selecionados de comunicação entre pilotos e engenheiros.

| Campo | Descrição |
|-------|-----------|
| `recording_url` | URL do áudio |
| `date` | Timestamp |
| `driver_number` | Piloto |

---

### 14. Overtakes — Ultrapassagens
**URL:** `https://api.openf1.org/v1/overtakes`

Trocas de posição na pista e nos pits (somente corridas).

| Campo | Descrição |
|-------|-----------|
| `driver_number_ahead` | Piloto que ficou à frente |
| `driver_number_behind` | Piloto que ficou atrás |
| `lap_number` | Volta da ultrapassagem |

---

### 15. Starting Grid — Grid de Largada
**URL:** `https://api.openf1.org/v1/starting_grid`

Posições de largada com tempos da volta de classificação.

| Campo | Descrição |
|-------|-----------|
| `position` | Posição no grid |
| `driver_number` | Piloto |
| `lap_time` | Tempo da volta de classificação |

---

### 16. Session Result — Resultado da Sessão
**URL:** `https://api.openf1.org/v1/session_result`

Classificação final por sessão.

| Campo | Descrição |
|-------|-----------|
| `position` | Posição final |
| `driver_number` | Piloto |
| `gap_to_leader` | Intervalo para o vencedor |
| `laps_completed` | Voltas completadas |
| `status` | DNF, DNS, DSQ ou vazio (finalizou) |

---

### 17. Championship Drivers — Campeonato de Pilotos *(beta)*
**URL:** `https://api.openf1.org/v1/championship_drivers`

Pontuação dos pilotos no campeonato. Disponível apenas para sessões de corrida.

| Campo | Descrição |
|-------|-----------|
| `driver_number` | Piloto |
| `points` | Pontos acumulados |
| `position` | Posição no campeonato |

---

### 18. Championship Teams — Campeonato de Construtores *(beta)*
**URL:** `https://api.openf1.org/v1/championship_teams`

Pontuação das equipes no campeonato. Disponível apenas para sessões de corrida.

| Campo | Descrição |
|-------|-----------|
| `team_name` | Nome da equipe |
| `points` | Pontos acumulados |
| `position` | Posição no campeonato |

---

## Referência: Status do DRS

| Valor | Status |
|-------|--------|
| 0, 1 | Desligado |
| 8 | Detectado / elegível na zona |
| 10, 12, 14 | Ligado |
| 2, 3, 9 | Desconhecido |

---

## Referência: Cores dos Mini-Setores (Segments)

| Valor | Cor | Significado |
|-------|-----|-------------|
| 2048 | Amarelo | Setor normal |
| 2049 | Verde | Melhor setor pessoal |
| 2051 | Roxo | Melhor setor geral (fastest) |

---

## Exportação CSV

Adicione `csv=true` a qualquer endpoint para receber os dados em CSV:

```
GET /v1/laps?session_key=latest&csv=true
```
