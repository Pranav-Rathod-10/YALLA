# API

Base path `/v1`. JSON in and out. Auth with `Authorization: Bearer <access_token>`
except where marked public. Errors use RFC 7807:

```json
{ "type": "about:blank", "title": "Trip is full", "status": 409, "code": "trip_full", "detail": "No seats left on this trip." }
```

The live, exact contract is the OpenAPI document at `GET /openapi.json` (Swagger UI at `/docs`).
`packages/api-client` is generated from it.

| Method | Path | Purpose | Notes |
|---|---|---|---|
| GET | `/health` | Liveness and DB check | public |
| POST | `/v1/auth/otp/request` | Send a login code | public |
| POST | `/v1/auth/otp/verify` | Exchange code for tokens | public, creates user on first login |
| POST | `/v1/auth/refresh` | New access token | public |
| GET / PATCH | `/v1/me` | Profile, home place, gender | |
| GET | `/v1/places/search?q=&near=lat,lng` | Place autocomplete | up to 5, prefix matches first |
| GET | `/v1/trips` | List and filter trips | see below |
| POST | `/v1/trips` | Post a trip | |
| GET | `/v1/trips/{id}` | Trip details with travellers | |
| PUT / DELETE | `/v1/trips/{id}/save` | Save / unsave (heart) | |
| POST | `/v1/trips/{id}/requests` | Request to join | optional message, max 1024 |
| DELETE | `/v1/requests/{id}` | Cancel own request | frees a seat if it was accepted |
| PATCH | `/v1/requests/{id}` | Host accepts or declines | `{ "status": "accepted" \| "declined" }` |
| GET | `/v1/me/requests?direction=sent\|received` | Requests tab | |
| GET | `/v1/me/alerts` | Alerts | newest first |
| GET | `/v1/events?city=` | Events (concerts) | |
| GET | `/v1/events/{id}/rides?direction=to_event\|from_event` | Home to Event / Event to Home | uses the user's home place |

## `GET /v1/trips` query parameters

| Param | Meaning |
|---|---|
| `from_place_id`, `to_place_id` | Match trips whose place is within `radius_km` of this place |
| `from_near`, `to_near` | `lat,lng` instead of a place id ("Current location") |
| `from`, `to` | Free-text fallback, case-insensitive substring on place name |
| `radius_km` | Default 3 |
| `date` | Local date `YYYY-MM-DD` |
| `time_min` | Local minutes since midnight; trips departing within 60 minutes of it (across midnight) |
| `cursor`, `limit` | Keyset pagination, default limit 20 |

Past trips and cancelled trips are never returned.
