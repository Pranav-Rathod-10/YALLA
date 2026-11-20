# 0005. Transactional outbox for alerts and push

- Status: Accepted
- Proposed by: Akash · Date: 2026-11-21

## Context
Accepting a request must change seats and notify the requester. Sending a push inside the
HTTP request is slow and is lost if the process dies; sending it before commit can notify
about a change that rolled back.

## Decision
Services insert an `alerts` row and an `outbox` row in the same transaction as the
business change. An arq worker reads unprocessed outbox rows with
`FOR UPDATE SKIP LOCKED`, delivers them, and marks them processed.

## Consequences
At-least-once delivery; consumers must be idempotent. The outbox is the seam for a future
notifications service.
