# Feature tracker

`features.csv` is the lightweight roadmap and ownership log. No Jira for now. Open it in
GitHub (renders as a searchable table), Excel, Numbers or Google Sheets.

| Column | Meaning |
|---|---|
| `id` | `YAL-0xx` for features/chores, `YAL-Bxx` for bugs |
| `type` | feat, fix, bug, chore, docs, ci, decision |
| `status` | proposed, planned, in_progress, in_review, merged, rejected, dropped |
| `proposed_by` | Who suggested it (spec items: Pranav) |
| `source` | Where it came from: spec section, ADR, discussion |
| `rationale` | Why it exists, one line |
| `owner` | Who builds it |
| `branch`, `pr` | Where the work is |
| `reviewer`, `review_outcome`, `merged_on` | Filled by the person who reviews and merges, at the time they do it |

Update the row in the same PR that changes the work.
