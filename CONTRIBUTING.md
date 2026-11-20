# Contributing

## Branches

```
main  <-  dev  <-  <type>/<YYYY-MM-DD>_dev_<slug>
```

- `main` is what ships. Only `dev` merges into it, through a release PR.
- `dev` is the integration branch. Every change reaches it through a PR.
- Work branches: `<type>/<YYYY-MM-DD>_dev_<slug>`, the date being the day the branch was cut.
  Examples: `feat/2026-11-21_dev_trip-filters`, `fix/2026-11-21_dev_time-filter-midnight`.

| Type | Use for |
|---|---|
| `feat` | New behaviour |
| `fix` | Bug fix |
| `refactor` | Code change with no behaviour change |
| `docs` | Documentation only |
| `chore` | Tooling, config, deps |
| `test` | Tests only |
| `ci` | Pipelines |
| `perf`, `build`, `revert` | As named |

## Commits

[Conventional Commits](https://www.conventionalcommits.org): `type(scope): summary`.
Scopes: `api`, `web`, `mobile`, `client`, `infra`, `spec`, `architecture`, `adr`.
The `commit-msg` hook rejects anything else.

## Pull requests

- One PR does one thing.
- Fill in the template (what, why, tests, tracker id).
- Update `CHANGELOG.md` (*Unreleased*) and the row in `docs/tracker/features.csv`.
- **Merge with "Create a merge commit"**, never squash. Branches are often stacked; merging
  stacked PRs in order with merge commits never conflicts.

## Setup

```bash
brew install uv pnpm pre-commit
pre-commit install
```

Backend and frontend setup: see `services/api/README.md`, `apps/web/README.md`,
`apps/mobile/README.md`.

## Proposing something bigger

Copy `docs/proposals/0000-template.md`, open a `docs/` PR, discuss there. Once agreed, record
the decision as an ADR in `docs/adr/`.
