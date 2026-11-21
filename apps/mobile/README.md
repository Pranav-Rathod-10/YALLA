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

## Android APK

One-time (needs an Expo account):

```bash
cd apps/mobile
npx eas-cli@latest login
npx eas-cli@latest init        # links the project, writes extra.eas.projectId into app.json
```

Then build an installable APK on EAS (profile `preview` in `eas.json`):

```bash
npx eas-cli@latest build --platform android --profile preview
```

EAS prints a download link and QR code when the build finishes. Set the real API URL in
`eas.json` → `build.preview.env.EXPO_PUBLIC_API_URL` first.

From GitHub: add an `EXPO_TOKEN` repo secret, then run the **mobile** workflow manually
(Actions → mobile → Run workflow).

Local build without EAS (needs Android Studio / SDK): `npx expo run:android --variant release`.
