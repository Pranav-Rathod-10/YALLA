# Yalla: Frontend Specification

Hand this file to any coding agent. It describes the mobile app's screens, flows, design tokens, data and rules. The companion file `prototype.html` is a clickable prototype of everything below. Open it in a browser and treat it as the visual source of truth. This file is the written source of truth. If the two disagree, ask the owner.

Scope: frontend only (iOS and Android). The backend does not exist yet. Section 12 proposes the data contract the frontend expects, and Section 13 lists what is not designed yet.

---

## 1. Product in one paragraph

> Renamed from "Bla Bla Goa" to **Yalla** and widened from Goa-only to any city (decision: YAL-001, see `docs/tracker/features.csv`). Sample data below still uses Goa places; the backend seeds several cities.

Yalla is a cab trip-sharing app that works in any city. A user posts a cab trip (destination, starting point, date, a departure window of at most 30 minutes, and 1 to 3 seats). A host can mark a trip **Females only**, which adds a label to its card on the Trips page. Other users browse trips, filter them, and send a request to join. The host accepts or declines each request. A Social tab lists big concerts and offers one-tap "Home to Concert" and "Concert to Home" ride searches.

Business model, payments, chat and ratings logic are not decided yet (see Section 13).

## 2. Branding and legal notes

- App name: **Yalla**. Logo for now: a white cab icon above the name on brand green. It is a first draft.
- The layouts were inspired by a sports-partner app the owner uses as a reference. Do not copy that app's name, logo, illustrations, wording or colours. The prototype already uses original wording and simple original illustrations. Keep it that way.
- All people, concerts, venues and prices in this spec are made-up sample data.
- Ad slot on Trip details is an optional placeholder only. No ad network is chosen.
- If a Google Places autocomplete is used later, follow Google's attribution rules. The prototype omits the "powered by Google" line because it uses a local sample list.

## 3. Recommended stack (change if the owner prefers)

| Concern | Recommendation |
|---|---|
| Framework | React Native with Expo, TypeScript, one codebase for iOS and Android |
| Navigation | Expo Router (file-based) with a bottom tab navigator and stack screens |
| Bottom sheets | `@gorhom/bottom-sheet` or Expo/React Navigation modal presentation |
| Server state | TanStack Query |
| Client state | Zustand (trip draft, filters, sheet state) |
| Dates | `date-fns` |
| Icons | `lucide-react-native` (the prototype uses simple stroke icons of this style) |
| Fonts | Inter (UI) and Space Grotesk (headings) via `expo-font` |
| Styling | StyleSheet with a central `theme.ts` built from Section 4 |

Build against mock data first (Section 11) behind a repository layer, so the real API can replace it without touching screens.

## 4. Design tokens

### Colours

| Token | Value | Use |
|---|---|---|
| `brand` | `#2F9E5E` | Primary buttons, active tab, selected date, splash background |
| `brandInk` | `#FFFFFF` | Text on brand |
| `brandTint` | `#D7EFE0` | Active chip fill, selected segment tint, month label |
| `brandDeep` | `#1F6B3F` | Text on brand tint |
| `brandPressed` | `#1D7A47` | "Request sent" button |
| `text` | `#141816` | Primary text |
| `textMuted` | `#5B625E` | Secondary text |
| `textSubtle` | `#7A817C` | Captions, labels |
| `line` | `#E3E7E3` | Card borders, dividers |
| `surfaceGray` | `#F1F2F1` | Page background behind cards |
| `surface` | `#FFFFFF` | Cards, sheets |
| `timePill` | `#2F6DF6` | Date and time pill on trip cards, Picks block |
| `warnFill` / `warnInk` | `#F6A93B` / `#3B2500` | "Only N seats" badge |
| `heartOn` | `#E0405A` | Saved heart |
| `femaleTag` | bg `#FDE7F1`, text `#A3185F` (note area `#FDF0F6`) | Females only label and switch note |
| `headerDark` | `#2A3238` | Trip details header, "Invite" segment |
| `statusPending` | bg `#FDF0D5`, text `#8A5A00` | Request status |
| `statusAccepted` | bg `#DFF3E6`, text `#1F6B3F` | Request status |
| `statusDeclined` | bg `#F7DCDC`, text `#8A1F1F` | Request status |
| `danger` | `#B3261E` (border `#E0B4B4`) | Log out |
| `scrim` | `rgba(0,0,0,0.22)` or `rgba(20,26,28,0.9)` | Behind sheets (light for pickers, dark for request and concert sheets) |

