# 0002. Python + FastAPI backend

- Status: Accepted
- Proposed by: Akash · Date: 2026-11-21

## Context
The backend owner is strongest in Python. The spec's frontend expects a JSON REST API with
typed models.

## Decision
FastAPI with Pydantic v2 and async SQLAlchemy 2, Alembic for migrations, arq for background
jobs. Tooling: uv, ruff (lint), black (format), mypy (strict), pytest.

## Alternatives
- Django + DRF: more batteries, but heavier and sync-first.
- Node/NestJS: one language across the repo, but not the owner's strength.

## Consequences
OpenAPI comes for free and drives the TS client (ADR 0004).
