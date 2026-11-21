# Data flow

How data moves for each main flow, from the client tap to the database and back.
All requests go through the generated client in `packages/api-client`.

## Request lifecycle (every API call)

```mermaid
sequenceDiagram
    autonumber
    participant C as Client (web / mobile)
    participant Q as TanStack Query cache
    participant A as FastAPI route
    participant S as Service
    participant D as PostgreSQL

    C->>Q: useQuery(['trips', filters])
    alt cached and fresh
        Q-->>C: cached data
    else stale or missing
        Q->>A: GET /v1/trips?... (Bearer JWT)
        A->>A: authenticate, validate query (Pydantic)
        A->>S: list_trips(user, filters)
        S->>D: SELECT ... (one transaction)
        D-->>S: rows
        S-->>A: domain objects
        A-->>Q: 200 JSON (response model)
        Q-->>C: data
    end
    Note over A: Domain errors become 4xx application/problem+json
```

## Sign in (phone OTP)

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as API
    participant R as Redis
    participant D as PostgreSQL
    participant P as SMS provider (later)

    C->>A: POST /v1/auth/otp/request {phone}
    A->>R: SET otp:{phone} = code (TTL 5 min)
    A-->>P: send code (prod only)
    A-->>C: 202 (dev: code echoed back)
    C->>A: POST /v1/auth/otp/verify {phone, code}
    A->>R: GET + DEL otp:{phone}
    A->>D: upsert user by phone
    A-->>C: {access_token (15 min), refresh_token (30 days)}
    C->>A: POST /v1/auth/refresh {refresh_token}
    A-->>C: new access_token
```

## Post a trip

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as API
    participant S as trips service
    participant D as PostgreSQL

    C->>A: POST /v1/trips {from_place_id, to_place_id, depart_date, window_start, window_minutes, passenger_seats, joining, females_only, cost}
    A->>A: validate: window 15|30, seats 1..3, date not past
    A->>S: create_trip(host, data)
    S->>D: INSERT trip, INSERT trip_member(host)
    D-->>S: trip
    S-->>A: trip
    A-->>C: 201 Trip
    C->>C: invalidate ['trips'] and navigate to Trips
```

## Search trips

```mermaid
flowchart LR
    q[GET /v1/trips] --> f1{from / to given?}
    f1 -- place id or lat,lng --> geo[ST_DWithin place.location, point, radius]
    f1 -- text only --> txt[name ILIKE fallback]
    f1 -- none --> all[no place filter]
    geo & txt & all --> t{time given?}
    t -- yes --> win[departs_at within +-60 min of date + time]
    t -- no --> d{date given?}
    win --> fut
    d -- yes --> day[departs_at on that local date]
    d -- no --> fut[departs_at >= now, status open]
    day --> fut
    fut --> fo[hide nothing for females_only; flag can_request per viewer]
    fo --> page[order by departs_at, id; cursor page]
```

## Request to join, accept, decline

```mermaid
sequenceDiagram
    autonumber
    participant R as Requester
    participant A as API
    participant S as requests service
    participant D as PostgreSQL
    participant W as Worker
    participant H as Host

    R->>A: POST /v1/trips/{id}/requests {message}
    A->>S: create_request(user, trip_id, message)
    S->>D: SELECT trip FOR UPDATE
    S->>S: checks: not own trip, not duplicate, females-only rule, trip open
    alt joining = instant
        S->>D: seats_taken + 1, INSERT member, request.status = accepted
    else joining = approval
        S->>D: INSERT request (pending)
    end
    S->>D: INSERT alert(host) + INSERT outbox(push) (same transaction)
    A-->>R: 201 TripRequest
    W->>D: poll outbox (SKIP LOCKED)
    W-->>H: push notification (later)

    H->>A: PATCH /v1/requests/{id} {status: accepted}
    A->>S: decide_request(host, id, accepted)
    S->>D: SELECT trip FOR UPDATE
    alt seats_taken < passenger_seats
        S->>D: seats_taken + 1, INSERT member, request accepted, alert(requester)
        A-->>H: 200
    else full
        A-->>H: 409 trip_full
    end
```

The `SELECT ... FOR UPDATE` on the trip row serialises concurrent accepts, so two hosts' taps
(or an instant join racing an accept) can never overbook the last seat.

## Request state machine

```mermaid
stateDiagram-v2
    [*] --> pending: approval trip
    [*] --> accepted: instant-join trip
    pending --> accepted: host accepts (seat free)
    pending --> declined: host declines
    pending --> cancelled: requester cancels
    accepted --> cancelled: requester cancels (seat freed)
    declined --> [*]
    cancelled --> [*]
```

## Event ride search (Home to Event / Event to Home)

```mermaid
flowchart LR
    tap[Tap event] --> dir{direction}
    dir -- to_event --> a[from = user's home place<br/>to = event venue]
    dir -- from_event --> b[from = event venue<br/>to = user's home place]
    a & b --> s[GET /v1/trips with from/to place ids<br/>date = event date]
```

## Alerts and the outbox

```mermaid
flowchart LR
    tx[Service transaction] -->|INSERT| alerts[(alerts)]
    tx -->|INSERT| outbox[(outbox)]
    worker[arq worker, every 5 s] -->|SELECT ... FOR UPDATE SKIP LOCKED| outbox
    worker --> push[send push]
    worker -->|processed_at = now| outbox
    client[Client] -->|GET /v1/me/alerts| alerts
```

Writing the alert and the outbox row in the same transaction as the business change means
an alert is never lost and never sent for a change that rolled back.
