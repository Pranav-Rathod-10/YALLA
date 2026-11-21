#!/usr/bin/env bash
# Regenerates packages/api-client from the FastAPI app (no running server needed). ADR 0004.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/packages/api-client"

(cd "$ROOT/services/api" && uv run python -c \
  "import json; from app.main import app; print(json.dumps(app.openapi(), indent=2, sort_keys=True))") \
  > "$OUT/openapi.json"
pnpm --dir "$OUT" exec openapi-typescript openapi.json -o src/schema.d.ts
echo "api-client regenerated"
