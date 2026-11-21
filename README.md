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

Setup instructions land with the backend skeleton. See `CONTRIBUTING.md` for
branch naming, commit style and the PR flow.
