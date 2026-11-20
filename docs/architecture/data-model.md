# Data model

PostgreSQL 16 with PostGIS. All ids are UUIDs. All timestamps are `timestamptz` (UTC).
Local times (a trip's departure) are stored as an instant plus the IANA timezone of the
pickup city so they render correctly anywhere.

```mermaid
erDiagram
    users ||--o{ trips : hosts
    users ||--o{ trip_requests : sends
    users ||--o{ trip_members : rides
    users ||--o{ alerts : receives
    users ||--o{ saved_trips : saves
    places ||--o{ trips : "from / to"
    places ||--o{ events : venue
    places ||--o{ users : home
    trips ||--o{ trip_requests : has
    trips ||--o{ trip_members : has
    trips ||--o{ saved_trips : saved

    users {
        uuid id PK
        text phone UK
        text name
        text gender "female | male | other | undisclosed"
        bool gender_verified
        uuid home_place_id FK
        timestamptz created_at
    }
    places {
        uuid id PK
        text name
        text address
        text city
        text timezone "IANA, e.g. Asia/Kolkata"
        geography location "Point, SRID 4326"
    }
    trips {
        uuid id PK
        uuid host_id FK
        text title
        text tag
        uuid from_place_id FK
        uuid to_place_id FK
        text pickup
        timestamptz departs_at
        text timezone
        smallint window_minutes "15 | 30"
        smallint passenger_seats "1..3, host not counted"
        smallint seats_taken "0..passenger_seats"
        text vehicle
        int cost_per_person_minor "nullable, paise"
        bool cost_shared
        text joining "approval | instant"
        bool females_only
        text status "open | full | cancelled | completed"
        timestamptz created_at
    }
    trip_requests {
        uuid id PK
        uuid trip_id FK
        uuid requester_id FK
        varchar message "max 1024"
        text status "pending | accepted | declined | cancelled"
        timestamptz created_at
        timestamptz decided_at
    }
    trip_members {
        uuid trip_id PK
        uuid user_id PK
        text role "host | traveller"
    }
    saved_trips {
        uuid user_id PK
        uuid trip_id PK
    }
    events {
        uuid id PK
        text name
        uuid venue_place_id FK
        timestamptz starts_at
        text image_url
    }
    alerts {
        uuid id PK
        uuid user_id FK
        uuid actor_id FK
        text kind "request | accepted | declined | query | new_trip"
        uuid trip_id FK
        text text
        timestamptz read_at
        timestamptz created_at
    }
    outbox {
        bigint id PK
        text topic
        jsonb payload
        timestamptz created_at
        timestamptz processed_at
    }
```

## Constraints enforced in the database

| Rule (spec section 12) | Constraint |
|---|---|
| 1 to 3 passenger seats | `CHECK (passenger_seats BETWEEN 1 AND 3)` |
| Seats taken never exceed seats | `CHECK (seats_taken BETWEEN 0 AND passenger_seats)` |
| Window is 15 or 30 minutes | `CHECK (window_minutes IN (15, 30))` |
| Message max 1024 chars | `varchar(1024)` |
| No duplicate live request | partial unique index on `(trip_id, requester_id) WHERE status IN ('pending','accepted')` |

Rules that need context (own trip, past date, females-only) live in the service layer.

## Indexes

- `trips (status, departs_at)` for the default "upcoming open trips" listing.
- GiST on `places.location` for radius search.
- `trip_requests (requester_id, created_at desc)` and `(trip_id, status)` for the Requests tabs.
- `alerts (user_id, created_at desc)`.
- `outbox (id) WHERE processed_at IS NULL`.
