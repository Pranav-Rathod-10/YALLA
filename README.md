# YALLA

Cab sharing app. Post a cab trip, let others request a seat, split the fare.
Works in any city.

> Status: early experiment, built to production standards.

## What's in here

| Path | What | Owner |
|---|---|---|
| `services/api` | Python backend (FastAPI + PostgreSQL/PostGIS + Redis) | @kadeep47 |
| `apps/web` | Thin web client (Vite + React + TypeScript) | @Pranav-Rathod-10 |
| `apps/mobile` | Mobile app (Expo + TypeScript), builds an Android APK | @Pranav-Rathod-10 |
| `packages/api-client` | TypeScript client generated from the backend's OpenAPI | shared |
| `docs/` | Spec, architecture, data flow, ADRs, feature tracker | shared |

## App pages (from the original brief)

Top pages: Home, Trips, Requests, Social (venues and events), Profile.

Other pages and sheets: Create cab trip, Filters, Trip card and details,
Notifications (Alerts), Chat (not designed yet).

## Getting started

```bash
make dev && make seed                 # API on :8000 with demo data, docs at /docs
pnpm install && pnpm --filter @yalla/web dev
```

Full setup, tests and configuration: [`docs/runbook.md`](docs/runbook.md).
How it fits together: [`docs/architecture/application.md`](docs/architecture/application.md),
[`docs/architecture/dataflow.md`](docs/architecture/dataflow.md).
Roadmap and ownership: [`docs/tracker/features.csv`](docs/tracker/features.csv).
Branches, commits, PRs: [`CONTRIBUTING.md`](CONTRIBUTING.md).
