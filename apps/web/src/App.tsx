import { useState } from 'react';

import { tokenStore } from './api';
import { Alerts } from './screens/Alerts';
import { Login } from './screens/Login';
import { PostTrip } from './screens/PostTrip';
import { Requests } from './screens/Requests';
import { TripDetail } from './screens/TripDetail';
import { Trips } from './screens/Trips';

type Tab = 'trips' | 'post' | 'requests' | 'alerts';
const TABS: [Tab, string][] = [
  ['trips', 'Trips'],
  ['post', 'Post a trip'],
  ['requests', 'Requests'],
  ['alerts', 'Alerts'],
];

export function App() {
  const [token, setToken] = useState(tokenStore.get());
  const [tab, setTab] = useState<Tab>('trips');
  const [openTrip, setOpenTrip] = useState<string | null>(null);

  if (!token) {
    return (
      <Login
        onSignedIn={(t) => {
          tokenStore.set(t);
          setToken(t);
        }}
      />
    );
  }

  return (
    <>
      <main>
        <div className="row" style={{ justifyContent: 'space-between', marginBottom: 12 }}>
          <h1>Yalla</h1>
          <button
            className="secondary"
            onClick={() => {
              tokenStore.set(null);
              setToken(null);
            }}
          >
            Log out
          </button>
        </div>
        {openTrip ? (
          <TripDetail id={openTrip} onBack={() => setOpenTrip(null)} />
        ) : tab === 'trips' ? (
          <Trips onOpen={setOpenTrip} />
        ) : tab === 'post' ? (
          <PostTrip onPosted={() => setTab('trips')} />
        ) : tab === 'requests' ? (
          <Requests />
        ) : (
          <Alerts />
        )}
      </main>
      <nav className="tabs">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            aria-current={tab === key && !openTrip ? 'page' : undefined}
            onClick={() => {
              setOpenTrip(null);
              setTab(key);
            }}
          >
            {label}
          </button>
        ))}
      </nav>
    </>
  );
}
