# yalla-api

FastAPI backend for Yalla.

```bash
uv sync                      # install
uv run uvicorn app.main:app --reload
uv run pytest
uv run mypy app
```

Config comes from environment variables (prefix `YALLA_`), see `.env.example`.
