# @yalla/api-client

Typed client for the Yalla API, **generated** from FastAPI's OpenAPI schema (ADR 0004).
Do not edit `src/schema.d.ts` or `openapi.json` by hand.

```bash
pnpm gen:api   # after changing any backend route or schema
```

```ts
import { createYallaClient } from '@yalla/api-client';

const api = createYallaClient({ baseUrl: 'http://localhost:8000', getToken: () => token });
const { data, error } = await api.GET('/v1/trips', { params: { query: { to: 'Vagator' } } });
```
