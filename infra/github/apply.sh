#!/usr/bin/env bash
# Applies repository settings and branch rulesets. Needs ADMIN on the repo.
#   REPO=Pranav-Rathod-10/YALLA ./infra/github/apply.sh
set -euo pipefail

REPO="${REPO:-Pranav-Rathod-10/YALLA}"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Repo settings on $REPO"
# Merge commits only: stacked PRs merge cleanly in order; squash would rewrite history.
gh api -X PATCH "repos/$REPO" \
  -F allow_merge_commit=true \
  -F allow_squash_merge=false \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true \
  -F allow_auto_merge=true >/dev/null

echo "==> Rulesets"
existing="$(gh api "repos/$REPO/rulesets" --jq '.[] | "\(.id) \(.name)"')"
for file in "$DIR"/rulesets/*.json; do
  name="$(jq -r .name "$file")"
  id="$(awk -v n="$name" '$2==n {print $1}' <<<"$existing")"
  if [[ -n "$id" ]]; then
    gh api -X PUT "repos/$REPO/rulesets/$id" --input "$file" >/dev/null && echo "updated $name"
  else
    # branch_name_pattern is not available on every plan; don't abort the rest.
    gh api -X POST "repos/$REPO/rulesets" --input "$file" >/dev/null \
      && echo "created $name" || echo "skipped $name (not supported on this plan?)"
  fi
done
