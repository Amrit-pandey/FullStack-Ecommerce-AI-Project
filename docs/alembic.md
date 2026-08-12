

# This document contains all Alembic(docker), configuration, migration flow related commands used in this project along with their purpose.

# Alembic

---

## Install Alembic

```bash
uv add alembic
```

---

## Initialize Alembic

Run only once.

```bash
uv run alembic init alembic
```

This creates:

```
alembic/
alembic.ini
```

---

# Alembic Configuration

Changes made in `env.py`

Imported:

```python
from app.core.config import settings
from app.db.database import Base
from app.models import user
```

Metadata:

```python
target_metadata = Base.metadata
```

Database URL:

```python
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)
```

Async engine:

```python
async_engine_from_config(...)
```

Run async migrations:

```python
asyncio.run(run_async_migrations())
```

---

# Migration Workflow

## Step 1

Modify SQLAlchemy model.

Example:

```python
phone = mapped_column(...)
```

---

## Step 2

Generate migration.

```bash
uv run alembic revision --autogenerate -m "add phone column",
# if using docker, after -it (contaier name)
docker exec -it fastapi_app uv run alembic revision --autogenerate -m "add onboarding_status column in users table"
```

---

## Step 3

Review generated migration.

File:

```
alembic/versions/
```

Always verify:

- columns
- constraints
- enums
- nullable
- defaults

---

## Step 4

Apply migration

```bash
uv run alembic upgrade head
```

---

## Current Migration

```bash
uv run alembic current
```

---

## Migration History

```bash
uv run alembic history
```

---

## Downgrade One Revision

```bash
uv run alembic downgrade -1
```

---

## Downgrade to Base

```bash
uv run alembic downgrade base
```

---

# Recommended Migration Workflow

```
Modify Model
      ↓
Generate Migration
      ↓
Review Migration
      ↓
Upgrade Database
      ↓
Test API
```

Commands

```bash
uv run alembic revision --autogenerate -m "meaningful message"

uv run alembic upgrade head
```

---

# Verify Everything

## Current migration

```bash
uv run alembic current
```

---

# Useful Commands Cheat Sheet

# Generate migration
uv run alembic revision --autogenerate -m "message"

# Apply migration
uv run alembic upgrade head

# Current revision
uv run alembic current

# History
uv run alembic history