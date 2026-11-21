# CLAUDE.md

Guidance for AI coding agents (Claude Code and others) working in this repo.

## Project
Yalla: cab trip-sharing app. Backend in Python (`services/api`), thin web (`apps/web`) and
Expo mobile (`apps/mobile`) clients, generated TS client (`packages/api-client`).
Read `docs/architecture/application.md` and `docs/architecture/dataflow.md` first.

## Sources of truth
- Product behaviour: `docs/spec/frontend-spec.md` (+ `prototype.html`).
- Where the backend deliberately differs from the spec: `docs/adr/` and `docs/spec/README.md`.
- API contract: FastAPI OpenAPI (`/openapi.json`), never hand-written TS types.

## Rules
- Follow `CONTRIBUTING.md`: branch `<type>/<YYYY-MM-DD>_dev_<slug>`, Conventional Commits, one thing per PR.
- Business rules live in `services/api/app/services/`. Routes stay thin.
- Every rule from spec section 12 needs a test.
- Never invent product behaviour listed in spec section 13 ("not designed yet"); add a
  proposal in `docs/proposals/` instead.
- Update `CHANGELOG.md` and `docs/tracker/features.csv` in the same PR.
- Do not commit secrets; `.env` is git-ignored, use `.env.example`.

## Commands
```bash
make dev        # docker compose up: db, redis, migrate, api, worker
make seed       # multi-city demo data
make test       # backend tests (needs a PostGIS database, see docs/runbook.md)
make lint       # pre-commit on all files
pnpm gen:api    # regenerate packages/api-client after any route/schema change
```
