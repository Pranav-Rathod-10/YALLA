# 0003. PostgreSQL + PostGIS, geo match instead of text match

- Status: Accepted
- Proposed by: Akash · Date: 2026-11-21

## Context
Spec 7.3 filters trips by case-insensitive substring on place names. That breaks on
spelling variants (`Panjim` / `Panaji`), on nearby places (`Calangute` vs `Baga`) and
cannot support "Current location". The app is also no longer Goa-only.

## Decision
Store every place with a `geography(Point)`. Filter trips by distance
(`ST_DWithin`, default 3 km) from a chosen place or from GPS coordinates. Keep the text
match only as a fallback when the client sends free text.

## Consequences
Needs the PostGIS extension in every environment (the Docker image includes it).
