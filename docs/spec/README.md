# Spec

| File | What |
|---|---|
| `frontend-spec.md` | Written source of truth for screens, flows, tokens and rules (by Pranav). |
| `prototype.html` | Clickable prototype. Open in a browser. Visual source of truth. |

The spec was written frontend-first. Backend decisions that differ from it are recorded
as ADRs in `docs/adr/` and as `fix/` or `refactor/` PRs that cite the spec section they change.

Known spec issues (tracked in `docs/tracker/features.csv`):

| ID | Spec section | Issue |
|---|---|---|
| YAL-B01 | 7.3 | Departure-time filter `abs(a - b) <= 60` misses trips across midnight (11:30 PM vs 12:00 AM). |
| YAL-B02 | 7.3 / 8.1 | Place matching by substring is fragile (`Panjim` vs `Panaji`) and ignores "Current location". |
| YAL-B03 | 7.5 / 11 / 12 | Seat count defined three ways (`total` includes host, `seatsTotal` doesn't, `seats + 1`). |
| YAL-B04 | 11 | Dates, times, costs and seats stored as display strings. |
| YAL-B05 | 7.3 | Date strip does not filter; past trips are never hidden. |
| YAL-B06 | 7.4 | Tapping "Request sent" cancels with no confirmation. |