The prototype supports a dark theme only for the outer presentation page, not for the app. Design the app in light mode first.

### Type

- Headings, card titles, big numbers: **Space Grotesk**, weights 600 and 700.
- Everything else: **Inter**, weights 400, 500, 600, 700.
- Sizes used: 11 (stat captions), 12 (captions, pills), 13 (meta), 14 (body, chips), 15 (rows), 16 (buttons, row titles), 17 to 19 (card titles, greeting), 22 (sheet and section titles), 26 to 32 (large screen titles).

### Shape and spacing

- Screen side padding: 18.
- Card radius 18, chips and pills fully rounded, buttons radius 14, bottom sheets top radius 34, avatar circles.
- Cards on gray pages use a soft shadow (`0 2 8 rgba(0,0,0,0.05)`). Cards on white pages use a 1 px `line` border.
- Tap targets at least 44 pt.

### Floating tab bar

Pill-shaped bar floating 22 pt above the bottom edge, 14 pt inset left and right, height 68, translucent white with blur, soft shadow. Four tabs, each with an icon and a label. Active tab: brand-green icon and label on a `brand` tint capsule.

## 5. Navigation map

```
Splash ──(2.2 s)──> Home

Tabs (floating bar, always visible on these four screens):
  Home | Trips | Requests | Social

Home      -> avatar: Profile
          -> bell: Alerts
          -> card Trips: Trips tab
          -> card Requests: Requests tab
          -> card Post a trip: Post a Trip
          -> card Social: Social tab
          -> other cards: nothing (intentional)

Trips     -> trip card: Trip details
          -> POST A TRIP button: Post a Trip
          -> filter chips: Location sheet or Departure window sheet

Trip details -> Request to Join: Request sheet -> Send Request -> button becomes "Request sent"

Post a Trip -> Destination / Starting from: Location sheet
            -> Date: Date sheet
            -> Departure time: Departure window sheet
            -> Females only switch, Joining, Share cost, Seats: in place
            -> Post Trip: back to Trips (new trip on top)

Social    -> concert card: Concert ride sheet
          -> Home to Concert / Concert to Home: Trips tab with filters set

Profile   -> Log out: Splash (later: Login)
```

Back arrows return to the previous screen. Tab switches replace the stack. The header (avatar, greeting, location, bell) appears on the four tab screens only.

## 6. Shared header (tab screens)

- Left: avatar circle (44) with the user's initial (photo later), tap opens Profile.
- Next to it: "Hey {firstName}!" (19, weight 600) and below it the user's city with a chevron, in green (sample: `Panjim, Goa`). The city picker is not designed yet. The app is not tied to one city: city, places and events come from the backend.
- Right: bell icon only, tap opens Alerts. (Chat and calendar icons were removed on purpose.)

## 7. Screens

### 7.1 Splash
Full-screen `brand` background. Centered: white cab icon (about 130 wide) above "Yalla" (Space Grotesk 700, 38, white, centered). Fades in. After about 2.2 seconds go to Home (later: Login if signed out).

### 7.2 Home (tab)
Gray page with a white header. Scrollable gray area with rounded top corners.
- A 2 by 2 grid of shortcut cards, each with an uppercase Space Grotesk title, a short line, and an illustration at the bottom right: **Trips** ("Find trips. Join the ride"), **Requests** ("Track your requests"), **Post a trip** ("Plan it. Post it."), **Social** ("Rides to big concerts."). They map to the four destinations in Section 5.
- A wide card **Weekend getaways** ("Quick trips this Sat and Sun"). No action yet.
- A blue block (`timePill`) titled **Yalla Picks** with three white cards: Beach hopping, Falls and treks, Heritage drives. No action yet.

