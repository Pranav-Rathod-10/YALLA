# 0007. Enforce Females-only on the server

- Status: Proposed (open question 14 in the spec is still with the owner)
- Proposed by: Akash · Date: 2026-11-21

## Context
The prototype only shows a label. A label alone lets anyone request, including through
Instant join.

## Decision (default until the owner decides)
- Females-only trips are **visible to everyone**.
- Only users whose profile gender is `female` can request or instant-join; others get
  `403 females_only` and the API returns `can_request: false` so clients can explain why.
- `gender_verified` exists on the user but is not required yet. Turning it on is a config
  flag (`FEMALES_ONLY_REQUIRE_VERIFIED`).

## Consequences
Self-declared gender is weak. Verification is needed before relying on this for safety.
