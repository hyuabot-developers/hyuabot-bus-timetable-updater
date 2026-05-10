# hyuabot-bus-timetable-updater

A one-time data loader that fetches bus timetables from the public bus API and populates the HYUabot database. Runs once at initial deployment.

## Overview

The job calls the public bus timetable API for each tracked route and inserts schedule data into the `bus_timetable` table. Routes 62, 9090, 110, and 707 are excluded.

## Architecture

```
src/
├── main.py           # Entry point; fetches and inserts timetables for all routes
├── models.py         # SQLAlchemy ORM models (BusTimetable)
└── utils/
    └── database.py   # PostgreSQL engine factory
```

## Requirements

- Python ≥ 3.12
- PostgreSQL
- Public bus API key

## Environment Variables

| Variable            | Description              |
|---------------------|--------------------------|
| `BUS_API_KEY`       | Public bus API service key |
| `POSTGRES_ID`       | PostgreSQL username      |
| `POSTGRES_PASSWORD` | PostgreSQL password      |
| `POSTGRES_HOST`     | PostgreSQL host          |
| `POSTGRES_PORT`     | PostgreSQL port          |
| `POSTGRES_DB`       | PostgreSQL database name |

## Running Locally

```bash
pip install -e .

export BUS_API_KEY=your_api_key
export POSTGRES_ID=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=hyuabot

cd src && python main.py
```

## Docker

The container exits after a single run — trigger it as a Kubernetes Job or one-off container.

```bash
docker build -t hyuabot-bus-timetable-updater .

docker run --rm \
  -e BUS_API_KEY=your_api_key \
  -e POSTGRES_ID=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=hyuabot \
  hyuabot-bus-timetable-updater
```

## Development

```bash
pip install -e .[lint]       # flake8
pip install -e .[typecheck]  # mypy
pip install -e .[test]       # pytest
```

```bash
python -m flake8 src/ tests/
python -m mypy src/ tests/
python -m pytest -v
```

Tests run against a PostgreSQL instance at `localhost:25432`.

## CI/CD

| Workflow | Trigger | Jobs |
|---|---|---|
| `code-check.yml` | Push to any branch except `main` | lint, typecheck, test |
| `deploy.yml` | PR merged to `main` (or manual dispatch) | Docker build → push to `localhost:5000` |

CI runners: self-hosted X64 Linux (code checks) · ARM64 Linux (Docker build).

## License

GPLv3