### 7.3 Trips (tab)
- Header, then a date strip: a vertical "NOV" month label and days (Today, then weekday names with day numbers). One day is selected (green circle). **Currently visual only. It does not filter yet.**
- A small filter icon with the label **Filter by**, then three chips in a horizontally scrollable row:
  - **Destination** opens the Location sheet (Section 8.1)
  - **Start point** opens the Location sheet
  - **Departure time** opens the Departure window sheet in filter mode
  - A chip with a value is highlighted and shows `Label: value` plus a clear (×).
- Section label "Explore all trips", then the list of trip cards.
- Floating green button **POST A TRIP** (plus icon) above the tab bar.

**Filter rules**
- Destination: case-insensitive substring match on `trip.to`.
- Start point: case-insensitive substring match on `trip.from`.
- The value `Current location` is treated as "no text filter" until real location matching exists.
- Departure time: show trips where `abs(trip.startMin - filter.startMin) <= 60` (minutes since midnight).
- Filters combine with AND. Clearing a chip removes that filter.
- Empty state text: "No trips match these filters. Clear a filter to see more."

**Trip card**
1. Blue pill: `Sat, 22 Nov · 6:00 AM - 6:30 AM` and a heart toggle (save) on the right.
2. Up to 4 overlapping avatar circles, then `• 2/4 going`, and an amber badge when seats are low (`2 seats left`, `Only 1 seat`).
3. Title (Space Grotesk 600, 17).
4. Route line: pin icon, `from`, arrow, `to`.
5. Small chips that wrap onto a new line if needed: vehicle (`Cab (SUV)`), cost (`₹900 / person`, or plain text like `Cost shared` when no amount), and, for Females only trips, a pink **Females only** chip.

Tapping the card (not the heart) opens Trip details.

### 7.4 Trip details
- Dark header (`headerDark`): back arrow, share icon, bookmark icon. Title (Space Grotesk 700, 26) with a white chip for the trip tag (`Road trip`). Below it the date and time window.
- A white route card overlapping the header: green pin, `{from} to {to}`, and `Pickup: {pickup}`.
- Card **Trip details**: rows Dates, Vehicle, Cost per person, Seats left (two digits, `02`); grey tags **Host approval** and **Cost shared**, plus a pink **Females only** tag when the trip is females only.
- Optional dashed "Sponsored" placeholder card for an ad. Remove if the owner decides on no ads.
- Card **Travellers (n)**: avatar, name, small caption (`Trip host` or `Traveller`), a **Host** pill on the first row.
- Fixed bottom bar: **Send Query** (white button, no behaviour yet, chat is not designed) and **Request to Join** (green).

**Request states**
- Not requested: green `Request to Join`. Tap opens the Request sheet.
- Requested: darker green `Request sent`. Tap again cancels the request.
- A requested trip appears at the top of Requests, Sent, as Pending.

### 7.5 Post a Trip (stack screen)
Back button (round, bordered) and a large title "Post a Trip". Scrollable form:
1. **Destination** row (flag icon). Opens the Location sheet. When set, shows a small label above the chosen place.
2. **Starting from** row (pin icon). Same.
3. **Date** row (calendar icon). Opens the Date sheet. Shows `Tue, 24 Nov`.
4. **Departure time** row (clock icon). Opens the Departure window sheet. Shows `6:00 PM - 6:30 PM`.
5. **Seats available**: stepper (minus, number, plus). Range **1 to 3**, default 2. Under it: `You + {n} will be sitting in the cab` and the hint `Maximum 3 seats per cab.`
6. **Joining**: segmented control **Host approval** (default) or **Instant join**. Helper text changes:
   - Host approval: "Travellers send a request. You review and accept or decline each one."
   - Instant join: "Anyone can join straight away until all seats are filled."
