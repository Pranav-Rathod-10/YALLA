# 0004. Generate the TypeScript client from OpenAPI

- Status: Accepted
- Proposed by: Akash · Date: 2026-11-21

## Context
Two TypeScript clients consume a Python API. Hand-written types drift.

## Decision
`packages/api-client` is generated with `openapi-typescript` from the API's `/openapi.json`
and wrapped with `openapi-fetch`. Regenerate with `pnpm gen:api`. CI fails if the committed
schema is out of date.

## Consequences
Backend response models are the single source of truth for the contract.
