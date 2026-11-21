# GitHub repository settings

Settings as code. Applying them needs **admin** on the repo.

```bash
REPO=Pranav-Rathod-10/YALLA ./infra/github/apply.sh
```

| Ruleset | Branch | What it enforces |
|---|---|---|
| `protect-main` | `main` | PR only, 1 approval from a code owner, CI green, no force-push or delete, merge commits only |
| `protect-dev` | `dev` | PR only, `pre-commit` check green, no force-push or delete |
| `branch-naming` | everything else | `<type>/<YYYY-MM-DD>_dev_<slug>` (may be unavailable on personal plans; the script skips it) |

Repo settings: merge commits only (squash and rebase off), delete head branch after merge, auto-merge allowed.

Why merge commits only: feature branches are often stacked (each cut from the previous one).
Merging them in order with merge commits never conflicts. Squash-merging rewrites the
commits and makes every later branch in the stack conflict.