7. **Females only** switch (default off), in its own card with the text "Only women can request to join. Your trip shows a Females only label on the Trips page."
8. **Share cost** switch (default on). Note: "The total cost is split equally among travellers and shown on the trip before anyone requests." (A cost amount field is not designed yet.)
9. Fixed green button **Post Trip**.

**Validation:** destination, starting point, date and departure time are required. If something is missing, tapping Post Trip shows the message "Add destination, starting point, date and departure time to post." above the button.

**On success:** create the trip, reset the form, go to Trips. In the prototype the new trip is added at the top with title `Trip to {destination}`, tag `Cab trip`, vehicle `Cab`, cost `Cost shared`, `going = 1`, `total = seats + 1`, `femalesOnly` from the switch, and the host as the only traveller. The Joining choice and Share cost switch are not yet stored in the prototype (Females only is). The real implementation must store them (Section 12).

### 7.6 Requests (tab)
Header, then a two-option segmented control **Sent** and **Received**.
- **Sent**: one row per request you made. Avatar (host initial), bold trip title, time, and a status pill on the right (Pending, Accepted, Declined).
- **Received**: one row per request on your trips. Text `{name} wants to join {trip title}`, time, status pill. Pending rows show **Decline** and **Accept** buttons. After tapping, the pill updates and the buttons disappear.
- This screen is the designer's proposal. The owner provided no reference. They may replace it.

### 7.7 Social (tab)
Heading **Big concerts**, subtitle "Tap a concert to find rides there or back home." A vertical list of concert cards: gradient banner with a music-note graphic and a date chip, then the concert name and the venue with a pin icon. (Banners are placeholders. Real concerts would have artwork.)

Tapping a card opens a half-height bottom sheet (Section 8.5) with two options:
- **Home → Concert**: start point = the user's home, destination = the concert venue.
- **Concert → Home**: start point = the concert venue, destination = the user's home.

Choosing an option goes to Trips with the Destination and Start point filters set and the time filter cleared. "Home" is the **Home base** on the profile (sample value `Panjim`). Letting users change it is an open question.

### 7.8 Alerts (stack screen)
Back arrow and centered title **Alerts**. A list of rows: avatar with initial, text with the person's name in bold (`Meera N requested to join your Gokarna Weekend Road Trip`), and a grey date line (`Yesterday`, `18th November`). Alert kinds: new request on your trip, request accepted, request declined, new query, new trip posted by someone you know.

