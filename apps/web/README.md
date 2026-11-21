# @yalla/web

Thin web client: shows the backend working end to end. Owner: @Pranav-Rathod-10.

```bash
make dev && make seed          # API on :8000 with demo data
pnpm --filter @yalla/web dev   # http://localhost:5173
```

Set `VITE_API_URL` if the API is not on `http://localhost:8000`. In dev, the login screen fills
in the OTP code the API echoes back. Seeded phones: `+919800000001` … `+919800000005`.

Screens: Login, Trips (filters), Trip details + Request to Join, Post a Trip, Requests
(Sent/Received with Accept/Decline/Cancel), Alerts.
