# 0001. Monorepo with two thin frontends and one backend

- Status: Accepted
- Proposed by: Akash · Date: 2026-11-21

## Context
We need a web app, an Expo app (with an Android APK) and a backend. Akash owns the backend,
Pranav owns the frontends. A previous project with separate web and app frontends over a
common backend worked well.

## Decision
One repository: `apps/web`, `apps/mobile`, `services/api`, `packages/api-client`, `docs/`.
pnpm workspaces for TypeScript, uv for Python. CODEOWNERS routes reviews by folder.

## Consequences
- One PR can change the API and its generated client together.
- CI runs per path so a docs change doesn't run mobile builds.
- When a backend module becomes its own service it moves to `services/<name>`.