### 7.9 Profile (stack screen)
- Top bar: back arrow only on white. There are no share or menu icons.
- Card 1 (kept from the owner's reference): avatar (92), stats **Trips 12, Buddies 78, Rating 4.8**, the user's name, `Last trip on 14th November`. There is no verification tag.
- Card **About you**: rows Age, Gender, Home base, Member since, each with a value on the right and a chevron. (Values are samples.)
- Card **Settings**: Edit profile, Notifications, Privacy and safety, Language (English), Help and support, About.
- Full-width outlined red **Log out** button, then `Yalla v0.1` in small grey text.

## 8. Bottom sheets

All sheets sit over a dimmed screen. The status bar area stays visible. Close with the X in the top corner.

### 8.1 Location sheet
Opens from Post a Trip (Destination, Starting from) and from the Trips filter chips. Full-height sheet (starts about 60 pt from the top, top radius 34).
- Text field with the placeholder `Location`. Once there is text, the label floats on the border and a clear (×) button appears.
- Line **Current location using GPS** (blue bold text, green location icon). Tapping sets the value to `Current location`.
- Nothing is shown below the GPS line until the user types. (Online and saved-location rows from the reference were removed on purpose.)
- After typing: a **Suggestions** heading and up to 5 results. Each has the place name (17) and a grey address line (13, single line, ellipsis). Prefix matches rank first, then other substring matches. If none match: "No matches. Try another place name."
- Tapping a suggestion fills the field that opened the sheet and closes the sheet.

### 8.2 Date sheet
Title **Select date**. Month calendar with previous and next arrows. Past days are disabled, today has a green ring, the selected day is a solid green circle. A line `Selected: Tue, 24 Nov` and a green **Done** button.

### 8.3 Departure window sheet
Title **Departure window** (or **Filter by departure time** in filter mode).
- Three columns with up and down buttons: hour (1 to 12), minutes (steps of 5), AM/PM.
- Window choice: **15 min** or **30 min** (default 30). Note: "Maximum window is 30 minutes."
- Preview box: `Travellers should arrive within 6:00 PM - 6:30 PM`. In filter mode: `Showing trips leaving within an hour of 6:00 PM - 6:30 PM`.
- **Done** saves the window as text and as `startMin` (minutes since midnight).
- Window text format: `{h}:{mm} {AM|PM} - {h}:{mm} {AM|PM}`, computed as start plus window length, wrapping past midnight.

### 8.4 Request sheet
Opens from Request to Join. Dark scrim. Title **Request to Join**, a short note: `Interested in joining {hostFirstName}’s trip to {destination}? If it is your first time with this host, check their profile before you travel.` Then a multi-line optional message box (placeholder: "Send the host a message with any requests you may have (optional)."), a live counter `0/1024 characters`, and a green **Send Request** button fixed at the bottom. Sending closes the sheet and sets the trip's button to `Request sent`. (There is no payment line because payment is undecided.)

### 8.5 Concert ride sheet
Half-height sheet from the bottom. Concert name, then `{date} · {address}. Find a ride:`, then two large bordered options, each with a bold title and a grey subline (`Panjim to Vagator`).

## 9. Interaction details

- Heart on trip cards toggles saved (outline to filled red). Local state is fine until a backend exists.
- Chips in the date strip: selecting one day deselects the others.
- Switch controls (Share cost) animate. Steppers clamp at their limits.
- Sheets can be dismissed by the X or by tapping Done, Send Request, or choosing an option. Dismissing the Location sheet without choosing keeps the old value.
- Keyboard: when the Location sheet opens, focus the text field. The Request sheet's message box should scroll above the keyboard.
- Respect reduced-motion settings. Splash fade is the only decorative animation.
- Minimum Android back-button behaviour: close an open sheet first, then go back a screen.

## 10. Copy deck (exact strings)

- Tabs: Home, Trips, Requests, Social.
- Home cards: "Trips / Find trips. Join the ride", "Requests / Track your requests", "Post a trip / Plan it. Post it.", "Social / Rides to big concerts.", "Weekend getaways / Quick trips this Sat and Sun", "Yalla Picks", "Beach hopping / Sun, sand and shacks", "Falls and treks / Monsoon and beyond", "Heritage drives / Old Goa to Fontainhas".
- Trips: "Filter by", "Destination", "Start point", "Departure time", "Explore all trips", "POST A TRIP".
- Trip details: "Trip details", "Dates", "Vehicle", "Cost per person", "Seats left", "Host approval", "Cost shared", "Travellers", "Send Query", "Request to Join", "Request sent".
- Post a Trip: "Post a Trip", "Destination", "Starting from", "Date", "Departure time", "Seats available", "Joining", "Host approval", "Instant join", "Females only", "SHARE COST", "Post Trip".
- Requests: "Sent", "Received", "Pending", "Accepted", "Declined", "Accept", "Decline".
- Profile: "About you", "Settings", "Log out".

## 11. Mock data for development

```ts
export const HOME = 'Panjim';

export const trips = [
  { id: 0, startMin: 360,  title: 'Dudhsagar Falls Day Trip',  tag: 'Day trip',   from: 'Panjim',  to: 'Dudhsagar Falls', when: 'Sat, 22 Nov · 6:00 AM - 6:30 AM',  date: 'Sat, 22 Nov',               ride: 'Cab (SUV)',       cost: '₹900',   going: 2, total: 4, slots: '2 seats left', pickup: 'Panjim bus stand',        people: ['Rohan S','Aditi M'] },
  { id: 1, startMin: 420,  title: 'Gokarna Weekend Road Trip', tag: 'Road trip',  from: 'Margao',  to: 'Gokarna',         when: 'Sat, 22 Nov · 7:00 AM - 7:30 AM',  date: 'Sat, 22 Nov - Sun, 23 Nov', ride: 'Cab (Sedan)',     cost: '₹1,800', going: 3, total: 4, slots: 'Only 1 seat',  pickup: 'Margao railway station',  people: ['Meera N','Vikram P','Kabir J'] },
  { id: 2, femalesOnly: true, startMin: 960,  title: 'North Goa Beach Hopping',   tag: 'Beach',      from: 'Calangute', to: 'Vagator, Anjuna', when: 'Sun, 23 Nov · 4:00 PM - 4:30 PM', date: 'Sun, 23 Nov',               ride: 'Cab (Hatchback)', cost: '₹500',   going: 2, total: 4, slots: '2 seats left', pickup: 'Calangute circle',        people: ['Sana K','Dev R'] },
  { id: 3, startMin: 1260, title: 'Hampi 3-Day Trip',          tag: 'Long trip',  from: 'Vasco',   to: 'Hampi',           when: 'Fri, 28 Nov · 9:00 PM - 9:30 PM',  date: 'Fri, 28 Nov - Sun, 30 Nov', ride: 'Cab (SUV)',       cost: '₹4,200', going: 3, total: 4, slots: 'Only 1 seat',  pickup: 'Vasco da Gama station',   people: ['Vikram P','Meera N','Sana K'] },
  { id: 4, startMin: 960,  title: 'Sunset Beats: ride there',  tag: 'Concert',    from: 'Panjim',  to: 'Vagator',         when: 'Sat, 22 Nov · 4:00 PM - 4:30 PM',  date: 'Sat, 22 Nov',               ride: 'Cab (Sedan)',     cost: '₹350',   going: 2, total: 4, slots: '2 seats left', pickup: 'Panjim bus stand',        people: ['Aditi M','Rohan S'] },
  { id: 5, startMin: 0,    title: 'Sunset Beats: ride back',   tag: 'Concert',    from: 'Vagator', to: 'Panjim',          when: 'Sun, 23 Nov · 12:00 AM - 12:30 AM', date: 'Sun, 23 Nov',               ride: 'Cab (Sedan)',     cost: '₹350',   going: 3, total: 4, slots: 'Only 1 seat',  pickup: 'Vagator main gate',       people: ['Kabir J','Sana K','Dev R'] },
  { id: 6, startMin: 1140, title: 'Electro Dunes: ride there', tag: 'Concert',    from: 'Panjim',  to: 'Anjuna',          when: 'Sat, 29 Nov · 7:00 PM - 7:30 PM',  date: 'Sat, 29 Nov',               ride: 'Cab (SUV)',       cost: '₹300',   going: 1, total: 4, slots: '3 seats left', pickup: 'Panjim bus stand',        people: ['Meera N'] },
  { id: 7, startMin: 60,   title: 'Electro Dunes: ride back',  tag: 'Concert',    from: 'Anjuna',  to: 'Panjim',          when: 'Sun, 30 Nov · 1:00 AM - 1:30 AM',  date: 'Sun, 30 Nov',               ride: 'Cab (SUV)',       cost: '₹300',   going: 2, total: 4, slots: '2 seats left', pickup: 'Anjuna flea market gate', people: ['Vikram P','Aditi M'] },
];
// The first person in `people` is the host. Seats left = total - going. `femalesOnly` is optional (defaults to false).

export const concerts = [
  { id: 0, name: 'Sunset Beats Festival', venue: 'Vagator',  addr: 'Vagator Beach, North Goa', when: 'Sat, 22 Nov · 5:00 PM onwards' },
  { id: 1, name: 'Electro Dunes Night',   venue: 'Anjuna',   addr: 'Anjuna, North Goa',        when: 'Sat, 29 Nov · 8:00 PM onwards' },
  { id: 2, name: 'Candolim Live',         venue: 'Candolim', addr: 'Candolim, North Goa',      when: 'Sun, 30 Nov · 6:00 PM onwards' }, // no sample rides on purpose
];

export const sentRequests     = [{ tripId: 0, status: 'accepted' }, { tripId: 3, status: 'pending' }, { tripId: 2, status: 'declined' }];
export const receivedRequests = [{ who: 'Aditi M', tripId: 1, status: 'pending' }, { who: 'Kabir J', tripId: 1, status: 'pending' }, { who: 'Dev R', tripId: 0, status: 'accepted' }];

export const alerts = [
  ['Meera N', 'requested to join your Gokarna Weekend Road Trip', 'Yesterday'],
  ['Rohan S', 'accepted your request for Dudhsagar Falls Day Trip', 'Yesterday'],
  ['Kabir J', 'requested to join your Gokarna Weekend Road Trip', '18th November'],
  ['Sana K', 'sent you a query about North Goa Beach Hopping', '18th November'],
  ['Vikram P', 'declined your request for Hampi 3-Day Trip', '17th November'],
  ['Dev R', 'posted a new trip: Hampi 3-Day Trip', '16th November'],
  ['Aditi M', 'requested to join your Gokarna Weekend Road Trip', '16th November'],
];

export const places = [
  ['Panjim','Panjim, North Goa, Goa'], ['Margao','Margao, South Goa, Goa'], ['Vasco da Gama','Vasco da Gama, South Goa, Goa'],
  ['Mapusa','Mapusa, North Goa, Goa'], ['Calangute','Calangute, North Goa, Goa'], ['Candolim','Candolim, North Goa, Goa'],
  ['Anjuna','Anjuna, North Goa, Goa'], ['Vagator','Vagator, North Goa, Goa'], ['Palolem','Palolem, Canacona, South Goa'],
  ['Old Goa','Old Goa, Tiswadi, Goa'], ['Ponda','Ponda, North Goa, Goa'], ['Dabolim Airport','Dabolim, Vasco da Gama, Goa'],
  ['Manohar International Airport','Mopa, Pernem, North Goa'], ['Dudhsagar Falls','Sonaulim, Sanguem, Goa border'],
  ['Gokarna','Gokarna, Uttara Kannada, Karnataka'], ['Hampi','Hampi, Vijayanagara, Karnataka'], ['Karwar','Karwar, Uttara Kannada, Karnataka'],
];

export const me = { name: 'Pranav Rathod', firstName: 'Pranav', city: 'Panjim, Goa', homeBase: 'Panjim',
  trips: 12, buddies: 78, rating: 4.8, age: 27, gender: 'Male', memberSince: 'Mar 2025' };
```

## 12. Data contract the frontend expects (draft for the backend)

Suggested types:

```ts
type Trip = {
  id: string; hostId: string; title: string; tag?: string;
  from: Place; to: Place; pickup: string;
  departDate: string;        // ISO date
  windowStart: string;       // ISO time, e.g. 18:00
  windowMinutes: 15 | 30;    // max 30
  seatsTotal: number;        // passengers, 1..3 (cab holds host + up to 3)
  seatsTaken: number;
  vehicle: string;           // 'Cab (SUV)', ...
  costPerPerson?: number;    // INR, optional
  costShared: boolean;
  joining: 'approval' | 'instant';
  femalesOnly: boolean;      // default false
  travellers: UserSummary[];
  createdAt: string;
};
type TripRequest = { id: string; tripId: string; requesterId: string; message?: string /* max 1024 */; status: 'pending'|'accepted'|'declined'|'cancelled'; createdAt: string };
type Place = { name: string; address: string; lat?: number; lng?: number };
type Concert = { id: string; name: string; venue: Place; startsAt: string; imageUrl?: string };
type Alert = { id: string; actor: UserSummary; kind: 'request'|'accepted'|'declined'|'query'|'new_trip'; text: string; createdAt: string };
```

Suggested endpoints (names are only a starting point):

| Purpose | Endpoint |
|---|---|
| List and filter trips | `GET /trips?to=&from=&date=&timeMin=&timeWindow=60` |
| Trip details | `GET /trips/:id` |
| Post a trip | `POST /trips` |
| Send request (with optional message) | `POST /trips/:id/requests` |
| Cancel own request | `DELETE /trips/:id/requests/:requestId` |
| My sent requests | `GET /me/requests?direction=sent` |
| Requests on my trips | `GET /me/requests?direction=received` |
| Accept or decline | `PATCH /requests/:id` with `{ status }` |
| Alerts | `GET /me/alerts` |
| Concerts | `GET /concerts` |
| Place search | `GET /places/search?q=` (or a Places provider) |
| Profile | `GET /me`, `PATCH /me` |

Rules the backend should enforce (the frontend only mirrors them):
- A trip has 1 to 3 passenger seats. `seatsTaken` cannot exceed `seatsTotal`.
- Departure window is 15 or 30 minutes, never more.
- Accepting a request when no seats are left must fail with a clear error.
- A user cannot request their own trip or request the same trip twice.
- Past dates cannot be posted.
- Females only trips: the backend should enforce who may request (see Section 13), based on the user's gender in their profile.

## 13. Not designed yet (do not invent, ask the owner)

1. Login, signup, onboarding and ID verification.
2. Chat or messaging with the host (Send Query button does nothing yet).
3. Payments, and whether travellers pay inside the app. This affects Share cost, cost fields and any refund or cancellation rules.
4. Cost amount input when posting a trip.
5. Other users' profiles, host profile and ratings after a trip.
6. Trip management for hosts (edit, cancel, remove a traveller), and what happens to accepted travellers if a trip is cancelled.
7. Trip photos and a map or route view.
8. City or home-base picker, and editing Home base.
9. The Home page cards that do nothing yet (Weekend getaways and the Picks block).
10. Where concerts come from (admin-added or an events feed).
11. Settings screens (Edit profile, Notifications, Privacy and safety, Language, Help, About).
12. Date strip filtering on Trips (the strip is visual only today).
13. Empty and error states for network failures, loading skeletons, and offline behaviour.
14. Females only rules: who can see these trips and who can request them (only women, or visible to all but only women can request), how gender is confirmed, and what a user who does not qualify sees. The prototype only shows the label.
15. Accessibility pass (labels, focus order, dynamic type), and Hindi or Konkani localisation.

## 14. Acceptance checklist for the first build

- [ ] Splash shows for about 2 seconds, then Home.
- [ ] Four-tab floating bar works on iOS and Android and is visible on Home, Trips, Requests and Social only.
- [ ] Home top cards navigate as in Section 5. The lower cards do nothing.
- [ ] Trips: all three filters work and combine. Clearing works. The empty state appears.
- [ ] Concert flow: both directions set the right filters, Candolim Live shows the empty state.
- [ ] Post a Trip: Females only switch adds a pink "Females only" chip to the trip card and tag on Trip details. Seats limited to 1 to 3 with the live "You + n" text, window limited to 15 or 30 minutes, validation message, new trip appears on top of Trips.
- [ ] Request flow: sheet opens, counter works up to 1024, Send Request flips the button to "Request sent", a Pending item appears under Requests, Sent, and tapping "Request sent" cancels.
- [ ] Requests, Received: Accept and Decline update the status pill and remove the buttons.
- [ ] Alerts and Profile match Sections 7.8 and 7.9 (Profile has no top-right icons, no verification tag and no travel style row), and Log out returns to Splash.
- [ ] All colours, fonts and radii come from one theme file built from Section 4.
- [ ] No branding, wording or artwork from the reference app is present.
