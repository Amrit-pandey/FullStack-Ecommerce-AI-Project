

# This document contains all Docker related commands used in this project along with their purpose.

Services running inside Docker:

- web (FastAPI)
- redis
- postgres

# Why `/app/.venv` Volume?

```yaml
volumes:
  - .:/app
  - /app/.venv
```

Purpose:

- Prevent host virtual environment from overwriting Docker virtual environment.
- Docker keeps its own isolated packages.
- VS Code unresolved imports issue gets fixed.


# Docker Commands

## Build project

Used first time or after Dockerfile changes.

```bash
docker compose up --build
```

---

## Start existing containers

```bash
docker compose up
```

---

## Stop containers

```bash
docker compose down
```

---

## Stop + Remove everything

```bash
docker compose down -v
```

Removes:

- Containers
- Networks
- PostgreSQL data volume

Use only when database reset is required.

---

## Run in background

```bash
docker compose up -d
```

---

# Container Commands

## Enter FastAPI container

```bash
docker compose exec web sh
```

---

## Enter PostgreSQL container

```bash
docker compose exec db sh
```

---

## Enter Redis container

```bash
docker compose exec redis sh
```

---

# Logs

FastAPI logs

```bash
docker compose logs web
```

Live logs

```bash
docker compose logs -f web
```

All services

```bash
docker compose logs
```

---

# Verify Python inside Docker

```bash
docker exec -it fastapi_app uv run python --version
```

---

# Verify uv Environment

```bash
uv run python -c "import sys; print(sys.executable)"
```

---


# Useful Commands Cheat Sheet

```bash
# Build project
docker compose up --build

# Start project
docker compose up

# Stop project
docker compose down

# Enter FastAPI
docker compose exec web sh

# FastAPI logs
docker compose logs -f web

# PostgreSQL shell
docker compose exec db psql -U postgres -d ShopOnBot_db

# Redis shell
docker compose exec redis sh