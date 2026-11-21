# 0006. Store departures as instant + timezone

- Status: Accepted
- Proposed by: Akash · Date: 2026-11-21

## Context
The spec's sample data stores `when: 'Sat, 22 Nov · 6:00 AM - 6:30 AM'` and `startMin`
(minutes since midnight). Minutes-since-midnight cannot express "within an hour" across
midnight and has no date or timezone.

## Decision
A trip stores `departs_at timestamptz` (start of the window), `window_minutes`, and the
IANA `timezone` of the pickup place. Clients receive ISO timestamps and format them locally.

## Consequences
Time filters become a range query on one indexed column. Display strings are a client concern.
