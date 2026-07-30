

# This document contains all Postgres(docker) related commands used in this project along with their purpose.

# PostgreSQL Commands

Open PostgreSQL shell

```bash
docker compose exec db psql -U postgres -d ShopOnBot_db
```

---

Show tables

```sql
\dt
```

---

Describe table

```sql
\d users
```

---

Exit PostgreSQL

```sql
\q
```

---

# Redis

Redis container shell

```bash
docker compose exec redis sh