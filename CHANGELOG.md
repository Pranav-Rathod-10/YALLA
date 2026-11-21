# Changelog

All notable changes to this project. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [SemVer](https://semver.org).

## [Unreleased]

### Added
- Repo scaffold: gitignore, editorconfig, PR and issue templates, CODEOWNERS (YAL-003).
- Pre-commit with ruff, black, prettier, gitleaks and a Conventional Commits check (YAL-004).
- GitHub rulesets and repo settings as code (YAL-005).
- Spec imported; app renamed from Bla Bla Goa to Yalla and widened to any city (YAL-001).
- Architecture, data flow, data model and API docs; ADRs 0001-0007 (YAL-006).
- Feature tracker CSV, proposal template, contributing guide.
- Join requests: send (optional 1024-char message), accept, decline, cancel, Sent/Received lists; instant join; row-locked seats (YAL-022).
- Females only enforced on the server (visible to all, only women can request or instant-join); can_request on trip responses (YAL-023, ADR 0007).
- Events list (any city, local times) and Home to Event / Event to Home ride search using the user's home place (YAL-024).
- Alerts for requests and decisions, mark as read, transactional outbox drained by an arq worker (YAL-025, ADR 0005).

### Fixed
- Departure-time filter now wraps past midnight (YAL-B01).
- Trip place filters match by distance (PostGIS) with text as fallback; place search can rank by distance (YAL-B02).
- Trip list hides departed, cancelled and completed trips and supports a local date filter (YAL-B05).

### Changed
- Trips use passenger_seats (1-3, host excluded) and seats_taken; seats_total/going removed with a data migration (YAL-B03).
- Trips store departs_at (instant) + timezone; API returns ISO 8601 local times and window_ends_at (YAL-B04, ADR 0006).
