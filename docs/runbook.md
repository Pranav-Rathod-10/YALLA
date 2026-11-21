# Runbook

## Prerequisites

```bash
brew install uv pnpm pre-commit
# Docker Desktop for Postgres/PostGIS and Redis
pre-commit install
pnpm install
```

## Run everything locally

```bash
make dev      # docker compose: db (PostGIS), redis, migrate, api (:8000), worker
make seed     # multi-city demo data (idempotent)
```

- API docs: <http://localhost:8000/docs> (Swagger), contract at `/openapi.json`
- Web: `pnpm --filter @yalla/web dev` → <http://localhost:5173>
- Mobile: `pnpm --filter @yalla/mobile start` (see `apps/mobile/README.md`)
- Sign in with a seeded phone (`+919800000001` … `+919800000005`); outside prod the API
  returns `dev_code`, and both clients fill it in.

## Backend without Docker for the API

```bash
docker compose -f infra/docker/compose.yaml up db redis
cd services/api
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
uv run arq app.workers.main.WorkerSettings   # outbox worker, second terminal
```

## Tests

```bash
docker compose -f infra/docker/compose.yaml exec db createdb -U yalla yalla_test   # once
cd services/api
YALLA_DATABASE_URL=postgresql+asyncpg://yalla:yalla@localhost:5432/yalla_test uv run pytest
```

Tests create the schema from the models once per session and truncate between tests. The
database needs the PostGIS extension (the compose image has it). CI runs the same suite plus
`alembic upgrade/check/downgrade`.

## Everyday changes

| Change | Then run |
|---|---|
| Model change | `make migration m="what changed"`, review the file, `make migrate` |
| Route or schema change | `pnpm gen:api` and commit `packages/api-client` (CI fails otherwise) |
| New env var | add it to `services/api/.env.example` and `app/core/config.py` |

## Configuration (`YALLA_*`)

| Variable | Default | Notes |
|---|---|---|
| `YALLA_ENV` | `dev` | `prod` hides `dev_code` and refuses the default JWT secret |
| `YALLA_DATABASE_URL` | local compose DB | `postgresql+asyncpg://…` |
| `YALLA_REDIS_URL` | `redis://localhost:6379/0` | OTP codes and the job queue |
| `YALLA_JWT_SECRET` | dev placeholder | **must** be set in prod, ≥ 32 bytes |
| `YALLA_FEMALES_ONLY_REQUIRE_VERIFIED` | `false` | ADR 0007 |
| `YALLA_CORS_ORIGINS` | web + Expo dev ports | JSON list |

## Repository settings (admin only)

```bash
REPO=Pranav-Rathod-10/YALLA ./infra/github/apply.sh
```

Merge commits only, branch protection on `main` and `dev`. See `infra/github/README.md`.

## Not done yet

- SMS provider for OTP, push provider (Expo Push) behind the outbox sender
- Deployment target (the API image is production-ready; pick a host and a managed Postgres with PostGIS)
- Rate limiting on OTP requests
- Spec §13 items (chat, payments, host trip management, ratings) — need product decisions first
