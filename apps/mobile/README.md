# @yalla/mobile

Expo (SDK 58) + Expo Router + TypeScript. Owner: @Pranav-Rathod-10.

This is a **skeleton**: four tabs (Home, Trips, Requests, Social), trip details with Request to
Join, OTP login, and the spec's design tokens in `src/theme.ts`. It talks to the real API
through `@yalla/api-client`. The real screens from `docs/spec/frontend-spec.md` are built on top.

```bash
make dev && make seed                     # API on :8000
pnpm --filter @yalla/mobile start         # Expo dev server
```

`EXPO_PUBLIC_API_URL` defaults to `http://10.0.2.2:8000` (Android emulator → host).
On a phone use your machine's LAN IP, e.g. `EXPO_PUBLIC_API_URL=http://192.168.1.20:8000`.

Read `AGENTS.md` before using an AI agent here: Expo APIs change every SDK.
